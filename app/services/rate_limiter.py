"""
app/services/rate_limiter.py
────────────────────────────
Redis-backed rate limiter to prevent API abuse.
Uses a sliding window counter per user (or IP).
Persists across restarts.
"""

from __future__ import annotations

import time
from typing import Optional

import structlog

from app.core.config import settings

logger = structlog.get_logger()


class RateLimiter:
    """
    Redis-backed sliding window rate limiter.
    Persists across restarts - survives server/container restarts.
    """

    def __init__(self):
        self._redis_url = settings.REDIS_URL
        if isinstance(self._redis_url, bytes):
            self._redis_url = self._redis_url.decode()
        self._initialized = False
        self._redis = None

    async def _get_redis(self):
        """Lazy initialization of Redis connection with robust auth handling."""
        if not self._initialized:
            import redis.asyncio as aioredis
            
            # Use explicit connection params to handle potential auth issues
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
                logger.error("Redis connection failed", error=str(e), url=self._redis_url)
                raise
            
            self._initialized = True
        return self._redis

    async def is_allowed(
        self,
        key: str,
        max_requests: int = 100,
        window_seconds: int = 60,
    ) -> dict:
        """
        Check if a request is allowed under the rate limit.
        Uses Redis sorted set for sliding window.

        Args:
            key: Unique identifier (e.g., user_id or IP address)
            max_requests: Maximum requests allowed in the window
            window_seconds: Time window in seconds

        Returns:
            Dict with 'allowed', 'remaining', 'reset_at' keys
        """
        try:
            redis = await self._get_redis()
            now = time.time()
            window_start = now - window_seconds

            pipe = redis.pipeline()
            # Remove old entries outside the window
            await pipe.zremrangebyscore(key, 0, window_start)
            # Count current requests in window
            await pipe.zcard(key)
            # Add current request
            await pipe.zadd(key, {str(now): now})
            # Set expiry on the key
            await pipe.expire(key, window_seconds + 1)
            
            results = await pipe.execute()
            current_count = results[1]

            if current_count >= max_requests:
                # Remove the request we just added since we're rejected
                await redis.zrem(key, str(now))
                oldest = await redis.zrange(key, 0, 0, withscores=True)
                reset_at = oldest[0][1] if oldest else now + window_seconds
                logger.warning("Rate limit exceeded", key=key, count=current_count, limit=max_requests)
                return {
                    "allowed": False,
                    "remaining": 0,
                    "current_count": current_count,
                    "limit": max_requests,
                    "reset_at": reset_at,
                    "retry_after": max(0, int(reset_at - now)),
                }

            return {
                "allowed": True,
                "remaining": max(0, max_requests - current_count - 1),
                "current_count": current_count + 1,
                "limit": max_requests,
                "reset_at": now + window_seconds,
                "retry_after": 0,
            }
        except Exception as e:
            logger.error("Rate limiter Redis unavailable, DENYING request (fail-closed)", error=str(e))
            if settings.APP_ENV == "development":
                logger.warning("Rate limiter bypass enabled in development due to Redis unavailability")
                return {
                    "allowed": True,
                    "remaining": max_requests,
                    "current_count": 0,
                    "limit": max_requests,
                    "reset_at": time.time() + window_seconds,
                    "retry_after": 0,
                    "warning": "Rate limiter bypassed in development",
                }
            return {
                "allowed": False,
                "remaining": 0,
                "current_count": max_requests,
                "limit": max_requests,
                "reset_at": time.time() + window_seconds,
                "retry_after": window_seconds,
                "error": "Security infrastructure unavailable"
            }

    async def check(
        self,
        key: str,
        max_requests: int = 100,
        window_seconds: int = 60,
    ) -> bool:
        """Simple boolean check if request is allowed."""
        result = await self.is_allowed(key, max_requests, window_seconds)
        return result["allowed"]

    async def reset(self, key: str) -> None:
        """Reset the rate limit counter for a key."""
        try:
            redis = await self._get_redis()
            await redis.delete(key)
        except Exception as e:
            logger.warning("Failed to reset rate limit key", key=key, error=str(e))

    async def get_stats(self) -> dict:
        """Get current rate limiter statistics."""
        try:
            redis = await self._get_redis()
            keys = []
            async for key in redis.scan_iter(match="rate:*"):
                keys.append(key)
            return {
                "tracked_keys": len(keys),
                "backend": "redis",
            }
        except Exception:
            return {"tracked_keys": 0, "backend": "redis_unavailable"}


# Global rate limiter instance
rate_limiter = RateLimiter()
