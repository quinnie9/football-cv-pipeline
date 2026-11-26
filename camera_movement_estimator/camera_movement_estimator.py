"""Estimate and compensate camera pan between frames (HU-6.1)."""

from __future__ import annotations

from typing import Any, List, Optional


class CameraMovementEstimator:
    def __init__(self, first_frame) -> None:
        self.first_frame = first_frame

    def get_camera_movement(
        self,
        frames: List[Any],
        read_from_stub: bool = False,
        stub_path: Optional[str] = None,
    ):
        raise NotImplementedError("HU-6.1")
