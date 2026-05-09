import os
import joblib
import pandas as pd
import numpy as np

# ─────────────────────────────────────────────
# Paths (relative to project root)
# ─────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_PATH = os.path.join(BASE_DIR, "models", "best_rf_model.pkl")
SOIL_CSV = os.path.join(BASE_DIR, "data", "region_soil_mapping_all_india.csv")
CLIMATE_CSV = os.path.join(BASE_DIR, "data", "region_climate_mapping_all_india.csv")

# ─────────────────────────────────────────────
# Load at module import (cached in memory)
# ─────────────────────────────────────────────
print("[AgriSen] Loading Random Forest model...")
MODEL = joblib.load(MODEL_PATH)
print(f"[AgriSen] Model loaded – classes: {list(MODEL.classes_)}")

print("[AgriSen] Loading soil & climate CSV datasets...")
SOIL_DF = pd.read_csv(SOIL_CSV).dropna()
CLIMATE_DF = pd.read_csv(CLIMATE_CSV).dropna()
# Normalise region/state names for matching
SOIL_DF["_region_key"] = SOIL_DF["State" if "State" in SOIL_DF.columns else "Region"].str.strip().str.lower().str.replace('_', ' ')
CLIMATE_DF["_region_key"] = CLIMATE_DF["State" if "State" in CLIMATE_DF.columns else "Region"].str.strip().str.lower().str.replace('_', ' ')
print(f"[AgriSen] Datasets loaded – soil: {len(SOIL_DF)} rows, climate: {len(CLIMATE_DF)} rows")

# Strict feature order required by the trained model
FEATURE_ORDER = ["N", "P", "K", "temperature", "humidity", "ph", "rainfall"]


def get_classes():
    return list(MODEL.classes_)


def predict(features: dict) -> tuple:
    """
    features: dict with keys matching FEATURE_ORDER
    Returns: (crop_label: str, confidence: float, prob_array: np.ndarray)
    """
    X = np.array([[features[f] for f in FEATURE_ORDER]])
    probabilities = MODEL.predict_proba(X)[0]
    pred_idx = int(np.argmax(probabilities))
    crop = MODEL.classes_[pred_idx]
    confidence = float(round(probabilities[pred_idx], 4))
    return crop, confidence, probabilities, pred_idx
