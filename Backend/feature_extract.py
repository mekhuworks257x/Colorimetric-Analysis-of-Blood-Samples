import cv2
import numpy as np

INNER_SCALE = 0.72

def extract_R_values(img, rows):
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    results = []

    for ridx, row in enumerate(rows, start=1):
        wells = []
        for (x,y,r) in row:
            inner_r = max(1, int(r * INNER_SCALE))
            mask = np.zeros(img.shape[:2], dtype=np.uint8)
            cv2.circle(mask, (x,y), inner_r, 255, -1)
            R = float(np.mean(img[:,:,2][mask==255]))
            wells.append(R)

        results.append({
            "trial": ridx,
            "R_values": wells
        })

    return results
