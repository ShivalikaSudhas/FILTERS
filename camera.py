"""
camera.py - Webcam Manager for EdgeCam
---------------------------------------
Handles camera initialization, thread-safe frame acquisition, and resource cleanup.
"""

import cv2
import threading
import time
import typing


class CameraManager:
    """
    Manages OpenCV VideoCapture in a background thread.
    """
    def __init__(self, camera_index: int = 0):
        self.camera_index = camera_index
        self.cap: typing.Optional[cv2.VideoCapture] = None
        self.running = False
        self.thread: typing.Optional[threading.Thread] = None
        self.lock = threading.Lock()
        
        self.latest_frame = None
        self.is_opened = False
        self.frame_width = 640
        self.frame_height = 480
        self.fps = 30.0

        self.start(camera_index)

    def start(self, camera_index: int = 0):
        """Starts webcam capture on specified camera index."""
        self.stop()
        self.camera_index = camera_index
        
        # Standard video capture initialization
        self.cap = cv2.VideoCapture(self.camera_index)

        if self.cap.isOpened():
            self.is_opened = True
            w = self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)
            h = self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
            fps = self.cap.get(cv2.CAP_PROP_FPS)
            
            if w > 0 and h > 0:
                self.frame_width = int(w)
                self.frame_height = int(h)
            if fps > 0:
                self.fps = fps

            self.running = True
            self.thread = threading.Thread(target=self._update_loop, daemon=True)
            self.thread.start()
        else:
            self.is_opened = False
            self.latest_frame = None

    def _update_loop(self):
        """Continuously reads frames from camera in background thread."""
        while self.running and self.cap and self.cap.isOpened():
            ret, frame = self.cap.read()
            if ret:
                with self.lock:
                    self.latest_frame = frame
            else:
                time.sleep(0.01)

    def get_frame(self):
        """Returns latest BGR frame safely using thread lock."""
        with self.lock:
            if self.latest_frame is not None:
                return self.latest_frame.copy()
            return None

    def stop(self):
        """Stops capture thread and releases camera."""
        self.running = False
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=1.0)
        
        if self.cap:
            self.cap.release()
            self.cap = None
        self.is_opened = False

    def release(self):
        self.stop()
