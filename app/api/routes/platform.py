"""
app/api/routes/platform.py
──────────────────────────
Platform connection API routes.
Handles cookie management for Internshala (and future platforms).
"""

from __future__ import annotations
from typing import Union
import asyncio
import json

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, status
from pydantic import BaseModel
from sqlalchemy import select

from app.api.routes.auth import get_current_user
from app.models.user import User
from app.models.cookie import PlatformCookie
from app.core.database import get_db_context
from app.services.cookie_service import cookie_service

router = APIRouter(prefix="/platform", tags=["Platform Connection"])


class LoginRequest(BaseModel):
    email: str = ""
    password: str = ""


class SaveCookiesRequest(BaseModel):
    platform: str
    cookies: Union[dict, list, str]


class ValidateCookiesRequest(BaseModel):
    platform: str


@router.get("/status")
async def platform_status(
    current_user: User = Depends(get_current_user),
):
    """Get the status of all platform connections for the user."""
    platforms = await cookie_service.list_platforms(current_user.id)
    return {"platforms": platforms}


async def _run_internshala_login(user_id: str, email: str, password: str):
    """Background task to run login - allows longer timeout."""
    from app.services.internshala_login_service import internshala_login_service
    await internshala_login_service.login_and_save_cookies(user_id, email, password)


async def _ensure_no_existing_platform_connection(user_id: str, platform: str) -> None:
    """Require users to delete an existing connection before adding/replacing one."""
    async with get_db_context() as db:
        result = await db.execute(
            select(PlatformCookie).where(
                PlatformCookie.user_id == user_id,
                PlatformCookie.platform == platform,
            )
        )
        existing = result.scalar_one_or_none()

    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                f"{platform.capitalize()} is already connected. "
                "Please delete the existing connection first."
            ),
        )


def _normalize_cookie_payload(cookies: Union[dict, list, str]) -> Union[dict, list]:
    """Normalize browser cookie input into the JSON shape Playwright consumers expect."""
    if isinstance(cookies, (dict, list)):
        return cookies

    if not isinstance(cookies, str):
        raise ValueError("Unsupported cookie format")

    raw = cookies.strip()
    if not raw:
        raise ValueError("Cookie payload is empty")

    if raw.startswith("[") or raw.startswith("{"):
        try:
            parsed = json.loads(raw)
            if isinstance(parsed, (dict, list)):
                return parsed
        except json.JSONDecodeError:
            pass

    cookie_items = []
    for part in raw.split(";"):
        chunk = part.strip()
        if not chunk or "=" not in chunk:
            continue
        name, value = chunk.split("=", 1)
        name = name.strip()
        value = value.strip()
        if not name:
            continue
        cookie_items.append(
            {
                "name": name,
                "value": value,
                "domain": ".internshala.com",
                "path": "/",
            }
        )

    if not cookie_items:
        raise ValueError("Could not parse cookie string. Paste a document.cookie value or JSON cookie array.")

    return cookie_items


@router.post("/login/{platform}")
async def login_platform(
    platform: str,
    data: LoginRequest,
    current_user: User = Depends(get_current_user),
):
    """
    Log into a platform - user manually logs in, we capture cookies.
    Currently supports: internshala
    """
    if platform != "internshala":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Platform '{platform}' login not supported yet. Supported: internshala",
        )

    await _ensure_no_existing_platform_connection(current_user.id, platform)
    
    from app.services.internshala_login_service import internshala_login_service
    
    result = await internshala_login_service.login_and_save_cookies(
        user_id=current_user.id,
        email=data.email,
        password=data.password,
    )
    
    if not result.get("success"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result.get("message", "Login failed"),
        )
    
    return {
        "connected": True,
        "platform": platform,
        "message": result.get("message"),
        "cookies_count": result.get("cookies_count"),
    }


@router.post("/connect")
async def connect_platform(
    data: SaveCookiesRequest,
    current_user: User = Depends(get_current_user),
):
    """Save platform cookies for automation. Encrypts and stores cookies server-side."""
    try:
        await _ensure_no_existing_platform_connection(current_user.id, data.platform)
        normalized_cookies = _normalize_cookie_payload(data.cookies)
        cookie = await cookie_service.save_cookies(
            user_id=current_user.id,
            platform=data.platform,
            cookies=normalized_cookies,
        )
        return {
            "connected": True,
            "platform": data.platform,
            "cookie_id": cookie.id,
            "message": f"Successfully connected to {data.platform}",
        }
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/upload-cookies")
async def upload_cookies(
    data: SaveCookiesRequest,
    current_user: User = Depends(get_current_user),
):
    """Alias for /connect for the cookie-paste flow in the UI."""
    return await connect_platform(data, current_user)


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


@router.post("/test-connection/{platform}")
async def test_platform_connection(
    platform: str,
    current_user: User = Depends(get_current_user),
):
    """
    Test whether stored platform cookies are valid and the session is active.
    Returns detailed diagnostics to help debug connection issues.
    """
    from app.services.cookie_service import cookie_service
    
    # 1. Check if cookies exist
    validation = await cookie_service.validate_cookies(current_user.id, platform)
    if not validation["valid"]:
        return {
            "connected": False,
            "platform": platform,
            "reason": validation["reason"],
            "diagnostics": {
                "cookies_exist": False,
                "login_tested": False,
                "recommendation": "Please connect your account via the dashboard Settings → Connect Accounts page.",
            },
        }
    
    # 2. Try a lightweight browser check (Internshala only for now)
    if platform == "internshala":
        try:
            from playwright.async_api import async_playwright
            cookie_data = await cookie_service.get_cookies(current_user.id, platform)
            cookies = cookie_data.get("cookies") if cookie_data else None
            fingerprint = cookie_data.get("fingerprint") if cookie_data else None
            
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True, args=["--no-sandbox"])
                context_kwargs = {}
                if fingerprint:
                    fp_ua = fingerprint.get("user_agent")
                    fp_vp = fingerprint.get("viewport")
                    if fp_ua:
                        context_kwargs["user_agent"] = fp_ua
                    if fp_vp and isinstance(fp_vp, dict) and "width" in fp_vp and "height" in fp_vp:
                        context_kwargs["viewport"] = fp_vp
                context = await browser.new_context(**context_kwargs)
                if cookies and isinstance(cookies, list):
                    await context.add_cookies(cookies)
                
                page = await context.new_page()
                await page.goto("https://internshala.com/student/dashboard", timeout=30000)
                
                # Check if we're actually on the dashboard (logged in)
                url = page.url
                has_login_form = await page.query_selector("input[type='password']") is not None
                has_dashboard = "dashboard" in url or await page.query_selector(".dashboard-container") is not None
                
                await browser.close()
                
                if has_dashboard and not has_login_form:
                    return {
                        "connected": True,
                        "platform": platform,
                        "reason": "Session is active and valid",
                        "diagnostics": {
                            "cookies_exist": True,
                            "login_tested": True,
                            "page_url": url,
                            "has_dashboard": True,
                        },
                    }
                else:
                    # Mark cookies invalid since they failed the real test
                    await cookie_service.invalidate_cookies(current_user.id, platform)
                    return {
                        "connected": False,
                        "platform": platform,
                        "reason": "Session expired or blocked (redirected to login)",
                        "diagnostics": {
                            "cookies_exist": True,
                            "login_tested": True,
                            "page_url": url,
                            "has_dashboard": False,
                            "has_login_form": has_login_form,
                            "recommendation": "Please re-upload your cookies or use the login form to reconnect.",
                        },
                    }
        except Exception as e:
            return {
                "connected": False,
                "platform": platform,
                "reason": f"Browser test failed: {str(e)[:200]}",
                "diagnostics": {
                    "cookies_exist": True,
                    "login_tested": False,
                    "error": str(e)[:500],
                },
            }
    
    # For unsupported platforms, just return cookie validation result
    return {
        "connected": validation["valid"],
        "platform": platform,
        "reason": validation.get("reason", "Unknown"),
        "diagnostics": {"cookies_exist": validation["valid"]},
    }


@router.post("/scan/messages/{platform}")
async def trigger_message_scan(
    platform: str = "internshala",
    current_user: User = Depends(get_current_user),
):
    """Trigger a message scan for the current user."""
    from app.services.message_scanner_service import message_scanner_service
    
    result = await message_scanner_service.scan_user_messages(current_user.id, platform)
    
    return {"message": f"Message scan completed for {platform}", "platform": platform, "result": result}


@router.get("/messages")
async def get_platform_messages(
    platform: str = "internshala",
    status: str = "all",
    limit: int = 50,
    current_user: User = Depends(get_current_user),
):
    """Get user's platform messages."""
    from app.models.platform_message import PlatformMessage
    from app.core.database import get_db_context
    from sqlalchemy import select, desc
    
    async with get_db_context() as db:
        query = select(PlatformMessage).where(
            PlatformMessage.user_id == current_user.id,
            PlatformMessage.platform == platform,
        )
        
        # Only filter by status if not "all"
        if status != "all":
            query = query.where(PlatformMessage.status == status)
        
        result = await db.execute(
            query.order_by(desc(PlatformMessage.received_at)).limit(limit)
        )
        messages = result.scalars().all()
    
    return [
        {
            "id": m.id,
            "sender": m.sender_name,
            "subject": m.subject,
            "content": m.content[:200],
            "is_important": m.is_important,
            "importance_keywords": m.importance_keywords,
            "status": m.status,
            "received_at": m.received_at.isoformat() if m.received_at else None,
        }
        for m in messages
    ]
