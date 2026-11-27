"""Assign players to two teams via jersey color clustering (K-Means)."""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Sequence, Tuple

import numpy as np
from sklearn.cluster import KMeans


class TeamAssigner:
    """Estimate two team colors from player crops, then assign each track.

    Pipeline
    --------
    1. Crop player bbox, take upper half (torso/jersey).
    2. KMeans(2) on pixels → separate jersey vs background/grass.
    3. Jersey cluster ≈ the one that is *not* dominant in the four corners.
    4. Collect jersey colors across players → KMeans(2) → team 1 / team 2.
    5. Assign each track ID to nearest team centroid (sticky per ID).
    """

    def __init__(self) -> None:
        self.team_colors: Dict[int, np.ndarray] = {}
        self.player_team_dict: Dict[int, int] = {}
        self.kmeans: Optional[KMeans] = None

    def get_clustering_model(self, image: np.ndarray) -> KMeans:
        image_2d = image.reshape(-1, 3)
        kmeans = KMeans(n_clusters=2, init="k-means++", n_init=10, random_state=42)
        kmeans.fit(image_2d)
        return kmeans

    def get_player_color(self, frame: np.ndarray, bbox: Sequence[float]) -> np.ndarray:
        x1, y1, x2, y2 = map(int, bbox)
        h, w = frame.shape[:2]
        x1, y1 = max(0, x1), max(0, y1)
        x2, y2 = min(w, x2), min(h, y2)
        if x2 <= x1 or y2 <= y1:
            return np.array([0.0, 0.0, 0.0])

        image = frame[y1:y2, x1:x2]
        if image.size == 0:
            return np.array([0.0, 0.0, 0.0])

        top_half = image[: max(1, image.shape[0] // 2), :]
        if top_half.size < 6:
            return top_half.reshape(-1, 3).mean(axis=0)

        kmeans = self.get_clustering_model(top_half)
        labels = kmeans.labels_.reshape(top_half.shape[0], top_half.shape[1])

        # Corners are often grass/background → that cluster is "non-player"
        corner_clusters = [
            labels[0, 0],
            labels[0, -1],
            labels[-1, 0],
            labels[-1, -1],
        ]
        non_player_cluster = max(set(corner_clusters), key=corner_clusters.count)
        player_cluster = 1 - non_player_cluster
        return kmeans.cluster_centers_[player_cluster]

    def assign_team_color(self, frame: np.ndarray, player_detections: Dict[int, Any]) -> None:
        player_colors: List[np.ndarray] = []
        for _, det in player_detections.items():
            color = self.get_player_color(frame, det["bbox"])
            player_colors.append(color)

        if len(player_colors) < 2:
            # Degenerate: invent two placeholders
            self.team_colors = {
                1: np.array([255.0, 255.0, 255.0]),
                2: np.array([0.0, 0.0, 255.0]),
            }
            self.kmeans = None
            return

        kmeans = KMeans(n_clusters=2, init="k-means++", n_init=10, random_state=42)
        kmeans.fit(np.asarray(player_colors))
        self.kmeans = kmeans
        self.team_colors[1] = kmeans.cluster_centers_[0]
        self.team_colors[2] = kmeans.cluster_centers_[1]

    def get_player_team(
        self,
        frame: np.ndarray,
        player_bbox: Sequence[float],
        player_id: int,
    ) -> int:
        if player_id in self.player_team_dict:
            return self.player_team_dict[player_id]

        if self.kmeans is None:
            team_id = 1
        else:
            player_color = self.get_player_color(frame, player_bbox)
            team_id = int(self.kmeans.predict(player_color.reshape(1, -1))[0]) + 1

        self.player_team_dict[player_id] = team_id
        return team_id

    def bgr_tuple(self, team_id: int) -> Tuple[int, int, int]:
        """Team centroid is in BGR (OpenCV frame space)."""
        c = self.team_colors.get(team_id)
        if c is None:
            return (0, 255, 0)
        return (int(c[0]), int(c[1]), int(c[2]))
