"""
app/services/cache_service.py
─────────────────────────────
Redis-backed caching service for API responses and heavy computations.
"""

from __future__ import annotations
import json
from typing import Any, Optional, Union
import structlog
from app.core.config import settings

logger = structlog.get_logger()


class CacheService:
    """
    Redis-backed caching service.
    """

    def __init__(self):
        self._redis_url = settings.REDIS_URL
        if isinstance(self._redis_url, bytes):
            self._redis_url = self._redis_url.decode()
        self._initialized = False
        self._redis = None

    async def _get_redis(self):
        """Lazy initialization of Redis connection."""
        if not self._initialized:
            import redis.asyncio as aioredis
            
            try:
                self._redis = aioredis.from_url(
                    self._redis_url,
                    decode_responses=True,
                    socket_connect_timeout=2,
                    socket_timeout=2,
                )
                # Test connection immediately
                await self._redis.ping()
            except Exception as e:
                logger.error("Failed to connect to Redis for caching", error=str(e))
                return None
            
            self._initialized = True
        return self._redis

    async def get(self, key: str) -> Optional[Any]:
        """Retrieve a value from the cache."""
        try:
            redis = await self._get_redis()
            if not redis:
                return None
            
            value = await redis.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            logger.warning("Cache retrieval failed", key=key, error=str(e))
            return None

    async def set(self, key: str, value: Any, ttl: int = 60) -> bool:
        """Store a value in the cache with a TTL (seconds)."""
        try:
            redis = await self._get_redis()
            if not redis:
                return False
            
            serialized = json.dumps(value)
            await redis.set(key, serialized, ex=ttl)
            return True
        except Exception as e:
            logger.warning("Cache storage failed", key=key, error=str(e))
            return False

    async def delete(self, key: str) -> bool:
        """Delete a value from the cache."""
        try:
            redis = await self._get_redis()
            if not redis:
                return False
            await redis.delete(key)
            return True
        except Exception as e:
            logger.warning("Cache deletion failed", key=key, error=str(e))
            return False


# Global cache service instance
cache_service = CacheService()
