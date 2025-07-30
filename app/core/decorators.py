import functools
from app.core.logging import logger
from app.core.redis_cache import cache as redis_cache_client

def cache_result(key_prefix: str, ttl: int = 3600):
    """
    Un decorator care gestioneaza automat caching-ul pentru o functie async.
    
    :param key_prefix: Un prefix pentru cheia de cache (ex: "fibonacci").
    :param ttl: Timpul de viata (Time To Live) al cache-ului, in secunde.
    """
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            if not redis_cache_client:
                logger.warning(
                    "Clientul Redis pentru cache nu este disponibil. "
                    "Se executa functia fara cache."
                )
                return await func(*args, **kwargs)

            arg_list = [str(a) for a in args[1:]]
            kwarg_list = [f"{k}={v}" for k, v in kwargs.items()]
            arg_str = ":".join(arg_list + kwarg_list)
            cache_key = f"{key_prefix}:{arg_str}"

            # 1. Verificam cache-ul
            cached_result = await redis_cache_client.get(cache_key)
            if cached_result is not None:
                logger.info("Cache HIT", key=cache_key)
                return cached_result 
            
            logger.info("Cache MISS", key=cache_key)
            
            result = await func(*args, **kwargs)

            await redis_cache_client.setex(cache_key, ttl, str(result)) 
            
            return result
        return wrapper
    return decorator