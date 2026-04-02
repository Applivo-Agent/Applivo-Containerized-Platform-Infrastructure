"""
app/api/routes/subscriptions.py
────────────────────────────────
Subscription management API routes.
Handles plan viewing, plan listing, and subscription management.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.api.routes.auth import get_current_user
from app.models.user import User
from app.models.subscription import (
    PlanTier,
    PLAN_PRICES,
    PLAN_DAILY_LIMITS,
    PLAN_PRIORITY,
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
                "price": PLAN_PRICES[PlanTier.STARTER],
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
                "price": PLAN_PRICES[PlanTier.PRO],
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
                "price": PLAN_PRICES[PlanTier.PREMIUM],
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
    """Get the user's current active subscription."""
    sub = await subscription_service.get_active_subscription(current_user.id)
    if not sub:
        return {"active": False, "plan": None, "subscription": None}

    features = await subscription_service.get_plan_features(current_user.id)
    return {
        "active": True,
        "subscription": {
            "id": sub.id,
            "plan": sub.plan if hasattr(sub, 'plan') else None,
            "status": sub.status.value if hasattr(sub.status, 'value') else sub.status,
            "start_date": sub.start_date.isoformat(),
            "end_date": sub.end_date.isoformat() if sub.end_date else None,
            "daily_limit": sub.daily_limit,
            "price": sub.price,
        },
        "features": features,
    }


@router.post("/cancel")
async def cancel_subscription(
    current_user: User = Depends(get_current_user),
):
    """Cancel the user's active subscription."""
    sub = await subscription_service.cancel_subscription(current_user.id)
    if not sub:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No active subscription found",
        )
    return {"message": "Subscription cancelled", "subscription_id": sub.id}
