"""
app/services/subscription_service.py
─────────────────────────────────────
Manages user subscription lifecycle: activation, expiration, plan checks.
Enforces plan-based access control across all platform features.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Optional

import structlog
from sqlalchemy import select, String, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db_context
from app.models.subscription import (
    PlanTier,
    Subscription,
    SubscriptionStatus,
    PLAN_DAILY_LIMITS,
    PLAN_PRIORITY,
)
from app.models.user import User

logger = structlog.get_logger()


class SubscriptionService:

    async def get_active_subscription(
        self, user_id: str, db:Optional[AsyncSession] = None,
    ) -> Optional[Subscription]:
        """Get the user's currently active subscription (including trials)."""
        async def _query(session: AsyncSession) -> Optional[Subscription]:
            result = await session.execute(
                select(Subscription)
                .where(
                    Subscription.user_id == user_id,
                    func.lower(Subscription.status.cast(String)).in_([
                        SubscriptionStatus.ACTIVE.value.lower(),
                        "success",
                        SubscriptionStatus.TRIAL.value.lower(),
                        SubscriptionStatus.PENDING.value.lower(),
                    ])
                )
                .order_by(Subscription.created_at.desc())
                .limit(1)
            )
            sub = result.scalar_one_or_none()
            if sub:
                # Check if subscription/trial has expired
                if sub.status == SubscriptionStatus.TRIAL and sub.trial_end_date:
                    trial_end = sub.trial_end_date.replace(tzinfo=timezone.utc) if sub.trial_end_date.tzinfo is None else sub.trial_end_date
                    if trial_end < datetime.now(timezone.utc):
                        sub.status = SubscriptionStatus.TRIAL_EXPIRED
                        await session.commit()
                        logger.info("Trial expired", user_id=user_id, sub_id=sub.id)
                        return None
                elif sub.end_date:
                    end_date = sub.end_date.replace(tzinfo=timezone.utc) if sub.end_date.tzinfo is None else sub.end_date
                    if end_date < datetime.now(timezone.utc):
                        sub.status = SubscriptionStatus.EXPIRED
                        await session.commit()
                        logger.info("Subscription expired", user_id=user_id, sub_id=sub.id)
                        return None
            return sub

        if db:
            return await _query(db)
        async with get_db_context() as session:
            return await _query(session)

    async def create_subscription(
        self,
        user_id: str,
        plan: PlanTier,
        duration_days: int = 30,
        razorpay_subscription_id: Optional[str] = None,
    ) -> Subscription:
        """Create a new subscription for the user. Deactivates any existing active subscription."""
        async with get_db_context() as db:
            existing = await self.get_active_subscription(user_id, db)
            if existing:
                existing.status = SubscriptionStatus.CANCELLED
                logger.info("Cancelled previous subscription", sub_id=existing.id)

            now = datetime.now(timezone.utc)
            sub = Subscription(
                user_id=user_id,
                plan=plan,
                status=SubscriptionStatus.ACTIVE,
                start_date=now,
                end_date=now + timedelta(days=duration_days),
                razorpay_subscription_id=razorpay_subscription_id,
            )
            db.add(sub)
            await db.commit()
            await db.refresh(sub)
            logger.info("Subscription created", user_id=user_id, plan=plan.value, sub_id=sub.id)
            return sub

    async def cancel_subscription(self, user_id: str) -> Optional[Subscription]:
        """Cancel the user's active subscription."""
        async with get_db_context() as db:
            sub = await self.get_active_subscription(user_id, db)
            if not sub:
                return None
            sub.status = SubscriptionStatus.CANCELLED
            await db.commit()
            logger.info("Subscription cancelled", user_id=user_id, sub_id=sub.id)
            return sub

    async def create_trial_subscription(self, user_id: str) -> Optional[Subscription]:
        """
        Create a 7-day free trial subscription for a new user.
        Returns None if user has already had a trial before.
        """
        async with get_db_context() as db:
            # Check if user has ever had a trial
            result = await db.execute(
                select(Subscription).where(
                    Subscription.user_id == user_id,
                    Subscription.is_trial == True,
                )
            )
            existing_trial = result.scalar_one_or_none()
            if existing_trial:
                logger.info("User already had a trial", user_id=user_id)
                return None
            
            # Create trial subscription
            now = datetime.now(timezone.utc)
            sub = Subscription(
                user_id=user_id,
                plan=PlanTier.STARTER,
                status=SubscriptionStatus.TRIAL,
                is_trial=True,
                start_date=now,
                end_date=now + timedelta(days=7),
                trial_end_date=now + timedelta(days=7),
            )
            db.add(sub)
            await db.commit()
            await db.refresh(sub)
            logger.info("Trial subscription created", user_id=user_id, sub_id=sub.id)
            return sub

    async def renew_subscription(
        self, user_id: str, duration_days: int = 30,
    ) -> Optional[Subscription]:
        """Renew the user's current subscription by extending the end date."""
        async with get_db_context() as db:
            sub = await self.get_active_subscription(user_id, db)
            if not sub:
                return None
            now = datetime.now(timezone.utc)
            if sub.end_date and sub.end_date > now:
                sub.end_date = sub.end_date + timedelta(days=duration_days)
            else:
                sub.end_date = now + timedelta(days=duration_days)
            sub.status = SubscriptionStatus.ACTIVE
            await db.commit()
            logger.info("Subscription renewed", user_id=user_id, sub_id=sub.id)
            return sub

    async def check_access(self, user_id: str, required_plan: Optional[PlanTier] = None) -> bool:
        """Check if user has an active subscription. Optionally require a minimum plan tier."""
        sub = await self.get_active_subscription(user_id)
        if not sub or not sub.is_active():
            return False
        if required_plan:
            current_priority = PLAN_PRIORITY.get(PlanTier(sub.plan), 0)
            required_priority = PLAN_PRIORITY.get(required_plan, 0)
            return current_priority >= required_priority
        return True

    async def get_daily_limit(self, user_id: str) -> int:
        """Get the daily application limit for the user's plan."""
        sub = await self.get_active_subscription(user_id)
        if not sub:
            return 0
        return PLAN_DAILY_LIMITS.get(PlanTier(sub.plan), 0)

    async def get_plan_features(self, user_id: str) -> dict:
        """Return feature flags for the user's current plan."""
        sub = await self.get_active_subscription(user_id)
        if not sub or not sub.is_active():
            return {"active": False, "plan": None}

        plan = PlanTier(sub.plan)
        features = {
            "active": True,
            "plan": plan.value,
            "daily_limit": PLAN_DAILY_LIMITS.get(plan, 0),
            "priority": PLAN_PRIORITY.get(plan, 0),
            "job_scraping": True,
            "auto_apply": True,
            "resume_upload": True,
            "email_notifications": True,
            "analytics_dashboard": True,
        }

        if plan == PlanTier.STARTER:
            features.update({
                "platforms": ["internshala"],
                "ai_answers": "basic",
                "cover_letter_generator": False,
                "telegram_notifications": False,
                "interview_tracking": False,
                "email_monitoring": False,
                "follow_up_automation": False,
                "priority_processing": False,
            })
        elif plan == PlanTier.PRO:
            features.update({
                "platforms": ["internshala"],
                "ai_answers": "full",
                "cover_letter_generator": True,
                "telegram_notifications": True,
                "interview_tracking": True,
                "email_monitoring": True,
                "follow_up_automation": True,
                "priority_processing": True,
            })
        elif plan == PlanTier.PREMIUM:
            features.update({
                "platforms": ["internshala"],
                "ai_answers": "advanced",
                "cover_letter_generator": True,
                "telegram_notifications": True,
                "interview_tracking": True,
                "email_monitoring": True,
                "follow_up_automation": True,
                "priority_processing": True,
                "highest_priority_queue": True,
                "advanced_analytics": True,
            })

        return features


subscription_service = SubscriptionService()
