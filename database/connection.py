from motor.motor_asyncio import AsyncIOMotorClient
from core.config import MONGODB_URL, DATABASE_NAME
import logging

logger = logging.getLogger(__name__)

client = None
db = None

async def connect_to_mongo():
    global client, db
    try:
        client = AsyncIOMotorClient(MONGODB_URL)
        db = client[DATABASE_NAME]
        await client.admin.command('ping')
        logger.info(f"[XCI] Successfully connected to MongoDB: {DATABASE_NAME}")
    except Exception as e:
        logger.error(f"[XCI] MongoDB connection failed: {str(e)}")
        raise

async def close_db():
    global client
    if client:
        client.close()
        logger.info("[XCI] MongoDB connection closed")

def get_db():
    if db is None:
        logger.error("Database connection requested but db is None.")
        from fastapi import HTTPException
        raise HTTPException(status_code=503, detail="Database connection is unavailable. Please try again later.")
    return db