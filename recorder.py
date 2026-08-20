"""
recorder.py - Non-blocking Video Recorder for EdgeCam
------------------------------------------------------
Handles video file generation using OpenCV VideoWriter and a dedicated background thread queue
so file saving never causes GUI stuttering or frame drops.
"""

import cv2
import os
import time
import queue
import threading
from datetime import datetime
import numpy as np


class VideoRecorder:
    """
    Asynchronous Video Recorder using OpenCV VideoWriter.
    """
    def __init__(self, output_dir: str = "recordings"):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)
        
        self.is_recording = False
        self.writer = None
        self.output_filepath = ""
        self.start_time = 0
        self.frame_queue = queue.Queue()
        self.worker_thread = None
        self.fps = 30.0
        self.frame_size = (640, 480)

    def start(self, width: int, height: int, fps: float = 30.0) -> str:
        """
        Starts video recording with specified dimensions and FPS.
        Returns output file path.
        """
        if self.is_recording:
            return self.output_filepath

        self.fps = max(10.0, fps)
        self.frame_size = (width, height)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"EdgeCam_Record_{timestamp}.mp4"
        self.output_filepath = os.path.join(self.output_dir, filename)

        # Codec selection for mp4 / avi on Windows
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        self.writer = cv2.VideoWriter(self.output_filepath, fourcc, self.fps, self.frame_size)
        
        if not self.writer.isOpened():
            # Fallback to AVI with XVID codec if mp4v fails
            filename = f"EdgeCam_Record_{timestamp}.avi"
            self.output_filepath = os.path.join(self.output_dir, filename)
            fourcc = cv2.VideoWriter_fourcc(*'XVID')
            self.writer = cv2.VideoWriter(self.output_filepath, fourcc, self.fps, self.frame_size)

        self.is_recording = True
        self.start_time = time.time()
        self.frame_queue = queue.Queue()

        self.worker_thread = threading.Thread(target=self._write_loop, daemon=True)
        self.worker_thread.start()

        return self.output_filepath

    def write_frame(self, frame: np.ndarray):
        """Pushes a processed frame into the write queue."""
        if self.is_recording and frame is not None:
            # Resize frame if it doesn't match initial VideoWriter resolution
            h, w = frame.shape[:2]
            if (w, h) != self.frame_size:
                frame = cv2.resize(frame, self.frame_size)
            self.frame_queue.put(frame.copy())

    def _write_loop(self):
        """Worker loop reading frames from queue and writing to disk."""
        while self.is_recording or not self.frame_queue.empty():
            try:
                frame = self.frame_queue.get(timeout=0.1)
                if self.writer and self.writer.isOpened():
                    self.writer.write(frame)
                self.frame_queue.task_done()
            except queue.Empty:
                continue

    def get_duration_formatted(self) -> str:
        """Returns formatted string MM:SS of elapsed recording time."""
        if not self.is_recording:
            return "00:00"
        elapsed = int(time.time() - self.start_time)
        minutes = elapsed // 60
        seconds = elapsed % 60
        return f"{minutes:02d}:{seconds:02d}"

    def stop(self) -> str:
        """Stops recording, flushes queue, closes file writer, and returns filepath."""
        if not self.is_recording:
            return ""

        self.is_recording = False
        
        if self.worker_thread:
            self.worker_thread.join(timeout=2.0)
            self.worker_thread = None

        if self.writer:
            self.writer.release()
            self.writer = None

        filepath = self.output_filepath
        self.output_filepath = ""
        return filepath
