#!/usr/bin/env python3
"""HU-5.1 — Team possession heuristic overlay on annotated video."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from player_ball_assigner import PlayerBallAssigner
from team_assigner import TeamAssigner
from trackers import Tracker
from utils import get_video_meta, read_video, save_video


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--video", default="input_videos/sample.mp4")
    parser.add_argument("--model", default="models/best_yolov11n.pt")
    parser.add_argument("--output", default="output_videos/possession_sample.mp4")
    parser.add_argument("--stub", default="stubs/track_stubs.pkl")
    parser.add_argument("--conf", type=float, default=0.2)
    parser.add_argument("--device", default="mps")
    parser.add_argument("--max-distance", type=float, default=70.0)
    parser.add_argument("--seed-frame", type=int, default=0)
    args = parser.parse_args()

    video = ROOT / args.video
    model = ROOT / args.model
    output = ROOT / args.output
    stub = ROOT / args.stub

    fps, w, h, _ = get_video_meta(str(video))
    print(f"video={video.name} {w}x{h} @ {fps:.2f} fps")

    frames = read_video(str(video))
    tracker = Tracker(str(model), conf=args.conf, device=args.device)
    tracks = tracker.get_object_tracks(
        frames,
        read_from_stub=stub.exists(),
        stub_path=str(stub),
    )
    tracker.add_position_to_tracks(tracks)

    seed = args.seed_frame
    if not tracks["players"][seed]:
        seed = next((i for i, t in enumerate(tracks["players"]) if t), 0)

    team_assigner = TeamAssigner()
    team_assigner.assign_team_color(frames[seed], tracks["players"][seed])
    for frame_num, player_track in enumerate(tracks["players"]):
        for player_id, track in player_track.items():
            team = team_assigner.get_player_team(
                frames[frame_num], track["bbox"], player_id
            )
            tracks["players"][frame_num][player_id]["team"] = team
            tracks["players"][frame_num][player_id]["team_color"] = (
                team_assigner.bgr_tuple(team)
            )

    assigner = PlayerBallAssigner(max_distance=args.max_distance)
    team_ball_control: list[int] = []
    assigned_frames = 0
    ball_visible = 0

    # Possession labels per frame:
    #   0 = unknown (no ball / ball too far)
    #   1/2 = team with ball this frame
    # We do NOT sticky-fill unknowns: with low ball recall, sticky would
    # dominate the whole clip after the first assignment (misleading %).
    for frame_num, player_track in enumerate(tracks["players"]):
        ball = tracks["ball"][frame_num]
        if not ball:
            team_ball_control.append(0)
            continue

        ball_visible += 1
        ball_bbox = next(iter(ball.values()))["bbox"]
        pid = assigner.assign_ball_to_player(player_track, ball_bbox)
        if pid != -1:
            tracks["players"][frame_num][pid]["has_ball"] = True
            team = int(tracks["players"][frame_num][pid].get("team", 0))
            team_ball_control.append(team)
            assigned_frames += 1
        else:
            team_ball_control.append(0)

    control = np.array(team_ball_control, dtype=int)
    valid = control[control > 0]
    if len(valid):
        t1 = 100.0 * float(np.mean(valid == 1))
        t2 = 100.0 * float(np.mean(valid == 2))
    else:
        t1 = t2 = 0.0

    print(f"ball_visible_frames={ball_visible}/{len(frames)}")
    print(f"possession_assigned_frames={assigned_frames}/{len(frames)}")
    print(f"team1_control={t1:.1f}% team2_control={t2:.1f}% (only assigned frames)")
    print(
        "NOTE: heuristic + low ball recall — exploratory only, not official possession."
    )
    annotated = tracker.draw_annotations(frames, tracks, team_ball_control=control)
    save_video(annotated, str(output), fps=fps)
    print("OK", output)


if __name__ == "__main__":
    main()
