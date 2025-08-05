"""
Defines decorators for enhancing functionality.
Includes caching for asynchronous functions using Redis.
"""

import functools
from app.core.logging import logger
from app.core.redis_cache import cache as redis_cache_client

def cache_result(key_prefix: str, ttl: int = 3600):
    """
    A decorator that automatically manages caching for an asynchronous function.

    Args:
        key_prefix (str): A prefix for the cache key (e.g., "fibonacci").
        ttl (int): Time To Live (TTL) for the cache, in seconds.

    Returns:
        Callable: The wrapped function with caching enabled.

    Notes:
        If the Redis cache client is unavailable, the function will execute without caching.
    """
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            if not redis_cache_client:
                logger.warning(
                    "Redis cache client is unavailable. Executing function without cache."
                )
                return await func(*args, **kwargs)

            arg_list = [str(a) for a in args[1:]]
            kwarg_list = [f"{k}={v}" for k, v in kwargs.items()]
            arg_str = ":".join(arg_list + kwarg_list)
            cache_key = f"{key_prefix}:{arg_str}"

            # 1. Check the cache
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