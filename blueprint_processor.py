"""Stage 1: load blueprint image and extract wall mask + rooms (classical CV)."""
import cv2, numpy as np
from PIL import Image

def load_image(file) -> np.ndarray:
    arr = np.array(Image.open(file).convert("RGB"))
    h, w = arr.shape[:2]
    if max(h, w) > 1600:
        s = 1600 / max(h, w)
        arr = cv2.resize(arr, (int(w * s), int(h * s)), interpolation=cv2.INTER_AREA)
    return arr

def extract_walls(rgb, min_thickness=3, sensitivity=0):
    """Binary wall mask (255 = wall): dark, thick strokes."""
    gray = cv2.GaussianBlur(cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY), (3, 3), 0)
    if sensitivity:
        _, mask = cv2.threshold(gray, 127 + sensitivity, 255, cv2.THRESH_BINARY_INV)
    else:
        _, mask = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    k = cv2.getStructuringElement(cv2.MORPH_RECT, (min_thickness, min_thickness))
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, k)   # remove thin text/dimension lines
    return cv2.morphologyEx(mask, cv2.MORPH_CLOSE, k)

def detect_rooms(wall_mask, min_area_px=1500):
    """Enclosed free spaces = rooms."""
    n, _, stats, cents = cv2.connectedComponentsWithStats(cv2.bitwise_not(wall_mask), connectivity=4)
    h, w = wall_mask.shape
    rooms = []
    for i in range(1, n):
        x, y, bw, bh, area = stats[i]
        if area >= min_area_px and x > 0 and y > 0 and x + bw < w and y + bh < h:
            rooms.append({"area_px": int(area), "centroid": tuple(map(float, cents[i])), "bbox": (int(x), int(y), int(bw), int(bh))})
    rooms.sort(key=lambda r: -r["area_px"])
    for k, r in enumerate(rooms, 1):
        r["name"] = f"Room {k}"
    return rooms

def annotate(rgb, wall_mask, rooms, px_per_m):
    out = rgb.copy(); ov = out.copy(); ov[wall_mask > 0] = (220, 40, 40)
    out = cv2.addWeighted(ov, 0.6, out, 0.4, 0)
    for r in rooms:
        cx, cy = map(int, r["centroid"])
        cv2.putText(out, r["name"], (cx - 30, cy), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 90, 200), 2)
        cv2.putText(out, f'{r["area_px"] / px_per_m ** 2:.1f} m2', (cx - 30, cy + 18), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 120, 0), 1)
    return out
