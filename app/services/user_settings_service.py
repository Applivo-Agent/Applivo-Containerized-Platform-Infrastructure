"""
app/services/user_settings_service.py
─────────────────────────────────────
Production-grade settings service.
Handles CRUD, validation, audit logging, and cache invalidation.
"""
from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.postgresql import insert as pg_insert

from app.models.user_settings import (
    UserSettings, SettingsAuditLog,
    AgentMode, AgentStrategy, ScheduleInterval,
    AIProvider, ReasoningDepth, AppGenStyle,
    NotificationFrequency, DashboardLayout, PlatformHealth,
)
from app.models.user import User


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class SettingsService:
    """Production settings service with audit logging."""

    @staticmethod
    async def get_or_create(
        db: AsyncSession,
        user_id: str,
    ) -> UserSettings:
        """Get user settings or create with defaults."""
        result = await db.execute(
            select(UserSettings).where(UserSettings.user_id == user_id)
        )
        settings = result.scalar_one_or_none()
        if not settings:
            settings = UserSettings(user_id=user_id)
            db.add(settings)
            await db.commit()
            await db.refresh(settings)
        return settings

    @staticmethod
    async def get(db: AsyncSession, user_id: str) -> Optional[UserSettings]:
        result = await db.execute(
            select(UserSettings).where(UserSettings.user_id == user_id)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def update_general(
        db: AsyncSession,
        user_id: str,
        data: Dict[str, Any],
        ip: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> UserSettings:
        settings = await SettingsService.get_or_create(db, user_id)
        changes = {}

        field_map = {
            "timezone": "timezone",
            "language": "language",
            "date_format": "date_format",
            "theme": "theme",
            "dashboard_layout": "dashboard_layout",
        }

        for key, attr in field_map.items():
            if key in data and data[key] is not None:
                old_val = getattr(settings, attr)
                new_val = data[key]
                if old_val != new_val:
                    setattr(settings, attr, new_val)
                    changes[attr] = (old_val, new_val)

        await db.commit()
        await db.refresh(settings)

        for attr, (old, new) in changes.items():
            await SettingsService._log_change(
                db, user_id, f"general.{attr}", old, new, ip, user_agent
            )

        return settings

    @staticmethod
    async def update_notifications(
        db: AsyncSession,
        user_id: str,
        data: Dict[str, Any],
        ip: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> UserSettings:
        settings = await SettingsService.get_or_create(db, user_id)
        changes = {}

        if "channels" in data:
            old = dict(settings.notification_channels)
            new = {**old, **data["channels"]}
            settings.notification_channels = new
            changes["notification_channels"] = (old, new)

        if "types" in data:
            old = dict(settings.notification_types)
            new = {**old, **data["types"]}
            settings.notification_types = new
            changes["notification_types"] = (old, new)

        if "frequency" in data and data["frequency"] is not None:
            old_val = settings.notification_frequency.value
            new_val = data["frequency"]
            if old_val != new_val:
                settings.notification_frequency = NotificationFrequency(new_val)
                changes["notification_frequency"] = (old_val, new_val)

        if "telegram_chat_id" in data:
            old_val = settings.telegram_chat_id
            new_val = data["telegram_chat_id"]
            if old_val != new_val:
                settings.telegram_chat_id = new_val
                changes["telegram_chat_id"] = (old_val, new_val)

        if "notification_email" in data:
            old_val = settings.notification_email
            new_val = data["notification_email"]
            if old_val != new_val:
                settings.notification_email = new_val
                changes["notification_email"] = (old_val, new_val)

        await db.commit()
        await db.refresh(settings)

        for attr, (old, new) in changes.items():
            await SettingsService._log_change(
                db, user_id, f"notifications.{attr}", old, new, ip, user_agent
            )

        return settings

    @staticmethod
    async def update_automation(
        db: AsyncSession,
        user_id: str,
        data: Dict[str, Any],
        ip: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> UserSettings:
        settings = await SettingsService.get_or_create(db, user_id)
        changes = {}

        bool_fields = {
            "auto_scrape_jobs": "auto_scrape_jobs",
            "auto_analyze_jobs": "auto_analyze_jobs",
            "auto_queue_jobs": "auto_queue_jobs",
            "auto_apply": "auto_apply",
            "require_manual_approval": "require_manual_approval",
        }
        for key, attr in bool_fields.items():
            if key in data and data[key] is not None:
                old_val = getattr(settings, attr)
                new_val = data[key]
                if old_val != new_val:
                    setattr(settings, attr, new_val)
                    changes[attr] = (old_val, new_val)

        int_fields = {
            "daily_application_limit": "daily_application_limit",
            "weekly_application_limit": "weekly_application_limit",
            "auto_approval_threshold": "auto_approval_threshold",
        }
        for key, attr in int_fields.items():
            if key in data and data[key] is not None:
                old_val = getattr(settings, attr)
                new_val = data[key]
                if old_val != new_val:
                    setattr(settings, attr, new_val)
                    changes[attr] = (old_val, new_val)

        if "agent_mode" in data and data["agent_mode"] is not None:
            old_val = settings.agent_mode.value
            new_val = data["agent_mode"]
            if old_val != new_val:
                settings.agent_mode = AgentMode(new_val)
                changes["agent_mode"] = (old_val, new_val)

        if "schedule_interval" in data and data["schedule_interval"] is not None:
            old_val = settings.schedule_interval.value
            new_val = data["schedule_interval"]
            if old_val != new_val:
                settings.schedule_interval = ScheduleInterval(new_val)
                changes["schedule_interval"] = (old_val, new_val)

        await db.commit()
        await db.refresh(settings)

        for attr, (old, new) in changes.items():
            await SettingsService._log_change(
                db, user_id, f"automation.{attr}", old, new, ip, user_agent
            )

        return settings

    @staticmethod
    async def update_strategy(
        db: AsyncSession,
        user_id: str,
        data: Dict[str, Any],
        ip: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> UserSettings:
        settings = await SettingsService.get_or_create(db, user_id)
        changes = {}

        if "agent_strategy" in data and data["agent_strategy"] is not None:
            old_val = settings.agent_strategy.value
            new_val = data["agent_strategy"]
            if old_val != new_val:
                settings.agent_strategy = AgentStrategy(new_val)
                changes["agent_strategy"] = (old_val, new_val)

        await db.commit()
        await db.refresh(settings)

        for attr, (old, new) in changes.items():
            await SettingsService._log_change(
                db, user_id, f"strategy.{attr}", old, new, ip, user_agent
            )

        return settings

    @staticmethod
    async def update_ai(
        db: AsyncSession,
        user_id: str,
        data: Dict[str, Any],
        ip: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> UserSettings:
        settings = await SettingsService.get_or_create(db, user_id)
        changes = {}

        if "ai_provider" in data and data["ai_provider"] is not None:
            old_val = settings.ai_provider.value
            new_val = data["ai_provider"]
            if old_val != new_val:
                settings.ai_provider = AIProvider(new_val)
                changes["ai_provider"] = (old_val, new_val)

        if "ai_model" in data and data["ai_model"] is not None:
            old_val = settings.ai_model
            new_val = data["ai_model"]
            if old_val != new_val:
                settings.ai_model = new_val
                changes["ai_model"] = (old_val, new_val)

        if "reasoning_depth" in data and data["reasoning_depth"] is not None:
            old_val = settings.reasoning_depth.value
            new_val = data["reasoning_depth"]
            if old_val != new_val:
                settings.reasoning_depth = ReasoningDepth(new_val)
                changes["reasoning_depth"] = (old_val, new_val)

        if "app_gen_style" in data and data["app_gen_style"] is not None:
            old_val = settings.app_gen_style.value
            new_val = data["app_gen_style"]
            if old_val != new_val:
                settings.app_gen_style = AppGenStyle(new_val)
                changes["app_gen_style"] = (old_val, new_val)

        if "fallback_enabled" in data and data["fallback_enabled"] is not None:
            old_val = settings.fallback_enabled
            new_val = data["fallback_enabled"]
            if old_val != new_val:
                settings.fallback_enabled = new_val
                changes["fallback_enabled"] = (old_val, new_val)

        if "fallback_strategy" in data and data["fallback_strategy"] is not None:
            from app.models.user_settings import FallbackStrategy
            old_val = settings.fallback_strategy.value
            new_val = data["fallback_strategy"]
            if old_val != new_val:
                settings.fallback_strategy = FallbackStrategy(new_val)
                changes["fallback_strategy"] = (old_val, new_val)

        await db.commit()
        await db.refresh(settings)

        for attr, (old, new) in changes.items():
            await SettingsService._log_change(
                db, user_id, f"ai.{attr}", old, new, ip, user_agent
            )

        return settings

    @staticmethod
    async def update_platforms(
        db: AsyncSession,
        user_id: str,
        data: Dict[str, Any],
        ip: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> UserSettings:
        settings = await SettingsService.get_or_create(db, user_id)
        changes = {}

        if "platforms" in data:
            old = dict(settings.platform_connections)
            new = {**old}
            for platform, pdata in data["platforms"].items():
                if platform in new:
                    new[platform] = {**new[platform], **pdata}
                else:
                    new[platform] = pdata
            settings.platform_connections = new
            changes["platform_connections"] = (old, new)

        await db.commit()
        await db.refresh(settings)

        for attr, (old, new) in changes.items():
            await SettingsService._log_change(
                db, user_id, f"platforms.{attr}", old, new, ip, user_agent
            )

        return settings

    @staticmethod
    async def update_security(
        db: AsyncSession,
        user_id: str,
        data: Dict[str, Any],
        ip: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> UserSettings:
        settings = await SettingsService.get_or_create(db, user_id)
        changes = {}

        if "two_factor_enabled" in data and data["two_factor_enabled"] is not None:
            old_val = settings.two_factor_enabled
            new_val = data["two_factor_enabled"]
            if old_val != new_val:
                settings.two_factor_enabled = new_val
                changes["two_factor_enabled"] = (old_val, new_val)

        if "api_keys" in data:
            old_val = settings.api_keys
            new_val = data["api_keys"]
            if old_val != new_val:
                settings.api_keys = new_val
                changes["api_keys"] = (old_val, new_val)

        if "webhooks" in data:
            old_val = settings.webhooks
            new_val = data["webhooks"]
            if old_val != new_val:
                settings.webhooks = new_val
                changes["webhooks"] = (old_val, new_val)

        await db.commit()
        await db.refresh(settings)

        for attr, (old, new) in changes.items():
            await SettingsService._log_change(
                db, user_id, f"security.{attr}", old, new, ip, user_agent
            )

        return settings

    @staticmethod
    async def update_advanced(
        db: AsyncSession,
        user_id: str,
        data: Dict[str, Any],
        ip: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> UserSettings:
        settings = await SettingsService.get_or_create(db, user_id)
        changes = {}

        if "debug_mode" in data and data["debug_mode"] is not None:
            old_val = settings.debug_mode
            new_val = data["debug_mode"]
            if old_val != new_val:
                settings.debug_mode = new_val
                changes["debug_mode"] = (old_val, new_val)

        if "experimental_features" in data and data["experimental_features"] is not None:
            old_val = settings.experimental_features
            new_val = data["experimental_features"]
            if old_val != new_val:
                settings.experimental_features = new_val
                changes["experimental_features"] = (old_val, new_val)

        await db.commit()
        await db.refresh(settings)

        for attr, (old, new) in changes.items():
            await SettingsService._log_change(
                db, user_id, f"advanced.{attr}", old, new, ip, user_agent
            )

        return settings

    @staticmethod
    async def get_audit_logs(
        db: AsyncSession,
        user_id: str,
        limit: int = 100,
        offset: int = 0,
    ) -> List[SettingsAuditLog]:
        result = await db.execute(
            select(SettingsAuditLog)
            .where(SettingsAuditLog.user_id == user_id)
            .order_by(SettingsAuditLog.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return list(result.scalars().all())

    @staticmethod
    async def _log_change(
        db: AsyncSession,
        user_id: str,
        setting_key: str,
        old_value: Any,
        new_value: Any,
        ip: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> None:
        """Create an immutable audit log entry."""
        log = SettingsAuditLog(
            user_id=user_id,
            setting_key=setting_key,
            old_value=json.dumps(old_value, default=str) if old_value is not None else None,
            new_value=json.dumps(new_value, default=str) if new_value is not None else None,
            ip_address=ip,
            user_agent=user_agent,
        )
        db.add(log)
        await db.commit()

    @staticmethod
    def to_dict(settings: UserSettings) -> Dict[str, Any]:
        """Serialize settings to frontend-friendly dict."""
        return {
            # General
            "timezone": settings.timezone,
            "language": settings.language,
            "date_format": settings.date_format,
            "theme": settings.theme,
            "dashboard_layout": settings.dashboard_layout.value,

            # Notifications
            "channels": settings.notification_channels,
            "types": settings.notification_types,
            "frequency": settings.notification_frequency.value,
            "telegram_chat_id": settings.telegram_chat_id,
            "notification_email": settings.notification_email,

            # Automation
            "agent_mode": settings.agent_mode.value,
            "auto_scrape_jobs": settings.auto_scrape_jobs,
            "auto_analyze_jobs": settings.auto_analyze_jobs,
            "auto_queue_jobs": settings.auto_queue_jobs,
            "auto_apply": settings.auto_apply,
            "daily_application_limit": settings.daily_application_limit,
            "weekly_application_limit": settings.weekly_application_limit,
            "require_manual_approval": settings.require_manual_approval,
            "auto_approval_threshold": settings.auto_approval_threshold,
            "schedule_interval": settings.schedule_interval.value,
            "next_scheduled_run": settings.next_scheduled_run.isoformat() if settings.next_scheduled_run else None,

            # Strategy
            "agent_strategy": settings.agent_strategy.value,

            # AI
            "ai_provider": settings.ai_provider.value,
            "ai_model": settings.ai_model,
            "reasoning_depth": settings.reasoning_depth.value,
            "app_gen_style": settings.app_gen_style.value,
            "fallback_enabled": settings.fallback_enabled,
            "fallback_strategy": settings.fallback_strategy.value,

            # Platforms
            "platforms": settings.platform_connections,

            # Security
            "two_factor_enabled": settings.two_factor_enabled,
            "api_keys": settings.api_keys,
            "webhooks": settings.webhooks,

            # Advanced
            "debug_mode": settings.debug_mode,
            "experimental_features": settings.experimental_features,

            # Metadata
            "created_at": settings.created_at.isoformat() if settings.created_at else None,
            "updated_at": settings.updated_at.isoformat() if settings.updated_at else None,
        }
