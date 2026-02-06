import cv2
import numpy as np

# Match reference notebook exactly
INNER_SCALE = 0.72

def extract_R_values(img, rows):
    """
    Extract R channel (red) values from each well's inner region.
    Matches the reference notebook approach exactly.
    """
    results = []

    for ridx, row in enumerate(rows, start=1):
        wells = []
        for (x, y, r) in row:
            # Extract inner well region using standard scale
            inner_r = max(1, int(r * INNER_SCALE))
            mask = np.zeros(img.shape[:2], dtype=np.uint8)
            cv2.circle(mask, (x, y), inner_r, 255, -1)
            
            # Get mean R value from inner region
            region_pixels = img[mask == 255]
            if len(region_pixels) > 0:
                # img is BGR, so channel 2 is R
                R = float(np.mean(region_pixels[:, 2]))
            else:
                R = 0.0
            
            wells.append(R)

        results.append({
            "trial": ridx,
            "R_values": wells
        })

    return results
