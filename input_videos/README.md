# Input videos

Large files are gitignored. Local artifacts after HU-0.3:

| File | Role |
|------|------|
| `match.mp4` | ~72 s montage of CC0 DFL `play` clips |
| `sample.mp4` | 45 s dev cut (default for experiments) |
| `_raw/` | original short clips (optional; gitignored) |

See `docs/DATA_SOURCES.md` for license and provenance.

```bash
ffprobe -v error -select_streams v:0 \
  -show_entries stream=width,height,r_frame_rate \
  -show_entries format=duration \
  -of default=noprint_wrappers=1 \
  input_videos/sample.mp4
```
