#!/usr/bin/env python3
"""HU-4.1 — Assign teams by jersey color and export annotated video."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from team_assigner import TeamAssigner
from trackers import Tracker
from utils import get_video_meta, read_video, save_video


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--video", default="input_videos/sample.mp4")
    parser.add_argument("--model", default="models/best_yolov11n.pt")
    parser.add_argument("--output", default="output_videos/teams_sample.mp4")
    parser.add_argument("--stub", default="stubs/track_stubs.pkl")
    parser.add_argument("--conf", type=float, default=0.2)
    parser.add_argument("--device", default="mps")
    parser.add_argument(
        "--seed-frame",
        type=int,
        default=0,
        help="Frame index used to fit the two team color centroids",
    )
    args = parser.parse_args()

    video = ROOT / args.video
    model = ROOT / args.model
    output = ROOT / args.output
    stub = ROOT / args.stub

    fps, w, h, _ = get_video_meta(str(video))
    print(f"video={video.name} {w}x{h} @ {fps:.2f} fps")

    print("Loading frames...")
    frames = read_video(str(video))

    tracker = Tracker(str(model), conf=args.conf, device=args.device)
    print("Tracking (reuse stub if present)...")
    tracks = tracker.get_object_tracks(
        frames,
        read_from_stub=stub.exists(),
        stub_path=str(stub),
    )
    tracker.add_position_to_tracks(tracks)

    # Find a seed frame that actually has players
    seed = args.seed_frame
    if not tracks["players"][seed]:
        seed = next((i for i, t in enumerate(tracks["players"]) if t), 0)
    print(f"Fitting team colors on frame {seed} ({len(tracks['players'][seed])} players)")

    team_assigner = TeamAssigner()
    team_assigner.assign_team_color(frames[seed], tracks["players"][seed])
    print("team_1_bgr", team_assigner.bgr_tuple(1))
    print("team_2_bgr", team_assigner.bgr_tuple(2))

    for frame_num, player_track in enumerate(tracks["players"]):
        for player_id, track in player_track.items():
            team = team_assigner.get_player_team(
                frames[frame_num], track["bbox"], player_id
            )
            tracks["players"][frame_num][player_id]["team"] = team
            tracks["players"][frame_num][player_id]["team_color"] = team_assigner.bgr_tuple(
                team
            )

    # Counts of sticky assignments
    from collections import Counter

    counts = Counter(team_assigner.player_team_dict.values())
    print("assigned_tracks_by_team", dict(counts))

    print("Drawing...")
    annotated = tracker.draw_annotations(frames, tracks)
    save_video(annotated, str(output), fps=fps)
    print("OK", output)


if __name__ == "__main__":
    main()
