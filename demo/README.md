# Videos de demostración

**Release público:** https://github.com/quinnie9/football-cv-pipeline/releases/tag/demo-v2

Los MP4 no están en git (peso + licencias). Descárgalos del Release o genéralos en local con `scripts/run_*.py`.

| Archivo | Parte del pipeline | Contenido | Uso sugerido |
|---------|-------------------|-----------|--------------|
| `01_E3_tracking_equipos_wc2022.mp4` | Tracking + equipos | ByteTrack + K-Means (broadcast) | IDs y separación por color |
| `02_E5_posesion_DFL.mp4` | Posesión (exploratoria) | Heurística balón→jugador (DFL) | Método + límite del balón |
| `03_E6E7E8_camara_homografia_velocidad_DFL.mp4` | Cámara + H + speed | Optical flow, metros, km/h | Explicar métricas |
| `04_E9_showcase_integrado_DFL.mp4` | Showcase integrado | Pipeline completo (clip calibrado) | **Demo principal** |
| `05_EXT_showcase_wc2022.mp4` | Extensión broadcast | WC2022 + límites | Generalización |
| `06_EXT_showcase_soccernet_NDA.mp4` | Extensión NDA | SoccerNet | **No** redistribuir en release público |

Orden recomendado: `01` → `02` → `03` → **`04`** → (`05` opcional).
