# Straßenschaden-Erkennung mit YOLOv8

**[English](README.md)** | **[Deutsch]**

Eine komplette Machine-Learning-Pipeline zum Trainieren, Exportieren und Bereitstellen eines Straßenschaden-Erkennungsmodells, optimiert für **Raspberry Pi Zero 2 WH** mit **Google Coral TPU-Accelerator**.

## Überblick

Dieses Projekt trainiert ein KI-Modell mit **YOLOv8** (You Only Look Once Version 8), um Straßenschäden in Bildern und Videostreams zu erkennen. Das trainierte Modell wird dann in das **TensorFlow Lite**-Format mit INT8-Quantisierung exportiert, wodurch es leicht und effizient genug wird, um auf Edge-Geräten wie dem Raspberry Pi Zero 2 WH mit Hardware-Beschleunigung über den Google Coral USB-Accelerator ausgeführt zu werden.

### Warum YOLOv8?

**YOLO (You Only Look Once)** ist ein hochmoderner Echtzeit-Objekterkennungsalgorithmus. Wir verwenden **YOLOv8n** (die Nano-Variante), weil:

- **Geschwindigkeit**: Erkennung in einem einzigen Durchlauf macht es ideal für Echtzeitanwendungen
- **Effizienz**: Die 'n' (Nano)-Variante ist die kleinste und schnellste, perfekt für Edge-Geräte
- **Genauigkeit**: Trotz seiner geringen Größe bietet es hervorragende Erkennungsleistung
- **Edge-Ready**: Einfach nach TensorFlow Lite exportierbar für die Bereitstellung auf ressourcenbeschränkten Geräten

**Python Version Requirements**

**Python 3.9 - 3.12** ist erforderlich aufgrund von Dependencies der `ultralytics`-Library (YOLOv8-Implementierung) und Kompatibilität mit PyTorch, TensorFlow Lite und anderen ML-Frameworks.

---

## Projektstruktur

```
.
├── .env.example              # Environment Variables Template
├── train/                    # Training Scripts
│   ├── train.py             # Haupt-Trainingsskript
│   └── validate.py          # Modell-Validierungsskript
├── utilities/               # Utilities
│   ├── export_model.py      # Modell-Export nach TFLite
│   └── utils.py            # Shared Utility Functions
└── detect/                  # Detection Scripts zum Testen
    ├── detect_video.py      # Straßenschäden in Videodateien erkennen
    └── detect_webcam.py     # Echtzeit-Webcam-Erkennung
```

---

## Konfiguration

### `.env.example`

Kopieren Sie `.env.example` nach `.env` und konfigurieren Sie die folgenden Variablen:

```bash
ROBOFLOW_API_KEY=          # Ihr Roboflow API Key für den Dataset Download
ROBOFLOW_WORKSPACE=        # Ihr Roboflow Workspace Name
ROBOFLOW_PROJECT=          # Ihre Roboflow Project ID
ROBOFLOW_PROJECT_NAME=     # Lesbarer Project Name (optional, Standard ist PROJECT)
ROBOFLOW_PROJECT_VERSION=  # Dataset Version Number (z.B. "1")
```

Diese Variablen verbinden sich mit Ihrem Roboflow Account, um automatisch das gelabelte Straßenschaden-Dataset für das Training herunterzuladen.

---

## Training

### `train/train.py`

Trainiert ein YOLOv8n-Modell auf Ihrem Straßenschaden-Datensatz. Lädt den Datensatz automatisch von Roboflow herunter, falls nicht vorhanden.

**Key Features:**
- Erkennt automatisch verfügbare Hardware (CUDA GPU, Apple MPS oder CPU)
- Lädt Dataset automatisch von Roboflow herunter
- Konfigurierbare Hyperparameter für optimales Training

**Training Parameters** (`model.train()`):

| Parameter | Wert | Beschreibung |
|-----------|------|--------------|
| `data` | `yaml_path` | Pfad zur Dataset-Konfigurations-YAML |
| `epochs` | `300` | Anzahl der Training Epochs |
| `imgsz` | `640` | Input Image Size (640x640 Pixel) |
| `batch` | `16` | Batch Size für das Training |
| `name` | `PROJECT_NAME` | Name für den Training Run |
| `project` | `'./runs/detect'` | Verzeichnis zum Speichern der Trainingsergebnisse |
| `patience` | `50` | Early Stopping Patience (stoppt bei keiner Verbesserung) |
| `save` | `True` | Checkpoints während des Trainings speichern |
| `device` | Automatisch erkannt | Device zum Trainieren (GPU/CPU/MPS) |
| `workers` | `2` (GPU) oder `0` (CPU) | Anzahl der Data Loading Workers |
| `cache` | `'disk'` | Images auf Disk cachen für schnelleres Laden |
| `amp` | `True` (nur GPU) | Automatic Mixed Precision Training |
| `lr0` | `0.01` | Initial Learning Rate |
| `lrf` | `0.1` | Final Learning Rate Factor (lr0 * lrf = final lr) |
| `warmup_epochs` | `5` | Learning Rate Warmup Epochs |
| `box` | `7.5` | Box Loss Weight (Bounding Box Regression) |
| `cls` | `1.0` | Classification Loss Weight |

**Verwendung:**
```bash
cd train
python train.py
```

**Output:** Trainiertes Modell gespeichert in `train/runs/detect/{PROJECT_NAME}/weights/best.pt`

---

### `train/validate.py`

Validiert das trainierte Modell auf dem Test-/Validierungs-Dataset zur Performance-Bewertung.

**Metrics:**
- **mAP50**: Mean Average Precision bei IoU-Schwellenwert 0.50
- **mAP50-95**: Mean Average Precision über IoU-Schwellenwerte 0.50 bis 0.95
- **Precision**: Verhältnis von True Positives zu allen positiven Vorhersagen
- **Recall**: Verhältnis von True Positives zu allen tatsächlichen Positives

**IoU (Intersection over Union) verstehen:**

IoU misst, wie gut eine vorhergesagte Bounding Box mit der Ground Truth (tatsächlichen) Bounding Box überlappt:

```
IoU = Überlappungsfläche / Vereinigungsfläche
```

- **IoU = 1.0** (100%): Perfekte Übereinstimmung - vorhergesagte Box entspricht exakt der Ground Truth
- **IoU = 0.5** (50%): Anständige Überlappung - häufig als Mindestschwellenwert verwendet
- **IoU = 0.0** (0%): Keine Überlappung

**In den obigen Metriken:**
- **mAP50**: Eine Erkennung zählt als "korrekt", wenn IoU ≥ 0.5 (nachsichtiger, erlaubt etwas Positionierungsfehler)
- **mAP50-95**: Gemittelt über IoU-Schwellenwerte von 0.50 bis 0.95 in Schritten von 0.05 (strenger, erfordert präzise Bounding Boxes)

Höhere IoU-Schwellenwerte erfordern präzisere Erkennungen. Für die Straßenschaden-Erkennung zeigt ein IoU von 0.7+ eine gute Lokalisierung an, während 0.9+ ausgezeichnet ist.

**Verwendung:**
```bash
cd train
python validate.py
```

---

## Modellexport

### `utilities/export_model.py`

Exportiert das trainierte PyTorch-Modell in das **TensorFlow Lite**-Format, optimiert für die Raspberry-Pi-Bereitstellung.

**Export Parameters** (`model.export()`):

| Parameter | Wert | Beschreibung |
|-----------|------|--------------|
| `format` | `'tflite'` | Export in TensorFlow Lite Format |
| `int8` | `True` | INT8 Quantization aktivieren (~75% Größenreduktion) |
| `imgsz` | `320` | Reduzierte Image Size für schnellere Inference auf Edge Devices |
| `device` | `'cpu'` | CPU für Export erzwingen (erforderlich für TFLite Optimization) |
| `optimize` | `True` | Zusätzliche TFLite Optimizations anwenden |
| `simplify` | `True` | Model Graph Structure vereinfachen |
| `data` | `'../dataset/data.yaml'` | Dataset YAML für Calibration während der Quantization |

**INT8 Quantization:** Konvertiert 32-Bit Floating-Point Weights in 8-Bit Integers, wodurch die Modellgröße dramatisch reduziert wird (~4x kleiner) bei gleichbleibender Accuracy. Essentiell für Edge Deployment.

**Verwendung:**
```bash
cd utilities
python export_model.py
```

**Output:** 
- Quantized TFLite Model gespeichert in `train/runs/detect/{PROJECT_NAME}/weights/best_saved_model/best_int8.tflite`
- Anweisungen für Edge TPU Compilation auf Raspberry Pi ausgegeben

**Nächste Schritte (auf Raspberry Pi):**
1. Übertragen Sie die `.tflite`-Datei auf Ihren Raspberry Pi
2. Installieren Sie den Edge TPU Compiler
3. Kompilieren für Coral TPU: `edgetpu_compiler best_int8.tflite`
4. Verwenden Sie die generierte `*_edgetpu.tflite`-Datei mit dem Coral USB-Accelerator

---

## Utilities

### `utilities/utils.py`

Shared Utility Functions, die projektübergreifend verwendet werden:

**Functions:**

- **`get_device()`**: Erkennt automatisch das beste verfügbare Compute Device
  - Return: `(device, device_name)` Tuple
  - Priorität: CUDA GPU > Apple MPS > CPU
  
- **`update_yaml_classes(yaml_path, class_names, verbose=True)`**: Aktualisiert Class Names in der YOLO Dataset YAML-Datei
  - Nützlich zum Umbenennen von Detection Classes nach dem Dataset Download

---

## Erkennung & Testen

### `detect/detect_video.py`

Verarbeitet Videodateien und annotiert erkannte Straßenschäden Frame für Frame.

**Features:**
- Unterstützt sowohl `.pt` (PyTorch) als auch `.tflite` (TensorFlow Lite) Models
- Konfigurierbarer Confidence Threshold
- Progress Tracking mit Frame Counter
- Speichert annotiertes Video Output

**Verwendung:**
```bash
cd detect
python detect_video.py
```

**Konfiguration:** Bearbeiten Sie das Script, um `VIDEO_PATH`, `OUTPUT_PATH` und `MODEL_PATH` festzulegen.

---

### `detect/detect_webcam.py`

Echtzeit-Straßenschaden-Erkennung mit einer angeschlossenen Webcam.

**Features:**
- Live Video Stream Processing
- Unterstützt sowohl `.pt` als auch `.tflite` Models
- Drücken Sie 'q' zum Beenden
- Frame Counter für Performance Monitoring

**Verwendung:**
```bash
cd detect
python detect_webcam.py
```

**Konfiguration:** Bearbeiten Sie das Script, um `MODEL_PATH` und `CONFIDENCE` Threshold festzulegen.

---

## Installation

```bash
# Dependencies installieren
pip install ultralytics roboflow opencv-python python-dotenv

# Environment konfigurieren
cp .env.example .env
# Bearbeiten Sie .env mit Ihren Roboflow Credentials

# Modell trainieren
cd train
python train.py

# Modell validieren
python validate.py

# Für Raspberry Pi exportieren
cd ../utilities
python export_model.py

# Mit Video oder Webcam testen
cd ../detect
python detect_webcam.py
```

---

## Hardware-Beschleunigung

Das exportierte TFLite-Modell kann den **Google Coral USB-Accelerator** nutzen für bis zu **10x schnellere Inference** auf dem Raspberry Pi Zero 2 WH. Nach dem Ausführen des Edge TPU Compilers wird das Modell automatisch die TPU nutzen, wenn verfügbar.

---

## Lizenz

Dieses Projekt wird wie besehen für Bildungs- und Forschungszwecke bereitgestellt.
