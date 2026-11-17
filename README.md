# Evolution of Architecture – 2D Blueprint to 3D Building

Upload a floor-plan image → walls & rooms are detected with OpenCV → wall polygons are extruded
into a 3D building (Trimesh) → interactive Plotly viewer → export **GLB / OBJ**.

## Setup (Windows PowerShell, Python 3.11 recommended)
```
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
streamlit run app.py
```
Open http://localhost:8501 and click **Use sample blueprint** or upload your own plan.

## Structure
- `app.py` – Streamlit UI
- `backend/blueprint_processor.py` – wall mask + room detection (OpenCV)
- `backend/wall_detection.py` – mask → vector polygons (Shapely)
- `backend/model_generator.py` – extrusion, GLB/OBJ export, Plotly viewer
- `utils/sample_blueprint.py` – synthetic demo plan

## Method & limitations
Detection uses classical computer vision (Otsu threshold + morphology), which works well on clean
black-on-white plans. Blueprints with heavy hatching or colour need the sidebar sliders, or a trained
**U-Net / YOLO** model (planned upgrade: drop weights in `models/` and replace `extract_walls`).
Doors/windows are treated as gaps in walls. Scale must be set manually (pixels per metre).
Output is conceptual visualisation only – not structurally verified or construction-ready.

## Future work
U-Net wall segmentation, YOLO door/window detection, Blender export, PDF input (PyMuPDF), BuildAI web platform.
