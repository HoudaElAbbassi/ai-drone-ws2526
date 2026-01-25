from ultralytics import YOLO
import os
import sys
from dotenv import load_dotenv

# Add parent directory to path to import utilities
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utilities.utils import get_device


def export_model(model_path, device, device_name, format='tflite', imgsz=320):
    """
    Export trained model to TFLite for Raspberry Pi deployment.
    """
    print(f"Loading model from: {model_path}")
    model = YOLO(model_path)

    # Check original model size
    original_size = os.path.getsize(model_path) / (1024 ** 2)
    print(f"Original model size: {original_size:.2f} MB")

    print(f"\nExporting to {format} format with INT8 quantization...")
    print(f"Using device: {device_name}")
    print(f"Image size: {imgsz}x{imgsz}")
    print("This will reduce model size by ~75%")

    export_path = model.export(
        format=format,
        int8=True,  # INT8 quantization for size reduction
        imgsz=imgsz,  # Smaller size for faster inference
        device=device,  # Use detected device
        optimize=True,  # Additional optimizations
        simplify=True,  # Simplify model structure
        data='../dataset/data.yaml'
    )

    # Check exported model size
    if os.path.exists(export_path):
        exported_size = os.path.getsize(export_path) / (1024 ** 2)
        reduction = ((original_size - exported_size) / original_size) * 100

        print(f"\n{'=' * 60}")
        print("EXPORT COMPLETE!")
        print(f"{'=' * 60}")
        print(f"Original model size: {original_size:.2f} MB")
        print(f"Exported model size: {exported_size:.2f} MB")
        print(f"Size reduction: {reduction:.1f}%")
        print(f"Model saved to: {export_path}")
        print(f"\n✅ This {exported_size:.2f}MB model is perfect for Pi Zero 2 WH!")
        print(f"{'=' * 60}")
        print("\nNext steps for Raspberry Pi deployment:")
        print("1. Transfer the .tflite file to your Raspberry Pi Zero 2 WH")
        print("2. Install Edge TPU Compiler:")
        print("   curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | sudo apt-key add -")
        print("   echo 'deb https://packages.cloud.google.com/apt coral-edgetpu-stable main' | sudo tee /etc/apt/sources.list.d/coral-edgetpu.list")
        print("   sudo apt-get update")
        print("   sudo apt-get install edgetpu-compiler")
        print("3. Convert to EdgeTPU format:")
        print(f"   edgetpu_compiler {os.path.basename(export_path)}")
        print("4. Use the generated _edgetpu.tflite file with Google Coral USB Accelerator")
        print(f"{'=' * 60}")

    return export_path


if __name__ == "__main__":
    load_dotenv()

    # Configuration
    PROJECT = os.getenv('ROBOFLOW_PROJECT')
    PROJECT_NAME = os.getenv('ROBOFLOW_PROJECT_NAME') or PROJECT

    MODEL_PATH = f'../train/runs/detect/{PROJECT_NAME}/weights/best.pt'
    EXPORT_FORMAT = 'tflite'  # For Raspberry Pi + Coral
    IMG_SIZE = 320  # Smaller size for edge devices

    # Get device
    """device, device_name = get_device()"""

    # Force CPU for export (optimize=True requires CPU)
    device = 'cpu'
    device_name = 'CPU'
    print("Using CPU for export (required for optimize=True with TFLite)")

    export_model(MODEL_PATH, device, device_name, EXPORT_FORMAT, IMG_SIZE)
