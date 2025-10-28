# Source Code

This directory contains the source code for the AI drone project.

## Structure

```
src/
├── detection/          # AI detection modules
│   ├── defect_detector.py
│   ├── model_loader.py
│   └── preprocessing.py
├── flight/            # Flight control modules
│   ├── autopilot.py
│   ├── waypoint_navigation.py
│   └── mission_planner.py
├── camera/            # Camera and video processing
│   ├── capture.py
│   ├── stream.py
│   └── recorder.py
├── utils/             # Utility functions
│   ├── config.py
│   ├── logger.py
│   └── gps_utils.py
└── main.py            # Main application entry point
```

## Usage

### Running the main application

```bash
python3 main.py --config config.yaml
```

### Running individual modules

```bash
# Test detection
python3 -m detection.defect_detector --image test.jpg

# Test camera
python3 -m camera.capture

# Test flight control
python3 -m flight.autopilot --simulate
```

## Development

### Setting up development environment

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run tests
pytest tests/
```

### Code Style

Please follow PEP 8 guidelines. Use `black` for formatting:

```bash
pip install black
black src/
```
