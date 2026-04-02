"""
app/api/routes/security.py
API routes for credentials, consent, and data rights.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.routes.auth import get_current_user
from app.core.database import get_db
from app.models.user import User
from app.models.credential import CredentialVault, CredentialType
from app.models.consent import UserConsent, ConsentType, ConsentScope, DEFAULT_CONSENTS
from app.models.audit import AuditLog, AuditAction, create_audit_entry

# Lazy initialization to avoid circular imports
def get_credential_manager():
    from app.services.encryption import credential_manager
    return credential_manager

router = APIRouter(prefix="/security", tags=["Security"])


# ─────────────────────────────────────────────────────────────────
# Pydantic Schemas
# ─────────────────────────────────────────────────────────────────

class CredentialCreate(BaseModel):
    credential_type: str
    display_name: str
    credentials: dict  # {"email": "...", "password": "..."}
    scope: Optional[dict] = None
    consent: bool = True


class CredentialResponse(BaseModel):
    id: str
    credential_type: str
    display_name: str
    is_active: bool
    consent_given: bool
    use_count: int
    last_used_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None


class ConsentCreate(BaseModel):
    consent_type: str
    scope: str
    granted: bool
    purpose: str
    data_categories: list[str] = []


class ConsentResponse(BaseModel):
    id: str
    consent_type: str
    scope: str
    granted: bool
    purpose: str
    data_categories: list[str]
    granted_at: Optional[datetime] = None


# ─────────────────────────────────────────────────────────────────
# Credentials API
# ─────────────────────────────────────────────────────────────────

@router.get("/credentials", response_model=list[CredentialResponse])
async def list_credentials(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List all stored credentials (metadata only, no secrets)."""
    result = await db.execute(
        select(CredentialVault)
        .where(CredentialVault.user_id == current_user.id)
        .order_by(CredentialVault.created_at.desc())
    )
    credentials = result.scalars().all()
    
    return [
        CredentialResponse(
            id=c.id,
            credential_type=c.credential_type,
            display_name=c.display_name,
            is_active=c.is_active,
            consent_given=c.consent_given,
            use_count=c.use_count,
            last_used_at=c.last_used_at,
            expires_at=c.expires_at,
        )
        for c in credentials
    ]


@router.post("/credentials", response_model=CredentialResponse, status_code=201)
async def store_credential(
    payload: CredentialCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Store encrypted credentials for a platform."""
    if not payload.consent:
        raise HTTPException(
            status_code=400,
            detail="Consent is required to store credentials"
        )
    
    # Validate credential type
    try:
        cred_type = CredentialType(payload.credential_type)
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid credential type. Valid: {[e.value for e in CredentialType]}"
        )
    
    # Encrypt credentials
    encrypted = get_credential_manager().store_credential(
        credential_type=payload.credential_type,
        credentials=payload.credentials,
        display_name=payload.display_name,
        scope=payload.scope,
    )
    
    # Create vault entry
    vault = CredentialVault(
        user_id=current_user.id,
        credential_type=payload.credential_type,
        display_name=payload.display_name,
        encrypted_data=encrypted["encrypted_data"],
        scope=encrypted.get("scope"),
        consent_given=True,
        consent_timestamp=datetime.now(timezone.utc),
        consent_purpose="Store credentials for job platform automation",
    )
    
    db.add(vault)
    
    # Audit log
    audit = create_audit_entry(
        action=AuditAction.CREDENTIAL_STORED,
        resource_type="credential",
        resource_id=vault.id,
        user_id=current_user.id,
        user_email=current_user.email,
        details={"credential_type": payload.credential_type, "display_name": payload.display_name},
    )
    db.add(audit)
    
    await db.commit()
    await db.refresh(vault)
    
    return CredentialResponse(
        id=vault.id,
        credential_type=vault.credential_type,
        display_name=vault.display_name,
        is_active=vault.is_active,
        consent_given=vault.consent_given,
        use_count=vault.use_count,
        last_used_at=vault.last_used_at,
        expires_at=vault.expires_at,
    )


@router.delete("/credentials/{credential_id}")
async def delete_credential(
    credential_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete a stored credential."""
    result = await db.execute(
        select(CredentialVault)
        .where(
            CredentialVault.id == credential_id,
            CredentialVault.user_id == current_user.id
        )
    )
    vault = result.scalar_one_or_none()
    
    if not vault:
        raise HTTPException(status_code=404, detail="Credential not found")
    
    # Audit log before delete
    audit = create_audit_entry(
        action=AuditAction.CREDENTIAL_DELETED,
        resource_type="credential",
        resource_id=vault.id,
        user_id=current_user.id,
        user_email=current_user.email,
        details={"credential_type": vault.credential_type},
    )
    db.add(audit)
    
    await db.delete(vault)
    await db.commit()
    
    return {"message": "Credential deleted"}


# ─────────────────────────────────────────────────────────────────
# Consent API
# ─────────────────────────────────────────────────────────────────

@router.get("/consents", response_model=list[ConsentResponse])
async def list_consents(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List all user consents."""
    result = await db.execute(
        select(UserConsent)
        .where(UserConsent.user_id == current_user.id)
    )
    consents = result.scalars().all()
    
    return [
        ConsentResponse(
            id=c.id,
            consent_type=c.consent_type,
            scope=c.scope,
            granted=c.granted,
            purpose=c.purpose,
            data_categories=c.data_categories or [],
            granted_at=c.granted_at,
        )
        for c in consents
    ]


@router.get("/consents/defaults")
async def get_default_consents():
    """Get the default consent requirements."""
    return DEFAULT_CONSENTS


@router.post("/consents", response_model=ConsentResponse, status_code=201)
async def update_consent(
    payload: ConsentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Grant or revoke consent for a specific purpose."""
    # Check if consent exists
    result = await db.execute(
        select(UserConsent)
        .where(
            UserConsent.user_id == current_user.id,
            UserConsent.consent_type == payload.consent_type,
        )
    )
    existing = result.scalar_one_or_none()
    
    now = datetime.now(timezone.utc)
    
    if existing:
        # Update existing
        existing.granted = payload.granted
        existing.revoked = now if not payload.granted else None
        existing.granted_at = now if payload.granted else None
        consent = existing
    else:
        # Create new
        consent = UserConsent(
            user_id=current_user.id,
            consent_type=payload.consent_type,
            scope=payload.scope,
            granted=payload.granted,
            granted_at=now if payload.granted else None,
            policy_version="1.0",
            purpose=payload.purpose,
            data_categories=payload.data_categories,
        )
        db.add(consent)
    
    # Audit log
    audit = create_audit_entry(
        action=AuditAction.CONSENT_GRANTED if payload.granted else AuditAction.CONSENT_REVOKED,
        resource_type="consent",
        user_id=current_user.id,
        user_email=current_user.email,
        details={"consent_type": payload.consent_type, "scope": payload.scope},
    )
    db.add(audit)
    
    await db.commit()
    await db.refresh(consent)
    
    return ConsentResponse(
        id=consent.id,
        consent_type=consent.consent_type,
        scope=consent.scope,
        granted=consent.granted,
        purpose=consent.purpose,
        data_categories=consent.data_categories or [],
        granted_at=consent.granted_at,
    )


# ─────────────────────────────────────────────────────────────────
# Data Rights API (GDPR)
# ─────────────────────────────────────────────────────────────────

@router.post("/data/export")
async def request_data_export(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Request export of all user data."""
    # Audit log
    audit = create_audit_entry(
        action=AuditAction.DATA_EXPORT_REQUESTED,
        resource_type="user",
        resource_id=current_user.id,
        user_id=current_user.id,
        user_email=current_user.email,
    )
    db.add(audit)
    await db.commit()
    
    return {
        "message": "Data export requested",
        "status": "processing",
        "note": "You will receive an email when your data is ready for download"
    }


@router.post("/data/delete")
async def request_data_deletion(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Request deletion of all user data."""
    # Audit log
    audit = create_audit_entry(
        action=AuditAction.DATA_DELETE_REQUESTED,
        resource_type="user",
        resource_id=current_user.id,
        user_id=current_user.id,
        user_email=current_user.email,
    )
    db.add(audit)
    await db.commit()
    
    return {
        "message": "Data deletion requested",
        "status": "processing",
        "note": "Your data will be deleted within 30 days. You can cancel within 14 days."
    }


@router.get("/data/audit")
async def get_my_audit_history(
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get user's own audit history."""
    result = await db.execute(
        select(AuditLog)
        .where(AuditLog.user_id == current_user.id)
        .order_by(AuditLog.timestamp.desc())
        .limit(limit)
    )
    logs = result.scalars().all()
    
    return [
        {
            "action": log.action,
            "resource_type": log.resource_type,
            "timestamp": log.timestamp.isoformat() if log.timestamp else None,
            "success": log.success,
        }
        for log in logs
    ]
