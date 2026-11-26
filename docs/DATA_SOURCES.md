# Data sources & licenses

| Asset | Origin | License / permission | Path | Notes |
|-------|--------|----------------------|------|-------|
| Match montage | DFL Bundesliga Data Shootout clips (`play`, match id `3c993bd2`) via Hugging Face mirror of Kaggle **DFL - All Clips** | **CC0: Public Domain** ([Kaggle dataset](https://www.kaggle.com/datasets/alejopaullier/dfl-clips)) | `input_videos/match.mp4` | Concatenation of 79 short `play` clips (~72 s), 1920×1080 @ 25 fps |
| Dev sample | ffmpeg cut of `match.mp4` | same (CC0) | `input_videos/sample.mp4` | First **45 s** for fast iteration |
| Detection dataset | _TBD (e.g. Roboflow)_ | _TBD_ | `dataset/` | classes: ball, goalkeeper, player, referee |

## How the video was prepared (HU-0.3)

1. Downloaded DFL `play` clips for match `3c993bd2` from  
   `https://huggingface.co/datasets/ManuD/DFL_video_classification`  
   (same competition clips redistributed; upstream Kaggle license **CC0**).
2. Sorted by timestamp in the filename and concatenated with ffmpeg.
3. Created the 45 s sample:

```bash
ffmpeg -y -ss 0 -i input_videos/match.mp4 -t 45 -c:v libx264 -crf 23 -preset fast -an input_videos/sample.mp4
```

4. Metadata check:

```bash
ffprobe -v error -select_streams v:0 \
  -show_entries stream=width,height,r_frame_rate,nb_frames \
  -show_entries format=duration \
  -of default=noprint_wrappers=1 \
  input_videos/sample.mp4
```

**Measured sample:** 1920×1080, 25 fps, duration 45.0 s.

## Caveats

- Source clips are event snippets (`play`), not one continuous take — cuts/jumps are expected.
- Fine for pipeline bring-up; for polished possession/speed demos, prefer a longer continuous broadcast clip later.
- Videos are **gitignored**; keep them local only.

## Tutorial attribution

Architecture inspired by public football-analysis tutorials (YOLO + OpenCV).  
Weights and field calibration in this repo are project-specific.
