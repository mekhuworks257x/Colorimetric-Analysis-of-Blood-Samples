from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import tempfile
import cv2
import numpy as np
from typing import List, Dict, Any

app = FastAPI(title="Color Strip Analyzer")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def rgb_to_hsv_np(r: np.ndarray, g: np.ndarray, b: np.ndarray):
    """Vectorized RGB(0-255) to HSV(0-1)."""
    r = r / 255.0
    g = g / 255.0
    b = b / 255.0

    cmax = np.max([r, g, b], axis=0)
    cmin = np.min([r, g, b], axis=0)
    diff = cmax - cmin

    h = np.zeros_like(cmax)
    # Avoid division by zero
    mask = diff != 0

    r_eq = (cmax == r) & mask
    g_eq = (cmax == g) & mask
    b_eq = (cmax == b) & mask

    h[r_eq] = ((g[r_eq] - b[r_eq]) / diff[r_eq]) % 6
    h[g_eq] = ((b[g_eq] - r[g_eq]) / diff[g_eq]) + 2
    h[b_eq] = ((r[b_eq] - g[b_eq]) / diff[b_eq]) + 4

    h = h / 6.0  # normalize to 0-1

    s = np.zeros_like(cmax)
    nonzero = cmax != 0
    s[nonzero] = diff[nonzero] / cmax[nonzero]
    v = cmax

    return h, s, v


def analyze_strip_image(img_bgr: np.ndarray) -> Dict[str, Any]:
    """
    Approximate the N.html workflow:
    - convert to HSV
    - threshold saturation/value to isolate colored pads
    - find circular blobs left-to-right
    - measure mean saturation per blob
    - map to fixed concentration list
    - fit simple polynomial curve and return data for graph.
    """
    # Parameters similar to N.html
    EXPECTED_COLS = 11
    CONCENTRATIONS = [0.5, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    SAT_THRESH = 35
    VAL_THRESH = 40
    MIN_BLOB_AREA = 60

    # Resize for consistency
    h0, w0 = img_bgr.shape[:2]
    scale = 800.0 / max(h0, w0)
    if scale < 1.0:
        img_bgr = cv2.resize(img_bgr, None, fx=scale, fy=scale, interpolation=cv2.INTER_AREA)

    hsv = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2HSV)
    H, S, V = cv2.split(hsv)

    # Threshold on S and V (similar to mask_from_hsv in N.html)
    mask = ((S > SAT_THRESH) & (V > VAL_THRESH)).astype("uint8") * 255

    # Morphological clean (approximation of morphological_clean)
    ko = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
    kc = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    mask_open = cv2.morphologyEx(mask, cv2.MORPH_OPEN, ko, iterations=1)
    mask_clean = cv2.morphologyEx(mask_open, cv2.MORPH_CLOSE, kc, iterations=1)

    # Find contours / blobs (similar to contours_from_mask + contours_to_circles)
    cnts, _ = cv2.findContours(mask_clean.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    blobs = []
    for c in cnts:
        area = cv2.contourArea(c)
        if area < 5:
            continue
        peri = cv2.arcLength(c, True)
        if peri == 0:
            continue
        circ = 4.0 * np.pi * area / (peri * peri)
        (x, y), r = cv2.minEnclosingCircle(c)
        if area >= MIN_BLOB_AREA and circ >= 0.3:
            blobs.append((int(x), int(y), int(round(r)), float(area), float(circ)))

    if not blobs:
        raise ValueError("No valid color pads detected on the strip.")

    # Sort left-to-right and keep EXPECTED_COLS nearest to center row
    blobs = sorted(blobs, key=lambda b: b[0])
    if len(blobs) > EXPECTED_COLS:
        # Choose the ones closest to the median y to avoid spurious detections
        ys = np.array([b[1] for b in blobs], dtype=float)
        median_y = np.median(ys)
        blobs = sorted(blobs, key=lambda b: abs(b[1] - median_y))[:EXPECTED_COLS]
        blobs = sorted(blobs, key=lambda b: b[0])

    # For each blob, measure mean saturation inside a slightly smaller circle
    h_img, w_img = S.shape
    means_s = []
    centers_x = []
    for (cx, cy, r, area, circ) in blobs:
        rr = max(1, int(r * 0.72))  # INNER_SCALE like N.html
        Y, X = np.ogrid[:h_img, :w_img]
        dist2 = (X - cx) ** 2 + (Y - cy) ** 2
        mask_circle = dist2 <= rr * rr
        s_vals = S[mask_circle]
        if s_vals.size == 0:
            means_s.append(0.0)
        else:
            means_s.append(float(np.mean(s_vals)))
        centers_x.append(cx)

    means_s = np.array(means_s, dtype=float)
    centers_x = np.array(centers_x, dtype=float)

    # Sort by x coordinate to align with increasing concentration
    order = np.argsort(centers_x)
    means_s = means_s[order]

    # Truncate or pad to length of EXPECTED_COLS/CONCENTRATIONS
    if len(means_s) > EXPECTED_COLS:
        means_s = means_s[:EXPECTED_COLS]
    elif len(means_s) < EXPECTED_COLS:
        # simple padding with NaN to show missing wells
        pad = np.full(EXPECTED_COLS - len(means_s), np.nan)
        means_s = np.concatenate([means_s, pad])

    x = np.array(CONCENTRATIONS, dtype=float)
    y = means_s

    # Filter out NaNs for fitting
    valid = ~np.isnan(y)
    if np.count_nonzero(valid) >= 2:
        # Fit simple linear regression (degree 1) as a baseline
        coeffs = np.polyfit(x[valid], y[valid], deg=1)
        poly = np.poly1d(coeffs)
        x_fit = np.linspace(x.min(), x.max(), 100)
        y_fit = poly(x_fit)

        # R^2
        y_pred = poly(x[valid])
        ss_res = np.sum((y[valid] - y_pred) ** 2)
        ss_tot = np.sum((y[valid] - np.mean(y[valid])) ** 2)
        r2 = 1 - ss_res / ss_tot if ss_tot > 0 else 0.0
    else:
        x_fit = x
        y_fit = y
        r2 = 0.0

    # Normalize y and y_fit to 0–1 range for convenience (optional)
    y_norm = (y - np.nanmin(y)) / (np.nanmax(y) - np.nanmin(y)) if np.nanmax(y) > np.nanmin(y) else y
    y_fit_norm = (y_fit - np.min(y_fit)) / (np.max(y_fit) - np.min(y_fit)) if np.max(y_fit) > np.min(y_fit) else y_fit

    return {
        "concentrations": x.tolist(),
        "mean_saturation": y.tolist(),
        "mean_saturation_normalized": y_norm.tolist(),
        "fit_x": x_fit.tolist(),
        "fit_y": y_fit.tolist(),
        "fit_y_normalized": y_fit_norm.tolist(),
        "r2": float(r2),
    }


@app.post("/analyze")
async def analyze(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        if not contents:
            return JSONResponse({"error": "Empty file"}, status_code=400)

        with tempfile.NamedTemporaryFile(suffix=".jpg") as tmp:
            tmp.write(contents)
            tmp.flush()
            img_bgr = cv2.imread(tmp.name)

        if img_bgr is None:
            return JSONResponse({"error": "Failed to decode image"}, status_code=400)

        result = analyze_strip_image(img_bgr)
        return JSONResponse(result)
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)


@app.get("/health")
def health():
    return {"status": "ok"}

