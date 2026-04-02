"""
app/models/interview.py
────────────────────────
Interview preparation, simulation, recruiter tracking,
notifications, agent task queue, skill gaps, and market intelligence.
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


# ═══════════════════════════════════════════════════════════════════════════
#  INTERVIEW MODELS  (Modules 18, 19, 20, 21)
# ═══════════════════════════════════════════════════════════════════════════

class InterviewType(str, enum.Enum):
    PHONE_SCREEN = "phone_screen"
    TECHNICAL = "technical"
    BEHAVIORAL = "behavioral"
    SYSTEM_DESIGN = "system_design"
    HR = "hr"
    FINAL = "final"
    TAKE_HOME = "take_home"


class Interview(Base, UUIDMixin, TimestampMixin):
    """Scheduled interview with auto-generated prep material."""
    __tablename__ = "interviews"

    application_id: Mapped[str] = mapped_column(String(36), ForeignKey("applications.id"), nullable=False, index=True)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=False, index=True)

    interview_type: Mapped[str] = mapped_column(Enum(InterviewType), nullable=False)
    scheduled_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    duration_minutes: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    platform: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    # "zoom" | "google_meet" | "teams" | "phone" | "onsite"
    meeting_link: Mapped[Optional[str]] = mapped_column(String(2000), nullable=True)

    # ── Prep Material (auto-generated) ────────────────────────
    company_report: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    # {products, news, tech_stack, culture, salary_data, glassdoor_rating}
    technical_questions: Mapped[List[dict]] = mapped_column(JSON, default=list)
    # [{"question": "...", "expected_answer": "...", "difficulty": "medium", "topic": "CNN"}]
    behavioral_questions: Mapped[List[dict]] = mapped_column(JSON, default=list)
    study_topics: Mapped[List[str]] = mapped_column(JSON, default=list)

    # ── Post-interview ────────────────────────────────────────
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    outcome: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    # "passed" | "failed" | "pending" | "cancelled"
    user_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    ai_feedback: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationships
    application: Mapped["Application"] = relationship("Application", back_populates="interviews")
    mock_sessions: Mapped[List["MockInterviewSession"]] = relationship(
        "MockInterviewSession", back_populates="interview", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Interview {self.interview_type} scheduled={self.scheduled_at}>"


class MockInterviewSession(Base, UUIDMixin, TimestampMixin):
    """AI mock interview session (Module 19)."""
    __tablename__ = "mock_interview_sessions"

    interview_id: Mapped[str] = mapped_column(ForeignKey("interviews.id"), nullable=False, index=True)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=False, index=True)

    transcript: Mapped[List[dict]] = mapped_column(JSON, default=list)
    # [{"role": "interviewer"|"user", "content": "...", "timestamp": "..."}]
    duration_seconds: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    # ── Scoring ───────────────────────────────────────────────
    overall_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    technical_depth_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    communication_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    confidence_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    improvement_suggestions: Mapped[List[str]] = mapped_column(JSON, default=list)

    # ── Recording Analysis (Module 20) ───────────────────────
    recording_path: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)
    transcription: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    filler_word_count: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    filler_words_detected: Mapped[List[str]] = mapped_column(JSON, default=list)
    speech_pace_wpm: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    interview: Mapped["Interview"] = relationship("Interview", back_populates="mock_sessions")


# ═══════════════════════════════════════════════════════════════════════════
#  RECRUITER TRACKING  (Module 17)
# ═══════════════════════════════════════════════════════════════════════════

class Recruiter(Base, UUIDMixin, TimestampMixin):
    """Recruiter / hiring manager contact."""
    __tablename__ = "recruiters"

    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    linkedin_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    company: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, index=True)
    title: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    interest_level: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    # "cold" | "warm" | "hot" | "responded"
    last_contact_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    next_follow_up_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    messages: Mapped[List["RecruiterMessage"]] = relationship(
        "RecruiterMessage", back_populates="recruiter", cascade="all, delete-orphan"
    )


class RecruiterMessage(Base, UUIDMixin, TimestampMixin):
    """Individual message in a recruiter conversation thread."""
    __tablename__ = "recruiter_messages"

    recruiter_id: Mapped[str] = mapped_column(ForeignKey("recruiters.id"), nullable=False, index=True)
    direction: Mapped[str] = mapped_column(String(10), nullable=False)
    # "sent" | "received"
    channel: Mapped[str] = mapped_column(String(20), nullable=False)
    # "email" | "linkedin" | "phone"
    subject: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    sent_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    recruiter: Mapped["Recruiter"] = relationship("Recruiter", back_populates="messages")


# ═══════════════════════════════════════════════════════════════════════════
#  NOTIFICATIONS  (Module 8)
# ═══════════════════════════════════════════════════════════════════════════

class NotificationChannel(str, enum.Enum):
    TELEGRAM = "telegram"
    EMAIL = "email"


class NotificationStatus(str, enum.Enum):
    PENDING = "pending"
    SENT = "sent"
    FAILED = "failed"
    READ = "read"


class Notification(Base, UUIDMixin, TimestampMixin):
    """Log of every notification sent to the user."""
    __tablename__ = "notifications"

    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    channel: Mapped[str] = mapped_column(Enum(NotificationChannel), nullable=False)
    status: Mapped[str] = mapped_column(
        Enum(NotificationStatus), default=NotificationStatus.PENDING, nullable=False, index=True
    )

    title: Mapped[str] = mapped_column(String(500), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    data: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    # Extra structured data attached to notification

    event_type: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    # "new_jobs_found" | "application_submitted" | "interview_scheduled" | "status_changed"

    # Telegram-specific
    telegram_message_id: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    telegram_reply_markup: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    # Inline keyboard buttons for interactive notifications

    sent_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    read_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    def __repr__(self) -> str:
        return f"<Notification {self.event_type} via {self.channel} [{self.status}]>"


# ═══════════════════════════════════════════════════════════════════════════
#  AGENT TASK QUEUE  (Background Automation)
# ═══════════════════════════════════════════════════════════════════════════

class AgentTaskType(str, enum.Enum):
    SCRAPE_JOBS = "scrape_jobs"
    ANALYZE_JOB = "analyze_job"
    GENERATE_RESUME = "generate_resume"
    GENERATE_COVER_LETTER = "generate_cover_letter"
    AUTO_APPLY = "auto_apply"
    SEND_FOLLOW_UP = "send_follow_up"
    PREP_INTERVIEW = "prep_interview"
    ANALYZE_MARKET = "analyze_market"
    UPDATE_LINKEDIN = "update_linkedin"
    UPDATE_GITHUB = "update_github"
    SEND_NOTIFICATION = "send_notification"


class AgentTaskStatus(str, enum.Enum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    RETRYING = "retrying"
    CANCELLED = "cancelled"


class AgentTask(Base, UUIDMixin, TimestampMixin):
    """
    Every automated action the system takes is recorded here.
    Provides full visibility into what the agent is doing.
    Doubles as a retry queue for failed tasks.
    """
    __tablename__ = "agent_tasks"

    task_type: Mapped[str] = mapped_column(Enum(AgentTaskType), nullable=False, index=True)
    status: Mapped[str] = mapped_column(
        Enum(AgentTaskStatus), default=AgentTaskStatus.PENDING, nullable=False, index=True
    )
    celery_task_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, unique=True)

    # ── Task Input/Output ─────────────────────────────────────
    payload: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    result: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    error: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # ── Timing ────────────────────────────────────────────────
    scheduled_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    duration_ms: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    # ── Retry ─────────────────────────────────────────────────
    retry_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    max_retries: Mapped[int] = mapped_column(Integer, default=3, nullable=False)

    # ── Context ───────────────────────────────────────────────
    related_job_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True, index=True)
    related_application_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    triggered_by: Mapped[str] = mapped_column(String(50), default="scheduler", nullable=False)
    # "scheduler" | "user" | "agent" | "webhook"

    def __repr__(self) -> str:
        return f"<AgentTask {self.task_type} [{self.status}]>"


# ═══════════════════════════════════════════════════════════════════════════
#  SKILL GAP & MARKET INTELLIGENCE  (Modules 10, 22)
# ═══════════════════════════════════════════════════════════════════════════

class SkillGap(Base, UUIDMixin, TimestampMixin):
    """
    Detected skill gap from market analysis.
    Linked to learning recommendations.
    """
    __tablename__ = "skill_gaps"

    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    skill_name: Mapped[str] = mapped_column(String(100), nullable=False)
    category: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    demand_count: Mapped[int] = mapped_column(Integer, default=0)
    # How many job descriptions in our DB require this skill
    demand_percentage: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    # % of relevant job postings that require this skill
    priority: Mapped[str] = mapped_column(String(20), default="medium")
    # "critical" | "high" | "medium" | "low"

    user_has_skill: Mapped[bool] = mapped_column(Boolean, default=False)
    user_proficiency: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)

    learning_plan_generated: Mapped[bool] = mapped_column(Boolean, default=False)
    resolved: Mapped[bool] = mapped_column(Boolean, default=False)
    # Marked resolved when user adds this skill


class MarketSnapshot(Base, UUIDMixin, TimestampMixin):
    """
    Periodic snapshot of job market intelligence.
    Taken after each scrape cycle for trend analysis.
    """
    __tablename__ = "market_snapshots"

    snapshot_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    total_jobs_scraped: Mapped[int] = mapped_column(Integer, default=0)
    total_jobs_analyzed: Mapped[int] = mapped_column(Integer, default=0)

    # Top demanded skills from this batch
    top_skills: Mapped[List[dict]] = mapped_column(JSON, default=list)
    # [{"skill": "Python", "count": 450, "percentage": 78.2}]

    top_companies_hiring: Mapped[List[dict]] = mapped_column(JSON, default=list)
    emerging_roles: Mapped[List[str]] = mapped_column(JSON, default=list)

    salary_data: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    # {"avg_min": 80000, "avg_max": 120000, "by_role": {...}}

    by_source: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    # {"linkedin": 120, "indeed": 80, ...}
    by_location: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    by_work_mode: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)


# ═══════════════════════════════════════════════════════════════════════════
#  LEARNING & PROJECTS  (Modules 11, 12)
# ═══════════════════════════════════════════════════════════════════════════

class LearningPlan(Base, UUIDMixin, TimestampMixin):
    """AI-generated learning roadmap to address skill gaps."""
    __tablename__ = "learning_plans"

    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    target_role: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    total_weeks: Mapped[int] = mapped_column(Integer, default=4)

    weekly_plans: Mapped[List[dict]] = mapped_column(JSON, default=list)
    # [{"week": 1, "focus": "Docker", "topics": [...], "resources": [...], "project": "..."}]

    skills_addressed: Mapped[List[str]] = mapped_column(JSON, default=list)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    progress_percentage: Mapped[float] = mapped_column(Float, default=0.0)


class GeneratedProject(Base, UUIDMixin, TimestampMixin):
    """AI-generated project idea to address a skill gap (Module 12)."""
    __tablename__ = "generated_projects"

    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    skill_gap_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)

    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    tech_stack: Mapped[List[str]] = mapped_column(JSON, default=list)
    difficulty: Mapped[str] = mapped_column(String(20), default="intermediate")

    # Generated artifacts
    github_structure: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    readme_content: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    starter_code: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    github_repo_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    status: Mapped[str] = mapped_column(String(30), default="suggested")
    # "suggested" | "started" | "completed"
