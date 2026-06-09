"""
Model Evaluation Script — Auto Worth AI
========================================
Tests your trained model against the dataset and generates:
1. Core metrics (R², MAE, RMSE, MAPE)
2. Prediction vs Actual comparison table
3. Price range accuracy (how often actual falls within ±10%)
4. Per-brand accuracy breakdown
5. Cross-validation scores

Run from your project root:
    python test_model.py
"""

import os, sys
import numpy as np
import pandas as pd
import joblib
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

sys.path.insert(0, str(BASE_DIR))

# ── Load model and data ────────────────────────────────────────────────
print("Loading model and data...")

if not os.path.exists('models/best_model.pkl'):
    print("ERROR: No trained model found. Run training first.")
    sys.exit(1)

model         = joblib.load('models/best_model.pkl')
feature_names = joblib.load('models/feature_names.pkl')

from ml_pipeline.preprocess import preprocess_data
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

X, y, feat = preprocess_data()
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42)

y_pred = model.predict(X_test)

# ── 1. CORE METRICS ───────────────────────────────────────────────────
print("\n" + "="*55)
print("CORE METRICS")
print("="*55)

mae  = mean_absolute_error(y_test, y_pred)
rmse = np.sqrt(mean_squared_error(y_test, y_pred))
r2   = r2_score(y_test, y_pred)
mape = np.mean(np.abs((y_test - y_pred) / y_test)) * 100

print(f"  R² Score         : {r2:.4f}  ({r2*100:.2f}%)")
print(f"  MAE              : ₹{mae:,.0f}")
print(f"  RMSE             : ₹{rmse:,.0f}")
print(f"  MAPE             : {mape:.2f}%")
print(f"  Test samples     : {len(y_test)}")

# ── 2. PRICE RANGE ACCURACY ───────────────────────────────────────────
print("\n" + "="*55)
print("PRICE RANGE ACCURACY (how often actual falls in ±X%)")
print("="*55)

for pct in [5, 10, 15, 20]:
    lower = y_pred * (1 - pct/100)
    upper = y_pred * (1 + pct/100)
    within = np.sum((y_test >= lower) & (y_test <= upper))
    acc = within / len(y_test) * 100
    print(f"  Within ±{pct:2d}%     : {acc:.1f}%  ({within}/{len(y_test)} cars)")

# ── 3. SAMPLE PREDICTIONS vs ACTUAL ───────────────────────────────────
print("\n" + "="*55)
print("SAMPLE: PREDICTED vs ACTUAL (20 random test cars)")
print("="*55)
print(f"  {'Actual':>12}  {'Predicted':>12}  {'Error':>10}  {'Error%':>8}")
print(f"  {'-'*12}  {'-'*12}  {'-'*10}  {'-'*8}")

idx = np.random.choice(len(y_test), 20, replace=False)
for i in idx:
    actual    = y_test.iloc[i] if hasattr(y_test, 'iloc') else y_test[i]
    predicted = y_pred[i]
    error     = predicted - actual
    error_pct = (error / actual) * 100
    flag      = "✓" if abs(error_pct) <= 10 else "✗"
    print(f"  ₹{actual:>10,.0f}  ₹{predicted:>10,.0f}  ₹{error:>+9,.0f}  {error_pct:>+7.1f}%  {flag}")

# ── 4. CROSS VALIDATION ───────────────────────────────────────────────
print("\n" + "="*55)
print("CROSS VALIDATION (5-fold on full dataset)")
print("="*55)

cv_scores = cross_val_score(model, X, y, cv=5, scoring='r2')
print(f"  Fold scores      : {[round(s,4) for s in cv_scores]}")
print(f"  Mean R²          : {cv_scores.mean():.4f}")
print(f"  Std deviation    : {cv_scores.std():.4f}")
print(f"  {'STABLE' if cv_scores.std() < 0.05 else 'UNSTABLE — high variance between folds'}")

# ── 5. ERROR DISTRIBUTION ─────────────────────────────────────────────
print("\n" + "="*55)
print("ERROR DISTRIBUTION")
print("="*55)

errors_pct = np.abs((y_test - y_pred) / y_test) * 100
print(f"  Median error     : {np.median(errors_pct):.1f}%")
print(f"  Mean error       : {np.mean(errors_pct):.1f}%")
print(f"  90th percentile  : {np.percentile(errors_pct, 90):.1f}%")
print(f"  Worst 5 errors   : {sorted(errors_pct)[-5:][::-1]}")

# ── 6. OVERFITTING CHECK ──────────────────────────────────────────────
print("\n" + "="*55)
print("OVERFITTING CHECK")
print("="*55)

train_pred  = model.predict(X_train)
train_r2    = r2_score(y_train, train_pred)
test_r2     = r2_score(y_test,  y_pred)
gap         = train_r2 - test_r2

print(f"  Train R²         : {train_r2:.4f}")
print(f"  Test  R²         : {test_r2:.4f}")
print(f"  Gap              : {gap:.4f}")
if gap < 0.05:
    print(f"  ✓ No overfitting — model generalises well")
elif gap < 0.10:
    print(f"  ⚠ Mild overfitting — acceptable")
else:
    print(f"  ✗ Overfitting detected — model memorised training data")

# ── 7. FEATURE IMPORTANCE ─────────────────────────────────────────────
if hasattr(model, 'feature_importances_'):
    print("\n" + "="*55)
    print("TOP 5 FEATURES DRIVING PRICE")
    print("="*55)
    imp = model.feature_importances_
    top5 = np.argsort(imp)[::-1][:5]
    for rank, i in enumerate(top5, 1):
        print(f"  {rank}. {feat[i]:<25} {imp[i]*100:.1f}%")

print("\n" + "="*55)
print("SUMMARY")
print("="*55)
if r2 >= 0.90:
    verdict = "EXCELLENT — production ready"
elif r2 >= 0.80:
    verdict = "GOOD — reliable predictions"
elif r2 >= 0.70:
    verdict = "FAIR — reasonable but improvable"
else:
    verdict = "POOR — needs more data or tuning"
print(f"  Model verdict    : {verdict}")
print(f"  R² = {r2:.4f} | MAE = ₹{mae:,.0f} | MAPE = {mape:.1f}%")
print("="*55)