"""Stage 2: wall mask -> vector polygons (Shapely)."""
import cv2
from shapely.geometry import Polygon
from shapely.ops import unary_union

def mask_to_polygons(mask, epsilon_px=1.5, min_area_px=40):
    cnts, hier = cv2.findContours(mask, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)
    if hier is None:
        return []
    hier, polys = hier[0], []
    for i, c in enumerate(cnts):
        if hier[i][3] != -1 or cv2.contourArea(c) < min_area_px:
            continue
        outer = cv2.approxPolyDP(c, epsilon_px, True)[:, 0, :]
        if len(outer) < 3:
            continue
        holes, j = [], hier[i][2]
        while j != -1:
            h = cv2.approxPolyDP(cnts[j], epsilon_px, True)[:, 0, :]
            if len(h) >= 3:
                holes.append(h)
            j = hier[j][0]
        p = Polygon(outer, holes)
        p = p if p.is_valid else p.buffer(0)
        if not p.is_empty:
            polys.append(p)
    return polys

def wall_summary(polys, px_per_m):
    u = unary_union(polys) if polys else None
    return {"wall_segments": len(polys), "wall_area_m2": round(u.area / px_per_m ** 2, 2) if u else 0.0}
