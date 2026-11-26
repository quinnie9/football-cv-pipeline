"""Object tracker wrapper (YOLO11 + ByteTrack). Logic lands in HU-3.x."""

from __future__ import annotations

from typing import Any, Dict, List, Optional


class Tracker:
    def __init__(self, model_path: str) -> None:
        self.model_path = model_path

    def get_object_tracks(
        self,
        frames: List[Any],
        read_from_stub: bool = False,
        stub_path: Optional[str] = None,
    ) -> Dict[str, List[Dict]]:
        raise NotImplementedError("HU-3.1: YOLO11 detect + ByteTrack")
