#!/usr/bin/env python3
"""Unified showcase: teams + possession + camera + H + speed + optional lineups."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Dict, List, Optional

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from camera_movement_estimator import CameraMovementEstimator
from player_ball_assigner import PlayerBallAssigner
from speed_and_distance_estimator import SpeedAndDistanceEstimator
from team_assigner import TeamAssigner
from trackers import Tracker
from utils import get_video_meta, read_video, save_video
from utils.ball_stabilize import jump_stats, stabilize_ball_tracks
from utils.lineup_overlay import draw_lineups, load_lineups
from utils.player_labels import label_for_track, load_track_map
from view_transformer import ViewTransformer


def interpolate_ball_tracks(
    ball_tracks: List[Dict], max_gap: int = 12
) -> List[Dict]:
    """Linear-interpolate ball bbox across short detection gaps (same track only)."""
    n = len(ball_tracks)
    centers: List[Optional[np.ndarray]] = [None] * n
    sizes: List[Optional[np.ndarray]] = [None] * n

    for i, frame_ball in enumerate(ball_tracks):
        if not frame_ball:
            continue
        bbox = next(iter(frame_ball.values()))["bbox"]
        x1, y1, x2, y2 = bbox
        centers[i] = np.array([(x1 + x2) / 2, (y1 + y2) / 2], dtype=np.float32)
        sizes[i] = np.array([x2 - x1, y2 - y1], dtype=np.float32)

    known = [i for i, c in enumerate(centers) if c is not None]
    if len(known) < 2:
        return ball_tracks

    out = [dict(b) for b in ball_tracks]
    for a, b in zip(known, known[1:]):
        gap = b - a
        if gap <= 1 or gap > max_gap:
            continue
        # Only interp if endpoints are spatially close (avoid bridging teleports)
        if float(np.linalg.norm(centers[b] - centers[a])) > 80.0 * gap:
            continue
        for t in range(a + 1, b):
            alpha = (t - a) / gap
            c = (1 - alpha) * centers[a] + alpha * centers[b]
            s = (1 - alpha) * sizes[a] + alpha * sizes[b]
            x1, y1 = float(c[0] - s[0] / 2), float(c[1] - s[1] / 2)
            x2, y2 = float(c[0] + s[0] / 2), float(c[1] + s[1] / 2)
            out[t] = {
                1: {
                    "bbox": [x1, y1, x2, y2],
                    "cls": "ball",
                    "interpolated": True,
                }
            }
    return out


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--video", default="input_videos/sample_wc2022.mp4")
    parser.add_argument("--model", default="models/best_yolov11n.pt")
    parser.add_argument("--output", default="output_videos/showcase_wc2022.mp4")
    parser.add_argument("--stub", default="stubs/track_stubs_wc2022_ballv2.pkl")
    parser.add_argument("--camera-stub", default="stubs/camera_movement_wc2022.pkl")
    parser.add_argument("--homography", default="configs/homography_wc2022.json")
    parser.add_argument("--lineups", default="")
    parser.add_argument(
        "--id-map",
        default="configs/track_to_player_wc2022.json",
        help="Manual track_id→player JSON (empty to skip names)",
    )
    parser.add_argument("--conf", type=float, default=0.15)
    parser.add_argument("--ball-conf", type=float, default=0.02)
    parser.add_argument("--ball-imgsz", type=int, default=1280)
    parser.add_argument(
        "--ball-mode",
        choices=["dedicated", "track", "off"],
        default="off",
        help="Ball is a known limitation; default off. dedicated/track are experimental.",
    )
    parser.add_argument("--max-jump", type=float, default=80.0)
    parser.add_argument("--device", default="mps")
    parser.add_argument("--max-distance", type=float, default=90.0)
    parser.add_argument("--ball-gap", type=int, default=10)
    parser.add_argument("--seed-frame", type=int, default=0)
    parser.add_argument("--refresh-tracks", action="store_true")
    parser.add_argument(
        "--with-lineups",
        action="store_true",
        help="Draw roster HUD (not linked to tracks — off by default)",
    )
    parser.add_argument(
        "--with-possession",
        action="store_true",
        help="Enable possession overlay (needs ball; off by default)",
    )
    parser.add_argument(
        "--no-speed",
        action="store_true",
        help="Skip speed/distance overlay (cleaner when H is approximate)",
    )
    parser.add_argument(
        "--no-camera-hud",
        action="store_true",
        help="Skip camera movement text overlay",
    )
    args = parser.parse_args()

    video = ROOT / args.video
    fps, w, h, _ = get_video_meta(str(video))
    print(f"video={video.name} {w}x{h} @ {fps:.2f} fps")

    frames = read_video(str(video))

    # ball_mode=track → disable dedicated pass by setting absurdly high ball_conf
    # and relying on boxes that appear in track() — actually track() no longer
    # keeps ball. For track mode, use dedicated with higher conf / smaller imgsz
    # matching the original single-pass behaviour.
    if args.ball_mode == "dedicated":
        ball_conf, ball_imgsz, detect_ball = args.ball_conf, args.ball_imgsz, True
    elif args.ball_mode == "track":
        ball_conf, ball_imgsz, detect_ball = args.conf, 640, True
    else:
        ball_conf, ball_imgsz, detect_ball = args.ball_conf, args.ball_imgsz, False

    tracker = Tracker(
        str(ROOT / args.model),
        conf=args.conf,
        device=args.device,
        ball_conf=ball_conf,
        ball_imgsz=ball_imgsz,
        detect_ball=detect_ball,
    )
    stub = ROOT / args.stub
    use_stub = stub.exists() and not args.refresh_tracks
    tracks = tracker.get_object_tracks(
        frames,
        read_from_stub=use_stub,
        stub_path=str(stub),
    )
    print(
        f"tracks_source={'stub' if use_stub else 'detect'} "
        f"ball_mode={args.ball_mode} ball_conf={ball_conf} ball_imgsz={ball_imgsz}"
    )

    if args.ball_mode == "off":
        tracks["ball"] = [{} for _ in frames]
        print("ball/possession: OFF (documented limitation)")
    else:
        raw_stats = jump_stats(tracks["ball"])
        print(
            f"ball_raw frames={sum(1 for b in tracks['ball'] if b)} "
            f"jump_med={raw_stats['median']:.1f}px p90={raw_stats['p90']:.1f} "
            f"gt80={raw_stats['gt80']*100:.1f}% gt150={raw_stats['gt150']*100:.1f}%"
        )
        tracks["ball"] = stabilize_ball_tracks(
            tracks["ball"], max_jump_px=args.max_jump, max_coast=8
        )
        stab_stats = jump_stats(tracks["ball"])
        before = sum(1 for b in tracks["ball"] if b)
        tracks["ball"] = interpolate_ball_tracks(tracks["ball"], max_gap=args.ball_gap)
        after = sum(1 for b in tracks["ball"] if b)
        print(
            f"ball_stab frames={before} -> {after} after interp | "
            f"jump_med={stab_stats['median']:.1f}px p90={stab_stats['p90']:.1f} "
            f"gt80={stab_stats['gt80']*100:.1f}% gt150={stab_stats['gt150']*100:.1f}%"
        )
        if stab_stats["gt150"] > 0.05:
            print(
                "WARN: ball still teleports often after stabilize — "
                "prefer --ball-mode off and document as limitation"
            )
    tracker.add_position_to_tracks(tracks)

    seed = args.seed_frame
    if not tracks["players"][seed]:
        seed = next((i for i, t in enumerate(tracks["players"]) if t), 0)
    team_assigner = TeamAssigner()
    team_assigner.assign_team_color(frames[seed], tracks["players"][seed])

    track_map = None
    id_map_path = ROOT / args.id_map if args.id_map else None
    if id_map_path and id_map_path.exists():
        track_map = load_track_map(id_map_path)
        print(
            f"id_map={id_map_path.name} "
            f"named={len(track_map.get('players', {}))} "
            f"teams={track_map.get('team_abbr')}"
        )

    for frame_num, player_track in enumerate(tracks["players"]):
        for player_id, track in player_track.items():
            team = team_assigner.get_player_team(
                frames[frame_num], track["bbox"], player_id
            )
            tracks["players"][frame_num][player_id]["team"] = team
            tracks["players"][frame_num][player_id]["team_color"] = (
                team_assigner.bgr_tuple(team)
            )
            tracks["players"][frame_num][player_id]["label"] = label_for_track(
                player_id, team, track_map
            )

    control: Optional[np.ndarray] = None
    if args.with_possession and args.ball_mode != "off":
        assigner = PlayerBallAssigner(max_distance=args.max_distance)
        team_ball_control: list[int] = []
        assigned = 0
        for frame_num, player_track in enumerate(tracks["players"]):
            ball = tracks["ball"][frame_num]
            if not ball:
                team_ball_control.append(0)
                continue
            ball_bbox = next(iter(ball.values()))["bbox"]
            pid = assigner.assign_ball_to_player(player_track, ball_bbox)
            if pid != -1:
                tracks["players"][frame_num][pid]["has_ball"] = True
                team = int(tracks["players"][frame_num][pid].get("team", 0))
                team_ball_control.append(team)
                assigned += 1
            else:
                team_ball_control.append(0)
        control = np.array(team_ball_control, dtype=int)
        valid = control[control > 0]
        t1 = 100.0 * float(np.mean(valid == 1)) if len(valid) else 0.0
        t2 = 100.0 * float(np.mean(valid == 2)) if len(valid) else 0.0
        print(
            f"possession_assigned={assigned}/{len(frames)} "
            f"team1={t1:.1f}% team2={t2:.1f}% (assigned frames only)"
        )
    print("Estimating camera movement...")
    cam = CameraMovementEstimator(frames[0])
    camera_movement = cam.get_camera_movement(
        frames,
        read_from_stub=(ROOT / args.camera_stub).exists(),
        stub_path=str(ROOT / args.camera_stub),
    )
    cam.add_adjust_positions_to_tracks(tracks, camera_movement)

    h_cfg = ROOT / args.homography if args.homography else None
    print(f"Applying homography ({h_cfg.name if h_cfg and h_cfg.exists() else 'default'})...")
    vt = (
        ViewTransformer(config_path=h_cfg)
        if h_cfg and h_cfg.exists()
        else ViewTransformer()
    )
    vt.add_transformed_position_to_tracks(tracks)
    transformed = sum(
        1
        for fr in tracks["players"]
        for info in fr.values()
        if info.get("position_transformed") is not None
    )
    print(f"player_positions_transformed={transformed}")

    spd = None
    if not args.no_speed:
        print("Computing speed/distance...")
        spd = SpeedAndDistanceEstimator(frame_rate=fps)
        spd.add_speed_and_distance_to_tracks(tracks)
    else:
        print("speed/distance: OFF")

    print("Drawing...")
    out = tracker.draw_annotations(frames, tracks, team_ball_control=control)
    if not args.no_camera_hud:
        out = cam.draw_camera_movement(out, camera_movement)
    if spd is not None:
        out = spd.draw_speed_and_distance(out, tracks)

    if args.with_lineups and args.lineups:
        lineup_path = ROOT / args.lineups
        if lineup_path.exists():
            print(f"Overlay lineups from {lineup_path.name} (roster only — not recommended)")
            out = draw_lineups(out, load_lineups(lineup_path))

    save_video(out, str(ROOT / args.output), fps=fps)
    print("OK", ROOT / args.output)


if __name__ == "__main__":
    main()
