"""
app/models/user.py
──────────────────
User account + rich profile.
The profile stores everything the AI agents need to know about the user:
skills, target roles, resume preferences, career goals.
"""

from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from sqlalchemy import (
    JSON,
    Boolean,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import SoftDeleteMixin, TimestampMixin, UUIDMixin

import enum


class ExperienceLevel(str, enum.Enum):
    ENTRY = "entry"
    MID = "mid"
    SENIOR = "senior"
    LEAD = "lead"
    EXECUTIVE = "executive"
    UNKNOWN = "unknown"


class User(Base, UUIDMixin, TimestampMixin, SoftDeleteMixin):
    """
    Core authentication entity.
    Single-user system initially — this stays for future multi-user expansion.
    """
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    google_id: Mapped[Optional[str]] = mapped_column(String(255), unique=True, nullable=True, index=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False)
    last_login_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    verified_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    password_reset_token: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, index=True)
    password_reset_expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    profile: Mapped[Optional["UserProfile"]] = relationship(
        "UserProfile", back_populates="user", uselist=False, cascade="all, delete-orphan"
    )
    resumes: Mapped[List["Resume"]] = relationship(
        "Resume", back_populates="user", cascade="all, delete-orphan"
    )
    applications: Mapped[List["Application"]] = relationship(
        "Application", back_populates="user", cascade="all, delete-orphan"
    )
    skills: Mapped[List["UserSkill"]] = relationship(
        "UserSkill", back_populates="user", cascade="all, delete-orphan"
    )
    sessions: Mapped[List["UserSession"]] = relationship(
        "UserSession", back_populates="user", cascade="all, delete-orphan"
    )
    credentials: Mapped[List["CredentialVault"]] = relationship(
        "CredentialVault", back_populates="user", cascade="all, delete-orphan"
    )
    consents: Mapped[List["UserConsent"]] = relationship(
        "UserConsent", back_populates="user", cascade="all, delete-orphan"
    )
    subscriptions: Mapped[List["Subscription"]] = relationship(
        "Subscription", back_populates="user", cascade="all, delete-orphan"
    )
    payments: Mapped[List["Payment"]] = relationship(
        "Payment", back_populates="user", cascade="all, delete-orphan"
    )
    platform_cookies: Mapped[List["PlatformCookie"]] = relationship(
        "PlatformCookie", back_populates="user", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<User id={self.id} email={self.email}>"


class UserProfile(Base, UUIDMixin, TimestampMixin):
    """
    Extended user career profile — fed into every AI prompt.
    Everything the agent needs to know to act on behalf of the user.
    """
    __tablename__ = "user_profiles"

    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), nullable=False, unique=True, index=True)

    # ── Contact Info ──────────────────────────────────────────
    phone: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    location: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    linkedin_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    github_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    portfolio_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    # ── Career Preferences ───────────────────────────────────
    experience_level: Mapped[ExperienceLevel] = mapped_column(
        Enum(ExperienceLevel, name="experiencelevel", values_callable=lambda obj: [e.value for e in obj]), 
        default=ExperienceLevel.ENTRY, 
        nullable=False
    )
    desired_roles: Mapped[List[str]] = mapped_column(JSON, default=list)
    desired_locations: Mapped[List[str]] = mapped_column(JSON, default=list)
    open_to_remote: Mapped[bool] = mapped_column(Boolean, default=True)
    open_to_hybrid: Mapped[bool] = mapped_column(Boolean, default=True)
    min_salary: Mapped[int] = mapped_column(Integer, default=0)
    preferred_company_size: Mapped[List[str]] = mapped_column(JSON, default=list)
    preferred_industries: Mapped[List[str]] = mapped_column(JSON, default=list)
    avoid_companies: Mapped[List[str]] = mapped_column(JSON, default=list)

    # ── Summary / Bio ────────────────────────────────────────
    professional_summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    career_goals: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    unique_value_proposition: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # ── Education ────────────────────────────────────────────
    education: Mapped[List[dict]] = mapped_column(JSON, default=list)
    # [{"degree": "B.Tech", "field": "AI", "institution": "...", "year": 2024, "gpa": 8.5}]

    # ── Work Experience ──────────────────────────────────────
    work_experience: Mapped[List[dict]] = mapped_column(JSON, default=list)
    # [{"title": "...", "company": "...", "start": "2023-01", "end": null, "bullets": [...]}]

    # ── Projects ─────────────────────────────────────────────
    projects: Mapped[List[dict]] = mapped_column(JSON, default=list)
    # [{"name": "...", "description": "...", "tech_stack": [...], "github": "...", "demo": "..."}]

    # ── Certifications / Awards ──────────────────────────────
    certifications: Mapped[List[dict]] = mapped_column(JSON, default=list)
    awards: Mapped[List[dict]] = mapped_column(JSON, default=list)

    # ── Publications / Research ──────────────────────────────
    publications: Mapped[List[dict]] = mapped_column(JSON, default=list)

    # ── Auto Apply Settings ──────────────────────────────────
    auto_apply_enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    auto_apply_threshold: Mapped[int] = mapped_column(Integer, default=75)
    auto_apply_daily_limit: Mapped[int] = mapped_column(Integer, default=10)
    require_apply_approval: Mapped[bool] = mapped_column(Boolean, default=True)

    # ── Notification Preferences ─────────────────────────────
    notify_new_jobs: Mapped[bool] = mapped_column(Boolean, default=True)
    notify_applications: Mapped[bool] = mapped_column(Boolean, default=True)
    notify_interviews: Mapped[bool] = mapped_column(Boolean, default=True)
    notify_via_telegram: Mapped[bool] = mapped_column(Boolean, default=True)
    notify_via_email: Mapped[bool] = mapped_column(Boolean, default=True)
    telegram_chat_id: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    notification_email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # ── Platform Credentials (encrypted in production) ───────
    linkedin_session_cookie: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    indeed_session_cookie: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationship
    user: Mapped["User"] = relationship("User", back_populates="profile")

    def __repr__(self) -> str:
        return f"<UserProfile user_id={self.user_id}>"


class UserSkill(Base, UUIDMixin, TimestampMixin):
    """
    Individual skill entry for the user.
    Separate table for querying/filtering by skill.
    """
    __tablename__ = "user_skills"
    __table_args__ = (UniqueConstraint("user_id", "name", name="uq_user_skill"),)

    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    category: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    # e.g. "programming", "ml_framework", "cloud", "tool", "soft_skill"
    proficiency: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    # "beginner" | "intermediate" | "advanced" | "expert"
    years_experience: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    is_primary: Mapped[bool] = mapped_column(Boolean, default=False)
    # Primary skills are weighted more heavily in job matching

    # Relationship
    user: Mapped["User"] = relationship("User", back_populates="skills")

    def __repr__(self) -> str:
        return f"<UserSkill {self.name} ({self.proficiency})>"


class UserSession(Base, UUIDMixin, TimestampMixin):
    """
    User session tracking for multi-device login and security.
    Tracks device info, IP, location, and allows session revocation.
    """
    __tablename__ = "user_sessions"
    __table_args__ = (
        UniqueConstraint("user_id", "device_id", name="uq_user_device_session"),
    )

    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    device_id: Mapped[str] = mapped_column(String(255), nullable=False)
    device_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    device_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    browser: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    os: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    ip_address: Mapped[Optional[str]] = mapped_column(String(45), nullable=True)
    location: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    user_agent: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    refresh_token_hash: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    refresh_token_expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    access_token_jti: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, index=True)
    last_used_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    is_current: Mapped[bool] = mapped_column(Boolean, default=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    user: Mapped["User"] = relationship("User", back_populates="sessions")

    def __repr__(self) -> str:
        return f"<UserSession user_id={self.user_id} device={self.device_name}>"

