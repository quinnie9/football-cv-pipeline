"""Video read/write helpers. Implemented in later HUs; stubs keep imports stable."""

from __future__ import annotations

from typing import List

import numpy as np


def read_video(path: str) -> List[np.ndarray]:
    """Load all frames from a video file (BGR)."""
    raise NotImplementedError("HU-3+/HU-9: implement with OpenCV VideoCapture")


def save_video(frames: List[np.ndarray], path: str, fps: float = 25.0) -> None:
    """Write frames to a video file."""
    raise NotImplementedError("HU-9: implement with OpenCV VideoWriter")
