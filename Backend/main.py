from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
import numpy as np
import cv2

from well_detect import detect_rows_and_wells
from feature_extract import extract_R_values
from predict import predict_concentrations

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/analyze")
async def analyze(file: UploadFile = File(...)):
    # -------- READ IMAGE SAFELY (NO cv2.imread) --------
    image_bytes = await file.read()
    np_arr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

    if img is None:
        return {
            "error": "Failed to decode image. Unsupported format or corrupted file."
        }

    # -------- STEP 1: WELL DETECTION --------
    rows = detect_rows_and_wells(img)
    total_wells = sum(len(r) for r in rows)
    total_trials = len(rows)

    # -------- STEP 2: FEATURE EXTRACTION --------
    features = extract_R_values(img, rows)

    # -------- STEP 3: PREDICTION --------
    predictions = predict_concentrations(features)

    # -------- FINAL RESPONSE (CONSISTENT STRUCTURE) --------
    return {
        "steps": {
            "wells_detected": total_wells,
            "trials_detected": total_trials,
            "feature_type": "Mean Red Channel Intensity (inner well region)",
            "model": "Polynomial Regression (calibrated on reference image)"
        },
        "predictions": predictions
    }
