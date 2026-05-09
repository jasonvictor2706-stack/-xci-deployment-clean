from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field
from typing import List
from services.fertilizer_service import predict_fertilizer

router = APIRouter()

class FertilizerRequest(BaseModel):
    temperature: float = Field(..., description="Temperature in Celsius")
    humidity: float = Field(..., description="Humidity percentage")
    N: float = Field(..., description="Nitrogen content in soil")
    P: float = Field(..., description="Phosphorus content in soil")
    K: float = Field(..., description="Potassium content in soil")
    ph: float = Field(..., description="Soil pH level")
    crop: str = Field(..., description="Name of the crop")

class FertilizerResponse(BaseModel):
    recommended_fertilizers: List[str]

@router.post("/predict/fertilizer", response_model=FertilizerResponse)
async def get_fertilizer_prediction(request: FertilizerRequest):
    """
    Predict top 3 recommended fertilizers based on environmental and soil conditions.
    """
    try:
        top_fertilizers = predict_fertilizer(
            temperature=request.temperature,
            humidity=request.humidity,
            N=request.N,
            P=request.P,
            K=request.K,
            ph=request.ph,
            crop=request.crop
        )
        return FertilizerResponse(recommended_fertilizers=top_fertilizers)
        
    except ValueError as ve:
        # Client side error - bad input
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail=str(ve)
        )
    except Exception as e:
        # Server side error
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred during prediction: {str(e)}"
        )
