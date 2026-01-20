import torch
import yaml


def get_device():
    """
    Auto-detect the best available device (CUDA GPU, Apple MPS, or CPU).

    Returns:
        tuple: (device, device_name) where device is the PyTorch device identifier
               and device_name is a human-readable string.
    """
    if torch.cuda.is_available():
        device = 0
        device_name = torch.cuda.get_device_name(0)
        print(f"Using CUDA GPU: {device_name}")
    elif torch.backends.mps.is_available():
        device = 'mps'
        device_name = 'Apple MPS'
        print("Using Apple MPS (Metal Performance Shaders)")
    else:
        device = 'cpu'
        device_name = 'CPU'
        print("Using CPU (no GPU detected)")

    return device, device_name


def update_yaml_classes(yaml_path, class_names, verbose=True):
    """
    Update class names in a YOLO dataset YAML file.

    Args:
        yaml_path (str): Path to the data.yaml file
        class_names (list): List of new class names
        verbose (bool): Whether to print status messages (default: True)

    Returns:
        list: The updated class names
    """
    if verbose:
        print(f"Updating class names in {yaml_path}...")

    with open(yaml_path, 'r') as file:
        data = yaml.safe_load(file)

    data['names'] = class_names

    with open(yaml_path, 'w') as file:
        yaml.dump(data, file)

    if verbose:
        print(f"Class names updated to: {data['names']}")

    return data['names']
