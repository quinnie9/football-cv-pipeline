#!/usr/bin/env bash
# Publica el backlog inicial como Issues en quinnie9/football-cv-pipeline
# Uso:
#   gh auth login
#   ./scripts/create_github_issues.sh

set -euo pipefail
REPO="quinnie9/football-cv-pipeline"
export PATH="/opt/homebrew/bin:$PATH"

if ! gh auth status >/dev/null 2>&1; then
  echo "No hay sesión de gh. Corre: gh auth login"
  exit 1
fi

echo "Creando labels..."
for label_color in \
  "epic:6f42c1" \
  "hu:0e8a16" \
  "P0:d73a4a" \
  "P1:e99695" \
  "P2:fef2c0" \
  "P3:cfd3d7" \
  "ml:1d76db" \
  "cv-geometry:5319e7" \
  "pipeline:fbca04" \
  "docs:0075ca" \
  "good-first-task:7057ff"
do
  name="${label_color%%:*}"
  color="${label_color##*:}"
  gh label create "$name" --repo "$REPO" --color "$color" 2>/dev/null || true
done

create_issue() {
  local title="$1"
  local labels="$2"
  local body="$3"
  gh issue create --repo "$REPO" --title "$title" --label "$labels" --body "$body"
}

echo "Creando épicas e HUs..."

create_issue "E0 — Fundación del proyecto" "epic,P0,pipeline" "$(cat <<'BODY'
## Épica
Setup de repo, entorno y video de trabajo.

## HUs hijas
- HU-0.1 Estructura del repositorio
- HU-0.2 Entorno reproducible
- HU-0.3 Video de trabajo

Ver `docs/BACKLOG.md`.
BODY
)"

create_issue "HU-0.1 — Estructura del repositorio" "hu,P0,pipeline,good-first-task" "$(cat <<'BODY'
**Como** integrante del proyecto
**Quiero** una estructura modular clara
**Para** implementar cada bloque sin mezclar responsabilidades.

### Criterios de aceptación
- [ ] Carpetas: `input_videos/`, `output_videos/`, `models/`, `stubs/`, módulos del pipeline
- [ ] README con propósito y stack (YOLO11 + ByteTrack + …)
- [ ] `.gitignore` adecuado (videos, venv, runs, stubs)

**Épica:** E0
BODY
)"

create_issue "HU-0.2 — Entorno reproducible" "hu,P0,pipeline,good-first-task" "$(cat <<'BODY'
**Como** desarrolladora
**Quiero** un entorno Python aislado con dependencias fijadas
**Para** entrenar e inferir de forma reproducible.

### Criterios de aceptación
- [ ] `requirements.txt` (+ lock opcional)
- [ ] Instrucciones venv
- [ ] Smoke test de imports (`cv2`, `ultralytics`, `supervision`)

**Épica:** E0
BODY
)"

create_issue "HU-0.3 — Video de trabajo" "hu,P0,docs" "$(cat <<'BODY'
**Como** analista
**Quiero** un clip autorizado y un sample corto
**Para** iterar rápido.

### Criterios de aceptación
- [ ] Origen/licencia documentados
- [ ] Sample 30–60 s
- [ ] Metadatos ffprobe (res, FPS, duración)

**Épica:** E0
BODY
)"

create_issue "E1 — Datos y etiquetado" "epic,P0,ml" "$(cat <<'BODY'
Dataset YOLO 4 clases + auditoría de labels.
HUs: 1.1, 1.2 — ver `docs/BACKLOG.md`.
BODY
)"

create_issue "HU-1.1 — Dataset YOLO con 4 clases" "hu,P0,ml" "$(cat <<'BODY'
**Como** ML engineer
**Quiero** dataset YOLO con `ball`, `goalkeeper`, `player`, `referee`
**Para** fine-tunear el detector.

### Criterios de aceptación
- [ ] Splits train/val/test + labels
- [ ] `data.yaml` correcto
- [ ] Origen/licencia documentados

**Épica:** E1
BODY
)"

create_issue "HU-1.2 — Auditoría de calidad de labels" "hu,P0,ml,docs" "$(cat <<'BODY'
**Como** responsable de datos
**Quiero** revisar una muestra de etiquetas
**Para** no entrenar sobre errores sistemáticos.

### Criterios de aceptación
- [ ] Revisión muestreada train/val
- [ ] Lista de problemas y decisiones
- [ ] Nota sobre fuga train/test por partido

**Épica:** E1
BODY
)"

create_issue "E2 — Detección YOLO11" "epic,P0,ml" "$(cat <<'BODY'
Baseline, train YOLO11, evaluación y experimento A'.
HUs: 2.1–2.4 — ver `docs/BACKLOG.md`.
BODY
)"

create_issue "HU-2.1 — Baseline genérico" "hu,P0,ml" "$(cat <<'BODY'
**Como** investigadora
**Quiero** correr YOLO11n COCO (u equivalente genérico) sobre el sample
**Para** medir el gap pre fine-tuning.

### Criterios de aceptación
- [ ] Predict documentado
- [ ] Salida guardada
- [ ] Notas cualitativas (balón, clases)

**Épica:** E2
BODY
)"

create_issue "HU-2.2 — Entrenar YOLO11 fine-tuned" "hu,P0,ml" "$(cat <<'BODY'
**Como** ML engineer
**Quiero** entrenar YOLO11 con nuestro dataset
**Para** obtener pesos propios (`models/best_yolov11n.pt`).

### Criterios de aceptación
- [ ] Hiperparámetros y seed registrados
- [ ] `best.pt` accesible / versionado
- [ ] Curvas y métricas val exportadas

**Épica:** E2
BODY
)"

create_issue "HU-2.3 — Evaluación del detector" "hu,P0,ml" "$(cat <<'BODY'
**Como** analista
**Quiero** métricas test + inspección visual
**Para** decidir Go/No-go hacia tracking.

### Criterios de aceptación
- [ ] mAP50 / mAP50-95 + foco recall balón
- [ ] Matriz de confusión revisada
- [ ] Decisión Go/No-go documentada

**Épica:** E2
BODY
)"

create_issue "HU-2.4 — Experimento A' (genérico vs fine-tuned)" "hu,P2,ml,docs" "$(cat <<'BODY'
**Como** autora del informe
**Quiero** comparar baseline vs YOLO11 fine-tuned (opcional + YOLO8)
**Para** justificar la modernización con evidencia.

### Criterios de aceptación
- [ ] Mismo test set
- [ ] Tabla comparativa
- [ ] Ejemplos visuales de fallos/aciertos

**Épica:** E2
BODY
)"

create_issue "E3 — Tracking temporal" "epic,P0,pipeline" "$(cat <<'BODY'
ByteTrack + stubs. HUs: 3.1, 3.2.
BODY
)"

create_issue "HU-3.1 — ByteTrack sobre detecciones" "hu,P0,pipeline" "$(cat <<'BODY'
**Como** desarrolladora
**Quiero** IDs temporales estables
**Para** trayectorias y métricas por entidad.

### Criterios de aceptación
- [ ] YOLO11 → supervision → ByteTrack
- [ ] Regla goalkeeper→player documentada si aplica
- [ ] Video con IDs; ID switches anotados

**Épica:** E3
BODY
)"

create_issue "HU-3.2 — Caché de tracks (stubs)" "hu,P1,pipeline" "$(cat <<'BODY'
**Como** desarrolladora
**Quiero** persistir tracks
**Para** no re-inferir en cada iteración.

### Criterios de aceptación
- [ ] save/load stub + flag
- [ ] Metadatos video/modelo/conf
- [ ] Nota de seguridad pickle

**Épica:** E3
BODY
)"

create_issue "E4 — Equipos por color" "epic,P1,pipeline" "$(cat <<'BODY'
K-Means camisetas. HU-4.1.
BODY
)"

create_issue "HU-4.1 — Asignación de equipo con K-Means" "hu,P1,pipeline" "$(cat <<'BODY'
**Como** analista
**Quiero** asignar tracks a equipo 1/2 por color
**Para** anotaciones y posesión por equipo.

### Criterios de aceptación
- [ ] Torso + K-Means
- [ ] Clustering a nivel tracks
- [ ] Validación visual + fallos conocidos

**Épica:** E4
BODY
)"

create_issue "E5 — Posesión" "epic,P1,pipeline" "$(cat <<'BODY'
Heurística de proximidad. HU-5.1.
BODY
)"

create_issue "HU-5.1 — Posesión por proximidad" "hu,P1,pipeline" "$(cat <<'BODY'
**Como** analista
**Quiero** % de posesión aproximada por equipo
**Para** enriquecer el análisis del clip.

### Criterios de aceptación
- [ ] Umbral documentado
- [ ] % + frames sin asignación
- [ ] Overlay + disclaimer (no posesión oficial)

**Épica:** E5
BODY
)"

create_issue "E6 — Movimiento de cámara" "epic,P1,cv-geometry" "$(cat <<'BODY'
Optical flow / compensación. HU-6.1.
BODY
)"

create_issue "HU-6.1 — Estimar y compensar paneo" "hu,P1,cv-geometry" "$(cat <<'BODY'
**Como** analista
**Quiero** corregir movimiento de cámara
**Para** no inflar desplazamientos de jugadores.

### Criterios de aceptación
- [ ] Optical flow (o afín robusta)
- [ ] Tracks ajustados
- [ ] Validación en tramo con paneo

**Épica:** E6
BODY
)"

create_issue "E7 — Calibración / homografía" "epic,P0,cv-geometry" "$(cat <<'BODY'
Homografía propia. HUs: 7.1, 7.2.
BODY
)"

create_issue "HU-7.1 — Calibrar plano del campo" "hu,P0,cv-geometry" "$(cat <<'BODY'
**Como** analista
**Quiero** homografía propia del video
**Para** pasar de píxeles a metros.

### Criterios de aceptación
- [ ] ≥4 correspondencias reales documentadas
- [ ] H en repo o puntos + código
- [ ] Error vs distancia conocida reportado

**Épica:** E7
BODY
)"

create_issue "HU-7.2 — Transformar trayectorias al plano" "hu,P0,cv-geometry" "$(cat <<'BODY'
**Como** desarrolladora
**Quiero** posiciones métricas por track
**Para** velocidad y distancia.

### Criterios de aceptación
- [ ] Transformar pies (no torso)
- [ ] Inspección plot/csv

**Épica:** E7
BODY
)"

create_issue "E8 — Velocidad y distancia" "epic,P1,pipeline" "$(cat <<'BODY'
Cinemática. HU-8.1.
BODY
)"

create_issue "HU-8.1 — Métricas de movimiento" "hu,P1,pipeline" "$(cat <<'BODY'
**Como** analista
**Quiero** distancia (m) y velocidad (km/h) por jugador
**Para** el video anotado y el informe.

### Criterios de aceptación
- [ ] Δt según FPS real
- [ ] Filtro de saltos documentado
- [ ] Overlay + rangos plausibles

**Épica:** E8
BODY
)"

create_issue "E9 — Integración y entrega" "epic,P0,pipeline" "$(cat <<'BODY'
main/CLI + reproducibilidad. HUs: 9.1, 9.2.
BODY
)"

create_issue "HU-9.1 — Pipeline end-to-end" "hu,P0,pipeline" "$(cat <<'BODY'
**Como** usuaria del repo
**Quiero** un entrypoint que corra todo el pipeline
**Para** reproducir el experimento.

### Criterios de aceptación
- [ ] Un comando → video en `output_videos/`
- [ ] Orden de módulos documentado
- [ ] Check duración/FPS

**Épica:** E9
BODY
)"

create_issue "HU-9.2 — Empaquetado reproducible" "hu,P1,docs" "$(cat <<'BODY'
**Como** revisora
**Quiero** instrucciones claras de reproducción
**Para** que otra persona repita el flujo.

### Criterios de aceptación
- [ ] README pasos 1…N
- [ ] Artefactos esperados listados

**Épica:** E9
BODY
)"

create_issue "E10 — Informe y extensión" "epic,P2,docs" "$(cat <<'BODY'
Protocolo experimental + backlog opcional. HUs: 10.1, 10.2.
BODY
)"

create_issue "HU-10.1 — Protocolo experimental documentado" "hu,P2,docs" "$(cat <<'BODY'
**Como** autora académica
**Quiero** registrar hardware, versiones, semillas y limitaciones
**Para** un informe trazable.

### Criterios de aceptación
- [ ] Docs de reproducibilidad
- [ ] Limitaciones explícitas

**Épica:** E10
BODY
)"

create_issue "HU-10.2 — Extensiones opcionales" "hu,P3,docs" "$(cat <<'BODY'
**Como** investigadora
**Quiero** un backlog de mejoras no bloqueantes
**Para** priorizar si sobra tiempo.

### Ideas
- [ ] Otro tracker
- [ ] Mejor asignación de equipos
- [ ] H por segmento
- [ ] YOLO11s/m vs n

**Épica:** E10
BODY
)"

echo "Listo. Issues en: https://github.com/$REPO/issues"
