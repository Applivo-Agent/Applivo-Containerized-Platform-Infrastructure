"""
app/services/quota_service.py
──────────────────────────────
Enforces per-user daily application limits based on subscription tier.
Prevents any user from exceeding their plan's daily quota.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

import structlog
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db_context
from app.models.application import Application, ApplicationStatus
from app.models.subscription import PLAN_DAILY_LIMITS, PlanTier, SubscriptionStatus
from app.services.subscription_service import subscription_service

logger = structlog.get_logger()


class QuotaService:
    """Enforces application quota limits per user per day."""

    async def check_quota(self, user_id: str) -> dict:
        """
        Check the user's remaining daily quota.
        Returns quota info including remaining count and limit.
        """
        # Superuser gets unlimited quota (bypass sub check)
        from app.models.user import User
        from app.core.database import get_db_context
        from sqlalchemy import select as sa_select
        async with get_db_context() as _db:
            _user_result = await _db.execute(sa_select(User).where(User.id == user_id))
            _user = _user_result.scalar_one_or_none()
        if _user and _user.is_superuser:
            used = await self._get_applications_today(user_id)
            limit = PLAN_DAILY_LIMITS.get(PlanTier.PREMIUM, 150)
            return {
                "allowed": True,
                "reason": None,
                "plan": "premium",
                "limit": limit,
                "used": used,
                "remaining": max(0, limit - used),
            }

        sub = await subscription_service.get_active_subscription(user_id)
        if not sub or not sub.is_active():
            return {
                "allowed": False,
                "reason": "No active subscription",
                "limit": 0,
                "used": 0,
                "remaining": 0,
            }

        daily_limit = PLAN_DAILY_LIMITS.get(PlanTier(sub.plan), 0)
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        redis_key = f"quota:{user_id}:{today}"
        
        try:
            import redis
            from app.core.config import settings
            redis_url = settings.REDIS_URL
            if isinstance(redis_url, bytes):
                redis_url = redis_url.decode()
            r = redis.from_url(redis_url, decode_responses=True)
            
            redis_used = r.get(redis_key)
            if redis_used is not None:
                used = int(redis_used)
            else:
                used = await self._get_applications_today(user_id)
                r.setex(redis_key, 86400, used)
        except Exception:
            used = await self._get_applications_today(user_id)
        
        remaining = max(0, daily_limit - used)

        return {
            "allowed": remaining > 0,
            "reason": None if remaining > 0 else f"Daily limit of {daily_limit} reached",
            "plan": sub.plan if hasattr(sub, 'plan') else None,
            "limit": daily_limit,
            "used": used,
            "remaining": remaining,
        }

    async def consume_quota(self, user_id: str, count: int = 1) -> bool:
        """
        Check and consume quota for the user atomically.
        Uses Redis for atomic decrement to prevent race conditions.
        Returns True if quota is available and consumed, False otherwise.
        """
        quota = await self.check_quota(user_id)
        if not quota["allowed"]:
            logger.warning("Quota exceeded", user_id=user_id, used=quota["used"], limit=quota["limit"])
            return False
        if quota["remaining"] < count:
            logger.warning("Insufficient quota", user_id=user_id, remaining=quota["remaining"], requested=count)
            return False
        
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        key = f"quota:{user_id}:{today}"
        
        try:
            import redis
            from app.core.config import settings
            redis_url = settings.REDIS_URL
            if isinstance(redis_url, bytes):
                redis_url = redis_url.decode()
            r = redis.from_url(redis_url, decode_responses=True)
            
            remaining = r.decrby(key, count)
            
            if remaining < 0:
                r.incrby(key, count)
                logger.warning("Race condition prevented - quota already consumed", user_id=user_id)
                return False
            
            ttl = 86400
            r.expire(key, ttl)
            
            logger.info("Quota consumed atomically", user_id=user_id, remaining=remaining, count=count)
            return True
        except Exception as e:
            logger.warning("Redis unavailable, falling back to DB-based quota check", error=str(e))
            return True

    async def get_quota_with_details(self, user_id: str) -> dict:
        """Get detailed quota information including subscription details."""
        quota = await self.check_quota(user_id)
        sub = await subscription_service.get_active_subscription(user_id)

        result = {
            **quota,
            "subscription": None,
        }

        if sub:
            result["subscription"] = {
                "id": sub.id,
                "plan": sub.plan if hasattr(sub, 'plan') else None,
                "status": sub.status.value if hasattr(sub.status, 'value') else sub.status,
                "start_date": sub.start_date.isoformat() if sub.start_date else None,
                "end_date": sub.end_date.isoformat() if sub.end_date else None,
            }

        return result

    async def _get_applications_today(self, user_id: str) -> int:
        """Count applications ACTUALLY SUBMITTED today for the given user.

        Only counts applications with post-submission statuses.
        QUEUED / APPLYING / PENDING_APPROVAL are excluded because they haven't
        been sent yet — pre-queued jobs must not consume quota.
        """
        async with get_db_context() as db:
            today = datetime.now(timezone.utc).date()
            result = await db.execute(
                select(func.count(Application.id)).where(
                    Application.user_id == user_id,
                    func.date(Application.created_at) == today,
                    Application.status.in_([
                        ApplicationStatus.APPLIED,
                        ApplicationStatus.VIEWED,
                        ApplicationStatus.SHORTLISTED,
                        ApplicationStatus.INTERVIEW_SCHEDULED,
                        ApplicationStatus.INTERVIEW_COMPLETED,
                        ApplicationStatus.OFFER_RECEIVED,
                        ApplicationStatus.OFFER_ACCEPTED,
                        ApplicationStatus.REJECTED,
                    ]),
                )
            )
            return result.scalar() or 0


quota_service = QuotaService()
