"""Resolve display labels from optional track_id → lineup mapping."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Optional


def load_track_map(path: str | Path) -> Dict[str, Any]:
    return json.loads(Path(path).read_text())


def label_for_track(
    track_id: int,
    team: Optional[int],
    track_map: Optional[Dict[str, Any]],
    *,
    prefer_name: bool = True,
) -> str:
    """Return overlay text: ``#26 Molina`` if mapped, else ``ARG`` / ``FRA`` / ``#id``."""
    if track_map:
        players = track_map.get("players", {})
        entry = players.get(str(track_id))
        if entry:
            num = entry.get("number", "")
            name = entry.get("name", "")
            short = name.split()[-1] if name else ""
            if prefer_name and short:
                return f"#{num} {short}" if num else short
            if num:
                return f"#{num}"
        if team is not None:
            abbr = track_map.get("team_abbr", {}).get(str(team))
            if abbr:
                return abbr
    if team is not None:
        return f"T{team}"
    return str(track_id)
