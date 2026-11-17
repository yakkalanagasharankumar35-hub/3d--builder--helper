dirimport streamlit as st, os, time
from backend.blueprint_processor import load_image, extract_walls, detect_rooms, annotate
from backend.wall_detection import mask_to_polygons, wall_summary
from backend.model_generator import build_building, export, scene_to_plotly
from utils.sample_blueprint import make_sample

st.set_page_config(page_title="Evolution of Architecture", page_icon="🏛️", layout="wide")
st.title("🏛️ Evolution of Architecture")
st.caption("2D Blueprint → AI/CV element detection → Interactive 3D building (OBJ / GLB export)")

with st.sidebar:
    st.header("Settings")
    px_per_m = st.number_input("Scale: pixels per metre", 5.0, 500.0, 50.0, 5.0,
                               help="Measure a known wall length in the image to set real-world scale.")
    wall_h = st.slider("Wall height (m)", 2.0, 5.0, 3.0, 0.1)
    floors = st.slider("Number of floors (stacked copy)", 1, 5, 1)
    thick = st.slider("Min wall thickness (px) – filters text/thin lines", 2, 15, 4)
    sens = st.slider("Threshold offset", -60, 60, 0)
    roof = st.checkbox("Add flat roof slab", False)
    st.info("Conceptual/educational visualisation only. Not a structural or construction-ready design.")

up = st.file_uploader("Upload a 2D floor plan (PNG/JPG)", type=["png", "jpg", "jpeg"])
use_sample = st.button("Use sample blueprint")
if use_sample:
    st.session_state["sample"] = make_sample()
src = up or st.session_state.get("sample")

if src:
    rgb = load_image(src)
    mask = extract_walls(rgb, thick, sens)
    rooms = detect_rooms(mask)
    polys = mask_to_polygons(mask)
    c1, c2, c3 = st.columns(3)
    c1.image(rgb, caption="Original blueprint", use_container_width=True)
    c2.image(mask, caption="Detected walls", use_container_width=True)
    c3.image(annotate(rgb, mask, rooms, px_per_m), caption="Walls + rooms", use_container_width=True)

    s = wall_summary(polys, px_per_m)
    m1, m2, m3 = st.columns(3)
    m1.metric("Rooms detected", len(rooms)); m2.metric("Wall segments", s["wall_segments"]); m3.metric("Wall area (m²)", s["wall_area_m2"])

    if not polys:
        st.error("No walls detected. Adjust thickness/threshold in the sidebar.")
    elif st.button("🏗️ Generate 3D building", type="primary"):
        with st.spinner("Building 3D model..."):
            scene = build_building(polys, rgb.shape, px_per_m, wall_h, floors, add_roof=roof)
            glb, obj = export(scene, f"building_{int(time.time())}")
        st.session_state["scene"], st.session_state["files"] = scene, (glb, obj)

    if "scene" in st.session_state:
        st.subheader("Interactive 3D model")
        st.plotly_chart(scene_to_plotly(st.session_state["scene"]), use_container_width=True)
        glb, obj = st.session_state["files"]
        d1, d2 = st.columns(2)
        d1.download_button("⬇ Download GLB", open(glb, "rb"), os.path.basename(glb))
        d2.download_button("⬇ Download OBJ", open(obj, "rb"), os.path.basename(obj))
else:
    st.info("Upload a floor plan or click **Use sample blueprint** to begin.")
