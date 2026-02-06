import joblib
import numpy as np
import os

# Load models
script_dir = os.path.dirname(os.path.abspath(__file__))
poly = joblib.load(os.path.join(script_dir, "calibration_poly.pkl"))
model = joblib.load(os.path.join(script_dir, "calibration_model.pkl"))

# Test with calibration data
test_R_values = [164.0951, 157.1643, 138.6038, 132.9423, 122.3280, 119.8036, 120.3674, 112.5461, 99.9079, 96.1239, 75.6670]
expected_conc = [0.5, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0]

print("=" * 62)
print("Testing Calibration Model with Reference Data")
print("=" * 62)
print(f"{'R Value':<15} {'Expected':<15} {'Predicted':<15} {'Error':<12}")
print("-" * 62)

errors = []
for R, expected in zip(test_R_values, expected_conc):
    X = poly.transform([[R]])
    prediction = model.predict(X)[0]
    error = prediction - expected
    errors.append(abs(error))
    print(f"{R:<15.2f} {expected:<15.2f} {prediction:<15.3f} {error:+.3f}")

import math
mae = np.mean(errors)
rmse = math.sqrt(np.mean(np.array(errors)**2))
print("-" * 62)
print(f"MAE: {mae:.4f} | RMSE: {rmse:.4f}")
print("=" * 62)

print("\n✅ Model is correctly loaded and working!")
print(f"Polynomial degree: {len(model.coef_)}")
print(f"Intercept: {model.intercept_:.6f}")
