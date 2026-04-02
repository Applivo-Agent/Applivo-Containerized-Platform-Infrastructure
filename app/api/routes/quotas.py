"""
app/api/routes/quotas.py
─────────────────────────
Quota management API routes.
Returns daily application limits and usage based on subscription tier.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends

from app.api.routes.auth import get_current_user
from app.models.user import User
from app.services.quota_service import quota_service

router = APIRouter(prefix="/quota", tags=["Quota"])


@router.get("/")
async def get_quota(
    current_user: User = Depends(get_current_user),
):
    """Get the user's daily quota status including remaining applications."""
    return await quota_service.get_quota_with_details(current_user.id)


@router.get("/check")
async def check_can_apply(
    current_user: User = Depends(get_current_user),
):
    """Quick check if the user can submit another application today."""
    return await quota_service.check_quota(current_user.id)
