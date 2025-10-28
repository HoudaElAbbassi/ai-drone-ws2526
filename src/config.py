#!/usr/bin/env python3
"""
Configuration file for Road Damage Detection System
"""

import os
from pathlib import Path

# Base paths
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
MODELS_DIR = BASE_DIR / "models"
LOGS_DIR = BASE_DIR / "logs"

# Create directories if they don't exist
DATA_DIR.mkdir(exist_ok=True)
MODELS_DIR.mkdir(exist_ok=True)
LOGS_DIR.mkdir(exist_ok=True)
(DATA_DIR / "images").mkdir(exist_ok=True)
(DATA_DIR / "detections").mkdir(exist_ok=True)

# Camera Configuration
CAMERA_CONFIG = {
    "resolution": (1280, 720),  # 720p for balance of quality and speed
    "framerate": 10,  # FPS for capture
    "format": "rgb",  # RGB format for processing
    "rotation": 0,  # Adjust if camera is mounted rotated
}

# AI Model Configuration
MODEL_CONFIG = {
    "model_path": MODELS_DIR / "road_damage_edgetpu.tflite",
    "labels_path": MODELS_DIR / "labels.txt",
    "confidence_threshold": 0.5,  # Minimum confidence for detection
    "iou_threshold": 0.45,  # Non-maximum suppression threshold
    "input_size": (320, 320),  # Model input size (adjust based on your model)
}

# Damage class labels
DAMAGE_CLASSES = {
    0: "longitudinal_crack",
    1: "transverse_crack",
    2: "alligator_crack",
    3: "pothole",
    4: "rutting",
    5: "bleeding",
    6: "weathering",
}

# Severity thresholds (based on bounding box area percentage)
SEVERITY_THRESHOLDS = {
    "low": 0.05,  # < 5% of image
    "medium": 0.15,  # 5-15% of image
    "high": 0.15,  # > 15% of image
}

# GPS Configuration
GPS_CONFIG = {
    "port": "/dev/ttyAMA0",  # UART port for GPS
    "baudrate": 9600,
    "timeout": 1,
}

# Flight Controller Configuration (optional)
FC_CONFIG = {
    "enabled": False,  # Set to True if connecting to FC
    "port": "/dev/ttyUSB0",
    "baudrate": 57600,
}

# Logging Configuration
LOG_CONFIG = {
    "level": "INFO",  # DEBUG, INFO, WARNING, ERROR
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "file": LOGS_DIR / "road_detection.log",
}

# Detection Storage
DETECTION_CONFIG = {
    "save_images": True,  # Save images with detections
    "save_crops": True,  # Save cropped damage regions
    "image_dir": DATA_DIR / "images",
    "detection_dir": DATA_DIR / "detections",
    "database": DATA_DIR / "detections.db",  # SQLite database
}

# Web Dashboard Configuration
WEB_CONFIG = {
    "enabled": True,
    "host": "0.0.0.0",  # Listen on all interfaces
    "port": 8080,
    "debug": False,
}

# Processing Configuration
PROCESSING_CONFIG = {
    "batch_size": 1,  # Process images one at a time
    "max_queue_size": 30,  # Maximum frames in processing queue
    "save_interval": 10,  # Save detection data every N detections
}

# Mission Configuration
MISSION_CONFIG = {
    "altitude": 10,  # meters above ground
    "speed": 3,  # m/s
    "overlap": 0.7,  # 70% image overlap
}

# System Configuration
SYSTEM_CONFIG = {
    "use_coral": True,  # Use Google Coral TPU if available
    "enable_display": False,  # Enable GUI display (set False for headless)
    "auto_start": False,  # Auto-start detection on boot
}
