# Estructura de presentación técnica (ante el profesor)

**Duración sugerida:** 10–12 min + preguntas  
**Hilo conductor:** “Pipeline híbrido reproducible, con decisión Go/No-go y límites explícitos.”

Archivo compañero para el grupo: [`INFORME_GRUPO.md`](INFORME_GRUPO.md).

---

## Guion de diapositivas (12 slides)

### 1. Portada (30 s)
- Título: Pipeline CV híbrido para análisis de video de fútbol  
- Integrantes / curso / fecha  
- Una frase: detección YOLO11 + tracking + equipos + geometría métrica  

### 2. Problema y objetivo (45 s)
- **Problema:** del video broadcast a métricas útiles (quién, dónde, qué tan rápido).  
- **Objetivo:** pipeline modular offline, entrenamiento y calibración propios.  
- **No-objetivo:** producto broadcast-grade ni GPS oficial.  

### 3. Arquitectura (1 min) — slide diagrama
Mostrar el flujo:

`Video → YOLO11n → ByteTrack → K-Means teams → (posesión) → optical flow → Homografía → speed/distance → video`

Mencionar: cada bloque es un módulo verificable (HU).

### 4. Datos y plataformas (1 min)
| Qué | Dónde |
|-----|--------|
| Dataset 4 clases | Roboflow (CC BY 4.0) |
| Clip desarrollo | DFL shootout / `08fd33_4` |
| Train device | Mac MPS (Ultralytics + PyTorch) |
| Repo | GitHub |
| Extra | YouTube WC2022 + lineups fwc_games; SoccerNet NDA pending |

### 5. Detector — evidencia cuantitativa (1.5 min) **CLAVE**
Tabla val:

- player / GK / referee: fuertes (mAP50 ~0.84–0.98)  
- **ball: recall ~0.20, mAP50 ~0.25**  

Baseline: COCO solo `person` vs fine-tune con clases del deporte.  
**Decisión GO** documentada pese a balón débil.

*Qué decir:* “Medimos antes de encadenar el resto del pipeline.”

### 6. Tracking y equipos (1 min)
- ByteTrack → IDs temporales  
- K-Means color → 2 equipos  
- **Video evidencia:** tracking / teams (o tramo de `showcase_sample.mp4`)  

*Riesgo a mencionar:* ID switches.

### 7. Posesión — método y límite (1 min)
- Heurística proximidad balón–pies  
- Solo frames asignados (sin sticky engañoso)  
- Depende del balón → **limitación estructural**  
- Evidencia: `possession_sample.mp4` + nota de recall  

### 8. Geometría y métricas (1.5 min) **CLAVE**
- Optical flow compensa paneo  
- Homografía → metros en parche calibrado  
- Label: `X km/h` = velocidad ventana; `Y m` = distancia acumulada del **track ID**  
- Clamps anti-spikes (≤36 km/h)  
- Evidencia: `geometry_speed_sample.mp4` / `showcase_sample.mp4`  

*Frase útil:* “No es GPS; es proyección métrica bajo H fija.”

### 9. Experimento broadcast WC2022 (1 min)
- Motivación: lineups reales + plano táctico  
- Qué funcionó: equipos ARG/FRA, tracking  
- Qué no: balón fiable, nombres automáticos  
- Solución honesta: balón OFF; nombres solo mapa manual (ej. Molina #26)  
- Evidencia: `showcase_wc2022.mp4`  

### 10. Decisiones de diseño / ética académica (45 s)
- Preferimos **menos overlay falso** que métricas inventadas  
- Videos académicos locales; no redistribuir YouTube/SoccerNet en git  
- Limitaciones escritas en `docs/experiments/`  

### 11. Resultados / deliverables (45 s)
Checklist visual:
- [x] Pesos propios `best_yolov11n.pt`  
- [x] Módulos del pipeline  
- [x] Videos anotados  
- [x] Docs de experimentos + Go/No-go  
- [~] CLI unificada (`run_showcase.py`; `main.py` formal pendiente)  

### 12. Conclusiones y trabajo futuro (1 min)
**Conclusión:** pipeline híbrido viable para jugadores/equipos/geometría en clip calibrado; balón e identidad son el frontier.  

**Futuro:** más datos de balón / imgsz↑, OCR dorsales, H por segmentos, SoccerNet cuando haya acceso.

---

## Qué mostrar en pantalla (evidencias)

Orden sugerido de clips (30–40 s cada uno, o un montaje de 2 min):

1. **Detector GO** — frames o short del fine-tune vs COCO (si tienen).  
2. **`showcase_sample.mp4`** — demo principal (limpia).  
3. **`possession_sample.mp4`** — 10 s + verbalizar límite del balón.  
4. **`showcase_wc2022.mp4`** — 15 s: ARG/FRA + “nombres solo si dorsal legible”.  

Tablas a tener en una slide o handout: métricas val del detector (HU-2.3).

---

## Frases listas para el profesor

**Si pregunta “¿qué tan preciso es?”**  
> En jugadores el mAP50 de validación está ~0.98; el balón ~0.25. Por eso posesión no la vendemos como ground truth.

**Si pregunta “¿de dónde salen los metros?”**  
> Homografía de un trapezoide calibrado al plano del campo; distancia euclídea en metros entre posiciones de pie transformadas, acumulada por ID.

**Si pregunta “¿por qué no salen Messi/Mbappé en todos?”**  
> ByteTrack da IDs opacos; leer dorsales en plano táctico es poco fiable. Solo mapeamos IDs donde el número se ve; el resto es etiqueta de equipo.

**Si pregunta “¿reproducible?”**  
> Sí: repo, requirements, seeds de train, scripts por etapa, stubs, y notas en `docs/experiments/`.

**Si pregunta “¿qué falta?”**  
> Empaquetado `main.py` formal, mejorar balón con más datos, y OCR/re-ID para identidad.

---

## Preguntas difíciles — cómo responder

| Pregunta | Respuesta corta |
|----------|-----------------|
| ¿Overfitting al dataset Roboflow? | Posible; test set chico. Contrastamos en video DFL/WC y documentamos dominio shift. |
| ¿Por qué no DeepSORT / tracker X? | ByteTrack vía Ultralytics cubría el alcance; comparar trackers es extensión (HU-10.2). |
| ¿La posesión es “oficial”? | No. Heurística CV; frames sin balón = sin asignación. |
| ¿Licencias? | Roboflow CC BY; DFL clips CC0; WC YouTube solo uso académico local, no en git. |

---

## Reparto sugerido en el grupo

| Rol | Slide / bloque |
|-----|----------------|
| A — ML | Detector, train MPS, métricas GO |
| B — Tracking/equipos | ByteTrack + K-Means + video |
| C — Geometría | Cámara, H, speed/distance |
| D — Integración/límites | Showcase, WC, limitaciones, futuro |

---

## Checklist día de la presentación

- [ ] Abrir `showcase_sample.mp4` offline (no depender de red)  
- [ ] Tener la tabla mAP en una slide  
- [ ] Una slide solo de **Limitaciones** (suma puntos)  
- [ ] Repo link + `docs/INFORME_GRUPO.md` por si piden detalle  
- [ ] No prometer balón/nombres automáticos en la demo en vivo  
