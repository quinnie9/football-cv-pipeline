# HU-2.3 — Detector validation & Go/No-go

**Checkpoint:** `models/best_yolov11n.pt`  
**Data:** `football-players-detection-1` (CC BY 4.0) via `configs/data.yaml`  
**Train setup:** YOLO11n, 50 epochs, imgsz=640, batch=16, device=mps, seed=42  
**Eval:** imgsz=640, device=mps (2026-11-26)

## Quantitative results

### Validation split (n=38 images)

| Class | Images | Instances | Precision | Recall | mAP50 | mAP50-95 |
|-------|--------|-----------|-----------|--------|-------|----------|
| all | 38 | 905 | 0.869 | 0.727 | 0.758 | 0.482 |
| ball | 35 | 35 | 0.820 | **0.200** | **0.251** | 0.066 |
| goalkeeper | 27 | 27 | 0.885 | 0.926 | 0.968 | 0.675 |
| player | 38 | 754 | 0.942 | 0.968 | 0.976 | 0.695 |
| referee | 38 | 89 | 0.828 | 0.813 | 0.837 | 0.491 |

### Test split (n=13 images — small; interpret cautiously)

| Class | Images | Instances | Precision | Recall | mAP50 | mAP50-95 |
|-------|--------|-----------|-----------|--------|-------|----------|
| all | 13 | 310 | 0.821 | 0.780 | 0.766 | 0.496 |
| ball | 11 | 11 | 0.673 | **0.273** | **0.255** | 0.072 |
| goalkeeper | 11 | 11 | 0.883 | 1.000 | 1.000 | 0.726 |
| player | 13 | 259 | 0.951 | 0.950 | 0.972 | 0.696 |
| referee | 13 | 29 | 0.779 | 0.897 | 0.837 | 0.489 |

Artifacts: `runs/detect/runs/eval/val_ft/`, `runs/detect/runs/eval/test_ft/`

## Baseline contrast on our sample clip (qualitative / counts)

Same `input_videos/sample.mp4`, every 25th frame, conf=0.2, 45 sampled frames:

| Model | Dominant detections |
|-------|---------------------|
| YOLO11n COCO | `person`: 853 only |
| YOLO11n fine-tuned | `player` 910 · `referee` 139 · `goalkeeper` 20 · `ball` 10 |

Fine-tuning enables the project classes. Ball remains rare on this wide montage.

## Visual notes (sample.mp4)

- Players / referees / goalkeepers: usable boxes and class labels (confirmed in FT video).  
- Ball: intermittent; many frames without a ball box even when a ball may be present.  
- Sample is a **cut montage** → harder than a continuous broadcast shot.

## Limitations (for the report)

1. Ball recall is the main bottleneck (~0.20–0.27).  
2. Test set is tiny (13 images) → point estimates are noisy.  
3. Train/val/test come from Roboflow v1; our DFL montage is a related but not identical domain.  
4. Detector transfer ≠ full pipeline transfer (teams/homography remain clip-specific).

## Decision

### **GO — proceed with this checkpoint for the rest of the pipeline**

**Rationale**

- Player / goalkeeper / referee metrics are strong enough for tracking and team modules.  
- Clear improvement vs COCO baseline for the task taxonomy.  
- Ball weakness is **known and documented**; possession/speed must treat missing ball frames as a limitation, not hide it.

**Do later (optional, not blocking)**

- More epochs / larger imgsz (e.g. 1280) if ball recall must improve.  
- Add hard ball frames from our video to the dataset.  
- Formal HU-2.4 table can reuse these numbers + COCO count contrast.

## Freeze

Use **`models/best_yolov11n.pt`** as the project detector until an explicit retrain.
EOF