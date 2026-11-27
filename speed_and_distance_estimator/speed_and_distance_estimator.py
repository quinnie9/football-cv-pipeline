"""Per-player speed (km/h) and distance (m) on transformed coordinates (HU-8.1)."""

from __future__ import annotations

from typing import Dict, List, Optional, Tuple

import cv2
import numpy as np

from utils.bbox import get_foot_position, measure_distance


class SpeedAndDistanceEstimator:
    """Metric speed/distance with sanity clamps for readable overlays.

    Football sprint ceiling ~36 km/h; values above ``max_speed_kmh`` are treated
    as geometry/ID noise and dropped from the overlay.
    """

    def __init__(
        self,
        frame_rate: float = 25.0,
        frame_window: int = 15,
        max_speed_kmh: float = 36.0,
        min_speed_kmh: float = 1.0,
    ) -> None:
        self.frame_rate = frame_rate
        self.frame_window = frame_window
        self.max_speed_kmh = max_speed_kmh
        self.min_speed_kmh = min_speed_kmh

    def add_speed_and_distance_to_tracks(self, tracks: Dict[str, List[Dict]]) -> None:
        total_distance: Dict[str, Dict[int, float]] = {}

        for object_name, object_tracks in tracks.items():
            if object_name in {"ball", "referees"}:
                continue
            n_frames = len(object_tracks)
            for frame_num in range(0, n_frames, self.frame_window):
                last_frame = min(frame_num + self.frame_window, n_frames - 1)
                for track_id, _ in object_tracks[frame_num].items():
                    if track_id not in object_tracks[last_frame]:
                        continue
                    start = object_tracks[frame_num][track_id].get("position_transformed")
                    end = object_tracks[last_frame][track_id].get("position_transformed")
                    if start is None or end is None:
                        continue

                    distance_covered = measure_distance(start, end)
                    dt = (last_frame - frame_num) / self.frame_rate
                    if dt <= 0:
                        continue
                    speed_kmh = (distance_covered / dt) * 3.6

                    # Reject non-physical spikes (homography / ID switch)
                    if speed_kmh > self.max_speed_kmh:
                        continue

                    total_distance.setdefault(object_name, {})
                    total_distance[object_name].setdefault(track_id, 0.0)
                    total_distance[object_name][track_id] += distance_covered

                    for batch_frame in range(frame_num, last_frame + 1):
                        if track_id not in tracks[object_name][batch_frame]:
                            continue
                        tracks[object_name][batch_frame][track_id]["speed"] = speed_kmh
                        tracks[object_name][batch_frame][track_id]["distance"] = (
                            total_distance[object_name][track_id]
                        )

    def _put_label(self, frame: np.ndarray, text: str, org: Tuple[int, int]) -> None:
        cv2.putText(
            frame, text, org, cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 0, 0), 3, cv2.LINE_AA
        )
        cv2.putText(
            frame, text, org, cv2.FONT_HERSHEY_SIMPLEX, 0.45, (255, 255, 255), 1, cv2.LINE_AA
        )

    def draw_speed_and_distance(
        self,
        frames: List[np.ndarray],
        tracks: Dict[str, List[Dict]],
        min_distance_m: float = 0.5,
    ) -> List[np.ndarray]:
        """One compact label per player; hide idle / invalid readings."""
        output_frames = []
        for frame_num, frame in enumerate(frames):
            frame = frame.copy()
            for object_name, object_tracks in tracks.items():
                if object_name in {"ball", "referees"}:
                    continue
                for _, track_info in object_tracks[frame_num].items():
                    speed = track_info.get("speed")
                    distance = track_info.get("distance")
                    if speed is None or distance is None:
                        continue
                    if distance < min_distance_m:
                        continue
                    if speed < self.min_speed_kmh or speed > self.max_speed_kmh:
                        continue
                    position = list(get_foot_position(track_info["bbox"]))
                    position[1] += 28
                    pos = (int(position[0]) - 20, int(position[1]))
                    self._put_label(frame, f"{speed:.0f} km/h  {distance:.0f} m", pos)
            output_frames.append(frame)
        return output_frames
