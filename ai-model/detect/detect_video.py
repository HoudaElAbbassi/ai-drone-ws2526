from ultralytics import YOLO
import cv2
import os
import sys
from dotenv import load_dotenv

# Add parent directory to path to import utilities
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utilities.utils import get_device


def detect_video(model_path, video_path, output_path, device, device_name, conf=0.3):
    """
    Detect road damage in a video file
    """
    # Load model
    print(f"Loading model from: {model_path}")
    if model_path.endswith('.tflite'):
        model = YOLO(model_path, task='detect')
    else:
        model = YOLO(model_path)

    # Open video
    cap = cv2.VideoCapture(video_path)

    if not cap.isOpened():
        print(f"Error: Cannot open video {video_path}")
        return

    # Get video properties
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    # Setup video writer
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

    print(f"Processing video: {video_path}")
    print(f"Total frames: {total_frames}")
    print(f"Output will be saved to: {output_path}")
    print(f"Using device: {device_name}")

    frame_count = 0

    while cap.isOpened():
        ret, frame = cap.read()

        if not ret:
            break

        # Run detection
        results = model.predict(frame, conf=conf, device=device, verbose=False)

        # Annotate frame
        annotated_frame = results[0].plot()

        # Write frame
        out.write(annotated_frame)

        frame_count += 1

        # Progress indicator
        if frame_count % 30 == 0:
            progress = (frame_count / total_frames) * 100
            print(f"Processed {frame_count}/{total_frames} frames ({progress:.1f}%)...")

    cap.release()
    out.release()

    print(f"\nVideo processing complete! Total frames processed: {frame_count}")
    print(f"Output saved to: {output_path}")


if __name__ == "__main__":
    load_dotenv()

    # Get device
    device, device_name = get_device()

    # Configuration
    PROJECT = os.getenv('ROBOFLOW_PROJECT')
    PROJECT_NAME = os.getenv('ROBOFLOW_PROJECT_NAME') or PROJECT
    VIDEO_PATH = '../video/1.mp4'
    OUTPUT_PATH = '../video/1_annotated.mp4'
    CONFIDENCE = 0.3

    # Choose model format: .pt (PyTorch) or .tflite (TensorFlow Lite)
    # MODEL_PATH = f'./runs/detect/{PROJECT_NAME}/weights/best.pt'
    MODEL_PATH = f'../train/runs/detect/{PROJECT_NAME}/weights/best_saved_model/best_int8.tflite'

    detect_video(MODEL_PATH, VIDEO_PATH, OUTPUT_PATH, device, device_name, CONFIDENCE)
