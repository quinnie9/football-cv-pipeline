# HU-6 / HU-7 / HU-8 — Camera, homography, speed/distance

**Date:** 2026-11-26  
**Clip:** `input_videos/sample.mp4` (08fd33_4 continuous, 1920×1080 @ 25 fps, 750 frames)  
**Model:** `models/best_yolov11n.pt` · device `mps`  
**Output:** `output_videos/geometry_speed_sample.mp4` (~73 MB)

## Pipeline

1. **Tracks + teams** — ByteTrack stub + K-Means team colors (same as possession run).
2. **HU-6 camera** — Lucas–Kanade optical flow on sparse features; stub `stubs/camera_movement_stub.pkl`.
3. **HU-7 homography** — Fixed 08fd33_4 court vertices → meters via `ViewTransformer`.
4. **HU-8 speed/distance** — Δposition on transformed coords, km/h + cumulative m overlay.

## Results (this run)

| Metric | Value |
|--------|-------|
| Frames with camera motion | **317 / 750** |
| Player positions transformed | **10 144** |
| Runtime (end-to-end) | ~28.5 s |

## Notes / caveats

- Homography vertices are the **tutorial calibration for 08fd33_4**. If the clip or camera framing changes, recalibrate vertices.
- Speed is noisy near ID switches / occlusions; treat overlays as relative, not broadcast-grade GPS.
- Ball detection remains the weak link upstream; geometry only uses player foot positions.

## Re-run

```bash
source .venv/bin/activate
python scripts/run_geometry_speed.py --device mps
```
