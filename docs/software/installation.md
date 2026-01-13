---
layout: default
title: Software Installation
---

# Software Installation Guide

[← Back to Home](../)

## Overview

This guide covers the installation and configuration of all software components for the AI drone system.

## Prerequisites

- Assembled drone hardware
- Raspberry Pi Zero 2 WH with SD card (16GB+ recommended)
- Computer with SD card reader
- Internet connection
- USB keyboard and mouse (for initial Pi setup)

## Operating System Setup

### 1. Install Raspbian OS

**Download Raspberry Pi Imager:**

```bash
# On macOS
brew install --cask raspberry-pi-imager

# On Linux
sudo apt install rpi-imager
```

**Flash SD Card:**

1. Insert SD card into computer
2. Launch Raspberry Pi Imager
3. Choose "Raspberry Pi OS Lite (64-bit)"
4. Select your SD card
5. Click "Write"

**Enable SSH (Optional):**

```bash
# After flashing, mount the boot partition
touch /Volumes/boot/ssh
```

**Configure WiFi (Optional):**
Create `wpa_supplicant.conf` in boot partition:

```
country=DE
ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
update_config=1

network={
    ssid="YOUR_WIFI_SSID"
    psk="YOUR_WIFI_PASSWORD"
    key_mgmt=WPA-PSK
}
```

### 2. First Boot Configuration

```bash
# SSH into Pi (if connected via network)
ssh pi@raspberrypi.local
# Default password: raspberry

# Update system
sudo apt update
sudo apt upgrade -y

# Configure system
sudo raspi-config
# - Change password
# - Set hostname to "ai-drone"
# - Enable Camera interface
# - Expand filesystem
# - Reboot
```

## Python Environment Setup

### Install Python Dependencies

```bash
# Install Python 3 and pip
sudo apt install python3 python3-pip python3-venv -y

# Install system dependencies
sudo apt install -y \
    git \
    cmake \
    libatlas-base-dev \
    libopencv-dev \
    python3-opencv \
    libhdf5-dev \
    libhdf5-serial-dev \
    libjpeg-dev \
    libpng-dev \
    libtiff-dev \
    libavcodec-dev \
    libavformat-dev \
    libswscale-dev \
    libv4l-dev \
    libxvidcore-dev \
    libx264-dev

# Create virtual environment
python3 -m venv ~/drone-env
source ~/drone-env/bin/activate

# Upgrade pip
pip install --upgrade pip
```

### Install AI Framework

```bash
# Install TensorFlow Lite
pip install tflite-runtime

# Install supporting libraries
pip install numpy opencv-python pillow

# For Google Coral
echo "deb https://packages.cloud.google.com/apt coral-edgetpu-stable main" | \
sudo tee /etc/apt/sources.list.d/coral-edgetpu.list
curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | sudo apt-key add -
sudo apt update
sudo apt install libedgetpu1-std python3-pycoral
```

## Flight Controller Software

### INAV Configuration

**Install INAV Configurator on Computer:**

1. Download from [github.com/iNavFlight/inav-configurator](https://github.com/iNavFlight/inav-configurator/releases)
2. Connect flight controller via USB
3. Flash latest INAV firmware

**Basic Configuration:**

```
1. Setup Tab:
   - Select quadcopter/fixed-wing configuration
   - Set correct board alignment

2. Ports Tab:
   - Enable MSP on UART for Raspberry Pi connection
   - Enable Serial RX on appropriate UART
   - Enable GPS if using

3. Configuration Tab:
   - Set ESC/Motor protocol
   - Configure receiver (ELRS, CRSF, etc.)
   - Enable features: GPS, OSD, TELEMETRY

4. PID Tuning:
   - Load default PID profile
   - Adjust based on drone weight and flight characteristics

5. Receiver Tab:
   - Configure channel mapping
   - Set failsafe values
   - Map AUX8 for camera recording trigger

6. Modes Tab:
   - Configure ARM switch
   - Set flight modes (Angle, Horizon, Acro)
   - Optional: Configure autonomous modes (RTH, WP, etc.)

7. Motors Tab:
   - Test motor direction (props OFF!)
   - Verify motor order: 1-Front Left, 2-Front Right,
                         3-Back Right, 4-Back Left
```

**Note**: INAV is used for this project due to its superior autonomous flight and GPS navigation capabilities, which are essential for systematic road inspection missions.

### ArduPilot Installation (Alternative)

```bash
# For autonomous flight capabilities
# Install on companion computer (Raspberry Pi)
cd ~
git clone https://github.com/ArduPilot/ardupilot.git
cd ardupilot
git submodule update --init --recursive

# Install MAVProxy (Ground Station Software)
sudo apt install python3-dev python3-opencv python3-wxgtk4.0 \
                 python3-pip python3-matplotlib python3-lxml python3-pygame
pip3 install MAVProxy
```

## Camera Configuration

### Test Camera Module

```bash
# Enable camera
sudo raspi-config
# Interface Options -> Camera -> Enable

# Test camera
raspistill -o test.jpg
raspivid -o test.h264 -t 10000

# Install picamera library
pip install picamera
```

### Video Streaming Setup

```python
# Install streaming software
sudo apt install -y gstreamer1.0-tools \
                    gstreamer1.0-plugins-good \
                    gstreamer1.0-plugins-bad

# Test video stream
raspivid -t 0 -w 1280 -h 720 -fps 30 -o - | \
gst-launch-1.0 -v fdsrc ! h264parse ! rtph264pay \
config-interval=1 pt=96 ! udpsink host=192.168.1.100 port=5000
```

## AI Application Setup

### Install YOLO for Object Detection

```bash
# Clone YOLO repository
cd ~/
git clone https://github.com/ultralytics/yolov5
cd yolov5
pip install -r requirements.txt

# Download pre-trained model
wget https://github.com/ultralytics/yolov5/releases/download/v6.0/yolov5s.pt

# Test detection
python detect.py --source 0  # Use webcam
```

### Convert Model for Edge TPU

```bash
# Install Edge TPU Compiler
curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | sudo apt-key add -
echo "deb https://packages.cloud.google.com/apt coral-edgetpu-stable main" | \
sudo tee /etc/apt/sources.list.d/coral-edgetpu.list
sudo apt update
sudo apt install edgetpu-compiler

# Convert TensorFlow model to TFLite
# (Conversion steps depend on your specific model)
edgetpu_compiler model.tflite
```

## Ground Control Station

### Install QGroundControl (on Computer)

**macOS:**

```bash
brew install --cask qgroundcontrol
```

**Linux:**

```bash
sudo usermod -a -G dialout $USER
sudo apt-get remove modemmanager -y
wget https://d176tv9ibo4jno.cloudfront.net/latest/QGroundControl.AppImage
chmod +x QGroundControl.AppImage
./QGroundControl.AppImage
```

**Windows:**
Download from [qgroundcontrol.com](http://qgroundcontrol.com)

## Testing Installation

### System Test Script

```python
# test_system.py
import sys
import cv2
import numpy as np

def test_camera():
    """Test camera functionality"""
    try:
        cap = cv2.VideoCapture(0)
        ret, frame = cap.read()
        cap.release()
        if ret:
            print("✓ Camera: OK")
            return True
        else:
            print("✗ Camera: FAILED")
            return False
    except Exception as e:
        print(f"✗ Camera: ERROR - {e}")
        return False

def test_coral():
    """Test Google Coral accelerator"""
    try:
        from pycoral.utils import edgetpu
        interpreters = edgetpu.list_edge_tpus()
        if interpreters:
            print(f"✓ Coral: OK - {len(interpreters)} device(s) found")
            return True
        else:
            print("✗ Coral: No devices found")
            return False
    except Exception as e:
        print(f"✗ Coral: ERROR - {e}")
        return False

def test_opencv():
    """Test OpenCV installation"""
    try:
        print(f"✓ OpenCV: OK - Version {cv2.__version__}")
        return True
    except Exception as e:
        print(f"✗ OpenCV: ERROR - {e}")
        return False

def main():
    print("=== AI Drone System Test ===\n")
    results = []

    results.append(test_opencv())
    results.append(test_camera())
    results.append(test_coral())

    print("\n" + "="*30)
    if all(results):
        print("All tests passed! ✓")
        sys.exit(0)
    else:
        print("Some tests failed! ✗")
        sys.exit(1)

if __name__ == "__main__":
    main()
```

Run the test:

```bash
python3 test_system.py
```

## Next Steps

1. **[Camera Control System](camera-control.html)** - Learn about the integrated recording & AI system
2. [Configure Flight Controller](../autopilot/configuration.html)
3. [Set up AI Applications](../ai-applications/setup.html)
4. [Begin Training AI Models](../ai-applications/training.html)

## Troubleshooting

### Common Issues

**Camera not detected:**

```bash
# Check camera connection
vcgencmd get_camera
# Should show: supported=1 detected=1

# Enable camera interface
sudo raspi-config
```

**Coral not detected:**

```bash
# Check USB connection
lsusb | grep "Google"

# Reinstall driver
sudo apt install --reinstall libedgetpu1-std
```

**Permission errors:**

```bash
# Add user to video group
sudo usermod -a -G video $USER

# Add user to dialout group (for serial)
sudo usermod -a -G dialout $USER

# Reboot
sudo reboot
```

---

[← Back to Home](../) | [Next: Camera Control →](camera-control.html) | [AI Applications →](../ai-applications/setup.html)
