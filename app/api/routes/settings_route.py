"""
app/api/routes/settings_route.py
─────────────────────────────────
Settings API — read from .env, persist changes to user profile in DB.
Add to app/main.py: 
    from app.api.routes.settings_route import settings_router
    app.include_router(settings_router, prefix="/api")
"""
from __future__ import annotations
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from typing import Optional
from pathlib import Path
import os

from app.core.database import get_db
from app.api.routes.auth import get_current_user
from app.models.user import User, UserProfile
from app.core.config import settings

settings_router = APIRouter(prefix="/settings", tags=["Settings"])


class AutoApplyUpdate(BaseModel):
    enabled: Optional[bool] = None
    threshold: Optional[int] = None
    daily_limit: Optional[int] = None
    require_approval: Optional[bool] = None


@settings_router.get("")
async def get_settings_endpoint(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(UserProfile).where(UserProfile.user_id == current_user.id)
    )
    profile = result.scalar_one_or_none()
    return {
        "auto_apply_enabled": profile.auto_apply_enabled if profile else settings.AUTO_APPLY_ENABLED,
        "auto_apply_threshold": profile.auto_apply_threshold if profile else settings.AUTO_APPLY_MATCH_THRESHOLD,
        "auto_apply_daily_limit": profile.auto_apply_daily_limit if profile else settings.AUTO_APPLY_DAILY_LIMIT,
        "require_apply_approval": profile.require_apply_approval if profile else settings.AUTO_APPLY_REQUIRE_APPROVAL,
        "scrape_interval_hours": settings.SCRAPE_INTERVAL_HOURS,
        "telegram_configured": bool(settings.TELEGRAM_BOT_TOKEN),
        "email_configured": bool(settings.SMTP_USERNAME),
        "openai_configured": bool(settings.OPENAI_API_KEY),
        "groq_configured": bool(getattr(settings, 'GROQ_API_KEY', '')),
        "notify_via_email": profile.notify_via_email if profile else True,
        "notify_via_telegram": profile.notify_via_telegram if profile else True,
    }


@settings_router.patch("")
async def patch_settings_endpoint(
    payload: dict,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update settings via PATCH."""
    result = await db.execute(
        select(UserProfile).where(UserProfile.user_id == current_user.id)
    )
    profile = result.scalar_one_or_none()
    if not profile:
        raise HTTPException(404, "Profile not found — complete onboarding first")

    if "auto_apply_threshold" in payload:
        profile.auto_apply_threshold = payload["auto_apply_threshold"]
    if "require_apply_approval" in payload:
        profile.require_apply_approval = payload["require_apply_approval"]
    if "auto_apply_enabled" in payload:
        profile.auto_apply_enabled = payload["auto_apply_enabled"]
    if "notify_via_email" in payload:
        profile.notify_via_email = payload["notify_via_email"]
    if "notify_via_telegram" in payload:
        profile.notify_via_telegram = payload["notify_via_telegram"]

    await db.commit()
    return {"success": True}


@settings_router.put("/auto-apply")
async def update_auto_apply(
    payload: AutoApplyUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(UserProfile).where(UserProfile.user_id == current_user.id)
    )
    profile = result.scalar_one_or_none()
    if not profile:
        raise HTTPException(404, "Profile not found — complete onboarding first")

    if payload.enabled is not None:
        profile.auto_apply_enabled = payload.enabled
    if payload.threshold is not None:
        profile.auto_apply_threshold = payload.threshold
    if payload.daily_limit is not None:
        profile.auto_apply_daily_limit = payload.daily_limit
    if payload.require_approval is not None:
        profile.require_apply_approval = payload.require_approval

    await db.commit()
    return {"success": True}