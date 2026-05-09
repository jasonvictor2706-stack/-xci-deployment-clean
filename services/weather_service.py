import os
import requests
import logging
from dotenv import load_dotenv
from fastapi import HTTPException
from cache.redis_client import get_cached_weather, set_cached_weather

# Load environment variables
load_dotenv()

OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")
WEATHERAPI_KEY = os.getenv("WEATHERAPI_KEY")

logger = logging.getLogger(__name__)

def get_weather(city: str):
    # 1. 1️⃣ Check Redis cache first.
    cached_data = get_cached_weather(city)
    if cached_data:
        logger.info("Weather Source: Redis Cache")
        print("Weather Source: Redis Cache")
        return cached_data

    # 2. 2️⃣ If cache miss: Call OpenWeather API (Primary)
    if OPENWEATHER_API_KEY:
        try:
            url = "https://api.openweathermap.org/data/2.5/forecast"
            params = {
                "q": city,
                "appid": OPENWEATHER_API_KEY,
                "units": "metric"
            }
            response = requests.get(url, params=params, timeout=5)
            response.raise_for_status()
            data = response.json()
            
            daily_forecasts = []
            seen_dates = set()
            
            for item in data.get("list", []):
                date_str = item["dt_txt"].split(" ")[0]
                is_midday = "12:00:00" in item["dt_txt"]
                
                if date_str not in seen_dates and (is_midday or len(seen_dates) == 0):
                    daily_forecasts.append({
                        "date": date_str,
                        "temperature": round(item["main"]["temp"]),
                        "humidity": item["main"]["humidity"],
                        "rainfall": item.get("rain", {}).get("3h", 0) if "rain" in item else 0,
                        "wind_speed": item["wind"]["speed"],
                        "condition": item["weather"][0]["main"],
                        "weather_icon": item["weather"][0]["icon"]
                    })
                    seen_dates.add(date_str)
                    
                if len(daily_forecasts) >= 5:
                    break
                    
            if len(daily_forecasts) < 5:
                seen_dates.clear()
                daily_forecasts.clear()
                for item in data.get("list", []):
                    date_str = item["dt_txt"].split(" ")[0]
                    if date_str not in seen_dates:
                        daily_forecasts.append({
                            "date": date_str,
                            "temperature": round(item["main"]["temp"]),
                            "humidity": item["main"]["humidity"],
                            "rainfall": item.get("rain", {}).get("3h", 0) if "rain" in item else 0,
                            "wind_speed": item["wind"]["speed"],
                            "condition": item["weather"][0]["main"],
                            "weather_icon": item["weather"][0]["icon"]
                        })
                        seen_dates.add(date_str)
                    if len(daily_forecasts) >= 5:
                        break
            
            if daily_forecasts:
                logger.info("Weather Source: OpenWeather API")
                print("Weather Source: OpenWeather API")
                set_cached_weather(city, daily_forecasts)
                return daily_forecasts
        except Exception as e:
            logger.warning(f"OpenWeather API failed: {e}")
            print(f"OpenWeather API failed: {e}")

    # 3. 3️⃣ If OpenWeather API fails: Call WeatherAPI fallback provider.
    if WEATHERAPI_KEY:
        try:
            url = "https://api.weatherapi.com/v1/forecast.json"
            params = {
                "key": WEATHERAPI_KEY,
                "q": city,
                "days": 5
            }
            response = requests.get(url, params=params, timeout=5)
            response.raise_for_status()
            data = response.json()
            
            daily_forecasts = []
            for item in data.get("forecast", {}).get("forecastday", []):
                # WeatherAPI uses 'icon' that looks like "//cdn.weatherapi.com/weather/64x64/day/113.png"
                icon_parts = item["day"]["condition"]["icon"].split("/")
                icon_fallback = icon_parts[-1] if hasattr(icon_parts, '__len__') and len(icon_parts) > 0 else "01d"

                daily_forecasts.append({
                    "date": item["date"],
                    "temperature": round(item["day"]["avgtemp_c"]),
                    "humidity": item["day"]["avghumidity"],
                    "rainfall": item["day"]["totalprecip_mm"],
                    "wind_speed": item["day"]["maxwind_kph"],
                    "condition": item["day"]["condition"]["text"],
                    "weather_icon": icon_fallback
                })
                
            if daily_forecasts:
                logger.info("Weather Source: WeatherAPI Fallback")
                print("Weather Source: WeatherAPI Fallback")
                set_cached_weather(city, daily_forecasts)
                return daily_forecasts
        except Exception as e:
            logger.warning(f"WeatherAPI Fallback failed: {e}")
            print(f"WeatherAPI Fallback failed: {e}")

    # 4. Error Handling
    # If both APIs fail check Redis for last cached value (already checked at the top)
    # The prompt explicitly asked to fallback to cache. If the cache is expired, we error.
    logger.error("All weather services failed")
    print("All weather services failed")
    raise HTTPException(status_code=503, detail="Weather service temporarily unavailable")
