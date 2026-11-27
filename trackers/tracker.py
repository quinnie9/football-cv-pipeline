"""YOLO11 detection + ByteTrack association (via Ultralytics tracker)."""

from __future__ import annotations

import pickle
from pathlib import Path
from typing import Any, Dict, List, Optional

import cv2
import numpy as np
from ultralytics import YOLO

from utils.bbox import get_bbox_width, get_center_of_bbox, get_foot_position


class Tracker:
    """Detect football objects and keep temporal IDs with ByteTrack.

    Notes
    -----
    - Goalkeepers are mapped to ``player`` for tracking continuity (jersey
      clustering can still use appearance later).
    - The ball is stored with a fixed key ``1`` (not ByteTrack), matching the
      classic football-analysis pipeline convention.
    """

    def __init__(
        self,
        model_path: str,
        conf: float = 0.2,
        device: Optional[str] = None,
        tracker_cfg: str = "bytetrack.yaml",
        ball_conf: float = 0.02,
        ball_imgsz: int = 1280,
        ball_min_side: float = 6.0,
        ball_max_side: float = 60.0,
        detect_ball: bool = True,
    ) -> None:
        self.model = YOLO(model_path)
        self.conf = conf
        self.device = device
        self.tracker_cfg = tracker_cfg
        # Dedicated ball pass: tiny object → lower conf + larger imgsz
        self.ball_conf = ball_conf
        self.ball_imgsz = ball_imgsz
        self.ball_min_side = ball_min_side
        self.ball_max_side = ball_max_side
        self.detect_ball = detect_ball
        self._ball_class_id = next(
            (i for i, n in self.model.names.items() if n == "ball"), 0
        )

    def add_position_to_tracks(self, tracks: Dict[str, List[Dict]]) -> None:
        for object_name, object_tracks in tracks.items():
            for frame_num, track in enumerate(object_tracks):
                for track_id, track_info in track.items():
                    bbox = track_info["bbox"]
                    if object_name == "ball":
                        position = get_center_of_bbox(bbox)
                    else:
                        position = get_foot_position(bbox)
                    tracks[object_name][frame_num][track_id]["position"] = position

    def _plausible_ball(self, bbox: np.ndarray) -> bool:
        w = float(bbox[2] - bbox[0])
        h = float(bbox[3] - bbox[1])
        return (
            self.ball_min_side <= w <= self.ball_max_side
            and self.ball_min_side <= h <= self.ball_max_side
        )

    def _detect_ball(self, frame: np.ndarray) -> Dict[int, Dict[str, Any]]:
        """High-res / low-conf ball-only pass; keep highest-confidence plausible box."""
        result = self.model.predict(
            frame,
            conf=self.ball_conf,
            imgsz=self.ball_imgsz,
            classes=[self._ball_class_id],
            verbose=False,
            device=self.device,
        )[0]
        ball: Dict[int, Dict[str, Any]] = {}
        boxes = result.boxes
        if boxes is None or len(boxes) == 0:
            return ball

        xyxy = boxes.xyxy.cpu().numpy()
        confs = boxes.conf.cpu().numpy()
        best_i = None
        best_conf = -1.0
        for i, (bbox, conf) in enumerate(zip(xyxy, confs)):
            if not self._plausible_ball(bbox):
                continue
            if float(conf) > best_conf:
                best_conf = float(conf)
                best_i = i
        if best_i is not None:
            ball[1] = {
                "bbox": xyxy[best_i].tolist(),
                "cls": "ball",
                "conf": best_conf,
            }
        return ball

    def get_object_tracks(
        self,
        frames: List[np.ndarray],
        read_from_stub: bool = False,
        stub_path: Optional[str] = None,
    ) -> Dict[str, List[Dict]]:
        if read_from_stub and stub_path and Path(stub_path).exists():
            with open(stub_path, "rb") as f:
                return pickle.load(f)

        tracks: Dict[str, List[Dict]] = {
            "players": [],
            "referees": [],
            "ball": [],
        }

        # Reset tracker state for a fresh clip
        self.model.predictor = None

        for frame in frames:
            result = self.model.track(
                frame,
                conf=self.conf,
                persist=True,
                tracker=self.tracker_cfg,
                verbose=False,
                device=self.device,
            )[0]

            names = result.names  # id -> name

            players: Dict[int, Dict[str, Any]] = {}
            referees: Dict[int, Dict[str, Any]] = {}

            boxes = result.boxes
            if boxes is not None and len(boxes) > 0:
                xyxy = boxes.xyxy.cpu().numpy()
                cls_ids = boxes.cls.cpu().numpy().astype(int)
                if boxes.id is not None:
                    track_ids = boxes.id.cpu().numpy().astype(int)
                else:
                    track_ids = np.array([-1] * len(xyxy))

                for bbox, cls_id, tid in zip(xyxy, cls_ids, track_ids):
                    cls_name = names.get(int(cls_id), "")
                    # Unify goalkeeper with player for ID continuity
                    if cls_name == "goalkeeper":
                        cls_name = "player"

                    bbox_list = bbox.tolist()
                    if cls_name == "player" and tid >= 0:
                        players[int(tid)] = {"bbox": bbox_list, "cls": "player"}
                    elif cls_name == "referee" and tid >= 0:
                        referees[int(tid)] = {"bbox": bbox_list, "cls": "referee"}

            # Ball: dedicated pass (ByteTrack + default conf misses tiny balls)
            ball = self._detect_ball(frame) if self.detect_ball else {}

            tracks["players"].append(players)
            tracks["referees"].append(referees)
            tracks["ball"].append(ball)

        if stub_path is not None:
            Path(stub_path).parent.mkdir(parents=True, exist_ok=True)
            with open(stub_path, "wb") as f:
                pickle.dump(tracks, f)

        return tracks

    def draw_ellipse(
        self,
        frame: np.ndarray,
        bbox: List[float],
        color: tuple,
        track_id: Optional[int] = None,
        label: Optional[str] = None,
    ) -> np.ndarray:
        y2 = int(bbox[3])
        x_center, _ = get_center_of_bbox(bbox)
        width = get_bbox_width(bbox)
        cv2.ellipse(
            frame,
            center=(x_center, y2),
            axes=(int(width), int(0.35 * width)),
            angle=0.0,
            startAngle=-45,
            endAngle=235,
            color=color,
            thickness=2,
            lineType=cv2.LINE_4,
        )
        text = label if label is not None else (str(track_id) if track_id is not None else None)
        if text is not None:
            font = cv2.FONT_HERSHEY_SIMPLEX
            scale = 0.45 if len(text) > 4 else 0.55
            (tw, th), _ = cv2.getTextSize(text, font, scale, 2)
            pad_x, pad_y = 6, 4
            rect_w, rect_h = tw + 2 * pad_x, th + 2 * pad_y
            x1_rect = x_center - rect_w // 2
            x2_rect = x1_rect + rect_w
            y1_rect = y2 + 8
            y2_rect = y1_rect + rect_h
            cv2.rectangle(
                frame,
                (int(x1_rect), int(y1_rect)),
                (int(x2_rect), int(y2_rect)),
                color,
                cv2.FILLED,
            )
            cv2.putText(
                frame,
                text,
                (int(x1_rect + pad_x), int(y2_rect - pad_y)),
                font,
                scale,
                (0, 0, 0),
                2,
            )
        return frame

    def draw_triangle(self, frame: np.ndarray, bbox: List[float], color: tuple) -> np.ndarray:
        y = int(bbox[1])
        x, _ = get_center_of_bbox(bbox)
        pts = np.array([[x, y], [x - 10, y - 20], [x + 10, y - 20]])
        cv2.drawContours(frame, [pts], 0, color, cv2.FILLED)
        cv2.drawContours(frame, [pts], 0, (0, 0, 0), 2)
        return frame

    def draw_team_ball_control(
        self,
        frame: np.ndarray,
        frame_num: int,
        team_ball_control: np.ndarray,
    ) -> np.ndarray:
        """Overlay cumulative possession % up to the current frame."""
        overlay = frame.copy()
        h, w = frame.shape[:2]
        x1, y1 = int(w * 0.70), int(h * 0.85)
        x2, y2 = int(w * 0.98), int(h * 0.97)
        cv2.rectangle(overlay, (x1, y1), (x2, y2), (255, 255, 255), -1)
        cv2.addWeighted(overlay, 0.4, frame, 0.6, 0, frame)

        until = team_ball_control[: frame_num + 1]
        # Ignore "unassigned" zeros when computing percentages if present
        valid = until[until > 0]
        if len(valid) == 0:
            t1 = t2 = 0.0
        else:
            t1 = float(np.sum(valid == 1) / len(valid))
            t2 = float(np.sum(valid == 2) / len(valid))

        cv2.putText(
            frame,
            f"Team 1 Ball Control: {t1 * 100:.1f}%",
            (x1 + 10, y1 + 35),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (0, 0, 0),
            2,
        )
        cv2.putText(
            frame,
            f"Team 2 Ball Control: {t2 * 100:.1f}%",
            (x1 + 10, y1 + 70),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (0, 0, 0),
            2,
        )
        return frame

    def draw_annotations(
        self,
        video_frames: List[np.ndarray],
        tracks: Dict[str, List[Dict]],
        team_ball_control: Optional[np.ndarray] = None,
    ) -> List[np.ndarray]:
        output: List[np.ndarray] = []
        n = len(video_frames)
        for frame_num in range(n):
            frame = video_frames[frame_num].copy()
            for track_id, player in tracks["players"][frame_num].items():
                color = tuple(player.get("team_color", (0, 255, 0)))
                label = player.get("label")
                frame = self.draw_ellipse(
                    frame, player["bbox"], color, track_id, label=label
                )
                if player.get("has_ball", False):
                    frame = self.draw_triangle(frame, player["bbox"], (0, 0, 255))
            for track_id, referee in tracks["referees"][frame_num].items():
                frame = self.draw_ellipse(frame, referee["bbox"], (0, 255, 255), track_id)
            for _, ball in tracks["ball"][frame_num].items():
                frame = self.draw_triangle(frame, ball["bbox"], (0, 255, 0))
            if team_ball_control is not None:
                frame = self.draw_team_ball_control(frame, frame_num, team_ball_control)
            output.append(frame)
        return output
