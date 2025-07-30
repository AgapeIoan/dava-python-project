# app/core/redis_logger.py

import json
from datetime import datetime, timezone
import redis.asyncio as redis
from app.core.config import settings
from app.core.logging import logger

try:
    # Cream o instanta de client Redis special pentru stream-ul de log-uri
    redis_client = redis.from_url(
        f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}",
        db=1,  # Folosim o baza de date Redis diferita (ex: 1) pentru a separa log-urile de cache
        decode_responses=True
    )
    # Ping pentru a verifica conexiunea la pornire
    # Nota: Intr-o aplicatie reala, acest ping ar trebui facut intr-un startup event
    # Dar pentru structura actuala, il lasam aici cu un log.
    logger.info("Clientul Redis async pentru logging a fost configurat.")
except Exception as e:
    logger.error("Nu s-a putut configura clientul Redis pentru logging.", error=e)
    redis_client = None


def make_serializable(data: dict) -> dict:
    """O functie recursiva simpla pentru a converti valorile non-serializabile."""
    def convert(v):
        # Orice nu este un dictionar este convertit la string
        if isinstance(v, dict):
            return make_serializable(v)
        return str(v)
    
    return {k: convert(v) for k, v in data.items()}


async def log_to_stream(level: str, message: str, extra: dict = None):
    """Construieste un log si il scrie in stream-ul Redis."""
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
            logger.error("Eroare la scrierea in Redis Stream.", error=e)