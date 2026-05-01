"""
app/models/platform_message.py
──────────────────────────────
Stores messages from platform inboxes (Internshala, LinkedIn, etc.)
"""

from __future__ import annotations
import enum
from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.base import TimestampMixin, UUIDMixin


class PlatformMessageStatus(str, enum.Enum):
    UNREAD = "unread"
    READ = "read"
    PROCESSED = "processed"


class PlatformMessage(Base, UUIDMixin, TimestampMixin):
    """
    Stores messages from platform inboxes.
    Currently supports Internshala, with future support for LinkedIn, Indeed.
    """
    __tablename__ = "platform_messages"

    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id"),
        nullable=False, index=True,
    )

    platform: Mapped[str] = mapped_column(
        String(50), nullable=False, index=True,
    )  # "internshala", "linkedin", "indeed"

    external_id: Mapped[Optional[str]] = mapped_column(
        String(100), nullable=True, index=True,
    )

    sender_name: Mapped[Optional[str]] = mapped_column(
        String(255), nullable=True,
    )

    sender_email: Mapped[Optional[str]] = mapped_column(
        String(255), nullable=True,
    )

    subject: Mapped[Optional[str]] = mapped_column(
        String(500), nullable=True,
    )

    content: Mapped[str] = mapped_column(Text, nullable=False)

    is_important: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False, index=True,
    )

    importance_keywords: Mapped[Optional[str]] = mapped_column(
        String(255), nullable=True,
    )

    status: Mapped[str] = mapped_column(
        String(20), default="unread", nullable=False, index=True,
    )

    received_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True, index=True,
    )

    def __repr__(self) -> str:
        return f"<PlatformMessage {self.platform} from={self.sender_name} status={self.status}>"