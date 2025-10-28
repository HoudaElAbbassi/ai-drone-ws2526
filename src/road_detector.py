#!/usr/bin/env python3
"""
Main Road Damage Detection System
Integrates camera, AI detection, and GPS tracking
"""

import time
import json
import sqlite3
from pathlib import Path
from datetime import datetime
from typing import List
import cv2
import numpy as np

from .camera.capture import CameraCapture, MockCamera
from .detection.detector import RoadDamageDetector
from .gps.tracker import GPSTracker, MockGPS
from .config import *


class RoadDamageDetectionSystem:
    """
    Complete road damage detection system
    """

    def __init__(self, use_mock: bool = False):
        """
        Initialize the system

        Args:
            use_mock: Use mock hardware for testing
        """
        self.use_mock = use_mock

        # Components
        self.camera = None
        self.detector = None
        self.gps = None
        self.db_conn = None

        # Statistics
        self.frame_count = 0
        self.detection_count = 0
        self.start_time = None

        # Initialize database
        self._init_database()

    def _init_database(self):
        """Initialize SQLite database for storing detections"""
        db_path = DETECTION_CONFIG["database"]
        db_path.parent.mkdir(parents=True, exist_ok=True)

        self.db_conn = sqlite3.connect(str(db_path), check_same_thread=False)
        cursor = self.db_conn.cursor()

        # Create tables
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS detections (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp REAL NOT NULL,
                datetime TEXT NOT NULL,
                latitude REAL,
                longitude REAL,
                altitude REAL,
                class_id INTEGER NOT NULL,
                class_name TEXT NOT NULL,
                confidence REAL NOT NULL,
                severity TEXT NOT NULL,
                bbox_xmin INTEGER,
                bbox_ymin INTEGER,
                bbox_xmax INTEGER,
                bbox_ymax INTEGER,
                area_percentage REAL,
                image_path TEXT,
                gps_fix_quality INTEGER
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                start_time REAL NOT NULL,
                end_time REAL,
                total_frames INTEGER,
                total_detections INTEGER,
                avg_fps REAL
            )
        ''')

        self.db_conn.commit()
        print(f"Database initialized: {db_path}")

    def start(self):
        """Start the detection system"""
        print("="*60)
        print("  Road Damage Detection System")
        print("="*60)

        self.start_time = time.time()

        # Initialize components
        print("\n[1/3] Initializing Camera...")
        if self.use_mock:
            self.camera = MockCamera()
        else:
            self.camera = CameraCapture()
        self.camera.start()

        print("\n[2/3] Loading AI Model...")
        self.detector = RoadDamageDetector(use_coral=SYSTEM_CONFIG["use_coral"])

        print("\n[3/3] Starting GPS Tracker...")
        if self.use_mock:
            self.gps = MockGPS()
        else:
            self.gps = GPSTracker()
        self.gps.start()

        print("\n" + "="*60)
        print("  System Ready!")
        print("="*60)
        print(f"  Camera: {self.camera.resolution[0]}x{self.camera.resolution[1]} @ {self.camera.framerate}fps")
        print(f"  AI Model: {'Coral TPU' if SYSTEM_CONFIG['use_coral'] else 'CPU'}")
        print(f"  Detection threshold: {MODEL_CONFIG['confidence_threshold']}")
        print("="*60 + "\n")

    def process_frame(self, save_detections: bool = True):
        """
        Process one frame from camera

        Args:
            save_detections: Save detections to database

        Returns:
            Number of detections found
        """
        # Get frame from camera
        result = self.camera.get_frame(timeout=2.0)
        if result is None:
            print("No frame received")
            return 0

        timestamp, frame = result
        self.frame_count += 1

        # Run detection
        detections = self.detector.detect(frame)

        # Get GPS position
        gps_data = self.gps.get_current_position()

        # Process detections
        if detections:
            print(f"\n[Frame {self.frame_count}] Found {len(detections)} damage(s):")

            for i, det in enumerate(detections, 1):
                print(f"  {i}. {det}")

                if gps_data:
                    print(f"     Location: {gps_data.latitude:.6f}, {gps_data.longitude:.6f}")

                # Save to database
                if save_detections:
                    self._save_detection(det, timestamp, gps_data, frame)

            self.detection_count += len(detections)

        # Print status every 10 frames
        if self.frame_count % 10 == 0:
            self._print_status()

        return len(detections)

    def _save_detection(self, detection, timestamp, gps_data, frame):
        """Save detection to database and optionally save image"""
        cursor = self.db_conn.cursor()

        # Save image if configured
        image_path = None
        if DETECTION_CONFIG["save_images"]:
            image_dir = DETECTION_CONFIG["detection_dir"]
            image_dir.mkdir(parents=True, exist_ok=True)

            # Generate filename
            dt = datetime.fromtimestamp(timestamp)
            filename = f"{dt.strftime('%Y%m%d_%H%M%S')}_{self.detection_count:04d}_{detection.class_name}.jpg"
            image_path = image_dir / filename

            # Draw detection and save
            result_image = self.detector.draw_detections(frame, [detection])
            cv2.imwrite(str(image_path), cv2.cvtColor(result_image, cv2.COLOR_RGB2BGR))

            # Optionally save cropped region
            if DETECTION_CONFIG["save_crops"]:
                x1, y1, x2, y2 = detection.bbox
                crop = frame[y1:y2, x1:x2]
                crop_path = image_path.parent / f"crop_{image_path.name}"
                cv2.imwrite(str(crop_path), cv2.cvtColor(crop, cv2.COLOR_RGB2BGR))

        # Insert into database
        cursor.execute('''
            INSERT INTO detections (
                timestamp, datetime, latitude, longitude, altitude,
                class_id, class_name, confidence, severity,
                bbox_xmin, bbox_ymin, bbox_xmax, bbox_ymax,
                area_percentage, image_path, gps_fix_quality
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            timestamp,
            datetime.fromtimestamp(timestamp).isoformat(),
            gps_data.latitude if gps_data else None,
            gps_data.longitude if gps_data else None,
            gps_data.altitude if gps_data else None,
            detection.class_id,
            detection.class_name,
            detection.confidence,
            detection.severity,
            detection.bbox[0],
            detection.bbox[1],
            detection.bbox[2],
            detection.bbox[3],
            detection.area_percentage,
            str(image_path) if image_path else None,
            gps_data.fix_quality if gps_data else None
        ))

        self.db_conn.commit()

    def _print_status(self):
        """Print system status"""
        elapsed = time.time() - self.start_time
        camera_fps = self.camera.get_fps()
        detector_fps = self.detector.get_fps()
        gps_fix_age = self.gps.get_fix_age()

        print("\n" + "="*60)
        print(f"  Runtime: {elapsed:.1f}s")
        print(f"  Frames processed: {self.frame_count}")
        print(f"  Total detections: {self.detection_count}")
        print(f"  Camera FPS: {camera_fps:.1f}")
        print(f"  Detector FPS: {detector_fps:.1f} (avg inference: {self.detector.get_avg_inference_time():.1f}ms)")
        print(f"  GPS fix: {'YES' if self.gps.has_fix() else 'NO'} (age: {gps_fix_age:.1f}s)")
        if self.gps.current_gps:
            print(f"  Position: {self.gps.current_gps.latitude:.6f}, {self.gps.current_gps.longitude:.6f}")
        print("="*60)

    def run(self, duration: float = None):
        """
        Run detection continuously

        Args:
            duration: Run for specified seconds (None = infinite)
        """
        print("\nStarting detection... (Press Ctrl+C to stop)\n")

        end_time = time.time() + duration if duration else None

        try:
            while True:
                # Check if duration expired
                if end_time and time.time() >= end_time:
                    break

                # Process frame
                self.process_frame()

                # Small delay to prevent busy loop
                time.sleep(0.01)

        except KeyboardInterrupt:
            print("\n\nStopping...")

    def export_report(self, output_path: Path = None):
        """
        Export detection report to JSON

        Args:
            output_path: Output file path
        """
        if output_path is None:
            output_path = DATA_DIR / f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        cursor = self.db_conn.cursor()

        # Get all detections
        cursor.execute('''
            SELECT * FROM detections ORDER BY timestamp
        ''')

        columns = [desc[0] for desc in cursor.description]
        detections = []

        for row in cursor.fetchall():
            det_dict = dict(zip(columns, row))
            detections.append(det_dict)

        # Create report
        report = {
            "generated_at": datetime.now().isoformat(),
            "session": {
                "start_time": datetime.fromtimestamp(self.start_time).isoformat(),
                "duration": time.time() - self.start_time,
                "total_frames": self.frame_count,
                "total_detections": self.detection_count,
                "camera_fps": self.camera.get_fps(),
                "detector_fps": self.detector.get_fps(),
            },
            "detections": detections,
            "summary": self._get_summary(),
        }

        # Save to file
        with open(output_path, 'w') as f:
            json.dump(report, f, indent=2)

        print(f"\nReport exported to: {output_path}")
        return output_path

    def _get_summary(self) -> dict:
        """Get detection summary statistics"""
        cursor = self.db_conn.cursor()

        # Count by class
        cursor.execute('''
            SELECT class_name, COUNT(*) as count
            FROM detections
            GROUP BY class_name
        ''')
        by_class = dict(cursor.fetchall())

        # Count by severity
        cursor.execute('''
            SELECT severity, COUNT(*) as count
            FROM detections
            GROUP BY severity
        ''')
        by_severity = dict(cursor.fetchall())

        return {
            "by_class": by_class,
            "by_severity": by_severity,
            "total": self.detection_count,
        }

    def stop(self):
        """Stop the detection system"""
        print("\nShutting down system...")

        if self.camera:
            self.camera.stop()

        if self.gps:
            self.gps.stop()

        if self.db_conn:
            self.db_conn.close()

        # Print final status
        self._print_status()

        print("\nSystem stopped.")

    def __enter__(self):
        """Context manager entry"""
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.stop()


# Main entry point
def main():
    """Main function"""
    import argparse

    parser = argparse.ArgumentParser(description="Road Damage Detection System")
    parser.add_argument("--mock", action="store_true",
                       help="Use mock hardware for testing")
    parser.add_argument("--duration", type=float, default=None,
                       help="Run for specified seconds")
    parser.add_argument("--export", action="store_true",
                       help="Export report after run")

    args = parser.parse_args()

    # Create and run system
    with RoadDamageDetectionSystem(use_mock=args.mock) as system:
        system.run(duration=args.duration)

        if args.export:
            system.export_report()


if __name__ == "__main__":
    main()
