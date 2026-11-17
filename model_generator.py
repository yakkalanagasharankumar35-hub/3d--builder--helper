"""Stage 3: extrude wall polygons into a 3D building; export OBJ/GLB; Plotly preview."""
import os, numpy as np, trimesh
from shapely.geometry import MultiPolygon
from shapely.affinity import scale, translate
from shapely.ops import unary_union

def _to_m(poly, ppm, h_px):
    return scale(translate(poly, yoff=-h_px), xfact=1 / ppm, yfact=-1 / ppm, origin=(0, 0))  # y-down -> y-up

def _extrude(geom, height, z0=0.0):
    out = []
    for g in (geom.geoms if isinstance(geom, MultiPolygon) else [geom]):
        if g.is_empty or g.area < 1e-4:
            continue
        m = trimesh.creation.extrude_polygon(g, height); m.apply_translation([0, 0, z0]); out.append(m)
    return out

def build_building(polys, img_shape, px_per_m=50.0, wall_height=3.0, floors=1, slab=0.2, add_floor=True, add_roof=False):
    walls = unary_union([_to_m(p, px_per_m, img_shape[0]) for p in polys])
    foot = walls.convex_hull
    sc = trimesh.Scene()
    def add(ms, color, name):
        for k, m in enumerate(ms):
            m.visual.face_colors = color; sc.add_geometry(m, node_name=f"{name}_{k}")
    if add_floor:
        add(_extrude(foot, slab, -slab), [190, 190, 190, 255], "foundation")
    for f in range(floors):
        z0 = f * (wall_height + slab)
        add(_extrude(walls, wall_height, z0), [235, 228, 215, 255], f"walls_f{f}")
        if f < floors - 1:
            add(_extrude(foot, slab, z0 + wall_height), [170, 170, 170, 255], f"slab_f{f}")
    if add_roof:
        add(_extrude(foot, slab, floors * (wall_height + slab) - slab), [150, 80, 70, 255], "roof")
    sc.apply_transform(trimesh.transformations.rotation_matrix(-np.pi / 2, [1, 0, 0]))  # Z-up -> Y-up
    return sc

def export(scene, name, out_dir="outputs"):
    glb, obj = f"{out_dir}/glb/{name}.glb", f"{out_dir}/obj/{name}.obj"
    os.makedirs(os.path.dirname(glb), exist_ok=True); os.makedirs(os.path.dirname(obj), exist_ok=True)
    scene.export(glb); scene.dump(concatenate=True).export(obj)
    return glb, obj

def scene_to_plotly(scene):
    import plotly.graph_objects as go
    tr = []
    for g in scene.geometry.values():
        v, f = g.vertices, g.faces
        c = "rgb(%d,%d,%d)" % tuple(int(x) for x in g.visual.face_colors[0][:3])
        tr.append(go.Mesh3d(x=v[:, 0], y=-v[:, 2], z=v[:, 1], i=f[:, 0], j=f[:, 1], k=f[:, 2], color=c, flatshading=True,
                            lighting=dict(ambient=0.55, diffuse=0.8)))
    fig = go.Figure(tr)
    fig.update_layout(scene=dict(aspectmode="data", xaxis_title="X (m)", yaxis_title="Y (m)", zaxis_title="Height (m)"),
                      margin=dict(l=0, r=0, t=0, b=0), height=620, showlegend=False)
    return fig
