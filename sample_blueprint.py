"""Synthetic floor plan so the app can be demoed without a real blueprint."""
import os, cv2, numpy as np
def make_sample(path="samples/sample_plan.png"):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    img = np.full((600, 800, 3), 255, np.uint8); t = 10; k = (0, 0, 0)
    cv2.rectangle(img, (50, 50), (750, 550), k, t)
    cv2.line(img, (400, 50), (400, 330), k, t); cv2.line(img, (50, 330), (750, 330), k, t); cv2.line(img, (560, 330), (560, 550), k, t)
    for x0, x1, y in [(150, 230, 50), (250, 330, 330), (600, 680, 330)]:
        cv2.line(img, (x0, y), (x1, y), (255, 255, 255), t + 2)   # door/window openings
    cv2.imwrite(path, img); return path
if __name__ == "__main__": print(make_sample())
