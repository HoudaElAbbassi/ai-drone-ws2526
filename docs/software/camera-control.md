---
layout: default
title: Camera Control System
---

# Camera Control & AI Detection System

[← Back to Home](../)

## Overview

The **camera_control.py** script is the core component of our AI-powered road damage detection system. It integrates real-time video recording, RC-triggered control, and Edge TPU-accelerated AI inference into a single cohesive system running on Raspberry Pi Zero 2 WH.

### Key Features

- **RC Switch Triggered Recording**: Start/stop video recording via auxiliary channel on RC transmitter
- **Real-time AI Inference**: Detect road damage (potholes) while recording using Google Coral Edge TPU
- **Dual-Stream Processing**: 1080p recording + low-res inference stream for optimal performance
- **MSP Protocol Integration**: Direct communication with INAV flight controller
- **Automatic Detection Capture**: Save raw images with metadata when damage is detected

## System Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                     Camera Control System                     │
├──────────────────────────────────────────────────────────────┤
│                                                               │
│  RC Transmitter                    Raspberry Pi Zero 2 WH    │
│       │                                    │                  │
│       │ MSP Protocol                       │                  │
│       ▼                                    ▼                  │
│  ┌─────────────┐                  ┌─────────────────┐        │
│  │    INAV     │◄────────────────►│  Serial Port    │        │
│  │    FC       │   /dev/ttyS0     │  (UART)         │        │
│  └─────────────┘    115200 baud   └─────────────────┘        │
│                                            │                  │
│                                            ▼                  │
│  ┌─────────────┐                  ┌─────────────────┐        │
│  │ Camera      │─────────────────►│  Picamera2      │        │
│  │ Module      │   CSI Interface  │  Video Pipeline │        │
│  └─────────────┘                  └─────────────────┘        │
│                                            │                  │
│                                ┌───────────┴──────────┐       │
│                                │                      │       │
│                                ▼                      ▼       │
│                        ┌──────────────┐      ┌──────────────┐│
│                        │ Main Stream  │      │ Lores Stream ││
│                        │ 1920x1080    │      │ 320x320      ││
│                        │ YUV420       │      │ YUV420       ││
│                        └──────┬───────┘      └──────┬───────┘│
│                               │                     │        │
│                               ▼                     ▼        │
│                        ┌──────────────┐      ┌──────────────┐│
│                        │ H.264 Encoder│      │ YUV→RGB      ││
│                        │ Recording    │      │ Conversion   ││
│                        └──────────────┘      └──────┬───────┘│
│                                                     │        │
│                                                     ▼        │
│                                              ┌──────────────┐│
│                                              │ TFLite Model ││
│                                              │ + Edge TPU   ││
│                                              │ (YOLOv8)     ││
│                                              └──────┬───────┘│
│                                                     │        │
│                                                     ▼        │
│                                              ┌──────────────┐│
│                                              │  Detection   ││
│                                              │  Results     ││
│                                              └──────┬───────┘│
│                                                     │        │
│                                                     ▼        │
│                                              ┌──────────────┐│
│                                              │ Save Image   ││
│                                              │ with Bbox    ││
│                                              └──────────────┘│
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

## How It Works

### 1. Initialization Phase

On startup, the script initializes three main components:

**Serial Communication** (`/dev/ttyS0` @ 115200 baud)

- Opens UART connection to INAV flight controller
- Uses MSP (MultiWii Serial Protocol) to read RC channel values
- Monitors AUX8 channel (index 8) for recording trigger

**AI Model Loading**

- Loads quantized YOLOv8 TFLite model (`best_int8.tflite`)
- Initializes Google Coral Edge TPU accelerator
- Configures input tensor (320x320 int8)
- Sets up output tensor for YOLO predictions

**Camera Configuration**

- Configures Picamera2 with dual-stream setup:
  - **Main stream**: 1920x1080 YUV420 for H.264 recording
  - **Lores stream**: 320x320 YUV420 for AI inference
- Uses 3 buffer system to prevent frame drops

### 2. Main Control Loop

The script continuously monitors RC channels and processes video:

```python
while True:
    # 1. Read RC channels via MSP
    channels = get_rc_channels()

    # 2. Check AUX8 switch position
    if switch_val > 1500 and not recording:
        # Start recording
        picam2.start_recording(encoder, filename)

    elif switch_val < 1500 and recording:
        # Stop recording
        picam2.stop_recording()

    # 3. If recording, run AI inference
    if recording:
        frame = picam2.capture_array("lores")
        rgb_frame = yuv420_to_rgb(frame)
        boxes, classes, scores = run_inference(rgb_frame)

        # Save detections
        if scores > threshold:
            save_detection(rgb_frame, box, score)
```

### 3. MSP Protocol Communication

The script uses MSP (MultiWii Serial Protocol) to communicate with the flight controller:

```python
# MSP_RC command (0x69)
MSP_RC_REQUEST = b'$M<\x00\x69\x69'

def get_rc_channels():
    ser.write(MSP_RC_REQUEST)
    header = ser.read(5)  # Read: $M> + size + command
    payload = ser.read(size)  # Read channel data
    checksum = ser.read(1)

    # Unpack 16-bit unsigned integers
    channels = struct.unpack('<' + 'H'*count, payload)
    return channels  # Returns tuple: (1000-2000, ...)
```

**Channel Values:**

- 1000-1500: Switch OFF (stop recording)
- 1500-2000: Switch ON (start recording)

### 4. Dual-Stream Video Processing

The Picamera2 library provides two simultaneous streams:

**Main Stream (Recording)**

- Resolution: 1920x1080
- Format: YUV420
- Purpose: High-quality H.264 video recording
- Encoded and saved to `.h264` file

**Lores Stream (AI Inference)**

- Resolution: 320x320 (matches model input)
- Format: YUV420
- Purpose: Real-time object detection
- Converted to RGB for inference

This dual-stream approach allows high-quality recording while maintaining fast inference speeds.

### 5. AI Inference Pipeline

**YUV to RGB Conversion**

```python
def yuv420_to_rgb(yuv_frame, width, height):
    yuv = yuv_frame.reshape((height * 3 // 2, width))
    rgb = cv2.cvtColor(yuv, cv2.COLOR_YUV2RGB_I420)
    return rgb
```

**Model Inference**

```python
def run_inference(image):
    # Prepare input (int8 quantization)
    input_data = (image.astype(np.float32) - 128).astype(np.int8)
    input_data = np.expand_dims(input_data, axis=0)

    # Run inference on Edge TPU
    interpreter.set_tensor(input_details[0]['index'], input_data)
    interpreter.invoke()

    # Get output [1, 12, 2100] - YOLOv8 format
    output_data = interpreter.get_tensor(output_details[0]['index'])

    # Post-process with NMS
    return yolo_postprocess(output_data, conf_thresh, nms_thresh)
```

**YOLO Post-Processing**

- Transpose output from [1, 12, 2100] to [2100, 12]
- Extract confidence scores (max across classes)
- Filter by confidence threshold (0.5)
- Convert center-based boxes to corner format
- Apply Non-Maximum Suppression (NMS) with threshold 0.4
- Normalize coordinates to [0, 1] range

### 6. Detection Recording

When a pothole is detected (confidence > 0.5):

```python
def save_detection(frame, box, score):
    # Save raw frame (no bbox drawing for performance)
    filename = f"detect_{timestamp}_{score:.2f}.jpg"

    # Convert RGB to BGR for OpenCV
    out_img = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
    cv2.imwrite(filename, out_img)

    # Save detection metadata separately
    metadata = {
        'bbox': box,  # [ymin, xmin, ymax, xmax]
        'score': float(score),
        'timestamp': timestamp
    }
```

**Why no bounding box visualization?**

Drawing rectangles and text with OpenCV (`cv2.rectangle()`, `cv2.putText()`) is computationally expensive on the Raspberry Pi Zero 2 WH:

- **Image copying**: `frame.copy()` duplicates memory
- **Rectangle drawing**: Anti-aliasing and pixel manipulation
- **Text rendering**: Font rasterization is CPU-intensive
- **Total overhead**: ~50-100ms per detection on Pi Zero 2

This overhead would cause:

- Frame drops in video recording
- Delayed inference on subsequent frames
- System instability during multiple simultaneous detections

**Solution**: Save raw images during flight, add annotations during post-processing on a laptop/desktop.

## Code Walkthrough

### Configuration Section

```python
SERIAL_PORT = '/dev/ttyS0'      # Raspberry Pi UART
BAUD_RATE = 115200              # Betaflight default
VIDEO_PATH = "/home/tpu/Videos/" # Output directory
MODEL_PATH = "/home/tpu/drone_script/best_int8.tflite"
AUX_CHANNEL_INDEX = 8           # AUX8 = index 8
TRIGGER_VALUE = 1500            # PWM threshold
CONFIDENCE_THRESHOLD = 0.5      # Min detection confidence
NMS_THRESHOLD = 0.4             # NMS IoU threshold
```

### Serial Communication

```python
# Initialize serial port
ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=0.1)

# MSP command structure: $ M < size command checksum
MSP_RC_REQUEST = b'$M<\x00\x69\x69'

def get_rc_channels():
    """Read RC channel values via MSP protocol"""
    ser.reset_input_buffer()
    ser.write(MSP_RC_REQUEST)

    # Parse response: $ M > size command payload checksum
    header = ser.read(5)
    if header[:3] != b'$M>':
        return None

    size = header[3]
    payload = ser.read(size)
    checksum = ser.read(1)

    # Unpack 16-bit channel values
    count = size // 2
    return struct.unpack('<' + 'H'*count, payload)
```

### AI Model Setup

```python
# Load model with Edge TPU delegate
interpreter = Interpreter(
    model_path=MODEL_PATH,
    experimental_delegates=[load_delegate('libedgetpu.so.1')]
)
interpreter.allocate_tensors()

# Get model metadata
input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()
_, input_height, input_width, _ = input_details[0]['shape']
input_type = input_details[0]['dtype']  # np.int8 for quantized
```

### Camera Configuration

```python
picam2 = Picamera2()
config = picam2.create_video_configuration(
    main={"size": (1920, 1080), "format": "YUV420"},
    lores={"size": (input_width, input_height), "format": "YUV420"},
    buffer_count=3  # Triple buffering
)
picam2.configure(config)
picam2.start()
```

### Recording Control

```python
encoder = H264Encoder()
recording = False
current_filename = ""

# Start recording
unique_id = str(uuid.uuid4())[:8]
current_filename = f"{VIDEO_PATH}flight_{timestamp}_{unique_id}.h264"
picam2.start_recording(encoder, current_filename)
recording = True

# Stop recording
picam2.stop_recording()
recording = False
```

### Detection Saving (Performance Optimized)

```python
def save_detection(frame, box, score):
    """Save raw detection without visualization overhead"""
    # Convert RGB to BGR (OpenCV format)
    out_img = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

    # Save immediately without drawing
    filename = f"{VIDEO_PATH}detect_{int(time.time())}_{score:.2f}.jpg"
    cv2.imwrite(filename, out_img)
    print(f"[AI] Pothole detected! Saved: {filename}")

# Note: cv2.rectangle() and cv2.putText() intentionally omitted
# Drawing adds 50-100ms overhead on Pi Zero 2 WH
```

## Configuration Options

### Serial Communication

| Parameter     | Value        | Description                  |
| ------------- | ------------ | ---------------------------- |
| `SERIAL_PORT` | `/dev/ttyS0` | Raspberry Pi UART port       |
| `BAUD_RATE`   | `115200`     | Must match INAV MSP settings |

**To change serial port:**

```bash
# Enable UART on GPIO 14/15
sudo raspi-config
# Interface Options → Serial Port → Disable login shell, Enable hardware
```

### Recording Trigger

| Parameter           | Default | Description                                  |
| ------------------- | ------- | -------------------------------------------- |
| `AUX_CHANNEL_INDEX` | `8`     | RC channel for recording control (0-indexed) |
| `TRIGGER_VALUE`     | `1500`  | PWM value threshold (1000-2000)              |

**To use different channel:**

- Channels are 0-indexed: AUX1=4, AUX2=5, ..., AUX8=11
- Configure in INAV Configurator: Modes tab → Set switch position

### AI Detection

| Parameter              | Default            | Description                            |
| ---------------------- | ------------------ | -------------------------------------- |
| `MODEL_PATH`           | `best_int8.tflite` | Path to TFLite model                   |
| `CONFIDENCE_THRESHOLD` | `0.5`              | Minimum detection confidence (0.0-1.0) |
| `NMS_THRESHOLD`        | `0.4`              | Non-Maximum Suppression IoU threshold  |

**To adjust sensitivity:**

- Lower `CONFIDENCE_THRESHOLD` (e.g., 0.3) → More detections, more false positives
- Higher `CONFIDENCE_THRESHOLD` (e.g., 0.7) → Fewer detections, more reliable

### Video Settings

| Parameter            | Default             | Description       |
| -------------------- | ------------------- | ----------------- |
| `VIDEO_PATH`         | `/home/tpu/Videos/` | Output directory  |
| Main resolution      | `1920x1080`         | Recording quality |
| Inference resolution | `320x320`           | Model input size  |

**To change video quality:**

```python
config = picam2.create_video_configuration(
    main={"size": (1280, 720), "format": "YUV420"},  # 720p
    # or
    main={"size": (2592, 1944), "format": "YUV420"},  # Max resolution
)
```

## Usage Instructions

### Installation

**1. Install dependencies:**

```bash
sudo apt update
sudo apt install -y python3-opencv python3-serial

# Install TFLite runtime
pip3 install tflite-runtime

# Install Edge TPU library
echo "deb https://packages.cloud.google.com/apt coral-edgetpu-stable main" | \
sudo tee /etc/apt/sources.list.d/coral-edgetpu.list
curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | sudo apt-key add -
sudo apt update
sudo apt install libedgetpu1-std python3-pycoral

# Install Picamera2
sudo apt install -y python3-picamera2
```

**2. Enable UART:**

```bash
sudo raspi-config
# Interface Options → Serial Port
# - Disable login shell over serial
# - Enable serial port hardware
sudo reboot
```

**3. Connect hardware:**

- Flight controller TX → Pi GPIO 15 (RXD)
- Flight controller RX → Pi GPIO 14 (TXD)
- Flight controller GND → Pi GND
- Camera module → CSI port
- Coral TPU → USB port

**4. Prepare model:**

```bash
# Copy your trained model
sudo mkdir -p /home/tpu/drone_script
sudo cp best_int8.tflite /home/tpu/drone_script/

# Create video directory
sudo mkdir -p /home/tpu/Videos
sudo chmod 777 /home/tpu/Videos
```

### Running the Script

**Manual start:**

```bash
cd /path/to/script
python3 camera_control.py
```

**Run on boot (systemd service):**

```bash
sudo nano /etc/systemd/system/camera-control.service
```

Add:

```ini
[Unit]
Description=AI Drone Camera Control
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi
ExecStart=/usr/bin/python3 /home/pi/camera_control.py
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
```

Enable service:

```bash
sudo systemctl daemon-reload
sudo systemctl enable camera-control.service
sudo systemctl start camera-control.service

# Check status
sudo systemctl status camera-control.service

# View logs
journalctl -u camera-control.service -f
```

### Operation

1. **Power on the drone**

   - Script auto-starts (if configured as service)
   - Wait for "Ready. Waiting for RC switch..." message

2. **Arm the drone and take off**

   - Normal flight operation

3. **Enable recording**

   - Flip AUX8 switch to ON position (>1500)
   - Console shows: `[REC] Starting: flight_<timestamp>_<uuid>.h264`
   - AI detection begins automatically

4. **Fly over target area**

   - Video records to main stream
   - AI processes lores stream in real-time
   - Detections saved as raw images: `detect_<timestamp>_<score>.jpg`
   - Bounding boxes NOT drawn to save processing resources

5. **Disable recording**

   - Flip AUX8 switch to OFF position (<1500)
   - Console shows: `[REC] Stopping.`
   - Video file saved

6. **Land and disarm**
   - Power off drone
   - Retrieve video files from `/home/tpu/Videos/`

### Output Files

**Video recordings:**

```
flight_1705232145_a3f7d89c.h264
```

- Timestamp: Unix epoch time
- UUID: 8-character unique ID
- Format: H.264 elementary stream

**Detection images:**

```
detect_1705232156_0.87.jpg
```

- Timestamp: Unix epoch time
- Score: Detection confidence (0.00-1.00)
- Format: Raw JPEG (no bounding box overlay for performance)
- Bounding box coordinates stored in memory during flight

**Convert H.264 to MP4:**

```bash
ffmpeg -framerate 30 -i flight_1705232145_a3f7d89c.h264 \
       -c copy output.mp4
```

## Troubleshooting

### Serial Communication Issues

**Problem: No RC channels received**

```bash
# Check serial port
ls -l /dev/ttyS0
# Should show: crw-rw---- 1 root dialout

# Add user to dialout group
sudo usermod -a -G dialout $USER
sudo reboot

# Test serial connection
sudo apt install minicom
minicom -D /dev/ttyS0 -b 115200
```

**Problem: Wrong channel values**

- Verify `BAUD_RATE` matches INAV configuration
- Check flight controller MSP port configuration (INAV Configurator → Ports tab)
- Try different UART pins (GPIO 14/15)

### Camera Issues

**Problem: Camera not detected**

```bash
# Check camera connection
vcgencmd get_camera
# Should show: supported=1 detected=1

# Enable camera
sudo raspi-config
# Interface Options → Legacy Camera → Enable
sudo reboot

# Test camera
libcamera-hello
```

**Problem: Frame drops or stuttering**

- Reduce main stream resolution to 720p
- Increase `buffer_count` to 4 or 5
- Lower inference frequency (skip frames)

### AI Model Issues

**Problem: Edge TPU not found**

```bash
# Check USB connection
lsusb | grep "Google"
# Should show: "Global Unichip Corp."

# Reinstall driver
sudo apt install --reinstall libedgetpu1-std

# Check library
python3 -c "from tflite_runtime.interpreter import load_delegate; \
            print(load_delegate('libedgetpu.so.1'))"
```

**Problem: Low detection accuracy**

- Adjust `CONFIDENCE_THRESHOLD` (try 0.3-0.7)
- Retrain model with more diverse dataset
- Check lighting conditions (model trained on)
- Verify model quantization didn't lose accuracy

**Problem: Model loading fails**

```bash
# Verify model file
ls -lh /home/tpu/drone_script/best_int8.tflite

# Check model format
python3 -c "from tflite_runtime.interpreter import Interpreter; \
            print(Interpreter(model_path='best_int8.tflite'))"

# Ensure model is Edge TPU compiled
# File should have _edgetpu suffix or compiled with edgetpu_compiler
```

### Recording Issues

**Problem: Video files not created**

```bash
# Check directory permissions
ls -ld /home/tpu/Videos
sudo chmod 777 /home/tpu/Videos

# Check disk space
df -h

# Monitor for errors
python3 camera_control.py 2>&1 | tee debug.log
```

**Problem: Video playback issues**

```bash
# Convert to MP4
ffmpeg -framerate 30 -i input.h264 -c copy output.mp4

# Or transcode
ffmpeg -i input.h264 -c:v libx264 -preset fast output.mp4
```

## Advanced Features

### Post-Processing: Add Bounding Boxes (Off-drone)

Since bounding boxes aren't drawn during flight for performance reasons, you can add them during post-processing on a more powerful computer:

```python
import cv2
import json
import glob

def add_bboxes_postprocessing(image_dir, metadata_file):
    """Draw bounding boxes on images after flight"""
    # Load detection metadata
    with open(metadata_file, 'r') as f:
        detections = json.load(f)

    for detection in detections:
        img_path = detection['image']
        box = detection['bbox']  # [ymin, xmin, ymax, xmax]
        score = detection['score']

        # Load image
        img = cv2.imread(img_path)
        h, w = img.shape[:2]

        # Draw bbox
        ymin, xmin, ymax, xmax = box
        start = (int(xmin * w), int(ymin * h))
        end = (int(xmax * w), int(ymax * h))
        cv2.rectangle(img, start, end, (0, 0, 255), 2)

        # Add label
        label = f"Pothole: {score:.2f}"
        cv2.putText(img, label, (start[0], start[1]-10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

        # Save annotated version
        output = img_path.replace('.jpg', '_annotated.jpg')
        cv2.imwrite(output, img)
        print(f"Saved: {output}")

# Usage after flight
add_bboxes_postprocessing('/home/tpu/Videos/', 'detections.json')
```

### Add GPS Coordinates to Detections

```python
import serial
import pynmea2

# Open GPS serial port
gps_ser = serial.Serial('/dev/ttyAMA1', 9600, timeout=1)

def get_gps_position():
    """Read current GPS position"""
    line = gps_ser.readline().decode('ascii', errors='replace')
    if line.startswith('$GPGGA'):
        msg = pynmea2.parse(line)
        return msg.latitude, msg.longitude, msg.altitude
    return None, None, None

def save_detection_with_gps(frame, box, score):
    """Save detection with GPS metadata (no bbox drawing for performance)"""
    lat, lon, alt = get_gps_position()

    # Save raw image
    filename = f"detect_{time.time()}_{score:.2f}.jpg"
    out_img = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
    cv2.imwrite(filename, out_img)

    # Save metadata
    metadata = {
        'timestamp': time.time(),
        'score': float(score),
        'bbox': box,
        'gps': {'lat': lat, 'lon': lon, 'alt': alt}
    }

    json_file = filename.replace('.jpg', '.json')
    with open(json_file, 'w') as f:
        json.dump(metadata, f, indent=2)
```

### Multiple Detection Classes

```python
# Update labels
LABELS = ['pothole', 'crack', 'manhole', 'patch']

def yolo_postprocess(output_data, conf_thresh, nms_thresh):
    """Support multiple classes"""
    predictions = np.transpose(output_data[0])

    # Get class with max score for each detection
    class_ids = np.argmax(predictions[:, 4:], axis=1)
    scores = np.max(predictions[:, 4:], axis=1)

    # Rest of processing...
    final_classes.append(int(class_ids[i]))

    return final_boxes, final_classes, final_scores

def save_detection(frame, box, score, class_id):
    """Save raw image with metadata (no visual overlay)"""
    filename = f"detect_{time.time()}_{score:.2f}_{LABELS[class_id]}.jpg"
    out_img = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
    cv2.imwrite(filename, out_img)
    # Save metadata with class info to JSON...
```

### Frame Skipping for Performance

```python
frame_counter = 0
INFERENCE_INTERVAL = 3  # Run inference every 3rd frame

if recording:
    frame_counter += 1
    if frame_counter % INFERENCE_INTERVAL == 0:
        # Run inference
        yuv_frame = picam2.capture_array("lores")
        # Process...
```

### Telemetry Logging

```python
import csv

telemetry_file = None
telemetry_writer = None

def start_telemetry_log(filename):
    """Start logging telemetry data"""
    global telemetry_file, telemetry_writer
    telemetry_file = open(filename.replace('.h264', '.csv'), 'w')
    telemetry_writer = csv.writer(telemetry_file)
    telemetry_writer.writerow([
        'timestamp', 'throttle', 'roll', 'pitch', 'yaw',
        'detections', 'inference_time_ms'
    ])

def log_telemetry(channels, detections, inference_time):
    """Log telemetry row"""
    if telemetry_writer:
        telemetry_writer.writerow([
            time.time(),
            channels[2],  # Throttle
            channels[0],  # Roll
            channels[1],  # Pitch
            channels[3],  # Yaw
            len(detections),
            inference_time * 1000
        ])
```

## Next Steps

- **[AI Model Training](../ai-applications/datasets.html)** - Train custom detection models
- **[Hardware Setup](../hardware/setup.html)** - Complete system integration
- **[Flight Testing](../tutorials/getting-started.html)** - First flight procedures

## Reference

### MSP Protocol Resources

- [INAV MSP Documentation](https://github.com/iNavFlight/inav/wiki/MSP-V2)
- [MSP Commands Reference](https://github.com/iNavFlight/inav/wiki/MSP-Navigation-Messages)

### Picamera2 Documentation

- [Picamera2 Manual](https://datasheets.raspberrypi.com/camera/picamera2-manual.pdf)
- [Picamera2 Examples](https://github.com/raspberrypi/picamera2/tree/main/examples)

### Edge TPU Resources

- [Coral USB Accelerator](https://coral.ai/products/accelerator)
- [TFLite Model Optimization](https://www.tensorflow.org/lite/performance/model_optimization)

---

[← Back to Software](../software/installation.html) | [← Back to Home](../)
