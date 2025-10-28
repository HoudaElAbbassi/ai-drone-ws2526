#!/usr/bin/env python3
"""
Road damage detection module using TensorFlow Lite and Google Coral TPU
"""

import time
from typing import List, Tuple, Optional
import numpy as np
import cv2

try:
    from pycoral.adapters import common
    from pycoral.adapters import detect
    from pycoral.utils import edgetpu
    CORAL_AVAILABLE = True
except ImportError:
    CORAL_AVAILABLE = False
    print("WARNING: PyCoral not available. Coral TPU acceleration disabled.")

try:
    import tflite_runtime.interpreter as tflite
    TFLITE_AVAILABLE = True
except ImportError:
    TFLITE_AVAILABLE = False
    print("WARNING: TFLite runtime not available.")

from ..config import MODEL_CONFIG, DAMAGE_CLASSES, SEVERITY_THRESHOLDS


class Detection:
    """Class representing a single detection"""

    def __init__(self, class_id: int, confidence: float,
                 bbox: Tuple[int, int, int, int],
                 image_size: Tuple[int, int]):
        self.class_id = class_id
        self.class_name = DAMAGE_CLASSES.get(class_id, "unknown")
        self.confidence = confidence
        self.bbox = bbox  # (xmin, ymin, xmax, ymax)
        self.image_size = image_size

        # Calculate bbox area and severity
        bbox_area = (bbox[2] - bbox[0]) * (bbox[3] - bbox[1])
        image_area = image_size[0] * image_size[1]
        self.area_percentage = bbox_area / image_area if image_area > 0 else 0
        self.severity = self._calculate_severity()

    def _calculate_severity(self) -> str:
        """Calculate damage severity based on size"""
        if self.area_percentage < SEVERITY_THRESHOLDS["low"]:
            return "low"
        elif self.area_percentage < SEVERITY_THRESHOLDS["medium"]:
            return "medium"
        else:
            return "high"

    def to_dict(self) -> dict:
        """Convert detection to dictionary"""
        return {
            "class_id": self.class_id,
            "class_name": self.class_name,
            "confidence": float(self.confidence),
            "bbox": self.bbox,
            "severity": self.severity,
            "area_percentage": float(self.area_percentage),
        }

    def __repr__(self) -> str:
        return (f"Detection(class={self.class_name}, "
                f"conf={self.confidence:.2f}, "
                f"severity={self.severity})")


class RoadDamageDetector:
    """
    Road damage detector using TensorFlow Lite model
    with optional Google Coral TPU acceleration
    """

    def __init__(self, model_path: str = None,
                 labels_path: str = None,
                 use_coral: bool = True):
        """
        Initialize detector

        Args:
            model_path: Path to TFLite model
            labels_path: Path to labels file
            use_coral: Use Coral TPU if available
        """
        self.model_path = model_path or MODEL_CONFIG["model_path"]
        self.labels_path = labels_path or MODEL_CONFIG["labels_path"]
        self.use_coral = use_coral and CORAL_AVAILABLE

        self.interpreter = None
        self.input_details = None
        self.output_details = None
        self.input_size = MODEL_CONFIG["input_size"]
        self.threshold = MODEL_CONFIG["confidence_threshold"]

        self.inference_times = []
        self.detection_count = 0

        # Load model
        self._load_model()

    def _load_model(self):
        """Load TFLite model with optional Coral TPU"""
        print(f"Loading model from {self.model_path}")

        try:
            if self.use_coral:
                # Load model with Coral TPU
                print("Initializing Google Coral TPU...")
                self.interpreter = edgetpu.make_interpreter(str(self.model_path))
                print("✓ Coral TPU initialized successfully")
            else:
                # Load model with CPU
                print("Using CPU inference (Coral TPU disabled)")
                if TFLITE_AVAILABLE:
                    self.interpreter = tflite.Interpreter(
                        model_path=str(self.model_path)
                    )
                else:
                    raise RuntimeError("TFLite runtime not available")

            self.interpreter.allocate_tensors()

            # Get input and output details
            self.input_details = self.interpreter.get_input_details()
            self.output_details = self.interpreter.get_output_details()

            # Get input size from model
            input_shape = self.input_details[0]['shape']
            self.input_size = (input_shape[2], input_shape[1])  # (width, height)

            print(f"Model loaded successfully")
            print(f"  Input size: {self.input_size}")
            print(f"  Input dtype: {self.input_details[0]['dtype']}")
            print(f"  Quantized: {self.input_details[0]['dtype'] == np.uint8}")

        except Exception as e:
            print(f"Error loading model: {e}")
            raise

    def preprocess_image(self, image: np.ndarray) -> np.ndarray:
        """
        Preprocess image for model input

        Args:
            image: Input image (RGB, uint8)

        Returns:
            Preprocessed image
        """
        # Resize to model input size
        input_image = cv2.resize(image, self.input_size)

        # Check if model expects uint8 (quantized) or float32
        if self.input_details[0]['dtype'] == np.uint8:
            # Quantized model - keep as uint8
            return np.expand_dims(input_image, axis=0).astype(np.uint8)
        else:
            # Float model - normalize to [0, 1]
            input_image = input_image.astype(np.float32) / 255.0
            return np.expand_dims(input_image, axis=0)

    def detect(self, image: np.ndarray) -> List[Detection]:
        """
        Detect road damage in image

        Args:
            image: Input image (RGB, uint8)

        Returns:
            List of Detection objects
        """
        start_time = time.time()

        # Preprocess image
        input_data = self.preprocess_image(image)

        # Run inference
        self.interpreter.set_tensor(self.input_details[0]['index'], input_data)
        self.interpreter.invoke()

        # Get output
        if self.use_coral:
            # Coral TPU output format
            detections = detect.get_objects(
                self.interpreter,
                self.threshold,
                (image.shape[1] / self.input_size[0],  # x_scale
                 image.shape[0] / self.input_size[1])   # y_scale
            )

            # Convert to Detection objects
            results = []
            for det in detections:
                bbox = (
                    int(det.bbox.xmin),
                    int(det.bbox.ymin),
                    int(det.bbox.xmax),
                    int(det.bbox.ymax)
                )
                results.append(Detection(
                    class_id=det.id,
                    confidence=det.score,
                    bbox=bbox,
                    image_size=(image.shape[1], image.shape[0])
                ))

        else:
            # Standard TFLite output (COCO SSD format)
            boxes = self.interpreter.get_tensor(self.output_details[0]['index'])[0]
            classes = self.interpreter.get_tensor(self.output_details[1]['index'])[0]
            scores = self.interpreter.get_tensor(self.output_details[2]['index'])[0]
            count = int(self.interpreter.get_tensor(self.output_details[3]['index'])[0])

            results = []
            for i in range(count):
                if scores[i] >= self.threshold:
                    # Convert normalized coordinates to pixel coordinates
                    ymin, xmin, ymax, xmax = boxes[i]
                    bbox = (
                        int(xmin * image.shape[1]),
                        int(ymin * image.shape[0]),
                        int(xmax * image.shape[1]),
                        int(ymax * image.shape[0])
                    )

                    results.append(Detection(
                        class_id=int(classes[i]),
                        confidence=float(scores[i]),
                        bbox=bbox,
                        image_size=(image.shape[1], image.shape[0])
                    ))

        # Record inference time
        inference_time = (time.time() - start_time) * 1000  # ms
        self.inference_times.append(inference_time)
        self.detection_count += 1

        return results

    def draw_detections(self, image: np.ndarray,
                       detections: List[Detection]) -> np.ndarray:
        """
        Draw bounding boxes and labels on image

        Args:
            image: Input image
            detections: List of detections

        Returns:
            Image with drawn detections
        """
        result_image = image.copy()

        # Color map for different damage types
        colors = {
            "longitudinal_crack": (255, 0, 0),      # Red
            "transverse_crack": (0, 255, 0),        # Green
            "alligator_crack": (0, 0, 255),         # Blue
            "pothole": (255, 255, 0),               # Yellow
            "rutting": (255, 0, 255),               # Magenta
            "bleeding": (0, 255, 255),              # Cyan
            "weathering": (128, 128, 128),          # Gray
        }

        for det in detections:
            color = colors.get(det.class_name, (255, 255, 255))

            # Draw bounding box
            cv2.rectangle(result_image,
                         (det.bbox[0], det.bbox[1]),
                         (det.bbox[2], det.bbox[3]),
                         color, 2)

            # Draw label
            label = f"{det.class_name} ({det.severity}): {det.confidence:.2f}"
            label_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 2)[0]

            # Draw label background
            cv2.rectangle(result_image,
                         (det.bbox[0], det.bbox[1] - label_size[1] - 10),
                         (det.bbox[0] + label_size[0], det.bbox[1]),
                         color, -1)

            # Draw label text
            cv2.putText(result_image, label,
                       (det.bbox[0], det.bbox[1] - 5),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2)

        return result_image

    def get_avg_inference_time(self) -> float:
        """Get average inference time in milliseconds"""
        if not self.inference_times:
            return 0.0
        return sum(self.inference_times) / len(self.inference_times)

    def get_fps(self) -> float:
        """Get average FPS"""
        avg_time = self.get_avg_inference_time()
        return 1000.0 / avg_time if avg_time > 0 else 0.0

    def reset_stats(self):
        """Reset performance statistics"""
        self.inference_times = []
        self.detection_count = 0


# Test code
if __name__ == "__main__":
    print("Testing road damage detector...")

    # Create a test image
    test_image = np.random.randint(0, 255, (720, 1280, 3), dtype=np.uint8)

    try:
        detector = RoadDamageDetector()

        print("\nRunning detection test...")
        for i in range(10):
            detections = detector.detect(test_image)
            print(f"Frame {i}: {len(detections)} detections, "
                  f"inference time: {detector.inference_times[-1]:.1f}ms")

        print(f"\nAverage inference time: {detector.get_avg_inference_time():.1f}ms")
        print(f"Average FPS: {detector.get_fps():.1f}")

    except Exception as e:
        print(f"Error: {e}")
        print("\nNote: This test requires a trained model.")
        print("Place your model at: models/road_damage_edgetpu.tflite")
