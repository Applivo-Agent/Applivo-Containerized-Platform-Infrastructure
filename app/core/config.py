"""
app/core/config.py
"""
from __future__ import annotations
import json
from functools import lru_cache
from pathlib import Path
from typing import List, Literal, Optional, Union, Any, Dict
from pydantic import field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8",
        case_sensitive=False, extra="ignore",
    )
    APP_NAME: str = "AI Career Platform"
    APP_ENV: str = "production"
    APP_HOST: str = "0.0.0.0"
    APP_PORT: int = 8000
    DEBUG: bool = False
    FRONTEND_URL: str = "https://applivo.in"
    SECRET_KEY: str = "changeme-at-least-32-characters-long-secret"
    BROWSER_HEADLESS: bool = True
    
    # Database: PostgreSQL for production
    DATABASE_URL: str = "postgresql+asyncpg://applivo:password@localhost:5432/applivo"
    DATABASE_URL_SYNC: str = "postgresql://applivo:password@localhost:5432/applivo"
    # -----------------------------
    # Redis
    # -----------------------------
    REDIS_HOST: str = "redis"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: Optional[str] = "change_me_in_prod"

    @property
    def REDIS_URL(self) -> str:
        if self.REDIS_PASSWORD:
            return f"redis://:{self.REDIS_PASSWORD}@{self.REDIS_HOST}:{self.REDIS_PORT}/0"
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/0"

    # -----------------------------
    # Celery
    # -----------------------------
    @property
    def CELERY_BROKER_URL(self) -> str:
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/0"

    @property
    def CELERY_RESULT_BACKEND(self) -> str:
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/1"
    OPENAI_API_KEY: str = ""      # Legacy field — use GROQ_API_KEY instead
    GROQ_API_KEY: str = ""         # Groq API key (gsk_...) — used for all AI calls
    GEMINI_API_KEY: str = ""       # Gemini API key for fallback
    AI_PROVIDER: str = "groq"      # Primary: groq | gemini
    FALLBACK_PROVIDER: str = "gemini"  # Fallback when primary fails
    OPENAI_MODEL_HEAVY: str = "llama-3.3-70b-versatile"
    OPENAI_MODEL_LIGHT: str = "llama-3.1-8b-instant"

    @property
    def ai_api_key(self) -> str:
        """Return whichever API key is set — Groq takes priority."""
        return self.GROQ_API_KEY or self.OPENAI_API_KEY
    OPENAI_EMBEDDING_MODEL: str = "text-embedding-3-small"
    OPENAI_MAX_TOKENS: int = 4096
    OPENAI_TEMPERATURE: float = 0.3
    CHROMA_HOST: str = "chroma"
    CHROMA_PORT: int = 8001
    CHROMA_COLLECTION_USER_PROFILE: str = "user_profile"
    CHROMA_COLLECTION_JOBS: str = "jobs"
    CHROMA_COLLECTION_RESUMES: str = "resumes"
    TELEGRAM_BOT_TOKEN: str = ""
    TELEGRAM_CHAT_ID: str = ""
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USERNAME: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_FROM_EMAIL: str = ""
    SMTP_FROM_NAME: str = "AI Career Agent"
    # IMAP settings for inbox monitoring
    IMAP_HOST: str = "imap.gmail.com"
    IMAP_PORT: int = 993
    IMAP_USERNAME: str = ""
    IMAP_PASSWORD: str = ""
    STORAGE_BACKEND: str = "local"
    LOCAL_STORAGE_PATH: str = "./storage"
    SCRAPE_INTERVAL_HOURS: int = 6
    MAX_JOBS_PER_CYCLE: int = 200
    SCRAPE_DELAY_MIN_SECONDS: float = 2.0
    SCRAPE_DELAY_MAX_SECONDS: float = 6.0
    LINKEDIN_EMAIL: str = ""
    LINKEDIN_PASSWORD: str = ""
    INTERNShALA_EMAIL: str = ""
    INTERNShALA_PASSWORD: str = ""
    INDEED_EMAIL: str = ""
    INDEED_PASSWORD: str = ""
    AUTO_APPLY_ENABLED: bool = False
    AUTO_APPLY_MATCH_THRESHOLD: int = 40
    AUTO_APPLY_DAILY_LIMIT: int = 10
    AUTO_APPLY_REQUIRE_APPROVAL: bool = True
    USE_COVER_LETTER: bool = False
    ALLOWED_ORIGINS: List[str] = ["https://applivo.in", "https://www.applivo.in"]
    USER_NAME: str = ""
    USER_EMAIL: str = ""
    USER_PHONE: str = ""
    USER_LOCATION: str = ""
    USER_LINKEDIN_URL: str = ""
    USER_GITHUB_URL: str = ""
    USER_DESIRED_ROLES: List[str] = []
    USER_DESIRED_LOCATIONS: List[str] = []
    USER_EXPERIENCE_LEVEL: str = "ENTRY"
    USER_OPEN_TO_REMOTE: bool = True
    USER_MIN_SALARY: int = 0
    JWT_SECRET_KEY: str = "changeme-jwt-secret-at-least-32-characters-long"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    GOOGLE_CLIENT_ID: str = ""
    ENCRYPTION_KEY: str = ""

    # ── Sentry Monitoring ──────────────────────────────────────
    SENTRY_DSN: str = ""
    SENTRY_TRACES_SAMPLE_RATE: float = 0.1

    # ── OTP Security ──────────────────────────────────────────
    OTP_EXPIRE_MINUTES: int = 10
    OTP_EXPIRY_SECONDS: int = 600
    OTP_LENGTH: int = 6

    # ── Razorpay Payment Gateway ───────────────────────────────
    RAZORPAY_KEY_ID: str = ""
    RAZORPAY_KEY_SECRET: str = ""
    RAZORPAY_WEBHOOK_SECRET: str = ""

    # ── Rate Limiting ──────────────────────────────────────────
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_WINDOW_SECONDS: int = 60
    AUTH_RATE_LIMIT_REQUESTS: int = 5
    AUTH_RATE_LIMIT_WINDOW_SECONDS: int = 300
    AUTH_RATE_LIMIT_DEV_REQUESTS: int = 50
    AUTH_RATE_LIMIT_DEV_WINDOW_SECONDS: int = 60

    # ── Redis ───────────────────────────────────────────────────

    @property
    def storage_path(self) -> Path:
        p = Path(self.LOCAL_STORAGE_PATH)
        p.mkdir(parents=True, exist_ok=True)
        return p

    @property
    def resumes_path(self) -> Path:
        p = self.storage_path / "resumes"
        p.mkdir(exist_ok=True)
        return p

    @property
    def cover_letters_path(self) -> Path:
        p = self.storage_path / "cover_letters"
        p.mkdir(exist_ok=True)
        return p

    @property
    def recordings_path(self) -> Path:
        p = self.storage_path / "recordings"
        p.mkdir(exist_ok=True)
        return p

    @field_validator("USER_DESIRED_ROLES", "USER_DESIRED_LOCATIONS", mode="before")
    @classmethod
    def parse_json_list(cls, v):
        if isinstance(v, str):
            try:
                return json.loads(v)
            except json.JSONDecodeError:
                return [i.strip() for i in v.split(",") if i.strip()]
        return v

    @field_validator("SMTP_PASSWORD", mode="before")
    @classmethod
    def normalize_smtp_password(cls, v):
        if isinstance(v, str):
            return v.replace(" ", "")
        return v

    @model_validator(mode="after")
    def validate_production_network_settings(self):
        if self.APP_ENV != "production":
            return self

        # In production, local loopback URLs/hosts usually indicate a bad env file.
        def _is_local(value: str) -> bool:
            lowered = value.lower()
            return "localhost" in lowered or "127.0.0.1" in lowered

        if _is_local(self.FRONTEND_URL):
            raise ValueError("FRONTEND_URL cannot point to localhost/127.0.0.1 in production")

        if _is_local(self.DATABASE_URL) or _is_local(self.DATABASE_URL_SYNC):
            raise ValueError("DATABASE_URL and DATABASE_URL_SYNC cannot point to localhost/127.0.0.1 in production")

        if _is_local(self.REDIS_HOST) or _is_local(self.REDIS_URL):
            raise ValueError("REDIS_HOST/REDIS_URL cannot point to localhost/127.0.0.1 in production")

        if any(_is_local(origin) for origin in self.ALLOWED_ORIGINS):
            raise ValueError("ALLOWED_ORIGINS cannot contain localhost/127.0.0.1 in production")

        return self

@lru_cache()
def get_settings() -> Settings:
    return Settings()

settings = get_settings()