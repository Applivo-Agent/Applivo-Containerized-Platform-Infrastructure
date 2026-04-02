"""
app/models/resume.py
"""
from __future__ import annotations
import enum
from typing import List, Optional
from sqlalchemy import JSON, Boolean, Enum, Float, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base
from app.models.base import TimestampMixin, UUIDMixin


class ResumeType(str, enum.Enum):
    BASE = "base"
    TAILORED = "tailored"
    ROLE_VARIANT = "role_variant"


class Resume(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "resumes"

    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    resume_type: Mapped[str] = mapped_column(
        Enum(ResumeType), default=ResumeType.BASE, nullable=False, index=True
    )
    role_category: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    content_json: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    content_markdown: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    file_path: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)
    file_size_bytes: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    ats_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    keyword_coverage: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    times_used: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    response_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    response_rate: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    target_job_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True, index=True)
    keywords_injected: Mapped[List[str]] = mapped_column(JSON, default=list)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
    is_default: Mapped[bool] = mapped_column(Boolean, default=False)

    user: Mapped["User"] = relationship("User", back_populates="resumes")
    applications: Mapped[List["Application"]] = relationship("Application", back_populates="resume")


class CoverLetter(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "cover_letters"

    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    job_id: Mapped[Optional[str]] = mapped_column(ForeignKey("jobs.id"), nullable=True, index=True)
    application_id: Mapped[Optional[str]] = mapped_column(ForeignKey("applications.id"), nullable=True, index=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    tone: Mapped[str] = mapped_column(String(50), default="professional", nullable=False)
    target_company: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    target_role: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    highlighted_skills: Mapped[List[str]] = mapped_column(JSON, default=list)
    file_path: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)
    model_used: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    tokens_used: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    word_count: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)