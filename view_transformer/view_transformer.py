"""Image-to-field homography (HU-7)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Union

import cv2
import numpy as np


class ViewTransformer:
    """Perspective transform from image pixels to a metric pitch patch.

    Default vertices match the tutorial calibration for ``08fd33_4.mp4``.
    Pass ``config_path`` or explicit vertices for other cameras/clips.
    """

    def __init__(
        self,
        config_path: Optional[Union[str, Path]] = None,
        pixel_vertices: Optional[Sequence[Sequence[float]]] = None,
        court_length_m: float = 23.32,
        court_width_m: float = 68.0,
    ) -> None:
        if config_path is not None:
            cfg = json.loads(Path(config_path).read_text())
            pixel_vertices = cfg["pixel_vertices"]
            court_length_m = float(cfg.get("court_length_m", court_length_m))
            court_width_m = float(cfg.get("court_width_m", court_width_m))

        if pixel_vertices is None:
            # Tutorial 08fd33_4 defaults
            pixel_vertices = [
                [110, 1035],
                [265, 275],
                [910, 260],
                [1640, 915],
            ]
            court_length_m = 23.32
            court_width_m = 68.0

        self.pixel_vertices = np.array(pixel_vertices, dtype=np.float32)
        self.target_vertices = np.array(
            [
                [0, court_width_m],
                [0, 0],
                [court_length_m, 0],
                [court_length_m, court_width_m],
            ],
            dtype=np.float32,
        )
        self.perspective_transformer = cv2.getPerspectiveTransform(
            self.pixel_vertices, self.target_vertices
        )

    def transform_point(self, point: np.ndarray) -> Optional[np.ndarray]:
        p = (int(point[0]), int(point[1]))
        if cv2.pointPolygonTest(self.pixel_vertices, p, False) < 0:
            return None
        reshaped = point.reshape(-1, 1, 2).astype(np.float32)
        transformed = cv2.perspectiveTransform(reshaped, self.perspective_transformer)
        return transformed.reshape(-1, 2)

    def add_transformed_position_to_tracks(self, tracks: Dict[str, List[Dict]]) -> None:
        for object_name, object_tracks in tracks.items():
            for frame_num, track in enumerate(object_tracks):
                for track_id, track_info in track.items():
                    position = track_info.get(
                        "position_adjusted", track_info.get("position")
                    )
                    if position is None:
                        continue
                    position_arr = np.array(position, dtype=np.float32)
                    transformed = self.transform_point(position_arr)
                    if transformed is not None:
                        tracks[object_name][frame_num][track_id][
                            "position_transformed"
                        ] = transformed.squeeze().tolist()
