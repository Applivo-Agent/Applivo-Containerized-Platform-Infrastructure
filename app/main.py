"""
app/main.py
───────────
FastAPI application factory for the Applivo SaaS platform.
Registers all routers, middleware, startup/shutdown events.
All automation runs server-side — no desktop dependencies.
"""

from __future__ import annotations

from contextlib import asynccontextmanager
from pathlib import Path

import structlog
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse

from app.core.config import settings
from app.core.database import check_db_connection, close_db, init_db

logger = structlog.get_logger()


# ── Lifespan (startup + shutdown) ────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(f"Starting {settings.APP_NAME}", env=settings.APP_ENV)

    await init_db()
    logger.info("Database tables initialized")

    if not await check_db_connection():
        logger.error("Database connection failed — check DATABASE_URL in .env")
        raise RuntimeError("Database unavailable")
    logger.info("Database connected")

    _ = settings.resumes_path
    _ = settings.cover_letters_path
    _ = settings.recordings_path
    logger.info("Storage directories ready")

    # Start the scheduler for auto-scrape and auto-apply
    from app.services.scheduler_service import SchedulerService, setup_default_jobs
    scheduler = SchedulerService()
    scheduler.start()
    setup_default_jobs()
    logger.info("Scheduler started with default jobs")

    # Enable auto-apply if configured
    if settings.AUTO_APPLY_ENABLED:
        logger.info("Auto-apply is enabled")

    yield

    # Shutdown scheduler
    from app.services.scheduler_service import SchedulerService
    scheduler = SchedulerService()
    scheduler.shutdown()
    logger.info("Scheduler stopped")

    await close_db()
    logger.info("Database connections closed")


# ── App factory ───────────────────────────────────────────────────────────────

def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.APP_NAME,
        description="Applivo — Multi-user AI Career Automation SaaS Platform",
        version="2.0.0",
        docs_url="/api/docs",
        redoc_url="/api/redoc",
        openapi_url="/api/openapi.json",
        lifespan=lifespan,
    )

    # ── CORS ──────────────────────────────────────────────────
    allowed_origins = (
        ["*"] if settings.APP_ENV == "development"
        else ["http://localhost:3000", "http://127.0.0.1:3000", "http://192.0.0.2:3000"]
    )
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
        logger.error("Unhandled exception", path=request.url.path, error=str(exc), traceback=tb)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "detail": str(exc),
                "error": tb,
            },
        )

    # ── Rate limiting middleware ───────────────────────────────
    @app.middleware("http")
    async def rate_limit_middleware(request: Request, call_next):
        from app.services.rate_limiter import rate_limiter
        from app.api.routes.auth import get_current_user

        # Skip rate limiting for health check and static assets
        skip_paths = ["/health", "/dashboard", "/", "/api/docs", "/api/redoc", "/api/openapi.json"]
        if request.url.path in skip_paths:
            return await call_next(request)

        # Rate limit by IP for unauthenticated, by user_id for authenticated
        client_ip = request.client.host if request.client else "unknown"
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

    # ── Routers ───────────────────────────────────────────────
    from app.api.routes.auth import router as auth_router
    from app.api.routes.jobs import router as jobs_router
    from app.api.routes.profile import router as profile_router
    from app.api.routes.security import router as security_router
    from app.api.routes.onboarding import router as onboarding_router
    from app.api.routes.scheduler import router as scheduler_router
    from app.api.routes.settings_route import settings_router
    from app.api.routes.subscriptions import router as subscriptions_router
    from app.api.routes.payments import router as payments_router
    from app.api.routes.platform import router as platform_router
    from app.api.routes.quotas import router as quotas_router
    from app.api.routes.admin import admin_router
    from app.api.routes.routes import (
        applications_router,
        resumes_router,
        cover_letters_router,
        agent_router,
        analytics_router,
        chat_router,
    )

    API_PREFIX = "/api"

    # Auth & core
    app.include_router(auth_router, prefix=API_PREFIX)
    app.include_router(onboarding_router, prefix=API_PREFIX)
    app.include_router(scheduler_router, prefix=API_PREFIX)  # /api/scheduler
    app.include_router(jobs_router, prefix=API_PREFIX)
    app.include_router(profile_router, prefix=API_PREFIX)
    app.include_router(security_router, prefix=API_PREFIX)
    app.include_router(applications_router, prefix=API_PREFIX)
    app.include_router(resumes_router, prefix=API_PREFIX)
    app.include_router(cover_letters_router, prefix=API_PREFIX)
    app.include_router(agent_router, prefix=API_PREFIX)
    app.include_router(analytics_router, prefix=API_PREFIX)
    app.include_router(settings_router, prefix=API_PREFIX)
    app.include_router(chat_router, prefix=API_PREFIX)

    # SaaS billing & subscription
    app.include_router(subscriptions_router, prefix=API_PREFIX)
    app.include_router(payments_router, prefix=API_PREFIX)
    app.include_router(platform_router, prefix=API_PREFIX)
    app.include_router(quotas_router, prefix=API_PREFIX)
    app.include_router(admin_router, prefix=API_PREFIX)

    # ── Health check ──────────────────────────────────────────
    @app.get("/health", tags=["System"])
    async def health():
        db_ok = await check_db_connection()
        return {
            "status": "healthy" if db_ok else "degraded",
            "database": "connected" if db_ok else "disconnected",
            "app": settings.APP_NAME,
            "version": "2.0.0",
            "env": settings.APP_ENV,
            "mode": "saas",
        }

    @app.get("/", tags=["System"])
    async def root():
        return {
            "app": settings.APP_NAME,
            "version": "2.0.0",
            "mode": "saas",
            "docs": "/api/docs",
            "health": "/health",
        }

    return app


app = create_app()
