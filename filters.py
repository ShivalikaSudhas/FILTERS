"""
filters.py - Computer Vision Filters for EdgeCam
-----------------------------------------------
Provides the core Edge Detection filter pipeline (Grayscale -> Gaussian Blur -> Canny Edges).
"""

from abc import ABC, abstractmethod
import cv2
import numpy as np


class BaseFilter(ABC):
    """Abstract Base Class for frame processing filters."""
    def __init__(self, name: str):
        self.name = name

    @abstractmethod
    def apply(self, frame: np.ndarray) -> np.ndarray:
        """Processes BGR image frame and returns 3-channel BGR output."""
        pass


class EdgeFilter(BaseFilter):
    """
    Canny Edge Filter with configurable Gaussian Blur and dual thresholds.
    """
    def __init__(self, blur_kernel: int = 5, threshold1: int = 50, threshold2: int = 120, colored_edges: bool = False):
        super().__init__("Edge Detection")
        self.blur_kernel = self._make_odd(blur_kernel)
        self.threshold1 = threshold1
        self.threshold2 = threshold2
        self.colored_edges = colored_edges

    @staticmethod
    def _make_odd(val: int) -> int:
        val = max(1, val)
        return val if val % 2 != 0 else val + 1

    def set_blur(self, kernel_size: int):
        self.blur_kernel = self._make_odd(kernel_size)

    def set_thresholds(self, t1: int, t2: int):
        self.threshold1 = t1
        self.threshold2 = t2

    def apply(self, frame: np.ndarray) -> np.ndarray:
        if frame is None:
            return frame

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        blur = cv2.GaussianBlur(gray, (self.blur_kernel, self.blur_kernel), 0)
        edges = cv2.Canny(blur, self.threshold1, self.threshold2)

        if self.colored_edges:
            colored = np.zeros_like(frame)
            colored[edges > 0] = (0, 255, 0)
            return colored
        else:
            return cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)


# Active filter registry
AVAILABLE_FILTERS = {
    "Edge Detection": EdgeFilter
}
