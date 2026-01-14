from ultralytics import YOLO
from utilities.utils import get_device
import os
from dotenv import load_dotenv


def validate_model(model_path, data_yaml):
    """
    Validate trained model on test/validation set.
    """
    print(f"Loading model from: {model_path}")
    model = YOLO(model_path)

    print(f"Running validation on {device_name}...")
    metrics = model.val(data=data_yaml, device=device)

    # Print results
    print("\n" + "=" * 50)
    print("VALIDATION RESULTS")
    print("=" * 50)
    print(f"mAP50:     {metrics.box.map50:.4f}")
    print(f"mAP50-95:  {metrics.box.map:.4f}")
    print(f"Precision: {metrics.box.mp:.4f}")
    print(f"Recall:    {metrics.box.mr:.4f}")
    print("=" * 50)

    return metrics


if __name__ == "__main__":
    load_dotenv()
    # Configuration
    PROJECT = os.getenv('ROBOFLOW_PROJECT')
    PROJECT_NAME = os.getenv('ROBOFLOW_PROJECT_NAME') or PROJECT
    MODEL_PATH = f'./runs/detect/{PROJECT_NAME}/weights/best.pt'
    DATA_YAML = '../dataset/data.yaml'

    # Get device
    device, device_name = get_device()

    validate_model(MODEL_PATH, DATA_YAML)
