"""
app/main.py
───────────
FastAPI application for the Applivo SaaS platform.
Registers all routers, middleware, startup/shutdown events.
All automation runs server-side — no desktop dependencies.
"""

from __future__ import annotations

from contextlib import asynccontextmanager
from pathlib import Path
import structlog
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.core.database import check_db_connection, close_db, init_db, get_db_context

# ── Routers ───────────────────────────────────────────────
from app.api.routes.auth import router as auth_router
from app.api.routes.jobs import router as jobs_router
from app.api.routes.profile import router as profile_router
from app.api.routes.security import router as security_router
from app.api.routes.onboarding import router as onboarding_router
from app.api.routes.scheduler import router as scheduler_router
from app.api.routes.settings_v2 import settings_v2_router
from app.api.routes.settings_route import settings_router
from app.api.routes.subscriptions import router as subscriptions_router
from app.api.routes.payments import router as payments_router
from app.api.routes.platform import router as platform_router
from app.api.routes.quotas import router as quotas_router
from app.api.routes.admin import admin_router
from app.api.routes.outreach import router as outreach_router
from app.api.routes.routes import (
    applications_router,
    resumes_router,
    cover_letters_router,
    agent_router,
    analytics_router,
    chat_router,
    workflow_router,
)

logger = structlog.get_logger()

# ── Sentry Error Tracking ─────────────────────────────────────────────────────

try:
    import sentry_sdk
    from sentry_sdk.integrations.fastapi import FastApiIntegration
    
    if settings.SENTRY_DSN:
        sentry_sdk.init(
            dsn=settings.SENTRY_DSN,
            integrations=[FastApiIntegration()],
            environment=settings.APP_ENV,
            traces_sample_rate=1.0,
        )
        logger.info("Sentry initialized")
except ImportError:
    logger.warning("Sentry SDK not found. Skipping error tracking.")
except Exception as e:
    logger.error("Sentry initialization failed", error=str(e))


# ── Auto-migration helper ─────────────────────────────────────────────────────

async def _run_sqlite_migrations() -> None:
    """Idempotent schema migrations for SQLite."""
    import sqlite3
    db_url = settings.DATABASE_URL_SYNC
    if not db_url.startswith("sqlite"):
        return
        
    db_path = db_url.replace("sqlite:///", "").replace("sqlite://", "")

    try:
        conn = sqlite3.connect(db_path)
        conn.execute("PRAGMA foreign_keys = OFF")
        cur = conn.cursor()

        cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='jobs'")
        if not cur.fetchone():
            conn.close()
            return

        cur.execute("PRAGMA table_info(jobs)")
        cols = [r[1] for r in cur.fetchall()]

        cur.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='jobs'")
        ddl = cur.fetchone()[0] or ""
        needs_rebuild = "uq_job_source_user" not in ddl

        if "user_id" not in cols or needs_rebuild:
            logger.info("Migrating jobs table: adding user_id + per-user unique constraint")
            cur.executescript("""
                CREATE TABLE IF NOT EXISTS jobs_migrated (
                    source VARCHAR(12) NOT NULL,
                    source_job_id VARCHAR(255) NOT NULL,
                    source_url VARCHAR(2000) NOT NULL,
                    raw_html TEXT,
                    title VARCHAR(500) NOT NULL,
                    company_name VARCHAR(255) NOT NULL,
                    company_logo_url VARCHAR(2000),
                    company_website VARCHAR(500),
                    description_raw TEXT,
                    description_clean TEXT,
                    location VARCHAR(255),
                    country VARCHAR(100),
                    city VARCHAR(100),
                    work_mode VARCHAR(7) NOT NULL,
                    job_type VARCHAR(10) NOT NULL,
                    experience_level VARCHAR(7) NOT NULL,
                    salary_min INTEGER,
                    salary_max INTEGER,
                    salary_currency VARCHAR(10),
                    salary_period VARCHAR(20),
                    posted_at DATETIME,
                    expires_at DATETIME,
                    scraped_at DATETIME NOT NULL,
                    status VARCHAR(8) NOT NULL,
                    is_active BOOLEAN NOT NULL,
                    applicant_count INTEGER,
                    easy_apply BOOLEAN NOT NULL,
                    id VARCHAR(36) NOT NULL,
                    created_at DATETIME DEFAULT (CURRENT_TIMESTAMP) NOT NULL,
                    updated_at DATETIME DEFAULT (CURRENT_TIMESTAMP) NOT NULL,
                    user_id TEXT REFERENCES users(id) ON DELETE CASCADE,
                    PRIMARY KEY (id),
                    CONSTRAINT uq_job_source_user UNIQUE (source, source_job_id, user_id)
                );
                INSERT OR IGNORE INTO jobs_migrated
                    SELECT source, source_job_id, source_url, raw_html, title,
                           company_name, company_logo_url, company_website,
                           description_raw, description_clean, location, country,
                           city, work_mode, job_type, experience_level,
                           salary_min, salary_max, salary_currency, salary_period,
                           posted_at, expires_at, scraped_at, status, is_active,
                           applicant_count, easy_apply, id, created_at, updated_at,
                           NULL
                    FROM jobs;
                DROP TABLE jobs;
                ALTER TABLE jobs_migrated RENAME TO jobs;
                CREATE INDEX IF NOT EXISTS ix_jobs_id ON jobs (id);
                CREATE INDEX IF NOT EXISTS ix_jobs_source ON jobs (source);
                CREATE INDEX IF NOT EXISTS ix_jobs_title ON jobs (title);
                CREATE INDEX IF NOT EXISTS ix_jobs_company_name ON jobs (company_name);
                CREATE INDEX IF NOT EXISTS ix_jobs_status ON jobs (status);
                CREATE INDEX IF NOT EXISTS ix_jobs_is_active ON jobs (is_active);
                CREATE INDEX IF NOT EXISTS ix_jobs_job_type ON jobs (job_type);
                CREATE INDEX IF NOT EXISTS ix_jobs_work_mode ON jobs (work_mode);
                CREATE INDEX IF NOT EXISTS ix_jobs_created_at ON jobs (created_at);
                CREATE INDEX IF NOT EXISTS ix_jobs_user_id ON jobs (user_id);
            """)
            conn.commit()
            logger.info("Jobs table migration complete")
        else:
            cur.execute("CREATE INDEX IF NOT EXISTS ix_jobs_user_id ON jobs (user_id)")
            conn.commit()

        conn.execute("PRAGMA foreign_keys = ON")
        conn.close()
    except Exception as exc:
        logger.warning("SQLite migration skipped", error=str(exc))


async def _run_postgres_schema_reconciliation() -> None:
    """Idempotent schema reconciliation for PostgreSQL deployments."""
    db_url = settings.DATABASE_URL_SYNC
    if not db_url.startswith("postgresql"):
        return

    from sqlalchemy import text

    try:
        async with get_db_context() as db:
            # Add missing multi-tenant columns expected by current models.
            await db.execute(text("ALTER TABLE IF EXISTS jobs ADD COLUMN IF NOT EXISTS user_id VARCHAR(36)"))
            await db.execute(text("ALTER TABLE IF EXISTS agent_tasks ADD COLUMN IF NOT EXISTS user_id VARCHAR(36)"))

            # Ensure indexes used by API filters exist.
            await db.execute(text("CREATE INDEX IF NOT EXISTS ix_jobs_user_id ON jobs(user_id)"))
            await db.execute(text("CREATE INDEX IF NOT EXISTS ix_agent_tasks_user_id ON agent_tasks(user_id)"))

            # Backfill jobs.user_id from applications where possible.
            await db.execute(
                text(
                    """
                    UPDATE jobs j
                    SET user_id = src.user_id
                    FROM (
                        SELECT job_id, MIN(user_id) AS user_id
                        FROM applications
                        WHERE user_id IS NOT NULL
                        GROUP BY job_id
                    ) AS src
                    WHERE j.id = src.job_id
                      AND j.user_id IS NULL
                    """
                )
            )

            # Backfill agent_tasks.user_id from related entities where possible.
            await db.execute(
                text(
                    """
                    UPDATE agent_tasks t
                    SET user_id = a.user_id
                    FROM applications a
                    WHERE t.user_id IS NULL
                      AND t.related_application_id IS NOT NULL
                      AND t.related_application_id = a.id
                    """
                )
            )
            await db.execute(
                text(
                    """
                    UPDATE agent_tasks t
                    SET user_id = j.user_id
                    FROM jobs j
                    WHERE t.user_id IS NULL
                      AND t.related_job_id IS NOT NULL
                      AND t.related_job_id = j.id
                      AND j.user_id IS NOT NULL
                    """
                )
            )

            # Normalize legacy lowercase enum-like values to canonical uppercase
            try:
                await db.execute(text("UPDATE jobs SET source = UPPER(source::text)::jobsource WHERE source IS NOT NULL AND source::text <> UPPER(source::text)"))
                await db.execute(text("UPDATE jobs SET experience_level = LOWER(experience_level::text)::experiencelevel WHERE experience_level IS NOT NULL AND experience_level::text <> LOWER(experience_level::text)"))
                await db.execute(text("UPDATE user_profiles SET experience_level = LOWER(experience_level::text)::experiencelevel WHERE experience_level IS NOT NULL AND experience_level::text <> LOWER(experience_level::text)"))
                logger.info("Normalized legacy enum-like string values")
            except Exception as exc:
                logger.warning("Failed to normalize legacy enum strings", error=str(exc))

        logger.info("PostgreSQL schema reconciliation verified")
    except Exception as exc:
        logger.warning("PostgreSQL schema reconciliation skipped", error=str(exc))


# ── Lifespan (startup + shutdown) ────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(f"Starting {settings.APP_NAME}", env=settings.APP_ENV)

    if settings.APP_ENV == "production":
        if "changeme" in settings.SECRET_KEY:
            raise RuntimeError("FATAL: Default SECRET_KEY in production.")
        if "changeme" in settings.JWT_SECRET_KEY:
            raise RuntimeError("FATAL: Default JWT_SECRET_KEY in production.")
        if not settings.ENCRYPTION_KEY:
            raise RuntimeError("FATAL: ENCRYPTION_KEY not set.")
        if not settings.REDIS_PASSWORD:
            raise RuntimeError("FATAL: REDIS_PASSWORD not set.")

    from app.core.startup_checks import check_hashing
    check_hashing()

    await init_db()
    logger.info("Database tables initialized")

    await _run_sqlite_migrations()
    logger.info("SQLite schema migrations verified")

    await _run_postgres_schema_reconciliation()

    # Reset stuck states
    from app.models.application import Application, ApplicationStatus
    from app.models.interview import AgentTask, AgentTaskStatus
    from sqlalchemy import update as sql_update
    async with get_db_context() as db:
        await db.execute(
            sql_update(Application)
            .where(Application.status == ApplicationStatus.APPLYING)
            .values(status=ApplicationStatus.QUEUED, bot_error="Reset: server restarted")
        )
        await db.execute(
            sql_update(AgentTask)
            .where(AgentTask.status == AgentTaskStatus.RUNNING)
            .values(status=AgentTaskStatus.FAILED, error="Reset: server restarted")
        )
    logger.info("Stuck state reset complete")

    if not await check_db_connection():
        logger.error("Database connection failed")
        raise RuntimeError("Database unavailable")
    
    logger.info("Database connected")
    _ = settings.resumes_path
    _ = settings.cover_letters_path
    _ = settings.recordings_path
    logger.info("Storage directories ready")

    if settings.APP_ENV == "development":
        from app.services.scheduler_service import SchedulerService, setup_default_jobs
        scheduler = SchedulerService()
        scheduler.start()
        setup_default_jobs()
        logger.info("Scheduler started (dev mode)")
    else:
        logger.info("Scheduler disabled - using Celery Beat in production")

    if settings.AUTO_APPLY_ENABLED:
        logger.info("Auto-apply is enabled")

    yield

    if settings.APP_ENV == "development":
        from app.services.scheduler_service import SchedulerService
        scheduler = SchedulerService()
        scheduler.shutdown()
        logger.info("Scheduler stopped")

    await close_db()
    logger.info("Database connections closed")


# ── App Initialization ────────────────────────────────────────────────────────

app = FastAPI(
    title=settings.APP_NAME,
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
)

@app.get("/health")
async def health():
    """Production health check endpoint."""
    return {
        "status": "ok",
        "app": settings.APP_NAME,
        "env": settings.APP_ENV
    }

# ── CORS Middleware ───────────────────────────────────────

allowed_origins = list(settings.ALLOWED_ORIGINS)
if settings.APP_ENV == "development":
    allowed_origins = list(set(allowed_origins + [
        "http://localhost:3000", "http://localhost:3001", "http://localhost:5173",
        "http://127.0.0.1:3000", "http://127.0.0.1:3001", "http://127.0.0.1:5173"
    ]))

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Global exception handler ──────────────────────────────

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    import traceback
    tb = traceback.format_exc()
    try:
        err_text = str(exc)
    except Exception:
        err_text = repr(exc)
    if settings.APP_ENV == "production":
        logger.error("Unhandled exception", path=request.url.path, error=err_text)
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal server error", "error_id": id(exc) % 10000}
        )
    return JSONResponse(
        status_code=500,
        content={"detail": err_text, "traceback": tb}
    )

# ── Rate limiting middleware ───────────────────────────────

@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    from app.services.rate_limiter import rate_limiter
    
    skip_paths = ["/health", "/dashboard", "/", "/api/docs", "/api/redoc", "/api/openapi.json"]
    if request.url.path in skip_paths:
        return await call_next(request)

    client_ip = request.client.host if request.client else "unknown"

    if request.url.path in ["/api/auth/login", "/api/auth/register", "/api/auth/login/initiate", "/api/auth/register/initiate"]:
        auth_key = f"auth_rate:{client_ip}"
        auth_max_requests = settings.AUTH_RATE_LIMIT_REQUESTS
        auth_window_seconds = settings.AUTH_RATE_LIMIT_WINDOW_SECONDS
        # Relaxed limits for all clients when APP_ENV=development (Docker uses 192.168.x IPs).
        if settings.APP_ENV == "development":
            auth_max_requests = settings.AUTH_RATE_LIMIT_DEV_REQUESTS
            auth_window_seconds = settings.AUTH_RATE_LIMIT_DEV_WINDOW_SECONDS

        result = await rate_limiter.is_allowed(
            key=auth_key,
            max_requests=auth_max_requests,
            window_seconds=auth_window_seconds,
        )
        if not result["allowed"]:
            limit_minutes = max(1, auth_window_seconds // 60)
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={"detail": f"Too many attempts. Try again in {limit_minutes} minutes.", "retry_after": result["retry_after"]},
                headers={"Retry-After": str(result["retry_after"])},
            )
    else:
        key = f"rate:{client_ip}"
        result = await rate_limiter.is_allowed(
            key=key,
            max_requests=settings.RATE_LIMIT_REQUESTS,
            window_seconds=settings.RATE_LIMIT_WINDOW_SECONDS,
        )
        if not result["allowed"]:
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={"detail": "Rate limit exceeded", "retry_after": result["retry_after"]},
                headers={"Retry-After": str(result["retry_after"])},
            )

    response = await call_next(request)
    response.headers["X-RateLimit-Remaining"] = str(result["remaining"])
    response.headers["X-RateLimit-Limit"] = str(result["limit"])
    return response

# ── Router Registration ───────────────────────────────────

API_PREFIX = "/api"

# Auth & core
app.include_router(auth_router, prefix=API_PREFIX)
app.include_router(onboarding_router, prefix=API_PREFIX)
app.include_router(scheduler_router, prefix=API_PREFIX)
app.include_router(jobs_router, prefix=API_PREFIX)
app.include_router(profile_router, prefix=API_PREFIX)
app.include_router(security_router, prefix=API_PREFIX)
app.include_router(applications_router, prefix=API_PREFIX)
app.include_router(resumes_router, prefix=API_PREFIX)
app.include_router(cover_letters_router, prefix=API_PREFIX)
app.include_router(agent_router, prefix=API_PREFIX)
app.include_router(workflow_router, prefix=API_PREFIX)
app.include_router(analytics_router, prefix=API_PREFIX)
app.include_router(settings_router, prefix=API_PREFIX)
app.include_router(settings_v2_router, prefix=API_PREFIX)
app.include_router(chat_router, prefix=API_PREFIX)

# SaaS billing & subscription
app.include_router(subscriptions_router, prefix=API_PREFIX)
app.include_router(payments_router, prefix=API_PREFIX)
app.include_router(platform_router, prefix=API_PREFIX)
app.include_router(quotas_router, prefix=API_PREFIX)
app.include_router(admin_router, prefix=API_PREFIX)
app.include_router(outreach_router, prefix=API_PREFIX)

# ── Health checks ─────────────────────────────────────────

@app.get("/health", tags=["System"])
async def health():
    db_ok = await check_db_connection()
    return {
        "status": "healthy" if db_ok else "degraded",
        "database": "connected" if db_ok else "disconnected",
    }

@app.get("/", tags=["System"])
async def root():
    return {
        "app": settings.APP_NAME,
        "docs": "/api/docs",
        "health": "/health",
    }
