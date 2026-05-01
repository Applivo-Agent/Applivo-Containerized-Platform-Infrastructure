"""
app/models/ai_usage.py
──────────────────────
Centralized logging for LLM/AI model calls.
Tracks granularity for cost, performance, and reliability monitoring.
"""

from __future__ import annotations
from datetime import datetime
from typing import Optional

from sqlalchemy import (
    Boolean,
    DateTime,
    Index,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.base import UUIDMixin


class AIUsageLog(Base, UUIDMixin):
    """
    Detailed log of every AI model call made by the system.
    Used for the Admin Analytics dashboard to track usage, errors, and costs.
    """
    __tablename__ = "ai_usage_logs"

    # ── Actor ─────────────────────────────────────────────────
    user_id: Mapped[Optional[str]] = mapped_column(
        String(36), index=True, nullable=True
    )
    # The user who triggered the AI call

    # ── Provider & Model ──────────────────────────────────────
    provider: Mapped[str] = mapped_column(String(50), index=True)
    # "groq" | "gemini" | "openai"
    
    model: Mapped[str] = mapped_column(String(100), index=True)
    # e.g., "llama-3.1-8b-instant", "gemini-1.5-flash"

    # ── Usage Metrics ─────────────────────────────────────────
    prompt_tokens: Mapped[int] = mapped_column(Integer, default=0)
    completion_tokens: Mapped[int] = mapped_column(Integer, default=0)
    total_tokens: Mapped[int] = mapped_column(Integer, default=0)
    cached_tokens: Mapped[int] = mapped_column(Integer, default=0)

    # ── Performance & Result ──────────────────────────────────
    latency_ms: Mapped[int] = mapped_column(Integer, default=0)
    status_code: Mapped[int] = mapped_column(Integer, index=True)
    # 200, 429, 500, etc.
    
    success: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
    
    endpoint_path: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    # The API route that triggered this call (e.g., "/analyze")

    # ── Content Metadata (Optional, for debugging) ───────────
    # We don't store full prompts for privacy, but we might store IDs
    resource_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    resource_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)

    # ── Timestamp ───────────────────────────────────────────
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        index=True
    )

    # ── Indexes ─────────────────────────────────────────────
    __table_args__ = (
        Index("ix_ai_usage_provider_model", "provider", "model"),
        Index("ix_ai_usage_created_at_status", "created_at", "status_code"),
    )

    def __repr__(self) -> str:
        return f"<AIUsageLog {self.model} ({self.status_code}) at {self.created_at}>"
