#creare inregistrare log
#scrie acest log in stream Redis

import json
from datetime import datetime
from app.core.redis_cache import cache as redis_client
REDIS_STREAM_KEY = "log_stream"

async def log_to_stream(level: str, message: str, extra: dict = None):
    log_entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "level": level,
        "message": message,
        "extra": json.dumps(extra or {})
    }

    await redis_client.xadd(REDIS_STREAM_KEY, log_entry)
