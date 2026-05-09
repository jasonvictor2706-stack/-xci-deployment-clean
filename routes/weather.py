from fastapi import APIRouter
from services.weather_service import get_weather

router = APIRouter()

@router.get("/{city}")
def get_weather_route(city: str):
    """
    Fetch 5-day weather forecast for a given city.
    """
    forecasts = get_weather(city)
    return {
        "city": city,
        "forecast": forecasts
    }
