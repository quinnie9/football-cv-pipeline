# football-cv-pipeline

Pipeline **offline** de visión por computador para análisis de video de fútbol.

| Etapa | Enfoque |
|-------|---------|
| Detección | **YOLO11n** fine-tuned (Ultralytics) |
| Tracking | **ByteTrack** |
| Equipos | K-Means sobre color de camiseta |
| Cámara | Optical flow (compensación de paneo) |
| Geometría | Homografía fija → metros |
| Métricas | Velocidad (km/h) y distancia (m) por track ID |
| Salida | Video anotado |

La posesión por proximidad balón–jugador existe como módulo exploratorio, pero **queda fuera del demo principal** (recall del balón ~0.20 en validación).

**Demos:** [Release `demo-v2`](https://github.com/quinnie9/football-cv-pipeline/releases/tag/demo-v2) · índice local en [`demo/README.md`](demo/README.md)

---

## Estructura

```text
trackers/                       # YOLO + ByteTrack
team_assigner/                  # color → 2 equipos
player_ball_assigner/           # posesión (opcional / off por defecto)
camera_movement_estimator/      # optical flow
view_transformer/               # homografía
speed_and_distance_estimator/   # km/h, m
utils/                          # bbox, video, labels
scripts/                        # train helpers + run_* + showcase
configs/                        # data.yaml, H, mapas ID→jugador
data/lineups/                   # alineaciones WC2022 (JSON)
docs/                           # informes, experimentos, Overleaf
demo/                           # README de videos (MP4 en Release)
training/                       # notas de entrenamiento
models/                         # pesos locales (gitignored)
input_videos/ · output_videos/  # clips locales (gitignored)
```

---

## Setup

Python **3.10+** (3.11 recomendado). `ffmpeg` útil para cortes.

```bash
cd football-cv-pipeline
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
python scripts/smoke_test_imports.py
```

Pesos esperados en `models/best_yolov11n.pt` (local). Dataset Roboflow: ver [`docs/DATASET.md`](docs/DATASET.md). Fuentes de video y licencias: [`docs/DATA_SOURCES.md`](docs/DATA_SOURCES.md).

---

## Demo recomendada (showcase DFL)

Con stubs ya generados en local:

```bash
source .venv/bin/activate
python scripts/run_showcase.py \
  --video input_videos/sample.mp4 \
  --stub stubs/track_stubs.pkl \
  --camera-stub stubs/camera_movement_stub.pkl \
  --homography "" \
  --id-map "" \
  --output output_videos/showcase_sample.mp4 \
  --ball-mode off \
  --device mps
```

`main.py` redirige a este entrypoint. Más scripts por etapa: `scripts/run_tracking.py`, `run_teams.py`, `run_geometry_speed.py`, …

---

## Documentación

| Documento | Para qué |
|-----------|----------|
| [`docs/README.md`](docs/README.md) | Índice de toda la documentación |
| [`docs/overleaf/`](docs/overleaf/) | Artículo IEEE + guía de laboratorio (Overleaf) |
| [`docs/experiments/`](docs/experiments/) | Bitácoras por etapa (métricas, decisiones) |
| [`docs/INFORME_GRUPO.md`](docs/INFORME_GRUPO.md) | Informe interno de grupo |
| [`docs/PRESENTACION_TECNICA.md`](docs/PRESENTACION_TECNICA.md) | Guion de presentación |

---

## Qué no va en git

Videos, pesos (`.pt`), stubs (`.pkl`), dataset Roboflow, SoccerNet (NDA) y clones HF locales. Solo se versionan código, configs ligeros, lineups JSON y docs. Los MP4 de evidencia pública están en el Release.
