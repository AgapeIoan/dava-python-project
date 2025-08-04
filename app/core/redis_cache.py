"""
Redis cache configuration module.
Provides an asynchronous Redis client for caching operations.
"""

import redis.asyncio as redis
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

try:
    """
    Configures the Redis client.

    Attributes:
        cache (redis.Redis): The Redis client instance.

    Notes:
        - Automatically converts bytes to strings using `decode_responses=True`.
        - Logs success or failure during configuration.
    """
    cache = redis.Redis(
        host=settings.REDIS_HOST,
        port=settings.REDIS_PORT,
        decode_responses=True  # Automatic conversion of bytes to str
    )
    logger.info("✅ Async Redis client has been configured.")
except Exception as e:
    logger.error(f"❌ Error configuring Redis: {e}")
    cache = None
