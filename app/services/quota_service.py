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
        Check and consume quota for the user.
        Returns True if quota is available and consumed, False otherwise.
        """
        quota = await self.check_quota(user_id)
        if not quota["allowed"]:
            logger.warning("Quota exceeded", user_id=user_id, used=quota["used"], limit=quota["limit"])
            return False
        if quota["remaining"] < count:
            logger.warning("Insufficient quota", user_id=user_id, remaining=quota["remaining"], requested=count)
            return False
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
        """Count applications submitted today for the given user."""
        async with get_db_context() as db:
            today = datetime.now(timezone.utc).date()
            result = await db.execute(
                select(func.count(Application.id)).where(
                    Application.user_id == user_id,
                    func.date(Application.created_at) == today,
                    Application.status.in_([
                        ApplicationStatus.APPLIED,
                        ApplicationStatus.QUEUED,
                        ApplicationStatus.APPLYING,
                        ApplicationStatus.PENDING_APPROVAL,
                    ]),
                )
            )
            return result.scalar() or 0


quota_service = QuotaService()
