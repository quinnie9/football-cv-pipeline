# HU-1.1 / HU-1.2 — Dataset audit (football-players-detection v1)

| Item | Value |
|------|-------|
| Path | `football-players-detection-1/` → symlink `dataset/` |
| License | CC BY 4.0 |
| Classes | 0 ball, 1 goalkeeper, 2 player, 3 referee |
| Split | train 612 / valid 38 / test 13 |
| Size on disk | ~148 MB |

## Box counts

| Split | ball | goalkeeper | player | referee |
|-------|------|------------|--------|---------|
| train | 519 | 435 | 12228 | 1401 |
| valid | 35 | 27 | 754 | 89 |
| test | 11 | 11 | 259 | 29 |

## Integrity

- No empty label files
- No orphan images/labels
- `data.yaml` paths normalized to `train/images`, `valid/images`, `test/images`

## Notes

- Strong class imbalance (player ≫ ball); expected for football frames.
- Test set is tiny (13) — useful as smoke test; report val metrics carefully.
- Ready for HU-2.2 (YOLO11 fine-tune). **Do not re-download** unless corrupt.
