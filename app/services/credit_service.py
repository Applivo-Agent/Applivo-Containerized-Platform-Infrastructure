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
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

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

        plan = PlanTier(sub.plan)
        monthly_limit = sub.ai_credits
        
        # Premium users get unlimited
        if plan == PlanTier.PREMIUM:
            return {
                "allowed": True,
                "reason": None,
                "limit": 999999,
                "used": 0,
                "remaining": 999999,
                "is_unlimited": True,
            }

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
        
        # For paid plans, we'd track the usage in a database table
        # For now, we'll just return True and log it
        logger.info("AI credit consumed", user_id=user_id, remaining=credits["remaining"])
        return True

    async def _get_monthly_usage(self, user_id: str) -> int:
        """
        Get number of AI chat messages this month.
        In production, this would query a credit_usage table.
        For now, we'll estimate based on chat history.
        """
        # TODO: Create a proper credit_usage tracking table
        # For now, return 0 (unlimited for demo until table is created)
        return 0

    async def reset_monthly_credits(self, user_id: str) -> None:
        """
        Reset credit usage for a new month.
        Called by scheduled job at start of each month.
        """
        # TODO: Implement with credit_usage table
        logger.info("Monthly credits reset", user_id=user_id)


# Singleton instance
credit_service = CreditService()