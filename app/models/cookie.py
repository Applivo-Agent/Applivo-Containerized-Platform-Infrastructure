"""
app/models/cookie.py
────────────────────
Encrypted platform cookie storage for multi-user automation.
Cookies are stored server-side, encrypted at rest.
"""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import TimestampMixin, UUIDMixin


class PlatformCookie(Base, UUIDMixin, TimestampMixin):
    """
    Stores encrypted session cookies for each user's platform connections.
    Supports Internshala (current) with future support for LinkedIn, Indeed, Naukri.
    """
    __tablename__ = "platform_cookies"

    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id"),
        nullable=False, index=True,
    )

    platform: Mapped[str] = mapped_column(
        String(50), nullable=False, index=True,
    )  # "internshala", "linkedin", "indeed", "naukri"

    # AES-256-GCM encrypted cookie JSON
    encrypted_cookies: Mapped[str] = mapped_column(
        Text, nullable=False,
    )

    is_valid: Mapped[bool] = mapped_column(
        Boolean, default=True, nullable=False,
    )
    expires_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True,
    )
    last_validated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True,
    )
    last_used_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True,
    )

    # Relationship
    user: Mapped["User"] = relationship("User", back_populates="platform_cookies")

    def __repr__(self) -> str:
        status = "valid" if self.is_valid else "expired"
        return f"<PlatformCookie {self.platform} [{status}] user={self.user_id}>"
