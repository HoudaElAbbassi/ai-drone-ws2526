# Quick Start Guide

Get your Road Damage Detection System running in minutes!

## Prerequisites

- Raspberry Pi Zero 2 WH with Raspberry Pi OS (Bullseye)
- Google Coral USB Accelerator
- Raspberry Pi Camera Module v2
- GPS module (Matek M10Q-5883)
- Internet connection

## Hardware Setup

### 1. Connect Camera

```
Raspberry Pi ─── CSI Cable ───> Camera Module v2
```

- Connect camera module to CSI port on Raspberry Pi
- Ensure ribbon cable is properly inserted (blue side facing USB ports)

### 2. Connect Google Coral

```
Raspberry Pi USB ─── USB Cable ───> Google Coral TPU
```

- Connect Coral USB Accelerator to USB port
- Use a USB hub if needed (RPi Zero 2 has only one port)

### 3. Connect GPS

```
Raspberry Pi GPIO ─── UART ───> GPS Module
```

- GPS TX (Pin 1) → RPi RX (GPIO 15, Pin 10)
- GPS RX (Pin 2) → RPi TX (GPIO 14, Pin 8)
- GPS GND → RPi GND (Pin 6)
- GPS VCC → RPi 5V (Pin 2)

**Note**: GPS is already connected on Drohne 3 via the flight controller

## Software Installation

### Step 1: Clone Repository

```bash
cd ~
git clone https://github.com/HoudaElAbbassi/ai-drone-ws2526.git
cd ai-drone-ws2526
```

### Step 2: Run Setup Script

```bash
chmod +x setup.sh
./setup.sh
```

This will:
- Install system dependencies
- Enable camera and UART
- Install Google Coral runtime
- Create Python virtual environment
- Install all required packages

**Estimated time**: 15-30 minutes

### Step 3: Reboot

```bash
sudo reboot
```

## Get a Trained Model

### Option 1: Download Pre-trained Model

Download a road damage detection model trained on RDD2020 dataset:

```bash
cd ~/ai-drone-ws2526/models

# Download model (example - replace with actual model URL)
wget https://example.com/road_damage_model.tflite -O road_damage.tflite

# Convert for Coral TPU
edgetpu_compiler road_damage.tflite

# This creates: road_damage_edgetpu.tflite

# Create labels file
cat > labels.txt << EOF
longitudinal_crack
transverse_crack
alligator_crack
pothole
rutting
bleeding
weathering
EOF
```

### Option 2: Train Your Own Model

See [docs/ai-applications/training.md](docs/ai-applications/training.md) for training instructions.

## Testing the System

### 1. Test with Mock Hardware

Test the system without actual hardware:

```bash
cd ~/ai-drone-ws2526
source venv/bin/activate

# Run with mock camera and GPS
python -m src.road_detector --mock --duration 30

# This will run for 30 seconds with simulated data
```

You should see:
```
==========================================
  Road Damage Detection System
==========================================

[1/3] Initializing Camera...
Using mock camera (no hardware)
Camera started: 1280x720 @ 10fps

[2/3] Loading AI Model...
✓ Coral TPU initialized successfully
Model loaded successfully

[3/3] Starting GPS Tracker...
Using mock GPS (no hardware)

==========================================
  System Ready!
==========================================
```

### 2. Test with Real Hardware

```bash
# Run with actual hardware
python -m src.road_detector --duration 60

# Press Ctrl+C to stop anytime
```

### 3. Check Detection Results

```bash
# View detection database
sqlite3 data/detections.db "SELECT * FROM detections;"

# View detection images
ls -lh data/detections/

# Export report
python -m src.road_detector --export
```

## Running on Startup

To run the system automatically on boot:

### 1. Create systemd service

```bash
sudo nano /etc/systemd/system/road-detector.service
```

Add:
```ini
[Unit]
Description=Road Damage Detection System
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/ai-drone-ws2526
ExecStart=/home/pi/ai-drone-ws2526/venv/bin/python -m src.road_detector
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

### 2. Enable service

```bash
sudo systemctl daemon-reload
sudo systemctl enable road-detector.service
sudo systemctl start road-detector.service

# Check status
sudo systemctl status road-detector.service

# View logs
sudo journalctl -u road-detector.service -f
```

## Usage Examples

### Basic Detection

```bash
# Run for 5 minutes
python -m src.road_detector --duration 300
```

### Export Report After Run

```bash
# Run and auto-export report
python -m src.road_detector --duration 180 --export
```

### Monitor Live Detections

```bash
# In one terminal
python -m src.road_detector

# In another terminal, watch detections
watch -n 1 'sqlite3 data/detections.db "SELECT COUNT(*) as total, class_name FROM detections GROUP BY class_name;"'
```

## Web Dashboard (Optional)

For a visual interface, run the web dashboard:

```bash
# Start dashboard
python -m src.dashboard.app

# Access from browser:
# http://raspberrypi.local:8080
```

Features:
- Live camera view with detections
- GPS map with damage markers
- Real-time statistics
- Detection history

## Troubleshooting

### Camera not working

```bash
# Test camera
libcamera-hello

# If not working:
sudo raspi-config
# → Interface Options → Camera → Enable
```

### Coral TPU not detected

```bash
# Check if Coral is connected
lsusb | grep Google

# Should show: "Google Inc. Coral USB Accelerator"

# Reinstall runtime
sudo apt install --reinstall libedgetpu1-std python3-pycoral
```

### GPS not working

```bash
# Check GPS serial port
cat /dev/ttyAMA0

# Should show NMEA sentences like:
# $GNGGA,123519,4807.038,N,01131.000,E,1,08,0.9,545.4,M,46.9,M,,*47
```

### Low FPS / Slow Detection

```bash
# Check if using Coral TPU
python3 << EOF
from pycoral.utils import edgetpu
print(f"Coral devices: {len(edgetpu.list_edge_tpus())}")
EOF

# Should print: "Coral devices: 1"
```

## Performance Expectations

### With Google Coral TPU:
- **Inference speed**: 10-30 FPS
- **Average latency**: 30-100ms per frame
- **CPU usage**: 30-50%

### Without Coral (CPU only):
- **Inference speed**: 1-3 FPS
- **Average latency**: 300-1000ms per frame
- **CPU usage**: 90-100%

## Next Steps

1. **Collect training data**: Fly drone and capture road images
2. **Train custom model**: Fine-tune on your specific roads
3. **Optimize parameters**: Adjust confidence thresholds
4. **Plan missions**: Create automated flight paths
5. **Generate reports**: Analyze detection patterns

## Support

For issues and questions:
- GitHub Issues: https://github.com/HoudaElAbbassi/ai-drone-ws2526/issues
- Documentation: https://houdaelabbassi.github.io/ai-drone-ws2526/

## Safety Reminders

⚠️ **Important**:
- Always test on ground before flying
- Ensure GPS has good fix before takeoff
- Monitor battery levels
- Follow local drone regulations
- Keep visual line of sight
- Have a safety spotter

Happy detecting! 🚁
