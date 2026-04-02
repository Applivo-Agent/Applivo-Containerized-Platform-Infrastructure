"""
app/models/consent.py
────────────────────
GDPR-compliant consent management.
Tracks user consent for data collection, processing, and sharing.
"""

from __future__ import annotations

import enum
from datetime import datetime
from typing import List, Optional, List

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    JSON,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import TimestampMixin, UUIDMixin


class ConsentType(str, enum.Enum):
    """Categories of consent."""
    DATA_COLLECTION = "data_collection"
    DATA_PROCESSING = "data_processing"
    DATA_SHARING = "data_sharing"
    MARKETING = "marketing"
    ANALYTICS = "analytics"
    AI_PROCESSING = "ai_processing"
    THIRD_PARTY_INTEGRATION = "third_party_integration"
    AUTOMATION = "automation"


class ConsentScope(str, enum.Enum):
    """
    Granular scope for each consent type.
    Maps to specific features/functionality.
    """
    ESSENTIAL = "essential"           # Required for service (no opt-out)
    ACCOUNT = "account"               # Account management
    JOB_SEARCH = "job_search"         # Job matching and search
    AUTOMATION = "automation"          # Auto-apply features
    IMPROVEMENT = "improvement"        # Platform improvement
    MARKETING = "marketing"            # Marketing communications
    THIRD_PARTY = "third_party"        # Third-party integrations


class UserConsent(Base, UUIDMixin, TimestampMixin):
    """
    Granular consent tracking per user per purpose.
    Supports GDPR Article 7 requirements:
    - Consent must be freely given
    - Must be specific and informed
    - Must be unambiguous
    - Must be as easy to withdraw as to give
    """
    __tablename__ = "user_consents"
    __table_args__ = (
        # Unique constraint: one consent per user per type
        # "uq_user_consent_user_type",  # Defined below
    )

    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id"),
        nullable=False, index=True
    )

    # Consent type (what they're consenting to)
    consent_type: Mapped[str] = mapped_column(
        String(50), nullable=False, index=True
    )

    # Granular scope within the type
    scope: Mapped[str] = mapped_column(
        String(50), nullable=False
    )

    # Consent status
    granted: Mapped[bool] = mapped_column(Boolean, default=False)
    revoked: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Consent proof (when, where, how)
    granted_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    ip_address: Mapped[Optional[str]] = mapped_column(String(45), nullable=True)
    user_agent: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Version of privacy policy at time of consent
    policy_version: Mapped[str] = mapped_column(String(20), nullable=False)

    # Purpose description (what data, why, how long)
    purpose: Mapped[str] = mapped_column(String(500), nullable=False)
    
    # Categories of data covered by this consent
    # e.g. ["email", "phone", "resume", "skills", "employment_history"]
    data_categories: Mapped[Optional[List[str]]] = mapped_column(
        JSON, default=list
    )

    # Additional metadata
    # e.g. {"method": "checkbox", "language": "en", "context": "onboarding"}
    extra_data: Mapped[Optional[dict]] = mapped_column(JSON, default=dict)

    # Relationship
    user: Mapped["User"] = relationship("User", back_populates="consents")

    def __repr__(self) -> str:
        return f"<UserConsent {self.consent_type}={self.granted} for user {self.user_id}>"


class ConsentVersion(Base, UUIDMixin, TimestampMixin):
    """
    Tracks privacy policy versions and default consent requirements.
    Allows tracking what consent was valid at any point in time.
    """
    __tablename__ = "consent_versions"

    version: Mapped[str] = mapped_column(String(20), nullable=False, unique=True)
    effective_from: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    
    # JSON: Consent requirements for this version
    # {
    #   "essentials": [{"type": "data_collection", "scope": "essential", "purpose": "..."}],
    #   "optionals": [{"type": "ai_processing", "scope": "automation", "purpose": "..."}]
    # }
    consent_requirements: Mapped[dict] = mapped_column(JSON, nullable=False)
    
    # Changelog for this version
    changes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    def __repr__(self) -> str:
        return f"<ConsentVersion {self.version} effective {self.effective_from}>"


# Default consent configurations
DEFAULT_CONSENTS = {
    "essentials": [
        {
            "type": ConsentType.DATA_COLLECTION,
            "scope": ConsentScope.ESSENTIAL,
            "purpose": "We collect your email to create and manage your account. This is required for the service to function.",
            "data_categories": ["email", "password_hash"],
            "required": True
        }
    ],
    "optional": [
        {
            "type": ConsentType.AI_PROCESSING,
            "scope": ConsentScope.AUTOMATION,
            "purpose": "Your resume and skills are processed by AI to match you with relevant jobs and generate application materials.",
            "data_categories": ["resume", "skills", "employment_history", "education"],
            "required": False
        },
        {
            "type": ConsentType.AUTOMATION,
            "scope": ConsentScope.AUTOMATION,
            "purpose": "Enable auto-apply features to automatically apply to jobs on your behalf using your stored profile and credentials.",
            "data_categories": ["profile", "credentials", "resume", "preferences"],
            "required": False
        },
        {
            "type": ConsentType.DATA_SHARING,
            "scope": ConsentScope.THIRD_PARTY,
            "purpose": "Share necessary data with job platforms (LinkedIn, Indeed, etc.) to submit applications on your behalf.",
            "data_categories": ["resume", "profile", "contact_info"],
            "required": False
        },
        {
            "type": ConsentType.MARKETING,
            "scope": ConsentScope.MARKETING,
            "purpose": "Receive emails about new features, job opportunities, and platform improvements.",
            "data_categories": ["email"],
            "required": False
        }
    ]
}
