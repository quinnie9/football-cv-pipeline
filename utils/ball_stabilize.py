"""Temporal gating for ball detections (reject impossible frame-to-frame jumps)."""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple

import numpy as np


def _center(bbox: List[float]) -> np.ndarray:
    return np.array(
        [(bbox[0] + bbox[2]) * 0.5, (bbox[1] + bbox[3]) * 0.5], dtype=np.float32
    )


def _size(bbox: List[float]) -> np.ndarray:
    return np.array([bbox[2] - bbox[0], bbox[3] - bbox[1]], dtype=np.float32)


def jump_stats(ball_tracks: List[Dict]) -> Dict[str, float]:
    """Frame-to-frame center displacement stats for accepted ball boxes."""
    centers: List[np.ndarray] = []
    idxs: List[int] = []
    for i, fr in enumerate(ball_tracks):
        if not fr:
            continue
        bbox = next(iter(fr.values()))["bbox"]
        centers.append(_center(bbox))
        idxs.append(i)
    jumps = []
    for (i0, c0), (i1, c1) in zip(zip(idxs, centers), zip(idxs[1:], centers[1:])):
        if i1 - i0 == 1:
            jumps.append(float(np.linalg.norm(c1 - c0)))
    if not jumps:
        return {"n": 0, "median": 0.0, "p90": 0.0, "gt80": 0.0, "gt150": 0.0}
    arr = np.array(jumps, dtype=np.float32)
    return {
        "n": float(len(arr)),
        "median": float(np.median(arr)),
        "p90": float(np.percentile(arr, 90)),
        "gt80": float(np.mean(arr > 80)),
        "gt150": float(np.mean(arr > 150)),
    }


def stabilize_ball_tracks(
    ball_tracks: List[Dict],
    max_jump_px: float = 80.0,
    max_coast: int = 8,
    candidates_key: str = "_candidates",
) -> List[Dict]:
    """Keep a temporally consistent ball by gating large jumps.

    If a frame has only the usual ``{1: {bbox...}}`` entry, that single box is
    the candidate. Prefer detections near the predicted position; otherwise
    coast for ``max_coast`` frames, then drop until a new lock.
    """
    out: List[Dict] = [{} for _ in ball_tracks]
    pos: Optional[np.ndarray] = None
    vel = np.zeros(2, dtype=np.float32)
    size = np.array([12.0, 12.0], dtype=np.float32)
    coast = 0
    locked = False

    for i, fr in enumerate(ball_tracks):
        cands: List[Tuple[np.ndarray, np.ndarray, float, Dict[str, Any]]] = []
        if fr:
            for _tid, info in fr.items():
                if _tid == candidates_key:
                    continue
                bbox = info["bbox"]
                cands.append(
                    (
                        _center(bbox),
                        _size(bbox),
                        float(info.get("conf", 1.0)),
                        info,
                    )
                )

        chosen = None
        if cands:
            if not locked:
                # bootstrap: highest conf
                chosen = max(cands, key=lambda t: t[2])
            else:
                pred = pos + vel
                nearby = [
                    t for t in cands if float(np.linalg.norm(t[0] - pred)) <= max_jump_px
                ]
                if nearby:
                    # closest to prediction, break ties with conf
                    chosen = min(
                        nearby,
                        key=lambda t: (float(np.linalg.norm(t[0] - pred)), -t[2]),
                    )

        if chosen is not None:
            c, s, conf, info = chosen
            if locked and pos is not None:
                vel = 0.6 * vel + 0.4 * (c - pos)
            else:
                vel = np.zeros(2, dtype=np.float32)
            pos = c
            size = s
            coast = 0
            locked = True
            out[i] = {
                1: {
                    "bbox": [
                        float(c[0] - s[0] / 2),
                        float(c[1] - s[1] / 2),
                        float(c[0] + s[0] / 2),
                        float(c[1] + s[1] / 2),
                    ],
                    "cls": "ball",
                    "conf": conf,
                    "stabilized": True,
                }
            }
        elif locked and pos is not None and coast < max_coast:
            pos = pos + vel
            coast += 1
            out[i] = {
                1: {
                    "bbox": [
                        float(pos[0] - size[0] / 2),
                        float(pos[1] - size[1] / 2),
                        float(pos[0] + size[0] / 2),
                        float(pos[1] + size[1] / 2),
                    ],
                    "cls": "ball",
                    "conf": 0.0,
                    "coasted": True,
                }
            }
        else:
            # lost lock — wait for a fresh detection (no teleport)
            if coast >= max_coast:
                locked = False
                pos = None
                vel = np.zeros(2, dtype=np.float32)
            out[i] = {}

    return out
