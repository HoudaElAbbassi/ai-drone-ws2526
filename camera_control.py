import time
import signal
import sys
import os
import uuid
import serial
import struct
import cv2
import numpy as np
from tflite_runtime.interpreter import Interpreter, load_delegate

# --- IMPORT PICAMERA2 MODULES ---
from picamera2 import Picamera2
from picamera2.encoders import H264Encoder

# --- CONFIGURATION ---
SERIAL_PORT = '/dev/ttyS0'
BAUD_RATE = 115200
VIDEO_PATH = "/home/tpu/Videos/"
MODEL_PATH = "/home/tpu/drone_script/best_int8.tflite"
AUX_CHANNEL_INDEX = 8
TRIGGER_VALUE = 1500
CONFIDENCE_THRESHOLD = 0.5
NMS_THRESHOLD = 0.4

# --- INITIALIZE SERIAL ---
try:
    ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=0.1)
    print(f"Opened serial port: {SERIAL_PORT}")
except Exception as e:
    print(f"Error opening serial port: {e}")
    sys.exit(1)

# --- INITIALIZE TFLITE ---
try:
    interpreter = Interpreter(
        model_path=MODEL_PATH,
        experimental_delegates=[load_delegate('libedgetpu.so.1')]
    )
    interpreter.allocate_tensors()
    input_details = interpreter.get_input_details()
    output_details = interpreter.get_output_details()
    _, input_height, input_width, _ = input_details[0]['shape']
    input_type = input_details[0]['dtype']
    
    print(f"Model Input: {input_width}x{input_height}, Dtype: {input_type}")

except Exception as e:
    print(f"Error loading Edge TPU model: {e}")
    sys.exit(1)

# --- INITIALIZE CAMERA ---
try:
    picam2 = Picamera2()
    # Using 2 buffers for lores to ensure we don't block
    config = picam2.create_video_configuration(
        main={"size": (1920, 1080), "format": "YUV420"}, 
        lores={"size": (input_width, input_height), "format": "YUV420"},
        buffer_count=3 
    )
    picam2.configure(config)
    picam2.start()
    print("Camera started.")
except Exception as e:
    print(f"Error initializing camera: {e}")
    sys.exit(1)

# Global State
recording = False
current_filename = ""
encoder = H264Encoder() 

MSP_RC_REQUEST = b'$M<\x00\x69\x69'

def get_rc_channels():
    try:
        ser.reset_input_buffer()
        ser.write(MSP_RC_REQUEST)
        header = ser.read(5)
        if len(header) < 5 or header[:3] != b'$M>': return None
        size = header[3]
        payload = ser.read(size)
        ser.read(1)
        count = size // 2
        return struct.unpack('<' + 'H'*count, payload)
    except:
        return None

def yuv420_to_rgb(yuv_frame, width, height):
    """Convert YUV420 to RGB using OpenCV."""
    # Reshape logic for YUV420
    yuv = yuv_frame.reshape((height * 3 // 2, width))
    rgb = cv2.cvtColor(yuv, cv2.COLOR_YUV2RGB_I420)
    return rgb

def yolo_postprocess(output_data, conf_thresh, nms_thresh):
    """Parses YOLOv8 output: Shape [1, 12, 2100]"""
    predictions = np.transpose(output_data[0])
    scores = np.max(predictions[:, 4:], axis=1)
    
    keep_indices = np.where(scores > conf_thresh)[0]
    predictions = predictions[keep_indices]
    scores = scores[keep_indices]
    
    if len(scores) == 0:
        return [], [], []

    box_data = predictions[:, :4]
    
    boxes = []
    for i in range(len(box_data)):
        cx, cy, w, h = box_data[i]
        x = int(cx - w/2)
        y = int(cy - h/2)
        width_box = int(w)
        height_box = int(h)
        boxes.append([x, y, width_box, height_box])

    indices = cv2.dnn.NMSBoxes(boxes, scores.tolist(), conf_thresh, nms_thresh)
    
    final_boxes = []
    final_scores = []
    final_classes = []
    
    if len(indices) > 0:
        for i in indices.flatten():
            x, y, w, h = boxes[i]
            norm_box = [
                y / input_height,       
                x / input_width,        
                (y + h) / input_height, 
                (x + w) / input_width   
            ]
            final_boxes.append(norm_box)
            final_scores.append(scores[i])
            final_classes.append(0)

    return final_boxes, final_classes, final_scores

def run_inference(image):
    """Runs inference on a single frame."""
    input_data = np.expand_dims(image, axis=0)

    if input_type == np.float32:
        input_data = (input_data.astype(np.float32) / 255.0)
    elif input_type == np.int8:
        input_data = (input_data.astype(np.float32) - 128).astype(np.int8)
    elif input_type == np.uint8:
        input_data = input_data.astype(np.uint8)

    interpreter.set_tensor(input_details[0]['index'], input_data)
    interpreter.invoke()

    output_data = interpreter.get_tensor(output_details[0]['index'])
    return yolo_postprocess(output_data, CONFIDENCE_THRESHOLD, NMS_THRESHOLD)

def save_detection(frame, box, score):
    h, w, _ = frame.shape
    ymin, xmin, ymax, xmax = box
    
    start_point = (int(xmin * w), int(ymin * h))
    end_point = (int(xmax * w), int(ymax * h))
    
    # Draw on a COPY to ensure we don't mess up thread safety (though we are single threaded here)
    out_img = frame.copy()
    out_img = cv2.cvtColor(out_img, cv2.COLOR_RGB2BGR)
    cv2.rectangle(out_img, start_point, end_point, (0, 0, 255), 2)
    
    label = f"Pothole: {score:.2f}"
    cv2.putText(out_img, label, (start_point[0], start_point[1]-10), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
    
    filename = f"{VIDEO_PATH}detect_{int(time.time())}_{score:.2f}.jpg"
    cv2.imwrite(filename, out_img)
    print(f"[AI] Pothole detected! Saved: {filename}")

def main():
    global recording, current_filename

    if not os.path.exists(VIDEO_PATH):
        os.makedirs(VIDEO_PATH)

    print("Ready. Waiting for RC switch...")

    try:
        while True:
            channels = get_rc_channels()
            
            if channels and len(channels) > AUX_CHANNEL_INDEX:
                switch_val = channels[AUX_CHANNEL_INDEX]
                
                if switch_val > TRIGGER_VALUE and not recording:
                    unique_id = str(uuid.uuid4())[:8]
                    current_filename = f"{VIDEO_PATH}flight_{int(time.time())}_{unique_id}.h264"
                    print(f"[REC] Starting: {current_filename}")
                    picam2.start_recording(encoder, current_filename)
                    recording = True
                    
                elif switch_val < TRIGGER_VALUE and recording:
                    print(f"[REC] Stopping.")
                    picam2.stop_recording()
                    recording = False

            if recording:
                # Capture array normally
                # Picamera2 'capture_array' blocks until a frame is ready.
                # If we take too long processing, the queue fills up.
                
                # Check if camera has a frame ready (non-blocking attempt roughly)
                # Ideally we just process as fast as possible.
                
                try:
                    # Capture RAW YUV data
                    # We copy it immediately to release the buffer
                    yuv_frame_ref = picam2.capture_array("lores")
                    yuv_frame = yuv_frame_ref.copy() 
                    del yuv_frame_ref # Explicitly release reference
                    
                    # Now we can take our time processing 'yuv_frame'
                    rgb_frame = yuv420_to_rgb(yuv_frame, input_width, input_height)
                    boxes, classes, scores = run_inference(rgb_frame)
                    
                    for i in range(len(scores)):
                        if scores[i] > CONFIDENCE_THRESHOLD:
                            save_detection(rgb_frame, boxes[i], scores[i])
                            break 
                            
                except Exception as e:
                    print(f"Frame drop warning: {e}")
            
            # Reduce sleep to process frames faster? 
            # Actually, we want to sleep IF we are idle, but capture_array blocks anyway.
            # Small sleep for RC check responsiveness if not recording.
            if not recording:
                time.sleep(0.05)

    except KeyboardInterrupt:
        print("Stopping...")
    finally:
        picam2.stop()
        ser.close()

if __name__ == "__main__":
    main()
