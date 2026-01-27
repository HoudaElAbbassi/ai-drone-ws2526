---
layout: default
title: Datasets for Road Damage Detection
---

# Datasets for Road Damage Detection

[← Back to AI Applications](setup.html)

## Overview

Training an accurate road damage detection model requires large, diverse, and well-annotated datasets. This page documents the dataset used in this project and provides information on public datasets for extending the system to detect additional damage types.

## Current Project Dataset

### Pothole Detection Dataset (Roboflow)

**Source**: [Roboflow Universe - Pothole Detection](https://universe.roboflow.com/jerry-cooper-tlzkx/pothole_detection-hfnqo/dataset/7)

**Dataset Statistics**:
- **Total Images**: 4,510
- **Train Set**: 3,993 images (88.5%)
- **Validation Set**: 352 images (7.8%)
- **Test Set**: 165 images (3.7%)

**Classes**: 1 class - `pothole` (bowl-shaped depressions and holes in road surface)

**Note**: The source Roboflow project contains 8 classes (pothole, curb, dash, distressed, grate, manhole, marking, utility), but this dataset version (v7) is filtered to only include pothole annotations for focused single-class detection.

#### Preprocessing Applied

The dataset has been preprocessed with the following operations:

| Operation | Description |
|-----------|-------------|
| **Auto-Orient** | Corrects image orientation based on EXIF data |
| **Resize** | Stretch to 840×840 pixels |
| **Auto-Adjust Contrast** | Histogram equalization for improved visibility |
| **Filter Null** | Requires ≥20% of images to contain annotations |

#### Augmentations Applied

To increase dataset diversity and model robustness:

| Augmentation | Details |
|--------------|---------|
| **Outputs per training example** | 3× (triples the training data) |
| **Grayscale** | Applied to 23% of images |
| **Blur** | Up to 2.5px blur radius |
| **Noise** | Up to 1.76% of pixels affected |

**Format**: YOLO format (text files with normalized bounding box coordinates)

**Access**: The dataset is managed through Roboflow API. Configure your `.env` file with appropriate credentials to automatically download during training (see [AI Applications Setup](setup.html)).

## Using the Project Dataset

### Quick Start with Roboflow

The training script (`ai-model/train/train.py`) automatically downloads the dataset from Roboflow. Configure your environment:

```bash
# 1. Copy environment template
cd ai-model
cp .env.example .env

# 2. Edit .env with your Roboflow credentials
ROBOFLOW_API_KEY=your_api_key_here
ROBOFLOW_WORKSPACE=jerry-cooper-tlzkx
ROBOFLOW_PROJECT=pothole_detection-hfnqo
ROBOFLOW_PROJECT_NAME=pothole_detection
ROBOFLOW_PROJECT_VERSION=7

# 3. Run training (dataset downloads automatically)
cd train
python train.py
```

### Dataset Structure

After download, the dataset follows YOLO format:

```
dataset/
├── train/
│   ├── images/
│   │   ├── image_0001.jpg
│   │   └── ...
│   └── labels/
│       ├── image_0001.txt  # YOLO annotations
│       └── ...
├── valid/
│   ├── images/
│   └── labels/
├── test/
│   ├── images/
│   └── labels/
└── data.yaml  # Dataset configuration
```

**YOLO Label Format** (`image_0001.txt`):
```
# class_id center_x center_y width height (all normalized 0-1)
0 0.512 0.634 0.124 0.089
```

Where `class_id` is `0` for pothole (single class detection).

## Extending to Additional Damage Types

To train the model on additional road damage types (cracks, rutting, etc.), you would need to collect and annotate a new dataset with those damage classes. The system architecture supports this through:

1. **Data Collection**: Capture images containing the desired damage types
2. **Annotation**: Use tools like Roboflow, LabelImg, or CVAT to annotate bounding boxes
3. **Training**: Run `train.py` with the new dataset configuration
4. **Export**: Convert the trained model to TFLite for edge deployment

The current Roboflow dataset management system makes it easy to extend the model's capabilities as new annotated data becomes available.

## Next Steps

1. [Setup AI Environment](setup.html) - Configure training environment
2. [Train Pothole Detection Model](setup.html#training-the-model) - Start training
3. [Validate Performance](setup.html#model-validation-trainvalidatepy) - Evaluate model

---

[← Back to AI Applications](setup.html)
