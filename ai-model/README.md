# Pothole Detection with YOLOv8

**[English]** | **[Deutsch](README.de.md)**

A complete machine learning pipeline for training, exporting, and deploying a pothole detection model optimized for **Raspberry Pi Zero 2 WH** with **Google Coral TPU accelerator**.

## Overview

This project trains an AI model using **YOLOv8** (You Only Look Once version 8) to detect potholes in images and video streams. The trained model is then exported to **TensorFlow Lite** format with INT8 quantization, making it lightweight and efficient enough to run on edge devices like the Raspberry Pi Zero 2 WH with hardware acceleration via Google Coral USB Accelerator.

### Why YOLOv8?

**YOLO (You Only Look Once)** is a state-of-the-art, real-time object detection algorithm. We use **YOLOv8n** (the nano variant) because:

- **Speed**: Single-pass detection makes it ideal for real-time applications
- **Efficiency**: The 'n' (nano) variant is the smallest and fastest, perfect for edge devices
- **Accuracy**: Despite its small size, it maintains excellent detection performance
- **Edge-Ready**: Easily exportable to TensorFlow Lite for deployment on resource-constrained devices

### Python Version Requirements

**Python 3.9 - 3.12** is required due to dependencies from the `ultralytics` library (YOLOv8 implementation) and compatibility with PyTorch, TensorFlow Lite, and other ML frameworks.

---

## Project Structure

```
.
├── .env.example              # Environment variables template
├── train/                    # Training scripts
│   ├── train.py             # Main training script
│   └── validate.py          # Model validation script
├── utilities/               # Helper utilities
│   ├── export_model.py      # Model export to TFLite
│   └── utils.py            # Shared utility functions
└── detect/                  # Detection scripts for testing
    ├── detect_video.py      # Detect potholes in video files
    └── detect_webcam.py     # Real-time webcam detection
```

---

## Configuration

### `.env.example`

Copy `.env.example` to `.env` and configure the following variables:

```bash
ROBOFLOW_API_KEY=          # Your Roboflow API key for dataset download
ROBOFLOW_WORKSPACE=        # Your Roboflow workspace name
ROBOFLOW_PROJECT=          # Your Roboflow project identifier
ROBOFLOW_PROJECT_NAME=     # Human-readable project name (optional, defaults to PROJECT)
ROBOFLOW_PROJECT_VERSION=  # Dataset version number (e.g., "1")
```

These variables connect to your Roboflow account to automatically download the labeled pothole dataset for training.

---

## Training

### `train/train.py`

Trains a YOLOv8n model on your pothole dataset. Automatically downloads the dataset from Roboflow if not present.

**Key Features:**
- Auto-detects available hardware (CUDA GPU, Apple MPS, or CPU)
- Downloads dataset from Roboflow automatically
- Configurable hyperparameters for optimal training

**Training Parameters** (`model.train()`):

| Parameter | Value | Description |
|-----------|-------|-------------|
| `data` | `yaml_path` | Path to dataset configuration YAML |
| `epochs` | `300` | Number of training epochs |
| `imgsz` | `640` | Input image size (640x640 pixels) |
| `batch` | `16` | Batch size for training |
| `name` | `PROJECT_NAME` | Name for the training run |
| `project` | `'./runs/detect'` | Directory to save training results |
| `patience` | `50` | Early stopping patience (stops if no improvement) |
| `save` | `True` | Save checkpoints during training |
| `device` | Auto-detected | Device to train on (GPU/CPU/MPS) |
| `workers` | `2` (GPU) or `0` (CPU) | Number of data loading workers |
| `cache` | `'disk'` | Cache images to disk for faster loading |
| `amp` | `True` (GPU only) | Automatic Mixed Precision training |
| `lr0` | `0.01` | Initial learning rate |
| `lrf` | `0.1` | Final learning rate factor (lr0 * lrf = final lr) |
| `warmup_epochs` | `5` | Learning rate warmup epochs |
| `box` | `7.5` | Box loss weight (bounding box regression) |
| `cls` | `1.0` | Classification loss weight |

**Usage:**
```bash
cd train
python train.py
```

**Output:** Trained model saved to `train/runs/detect/{PROJECT_NAME}/weights/best.pt`

---

### `train/validate.py`

Validates the trained model on the test/validation dataset to evaluate performance.

**Metrics Reported:**
- **mAP50**: Mean Average Precision at IoU threshold 0.50
- **mAP50-95**: Mean Average Precision across IoU thresholds 0.50 to 0.95
- **Precision**: Ratio of true positives to all positive predictions
- **Recall**: Ratio of true positives to all actual positives

**Understanding IoU (Intersection over Union):**

IoU measures how well a predicted bounding box overlaps with the ground truth (actual) bounding box:

```
IoU = Area of Overlap / Area of Union
```

- **IoU = 1.0** (100%): Perfect match - predicted box exactly matches ground truth
- **IoU = 0.5** (50%): Decent overlap - commonly used as minimum threshold
- **IoU = 0.0** (0%): No overlap at all

**In the metrics above:**
- **mAP50**: A detection counts as "correct" if IoU ≥ 0.5 (more lenient, allows some positioning error)
- **mAP50-95**: Averaged across IoU thresholds from 0.50 to 0.95 in steps of 0.05 (stricter, requires precise bounding boxes)

Higher IoU thresholds demand more precise detections. For pothole detection, an IoU of 0.7+ indicates good localization, while 0.9+ is excellent.

**Usage:**
```bash
cd train
python validate.py
```

---

## Model Export

### `utilities/export_model.py`

Exports the trained PyTorch model to **TensorFlow Lite** format optimized for Raspberry Pi deployment.

**Export Parameters** (`model.export()`):

| Parameter | Value | Description |
|-----------|-------|-------------|
| `format` | `'tflite'` | Export to TensorFlow Lite format |
| `int8` | `True` | Enable INT8 quantization (~75% size reduction) |
| `imgsz` | `320` | Reduced image size for faster inference on edge devices |
| `device` | `'cpu'` | Force CPU for export (required for TFLite optimization) |
| `optimize` | `True` | Apply additional TFLite optimizations |
| `simplify` | `True` | Simplify the model graph structure |
| `data` | `'../dataset/data.yaml'` | Dataset YAML for calibration during quantization |

**INT8 Quantization:** Converts 32-bit floating-point weights to 8-bit integers, dramatically reducing model size (~4x smaller) while maintaining accuracy. Essential for edge deployment.

**Usage:**
```bash
cd utilities
python export_model.py
```

**Output:** 
- Quantized TFLite model saved to `train/runs/detect/{PROJECT_NAME}/weights/best_saved_model/best_int8.tflite`
- Instructions printed for Edge TPU compilation on Raspberry Pi

**Next Steps (on Raspberry Pi):**
1. Transfer the `.tflite` file to your Raspberry Pi
2. Install Edge TPU Compiler
3. Compile for Coral TPU: `edgetpu_compiler best_int8.tflite`
4. Use the generated `*_edgetpu.tflite` file with Coral USB Accelerator

---

## Utilities

### `utilities/utils.py`

Shared utility functions used across the project:

**Functions:**

- **`get_device()`**: Auto-detects the best available compute device
  - Returns: `(device, device_name)` tuple
  - Priority: CUDA GPU > Apple MPS > CPU
  
- **`update_yaml_classes(yaml_path, class_names, verbose=True)`**: Updates class names in the YOLO dataset YAML file
  - Useful for renaming detection classes after dataset download

---

## Detection & Testing

### `detect/detect_video.py`

Processes video files and annotates detected potholes frame-by-frame.

**Features:**
- Supports both `.pt` (PyTorch) and `.tflite` (TensorFlow Lite) models
- Configurable confidence threshold
- Progress tracking with frame counter
- Saves annotated video output

**Usage:**
```bash
cd detect
python detect_video.py
```

**Configuration:** Edit the script to set `VIDEO_PATH`, `OUTPUT_PATH`, and `MODEL_PATH`.

---

### `detect/detect_webcam.py`

Real-time pothole detection using a connected webcam.

**Features:**
- Live video stream processing
- Supports both `.pt` and `.tflite` models
- Press 'q' to quit
- Frame counter for performance monitoring

**Usage:**
```bash
cd detect
python detect_webcam.py
```

**Configuration:** Edit the script to set `MODEL_PATH` and `CONFIDENCE` threshold.

---

## Installation

```bash
# Install dependencies
pip install ultralytics roboflow opencv-python python-dotenv

# Configure environment
cp .env.example .env
# Edit .env with your Roboflow credentials

# Train model
cd train
python train.py

# Validate model
python validate.py

# Export for Raspberry Pi
cd ../utilities
python export_model.py

# Test with video or webcam
cd ../detect
python detect_webcam.py
```

---

## Hardware Acceleration

The exported TFLite model can leverage the **Google Coral USB Accelerator** for up to **10x faster inference** on the Raspberry Pi Zero 2 WH. After running the Edge TPU compiler, the model will automatically utilize the TPU when available.

---

## License

This project is provided as-is for educational and research purposes.