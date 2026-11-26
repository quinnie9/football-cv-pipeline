"""I/O and geometry helpers (bbox, video read/write, foot position)."""

from .bbox import get_center_of_bbox, get_bbox_width, get_foot_position

__all__ = [
    "get_center_of_bbox",
    "get_bbox_width",
    "get_foot_position",
    "read_video",
    "save_video",
]


def __getattr__(name: str):
    if name in {"read_video", "save_video"}:
        from . import video

        return getattr(video, name)
    raise AttributeError(name)
