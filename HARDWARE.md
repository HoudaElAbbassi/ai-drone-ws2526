# Drohne 3 - Hardware Specifications

## Drone Components

### Frame & Flight Controller
- **Frame**: SpeedyBee BEE35 Pro 3.5" CineWhoop Frame Kit
- **Flight Controller**: Flywoo GOKU F722 PRO V2
  - MCU: STM32F722 (216MHz, 512kB Flash)
  - ESC: 55A Stack 3-6S AM32
  - Firmware: Betaflight v4.5.2

### Camera & Video System
- **FPV Camera**: Caddx Ratel Pro 1500TVL Analog
- **Video Transmitter**: SpeedyBee TX800 VTX
  - Channel: 5847 MHz (Band: BOSCAM/RichWave, Channel: 7)
  - Antenna: Foxeer Lollipop 4 RHCP

### Radio & Receiver
- **Receiver**: Radiomaster XR1 ELRS Dual Band RX
  - Firmware: ExpressLRS 3.6.0
  - Binding Phase: `drone3`
- **Remote Control**: Radiomaster Boxer ELRS Transmitter
  - Firmware: EdgeTX v2.11.3

### Motors & Propulsion
- **Motors**: Axisflying C206 2006 2500KV 4-6S
- **Propellers**: Gemfan 90mm D90-5 3.5" Ducted 5-Blade

### Navigation
- **GPS**: Matek M10Q-5883 GPS with Compass

## AI & Computing Hardware

### Onboard Computer
- **Single Board Computer**: Raspberry Pi Zero 2 WH
  - CPU: Quad-core 64-bit ARM Cortex-A53 @ 1GHz
  - RAM: 512MB
  - WiFi: 2.4GHz 802.11 b/g/n
  - Bluetooth: 4.2 / BLE
  - GPIO: 40-pin header

### AI Accelerator
- **Edge TPU**: Google Coral USB Accelerator
  - Performance: 4 TOPS (trillion operations per second)
  - Interface: USB 3.0
  - Supported frameworks: TensorFlow Lite

### Camera for AI Processing
- **Raspberry Pi Camera Module v2**
  - Sensor: Sony IMX219
  - Resolution: 8 megapixels (3280 x 2464)
  - Video: 1080p30, 720p60, 640x480p90
  - Field of View: 62.2° horizontal, 48.8° vertical
  - Interface: CSI (Camera Serial Interface)

### Video Capture
- **USB Video Grabber**: MacroSilicon MS210x
  - Purpose: Capture FPV camera feed for processing
  - Input: Analog video (CVBS)
  - Output: USB video stream

## Power System

### Battery
- **LiPo Battery**: 3-6S (11.1V - 22.2V)
- **Typical**: 4S 850mAh - 1300mAh
- **Connector**: XT30 or XT60

### Power Distribution
- Integrated in FC stack (55A ESC)
- 5V BEC for Raspberry Pi (via USB)
- Regulated voltage for peripherals

## Additional Equipment

### FPV Goggles
- **Model**: Skyzone Cobra X
- **Features**: 5.8GHz 48CH, DVR recording

### Charger
- **Model**: SkyRC B6neo+
- **Capabilities**: LiPo, LiHV, NiMH charging

### Storage & Connectivity
- **SD Card**: Pre-installed with Raspberry Pi OS Lite (32-bit)
  - OS: Debian 11.11 (Bullseye)
  - Pre-configured for Google Coral compatibility
- **Mini-HDMI to HDMI Cable**: For display connection
- **Micro-USB to USB-A Cable**: For Coral and peripherals

## Connections & Wiring

```
┌─────────────────────────────────────────────────────┐
│                   Drohne 3                          │
│                                                     │
│  ┌──────────────┐         ┌──────────────┐        │
│  │ FPV Camera   │────────▶│  VTX TX800   │        │
│  │ Ratel Pro    │         │  5847 MHz    │        │
│  └──────────────┘         └──────────────┘        │
│         │                                           │
│         │ Analog Video                             │
│         ▼                                           │
│  ┌──────────────┐                                  │
│  │ Video Grabber│────USB───┐                       │
│  │  MS210x      │          │                       │
│  └──────────────┘          │                       │
│                             │                       │
│  ┌──────────────┐          │                       │
│  │ RPi Camera   │──CSI─────┤                       │
│  │  Module v2   │          │                       │
│  └──────────────┘          │                       │
│                             │                       │
│                             ▼                       │
│                    ┌────────────────┐              │
│                    │  Raspberry Pi  │              │
│                    │   Zero 2 WH    │              │
│                    └────────┬───────┘              │
│                             │                       │
│                             │ USB                   │
│                             ▼                       │
│                    ┌────────────────┐              │
│                    │  Google Coral  │              │
│                    │  USB Accel.    │              │
│                    └────────────────┘              │
│                                                     │
│  ┌──────────────┐         ┌──────────────┐        │
│  │ Flight Ctrl  │◀──UART─▶│  GPS Matek   │        │
│  │ GOKU F722    │         │  M10Q-5883   │        │
│  └──────┬───────┘         └──────────────┘        │
│         │                                           │
│         │ (Optional: UART to RPi for telemetry)    │
│                                                     │
│  ┌──────────────┐                                  │
│  │ ELRS RX      │◀──────2.4GHz──────┐             │
│  │  XR1         │                    │             │
│  └──────────────┘                    │             │
└─────────────────────────────────────┼─────────────┘
                                       │
                               ┌───────▼────────┐
                               │ Radiomaster    │
                               │ Boxer TX       │
                               └────────────────┘
```

## Weight & Dimensions

- **AUW** (All-Up Weight): ~250-300g (without LiPo)
- **Frame Size**: 3.5" (89mm prop-to-prop diagonal)
- **Prop Guards**: Integrated in CineWhoop frame

## Operating Parameters

### Flight Performance
- **Max Speed**: ~40-60 km/h (depending on battery)
- **Flight Time**: 5-8 minutes (with AI processing)
- **Hover Time**: 8-12 minutes (without AI)
- **Max Range**: ~500m (ELRS)

### AI Processing
- **Inference Speed**: ~10-30 FPS (with Coral TPU)
- **Camera Resolution**: 1080p or 720p for processing
- **Power Consumption**: +2-3W for RPi + Coral

## Communication Interfaces

### Available on Raspberry Pi
- **CSI**: Camera Module v2
- **USB**: Coral TPU, Video Grabber
- **GPIO**: UART for GPS/Telemetry
- **WiFi**: Remote access and data transfer
- **Bluetooth**: Optional peripherals

### Flight Controller Ports
- **UART**: Telemetry, GPS, RPi communication
- **I2C**: Compass, other sensors
- **SPI**: OSD, Receiver

## Software Compatibility

### Supported on Raspberry Pi Zero 2 WH
- ✅ Raspberry Pi OS (32-bit Bullseye) - Pre-installed
- ✅ TensorFlow Lite 2.x
- ✅ Python 3.9
- ✅ OpenCV 4.x
- ✅ PyCoral library
- ✅ MAVLink/pymavlink
- ✅ picamera2

### Flight Controller Software
- **Betaflight 4.5.2**: Default firmware
- **INAV**: Alternative for waypoint missions
- **ArduPilot**: For advanced autonomy (requires reflash)

## Limitations & Considerations

### Raspberry Pi Zero 2 WH
- ⚠️ Limited RAM (512MB) - optimize memory usage
- ⚠️ No Ethernet - WiFi only
- ⚠️ Single USB port - requires USB hub for multiple devices
- ⚠️ Lower processing power - Coral TPU essential for real-time

### Power Management
- ⚠️ RPi + Coral add ~2-3W consumption
- ⚠️ Reduces flight time by 30-40%
- ⚠️ Requires stable 5V power supply (BEC)

### Weight Constraints
- ⚠️ Total payload < 100g (RPi + Coral + camera + mounting)
- ⚠️ Center of gravity must remain balanced
- ⚠️ May require motor/prop tuning

## Mounting Considerations

### Raspberry Pi Mounting
- Use vibration dampeners
- Ensure good ventilation
- Protect from propwash
- Cable management critical

### GPS Placement
- Away from motors and ESC
- Clear view of sky
- Minimize magnetic interference
- Already mounted on Drohne 3

## Next Steps

1. [Setup Raspberry Pi](docs/software/installation.html)
2. [Install AI Framework](docs/ai-applications/setup.html)
3. [Connect Hardware Components](docs/hardware/setup.html)
4. [Test Camera and GPS](docs/tutorials/getting-started.html)
