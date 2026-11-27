# HU-5.1 — Possession heuristic

| Item | Value |
|------|-------|
| Video | `input_videos/sample.mp4` |
| Output | `output_videos/possession_sample.mp4` |
| Rule | nearest player (feet) to ball center if distance &lt; 70 px |
| Ball visible frames | 43 / 1123 (~3.8%) |
| Frames with possession assigned | 36 / 1123 |

## Design choice

Percentages are computed **only on frames with a successful ball→player assignment**.  
Unknown frames are left as 0 (not sticky-filled). With our low ball recall, sticky-fill would freeze one team’s % for almost the entire clip after the first hit.

## Interpretation

This is an **exploratory overlay**, not official match possession. It inherits detector ball weakness documented in `detector_validation_hu23.md`.
