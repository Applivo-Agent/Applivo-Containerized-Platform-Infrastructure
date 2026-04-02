"""
app/models/credential.py
─────────────────────────
Secure vault for user-provided platform credentials.
Credentials are encrypted at rest using AES-256-GCM.
"""

from __future__ import annotations

import enum
from datetime import datetime
from typing import List, Optional

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


class CredentialType(str, enum.Enum):
    LINKEDIN = "linkedin"
    INDEED = "indeed"
    INTERNShALA = "internshala"
    WELLFOUND = "wellfound"
    CUSTOM_API = "custom_api"


class CredentialVault(Base, UUIDMixin, TimestampMixin):
    """
    Encrypted storage for user platform credentials.
    Each user can have multiple credential sets.
    
    Data is encrypted using AES-256-GCM before storage.
    Only the encrypted blob is stored, never plaintext.
    """
    __tablename__ = "credential_vaults"

    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id"),
        nullable=False, index=True
    )

    # Credential metadata (stored as plaintext)
    credential_type: Mapped[str] = mapped_column(
        String(50), nullable=False, index=True
    )
    display_name: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    # Encrypted credential data
    # Structure: {"email": "...", "password": "...", "cookies": {...}, "api_key": "..."}
    # Entire JSON encrypted as single blob using AES-256-GCM
    encrypted_data: Mapped[str] = mapped_column(Text, nullable=False)

    # Consent tracking - required before storing/using credentials
    consent_given: Mapped[bool] = mapped_column(Boolean, default=False)
    consent_timestamp: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    consent_purpose: Mapped[str] = mapped_column(
        String(500), nullable=False
    )

    # Usage tracking
    last_used_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    use_count: Mapped[int] = mapped_column(default=0, nullable=False)

    # Expiration (optional - for API keys that expire)
    expires_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Scope limitations - restricts what actions can be performed
    # JSON: {"allowed_actions": ["apply", "scrape"], "rate_limit": 10}
    scope: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)

    # Relationship
    user: Mapped["User"] = relationship("User", back_populates="credentials")
    use_logs: Mapped[List["CredentialUseLog"]] = relationship(
        "CredentialUseLog", back_populates="credential", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<CredentialVault {self.credential_type} for user {self.user_id}>"


class CredentialUseLog(Base, UUIDMixin, TimestampMixin):
    """
    Log of each time a credential is used.
    For security audit and rate limiting.
    """
    __tablename__ = "credential_use_logs"

    credential_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("credential_vaults.id"),
        nullable=False, index=True
    )
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id"),
        nullable=False, index=True
    )

    # Usage details
    action: Mapped[str] = mapped_column(String(100), nullable=False)
    # e.g., "linkedin.apply", "indeed.scrape"

    # Request context
    ip_address: Mapped[Optional[str]] = mapped_column(String(45), nullable=True)
    user_agent: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Outcome
    success: Mapped[bool] = mapped_column(default=True)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationship
    credential: Mapped["CredentialVault"] = relationship(
        "CredentialVault", back_populates="use_logs"
    )

    def __repr__(self) -> str:
        return f"<CredentialUseLog {self.action} for credential {self.credential_id}>"


# Add relationship to User model
# This will be added via model imports in __init__.py
