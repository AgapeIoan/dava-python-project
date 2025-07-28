#creare inregistrare log
#scrie acest log in stream Redis

import json
from datetime import datetime, timezone
from app.services.math_service import redis_client

def make_serializable(data: dict) -> dict:
    def convert(v):
        if isinstance(v, complex):
            return str(v)
        if isinstance(v, dict):
            return make_serializable(v)
        return v
    return {k: convert(v) for k, v in data.items()}

async def log_to_stream(level: str, message: str, extra: dict = None):
    log_entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "level": level,
        "message": message,
        "extra": json.dumps(make_serializable(extra or {}))
    }

    if redis_client:
        await redis_client.xadd("log_stream", log_entry)
