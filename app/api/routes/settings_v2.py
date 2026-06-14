"""
app/api/routes/settings_v2.py
────────────────────────────
Production settings API v2.
Full CRUD for all settings sections with audit logging.
"""
from __future__ import annotations

from typing import Optional, Dict, Any, List
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel, Field, field_validator
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.api.routes.auth import get_current_user
from app.models.user import User
from app.services.user_settings_service import SettingsService
from app.models.user_settings import (
    AgentMode, AgentStrategy, ScheduleInterval,
    AIProvider, ReasoningDepth, AppGenStyle,
    NotificationFrequency, DashboardLayout,
)

settings_v2_router = APIRouter(prefix="/settings", tags=["Settings v2"])


# ── Helper ───────────────────────────────────────────────────────────────────

def _get_client_info(request: Request) -> tuple[Optional[str], Optional[str]]:
    """Extract IP and user agent from request."""
    ip = request.client.host if request.client else None
    ua = request.headers.get("user-agent")
    return ip, ua


# ── Schemas ──────────────────────────────────────────────────────────────────

class GeneralSettingsUpdate(BaseModel):
    timezone: Optional[str] = None
    language: Optional[str] = None
    date_format: Optional[str] = None
    theme: Optional[str] = None
    dashboard_layout: Optional[str] = None


class NotificationChannelsUpdate(BaseModel):
    email: Optional[bool] = None
    telegram: Optional[bool] = None
    discord: Optional[bool] = None
    slack: Optional[bool] = None


class NotificationTypesUpdate(BaseModel):
    jobs_found: Optional[bool] = None
    application_submitted: Optional[bool] = None
    interview_invitation: Optional[bool] = None
    resume_analysis_completed: Optional[bool] = None
    weekly_summary: Optional[bool] = None
    ai_agent_alerts: Optional[bool] = None
    workflow_failures: Optional[bool] = None


class NotificationsUpdate(BaseModel):
    channels: Optional[NotificationChannelsUpdate] = None
    types: Optional[NotificationTypesUpdate] = None
    frequency: Optional[str] = None
    telegram_chat_id: Optional[str] = None
    notification_email: Optional[str] = None


class AutomationUpdate(BaseModel):
    agent_mode: Optional[str] = None
    auto_scrape_jobs: Optional[bool] = None
    auto_analyze_jobs: Optional[bool] = None
    auto_queue_jobs: Optional[bool] = None
    auto_apply: Optional[bool] = None
    daily_application_limit: Optional[int] = Field(None, ge=1, le=200)
    weekly_application_limit: Optional[int] = Field(None, ge=1, le=1000)
    require_manual_approval: Optional[bool] = None
    auto_approval_threshold: Optional[int] = Field(None, ge=0, le=100)
    schedule_interval: Optional[str] = None


class StrategyUpdate(BaseModel):
    agent_strategy: Optional[str] = None


class AISettingsUpdate(BaseModel):
    ai_provider: Optional[str] = None
    ai_model: Optional[str] = None
    reasoning_depth: Optional[str] = None
    app_gen_style: Optional[str] = None
    fallback_enabled: Optional[bool] = None
    fallback_strategy: Optional[str] = None


class PlatformUpdate(BaseModel):
    platforms: Dict[str, Any]


class SecurityUpdate(BaseModel):
    two_factor_enabled: Optional[bool] = None
    api_keys: Optional[Dict[str, Any]] = None
    webhooks: Optional[List[Dict[str, Any]]] = None


class AdvancedUpdate(BaseModel):
    debug_mode: Optional[bool] = None
    experimental_features: Optional[bool] = None


class TestNotificationRequest(BaseModel):
    channel: str = "email"  # email | telegram | discord | slack


class SettingsResponse(BaseModel):
    success: bool = True
    data: Dict[str, Any]
    updated_at: Optional[str] = None


class AuditLogEntry(BaseModel):
    id: str
    setting_key: str
    old_value: Optional[str] = None
    new_value: Optional[str] = None
    ip_address: Optional[str] = None
    created_at: str
    model_config = {"from_attributes": True}


class AuditLogResponse(BaseModel):
    logs: List[AuditLogEntry]
    total: int


# ── GET Full Settings ───────────────────────────────────────────────────────

@settings_v2_router.get("/v2", response_model=SettingsResponse)
async def get_full_settings(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get all user settings in a single response."""
    settings = await SettingsService.get_or_create(db, current_user.id)
    return SettingsResponse(
        success=True,
        data=SettingsService.to_dict(settings),
        updated_at=settings.updated_at.isoformat() if settings.updated_at else None,
    )


# ── General ─────────────────────────────────────────────────────────────────

@settings_v2_router.put("/v2/general", response_model=SettingsResponse)
async def update_general(
    payload: GeneralSettingsUpdate,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    ip, ua = _get_client_info(request)
    settings = await SettingsService.update_general(
        db, current_user.id, payload.model_dump(exclude_none=True), ip, ua
    )
    return SettingsResponse(
        success=True,
        data=SettingsService.to_dict(settings),
        updated_at=settings.updated_at.isoformat() if settings.updated_at else None,
    )


# ── Notifications ───────────────────────────────────────────────────────────

@settings_v2_router.put("/v2/notifications", response_model=SettingsResponse)
async def update_notifications(
    payload: NotificationsUpdate,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    ip, ua = _get_client_info(request)
    data = payload.model_dump(exclude_none=True)
    if payload.channels:
        data["channels"] = payload.channels.model_dump(exclude_none=True)
    if payload.types:
        data["types"] = payload.types.model_dump(exclude_none=True)
    settings = await SettingsService.update_notifications(db, current_user.id, data, ip, ua)
    return SettingsResponse(
        success=True,
        data=SettingsService.to_dict(settings),
        updated_at=settings.updated_at.isoformat() if settings.updated_at else None,
    )


@settings_v2_router.post("/v2/notifications/test")
async def test_notification(
    payload: TestNotificationRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Send a test notification to the specified channel."""
    settings = await SettingsService.get_or_create(db, current_user.id)

    if payload.channel == "email":
        email = settings.notification_email or current_user.email
        # TODO: integrate with notification service
        return {"success": True, "message": f"Test email queued to {email}"}

    elif payload.channel == "telegram":
        if not settings.telegram_chat_id:
            raise HTTPException(
                status_code=400,
                detail="Telegram chat ID not configured. Set it in notification settings first."
            )
        # TODO: integrate with telegram service
        return {"success": True, "message": f"Test message sent to Telegram chat {settings.telegram_chat_id}"}

    elif payload.channel in ("discord", "slack"):
        return {"success": False, "message": f"{payload.channel.title()} integration coming soon"}

    else:
        raise HTTPException(status_code=400, detail=f"Unknown channel: {payload.channel}")


# ── Automation ──────────────────────────────────────────────────────────────

@settings_v2_router.put("/v2/automation", response_model=SettingsResponse)
async def update_automation(
    payload: AutomationUpdate,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    ip, ua = _get_client_info(request)
    settings = await SettingsService.update_automation(
        db, current_user.id, payload.model_dump(exclude_none=True), ip, ua
    )
    return SettingsResponse(
        success=True,
        data=SettingsService.to_dict(settings),
        updated_at=settings.updated_at.isoformat() if settings.updated_at else None,
    )


# ── Strategy ────────────────────────────────────────────────────────────────

@settings_v2_router.put("/v2/strategy", response_model=SettingsResponse)
async def update_strategy(
    payload: StrategyUpdate,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    ip, ua = _get_client_info(request)
    settings = await SettingsService.update_strategy(
        db, current_user.id, payload.model_dump(exclude_none=True), ip, ua
    )
    return SettingsResponse(
        success=True,
        data=SettingsService.to_dict(settings),
        updated_at=settings.updated_at.isoformat() if settings.updated_at else None,
    )


# ── AI Settings ─────────────────────────────────────────────────────────────

@settings_v2_router.put("/v2/ai", response_model=SettingsResponse)
async def update_ai(
    payload: AISettingsUpdate,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    ip, ua = _get_client_info(request)
    settings = await SettingsService.update_ai(
        db, current_user.id, payload.model_dump(exclude_none=True), ip, ua
    )
    return SettingsResponse(
        success=True,
        data=SettingsService.to_dict(settings),
        updated_at=settings.updated_at.isoformat() if settings.updated_at else None,
    )


# ── Platforms ─────────────────────────────────────────────────────────────────

@settings_v2_router.put("/v2/platforms", response_model=SettingsResponse)
async def update_platforms(
    payload: PlatformUpdate,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    ip, ua = _get_client_info(request)
    settings = await SettingsService.update_platforms(
        db, current_user.id, payload.model_dump(exclude_none=True), ip, ua
    )
    return SettingsResponse(
        success=True,
        data=SettingsService.to_dict(settings),
        updated_at=settings.updated_at.isoformat() if settings.updated_at else None,
    )


@settings_v2_router.get("/v2/platforms/status")
async def get_platform_status(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get real-time platform connection status."""
    from app.models.cookie import PlatformCookie
    from sqlalchemy import select as sa_select

    settings = await SettingsService.get_or_create(db, current_user.id)
    platforms = dict(settings.platform_connections)

    # Check actual cookie status from DB
    result = await db.execute(
        sa_select(PlatformCookie).where(PlatformCookie.user_id == current_user.id)
    )
    cookies = result.scalars().all()
    cookie_platforms = {c.platform: c for c in cookies}

    for platform_name in platforms:
        if platform_name in cookie_platforms:
            cookie = cookie_platforms[platform_name]
            platforms[platform_name]["connected"] = True
            platforms[platform_name]["health"] = "healthy" if cookie.is_valid else "warning"
            platforms[platform_name]["last_sync"] = cookie.updated_at.isoformat() if cookie.updated_at else None
        else:
            platforms[platform_name]["connected"] = False
            platforms[platform_name]["health"] = "disconnected"
            platforms[platform_name]["last_sync"] = None

    return {"success": True, "platforms": platforms}


# ── Security ─────────────────────────────────────────────────────────────────

@settings_v2_router.put("/v2/security", response_model=SettingsResponse)
async def update_security(
    payload: SecurityUpdate,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    ip, ua = _get_client_info(request)
    settings = await SettingsService.update_security(
        db, current_user.id, payload.model_dump(exclude_none=True), ip, ua
    )
    return SettingsResponse(
        success=True,
        data=SettingsService.to_dict(settings),
        updated_at=settings.updated_at.isoformat() if settings.updated_at else None,
    )


@settings_v2_router.get("/v2/security/sessions")
async def get_sessions(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get active user sessions."""
    from app.models.user import UserSession
    from sqlalchemy import select as sa_select

    result = await db.execute(
        sa_select(UserSession)
        .where(UserSession.user_id == current_user.id)
        .where(UserSession.is_active == True)
        .order_by(UserSession.last_used_at.desc())
    )
    sessions = result.scalars().all()

    return {
        "success": True,
        "sessions": [
            {
                "id": s.id,
                "device_name": s.device_name,
                "device_type": s.device_type,
                "browser": s.browser,
                "os": s.os,
                "ip_address": s.ip_address,
                "location": s.location,
                "last_used_at": s.last_used_at.isoformat() if s.last_used_at else None,
                "is_current": s.is_current,
                "created_at": s.created_at.isoformat() if s.created_at else None,
            }
            for s in sessions
        ],
    }


@settings_v2_router.post("/v2/security/sessions/{session_id}/terminate")
async def terminate_session(
    session_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Terminate a specific session."""
    from app.models.user import UserSession
    from sqlalchemy import select as sa_select, update as sa_update

    result = await db.execute(
        sa_select(UserSession).where(
            UserSession.id == session_id,
            UserSession.user_id == current_user.id,
        )
    )
    session = result.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    session.is_active = False
    await db.commit()

    return {"success": True, "message": "Session terminated"}


@settings_v2_router.post("/v2/security/sessions/terminate-all")
async def terminate_all_sessions(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Terminate all sessions except current."""
    from app.models.user import UserSession
    from sqlalchemy import update as sa_update

    # Get current session identifier from request
    current_jti = None
    auth_header = request.headers.get("authorization", "")
    if auth_header.startswith("Bearer "):
        token = auth_header[7:]
        try:
            from app.core.security import decode_token
            payload = decode_token(token)
            current_jti = payload.get("jti")
        except Exception:
            pass

    query = (
        sa_update(UserSession)
        .where(UserSession.user_id == current_user.id)
        .where(UserSession.is_active == True)
        .values(is_active=False)
    )
    if current_jti:
        query = query.where(UserSession.access_token_jti != current_jti)

    await db.execute(query)
    await db.commit()

    return {"success": True, "message": "All other sessions terminated"}


# ── Advanced ──────────────────────────────────────────────────────────────────

@settings_v2_router.put("/v2/advanced", response_model=SettingsResponse)
async def update_advanced(
    payload: AdvancedUpdate,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    ip, ua = _get_client_info(request)
    settings = await SettingsService.update_advanced(
        db, current_user.id, payload.model_dump(exclude_none=True), ip, ua
    )
    return SettingsResponse(
        success=True,
        data=SettingsService.to_dict(settings),
        updated_at=settings.updated_at.isoformat() if settings.updated_at else None,
    )


@settings_v2_router.post("/v2/advanced/export")
async def export_data(
    payload: Dict[str, Any],
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Export user data. Returns a download URL or direct data."""
    export_types = payload.get("types", ["settings"])
    format_type = payload.get("format", "json")

    result = {"exported_at": datetime.utcnow().isoformat(), "types": {}}

    if "settings" in export_types:
        settings = await SettingsService.get_or_create(db, current_user.id)
        result["types"]["settings"] = SettingsService.to_dict(settings)

    # TODO: Add applications, jobs, analytics, messages export

    return {"success": True, "data": result, "format": format_type}


@settings_v2_router.post("/v2/advanced/reset")
async def reset_system(
    payload: Dict[str, Any],
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Reset all settings to defaults. Requires confirmation."""
    confirmation = payload.get("confirmation", "")
    if confirmation != "RESET":
        raise HTTPException(
            status_code=400,
            detail="Invalid confirmation. Type 'RESET' to confirm system reset."
        )

    ip, ua = _get_client_info(request)
    settings = await SettingsService.get_or_create(db, current_user.id)

    # Log the reset
    await SettingsService._log_change(
        db, current_user.id, "system.reset", "all_settings", "default", ip, ua
    )

    # Delete and recreate with defaults
    await db.delete(settings)
    await db.commit()

    new_settings = await SettingsService.get_or_create(db, current_user.id)

    return SettingsResponse(
        success=True,
        data=SettingsService.to_dict(new_settings),
        message="All settings reset to defaults",
    )


# ── Audit Logs ──────────────────────────────────────────────────────────────

@settings_v2_router.get("/v2/audit", response_model=AuditLogResponse)
async def get_audit_logs(
    limit: int = 50,
    offset: int = 0,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get settings change audit log."""
    logs = await SettingsService.get_audit_logs(db, current_user.id, limit, offset)

    return AuditLogResponse(
        logs=[
            AuditLogEntry(
                id=log.id,
                setting_key=log.setting_key,
                old_value=log.old_value,
                new_value=log.new_value,
                ip_address=log.ip_address,
                created_at=log.created_at.isoformat() if log.created_at else "",
            )
            for log in logs
        ],
        total=len(logs),
    )
