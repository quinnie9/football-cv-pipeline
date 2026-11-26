# Dataset plan (HU-1.1 / HU-1.2)

## Recommended primary dataset

**[football-players-detection](https://universe.roboflow.com/roboflow-jvuqo/football-players-detection-3zvbc)** (Roboflow Universe)

| Item | Value |
|------|-------|
| Classes | `ball`, `goalkeeper`, `player`, `referee` (exact match for this pipeline) |
| Version 1 | 663 images (612 train / 38 valid / 13 test) — classic tutorial size |
| Newer versions | ~372 images with stronger models published; still 4 classes |
| Format | YOLOv8/YOLOv11 export (TXT + `data.yaml`) |
| Domain | Same family as DFL / soccer broadcast frames |
| Access | Free Roboflow account + API key |

### Download

```bash
source .venv/bin/activate
export ROBOFLOW_API_KEY=your_key_here   # https://app.roboflow.com/settings/api
python scripts/download_roboflow_dataset.py
# or: python scripts/download_roboflow_dataset.py --login
```

## Fallback / complementary

| Dataset | Classes | License | Notes |
|---------|---------|---------|-------|
| [Football-Image-Dataset](https://github.com/skaczylo/Football-Image-Dataset) | ball, player, referee | CC BY 4.0 | No separate `goalkeeper`; 612 images |
| Custom frames from `input_videos/sample.mp4` | same 4 | our CC0 video | Label in Roboflow/CVAT if we need domain match |

## Why not label everything from scratch first?

Labeling 500+ frames well takes days. Starting from the Roboflow set gets a working detector; we can **add** DFL frames later if recall on our `sample.mp4` is weak (especially ball).

## Audit checklist (HU-1.2)

- [ ] Open `data.yaml` — class order matches labels
- [ ] Spot-check ≥20 train + ≥15 val images
- [ ] Note ball miss / crowd false positives
- [ ] Record license + citation in `DATA_SOURCES.md`
