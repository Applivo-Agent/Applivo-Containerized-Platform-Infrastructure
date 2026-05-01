"""
app/core/database.py
"""
from __future__ import annotations
from contextlib import asynccontextmanager
from typing import AsyncGenerator
from sqlalchemy import text
from sqlalchemy.ext.asyncio import (
    AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.pool import NullPool
from app.core.config import settings

class Base(DeclarativeBase):
    pass

def _build_engine() -> AsyncEngine:
    # SQLite doesn't need pooling, PostgreSQL does
    is_sqlite = settings.DATABASE_URL.startswith("sqlite")
    
    kwargs: dict = dict(echo=settings.DEBUG, echo_pool=False)
    
    if settings.APP_ENV == "testing":
        kwargs = {"echo": False, "poolclass": NullPool}
    elif is_sqlite:
        # SQLite: no pooling, direct file access
        kwargs = {
            "echo": settings.DEBUG,
            "connect_args": {"check_same_thread": False, "timeout": 30},
            "poolclass": NullPool,
        }
    else:
        # PostgreSQL: connection pooling
        kwargs = dict(
            pool_pre_ping=True,
            pool_size=10, max_overflow=20, pool_timeout=30, pool_recycle=1800,
        )
    
    return create_async_engine(settings.DATABASE_URL, **kwargs)

engine: AsyncEngine = _build_engine()

AsyncSessionLocal = async_sessionmaker(
    bind=engine, class_=AsyncSession,
    expire_on_commit=False, autoflush=False, autocommit=False,
)

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

@asynccontextmanager
async def get_db_context() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

async def check_db_connection() -> bool:
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        return True
    except Exception:
        return False

async def init_db() -> None:
    from app.models import (  # noqa: F401
        user, job, application, resume, interview,
        subscription, cookie, credential, consent, audit,
        chat_message, chat_usage, platform_message,
    )
    async with engine.begin() as conn:
        # Enable WAL mode for better concurrency with SQLite
        if settings.DATABASE_URL.startswith("sqlite"):
            await conn.execute(text("PRAGMA journal_mode=WAL;"))
        
        await conn.run_sync(Base.metadata.create_all)
        # Create indexes for performance
        await conn.run_sync(_create_indexes)


def _create_indexes(connection):
    """Create performance indexes."""
    indexes = [
        "CREATE INDEX IF NOT EXISTS ix_job_analyses_job_id ON job_analyses(job_id)",
        "CREATE INDEX IF NOT EXISTS ix_job_analyses_match_score ON job_analyses(match_score)",
        "CREATE INDEX IF NOT EXISTS ix_job_analyses_priority_score ON job_analyses(priority_score)",
        "CREATE INDEX IF NOT EXISTS ix_applications_user_id ON applications(user_id)",
        "CREATE INDEX IF NOT EXISTS ix_applications_status ON applications(status)",
        "CREATE INDEX IF NOT EXISTS ix_applications_created_at ON applications(created_at)",
        "CREATE INDEX IF NOT EXISTS ix_notifications_user_id ON notifications(user_id)",
        "CREATE INDEX IF NOT EXISTS ix_subscriptions_user_id ON subscriptions(user_id)",
        "CREATE INDEX IF NOT EXISTS ix_payments_user_id ON payments(user_id)",
    ]
    for idx in indexes:
        try:
            connection.execute(text(idx))
        except Exception:
            pass  # Index may already exist

async def close_db() -> None:
    await engine.dispose()
