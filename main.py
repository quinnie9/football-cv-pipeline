"""
Entrypoint for the football CV pipeline.

Modules are wired in later HUs; this file documents the intended order:
  video → YOLO11+ByteTrack → camera motion → homography → ball interpolate
  → speed/distance → teams → possession → draw → export
"""

from __future__ import annotations


def main() -> None:
    raise SystemExit(
        "Pipeline not wired yet. Complete HU-0.x → detection → tracking, "
        "then HU-9.1 will connect modules here."
    )


if __name__ == "__main__":
    main()
