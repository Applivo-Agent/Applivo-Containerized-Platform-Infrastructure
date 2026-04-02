"""
app/services/rate_limiter.py
─────────────────────────────
In-memory rate limiter to prevent API abuse.
Uses a sliding window counter per user (or IP).
"""

from __future__ import annotations

import time
import asyncio
from collections import defaultdict
from typing import Optional

import structlog

logger = structlog.get_logger()


class RateLimiter:
    """
    Token-bucket rate limiter.
    Supports per-user and global rate limiting.
    """

    def __init__(self):
        # {key: [(timestamp, count), ...]}
        self._requests: dict[str, list[float]] = defaultdict(list)
        self._lock = asyncio.Lock()

    async def is_allowed(
        self,
        key: str,
        max_requests: int = 100,
        window_seconds: int = 60,
    ) -> dict:
        """
        Check if a request is allowed under the rate limit.

        Args:
            key: Unique identifier (e.g., user_id or IP address)
            max_requests: Maximum requests allowed in the window
            window_seconds: Time window in seconds

        Returns:
            Dict with 'allowed', 'remaining', 'reset_at' keys
        """
        async with self._lock:
            now = time.time()
            window_start = now - window_seconds

            # Clean old entries
            self._requests[key] = [
                ts for ts in self._requests[key] if ts > window_start
            ]

            current_count = len(self._requests[key])

            if current_count >= max_requests:
                oldest = min(self._requests[key]) if self._requests[key] else now
                reset_at = oldest + window_seconds
                logger.warning("Rate limit exceeded", key=key, count=current_count, limit=max_requests)
                return {
                    "allowed": False,
                    "remaining": 0,
                    "current_count": current_count,
                    "limit": max_requests,
                    "reset_at": reset_at,
                    "retry_after": max(0, int(reset_at - now)),
                }

            # Record this request
            self._requests[key].append(now)

            return {
                "allowed": True,
                "remaining": max_requests - current_count - 1,
                "current_count": current_count + 1,
                "limit": max_requests,
                "reset_at": now + window_seconds,
                "retry_after": 0,
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
        async with self._lock:
            self._requests.pop(key, None)

    async def get_stats(self) -> dict:
        """Get current rate limiter statistics."""
        async with self._lock:
            now = time.time()
            return {
                "tracked_keys": len(self._requests),
                "total_requests_last_minute": sum(
                    len([ts for ts in timestamps if ts > now - 60])
                    for timestamps in self._requests.values()
                ),
            }


# Global rate limiter instance
rate_limiter = RateLimiter()
