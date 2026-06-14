"""
app/models/workflow.py
──────────────────────
Workflow execution model for the Scrape → Analyze → Queue → Deploy pipeline.
Provides persistent, step-level state that survives refresh and navigation.
"""

from __future__ import annotations

import enum
import uuid
from datetime import datetime
from typing import List, Optional

from sqlalchemy import (
    JSON,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import TimestampMixin, UUIDMixin


class WorkflowStatus(str, enum.Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


class WorkflowStepType(str, enum.Enum):
    SCRAPE = "SCRAPE"
    ANALYZE = "ANALYZE"
    QUEUE = "QUEUE"
    DEPLOY = "DEPLOY"


class WorkflowStepStatus(str, enum.Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    SKIPPED = "SKIPPED"


def _uuid_str() -> str:
    return str(uuid.uuid4())


class WorkflowExecution(Base, UUIDMixin, TimestampMixin):
    """
    A single run of the Scrape → Analyze → Queue → Deploy pipeline.
    Tracks overall progress and per-step results.
    """
    __tablename__ = "workflow_executions"

    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    status: Mapped[WorkflowStatus] = mapped_column(
        Enum(WorkflowStatus, name="workflowstatus", values_callable=lambda obj: [e.value for e in obj]),
        default=WorkflowStatus.PENDING,
        nullable=False,
        index=True,
    )

    current_step_index: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    failed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    result_summary: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    steps: Mapped[List["WorkflowStep"]] = relationship(
        "WorkflowStep",
        back_populates="workflow",
        cascade="all, delete-orphan",
        order_by="WorkflowStep.step_index",
        lazy="selectin",
    )


class WorkflowStep(Base, TimestampMixin):
    """
    Individual step within a workflow execution.
    """
    __tablename__ = "workflow_steps"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid_str)

    workflow_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("workflow_executions.id", ondelete="CASCADE"), nullable=False, index=True
    )
    step_index: Mapped[int] = mapped_column(Integer, nullable=False)
    step_type: Mapped[WorkflowStepType] = mapped_column(
        Enum(WorkflowStepType, name="workflowsteptype", values_callable=lambda obj: [e.value for e in obj]),
        nullable=False,
    )

    status: Mapped[WorkflowStepStatus] = mapped_column(
        Enum(WorkflowStepStatus, name="workflowstepstatus", values_callable=lambda obj: [e.value for e in obj]),
        default=WorkflowStepStatus.PENDING,
        nullable=False,
        index=True,
    )

    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    result_summary: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    tokens_used: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    workflow: Mapped["WorkflowExecution"] = relationship("WorkflowExecution", back_populates="steps")
