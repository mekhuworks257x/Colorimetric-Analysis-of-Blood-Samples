import cv2
import math
import numpy as np
from sklearn.cluster import DBSCAN

# ==== CONSTANTS (same as Colab) ====
INNER_SCALE = 0.72
MIN_BLOB_AREA = 60
EXPECTED_COLS = 12

# ==== UTILITY FUNCTIONS (from Cell 2) ====

def to_hsv(img_bgr):
    return cv2.cvtColor(img_bgr, cv2.COLOR_BGR2HSV)

def mask_from_hsv(hsv, s_thresh=30, v_thresh=30):
    s = hsv[:,:,1]
    v = hsv[:,:,2]
    return ((s > s_thresh) & (v > v_thresh)).astype(np.uint8) * 255

def morphological_clean(mask, open_k=3, close_k=5):
    ko = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (open_k,open_k))
    kc = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (close_k,close_k))
    m_open = cv2.morphologyEx(mask, cv2.MORPH_OPEN, ko, iterations=1)
    m_close = cv2.morphologyEx(m_open, cv2.MORPH_CLOSE, kc, iterations=1)
    return m_close

def contours_to_circles(contours, area_min=MIN_BLOB_AREA, circ_min=0.3):
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

def hough_fallback(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray,(5,5),1.2)
    
    # Optimize: Use faster Hough with relaxed parameters
    circles = cv2.HoughCircles(
        blur, cv2.HOUGH_GRADIENT,
        dp=2.0,  # Increased from 1.2 for faster processing
        minDist=24,
        param1=50,  # Reduced from 80
        param2=20,  # Reduced from 26
        minRadius=12, maxRadius=60
    )
    if circles is None:
        return []
    return [(int(x),int(y),int(r)) for x,y,r in circles[0]]

def cluster_rows(blobs):
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
    # Optimize: downscale image for faster processing
    original_height, original_width = img.shape[:2]
    scale_factor = 1.0
    
    # If image is very large, downscale it
    if original_width > 2000 or original_height > 2000:
        scale_factor = max(original_width, original_height) / 1500.0
        new_width = int(original_width / scale_factor)
        new_height = int(original_height / scale_factor)
        img = cv2.resize(img, (new_width, new_height), interpolation=cv2.INTER_AREA)
    
    hsv = to_hsv(img)
    mask = mask_from_hsv(hsv)
    clean = morphological_clean(mask)

    contours,_ = cv2.findContours(clean, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    blobs = contours_to_circles(contours)

    if len(blobs) < EXPECTED_COLS:
        blobs += hough_fallback(img)

    # Scale coordinates back if we downscaled
    if scale_factor > 1.0:
        blobs = [(int(x*scale_factor), int(y*scale_factor), int(r*scale_factor)) for x, y, r in blobs]
    
    blobs = sorted(set(blobs), key=lambda b:(b[1], b[0]))
    return cluster_rows(blobs)
