"""
app/models/application.py
──────────────────────────
Application tracking system — the core of Module 6.
Full state machine: Applied → Viewed → Shortlisted → Interview → Offer / Rejected.
Every state transition is logged in ApplicationEvent for full audit history.
"""

from __future__ import annotations

import enum
from datetime import datetime
from typing import List, Optional

from sqlalchemy import (
    ForeignKey,
    JSON,
    Boolean,
    DateTime,
    Enum,
    Float,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import TimestampMixin, UUIDMixin


# ── Enums ────────────────────────────────────────────────────────────────────

class ApplicationStatus(str, enum.Enum):
    PENDING_APPROVAL = "pending_approval"   # Waiting for user to approve auto-apply
    QUEUED = "queued"                       # Approved, queued for bot
    APPLYING = "applying"                   # Bot is currently applying
    APPLIED = "applied"                     # Successfully submitted
    VIEWED = "viewed"                       # Recruiter viewed application
    SHORTLISTED = "shortlisted"             # Made it to shortlist
    INTERVIEW_SCHEDULED = "interview_scheduled"
    INTERVIEW_COMPLETED = "interview_completed"
    OFFER_RECEIVED = "offer_received"
    OFFER_ACCEPTED = "offer_accepted"
    OFFER_DECLINED = "offer_declined"
    REJECTED = "rejected"
    WITHDRAWN = "withdrawn"                 # User withdrew application
    FAILED = "failed"                       # Bot failed to apply


class ApplicationMethod(str, enum.Enum):
    AUTO_BOT = "auto_bot"           # Playwright auto-apply
    EASY_APPLY = "easy_apply"       # LinkedIn Easy Apply
    MANUAL = "manual"               # User applied manually, logged here
    EMAIL = "email"                 # Applied via email


class FollowUpStatus(str, enum.Enum):
    NONE = "none"
    SCHEDULED = "scheduled"
    SENT = "sent"
    RESPONDED = "responded"


# ── Models ───────────────────────────────────────────────────────────────────

class Application(Base, UUIDMixin, TimestampMixin):
    """
    Single job application with full lifecycle tracking.
    """
    __tablename__ = "applications"

    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    job_id: Mapped[str] = mapped_column(String(36), ForeignKey("jobs.id"), nullable=False, index=True)
    resume_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("resumes.id"), nullable=True, index=True)
    cover_letter_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)

    # ── Status ────────────────────────────────────────────────
    status: Mapped[str] = mapped_column(
        Enum(ApplicationStatus),
        default=ApplicationStatus.QUEUED,
        nullable=False,
        index=True,
    )
    method: Mapped[str] = mapped_column(
        Enum(ApplicationMethod),
        default=ApplicationMethod.AUTO_BOT,
        nullable=False,
    )

    # ── Key Dates ─────────────────────────────────────────────
    applied_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    viewed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    shortlisted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    interview_scheduled_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    offer_received_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    rejected_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # ── Application Context (snapshot at apply time) ──────────
    match_score_at_apply: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    job_title_snapshot: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    company_snapshot: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # ── Recruiter ─────────────────────────────────────────────
    recruiter_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True, index=True)
    recruiter_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    recruiter_email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    recruiter_linkedin: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    # ── Follow-up ─────────────────────────────────────────────
    follow_up_status: Mapped[str] = mapped_column(
        Enum(FollowUpStatus), default=FollowUpStatus.NONE, nullable=False
    )
    follow_up_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    follow_up_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    last_follow_up_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # ── Interview Details ─────────────────────────────────────
    interview_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    interview_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    # "phone" | "video" | "onsite" | "technical" | "hr"
    interview_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    interview_feedback: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # ── Offer Details ─────────────────────────────────────────
    offer_salary: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    offer_details: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    # {"salary": 100000, "equity": "0.1%", "bonus": 10000, "benefits": [...]}

    # ── Bot Execution Info ────────────────────────────────────
    bot_session_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    bot_error: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    bot_screenshot_path: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)
    retry_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # ── User Notes ────────────────────────────────────────────
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_starred: Mapped[bool] = mapped_column(Boolean, default=False)
    # User can star priority applications

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="applications")
    job: Mapped["Job"] = relationship("Job", back_populates="applications")
    resume: Mapped[Optional["Resume"]] = relationship("Resume", back_populates="applications")
    events: Mapped[List["ApplicationEvent"]] = relationship(
        "ApplicationEvent", back_populates="application", cascade="all, delete-orphan",
        order_by="ApplicationEvent.created_at"
    )
    interviews: Mapped[List["Interview"]] = relationship(
        "Interview", back_populates="application", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Application {self.company_snapshot} - {self.job_title_snapshot} [{self.status}]>"


class ApplicationEvent(Base, UUIDMixin, TimestampMixin):
    """
    Immutable audit log of every state change in an application.
    Answers: what happened, when, and what triggered it.
    """
    __tablename__ = "application_events"

    application_id: Mapped[str] = mapped_column(String(36), ForeignKey("applications.id"), nullable=False, index=True)

    event_type: Mapped[str] = mapped_column(String(100), nullable=False)
    # e.g. "status_changed", "follow_up_sent", "bot_started", "captcha_detected"

    from_status: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    to_status: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    triggered_by: Mapped[str] = mapped_column(String(50), nullable=False)
    # "agent" | "user" | "system" | "webhook"

    details: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    # Flexible payload: error messages, metadata, bot output, etc.

    # Relationship
    application: Mapped["Application"] = relationship("Application", back_populates="events")

    def __repr__(self) -> str:
        return f"<ApplicationEvent {self.event_type} [{self.from_status} → {self.to_status}]>"
