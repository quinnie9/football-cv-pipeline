# football-cv-pipeline

Hybrid **computer-vision pipeline** for offline football video analysis.

| Stage | Approach |
|-------|----------|
| Detection | **YOLO11** (Ultralytics), project-trained weights |
| Tracking | **ByteTrack** via `supervision` |
| Teams | K-Means on jersey color |
| Possession | Ball–player proximity heuristic |
| Camera | Optical flow compensation |
| Geometry | Homography (our calibration) → meters |
| Metrics | Distance (m) and speed (km/h) |
| Output | Annotated video |

Inspired by public tutorials; implementation is modular/hybrid. **Training and field calibration are ours.**

## Repository layout

```text
main.py                         # end-to-end entry (wired in HU-9.1)
utils/                          # video I/O, bbox helpers
trackers/                       # YOLO11 + ByteTrack
team_assigner/                  # jersey color → team
player_ball_assigner/           # possession heuristic
camera_movement_estimator/      # optical flow
view_transformer/               # homography
speed_and_distance_estimator/   # kinematics
training/                       # train notes / notebooks
configs/                        # data.yaml & pipeline examples
input_videos/                   # clips (gitignored)
output_videos/                  # annotated exports
models/                         # .pt weights (gitignored)
stubs/                          # cached tracks (gitignored)
runs/                           # ultralytics runs
docs/BACKLOG.md                 # epics + user stories
```

## Setup (HU-0.2)

Requires **Python 3.10+** (3.11 recommended), `ffmpeg` optional for clipping.

```bash
cd football-cv-pipeline
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
python scripts/smoke_test_imports.py
```

Optional lockfile after a good install:

```bash
pip freeze > requirements-lock.txt
```

## Quick status

- [x] HU-0.1 structure
- [x] HU-0.2 environment files + smoke test
- [x] HU-0.3 CC0 DFL sample (`input_videos/sample.mp4`)
- [ ] Detection / tracking / … (see [docs/BACKLOG.md](docs/BACKLOG.md))

```bash
python main.py   # exits until pipeline is wired (HU-9.1)
```

## Issues

Backlog as GitHub Issues: https://github.com/quinnie9/football-cv-pipeline/issues
