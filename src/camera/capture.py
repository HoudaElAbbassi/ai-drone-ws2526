#!/usr/bin/env python3
"""
Camera capture module for Raspberry Pi Camera Module v2
"""

import time
import threading
from queue import Queue
from typing import Optional, Tuple
import numpy as np

try:
    from picamera2 import Picamera2
    from picamera2.configuration import CameraConfiguration
    PICAMERA_AVAILABLE = True
except ImportError:
    PICAMERA_AVAILABLE = False
    print("WARNING: picamera2 not available. Using fallback.")

import cv2
from ..config import CAMERA_CONFIG


class CameraCapture:
    """
    Camera capture class for Raspberry Pi Camera Module v2
    """

    def __init__(self, resolution: Tuple[int, int] = None,
                 framerate: int = None):
        """
        Initialize camera capture

        Args:
            resolution: Camera resolution (width, height)
            framerate: Frames per second
        """
        self.resolution = resolution or CAMERA_CONFIG["resolution"]
        self.framerate = framerate or CAMERA_CONFIG["framerate"]

        self.camera = None
        self.frame_queue = Queue(maxsize=30)
        self.running = False
        self.capture_thread = None
        self.frame_count = 0
        self.start_time = None

    def start(self):
        """Start camera capture"""
        if PICAMERA_AVAILABLE:
            self._start_picamera()
        else:
            self._start_opencv()

        self.running = True
        self.start_time = time.time()
        self.capture_thread = threading.Thread(target=self._capture_loop, daemon=True)
        self.capture_thread.start()

        print(f"Camera started: {self.resolution[0]}x{self.resolution[1]} @ {self.framerate}fps")

    def _start_picamera(self):
        """Initialize Picamera2"""
        self.camera = Picamera2()

        # Configure camera
        config = self.camera.create_video_configuration(
            main={"size": self.resolution, "format": "RGB888"},
            controls={"FrameRate": self.framerate}
        )
        self.camera.configure(config)
        self.camera.start()

        # Wait for camera to warm up
        time.sleep(1)

    def _start_opencv(self):
        """Initialize OpenCV camera (fallback)"""
        self.camera = cv2.VideoCapture(0)
        self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, self.resolution[0])
        self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, self.resolution[1])
        self.camera.set(cv2.CAP_PROP_FPS, self.framerate)

        if not self.camera.isOpened():
            raise RuntimeError("Failed to open camera")

    def _capture_loop(self):
        """Main capture loop (runs in separate thread)"""
        while self.running:
            try:
                if PICAMERA_AVAILABLE and isinstance(self.camera, Picamera2):
                    # Capture from Picamera2
                    frame = self.camera.capture_array()
                else:
                    # Capture from OpenCV
                    ret, frame = self.camera.read()
                    if not ret:
                        print("Failed to capture frame")
                        time.sleep(0.1)
                        continue

                    # Convert BGR to RGB
                    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

                # Add frame to queue (non-blocking)
                if not self.frame_queue.full():
                    self.frame_queue.put((time.time(), frame))
                    self.frame_count += 1
                else:
                    # Queue full, skip frame
                    pass

                # Control frame rate
                time.sleep(1.0 / self.framerate)

            except Exception as e:
                print(f"Error in capture loop: {e}")
                time.sleep(0.1)

    def get_frame(self, timeout: float = 1.0) -> Optional[Tuple[float, np.ndarray]]:
        """
        Get the next frame from the queue

        Args:
            timeout: Maximum time to wait for frame

        Returns:
            Tuple of (timestamp, frame) or None if timeout
        """
        try:
            return self.frame_queue.get(timeout=timeout)
        except:
            return None

    def get_fps(self) -> float:
        """Get actual capture FPS"""
        if self.start_time is None or self.frame_count == 0:
            return 0.0
        elapsed = time.time() - self.start_time
        return self.frame_count / elapsed if elapsed > 0 else 0.0

    def stop(self):
        """Stop camera capture"""
        self.running = False

        if self.capture_thread:
            self.capture_thread.join(timeout=2.0)

        if self.camera:
            if PICAMERA_AVAILABLE and isinstance(self.camera, Picamera2):
                self.camera.stop()
            else:
                self.camera.release()

        print(f"Camera stopped. Captured {self.frame_count} frames.")

    def __enter__(self):
        """Context manager entry"""
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.stop()


class MockCamera(CameraCapture):
    """
    Mock camera for testing without hardware
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def _start_picamera(self):
        """Mock camera initialization"""
        print("Using mock camera (no hardware)")

    def _start_opencv(self):
        """Mock camera initialization"""
        print("Using mock camera (no hardware)")

    def _capture_loop(self):
        """Generate test frames"""
        while self.running:
            try:
                # Generate a random colored frame
                frame = np.random.randint(0, 255,
                    (self.resolution[1], self.resolution[0], 3),
                    dtype=np.uint8)

                # Add frame counter text
                cv2.putText(frame, f"Frame: {self.frame_count}",
                           (10, 30), cv2.FONT_HERSHEY_SIMPLEX,
                           1, (255, 255, 255), 2)

                if not self.frame_queue.full():
                    self.frame_queue.put((time.time(), frame))
                    self.frame_count += 1

                time.sleep(1.0 / self.framerate)

            except Exception as e:
                print(f"Error in mock capture: {e}")
                time.sleep(0.1)


# Test code
if __name__ == "__main__":
    print("Testing camera capture...")

    with CameraCapture() as camera:
        print("Camera started. Press Ctrl+C to stop.")

        try:
            for i in range(100):
                result = camera.get_frame()
                if result:
                    timestamp, frame = result
                    print(f"Frame {i}: {frame.shape}, FPS: {camera.get_fps():.1f}")
                else:
                    print(f"Frame {i}: Timeout")

        except KeyboardInterrupt:
            print("\nStopping...")

    print("Camera test complete.")
