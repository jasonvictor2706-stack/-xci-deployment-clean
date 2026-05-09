from fastapi import APIRouter, Depends, HTTPException, Header
from pydantic import BaseModel
from schemas.prediction import PredictRequest, PredictResponse, FactorItem
from services.auth_service import get_current_user
from services import ml_service, shap_service, region_service
from database.connection import get_db
from datetime import datetime

router = APIRouter(tags=["Prediction"])


class RegionPredictRequest(BaseModel):
    region: str
    season: str


@router.post("/predict", response_model=PredictResponse)
async def predict(data: PredictRequest, current_user: dict = Depends(get_current_user), accept_language: str = Header("en")):
    # ── resolve features ──────────────────────────────────────────────────
    required = [data.N, data.P, data.K, data.temperature, data.humidity, data.rainfall, data.ph]
    if any(v is None for v in required):
        raise HTTPException(
            status_code=422,
            detail="Manual mode requires all fields: N, P, K, temperature, humidity, rainfall, ph",
        )
    features = {
        "N": data.N,
        "P": data.P,
        "K": data.K,
        "temperature": data.temperature,
        "humidity": data.humidity,
        "ph": data.ph,
        "rainfall": data.rainfall,
    }
    region_info = {}

    # ── ML prediction ─────────────────────────────────────────────────────
    # ── ML prediction ─────────────────────────────────────────────────────
    crop, confidence, probabilities, pred_idx = ml_service.predict(features)
    
    classes = ml_service.get_classes()
    crop_probs = sorted(zip(classes, probabilities), key=lambda x: x[1], reverse=True)
    top_crops = [{"crop": c, "score": float(round(p, 4))} for c, p in crop_probs[:3]]

    top_factors, explanation_text, shap_chart = shap_service.explain(features, pred_idx, crop, top_crops, accept_language)

    # ── Save to history ───────────────────────────────────────────────────
    db = get_db()
    history_doc = {
        "user_id": str(current_user["_id"]),
        "user_email": current_user["email"],
        "mode": "manual",
        "region": None,
        "features": features,
        "crop": crop,
        "confidence": confidence,
        "explanation_text": explanation_text,
        "top_factors": top_factors,
        "shap_chart": shap_chart,
        "timestamp": datetime.utcnow(),
    }
    await db["prediction_history"].insert_one(history_doc)

    return PredictResponse(
        predicted_crop=crop,
        confidence=confidence,
        top_crops=top_crops,
        temperature=features["temperature"],
        humidity=features["humidity"],
        rainfall=features["rainfall"],
        N=features["N"],
        P=features["P"],
        K=features["K"],
        pH=features["ph"],
        top_factors=[FactorItem(**f) for f in top_factors],
        explanation_text=explanation_text,
        shap_chart=shap_chart,
    )


@router.post("/predict_region", response_model=PredictResponse)
async def predict_region(data: RegionPredictRequest, current_user: dict = Depends(get_current_user), accept_language: str = Header("en")):
    # ── resolve features ──────────────────────────────────────────────────
    region_data = region_service.get_region_features(data.region, data.season)
    features = {k: region_data[k] for k in ml_service.FEATURE_ORDER}
    region_info = {
        "soil_type": region_data.get("soil_type"),
        "region_matched": region_data.get("region_matched"),
        "season": data.season
    }

    # ── ML prediction ─────────────────────────────────────────────────────
    # ── ML prediction ─────────────────────────────────────────────────────
    crop, confidence, probabilities, pred_idx = ml_service.predict(features)

    classes = ml_service.get_classes()
    crop_probs = sorted(zip(classes, probabilities), key=lambda x: x[1], reverse=True)
    top_crops = [{"crop": c, "score": float(round(p, 4))} for c, p in crop_probs[:3]]

    # ── SHAP explanation ──────────────────────────────────────────────────
    top_factors, explanation_text, shap_chart = shap_service.explain(features, pred_idx, crop, top_crops, accept_language)

    # ── Save to history ───────────────────────────────────────────────────
    db = get_db()
    history_doc = {
        "user_id": str(current_user["_id"]),
        "user_email": current_user["email"],
        "mode": "region",
        "region": data.region,
        "features": features,
        "crop": crop,
        "confidence": confidence,
        "explanation_text": explanation_text,
        "top_factors": top_factors,
        "shap_chart": shap_chart,
        "timestamp": datetime.utcnow(),
    }
    if region_info:
        history_doc.update(region_info)
    await db["prediction_history"].insert_one(history_doc)

    return PredictResponse(
        predicted_crop=crop,
        confidence=confidence,
        top_crops=top_crops,
        temperature=features["temperature"],
        humidity=features["humidity"],
        rainfall=features["rainfall"],
        N=features["N"],
        P=features["P"],
        K=features["K"],
        pH=features["ph"],
        top_factors=[FactorItem(**f) for f in top_factors],
        explanation_text=explanation_text,
        shap_chart=shap_chart,
    )


@router.get("/history")
async def get_history(current_user: dict = Depends(get_current_user)):
    db = get_db()
    cursor = db["prediction_history"].find(
        {"user_id": str(current_user["_id"])},
        {"_id": 0},
    ).sort("timestamp", -1).limit(50)
    records = await cursor.to_list(length=50)
    return {"history": records}


@router.get("/regions")
async def list_regions():
    """Returns all available region names."""
    from services.ml_service import SOIL_DF
    regions = sorted(SOIL_DF["Region"].dropna().tolist())
    return {"regions": regions}
