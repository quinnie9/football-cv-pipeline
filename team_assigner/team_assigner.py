"""Assign players to two teams via jersey color clustering (HU-4.1)."""

from __future__ import annotations

from typing import Any, Dict


class TeamAssigner:
    def __init__(self) -> None:
        self.team_colors: Dict[int, Any] = {}

    def assign_team_color(self, frame, player_detections) -> None:
        raise NotImplementedError("HU-4.1")

    def get_player_team(self, frame, bbox, player_id: int) -> int:
        raise NotImplementedError("HU-4.1")
