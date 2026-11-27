# Informe de proyecto — football-cv-pipeline

**Audiencia:** compañeros de grupo  
**Fecha:** 2026-11-26  
**Repo:** [github.com/quinnie9/football-cv-pipeline](https://github.com/quinnie9/football-cv-pipeline)  
**Objetivo:** reproducir un pipeline híbrido de análisis de video de fútbol (detección → tracking → equipos → posesión → cámara → homografía → velocidad/distancia), con entrenamiento y calibración propios, documentando límites con honestidad académica.

---

## 1. Resumen ejecutivo

Se construyó un pipeline modular offline que anota video de partido. El núcleo funciona bien para **jugadores, árbitros y equipos**. El **balón** es el cuello de botella (recall bajo) y condiciona posesión. La **identidad por nombre/dorsal** no es automática: solo mapa manual parcial + etiquetas ARG/FRA. El artefacto más limpio para demo es el clip DFL calibrado; el clip WC2022 sirve para mostrar generalización y límites en broadcast.

---

## 2. Stack y plataformas usadas

| Capa | Tecnología / plataforma | Uso |
|------|-------------------------|-----|
| Lenguaje | Python 3.11+ (venv) | Todo el pipeline |
| Detección | **Ultralytics YOLO11n** | Fine-tune + inferencia |
| Tracking | **ByteTrack** (vía Ultralytics `model.track`) | IDs temporales de jugadores |
| Equipos | **scikit-learn K-Means** | Color de camiseta → 2 equipos |
| Visión | **OpenCV** | Video I/O, optical flow, homografía, overlays |
| Deep learning | **PyTorch** (backend Ultralytics) | Entrenamiento/inferencia |
| Aceleración local | **Apple Silicon MPS** (Mac) | Train + inferencia (Colab falló → se pasó a local) |
| Dataset detección | **Roboflow Universe** — football-players-detection v1 (CC BY 4.0) | 4 clases: ball, goalkeeper, player, referee |
| Video DFL | **Kaggle / HF mirror** clips Bundesliga Data Shootout (CC0) | Clip continuo `08fd33_4` / `sample.mp4` |
| Video + lineups WC | **YouTube** + dataset **fwc_games** (Hugging Face) | Final ARG–FRA 2022 + `lineups.json` |
| Acceso académico | **SoccerNet Raw HQ** (Hugging Face, NDA) | Acceso concedido; sample local (no redistribuir) |
| Repo / issues | **GitHub** | Código + backlog HU |
| Utilidades | ffmpeg, yt-dlp, huggingface_hub | Cortes de video y descarga de metadatos |

**Versiones observadas en el entorno de trabajo:** PyTorch ~2.15, Ultralytics ~8.4, OpenCV ~4.10.

**Hardware:** Mac Apple Silicon (entrenamiento e inferencia con `device=mps`).

---

## 3. Qué se hizo (por etapas)

### 3.1 Fundación (HU-0)

- Repo modular: `trackers/`, `team_assigner/`, `player_ball_assigner/`, `camera_movement_estimator/`, `view_transformer/`, `speed_and_distance_estimator/`, `utils/`, `scripts/`, `docs/`, `configs/`.
- Entorno reproducible (`requirements.txt`, smoke test de imports).
- Videos documentados en `docs/DATA_SOURCES.md` (gitignored; no se suben al remoto).

### 3.2 Datos y detector (HU-1 / HU-2)

- Dataset Roboflow v1 auditado (`docs/experiments/dataset_audit_v1.md`).
- Baseline YOLO11n **COCO** vs fine-tuned (`docs/experiments/baseline_yolo11n_coco.md`).
- Entrenamiento: YOLO11n, **50 epochs**, imgsz=640, batch=16, seed=42, **MPS**.
- Checkpoint: `models/best_yolov11n.pt`.
- **Go/No-go GO** con ball débil documentado (`docs/experiments/detector_validation_hu23.md`).

**Métricas val (resumen):**

| Clase | Precision | Recall | mAP50 |
|-------|-----------|--------|-------|
| all | 0.87 | 0.73 | 0.76 |
| player | 0.94 | 0.97 | 0.98 |
| goalkeeper | 0.89 | 0.93 | 0.97 |
| referee | 0.83 | 0.81 | 0.84 |
| **ball** | 0.82 | **0.20** | **0.25** |

### 3.3 Tracking (HU-3)

- ByteTrack sobre el fine-tune.
- Stubs en `stubs/` para no re-detectar en cada experimento.
- Evidencia: `docs/experiments/tracking_bytetrack.md`.

### 3.4 Equipos (HU-4)

- K-Means sobre color de torso/camiseta; asignación sticky por track ID.
- Evidencia: `docs/experiments/teams_kmeans.md`.

### 3.5 Posesión (HU-5)

- Heurística: balón → jugador más cercano (pies) bajo umbral de píxeles.
- Clip montaje con cortes → malo; se pasó a clip **continuo** `08fd33_4`.
- % de posesión solo sobre frames con asignación (sin “sticky” engañoso).
- Evidencia: `docs/experiments/possession_continuous_08fd33.md`, video `output_videos/possession_sample.mp4`.

### 3.6 Cámara + homografía + speed (HU-6/7/8)

- Optical flow (Lucas–Kanade) para compensar paneo.
- Homografía imagen → metros (calibración tutorial para `08fd33_4`).
- Velocidad km/h y distancia acumulada m por track ID (con clamps ≤36 km/h en showcase limpio).
- Evidencia: `docs/experiments/geometry_speed_hu678.md`, `output_videos/geometry_speed_sample.mp4`.

### 3.7 Showcase unificado + experimento WC2022

- Script: `scripts/run_showcase.py` (equipos + opc. posesión + cámara + H + speed).
- Clip YouTube final Mundial 2022 + lineups JSON.
- Intentos de mejorar balón (pase hi-res / low-conf + estabilización temporal): más detecciones pero posición aún poco fiable → **balón/posesión OFF por defecto**.
- Nombres: mapa manual `configs/track_to_player_wc2022.json` (solo dorsales legibles, p.ej. Molina #26) + resto `ARG`/`FRA`.
- Videos:
  - `output_videos/showcase_sample.mp4` — clip DFL calibrado (demo recomendada)
  - `output_videos/showcase_wc2022.mp4` — broadcast + límites

---

## 4. Arquitectura del pipeline

```text
Video
  → YOLO11n (fine-tuned)
  → ByteTrack (IDs)
  → K-Means teams
  → [opcional] posesión por proximidad al balón
  → optical flow (ajuste de posición)
  → homografía (metros)
  → speed / distance
  → video anotado
```

Entrada típica:

```bash
source .venv/bin/activate
# Demo limpia (recomendado)
python scripts/run_showcase.py \
  --video input_videos/sample.mp4 \
  --stub stubs/track_stubs.pkl \
  --camera-stub stubs/camera_movement_stub.pkl \
  --homography "" \
  --id-map "" \
  --output output_videos/showcase_sample.mp4 \
  --ball-mode off --device mps
```

---

## 5. Artefactos clave (dónde mirar)

| Tipo | Ruta |
|------|------|
| Pesos | `models/best_yolov11n.pt` |
| Docs experimentos | `docs/experiments/*.md` |
| Fuentes/licencias | `docs/DATA_SOURCES.md` |
| Backlog HU | `docs/BACKLOG.md` |
| Lineups WC | `data/lineups/wc2022_arg_fra.json` |
| Mapa ID→nombre | `configs/track_to_player_wc2022.json` |
| H WC (aprox.) | `configs/homography_wc2022.json` |
| Videos salida | `output_videos/showcase_sample.mp4`, `showcase_wc2022.mp4`, `possession_sample.mp4`, `geometry_speed_sample.mp4` |

---

## 6. Limitaciones (para ser honestos en grupo y ante el profesor)

1. **Balón:** recall ~0.20–0.27 en val; posesión no es métrica oficial.
2. **IDs ByteTrack:** pueden saltar → reinicia distancia/nombre si el mapa es por ID.
3. **Homografía:** fija por clip; la del tutorial no transfiere al WC sin recalibrar (y la del WC es aproximada).
4. **Nombres/dorsales:** sin OCR robusto; solo etiquetado manual parcial + equipo por color.
5. **Test set del detector:** muy pequeño (13 imgs) → métricas ruidosas.
6. **Videos YouTube/SoccerNet:** uso académico local; no redistribuir en el repo público.
7. **HU-9 `main.py` unificado / empaquetado formal:** parcialmente cubierto por `run_showcase.py`; README aún puede actualizarse.

---

## 7. Conclusión del experimento

El proyecto **cumple el objetivo de pipeline híbrido reproducible por módulos**, con evidencia cuantitativa (detector) y cualitativa (videos). Lo correcto académicamente es presentar **fortalezas (jugadores/equipos/geometría en clip calibrado)** y **límites (balón, identidad, H en broadcast)** en lugar de forzar overlays engañosos.

---

## 8. Próximos pasos opcionales (si sobra tiempo)

- Retrain con más frames de balón / imgsz mayor.
- OCR de dorsales o re-ID ligero.
- Homografía por segmentos o landmarks automáticos.
- Cerrar HU-9/HU-10 (CLI única + sección de reproducibilidad en informe final).
- Cuando SoccerNet apruebe NDA: clip broadcast + metadata oficial.
