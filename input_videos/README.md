# Input videos

Place authorized match clips here. Large files are gitignored.

## Suggested workflow (HU-0.3)

1. Copy your source clip as `match.mp4` (document origin/license in `docs/DATA_SOURCES.md`).
2. Create a short sample for development:

```bash
ffmpeg -ss 00:00:20 -i input_videos/match.mp4 -t 45 -c:v libx264 -crf 23 -c:a aac input_videos/sample.mp4
```

3. Inspect metadata:

```bash
ffprobe -v error -select_streams v:0 \
  -show_entries stream=width,height,r_frame_rate,nb_frames \
  -show_entries format=duration \
  -of default=noprint_wrappers=1 \
  input_videos/sample.mp4
```

Default path used by `configs/pipeline.example.yaml`: `input_videos/sample.mp4`.
