"""
app/core/config.py
"""
from __future__ import annotations
import json
from functools import lru_cache
from pathlib import Path
from typing import List, Literal
from pydantic import field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8",
        case_sensitive=False, extra="ignore",
    )
    APP_NAME: str = "AI Career Platform"
    APP_ENV: str = "development"
    APP_HOST: str = "0.0.0.0"
    APP_PORT: int = 8000
    DEBUG: bool = True
    SECRET_KEY: str = "changeme-at-least-32-characters-long-secret"
    
    # Database: SQLite for desktop (no server needed), PostgreSQL for production
    DATABASE_URL: str = "sqlite+aiosqlite:///./applivo.db"
    DATABASE_URL_SYNC: str = "sqlite:///./applivo.db"
    REDIS_URL: str = "redis://localhost:6379/0"
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/1"
    OPENAI_API_KEY: str = ""      # Legacy field — use GROQ_API_KEY instead
    GROQ_API_KEY: str = ""         # Groq API key (gsk_...) — used for all AI calls
    OPENAI_MODEL_HEAVY: str = "llama3-70b-8192"
    OPENAI_MODEL_LIGHT: str = "llama3-8b-8192"

    @property
    def ai_api_key(self) -> str:
        """Return whichever API key is set — Groq takes priority."""
        return self.GROQ_API_KEY or self.OPENAI_API_KEY
    OPENAI_EMBEDDING_MODEL: str = "text-embedding-3-small"
    OPENAI_MAX_TOKENS: int = 4096
    OPENAI_TEMPERATURE: float = 0.3
    CHROMA_HOST: str = "localhost"
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
    AUTO_APPLY_MATCH_THRESHOLD: int = 75
    AUTO_APPLY_DAILY_LIMIT: int = 10
    AUTO_APPLY_REQUIRE_APPROVAL: bool = True
    USER_NAME: str = ""
    USER_EMAIL: str = ""
    USER_PHONE: str = ""
    USER_LOCATION: str = ""
    USER_LINKEDIN_URL: str = ""
    USER_GITHUB_URL: str = ""
    USER_DESIRED_ROLES: List[str] = []
    USER_DESIRED_LOCATIONS: List[str] = []
    USER_EXPERIENCE_LEVEL: str = "entry"
    USER_OPEN_TO_REMOTE: bool = True
    USER_MIN_SALARY: int = 0
    JWT_SECRET_KEY: str = "changeme-jwt-secret-at-least-32-characters-long"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440
    ENCRYPTION_KEY: str = ""

    # ── Razorpay Payment Gateway ───────────────────────────────
    RAZORPAY_KEY_ID: str = ""
    RAZORPAY_KEY_SECRET: str = ""

    # ── Rate Limiting ──────────────────────────────────────────
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_WINDOW_SECONDS: int = 60

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

@lru_cache()
def get_settings() -> Settings:
    return Settings()

settings = get_settings()