# Data sources & licenses

| Asset | Origin | License / permission | Path | Notes |
|-------|--------|----------------------|------|-------|
| Match montage | DFL Bundesliga Data Shootout clips (`play`, match id `3c993bd2`) via Hugging Face mirror of Kaggle **DFL - All Clips** | **CC0: Public Domain** ([Kaggle dataset](https://www.kaggle.com/datasets/alejopaullier/dfl-clips)) | `input_videos/match.mp4` | Concatenation of 79 short `play` clips (~72 s), 1920×1080 @ 25 fps |
| Dev sample (montage) | ffmpeg/concat of DFL play clips | CC0 | `input_videos/sample_montage.mp4` | 45 s with cuts — weak for possession |
| Continuous clip | Tutorial `08fd33_4` (DFL shootout) via [Drive sample](https://drive.google.com/file/d/1t6agoqggZKx6thamUuPAIdN_1zR9v9S_/view) | DFL/Kaggle competition clip; cite source | `input_videos/08fd33_4.mp4` / `sample.mp4` | **30 s continuous** 1080p25 — use for tracking/possession |
| WC2022 showcase clip | YouTube full match [`ORzHdV_NVnQ`](https://www.youtube.com/watch?v=ORzHdV_NVnQ) (ARG–FRA final); section ~YT 35:35–36:20 (match ~33′) | Academic / learning local use — **do not redistribute** in git | `input_videos/sample_wc2022.mp4` | **45 s** 1920×1080 @ 30 fps, wide tactical camera |
| WC2022 lineups | [fwc_games / FIFA_World_Cup_Games](https://huggingface.co/datasets/choucsan/FIFA_World_Cup_Games) `games/2022-final-Argentina-vs-France/` | Dataset MIT; video remains YouTube | `data/lineups/wc2022_arg_fra.json` | Starting XI + dorsales + formaciones 4-3-3 / 4-2-3-1 |
| Detection dataset | [Roboflow football-players-detection v1](https://universe.roboflow.com/roboflow-jvuqo/football-players-detection-3zvbc/dataset/1) | **CC BY 4.0** | `football-players-detection-1/` (symlink `dataset/`) | 663 images; classes ball/goalkeeper/player/referee — downloaded locally, not in git |
| SoccerNet half | [SoccerNet Raw HQ](https://huggingface.co/datasets/SoccerNet/SoccerNet_raw_HQ) branch `videos-720p` — Dortmund–Frankfurt 2015-04-25 `1_720p.mkv` | **NDA / research only** — do not redistribute | `data/SoccerNet/.../1_720p.mkv` | ~1.1 GB, 1280×720 @ 25 fps, 45 min |
| SoccerNet sample | ffmpeg cut @ 20:00, 45 s from that half | same NDA | `input_videos/sample_soccernet.mp4` | Continuous tactical clip for pipeline |

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

## YouTube clip prep (WC2022)

```bash
# metadata + lineups (HF, public)
# → data/fwc_games/... and copies under data/lineups/

yt-dlp -f "bv*[height<=1080]+ba/b" \
  --download-sections "*00:35:00-00:37:30" --force-keyframes-at-cuts \
  -o "input_videos/wc2022_probe.%(ext)s" \
  "https://www.youtube.com/watch?v=ORzHdV_NVnQ"

# pick a wide-tactical window (verified ~35–80s of probe), then:
ffmpeg -y -ss 35 -i input_videos/wc2022_probe.mp4 -t 45 \
  -c:v libx264 -crf 20 -preset fast -an input_videos/sample_wc2022.mp4
```

**Caveat:** broadcast mixes close-ups/replays; always spot-check frames before running the pipeline. Homography vertices from `08fd33_4` **do not** transfer — recalibrate for this clip.

## Caveats

- DFL montage clips are event snippets (`play`), not one continuous take — cuts/jumps are expected.
- Fine for pipeline bring-up; WC2022 clip is the better continuous broadcast sample for demos.
- Videos are **gitignored**; keep them local only.

## Tutorial attribution

Architecture inspired by public football-analysis tutorials (YOLO + OpenCV).  
Weights and field calibration in this repo are project-specific.
