"""Kinematics on metric trajectories (HU-8.1)."""

from __future__ import annotations


class SpeedAndDistanceEstimator:
    def __init__(self, fps: float = 25.0) -> None:
        self.fps = fps

    def add_speed_and_distance_to_tracks(self, tracks) -> None:
        raise NotImplementedError("HU-8.1")
