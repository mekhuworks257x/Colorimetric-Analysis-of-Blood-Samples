import cv2
import math
import numpy as np
from sklearn.cluster import DBSCAN

# ==== CONSTANTS (matching reference notebook) ====
INNER_SCALE = 0.72      # MUST match reference (was incorrectly changed to 0.65)
MIN_BLOB_AREA = 60      # Minimum blob area filter
EXPECTED_COLS = 12      # Expected wells per row (6x12 well plate = 72 wells total)

# ==== UTILITY FUNCTIONS ====

def to_hsv(img_bgr):
    return cv2.cvtColor(img_bgr, cv2.COLOR_BGR2HSV)

def mask_from_hsv(hsv, s_thresh=30, v_thresh=30):
    """Create mask from HSV saturation and value channels"""
    s = hsv[:,:,1]
    v = hsv[:,:,2]
    return ((s > s_thresh) & (v > v_thresh)).astype(np.uint8) * 255

def morphological_clean(mask, open_k=3, close_k=5):
    """Apply morphological open and close operations"""
    ko = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (open_k,open_k))
    kc = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (close_k,close_k))
    m_open = cv2.morphologyEx(mask, cv2.MORPH_OPEN, ko, iterations=1)
    m_close = cv2.morphologyEx(m_open, cv2.MORPH_CLOSE, kc, iterations=1)
    return m_close

def contours_to_circles(contours, area_min=MIN_BLOB_AREA, circ_min=0.3):
    """Convert contours to circular blobs with area and circularity filters"""
    blobs = []
    for c in contours:
        area = cv2.contourArea(c)
        if area < area_min:
            continue
        peri = cv2.arcLength(c, True)
        if peri == 0:
            continue
        circ = 4 * math.pi * area / (peri * peri)
        if circ < circ_min:
            continue
        (x,y), r = cv2.minEnclosingCircle(c)
        blobs.append((int(x), int(y), int(r)))
    return sorted(blobs, key=lambda b: b[0])

def hough_fallback(img, dp=1.2, minDist=24, param1=80, param2=26, minR=12, maxR=60):
    """Hough circle detection fallback if contour-based method finds too few"""
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5,5), 1.2)
    circles = cv2.HoughCircles(
        blur, cv2.HOUGH_GRADIENT,
        dp=dp, minDist=minDist,
        param1=param1, param2=param2,
        minRadius=minR, maxRadius=maxR
    )
    if circles is None:
        return []
    return [(int(x),int(y),int(r)) for x,y,r in circles[0]]

def cluster_rows(blobs):
    """Cluster blobs into horizontal rows using Y coordinate DBSCAN"""
    if len(blobs) == 0:
        return []
    ys = np.array([b[1] for b in blobs]).reshape(-1,1)
    rs = np.array([b[2] for b in blobs])
    eps = max(6.0, np.median(rs)) * 1.8
    labels = DBSCAN(eps=eps, min_samples=2).fit(ys).labels_

    rows = {}
    for lbl, blob in zip(labels, blobs):
        if lbl == -1:
            continue
        rows.setdefault(lbl, []).append(blob)

    return [sorted(v, key=lambda b: b[0])
            for k,v in sorted(rows.items(), key=lambda x: np.mean([b[1] for b in x[1]]))]

# ==== MAIN DETECTION FUNCTION ====

def detect_rows_and_wells(img):
    """Detect well plates: HSV mask -> contours -> blobs -> rows"""
    hsv = to_hsv(img)
    mask = mask_from_hsv(hsv, s_thresh=30, v_thresh=30)
    clean = morphological_clean(mask)

    contours, _ = cv2.findContours(clean, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    blobs = contours_to_circles(contours)

    # Hough fallback if we found too few
    if len(blobs) < EXPECTED_COLS:
        hough_blobs = hough_fallback(img)
        # Only add Hough circles if they don't duplicate existing blobs
        for hb in hough_blobs:
            hx, hy, hr = hb
            is_duplicate = False
            for b in blobs:
                if np.hypot(b[0]-hx, b[1]-hy) < 0.6*max(b[2], hr):
                    is_duplicate = True
                    break
            if not is_duplicate:
                blobs.append(hb)
    
    blobs = sorted(set(blobs), key=lambda b:(b[1], b[0]))
    return cluster_rows(blobs)
    if scale_factor > 1.0:
        blobs = [(int(x*scale_factor), int(y*scale_factor), int(r*scale_factor)) for x, y, r in blobs]
    
    blobs = sorted(set(blobs), key=lambda b:(b[1], b[0]))
    return cluster_rows(blobs)
