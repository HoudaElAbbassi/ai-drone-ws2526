#!/bin/bash
# Setup script for Road Damage Detection System on Raspberry Pi Zero 2 WH

set -e  # Exit on error

echo "=========================================="
echo "  Road Damage Detection System Setup"
echo "=========================================="
echo ""

# Check if running on Raspberry Pi
if [ ! -f /proc/device-tree/model ]; then
    echo "WARNING: This script is designed for Raspberry Pi"
    read -p "Continue anyway? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Update system
echo "[1/8] Updating system..."
sudo apt update
sudo apt upgrade -y

# Install system dependencies
echo "[2/8] Installing system dependencies..."
sudo apt install -y \
    python3-pip \
    python3-venv \
    python3-picamera2 \
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

# Enable camera interface
echo "[3/8] Enabling camera interface..."
sudo raspi-config nonint do_camera 0

# Enable UART for GPS
echo "[4/8] Configuring UART for GPS..."
sudo raspi-config nonint do_serial 2  # Disable login shell, enable hardware

# Install Google Coral Edge TPU
echo "[5/8] Installing Google Coral Edge TPU runtime..."
echo "deb https://packages.cloud.google.com/apt coral-edgetpu-stable main" | sudo tee /etc/apt/sources.list.d/coral-edgetpu.list
curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | sudo apt-key add -
sudo apt update
sudo apt install -y libedgetpu1-std python3-pycoral

# Create virtual environment
echo "[6/8] Creating Python virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
echo "[7/8] Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Create necessary directories
echo "[8/8] Creating project directories..."
mkdir -p data/images
mkdir -p data/detections
mkdir -p models
mkdir -p logs

echo ""
echo "=========================================="
echo "  Setup Complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "  1. Download a trained model to the 'models/' directory"
echo "  2. Connect hardware (camera, GPS, Coral TPU)"
echo "  3. Run: source venv/bin/activate"
echo "  4. Test: python -m src.road_detector --mock"
echo "  5. Run live: python -m src.road_detector"
echo ""
echo "See README.md for more information."
echo ""
