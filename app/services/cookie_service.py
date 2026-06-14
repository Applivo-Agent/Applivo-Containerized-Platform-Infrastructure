"""
app/services/cookie_service.py
───────────────────────────────
Encrypted platform cookie management for multi-user automation.
Cookies are AES-256-GCM encrypted at rest, user-specific, and validated periodically.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone, timedelta
from typing import Optional, Union

import structlog
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db_context
from app.models.cookie import PlatformCookie
from app.services.encryption import EncryptionService

logger = structlog.get_logger()

SUPPORTED_PLATFORMS = ["internshala"]  # Future: linkedin, indeed, naukri


class CookieService:
    """Manages encrypted platform cookies for user automation sessions."""

    def __init__(self):
        self._encryption: Optional[EncryptionService] = None

    @property
    def enc(self) -> EncryptionService:
        if self._encryption is None:
            self._encryption = EncryptionService()
        return self._encryption

    async def save_cookies(
        self,
        user_id: str,
        platform: str,
        cookies: Union[dict, list],
    ) -> PlatformCookie:
        """
        Encrypt and save platform cookies for a user.
        Replaces any existing cookies for the same platform.
        Sets expiry to 30 days from now (typical Internshala session duration).
        """
        if platform not in SUPPORTED_PLATFORMS:
            raise ValueError(f"Unsupported platform: {platform}. Supported: {SUPPORTED_PLATFORMS}")

        encrypted = self.enc.encrypt(cookies)

        async with get_db_context() as db:
            result = await db.execute(
                select(PlatformCookie).where(
                    PlatformCookie.user_id == user_id,
                    PlatformCookie.platform == platform,
                )
            )
            existing = result.scalar_one_or_none()

            now = datetime.now(timezone.utc)
            # Cookies typically expire in 30 days for Internshala
            expires_at = now + timedelta(days=30)
            
            if existing:
                existing.encrypted_cookies = encrypted
                existing.is_valid = True
                existing.last_validated_at = now
                existing.expires_at = expires_at
                existing.updated_at = now
                await db.commit()
                await db.refresh(existing)
                logger.info("Cookies updated", user_id=user_id, platform=platform)
                return existing

            cookie = PlatformCookie(
                user_id=user_id,
                platform=platform,
                encrypted_cookies=encrypted,
                is_valid=True,
                last_validated_at=now,
                expires_at=expires_at,
            )
            db.add(cookie)
            await db.commit()
            await db.refresh(cookie)
            logger.info("Cookies saved", user_id=user_id, platform=platform)
            return cookie

    async def get_cookies(
        self, user_id: str, platform: str,
    ) -> Optional[Union[dict, list]]:
        """Decrypt and return platform cookies for a user."""
        async with get_db_context() as db:
            result = await db.execute(
                select(PlatformCookie).where(
                    PlatformCookie.user_id == user_id,
                    PlatformCookie.platform == platform,
                    PlatformCookie.is_valid == True,
                )
            )
            cookie = result.scalar_one_or_none()
            if not cookie:
                return None

            try:
                decrypted = self.enc.decrypt_json(cookie.encrypted_cookies)
                return decrypted
            except Exception as e:
                logger.error("Cookie decryption failed", user_id=user_id, platform=platform, error=str(e))
                cookie.is_valid = False
                await db.commit()
                return None

    async def validate_cookies(self, user_id: str, platform: str) -> dict:
        """Check if cookies exist and are not expired."""
        async with get_db_context() as db:
            result = await db.execute(
                select(PlatformCookie).where(
                    PlatformCookie.user_id == user_id,
                    PlatformCookie.platform == platform,
                )
            )
            cookie = result.scalar_one_or_none()

            if not cookie:
                return {"valid": False, "reason": "No cookies found"}

            if not cookie.is_valid:
                return {"valid": False, "reason": "Cookies marked invalid"}

            if cookie.expires_at and cookie.expires_at < datetime.now(timezone.utc):
                cookie.is_valid = False
                await db.commit()
                return {"valid": False, "reason": "Cookies expired"}

            return {"valid": True, "last_validated": cookie.last_validated_at.isoformat() if cookie.last_validated_at else None}

    async def invalidate_cookies(self, user_id: str, platform: str) -> bool:
        """Mark cookies as invalid (e.g., when session expires)."""
        async with get_db_context() as db:
            result = await db.execute(
                select(PlatformCookie).where(
                    PlatformCookie.user_id == user_id,
                    PlatformCookie.platform == platform,
                )
            )
            cookie = result.scalar_one_or_none()
            if cookie:
                cookie.is_valid = False
                await db.commit()
                logger.info("Cookies invalidated", user_id=user_id, platform=platform)
                return True
            return False

    async def delete_cookies(self, user_id: str, platform: str) -> bool:
        """Delete platform cookies for a user."""
        async with get_db_context() as db:
            result = await db.execute(
                select(PlatformCookie).where(
                    PlatformCookie.user_id == user_id,
                    PlatformCookie.platform == platform,
                )
            )
            cookie = result.scalar_one_or_none()
            if cookie:
                await db.delete(cookie)
                await db.commit()
                logger.info("Cookies deleted", user_id=user_id, platform=platform)
                return True
            return False

    async def list_platforms(self, user_id: str) -> list[dict]:
        """List all platform cookie statuses for a user."""
        async with get_db_context() as db:
            result = await db.execute(
                select(PlatformCookie).where(PlatformCookie.user_id == user_id)
            )
            cookies = result.scalars().all()
            return [
                {
                    "platform": c.platform,
                    "is_valid": c.is_valid,
                    "last_validated": c.last_validated_at.isoformat() if c.last_validated_at else None,
                    "last_used": c.last_used_at.isoformat() if c.last_used_at else None,
                    "expires_at": c.expires_at.isoformat() if c.expires_at else None,
                }
                for c in cookies
            ]


cookie_service = CookieService()
