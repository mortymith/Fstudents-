"""
Redis dependencies for FastAPI.
"""
from typing import AsyncGenerator
from app.core.config import settings
from app.core.cache import CacheManager
from redis.asyncio import Redis



async def get_redis_client() -> AsyncGenerator[Redis, None]:
    """
    Dependency that provides a Redis client.
    
    Usage:
        async def some_route(redis_client = Depends(get_redis_client)):
            # Use redis client
            pass
    """
    cache = CacheManager(settings.redis_url)
    await cache.connect()


    return cache.get_client()


    
    
    
    
    
