# Backlog — football-cv-pipeline

Formato: **Épicas** → **Historias de usuario (HU)** con criterios de aceptación.  
Aunque el dominio es analítica/CV, las HU se redactan como capacidad entregable verificable.

**Convenciones**

| Campo | Significado |
|-------|-------------|
| ID | `E#` épica · `HU-#.#` historia |
| Prioridad | P0 bloqueante · P1 núcleo · P2 extensión · P3 nice-to-have |
| DoD mínimo | Criterios de aceptación cumplidos + evidencia (clip, métrica o captura) en el PR/issue |

**Orden de trabajo sugerido:** E0 → E1 → E2 → E3 → E4 → E5 → E6 → E7 → E8 → E9 → E10

---

## E0 — Fundación del proyecto (P0)

### HU-0.1 — Estructura del repositorio
**Como** integrante del proyecto  
**Quiero** una estructura modular clara (input/output, models, módulos del pipeline)  
**Para** implementar cada bloque sin mezclar responsabilidades.

**Criterios de aceptación**
- [ ] Existen carpetas: `input_videos/`, `output_videos/`, `models/`, `dataset/` (o docs de cómo montarlo), `stubs/`, y módulos (`trackers/`, `team_assigner/`, etc.) o equivalentes documentados.
- [ ] `README` describe propósito, stack (YOLO11 + ByteTrack + …) y cómo correr el entorno.
- [ ] `.gitignore` excluye videos pesados, pesos grandes opcionales, stubs, `.venv`, runs.

### HU-0.2 — Entorno reproducible
**Como** desarrolladora  
**Quiero** un entorno Python aislado con dependencias fijadas  
**Para** entrenar e inferir sin “en mi máquina funciona”.

**Criterios de aceptación**
- [ ] `requirements.txt` (y opcionalmente `requirements-lock.txt`) con ultralytics, supervision, opencv, numpy, scikit-learn, pandas, etc.
- [ ] Instrucciones para crear venv e instalar.
- [ ] Smoke test: import de `cv2`, `ultralytics`, `supervision` OK.

### HU-0.3 — Video de trabajo
**Como** analista  
**Quiero** un clip de entrada autorizado y un sample corto  
**Para** iterar rápido sin procesar partidos enteros.

**Criterios de aceptación**
- [ ] Video fuente documentado (origen/licencia) en `input_videos/` o instrucciones de descarga.
- [ ] Sample de 30–60 s generado (p. ej. con ffmpeg) y usado como default de desarrollo.
- [ ] `ffprobe` documenta resolución, FPS y duración del sample.

---

## E1 — Datos y etiquetado (P0)

### HU-1.1 — Dataset YOLO con 4 clases
**Como** ML engineer  
**Quiero** un dataset en formato YOLO con clases `ball`, `goalkeeper`, `player`, `referee`  
**Para** fine-tunear el detector del dominio.

**Criterios de aceptación**
- [ ] Estructura `images/{train,val,test}` + `labels/{train,val,test}`.
- [ ] `data.yaml` con `path`, splits y `names` en orden correcto.
- [ ] Origen y licencia del dataset documentados.

### HU-1.2 — Auditoría de calidad de labels
**Como** responsable de datos  
**Quiero** revisar una muestra de etiquetas a mano  
**Para** no entrenar sobre errores sistemáticos.

**Criterios de aceptación**
- [ ] Revisión de ≥20–30 imágenes train y ≥15–20 val (checklist en el issue).
- [ ] Lista de problemas encontrados (balón sin label, público como player, etc.) y decisión (fix / aceptar / excluir).
- [ ] Confirmación de que train/val/test no filtran el mismo partido de forma ingenua (o se documenta la limitación).

---

## E2 — Detección YOLO11 (P0)

### HU-2.1 — Baseline genérico
**Como** investigadora  
**Quiero** correr un detector genérico (p. ej. YOLO11n COCO) sobre el sample  
**Para** cuantificar el gap antes del fine-tuning.

**Criterios de aceptación**
- [ ] Comando/script de predict documentado.
- [ ] Video o frames de salida guardados bajo `runs/` u `output_videos/`.
- [ ] Notas cualitativas: balón, personas, clases no deportivas.

### HU-2.2 — Entrenar YOLO11 fine-tuned
**Como** ML engineer  
**Quiero** entrenar YOLO11 con nuestro `data.yaml`  
**Para** obtener `models/best_yolov11n.pt` (o equivalente) propio.

**Criterios de aceptación**
- [ ] Entrenamiento reproducible (seed, epochs, imgsz, batch, device) registrado.
- [ ] `best.pt` versionado o instrucciones claras de dónde está (Drive/LFS/release).
- [ ] Curvas train/val y métricas val exportadas (csv/png).

### HU-2.3 — Evaluación del detector
**Como** analista  
**Quiero** métricas en test + inspección visual  
**Para** decidir si el detector es usable para el pipeline.

**Criterios de aceptación**
- [ ] mAP50, mAP50-95 y énfasis en **recall/mAP del ball**.
- [ ] Matriz de confusión revisada (player↔referee, player↔goalkeeper).
- [ ] Go / No-go documentado para pasar a tracking.

### HU-2.4 — Experimento A': genérico vs fine-tuned (y opcional v8)
**Como** autora del informe  
**Quiero** comparar baseline vs YOLO11 fine-tuned (opcional: también un YOLO8 fine-tuned)  
**Para** justificar la modernización con evidencia.

**Criterios de aceptación**
- [ ] Misma partición de test para todos los modelos.
- [ ] Tabla comparativa (mAP, recall balón, tiempo/frame aproximado).
- [ ] 2–3 ejemplos visuales de aciertos/fallos.

---

## E3 — Tracking temporal (P0)

### HU-3.1 — ByteTrack sobre detecciones
**Como** desarrolladora  
**Quiero** IDs temporales estables por jugador/árbitro  
**Para** acumular trayectorias y métricas por entidad.

**Criterios de aceptación**
- [ ] Módulo tracker: YOLO11 → `sv.Detections` → ByteTrack.
- [ ] Goalkeeper unificado a player para tracking si se adopta esa regla del tutorial.
- [ ] Video con IDs dibujados; se documentan ID switches obvios en un clip de prueba.

### HU-3.2 — Caché de tracks (stubs)
**Como** desarrolladora  
**Quiero** persistir tracks intermedios  
**Para** no re-inferir en cada iteración de visualización/estadística.

**Criterios de aceptación**
- [ ] Guardar/cargar stub (p. ej. pickle) con flag `read_from_stub`.
- [ ] Metadatos mínimos documentados: video usado, modelo, conf.
- [ ] Advertencia de seguridad: no cargar pickles de fuentes desconocidas.

---

## E4 — Equipos por color (P1)

### HU-4.1 — Asignación de equipo con K-Means
**Como** analista  
**Quiero** asignar cada track de jugador a equipo 1 o 2 según camiseta  
**Para** colorear anotaciones y calcular posesión por equipo.

**Criterios de aceptación**
- [ ] Recorte torso + K-Means(2) para color representativo.
- [ ] Segundo clustering a nivel tracks → 2 equipos.
- [ ] Video/frames donde los colores de equipo se ven coherentes; fallos conocidos listados.

---

## E5 — Posesión (P1)

### HU-5.1 — Posesión por proximidad
**Como** analista  
**Quiero** estimar qué equipo “tiene” el balón por frame  
**Para** reportar % de posesión aproximada en el clip.

**Criterios de aceptación**
- [ ] Distancia balón ↔ pies del jugador con umbral documentado.
- [ ] Acumulación de % equipo 1 / 2 y frames sin asignación (si aplica).
- [ ] Overlay en video; nota explícita de que no es posesión oficial.

---

## E6 — Movimiento de cámara (P1)

### HU-6.1 — Estimar y compensar paneo
**Como** analista  
**Quiero** corregir el desplazamiento inducido por la cámara  
**Para** no inflar movimiento de jugadores quietos en el campo.

**Criterios de aceptación**
- [ ] Optical flow (goodFeaturesToTrack + Lucas–Kanade o afín robusta).
- [ ] Posiciones de tracks ajustadas por movimiento de cámara.
- [ ] Validación cualitativa en un tramo con paneo.

---

## E7 — Calibración / homografía (P0 para métricas métricas)

### HU-7.1 — Calibrar plano del campo
**Como** analista  
**Quiero** una homografía propia del video de trabajo  
**Para** transformar pies de jugadores a coordenadas en metros.

**Criterios de aceptación**
- [ ] ≥4 correspondencias imagen ↔ metros documentadas (no puntos de ejemplo del informe genérico).
- [ ] Matriz H versionada o código + puntos en repo.
- [ ] Chequeo con una distancia conocida del campo (error reportado).

### HU-7.2 — Transformar trayectorias al plano
**Como** desarrolladora  
**Quiero** posiciones métricas por track  
**Para** alimentar velocidad y distancia.

**Criterios de aceptación**
- [ ] Se transforma el punto de pies, no el centro del torso.
- [ ] Trayectorias en plano se pueden inspeccionar (plot o dump csv).

---

## E8 — Velocidad y distancia (P1)

### HU-8.1 — Métricas de movimiento
**Como** analista  
**Quiero** distancia acumulada (m) y velocidad (km/h) por jugador  
**Para** enriquecer el video y el informe.

**Criterios de aceptación**
- [ ] Cálculo con Δt del FPS real del video.
- [ ] Suavizado o filtro de saltos no plausibles documentado.
- [ ] Overlay legible; rangos revisados a ojo (sin velocidades absurdas sistemáticas).

---

## E9 — Integración y entrega (P0)

### HU-9.1 — Pipeline end-to-end
**Como** usuaria del repo  
**Quiero** un `main.py` (o CLI) que ejecute el pipeline completo  
**Para** reproducir el experimento de punta a punta.

**Criterios de aceptación**
- [ ] Un comando genera el video anotado en `output_videos/`.
- [ ] Orden de módulos documentado y coherente con la arquitectura.
- [ ] Duración/FPS de salida verificados vs entrada (o diferencias explicadas).

### HU-9.2 — Empaquetado reproducible del experimento
**Como** revisora  
**Quiero** instrucciones claras de reproducción  
**Para** que otra persona pueda repetir el flujo principal.

**Criterios de aceptación**
- [ ] README con pasos 1…N (datos, train o descarga de pesos, inferencia, calibración).
- [ ] Lista de artefactos esperados (best.pt, H, video salida, tablas).

---

## E10 — Informe y extensión (P2)

### HU-10.1 — Protocolo experimental documentado
**Como** autora académica  
**Quiero** registrar hardware, versiones, semillas, splits y limitaciones  
**Para** un informe trazable.

**Criterios de aceptación**
- [ ] Sección de reproducibilidad en `docs/` o informe.
- [ ] Limitaciones explícitas (posesión heurística, IDs temporales, H fija, etc.).

### HU-10.2 — Extensiones opcionales
**Como** investigadora  
**Quiero** backlog de mejoras no bloqueantes  
**Para** priorizar si sobra tiempo.

**Ideas (no compromiso)**
- [ ] Comparar ByteTrack vs otro tracker.
- [ ] Mejorar asignación de equipos (temporal / embeddings).
- [ ] Homografía por segmento si cambia el encuadre.
- [ ] YOLO11s/m vs n (coste/beneficio).

---

## Tablero sugerido (labels)

| Label | Uso |
|-------|-----|
| `epic` | Épica |
| `hu` | Historia de usuario |
| `P0` / `P1` / `P2` / `P3` | Prioridad |
| `ml` | Entrenamiento / datos |
| `cv-geometry` | Cámara / homografía |
| `pipeline` | Integración código |
| `docs` | Documentación / informe |
| `good-first-task` | Ideal para primera sesión con el agente |

## Primera tanda para ejecutar con Cursor Agent

1. HU-0.1, HU-0.2, HU-0.3  
2. HU-1.1, HU-1.2  
3. HU-2.1 → HU-2.2 → HU-2.3  
4. HU-3.1  
5. …siguiente módulo solo cuando el anterior tenga evidencia
