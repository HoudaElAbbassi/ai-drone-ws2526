from ultralytics import YOLO
import cv2
import os
from dotenv import load_dotenv
from utilities.utils import get_device


def detect_webcam(model_path, device, conf=0.5):
    """
    Real-time road damage detection using webcam.

    Args:
        model_path (str): Path to the YOLO model weights (.pt or .tflite)
        device (str): Device to run inference on ('cuda', 'cpu', 'mps', etc.)
        conf (float): Confidence threshold for detections
    """
    # Load model (works with both .pt and .tflite)
    print(f"Loading model from: {model_path}")
    if model_path.endswith('.tflite'):
        model = YOLO(model_path, task='detect')  # Explicit task for TFLite
    else:
        model = YOLO(model_path)

    # Open webcam
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("Error: Cannot access webcam")
        return

    print("Starting webcam detection...")
    print(f"Using device: {device}")
    print("Press 'q' to quit")

    frame_count = 0

    while True:
        ret, frame = cap.read()

        if not ret:
            print("Error: Failed to grab frame")
            break

        # Run detection
        results = model.predict(frame, conf=conf, device=device, verbose=False)

        # Annotate frame
        annotated_frame = results[0].plot()

        # Add FPS counter
        frame_count += 1
        if frame_count % 30 == 0:
            print(f"Processed {frame_count} frames...")

        # Display
        cv2.imshow('Road Damage Detector - Press Q to Quit', annotated_frame)

        # Exit on 'q'
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    print(f"Webcam detection stopped. Total frames processed: {frame_count}")


if __name__ == "__main__":
    load_dotenv()

    # Get device
    device, device_name = get_device()

    # Configuration
    PROJECT = os.getenv('ROBOFLOW_PROJECT')
    PROJECT_NAME = os.getenv('ROBOFLOW_PROJECT_NAME') or PROJECT

    # Choose model format: .pt (PyTorch) or .tflite (TensorFlow Lite)
    # MODEL_PATH = f'./runs/detect/{PROJECT_NAME}/weights/best.pt'
    MODEL_PATH = f'../train/runs/detect/{PROJECT_NAME}/weights/best_saved_model/best_int8.tflite'

    CONFIDENCE = 0.3

    detect_webcam(MODEL_PATH, device, CONFIDENCE)
