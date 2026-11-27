"""Assign ball to nearest player under a distance threshold (possession heuristic)."""

from __future__ import annotations

from typing import Any, Dict, Sequence

from utils.bbox import get_center_of_bbox, measure_distance


class PlayerBallAssigner:
    """Approximate possession: nearest player feet to ball center, within max_distance.

    This is NOT official possession. Missing ball detections ⇒ no new assignment.
    """

    def __init__(self, max_distance: float = 70.0) -> None:
        self.max_distance = max_distance

    def assign_ball_to_player(self, players: Dict[int, Any], ball_bbox: Sequence[float]) -> int:
        ball_position = get_center_of_bbox(ball_bbox)
        minimum_distance = float("inf")
        assigned_player = -1

        for player_id, player in players.items():
            player_bbox = player["bbox"]
            # Distance from ball to each bottom corner of the player box (feet approx)
            distance_left = measure_distance(
                (player_bbox[0], player_bbox[3]), ball_position
            )
            distance_right = measure_distance(
                (player_bbox[2], player_bbox[3]), ball_position
            )
            distance = min(distance_left, distance_right)

            if distance < self.max_distance and distance < minimum_distance:
                minimum_distance = distance
                assigned_player = int(player_id)

        return assigned_player
