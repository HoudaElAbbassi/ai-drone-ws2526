from ultralytics import YOLO
from roboflow import Roboflow
import os
import yaml
from dotenv import load_dotenv
from ..utilities.utils import get_device, update_yaml_classes

if __name__ == "__main__":
    # Load environment variables from .env file
    load_dotenv()

    # Configuration
    DATASET_DIR = '../dataset'
    API_KEY = os.getenv('ROBOFLOW_API_KEY')
    WORKSPACE = os.getenv('ROBOFLOW_WORKSPACE')
    PROJECT = os.getenv('ROBOFLOW_PROJECT')
    PROJECT_NAME = os.getenv('ROBOFLOW_PROJECT_NAME') or PROJECT
    VERSION = os.getenv('ROBOFLOW_PROJECT_VERSION')
    yaml_path = f'{DATASET_DIR}/data.yaml'

    # Validate env
    missing = []
    if not API_KEY:
        missing.append('ROBOFLOW_API_KEY')
    if not WORKSPACE:
        missing.append('ROBOFLOW_WORKSPACE')
    if not PROJECT:
        missing.append('ROBOFLOW_PROJECT')
    if not VERSION:
        missing.append('PROJECT_VERSION')

    if missing:
        raise ValueError(f"Missing required environment variables: {', '.join(missing)}")

    # Get device
    device, device_name = get_device()

    # Download dataset if missing
    if not os.path.exists(DATASET_DIR):
        print("Downloading severity dataset from Roboflow...")
        rf = Roboflow(api_key=API_KEY)
        project = rf.workspace(WORKSPACE).project(PROJECT)
        dataset = project.version(VERSION).download("yolov8", location=DATASET_DIR)
        print(f"Dataset downloaded to: {dataset.location}")
    else:
        print(f"Dataset already exists at {DATASET_DIR}. Skipping download.")

    # Rename classes
    #update_yaml_classes(yaml_path, ['light', 'medium', 'severe'])

    # Load model
    print("Loading YOLOv8n model...")
    model = YOLO('yolov8n.pt')

    # Start training with improvements
    print(f"Starting training on {device_name}...")

    results = model.train(
        data=yaml_path,
        epochs=300,
        imgsz=640,
        batch=16,
        name=PROJECT_NAME,
        project='./runs/detect',
        patience=50,
        save=True,
        device=device,
        workers=2 if device == 0 else 0,
        cache='disk',
        amp=True if device == 0 else False,
        # Core hyperparameters (all officially supported in YOLOv8)
        lr0=0.01,  # Initial learning rate
        lrf=0.1,  # Final learning rate factor
        warmup_epochs=5,  # Warmup epochs
        box=7.5,  # Box loss weight
        cls=1.0  # Classification loss weight
    )

    print("Training complete!")
    print(f"Best model saved at: runs/detect/{PROJECT_NAME}/weights/best.pt")
