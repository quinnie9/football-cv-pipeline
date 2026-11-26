# football-cv-pipeline

Pipeline híbrido de análisis de video de fútbol:

- **Detección:** YOLO11 (Ultralytics), pesos propios
- **Tracking:** ByteTrack (`supervision`)
- **Equipos:** K-Means sobre color de camiseta
- **Posesión:** heurística de proximidad balón–jugador
- **Cámara:** flujo óptico (corrección de paneo)
- **Geometría:** homografía calibrada por nosotros
- **Métricas:** distancia (m) y velocidad (km/h)
- **Salida:** video anotado

Inspirado en tutoriales públicos de análisis con YOLO/OpenCV; implementación propia (enfoque híbrido), entrenamiento y calibración del proyecto.

## Estado

Backlog tipo historias de usuario en [`docs/BACKLOG.md`](docs/BACKLOG.md).  
Para publicar el backlog como Issues de GitHub: ver [`scripts/create_github_issues.sh`](scripts/create_github_issues.sh).

## Roadmap corto

1. Setup del repo y entorno  
2. Dataset + entrenamiento YOLO11  
3. Tracking → equipos → posesión  
4. Calibración + velocidad/distancia  
5. Experimentos (baseline vs YOLO11) e informe  

## Licencia / atribución

Documentar en el informe el material de referencia y las licencias del dataset/video usados.
