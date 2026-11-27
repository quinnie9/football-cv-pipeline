#!/usr/bin/env python3
"""HU-3.1 — Run YOLO11 + ByteTrack on a clip and export annotated video."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from trackers import Tracker
from utils import get_video_meta, read_video, save_video


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--video", default="input_videos/sample.mp4")
    parser.add_argument("--model", default="models/best_yolov11n.pt")
    parser.add_argument("--output", default="output_videos/tracked_sample.mp4")
    parser.add_argument("--stub", default="stubs/track_stubs.pkl")
    parser.add_argument("--conf", type=float, default=0.2)
    parser.add_argument("--device", default="mps")
    parser.add_argument("--read-stub", action="store_true")
    args = parser.parse_args()

    video = ROOT / args.video
    model = ROOT / args.model
    output = ROOT / args.output
    stub = ROOT / args.stub

    if not video.exists():
        raise SystemExit(f"Missing video: {video}")
    if not model.exists():
        raise SystemExit(f"Missing model: {model}")

    fps, w, h, n = get_video_meta(str(video))
    print(f"video={video.name} {w}x{h} @ {fps:.2f} fps frames≈{n}")

    print("Loading frames...")
    frames = read_video(str(video))
    print(f"loaded {len(frames)} frames")

    tracker = Tracker(str(model), conf=args.conf, device=args.device)
    print("Tracking (ByteTrack)...")
    tracks = tracker.get_object_tracks(
        frames,
        read_from_stub=args.read_stub,
        stub_path=str(stub),
    )
    tracker.add_position_to_tracks(tracks)

    # Quick stats
    ids = set()
    for frame_tracks in tracks["players"]:
        ids.update(frame_tracks.keys())
    ball_frames = sum(1 for b in tracks["ball"] if b)
    print(f"unique_player_ids={len(ids)} ball_frames={ball_frames}/{len(frames)}")

    print("Drawing annotations...")
    annotated = tracker.draw_annotations(frames, tracks)
    print(f"Writing {output} ...")
    save_video(annotated, str(output), fps=fps)
    print("OK", output)


if __name__ == "__main__":
    main()
