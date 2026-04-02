"""
app/models/audit.py
──────────────────
Immutable audit log for security and compliance.
Tracks all significant actions for GDPR compliance and security monitoring.
"""

from __future__ import annotations

import enum
from datetime import datetime
from typing import Any, List, Optional

from sqlalchemy import (
    JSON,
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


class AuditAction(str, enum.Enum):
    """
    Standardized audit action types.
    Used for filtering and categorizing audit events.
    """
    # Authentication events
    USER_REGISTERED = "user.registered"
    USER_LOGIN = "user.login"
    USER_LOGOUT = "user.logout"
    LOGIN_FAILED = "auth.login_failed"
    LOGIN_RATE_LIMITED = "auth.login_rate_limited"
    PASSWORD_CHANGED = "auth.password_changed"
    PASSWORD_RESET_REQUESTED = "auth.password_reset_requested"
    PASSWORD_RESET_COMPLETED = "auth.password_reset_completed"
    TOKEN_REFRESHED = "auth.token_refreshed"
    SESSION_REVOKED = "auth.session_revoked"
    
    # Profile events
    PROFILE_VIEWED = "profile.viewed"
    PROFILE_UPDATED = "profile.updated"
    PROFILE_DELETED = "profile.deleted"
    
    # Resume events
    RESUME_UPLOADED = "resume.uploaded"
    RESUME_VIEWED = "resume.viewed"
    RESUME_DOWNLOADED = "resume.downloaded"
    RESUME_UPDATED = "resume.updated"
    RESUME_DELETED = "resume.deleted"
    
    # Credential events
    CREDENTIAL_STORED = "credential.stored"
    CREDENTIAL_UPDATED = "credential.updated"
    CREDENTIAL_DELETED = "credential.deleted"
    CREDENTIAL_USED = "credential.used"
    CREDENTIAL_EXPIRED = "credential.expired"
    CREDENTIAL_FAILED = "credential.failed"
    
    # Consent events
    CONSENT_GRANTED = "consent.granted"
    CONSENT_REVOKED = "consent.revoked"
    CONSENT_UPDATED = "consent.updated"
    
    # Application events
    APPLICATION_CREATED = "application.created"
    APPLICATION_SUBMITTED = "application.submitted"
    APPLICATION_WITHDRAWN = "application.withdrawn"
    
    # Data rights events (GDPR)
    DATA_EXPORT_REQUESTED = "data.export_requested"
    DATA_EXPORT_COMPLETED = "data.export_completed"
    DATA_DELETE_REQUESTED = "data.delete_requested"
    DATA_DELETE_COMPLETED = "data.delete_completed"
    DATA_ACCESSED = "data.accessed"
    
    # Security events
    SUSPICIOUS_ACTIVITY = "security.suspicious"
    RATE_LIMIT_EXCEEDED = "security.rate_limit"
    INVALID_TOKEN = "security.invalid_token"
    PERMISSION_DENIED = "security.permission_denied"
    
    # Admin events
    ADMIN_USER_CREATED = "admin.user_created"
    ADMIN_USER_UPDATED = "admin.user_updated"
    ADMIN_USER_DELETED = "admin.user_deleted"
    ADMIN_SETTINGS_CHANGED = "admin.settings_changed"


class AuditLog(Base, UUIDMixin):
    """
    Immutable audit log - append only, never modified or deleted.
    
    This is the backbone of:
    - GDPR compliance (right to access, data portability)
    - Security monitoring
    - Incident investigation
    - Compliance reporting
    """
    __tablename__ = "audit_logs"

    # ═══════════════════════════════════════════════════════════════
    # ACTOR (who performed the action)
    # ═════════════════════════════════════════════════════════════
    
    user_id: Mapped[Optional[str]] = mapped_column(
        String(36), index=True, nullable=True
    )
    # Can be null for failed auth attempts where user doesn't exist
    
    user_email: Mapped[Optional[str]] = mapped_column(
        String(255), nullable=True
    )
    # Stored separately in case user is deleted

    # ═════════════════════════════════════════════════════════════
    # ACTION (what happened)
    # ═════════════════════════════════════════════════════════════
    
    action: Mapped[str] = mapped_column(
        String(100), nullable=False, index=True
    )
    # e.g., "user.login", "profile.updated"
    
    resource_type: Mapped[str] = mapped_column(
        String(50), nullable=False
    )
    # e.g., "user", "profile", "resume", "credential"
    
    resource_id: Mapped[Optional[str]] = mapped_column(
        String(36), nullable=True
    )
    # ID of the affected resource

    # ═════════════════════════════════════════════════════════════
    # REQUEST CONTEXT (where it happened)
    # ═════════════════════════════════════════════════════════════
    
    ip_address: Mapped[Optional[str]] = mapped_column(
        String(45), nullable=True
    )
    # IPv4 or IPv6 address
    
    user_agent: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True
    )
    # Full user agent string
    
    request_method: Mapped[Optional[str]] = mapped_column(
        String(10), nullable=True
    )
    # HTTP method: GET, POST, PATCH, DELETE
    
    request_path: Mapped[Optional[str]] = mapped_column(
        String(500), nullable=True
    )
    # Full request path
    
    request_id: Mapped[Optional[str]] = mapped_column(
        String(36), nullable=True
    )
    # Correlation ID for request tracing

    # ═════════════════════════════════════════════════════════════
    # DETAILS (what specifically changed/happened)
    # ═════════════════════════════════════════════════════════════
    
    details: Mapped[Optional[dict]] = mapped_column(
        JSON, nullable=True
    )
    # Flexible payload:
    # For updates: {"field": "email", "old": "a@b.com", "new": "c@d.com"}
    # For creates: {"result": "created", "id": "..."}
    # For deletes: {"deleted_id": "...", "cascade": true}
    # For auth: {"method": "password", "mfa_used": false}
    
    changes: Mapped[Optional[list]] = mapped_column(
        JSON, nullable=True
    )
    # Array of changes for diff-style tracking:
    # [{"field": "email", "old": "a@b.com", "new": "c@d.com"}]

    # ═════════════════════════════════════════════════════════════
    # OUTCOME (what was the result)
    # ═════════════════════════════════════════════════════════════
    
    success: Mapped[bool] = mapped_column(
        Boolean, default=True, nullable=False
    )
    
    error_code: Mapped[Optional[str]] = mapped_column(
        String(50), nullable=True
    )
    # e.g., "INVALID_CREDENTIALS", "RATE_LIMITED", "NOT_FOUND"
    
    error_message: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True
    )
    # Human-readable error (sanitized, no PII)

    # ═════════════════════════════════════════════════════════════
    # TIMESTAMP (when it happened)
    # ═════════════════════════════════════════════════════════════
    
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        index=True
    )
    # Use UTC for all timestamps

    # ═════════════════════════════════════════════════════════════
    # TABLE CONFIGURATION
    # ═════════════════════════════════════════════════════════════
    
    __table_args__ = (
        # Composite indexes for common query patterns
        Index("ix_audit_user_action", "user_id", "action"),
        Index("ix_audit_user_timestamp", "user_id", "timestamp"),
        Index("ix_audit_timestamp_action", "timestamp", "action"),
        Index("ix_audit_resource", "resource_type", "resource_id"),
        Index("ix_audit_ip_timestamp", "ip_address", "timestamp"),
    )

    def __repr__(self) -> str:
        return f"<AuditLog {self.action} by {self.user_email} at {self.timestamp}>"


# Helper function for creating audit log entries
def create_audit_entry(
    action: str | AuditAction,
    resource_type: str,
    resource_id: Optional[str] = None,
    user_id: Optional[str] = None,
    user_email: Optional[str] = None,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
    request_method: Optional[str] = None,
    request_path: Optional[str] = None,
    request_id: Optional[str] = None,
    details: Optional[dict] = None,
    changes: Optional[list] = None,
    success: bool = True,
    error_code: Optional[str] = None,
    error_message: Optional[str] = None,
) -> AuditLog:
    """Factory function for creating audit log entries."""
    return AuditLog(
        action=action.value if isinstance(action, AuditAction) else action,
        resource_type=resource_type,
        resource_id=resource_id,
        user_id=user_id,
        user_email=user_email,
        ip_address=ip_address,
        user_agent=user_agent,
        request_method=request_method,
        request_path=request_path,
        request_id=request_id,
        details=details,
        changes=changes,
        success=success,
        error_code=error_code,
        error_message=error_message,
        timestamp=datetime.utcnow(),
    )
