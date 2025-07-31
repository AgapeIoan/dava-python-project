import redis.asyncio as redis
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

try:
    # configuration for the Redis client
    cache = redis.Redis(
        host=settings.REDIS_HOST,
        port=settings.REDIS_PORT,
        decode_responses=True  # automatic conversion of bytes to str
    )
    logger.info("✅ Clientul Redis async a fost configurat.")
except Exception as e:
    logger.error(f"❌ Eroare la configurarea Redis: {e}")
    cache = None
