"""Estimate camera pan between frames via Lucas–Kanade optical flow (HU-6.1)."""

from __future__ import annotations

import pickle
from pathlib import Path
from typing import Dict, List, Optional, Sequence

import cv2
import numpy as np

from utils.bbox import measure_distance, measure_xy_distance


class CameraMovementEstimator:
    def __init__(self, frame: np.ndarray, minimum_distance: float = 5.0) -> None:
        self.minimum_distance = minimum_distance
        self.lk_params = dict(
            winSize=(15, 15),
            maxLevel=2,
            criteria=(cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 0.03),
        )

        first_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        mask_features = np.zeros_like(first_gray)
        # Prefer relatively static side strips (tutorial calibration for 1920-wide)
        mask_features[:, 0:20] = 1
        mask_features[:, 900:1050] = 1

        self.features = dict(
            maxCorners=100,
            qualityLevel=0.3,
            minDistance=3,
            blockSize=7,
            mask=mask_features,
        )

    def add_adjust_positions_to_tracks(
        self,
        tracks: Dict[str, List[Dict]],
        camera_movement_per_frame: Sequence[Sequence[float]],
    ) -> None:
        for object_name, object_tracks in tracks.items():
            for frame_num, track in enumerate(object_tracks):
                for track_id, track_info in track.items():
                    position = track_info.get("position")
                    if position is None:
                        continue
                    cam = camera_movement_per_frame[frame_num]
                    tracks[object_name][frame_num][track_id]["position_adjusted"] = (
                        position[0] - cam[0],
                        position[1] - cam[1],
                    )

    def get_camera_movement(
        self,
        frames: List[np.ndarray],
        read_from_stub: bool = False,
        stub_path: Optional[str] = None,
    ) -> List[List[float]]:
        if read_from_stub and stub_path and Path(stub_path).exists():
            with open(stub_path, "rb") as f:
                return pickle.load(f)

        camera_movement: List[List[float]] = [[0.0, 0.0] for _ in frames]
        old_gray = cv2.cvtColor(frames[0], cv2.COLOR_BGR2GRAY)
        old_features = cv2.goodFeaturesToTrack(old_gray, **self.features)

        for frame_num in range(1, len(frames)):
            frame_gray = cv2.cvtColor(frames[frame_num], cv2.COLOR_BGR2GRAY)
            if old_features is None or len(old_features) == 0:
                old_features = cv2.goodFeaturesToTrack(frame_gray, **self.features)
                old_gray = frame_gray.copy()
                continue

            new_features, status, _ = cv2.calcOpticalFlowPyrLK(
                old_gray, frame_gray, old_features, None, **self.lk_params
            )
            if new_features is None or status is None:
                old_gray = frame_gray.copy()
                old_features = cv2.goodFeaturesToTrack(frame_gray, **self.features)
                continue

            max_distance = 0.0
            camera_movement_x, camera_movement_y = 0.0, 0.0
            for new, old, st in zip(new_features, old_features, status):
                if st[0] == 0:
                    continue
                new_pt = new.ravel()
                old_pt = old.ravel()
                distance = measure_distance(new_pt, old_pt)
                if distance > max_distance:
                    max_distance = distance
                    camera_movement_x, camera_movement_y = measure_xy_distance(
                        old_pt, new_pt
                    )

            if max_distance > self.minimum_distance:
                camera_movement[frame_num] = [camera_movement_x, camera_movement_y]
                old_features = cv2.goodFeaturesToTrack(frame_gray, **self.features)

            old_gray = frame_gray.copy()

        if stub_path is not None:
            Path(stub_path).parent.mkdir(parents=True, exist_ok=True)
            with open(stub_path, "wb") as f:
                pickle.dump(camera_movement, f)

        return camera_movement

    def draw_camera_movement(
        self,
        frames: List[np.ndarray],
        camera_movement_per_frame: Sequence[Sequence[float]],
    ) -> List[np.ndarray]:
        output_frames = []
        for frame_num, frame in enumerate(frames):
            frame = frame.copy()
            overlay = frame.copy()
            cv2.rectangle(overlay, (0, 0), (520, 100), (255, 255, 255), -1)
            cv2.addWeighted(overlay, 0.6, frame, 0.4, 0, frame)
            x_movement, y_movement = camera_movement_per_frame[frame_num]
            cv2.putText(
                frame,
                f"Camera Movement X: {x_movement:.2f}",
                (10, 35),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.9,
                (0, 0, 0),
                2,
            )
            cv2.putText(
                frame,
                f"Camera Movement Y: {y_movement:.2f}",
                (10, 75),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.9,
                (0, 0, 0),
                2,
            )
            output_frames.append(frame)
        return output_frames
