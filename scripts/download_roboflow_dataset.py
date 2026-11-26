#!/usr/bin/env python3
"""Download football-players-detection (4 classes) from Roboflow Universe.

Preferred for this project: ball, goalkeeper, player, referee.
Requires a free Roboflow account.

Usage:
  # Option A — API key in env
  export ROBOFLOW_API_KEY=xxxxxxxx
  python scripts/download_roboflow_dataset.py

  # Option B — interactive browser login
  python scripts/download_roboflow_dataset.py --login
"""

from __future__ import annotations

import argparse
import os
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT / "dataset"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--login", action="store_true", help="Use roboflow.login() browser auth")
    parser.add_argument("--version", type=int, default=1, help="Dataset version (1 = 663 images classic tutorial)")
    parser.add_argument("--format", default="yolov8", help="Export format (yolov8 works with YOLO11)")
    args = parser.parse_args()

    from roboflow import Roboflow
    import roboflow

    if args.login:
        roboflow.login()
        rf = Roboflow()
    else:
        key = os.environ.get("ROBOFLOW_API_KEY")
        if not key:
            raise SystemExit(
                "Set ROBOFLOW_API_KEY or pass --login\n"
                "Get a free key: https://app.roboflow.com/settings/api"
            )
        rf = Roboflow(api_key=key)

    project = rf.workspace("roboflow-jvuqo").project("football-players-detection-3zvbc")
    version = project.version(args.version)
    # Download next to repo; then normalize into dataset/
    tmp = ROOT / f"football-players-detection-{args.version}"
    if tmp.exists():
        shutil.rmtree(tmp)

    ds = version.download(args.format, location=str(tmp))
    print("Downloaded to", ds.location)

    # Normalize layout to dataset/{images,labels}/{train,val,test} if needed
    # Roboflow YOLOv8 layout is usually:
    #   train/images, train/labels, valid/images, valid/labels, test/..., data.yaml
    data_yaml = Path(ds.location) / "data.yaml"
    print("data.yaml at", data_yaml)
    print(data_yaml.read_text())

    # Symlink/copy convenience path
    if DEST.exists():
        if DEST.is_symlink() or DEST.is_dir():
            # keep existing if already populated
            print("Note: ./dataset already exists; leaving download at", ds.location)
        else:
            DEST.symlink_to(tmp, target_is_directory=True)
    else:
        DEST.symlink_to(tmp, target_is_directory=True)
        print("Linked dataset/ ->", tmp)

    print("OK — next: audit labels (HU-1.2) then train YOLO11 (HU-2.2)")


if __name__ == "__main__":
    main()
