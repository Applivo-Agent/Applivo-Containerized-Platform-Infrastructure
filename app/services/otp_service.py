from __future__ import annotations
import random
import string
import structlog
from typing import Optional
from app.core.config import settings
from app.services.cache_service import CacheService

logger = structlog.get_logger()

class OTPService:
    """
    Handles One-Time Password (OTP) generation, storage, and validation.
    OTPs are stored in Redis with a configurable TTL.
    """

    def __init__(self, cache_service: CacheService = None):
        from app.services.cache_service import cache_service as default_cache
        self.cache = cache_service or default_cache

    def generate_otp(self, length: int = None) -> str:
        """Generate a numeric OTP of specified length."""
        otp_length = length or settings.OTP_LENGTH
        return "".join(random.choices(string.digits, k=otp_length))

    @staticmethod
    def _normalize_email(email: str) -> str:
        # Normalize email to keep OTP keys consistent across initiate/verify requests.
        return str(email or "").strip().lower()

    async def store_otp(self, email: str, purpose: str, otp: str, ttl_seconds: int = None) -> bool:
        """Store OTP in Redis with a TTL."""
        ttl = ttl_seconds or settings.OTP_EXPIRY_SECONDS
        key = f"otp:{purpose}:{self._normalize_email(email)}"
        return await self.cache.set(key, otp, ttl=ttl)

    async def verify_otp(self, email: str, purpose: str, submitted_otp: str) -> bool:
        """Verify the submitted OTP and delete it if valid."""
        normalized_email = self._normalize_email(email)
        key = f"otp:{purpose}:{normalized_email}"
        stored_otp = await self.cache.get(key)

        # Backward compatibility for OTPs stored before email key normalization.
        if stored_otp is None and normalized_email != str(email):
            legacy_key = f"otp:{purpose}:{email}"
            stored_otp = await self.cache.get(legacy_key)
            if stored_otp is not None:
                key = legacy_key

        submitted = "".join(ch for ch in str(submitted_otp or "").strip() if ch.isdigit())
        if len(submitted) != settings.OTP_LENGTH:
            submitted = str(submitted_otp or "").strip()
        
        if stored_otp is not None and str(stored_otp).strip() == submitted:
            await self.cache.delete(key)
            return True
        
        return False

# Global OTP service instance
otp_service = OTPService()
