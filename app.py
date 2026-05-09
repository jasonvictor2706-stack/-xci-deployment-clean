from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from database.connection import connect_to_mongo, close_db

# ROUTERS
from routes.auth import router as auth_router
from routes.predict import router as predict_router
from routes.weather import router as weather_router
from routes.fertilizer import router as fertilizer_router
from routes.chatbot import router as chatbot_router


@asynccontextmanager
async def lifespan(app: FastAPI):

    # Startup
    await connect_to_mongo()

    yield

    # Shutdown
    await close_db()


app = FastAPI(
    title="XCI API",
    version="1.0.0",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ROUTES
app.include_router(auth_router)
app.include_router(predict_router)
app.include_router(weather_router, prefix="/weather")
app.include_router(fertilizer_router, prefix="/api")
app.include_router(chatbot_router, prefix="/api")


@app.get("/")
async def root():
    return {
        "message": "XCI Backend Running"
    }


@app.get("/health")
async def health():
    return {
        "status": "ok"
    }