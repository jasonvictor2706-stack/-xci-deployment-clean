import redis
import json
import logging

logger = logging.getLogger(__name__)

# Connect to a local Redis instance
try:
    redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True, socket_timeout=1, socket_connect_timeout=1)
except Exception as e:
    redis_client = None
    logger.error(f"Failed to initialize Redis client: {e}")

def get_cached_weather(city: str):
    if not redis_client:
        return None
    try:
        key = f"weather:{city.lower()}"
        data = redis_client.get(key)
        if data:
            return json.loads(data)
    except Exception as e:
        logger.error(f"Redis get error: {e}")
    return None

def set_cached_weather(city: str, data: list):
    if not redis_client:
        return
    try:
        key = f"weather:{city.lower()}"
        # Cache expiry: 1800 seconds (30 minutes)
        redis_client.setex(key, 1800, json.dumps(data))
    except Exception as e:
        logger.error(f"Redis set error: {e}")
