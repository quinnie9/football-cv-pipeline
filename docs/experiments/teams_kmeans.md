# HU-4.1 — Team assignment (K-Means jersey color)

| Item | Value |
|------|-------|
| Seed frame | 0 (21 players) |
| Team 1 BGR | (185, 224, 223) — light |
| Team 2 BGR | (28, 90, 79) — dark |
| Sticky track assignments | team1: 591 · team2: 480 |
| Output | `output_videos/teams_sample.mp4` |

## Method

1. Upper-half crop of each player bbox  
2. KMeans(2) pixels → jersey vs corner/background  
3. KMeans(2) over jersey colors → two team centroids  
4. Each track ID keeps its first assignment (sticky)

## Caveats

- Grass/shadows can pollute colors.  
- Similar kits or GKs confuse clusters.  
- Montage cuts create many track IDs; assignment is per ID, not per real person.
