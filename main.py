from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import random
from datetime import datetime

app = FastAPI(title="XCI API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Models
class LoginRequest(BaseModel):
    email: str
    password: str

class RegisterRequest(BaseModel):
    name: str
    email: str
    password: str
    role: str

class OTPRequest(BaseModel):
    email: str
    otp: str

class PredictRequest(BaseModel):
    N: float = 50
    P: float = 50
    K: float = 50
    temperature: float = 25.0
    humidity: float = 60.0
    ph: float = 7.0
    rainfall: float = 100.0

# Basic routes
@app.get("/")
async def root():
    return {"message": "XCI Backend Running", "status": "online"}

@app.get("/health")
async def health():
    return {"status": "ok"}

# Auth routes
@app.post("/auth/register")
async def register(data: RegisterRequest):
    return {
        "message": "Registration successful",
        "access_token": f"token_{random.randint(1000, 9999)}",
        "user": {
            "id": f"user_{random.randint(1000, 9999)}",
            "name": data.name,
            "email": data.email,
            "role": data.role,
            "is_verified": False
        }
    }

@app.post("/auth/login")
async def login(data: LoginRequest):
    return {
        "access_token": f"token_{random.randint(1000, 9999)}",
        "user": {
            "id": f"user_{random.randint(1000, 9999)}",
            "name": "User",
            "email": data.email,
            "role": "farmer",
            "is_verified": True
        }
    }

@app.post("/auth/verify-otp")
async def verify_otp(data: OTPRequest):
    return {
        "message": "Email verified",
        "access_token": f"token_{random.randint(1000, 9999)}",
        "user": {
            "id": f"user_{random.randint(1000, 9999)}",
            "name": "User",
            "email": data.email,
            "role": "farmer",
            "is_verified": True
        }
    }

@app.post("/auth/resend-otp")
async def resend_otp(email: str):
    return {"message": f"OTP sent to {email}"}

# Prediction routes
@app.post("/predict")
async def predict(data: PredictRequest):
    crops = ["Rice", "Wheat", "Maize", "Mango", "Tomato"]
    predicted_crop = crops[int((data.N + data.P + data.K) / 50) % len(crops)]
    
    return {
        "predicted_crop": predicted_crop,
        "confidence": 0.85,
        "explanation": f"{predicted_crop} is recommended based on your soil parameters"
    }

@app.get("/predict_region")
async def predict_region(region: str = "Hyderabad", season: str = "Summer"):
    crops_map = {
        "summer": "Maize",
        "winter": "Wheat",
        "monsoon": "Rice"
    }
    crop = crops_map.get(season.lower(), "Rice")
    
    return {
        "predicted_crop": crop,
        "confidence": 0.88,
        "region": region,
        "season": season
    }

# Weather route
@app.get("/weather/{city}")
async def get_weather(city: str):
    return {
        "city": city,
        "current": {
            "temperature": 28,
            "humidity": 65,
            "condition": "Cloudy"
        },
        "forecast": [
            {"date": "2026-05-09", "temperature": 28, "humidity": 65, "rainfall": 0},
            {"date": "2026-05-10", "temperature": 30, "humidity": 60, "rainfall": 0},
        ]
    }

# Fertilizer route
@app.get("/fertilizer")
async def get_fertilizer(crop: str = "Rice"):
    return {
        "crop": crop,
        "primary": "NPK 20:10:10",
        "quantity": "60 kg/hectare",
        "timing": "During plowing"
    }

# Chatbot route
@app.post("/chatbot")
async def chatbot(message: str):
    return {
        "response": "Hello! How can I help you with crop recommendations?",
        "timestamp": datetime.now().isoformat()
    }