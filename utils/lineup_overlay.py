"""Draw starting-XI roster HUD from lineup JSON (not linked to track IDs)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

import cv2
import numpy as np


def load_lineups(path: str | Path) -> Dict[str, Any]:
    return json.loads(Path(path).read_text())


def draw_lineups(
    frames: List[np.ndarray],
    lineups: Dict[str, Any],
    team_order: Optional[List[str]] = None,
) -> List[np.ndarray]:
    """Overlay starting XIs. Explicitly labels that IDs ≠ jersey mapping."""
    teams = team_order or [k for k in lineups.keys() if k != "formation"]
    formation = lineups.get("formation", {})
    out: List[np.ndarray] = []

    for frame in frames:
        img = frame.copy()
        h, w = img.shape[:2]
        panel_w = int(w * 0.22)
        overlay = img.copy()
        cv2.rectangle(overlay, (8, 8), (8 + panel_w, h - 8), (20, 20, 20), -1)
        cv2.addWeighted(overlay, 0.55, img, 0.45, 0, img)

        y = 36
        cv2.putText(
            img,
            "LINEUPS (roster only)",
            (18, y),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.55,
            (255, 255, 255),
            2,
        )
        y += 22
        cv2.putText(
            img,
            "Not linked to track IDs",
            (18, y),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.45,
            (180, 180, 255),
            1,
        )
        y += 28

        for team in teams[:2]:
            blob = lineups.get(team, {})
            starters = blob.get("starting", [])
            form = formation.get(team, "")
            cv2.putText(
                img,
                f"{team} {form}".strip(),
                (18, y),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.55,
                (0, 220, 255),
                2,
            )
            y += 22
            for p in starters:
                num = str(p.get("number", "?"))
                name = str(p.get("name", ""))
                # shorten long names
                if len(name) > 18:
                    name = name[:16] + "…"
                cv2.putText(
                    img,
                    f"{num:>2}  {name}",
                    (18, y),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.42,
                    (230, 230, 230),
                    1,
                )
                y += 18
            y += 12

        out.append(img)
    return out
