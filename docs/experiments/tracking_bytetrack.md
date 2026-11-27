# HU-3.1 — ByteTrack on fine-tuned YOLO11n

| Item | Value |
|------|-------|
| Model | `models/best_yolov11n.pt` |
| Tracker | Ultralytics ByteTrack (`bytetrack.yaml`) |
| Video | `input_videos/sample.mp4` (45 s montage of DFL play clips) |
| Output | `output_videos/tracked_sample.mp4` |
| Stub | `stubs/track_stubs.pkl` |

## Implementation notes

- `supervision` 0.32 no longer ships ByteTrack; we use Ultralytics' built-in ByteTrack (same family).
- Goalkeeper detections are mapped to `player` for ID continuity.
- Ball stored under fixed key `1` (not ByteTrack).

## Results on sample

- Tracking runs end-to-end with ellipses + IDs + ball triangle.
- **High unique player ID count** on this clip is expected: `sample.mp4` is a concatenation of many short DFL events, so camera/scene cuts reset tracks.
- Within a continuous shot, IDs are stable (verified on the first frames).

## Next

Prefer a continuous broadcast clip for cleaner possession/speed demos; keep this sample for detection bring-up.
