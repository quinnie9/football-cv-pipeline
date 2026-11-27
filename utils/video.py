"""Video read/write helpers."""

from __future__ import annotations

from pathlib import Path
from typing import List, Tuple

import cv2
import numpy as np


def read_video(path: str) -> List[np.ndarray]:
    """Load all frames from a video file (BGR)."""
    cap = cv2.VideoCapture(path)
    if not cap.isOpened():
        raise FileNotFoundError(f"Cannot open video: {path}")
    frames: List[np.ndarray] = []
    while True:
        ok, frame = cap.read()
        if not ok:
            break
        frames.append(frame)
    cap.release()
    if not frames:
        raise RuntimeError(f"No frames read from {path}")
    return frames


def get_video_meta(path: str) -> Tuple[float, int, int, int]:
    """Return fps, width, height, frame_count (frame_count may be 0 if unknown)."""
    cap = cv2.VideoCapture(path)
    if not cap.isOpened():
        raise FileNotFoundError(f"Cannot open video: {path}")
    fps = float(cap.get(cv2.CAP_PROP_FPS) or 25.0)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    n = int(cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
    cap.release()
    return fps, width, height, n


def save_video(frames: List[np.ndarray], path: str, fps: float = 25.0) -> None:
    """Write frames to a video file (mp4v)."""
    if not frames:
        raise ValueError("No frames to write")
    path_obj = Path(path)
    path_obj.parent.mkdir(parents=True, exist_ok=True)
    h, w = frames[0].shape[:2]
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    writer = cv2.VideoWriter(str(path_obj), fourcc, fps, (w, h))
    if not writer.isOpened():
        raise RuntimeError(f"Cannot open VideoWriter for {path}")
    for frame in frames:
        writer.write(frame)
    writer.release()
