"""
Redis logger module.
Provides functionality for logging events to a Redis stream.
"""

import json
from datetime import datetime, timezone
import redis.asyncio as redis
from app.core.config import settings
from app.core.logging import logger

try:
    """
    Configures a Redis client specifically for logging.

    Attributes:
        redis_client (redis.Redis): The Redis client instance for logging.

    Notes:
        - Uses a separate Redis database (e.g., db=1) to isolate logs from cache.
        - Logs success or failure during configuration.
    """
    redis_client = redis.from_url(
        f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}",
        db=1,  # Separate Redis database for logs
        decode_responses=True
    )
    logger.info("✅ Async Redis client for logging has been configured.")
except Exception as e:
    logger.error("❌ Failed to configure Redis client for logging.", error=e)
    redis_client = None

def make_serializable(data: dict) -> dict:
    """
    Recursively converts non-serializable values in a dictionary to strings.

    Args:
        data (dict): The dictionary to process.

    Returns:
        dict: A dictionary with all values converted to strings.
    """
    def convert(v):
        if isinstance(v, dict):
            return make_serializable(v)
        return str(v)
    
    return {k: convert(v) for k, v in data.items()}

async def log_to_stream(level: str, message: str, extra: dict = None):
    """
    Constructs a log entry and writes it to a Redis stream.

    Args:
        level (str): The log level (e.g., "INFO", "ERROR").
        message (str): The log message.
        extra (dict, optional): Additional data to include in the log entry.

    Notes:
        - Uses the Redis `xadd` command to append the log entry to the stream.
        - Logs errors if writing to the Redis stream fails.
    """
    log_entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "level": level,
        "message": message,
        "extra": json.dumps(make_serializable(extra or {}))
    }

    if redis_client:
        try:
            await redis_client.xadd("log_stream", log_entry)
        except Exception as e:
            logger.error("Error writing to Redis stream.", error=e)