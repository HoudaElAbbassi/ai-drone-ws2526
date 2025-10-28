---
layout: default
title: Datasets for Road Damage Detection
---

# Datasets for Road Damage Detection

[← Back to AI Applications](setup.html)

## Overview

Training an accurate road damage detection model requires large, diverse, and well-annotated datasets. This page provides information on available public datasets and guidelines for creating custom datasets.

## Public Datasets

### 1. RDD2020 (Road Damage Dataset 2020)

**Description**: Large-scale dataset containing 26,620 road damage images from India, Japan, and Czech Republic.

**Damage Classes**:
- D00: Longitudinal cracks
- D10: Transverse cracks
- D20: Alligator cracks
- D40: Potholes

**Format**: COCO annotation format
**Resolution**: Variable (typically 600x600 to 4000x3000)
**Source**: [IEEE DataPort](https://ieee-dataport.org/)

**Usage**:
```python
# Download and extract RDD2020
# Available at: https://github.com/sekilab/RoadDamageDetector

# Annotations in COCO JSON format
{
  "images": [...],
  "annotations": [
    {
      "id": 1,
      "image_id": 1,
      "category_id": 1,
      "bbox": [x, y, width, height],
      "area": 1234.5,
      "iscrowd": 0
    }
  ],
  "categories": [...]
}
```

### 2. CrackForest Dataset

**Description**: 118 images with pixel-level crack annotations.

**Damage Classes**:
- Surface cracks (binary classification)

**Format**: Image + pixel masks
**Resolution**: 480x320
**Source**: [GitHub](https://github.com/cuilimeng/CrackForest-dataset)

**Best for**: Semantic segmentation of cracks, suitable for detailed crack width estimation.

### 3. GAPs Dataset (German Asphalt Pavement)

**Description**: 1,969 labeled images of German road surfaces.

**Damage Classes**:
- Crack (single class)

**Format**: Pascal VOC XML
**Resolution**: Various
**Source**: Research publication

### 4. SDNET2018 (Surface Defect Network)

**Description**: 56,000 images of concrete surfaces with cracks.

**Damage Classes**:
- Cracked
- Non-cracked

**Format**: Image classification dataset
**Resolution**: 256x256
**Source**: Utah State University

**Note**: Originally for concrete structures, but useful for transfer learning.

### 5. Crack500 Dataset

**Description**: 500 images of pavement cracks with pixel-level annotations.

**Damage Classes**:
- Cracks (pixel-level segmentation)

**Format**: Images + segmentation masks
**Resolution**: 2000x1500
**Source**: [GitHub](https://github.com/fyangneil/pavement-crack-detection)

### 6. CFD (Concrete Fracture Dataset)

**Description**: 118 concrete images with detailed crack annotations.

**Damage Classes**:
- Cracks

**Format**: Images + binary masks
**Resolution**: 480x320

## Dataset Comparison

| Dataset | Images | Classes | Annotation Type | Best For |
|---------|--------|---------|-----------------|----------|
| RDD2020 | 26,620 | 4 | Bounding boxes | Multi-class detection |
| CrackForest | 118 | 1 | Pixel masks | Crack segmentation |
| GAPs | 1,969 | 1 | Bounding boxes | German road conditions |
| SDNET2018 | 56,000 | 2 | Image labels | Transfer learning |
| Crack500 | 500 | 1 | Pixel masks | Detailed segmentation |
| CFD | 118 | 1 | Binary masks | Crack patterns |

## Creating Custom Dataset

For optimal performance specific to your region and conditions, collect custom data.

### Data Collection Guidelines

**Flight Parameters**:
- Altitude: 5-10 meters
- Speed: 2-5 m/s
- Overlap: 70-80% between images
- Resolution: Minimum 4K (3840x2160)
- Frame rate: 5-10 FPS

**Coverage Requirements**:
- Multiple road types: highways, urban, rural
- Various weather: sunny, cloudy, wet, dry
- Different times: morning, noon, afternoon (varying shadows)
- All damage severity levels: low, medium, high
- Various road materials: asphalt, concrete

**Target Dataset Size**:
- Minimum: 1,000 images per damage class
- Recommended: 5,000+ images per class
- Optimal: 10,000+ images per class

### Annotation Tools

#### 1. LabelImg
**Best for**: Bounding box annotations (YOLO/COCO format)

```bash
# Install
pip install labelImg

# Run
labelImg
```

**Workflow**:
1. Open directory with images
2. Draw bounding boxes around damage
3. Assign class labels
4. Save in YOLO or PascalVOC format

#### 2. CVAT (Computer Vision Annotation Tool)
**Best for**: Team collaboration, bounding boxes, polygons, segmentation

- Web-based interface
- Multi-user support
- Supports COCO, YOLO, VOC formats
- Can be self-hosted or use cloud version

**URL**: https://cvat.org

#### 3. Roboflow
**Best for**: Data augmentation, format conversion, team collaboration

- Web-based platform
- Automatic augmentation
- Export to multiple formats
- Preprocessing pipeline

**URL**: https://roboflow.com

### Annotation Guidelines

**Quality Standards**:
- Draw tight bounding boxes around damage
- Include entire damage area (don't crop)
- Consistent labeling across annotators
- Mark occluded damage (partially visible)
- Annotate all visible damage in image

**Bounding Box Rules**:
```
✓ Good: Box tightly fits damage area
✗ Bad: Box too large, includes too much background
✗ Bad: Box too small, cuts off damage
✗ Bad: Missing damage instances
```

**Class Assignment**:
- **Longitudinal**: Crack length > 2x width, parallel to traffic
- **Transverse**: Crack length > 2x width, perpendicular to traffic
- **Alligator**: Interconnected cracks forming pattern
- **Pothole**: Hole or depression in surface
- **Rutting**: Linear depression in wheel path
- **Bleeding**: Shiny asphalt surface
- **Weathering**: Aggregate loss, rough surface

### Data Augmentation

Increase dataset diversity and model robustness:

```python
import albumentations as A

# Define augmentation pipeline
transform = A.Compose([
    # Geometric transformations
    A.HorizontalFlip(p=0.5),
    A.VerticalFlip(p=0.5),
    A.Rotate(limit=15, p=0.5),
    A.ShiftScaleRotate(shift_limit=0.1, scale_limit=0.1, rotate_limit=15, p=0.5),

    # Color transformations
    A.RandomBrightnessContrast(brightness_limit=0.2, contrast_limit=0.2, p=0.5),
    A.HueSaturationValue(hue_shift_limit=10, sat_shift_limit=20, val_shift_limit=20, p=0.5),

    # Weather effects
    A.RandomRain(p=0.2),
    A.RandomShadow(p=0.2),
    A.RandomSunFlare(p=0.1),

    # Noise and blur
    A.GaussNoise(p=0.2),
    A.GaussianBlur(blur_limit=(3, 5), p=0.2),
    A.MotionBlur(blur_limit=5, p=0.2),
], bbox_params=A.BboxParams(format='yolo', label_fields=['class_labels']))

# Apply augmentation
augmented = transform(image=image, bboxes=bboxes, class_labels=labels)
```

### Dataset Split

Standard split for training, validation, and testing:

```
Training:   70% (for model learning)
Validation: 20% (for hyperparameter tuning)
Testing:    10% (for final evaluation)
```

**Important**:
- Ensure no overlap between splits
- Stratify by damage class (equal representation)
- Test set should represent real-world conditions

### Dataset Organization

```
road_damage_dataset/
├── train/
│   ├── images/
│   │   ├── img_0001.jpg
│   │   ├── img_0002.jpg
│   │   └── ...
│   └── labels/
│       ├── img_0001.txt  # YOLO format
│       ├── img_0002.txt
│       └── ...
├── val/
│   ├── images/
│   └── labels/
├── test/
│   ├── images/
│   └── labels/
└── dataset.yaml  # Configuration file
```

**dataset.yaml**:
```yaml
train: ./train/images
val: ./val/images
test: ./test/images

nc: 7  # number of classes

names:
  0: longitudinal_crack
  1: transverse_crack
  2: alligator_crack
  3: pothole
  4: rutting
  5: bleeding
  6: weathering
```

## Data Quality Checks

Before training, verify dataset quality:

```python
# Check dataset statistics
import os
import json

def analyze_dataset(annotations_file):
    with open(annotations_file, 'r') as f:
        data = json.load(f)

    # Count images per class
    class_counts = {}
    for ann in data['annotations']:
        cat_id = ann['category_id']
        class_counts[cat_id] = class_counts.get(cat_id, 0) + 1

    print("Class distribution:")
    for cat_id, count in class_counts.items():
        print(f"  Class {cat_id}: {count} instances")

    # Check image sizes
    sizes = [(img['width'], img['height']) for img in data['images']]
    print(f"\nImage sizes: {len(set(sizes))} unique sizes")

    # Check annotation bounding box sizes
    bbox_areas = [ann['area'] for ann in data['annotations']]
    print(f"\nBbox areas: min={min(bbox_areas):.2f}, max={max(bbox_areas):.2f}, mean={sum(bbox_areas)/len(bbox_areas):.2f}")

analyze_dataset('annotations/train.json')
```

## Transfer Learning Sources

Pre-trained models that can be fine-tuned:

1. **COCO-pretrained YOLOv5**: General object detection
2. **ImageNet-pretrained backbones**: Feature extraction
3. **RDD2020-trained models**: Road damage specific
4. **SDNET2018 models**: Crack detection

## Next Steps

1. [Download and prepare datasets](setup.html)
2. [Train your first model](training.html)
3. [Evaluate model performance](evaluation.html)

---

[← Back to AI Applications](setup.html) | [Next: Model Training →](training.html)
