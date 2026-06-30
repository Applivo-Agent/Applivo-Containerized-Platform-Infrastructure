"""
app/models/outreach.py
──────────────────────
Outreach Platform data models.
Covers: Company Workspaces, Contacts, Campaigns, Emails, Conversations, Connectors.
"""
from __future__ import annotations

import enum
from datetime import datetime
from typing import List, Optional

from sqlalchemy import (
    JSON, Boolean, DateTime, Enum, Float, ForeignKey,
    Integer, String, Text, UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import TimestampMixin, UUIDMixin


# ── Enums ─────────────────────────────────────────────────────────────────────

class OutreachCompanyPriority(str, enum.Enum):
    HOT = "HOT"
    WARM = "WARM"
    COLD = "COLD"

class OutreachCompanyStatus(str, enum.Enum):
    WATCHING = "WATCHING"
    RESEARCHING = "RESEARCHING"
    RESEARCHED = "RESEARCHED"
    CONTACTED = "CONTACTED"
    REPLIED = "REPLIED"
    INTERVIEWING = "INTERVIEWING"
    OFFER = "OFFER"
    ARCHIVED = "ARCHIVED"

class OutreachResearchStatus(str, enum.Enum):
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETE = "COMPLETE"
    FAILED = "FAILED"

class OutreachContactRoleType(str, enum.Enum):
    RECRUITER = "RECRUITER"
    HIRING_MANAGER = "HIRING_MANAGER"
    CTO = "CTO"
    FOUNDER = "FOUNDER"
    TEAM_LEAD = "TEAM_LEAD"
    OTHER = "OTHER"

class OutreachContactEmailValidity(str, enum.Enum):
    VERIFIED = "VERIFIED"
    PROBABLE = "PROBABLE"
    UNVERIFIED = "UNVERIFIED"
    INVALID = "INVALID"

class OutreachContactRelationship(str, enum.Enum):
    NOT_CONTACTED = "NOT_CONTACTED"
    REACHED_OUT = "REACHED_OUT"
    REPLIED = "REPLIED"
    WARM = "WARM"
    DECLINED = "DECLINED"
    REFERRAL_GIVEN = "REFERRAL_GIVEN"

class OutreachCampaignGoal(str, enum.Enum):
    JOB_SEARCH = "JOB_SEARCH"
    NETWORKING = "NETWORKING"
    MENTORSHIP = "MENTORSHIP"
    REFERRAL = "REFERRAL"
    RESEARCH = "RESEARCH"
    CONFERENCE = "CONFERENCE"

class OutreachCampaignStatus(str, enum.Enum):
    DRAFT = "DRAFT"
    ACTIVE = "ACTIVE"
    PAUSED = "PAUSED"
    COMPLETED = "COMPLETED"
    ARCHIVED = "ARCHIVED"

class OutreachEmailStatus(str, enum.Enum):
    DRAFT = "DRAFT"
    APPROVED = "APPROVED"
    SCHEDULED = "SCHEDULED"
    SENT = "SENT"
    DELIVERED = "DELIVERED"
    OPENED = "OPENED"
    REPLIED = "REPLIED"
    BOUNCED = "BOUNCED"
    FAILED = "FAILED"

class OutreachConversationStatus(str, enum.Enum):
    AWAITING_REPLY = "AWAITING_REPLY"
    REPLIED = "REPLIED"
    INTERVIEW_SCHEDULED = "INTERVIEW_SCHEDULED"
    OFFER_RECEIVED = "OFFER_RECEIVED"
    DECLINED = "DECLINED"
    ARCHIVED = "ARCHIVED"

class OutreachEmailProvider(str, enum.Enum):
    GMAIL = "GMAIL"
    OUTLOOK = "OUTLOOK"
    RELAY = "RELAY"


# ── Models ────────────────────────────────────────────────────────────────────

class OutreachCompany(Base, UUIDMixin, TimestampMixin):
    """Company workspace — the hub for all research and outreach to one company."""
    __tablename__ = "outreach_companies"

    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    domain: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, index=True)
    industry: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    stage: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    size: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    location: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    remote_policy: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    priority: Mapped[str] = mapped_column(
        Enum(OutreachCompanyPriority), default=OutreachCompanyPriority.WARM, nullable=False
    )
    status: Mapped[str] = mapped_column(
        Enum(OutreachCompanyStatus), default=OutreachCompanyStatus.WATCHING, nullable=False, index=True
    )
    research_status: Mapped[str] = mapped_column(
        Enum(OutreachResearchStatus), default=OutreachResearchStatus.PENDING, nullable=False
    )
    researched_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    match_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    tech_stack: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)
    open_roles_count: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationships
    intelligence: Mapped[Optional["OutreachIntelligence"]] = relationship(
        "OutreachIntelligence", back_populates="company", uselist=False, cascade="all, delete-orphan"
    )
    contacts: Mapped[List["OutreachContact"]] = relationship(
        "OutreachContact", back_populates="company", cascade="all, delete-orphan"
    )
    emails: Mapped[List["OutreachEmail"]] = relationship(
        "OutreachEmail", back_populates="company"
    )
    conversations: Mapped[List["OutreachConversation"]] = relationship(
        "OutreachConversation", back_populates="company"
    )


class OutreachIntelligence(Base, UUIDMixin, TimestampMixin):
    """Company intelligence report generated by AI research."""
    __tablename__ = "outreach_intelligence"

    company_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("outreach_companies.id", ondelete="CASCADE"),
        nullable=False, unique=True, index=True
    )
    report: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    executive_summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    personalization_hooks: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)
    tech_stack: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)
    culture_profile: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    recent_news: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)
    outreach_recommendation: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    sources: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)
    confidence: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    company: Mapped["OutreachCompany"] = relationship("OutreachCompany", back_populates="intelligence")


class OutreachContact(Base, UUIDMixin, TimestampMixin):
    """A person at a target company — recruiter, HM, or other."""
    __tablename__ = "outreach_contacts"

    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    company_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("outreach_companies.id", ondelete="CASCADE"), nullable=False, index=True
    )
    name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    title: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, index=True)
    email_confidence: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    email_validity: Mapped[str] = mapped_column(
        Enum(OutreachContactEmailValidity), default=OutreachContactEmailValidity.UNVERIFIED
    )
    linkedin_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    role_type: Mapped[str] = mapped_column(
        Enum(OutreachContactRoleType), default=OutreachContactRoleType.OTHER
    )
    relationship_strength: Mapped[float] = mapped_column(Float, default=0.0)
    relationship_status: Mapped[str] = mapped_column(
        Enum(OutreachContactRelationship), default=OutreachContactRelationship.NOT_CONTACTED, index=True
    )
    last_contacted: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    last_replied: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    do_not_contact: Mapped[bool] = mapped_column(Boolean, default=False)
    source: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    company: Mapped["OutreachCompany"] = relationship("OutreachCompany", back_populates="contacts")
    emails: Mapped[List["OutreachEmail"]] = relationship("OutreachEmail", back_populates="contact")
    conversations: Mapped[List["OutreachConversation"]] = relationship("OutreachConversation", back_populates="contact")


class OutreachCampaign(Base, UUIDMixin, TimestampMixin):
    """A structured outreach campaign targeting multiple companies."""
    __tablename__ = "outreach_campaigns"

    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    goal: Mapped[str] = mapped_column(
        Enum(OutreachCampaignGoal), default=OutreachCampaignGoal.JOB_SEARCH
    )
    status: Mapped[str] = mapped_column(
        Enum(OutreachCampaignStatus), default=OutreachCampaignStatus.DRAFT, nullable=False, index=True
    )
    sequence_config: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    send_window: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    daily_limit: Mapped[int] = mapped_column(Integer, default=5)
    resume_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    ab_config: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    stats: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True, default=dict)
    start_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    end_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    paused_reason: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    emails: Mapped[List["OutreachEmail"]] = relationship("OutreachEmail", back_populates="campaign")
    conversations: Mapped[List["OutreachConversation"]] = relationship("OutreachConversation", back_populates="campaign")


class OutreachEmail(Base, UUIDMixin, TimestampMixin):
    """A single outreach email — draft, approved, scheduled, or sent."""
    __tablename__ = "outreach_emails"

    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    campaign_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("outreach_campaigns.id", ondelete="SET NULL"), nullable=True, index=True
    )
    contact_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("outreach_contacts.id", ondelete="SET NULL"), nullable=True, index=True
    )
    company_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("outreach_companies.id", ondelete="SET NULL"), nullable=True, index=True
    )
    sequence_position: Mapped[int] = mapped_column(Integer, default=1)
    subject: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    body: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    subject_options: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)
    personalization_hooks: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)
    quality_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    quality_breakdown: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    reply_probability: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    from_address: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    to_address: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    resume_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    status: Mapped[str] = mapped_column(
        Enum(OutreachEmailStatus), default=OutreachEmailStatus.DRAFT, nullable=False, index=True
    )
    scheduled_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True, index=True)
    sent_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    opened_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    replied_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    provider_message_id: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    provider_thread_id: Mapped[Optional[str]] = mapped_column(String(500), nullable=True, index=True)
    ab_variant: Mapped[Optional[str]] = mapped_column(String(1), nullable=True)
    ai_model_used: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    campaign: Mapped[Optional["OutreachCampaign"]] = relationship("OutreachCampaign", back_populates="emails")
    contact: Mapped[Optional["OutreachContact"]] = relationship("OutreachContact", back_populates="emails")
    company: Mapped[Optional["OutreachCompany"]] = relationship("OutreachCompany", back_populates="emails")


class OutreachConversation(Base, UUIDMixin, TimestampMixin):
    """Thread-level conversation record after an email is sent."""
    __tablename__ = "outreach_conversations"

    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    contact_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("outreach_contacts.id", ondelete="SET NULL"), nullable=True, index=True
    )
    company_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("outreach_companies.id", ondelete="SET NULL"), nullable=True, index=True
    )
    campaign_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("outreach_campaigns.id", ondelete="SET NULL"), nullable=True, index=True
    )
    thread_id: Mapped[Optional[str]] = mapped_column(String(500), nullable=True, index=True)
    status: Mapped[str] = mapped_column(
        Enum(OutreachConversationStatus), default=OutreachConversationStatus.AWAITING_REPLY, nullable=False, index=True
    )
    sentiment: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    reply_classification: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    ai_summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    next_action: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    next_action_due: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    interview_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    offer_details: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    last_message_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    messages: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)

    contact: Mapped[Optional["OutreachContact"]] = relationship("OutreachContact", back_populates="conversations")
    company: Mapped[Optional["OutreachCompany"]] = relationship("OutreachCompany", back_populates="conversations")
    campaign: Mapped[Optional["OutreachCampaign"]] = relationship("OutreachCampaign", back_populates="conversations")


class OutreachEmailConnector(Base, UUIDMixin, TimestampMixin):
    """Encrypted OAuth connector for Gmail or Outlook."""
    __tablename__ = "outreach_email_connectors"
    __table_args__ = (UniqueConstraint("user_id", name="uq_outreach_connector_user"),)

    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True, index=True
    )
    provider: Mapped[str] = mapped_column(Enum(OutreachEmailProvider), nullable=False)
    email_address: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    access_token_enc: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    refresh_token_enc: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    token_expires: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    scopes: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    last_sync_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    last_history_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)


class OutreachGitHubConnector(Base, UUIDMixin, TimestampMixin):
    """Encrypted OAuth connector for GitHub."""
    __tablename__ = "outreach_github_connectors"
    __table_args__ = (UniqueConstraint("user_id", name="uq_outreach_github_connector_user"),)

    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True, index=True
    )
    github_username: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    access_token_enc: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    refresh_token_enc: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    token_expires: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    scopes: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    last_sync_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    repo_count: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    star_count: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    profile_json: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)


class OutreachFollowUp(Base, UUIDMixin, TimestampMixin):
    """Scheduled follow-up email in a campaign sequence."""
    __tablename__ = "outreach_followups"

    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    email_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("outreach_emails.id", ondelete="CASCADE"), nullable=True
    )
    campaign_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("outreach_campaigns.id", ondelete="CASCADE"), nullable=True
    )
    contact_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("outreach_contacts.id", ondelete="CASCADE"), nullable=True
    )
    company_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("outreach_companies.id", ondelete="CASCADE"), nullable=True
    )
    sequence_position: Mapped[int] = mapped_column(Integer, default=2)
    scheduled_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(20), default="pending", index=True)
    skip_reason: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
