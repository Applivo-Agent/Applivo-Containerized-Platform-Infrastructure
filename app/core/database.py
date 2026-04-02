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
            "connect_args": {"check_same_thread": False},
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
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def close_db() -> None:
    await engine.dispose()
