import os
import requests
from dotenv import load_dotenv

load_dotenv()
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")
WEATHERAPI_KEY = os.getenv("WEATHERAPI_KEY")

print("Keys:", OPENWEATHER_API_KEY, WEATHERAPI_KEY)

try:
    print('Testing OpenWeather...')
    res = requests.get('https://api.openweathermap.org/data/2.5/forecast', params={'q':'Hyderabad', 'appid': OPENWEATHER_API_KEY})
    print('OpenWeather status:', res.status_code)
    print(res.text[:100])
except Exception as e:
    print('OpenWeather error:', e)

try:
    print('Testing WeatherAPI...')
    res = requests.get('https://api.weatherapi.com/v1/forecast.json', params={'key': WEATHERAPI_KEY, 'q': 'Hyderabad', 'days': 5})
    print('WeatherAPI status:', res.status_code)
    print(res.text[:100])
except Exception as e:
    print('WeatherAPI error:', e)
