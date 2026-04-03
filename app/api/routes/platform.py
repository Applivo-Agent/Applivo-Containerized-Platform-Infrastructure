"""
app/api/routes/platform.py
───────────────────────────
Platform connection API routes.
Handles cookie management for Internshala (and future platforms).
"""

from __future__ import annotations
from typing import Union

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from app.api.routes.auth import get_current_user
from app.models.user import User
from app.services.cookie_service import cookie_service

router = APIRouter(prefix="/platform", tags=["Platform Connection"])


class SaveCookiesRequest(BaseModel):
    platform: str
    cookies: Union[dict, list]


class ValidateCookiesRequest(BaseModel):
    platform: str


@router.get("/status")
async def platform_status(
    current_user: User = Depends(get_current_user),
):
    """Get the status of all platform connections for the user."""
    platforms = await cookie_service.list_platforms(current_user.id)
    return {"platforms": platforms}


@router.post("/connect")
async def connect_platform(
    data: SaveCookiesRequest,
    current_user: User = Depends(get_current_user),
):
    """Save platform cookies for automation. Encrypts and stores cookies server-side."""
    try:
        cookie = await cookie_service.save_cookies(
            user_id=current_user.id,
            platform=data.platform,
            cookies=data.cookies,
        )
        return {
            "connected": True,
            "platform": data.platform,
            "cookie_id": cookie.id,
            "message": f"Successfully connected to {data.platform}",
        }
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/validate")
async def validate_platform(
    data: ValidateCookiesRequest,
    current_user: User = Depends(get_current_user),
):
    """Validate if the platform cookies are still valid."""
    result = await cookie_service.validate_cookies(
        user_id=current_user.id,
        platform=data.platform,
    )
    return result


@router.delete("/disconnect/{platform}")
async def disconnect_platform(
    platform: str,
    current_user: User = Depends(get_current_user),
):
    """Disconnect a platform by deleting its cookies."""
    deleted = await cookie_service.delete_cookies(
        user_id=current_user.id,
        platform=platform,
    )
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No connection found for platform: {platform}",
        )
    return {"disconnected": True, "platform": platform}


@router.post("/invalidate/{platform}")
async def invalidate_platform(
    platform: str,
    current_user: User = Depends(get_current_user),
):
    """Mark platform cookies as invalid (e.g., when session expires)."""
    await cookie_service.invalidate_cookies(
        user_id=current_user.id,
        platform=platform,
    )
    return {"invalidated": True, "platform": platform}
