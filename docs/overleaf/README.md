# Overleaf — football-cv-pipeline

Dos documentos (pdfLaTeX), complementarios:

| Archivo | Formato | Contenido |
|---------|---------|-----------|
| `main.tex` | IEEE (IEEEtran) | Metodología, descartes, resultados, limitaciones, futuro, aplicaciones |
| `lab.tex` | Artículo normal (`article`) | **Guía de laboratorio:** herramientas, datasets, repo, protocolo, comandos, artefactos |

Abstract / intro / SOTA del artículo de grupo → compañeros.

## Cómo usarlo

**Opción A — Proyectos separados en Overleaf**  
- Artículo: upload `informe_football_cv_overleaf.zip`  
- Lab: upload `lab_football_cv_overleaf.zip`

**Opción B — Pegar en el Overleaf del grupo**  
Copiá las `\section{...}` que correspondan desde cada `.tex`.

## Regenerar ZIPs

```bash
cd docs/overleaf
zip -r informe_football_cv_overleaf.zip main.tex README.md
zip -r lab_football_cv_overleaf.zip lab.tex README.md
```

## Videos citados

https://github.com/quinnie9/football-cv-pipeline/releases/tag/demo-v2
