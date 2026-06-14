"""
app/api/routes/subscriptions.py
────────────────────────────────
Subscription management API routes.
Handles plan viewing, plan listing, and subscription management.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import structlog
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

logger = structlog.get_logger()

from app.core.database import get_db
from app.api.routes.auth import get_current_user
from app.models.user import User
from app.models.subscription import (
    PlanTier,
    PLAN_PRICES,
    PLAN_DAILY_LIMITS,
    PLAN_PRIORITY,
    PLAN_MONTHLY_AI_CREDITS,
    Subscription,
    SubscriptionStatus,
)
from app.services.subscription_service import subscription_service

router = APIRouter(prefix="/subscriptions", tags=["Subscriptions"])


@router.get("/plans")
async def list_plans():
    """List all available subscription plans with pricing and features."""
    return {
        "plans": [
            {
                "id": "starter",
                "name": "Starter",
                "price": PLAN_PRICES[PlanTier.STARTER] // 100,  # Convert paise to rupees
                "currency": "INR",
                "duration_days": 30,
                "daily_limit": PLAN_DAILY_LIMITS[PlanTier.STARTER],
                "priority": PLAN_PRIORITY[PlanTier.STARTER],
                "features": {
                    "job_scraping": True,
                    "auto_apply": True,
                    "basic_ai_answers": True,
                    "resume_upload": True,
                    "email_notifications": True,
                    "analytics_dashboard": True,
                    "platforms": ["internshala"],
                    "follow_up_automation": False,
                    "priority_processing": False,
                    "email_monitoring": False,
                },
            },
            {
                "id": "pro",
                "name": "Pro",
                "price": PLAN_PRICES[PlanTier.PRO] // 100,  # Convert paise to rupees
                "currency": "INR",
                "duration_days": 30,
                "daily_limit": PLAN_DAILY_LIMITS[PlanTier.PRO],
                "priority": PLAN_PRIORITY[PlanTier.PRO],
                "features": {
                    "job_scraping": True,
                    "auto_apply": True,
                    "full_ai_answers": True,
                    "resume_upload": True,
                    "cover_letter_generator": True,
                    "email_notifications": True,
                    "telegram_notifications": True,
                    "interview_tracking": True,
                    "email_monitoring": True,
                    "follow_up_automation": True,
                    "priority_processing": True,
                    "analytics_dashboard": True,
                    "platforms": ["internshala"],
                },
            },
            {
                "id": "premium",
                "name": "Premium",
                "price": PLAN_PRICES[PlanTier.PREMIUM] // 100,  # Convert paise to rupees
                "currency": "INR",
                "duration_days": 30,
                "daily_limit": PLAN_DAILY_LIMITS[PlanTier.PREMIUM],
                "priority": PLAN_PRIORITY[PlanTier.PREMIUM],
                "features": {
                    "job_scraping": True,
                    "auto_apply": True,
                    "advanced_ai_answers": True,
                    "resume_upload": True,
                    "cover_letter_generator": True,
                    "email_notifications": True,
                    "telegram_notifications": True,
                    "interview_tracking": True,
                    "email_monitoring": True,
                    "follow_up_automation": True,
                    "highest_priority_queue": True,
                    "advanced_analytics": True,
                    "analytics_dashboard": True,
                    "platforms": ["internshala"],
                },
            },
        ]
    }


@router.get("/current")
async def get_current_subscription(
    current_user: User = Depends(get_current_user),
):
    """Get the user's current active subscription with trial details."""
    sub = await subscription_service.get_active_subscription(current_user.id)
    if not sub:
        return {"active": False, "plan": None, "subscription": None}

    features = await subscription_service.get_plan_features(current_user.id)
    
    # Calculate trial days remaining
    trial_days_remaining = 0
    if sub.status == SubscriptionStatus.TRIAL and sub.trial_end_date:
        trial_end = sub.trial_end_date.replace(tzinfo=timezone.utc) if sub.trial_end_date.tzinfo is None else sub.trial_end_date
        now = datetime.now(timezone.utc)
        trial_days_remaining = max(0, (trial_end - now).days)
    
    return {
        "active": True,
        "subscription": {
            "id": sub.id,
            "plan": sub.plan if hasattr(sub, 'plan') else None,
            "status": sub.status.value if hasattr(sub.status, 'value') else sub.status,
            "is_trial": sub.is_trial if hasattr(sub, 'is_trial') else False,
            "trial_days_remaining": trial_days_remaining,
            "trial_end_date": sub.trial_end_date.isoformat() if sub.trial_end_date else None,
            "start_date": sub.start_date.isoformat(),
            "end_date": sub.end_date.isoformat() if sub.end_date else None,
            "daily_limit": sub.daily_limit,
            "autopay_enabled": bool(sub.razorpay_subscription_id),
            "ai_credits": sub.ai_credits,
        },
        "features": features,
    }


@router.post("/activate/free")
async def activate_free_plan(
    current_user: User = Depends(get_current_user),
):
    """Activate free starter plan for testing. Admin only."""
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Admin only")
    
    from app.models.subscription import Subscription, SubscriptionStatus
    from app.core.database import get_db_context
    
    async with get_db_context() as db:
        existing = await db.execute(
            select(Subscription).where(Subscription.user_id == current_user.id)
        )
        existing_sub = existing.scalar_one_or_none()
        
        if existing_sub:
            existing_sub.status = SubscriptionStatus.ACTIVE
            existing_sub.plan = PlanTier.STARTER
            existing_sub.start_date = datetime.now(timezone.utc)
            existing_sub.end_date = datetime.now(timezone.utc) + timedelta(days=30)
        else:
            sub = Subscription(
                user_id=current_user.id,
                plan=PlanTier.STARTER,
                status=SubscriptionStatus.ACTIVE,
                start_date=datetime.now(timezone.utc),
                end_date=datetime.now(timezone.utc) + timedelta(days=30),
            )
            db.add(sub)
        
        await db.commit()
    
    return {"active": True, "plan": "starter", "message": "Free plan activated for testing"}


@router.post("/cancel")
async def cancel_subscription(
    current_user: User = Depends(get_current_user),
):
    """Cancel the user's active subscription (including Razorpay autopay if linked)."""
    from app.services.payment_service import payment_service

    active = await subscription_service.get_active_subscription(current_user.id)
    if not active:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No active subscription found",
        )

    # Cancel Razorpay subscription if one exists (best-effort, don't block on failure)
    if active.razorpay_subscription_id:
        try:
            await payment_service.cancel_razorpay_subscription(active.razorpay_subscription_id)
        except Exception as e:
            logger.warning("Failed to cancel Razorpay subscription", error=str(e),
                           razorpay_id=active.razorpay_subscription_id)

    sub = await subscription_service.cancel_subscription(current_user.id)
    return {"message": "Subscription cancelled", "subscription_id": sub.id}
