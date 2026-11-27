# Showcase notes — WC2022 vs calibrated sample

## Decision (2026-11-26)

After WC2022 broadcast experiments:

| Idea | Outcome |
|------|---------|
| Dedicated low-conf ball | More hits, but position still unreliable for possession |
| Temporal ball stabilize | Fewer teleports, still not trustworthy on wide tactical |
| Roster lineups HUD | **Removed from default** — useless if not linked to tracks |
| Jersey → track IDs | **Not implemented** (needs OCR / re-ID) |

**Default showcase posture:** teams + tracking + clamped speed/distance.  
**Ball / possession = documented limitations.**  
**Names:** manual `configs/track_to_player_wc2022.json` — only IDs with readable jersey are named; others show `ARG`/`FRA`. Incomplete by design (ByteTrack ID switches).

## Artifacts

| File | Clip | Notes |
|------|------|-------|
| `output_videos/showcase_wc2022.mp4` | YouTube WC2022 cut | H aproximada; speed clamped ≤36 km/h; **no ball** |
| `output_videos/showcase_sample.mp4` | `08fd33_4` / `sample.mp4` | Tutorial H; more readable metrics; **no ball** |

## Re-run (clean defaults)

```bash
# WC (approximate H)
python scripts/run_showcase.py --device mps --ball-mode off

# Calibrated DFL sample (prefer for demos)
python scripts/run_showcase.py \
  --video input_videos/sample.mp4 \
  --stub stubs/track_stubs.pkl \
  --camera-stub stubs/camera_movement_stub.pkl \
  --homography "" \
  --output output_videos/showcase_sample.mp4 \
  --ball-mode off --device mps
```

Experimental flags (not recommended for report demos): `--ball-mode dedicated --with-possession`, `--with-lineups --lineups data/lineups/wc2022_arg_fra.json`.
