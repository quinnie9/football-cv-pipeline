"""Bounding-box utilities."""

from __future__ import annotations

from typing import Sequence, Tuple


def get_center_of_bbox(bbox: Sequence[float]) -> Tuple[int, int]:
    x1, y1, x2, y2 = bbox
    return int((x1 + x2) / 2), int((y1 + y2) / 2)


def get_bbox_width(bbox: Sequence[float]) -> int:
    return int(bbox[2] - bbox[0])


def get_foot_position(bbox: Sequence[float]) -> Tuple[int, int]:
    """Bottom-center of the box — approximate ground contact for homography."""
    x1, _, x2, y2 = bbox
    return int((x1 + x2) / 2), int(y2)
