"""Assign ball to nearest player under a distance threshold (HU-5.1)."""

from __future__ import annotations

from typing import Any, Dict


class PlayerBallAssigner:
    def __init__(self, max_distance: float = 70.0) -> None:
        self.max_distance = max_distance

    def assign_ball_to_player(self, players: Dict[int, Any], ball_bbox) -> int:
        raise NotImplementedError("HU-5.1")
