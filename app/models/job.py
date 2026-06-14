"""
app/models/job.py
─────────────────
Job discovery and AI analysis models.
Jobs are scraped, stored raw, then enriched by the AI pipeline.
"""

from __future__ import annotations

import enum
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
from app.models.base import TimestampMixin, UUIDMixin
from app.models.enums import ExperienceLevel


# ── Enums ────────────────────────────────────────────────────────────────────

class JobSource(str, enum.Enum):
    LINKEDIN = "linkedin"
    INDEED = "indeed"
    INTERNSHALA = "internshala"
    REMOTEOK = "remoteok"
    WELLFOUND = "wellfound"
    GLASSDOOR = "glassdoor"
    COMPANY_SITE = "company_site"
    MANUAL = "manual"


class JobType(str, enum.Enum):
    FULL_TIME = "FULL_TIME"
    PART_TIME = "PART_TIME"
    INTERNSHIP = "INTERNSHIP"
    CONTRACT = "CONTRACT"
    FREELANCE = "FREELANCE"


class WorkMode(str, enum.Enum):
    REMOTE = "REMOTE"
    ONSITE = "ONSITE"
    HYBRID = "HYBRID"
    UNKNOWN = "UNKNOWN"


class JobStatus(str, enum.Enum):
    NEW = "NEW"               # Just scraped, not processed
    ANALYZED = "ANALYZED"     # AI pipeline ran
    QUEUED = "QUEUED"         # Queued for application
    APPLIED = "APPLIED"       # Application submitted
    SKIPPED = "SKIPPED"       # User/agent skipped
    EXPIRED = "EXPIRED"       # Job no longer active


# ── Models ───────────────────────────────────────────────────────────────────

class Job(Base, UUIDMixin, TimestampMixin):
    """
    Raw job listing as scraped from source platforms.
    The source of truth — never modified after creation.
    All AI enrichment goes into JobAnalysis.
    Jobs are user-scoped: each user has their own independent job list.
    """
    __tablename__ = "jobs"
    __table_args__ = (
        # Prevent duplicate jobs from same source
        UniqueConstraint("source", "source_job_id", name="uq_job_source"),
    )

    # ── Owner ─────────────────────────────────────────────────
    # Nullable for backward-compat with legacy rows that pre-date multi-tenancy
    user_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"),
        nullable=True, index=True
    )

    # ── Source Info ───────────────────────────────────────────
    source: Mapped[JobSource] = mapped_column(Enum(JobSource, name="jobsource"), nullable=False, index=True)
    source_job_id: Mapped[str] = mapped_column(String(255), nullable=False)
    source_url: Mapped[str] = mapped_column(String(2000), nullable=False)
    raw_html: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    # Store raw HTML for reprocessing without re-scraping

    # ── Basic Info ────────────────────────────────────────────
    title: Mapped[str] = mapped_column(String(500), nullable=False, index=True)
    company_name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    company_logo_url: Mapped[Optional[str]] = mapped_column(String(2000), nullable=True)
    company_website: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    # ── Description ───────────────────────────────────────────
    description_raw: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    description_clean: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # ── Location / Mode ───────────────────────────────────────
    location: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    country: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    city: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    work_mode: Mapped[WorkMode] = mapped_column(
        Enum(WorkMode, name="workmode"), default=WorkMode.UNKNOWN, nullable=False, index=True
    )

    # ── Classification ────────────────────────────────────────
    job_type: Mapped[JobType] = mapped_column(
        Enum(JobType, name="jobtype"), default=JobType.FULL_TIME, nullable=False, index=True
    )
    experience_level: Mapped[ExperienceLevel] = mapped_column(
        Enum(ExperienceLevel, name="experiencelevel", values_callable=lambda obj: [e.value for e in obj]), 
        default=ExperienceLevel.UNKNOWN, 
        nullable=False
    )

    # ── Compensation ──────────────────────────────────────────
    salary_min: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    salary_max: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    salary_currency: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)
    salary_period: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    # "annual" | "monthly" | "hourly"

    # ── Dates ─────────────────────────────────────────────────
    posted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    scraped_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    # ── Pipeline Status ───────────────────────────────────────
    status: Mapped[JobStatus] = mapped_column(
        Enum(JobStatus, name="jobstatus", values_callable=lambda obj: [e.value for e in obj]),
        default=JobStatus.NEW,
        nullable=False,
        index=True,
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, index=True)

    # ── Applicant Count (if available) ───────────────────────
    applicant_count: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    easy_apply: Mapped[bool] = mapped_column(Boolean, default=False)

    # Relationships
    analysis: Mapped[Optional["JobAnalysis"]] = relationship(
        "JobAnalysis", back_populates="job", uselist=False, cascade="all, delete-orphan"
    )
    applications: Mapped[List["Application"]] = relationship(
        "Application", back_populates="job"
    )

    def __repr__(self) -> str:
        return f"<Job {self.title} @ {self.company_name} ({self.source})>"


class JobAnalysis(Base, UUIDMixin, TimestampMixin):
    """
    AI-generated analysis of a job description.
    Produced by the Job Description Analyzer (Module 2).
    Also stores the match score against the current user profile.
    """
    __tablename__ = "job_analyses"

    job_id: Mapped[str] = mapped_column(ForeignKey("jobs.id"), nullable=False, unique=True, index=True)

    # ── Extracted Skills ──────────────────────────────────────
    required_skills: Mapped[List[str]] = mapped_column(JSON, default=list)
    preferred_skills: Mapped[List[str]] = mapped_column(JSON, default=list)
    tech_stack: Mapped[List[str]] = mapped_column(JSON, default=list)
    # e.g. ["Python", "PyTorch", "AWS", "Docker"]

    # ── ATS Keywords ──────────────────────────────────────────
    ats_keywords: Mapped[List[str]] = mapped_column(JSON, default=list)
    # Keywords that ATS filters look for

    # ── Requirements ─────────────────────────────────────────
    min_years_experience: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    max_years_experience: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    education_requirement: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    # "bachelor" | "master" | "phd" | "none"

    # ── Responsibilities ──────────────────────────────────────
    key_responsibilities: Mapped[List[str]] = mapped_column(JSON, default=list)

    # ── Classification ────────────────────────────────────────
    role_category: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    # e.g. "computer_vision", "nlp", "mlops", "data_science", "software_engineering"
    seniority_detected: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    is_internship: Mapped[bool] = mapped_column(Boolean, default=False)

    # ── Match Scoring ─────────────────────────────────────────
    match_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True, index=True)
    # 0.0 – 100.0 — overall match against user profile
    skill_match_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    experience_match_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    semantic_similarity_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    # Embedding cosine similarity

    matching_skills: Mapped[List[str]] = mapped_column(JSON, default=list)
    missing_skills: Mapped[List[str]] = mapped_column(JSON, default=list)
    skill_gap_count: Mapped[int] = mapped_column(Integer, default=0)

    # ── Competition Estimate ──────────────────────────────────
    estimated_applicants: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    competition_level: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    # "low" | "medium" | "high" | "very_high"
    interview_probability: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    # Predicted probability of getting an interview (0.0 – 1.0)

    # ── Difficulty & Priority ─────────────────────────────────
    job_difficulty: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    # "easy" | "medium" | "hard"
    priority_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    # Combined score: match_score * interview_probability / competition

    # ── Salary Estimate (if not in listing) ──────────────────
    estimated_salary_min: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    estimated_salary_max: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    # ── AI Summary ────────────────────────────────────────────
    ai_summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    ai_recommendation: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    # "Strongly recommend applying — your PyTorch and OpenCV experience directly match..."

    # ── Processing Metadata ───────────────────────────────────
    model_used: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    ai_provider: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    tokens_used: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    processing_time_ms: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    # Relationship
    job: Mapped["Job"] = relationship("Job", back_populates="analysis")

    def __repr__(self) -> str:
        return f"<JobAnalysis job_id={self.job_id} match={self.match_score}>"
