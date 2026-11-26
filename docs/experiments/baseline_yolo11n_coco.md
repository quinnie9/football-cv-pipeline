# HU-2.1 — Baseline YOLO11n (COCO) on `sample.mp4`

| Item | Value |
|------|-------|
| Model | `yolo11n.pt` (COCO pretrained, no football fine-tune) |
| Source | `input_videos/sample.mp4` (45 s, 1080p25, CC0 DFL montage) |
| imgsz | 640 |
| conf | 0.25 |
| device | mps |
| Output | `runs/detect/runs/baseline/yolo11n_coco/` |

## Qualitative result

- Detects mostly **`person`** (COCO class).
- Does **not** emit `player` / `goalkeeper` / `referee` / `ball` as project classes.
- Sports ball may appear rarely or not at all at this resolution/conf on wide shots.

## Takeaway

Baseline justifies fine-tuning on a football-labelled dataset (Roboflow `football-players-detection-3zvbc`).
