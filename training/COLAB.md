# Train YOLO11 on Google Colab (HU-2.2)

## Steps

1. Open [Google Colab](https://colab.research.google.com/).
2. Upload `training/colab_train_yolo11.ipynb` (**File → Upload notebook**)  
   or push this repo to GitHub and `Open notebook` from GitHub.
3. **Runtime → Change runtime type → GPU (T4)**.
4. Add secret `ROBOFLOW_API_KEY` (🔑 Secrets panel) with your Roboflow private key.
5. Run all cells.
6. Download `best_yolov11n.pt` when prompted.
7. Save it locally as `models/best_yolov11n.pt`.

## Expected time

- Dataset download: ~1–2 min  
- Train 50 epochs, YOLO11n, imgsz=640, batch=16 on T4: often ~20–45 min (depends on queue/GPU)

## Tips

- If GPU is unavailable, wait or try again later; CPU training is too slow.
- If ball recall is weak after 50 epochs, re-run with `epochs=100` and/or `imgsz=1280` (more VRAM).
- Do **not** commit API keys or `.pt` weights to git.
