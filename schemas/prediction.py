from pydantic import BaseModel
from typing import Optional, List
from enum import Enum


class PredictMode(str, Enum):
    manual = "manual"
    region = "region"


class PredictRequest(BaseModel):
    mode: PredictMode
    N: Optional[float] = None
    P: Optional[float] = None
    K: Optional[float] = None
    temperature: Optional[float] = None
    humidity: Optional[float] = None
    rainfall: Optional[float] = None
    ph: Optional[float] = None
    region: Optional[str] = None
    season: Optional[str] = None


class FactorItem(BaseModel):
    feature: str
    impact: str


class ShapChartItem(BaseModel):
    feature: str
    value: float


class TopCropItem(BaseModel):
    crop: str
    score: float


class PredictResponse(BaseModel):
    predicted_crop: str
    confidence: float
    top_crops: List[TopCropItem]
    temperature: float
    humidity: float
    rainfall: float
    N: float
    P: float
    K: float
    pH: float
    top_factors: List[FactorItem]
    explanation_text: str
    shap_chart: Optional[List[ShapChartItem]] = None
