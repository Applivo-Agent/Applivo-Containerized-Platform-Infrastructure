"""
app/models/user_settings.py
───────────────────────────
Unified user settings storage.
All settings are stored as structured JSON per section for flexibility
while maintaining type safety through Pydantic schemas.
"""
from __future__ import annotations

import enum
from datetime import datetime
from typing import Optional, List, Dict, Any

from sqlalchemy import (
    JSON, Boolean, DateTime, Enum, Float, ForeignKey,
    Integer, String, Text, UniqueConstraint, Index, text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import TimestampMixin, UUIDMixin


class AgentMode(str, enum.Enum):
    """Agent autonomy level."""
    MANUAL = "manual"
    SEMI_AUTO = "semi_auto"
    FULL_AUTO = "full_auto"


class AgentStrategy(str, enum.Enum):
    """Job application strategy."""
    AGGRESSIVE = "aggressive"
    BALANCED = "balanced"
    QUALITY = "quality"


class ScheduleInterval(str, enum.Enum):
    """Automation schedule interval."""
    MIN_30 = "30min"
    HOUR_1 = "1hour"
    HOUR_6 = "6hours"
    DAILY = "daily"


class AIProvider(str, enum.Enum):
    """AI model provider."""
    GROQ = "groq"
    GEMINI = "gemini"
    OPENROUTER = "openrouter"
    # Legacy values kept to avoid breaking existing rows
    OPENAI = "openai"
    ANTHROPIC = "anthropic"


class FallbackStrategy(str, enum.Enum):
    """Fallback provider selection strategy."""
    FASTEST = "fastest"
    BALANCED = "balanced"
    BEST_QUALITY = "best_quality"


class ReasoningDepth(str, enum.Enum):
    """AI reasoning depth for applications."""
    FAST = "fast"
    BALANCED = "balanced"
    DEEP = "deep"


class AppGenStyle(str, enum.Enum):
    """Cover letter / application generation style."""
    PROFESSIONAL = "professional"
    TECHNICAL = "technical"
    STARTUP = "startup"
    ENTERPRISE = "enterprise"


class NotificationFrequency(str, enum.Enum):
    """Notification digest frequency."""
    INSTANT = "instant"
    HOURLY = "hourly"
    DAILY = "daily"


class DashboardLayout(str, enum.Enum):
    """Dashboard density layout."""
    COMPACT = "compact"
    COMFORTABLE = "comfortable"
    SPACIOUS = "spacious"


class PlatformHealth(str, enum.Enum):
    """Platform connection health status."""
    HEALTHY = "healthy"
    WARNING = "warning"
    ERROR = "error"
    SYNCING = "syncing"
    DISCONNECTED = "disconnected"


class UserSettings(Base, UUIDMixin, TimestampMixin):
    """
    Unified user settings table.
    One row per user. All settings stored as structured JSON columns.
    """
    __tablename__ = "user_settings"
    __table_args__ = (
        UniqueConstraint("user_id", name="uq_user_settings_user"),
        Index("ix_user_settings_user_id", "user_id"),
    )

    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False, index=True,
    )

    # ── General ───────────────────────────────────────────────
    timezone: Mapped[str] = mapped_column(String(50), default="Asia/Kolkata", nullable=False)
    language: Mapped[str] = mapped_column(String(10), default="en", nullable=False)
    date_format: Mapped[str] = mapped_column(String(20), default="DD/MM/YYYY", nullable=False)
    theme: Mapped[str] = mapped_column(String(10), default="dark", nullable=False)
    dashboard_layout: Mapped[DashboardLayout] = mapped_column(
        Enum(DashboardLayout, name="dashboardlayout", values_callable=lambda obj: [e.value for e in obj]),
        default=DashboardLayout.COMFORTABLE, nullable=False,
    )

    # ── Notifications ───────────────────────────────────────
    # Stored as JSON for flexibility: {email: bool, telegram: bool, discord: bool, slack: bool}
    notification_channels: Mapped[Dict[str, Any]] = mapped_column(
        JSON, default=lambda: {"email": True, "telegram": False, "discord": False, "slack": False},
        nullable=False,
    )
    # Stored as JSON: {jobs_found: bool, application_submitted: bool, ...}
    notification_types: Mapped[Dict[str, Any]] = mapped_column(
        JSON, default=lambda: {
            "jobs_found": True,
            "application_submitted": True,
            "interview_invitation": True,
            "resume_analysis_completed": False,
            "weekly_summary": True,
            "ai_agent_alerts": True,
            "workflow_failures": True,
        },
        nullable=False,
    )
    notification_frequency: Mapped[NotificationFrequency] = mapped_column(
        Enum(NotificationFrequency, name="notificationfrequency", values_callable=lambda obj: [e.value for e in obj]),
        default=NotificationFrequency.INSTANT, nullable=False,
    )
    telegram_chat_id: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    notification_email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # ── Job Automation ──────────────────────────────────────
    agent_mode: Mapped[AgentMode] = mapped_column(
        Enum(AgentMode, name="agentmode", values_callable=lambda obj: [e.value for e in obj]),
        default=AgentMode.MANUAL, nullable=False,
    )
    auto_scrape_jobs: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    auto_analyze_jobs: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    auto_queue_jobs: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    auto_apply: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    daily_application_limit: Mapped[int] = mapped_column(Integer, default=10, nullable=False)
    weekly_application_limit: Mapped[int] = mapped_column(Integer, default=50, nullable=False)
    require_manual_approval: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    auto_approval_threshold: Mapped[int] = mapped_column(Integer, default=75, nullable=False)
    schedule_interval: Mapped[ScheduleInterval] = mapped_column(
        Enum(ScheduleInterval, name="scheduleinterval", values_callable=lambda obj: [e.value for e in obj]),
        default=ScheduleInterval.HOUR_6, nullable=False,
    )
    next_scheduled_run: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # ── Agent Strategy ──────────────────────────────────────
    agent_strategy: Mapped[AgentStrategy] = mapped_column(
        Enum(AgentStrategy, name="agentstrategy", values_callable=lambda obj: [e.value for e in obj]),
        default=AgentStrategy.BALANCED, nullable=False,
    )

    # ── AI Settings ─────────────────────────────────────────
    ai_provider: Mapped[AIProvider] = mapped_column(
        Enum(AIProvider, name="aiprovider", values_callable=lambda obj: [e.value for e in obj]),
        default=AIProvider.GROQ, nullable=False,
    )
    ai_model: Mapped[str] = mapped_column(String(100), default="auto", nullable=False)
    reasoning_depth: Mapped[ReasoningDepth] = mapped_column(
        Enum(ReasoningDepth, name="reasoningdepth", values_callable=lambda obj: [e.value for e in obj]),
        default=ReasoningDepth.BALANCED, nullable=False,
    )
    app_gen_style: Mapped[AppGenStyle] = mapped_column(
        Enum(AppGenStyle, name="appgenstyle", values_callable=lambda obj: [e.value for e in obj]),
        default=AppGenStyle.PROFESSIONAL, nullable=False,
    )
    fallback_enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    fallback_strategy: Mapped[FallbackStrategy] = mapped_column(
        Enum(FallbackStrategy, name="fallbackstrategy", values_callable=lambda obj: [e.value for e in obj]),
        default=FallbackStrategy.BALANCED, nullable=False,
    )

    # ── Platform Connections ──────────────────────────────
    # Stored as JSON: {linkedin: {connected, last_sync, health, ...}, ...}
    platform_connections: Mapped[Dict[str, Any]] = mapped_column(
        JSON, default=lambda: {
            "linkedin": {"connected": False, "last_sync": None, "health": "disconnected"},
            "internshala": {"connected": False, "last_sync": None, "health": "disconnected"},
            "indeed": {"connected": False, "last_sync": None, "health": "disconnected"},
            "naukri": {"connected": False, "last_sync": None, "health": "disconnected"},
        },
        nullable=False,
    )

    # ── Security ────────────────────────────────────────────
    two_factor_enabled: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    two_factor_secret: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    # API keys stored encrypted (encryption handled at service layer)
    api_keys: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    # Webhooks: [{id, url, events, secret, active, created_at}]
    webhooks: Mapped[Optional[List[Dict[str, Any]]]] = mapped_column(JSON, nullable=True)

    # ── Advanced ──────────────────────────────────────────────
    debug_mode: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    experimental_features: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Relationship
    user: Mapped["User"] = relationship("User", back_populates="settings")

    def __repr__(self) -> str:
        return f"<UserSettings user_id={self.user_id}>"


class SettingsAuditLog(Base, UUIDMixin, TimestampMixin):
    """
    Audit trail for every settings change.
    Immutable log of who changed what, when, from what, to what.
    """
    __tablename__ = "settings_audit_logs"
    __table_args__ = (
        Index("ix_audit_user_id", "user_id"),
        Index("ix_audit_setting_key", "setting_key"),
        Index("ix_audit_created_at", "created_at"),
    )

    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False, index=True,
    )
    setting_key: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    old_value: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    new_value: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    ip_address: Mapped[Optional[str]] = mapped_column(String(45), nullable=True)
    user_agent: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    source: Mapped[str] = mapped_column(String(20), default="web", nullable=False)
    # "web" | "api" | "worker" | "admin"

    def __repr__(self) -> str:
        return f"<SettingsAuditLog user={self.user_id} key={self.setting_key}>"
