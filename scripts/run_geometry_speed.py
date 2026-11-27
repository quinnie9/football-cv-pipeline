#!/usr/bin/env python3
"""HU-6/7/8 — Camera motion, homography, speed/distance on continuous clip."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from camera_movement_estimator import CameraMovementEstimator
from speed_and_distance_estimator import SpeedAndDistanceEstimator
from team_assigner import TeamAssigner
from trackers import Tracker
from utils import get_video_meta, read_video, save_video
from view_transformer import ViewTransformer


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--video", default="input_videos/sample.mp4")
    parser.add_argument("--model", default="models/best_yolov11n.pt")
    parser.add_argument("--output", default="output_videos/geometry_speed_sample.mp4")
    parser.add_argument("--stub", default="stubs/track_stubs.pkl")
    parser.add_argument("--camera-stub", default="stubs/camera_movement_stub.pkl")
    parser.add_argument("--conf", type=float, default=0.2)
    parser.add_argument("--device", default="mps")
    parser.add_argument("--seed-frame", type=int, default=0)
    args = parser.parse_args()

    video = ROOT / args.video
    fps, w, h, _ = get_video_meta(str(video))
    print(f"video={video.name} {w}x{h} @ {fps:.2f} fps")

    frames = read_video(str(video))
    tracker = Tracker(str(ROOT / args.model), conf=args.conf, device=args.device)
    tracks = tracker.get_object_tracks(
        frames,
        read_from_stub=(ROOT / args.stub).exists(),
        stub_path=str(ROOT / args.stub),
    )
    tracker.add_position_to_tracks(tracks)

    # Teams (for colored ellipses)
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

    print("Estimating camera movement...")
    cam = CameraMovementEstimator(frames[0])
    camera_movement = cam.get_camera_movement(
        frames,
        read_from_stub=False,
        stub_path=str(ROOT / args.camera_stub),
    )
    cam.add_adjust_positions_to_tracks(tracks, camera_movement)
    moved = sum(1 for m in camera_movement if abs(m[0]) + abs(m[1]) > 0)
    print(f"frames_with_camera_motion={moved}/{len(frames)}")

    print("Applying homography (08fd33_4 calibration)...")
    vt = ViewTransformer()
    vt.add_transformed_position_to_tracks(tracks)
    transformed = sum(
        1
        for fr in tracks["players"]
        for info in fr.values()
        if info.get("position_transformed") is not None
    )
    print(f"player_positions_transformed={transformed}")

    print("Computing speed/distance...")
    spd = SpeedAndDistanceEstimator(frame_rate=fps)
    spd.add_speed_and_distance_to_tracks(tracks)

    print("Drawing...")
    out = tracker.draw_annotations(frames, tracks)
    out = cam.draw_camera_movement(out, camera_movement)
    out = spd.draw_speed_and_distance(out, tracks)
    save_video(out, str(ROOT / args.output), fps=fps)
    print("OK", ROOT / args.output)


if __name__ == "__main__":
    main()
