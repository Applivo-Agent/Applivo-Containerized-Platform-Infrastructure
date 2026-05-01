"""
app/services/credit_service.py
─────────────────────────────
Credit service for tracking AI chat usage.
Manages monthly credits per user based on subscription tier.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

import structlog
from sqlalchemy import select

from app.core.database import get_db_context
from app.models.subscription import PlanTier, SubscriptionStatus
from app.services.subscription_service import subscription_service

logger = structlog.get_logger()


class CreditService:
    """Tracks and manages AI chat credits per user."""

    async def get_user_credits(self, user_id: str) -> dict:
        """
        Get current credit status for user.
        Returns: { allowed, reason, limit, used, remaining, is_unlimited }
        """
        # Check if user is superuser FIRST - they get unlimited always
        from app.models.user import User
        
        async with get_db_context() as db:
            user_result = await db.execute(select(User.is_superuser).where(User.id == user_id))
            is_superuser = user_result.scalar() or False
        
        # Superusers get unlimited - bypass subscription check
        if is_superuser:
            return {
                "allowed": True,
                "reason": None,
                "limit": 999999,
                "used": 0,
                "remaining": 999999,
                "is_unlimited": True,
            }
        
        sub = await subscription_service.get_active_subscription(user_id)
        
        if not sub:
            return {
                "allowed": False,
                "reason": "No active subscription",
                "limit": 0,
                "used": 0,
                "remaining": 0,
                "is_unlimited": False,
            }

        monthly_limit = sub.ai_credits

        # Get usage for current month
        used = await self._get_monthly_usage(user_id)
        remaining = max(0, monthly_limit - used)

        return {
            "allowed": remaining > 0,
            "reason": None if remaining > 0 else f"Monthly AI credits exhausted ({monthly_limit} used)",
            "limit": monthly_limit,
            "used": used,
            "remaining": remaining,
            "is_unlimited": False,
        }

    async def consume_credit(self, user_id: str) -> bool:
        """
        Consume one credit for AI chat.
        Returns True if credit was consumed, False if not allowed.
        """
        credits = await self.get_user_credits(user_id)
        
        if not credits["allowed"]:
            return False
        
        if credits["is_unlimited"]:
            return True
        
        month = datetime.now(timezone.utc).strftime("%Y-%m")
        
        async with get_db_context() as db:
            from app.models.chat_usage import ChatUsage
            result = await db.execute(
                select(ChatUsage).where(
                    ChatUsage.user_id == user_id,
                    ChatUsage.month == month
                )
            )
            usage = result.scalar_one_or_none()
            
            if usage:
                usage.message_count += 1
            else:
                usage = ChatUsage(user_id=user_id, month=month, message_count=1)
                db.add(usage)
            
            await db.commit()
        
        logger.info("AI credit consumed", user_id=user_id, remaining=credits["remaining"] - 1)
        return True

    async def _get_monthly_usage(self, user_id: str) -> int:
        """
        Get number of AI chat messages this month.
        """
        month = datetime.now(timezone.utc).strftime("%Y-%m")
        
        async with get_db_context() as db:
            from app.models.chat_usage import ChatUsage
            result = await db.execute(
                select(ChatUsage.message_count).where(
                    ChatUsage.user_id == user_id,
                    ChatUsage.month == month
                )
            )
            return result.scalar() or 0

    async def reset_monthly_credits(self, user_id: str) -> None:
        """
        Reset credit usage for a new month.
        Called by scheduled job at start of each month.
        """
        month = datetime.now(timezone.utc).strftime("%Y-%m")
        
        async with get_db_context() as db:
            from app.models.chat_usage import ChatUsage
            result = await db.execute(
                select(ChatUsage).where(
                    ChatUsage.user_id == user_id,
                    ChatUsage.month == month
                )
            )
            usage = result.scalar_one_or_none()
            
            if usage:
                usage.message_count = 0
                await db.commit()
                logger.info("Monthly credits reset", user_id=user_id, month=month)
            else:
                logger.info("No usage record to reset", user_id=user_id, month=month)


# Singleton instance
credit_service = CreditService()