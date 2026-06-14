"""
app/services/scheduler_service.py
────────────────────────────────
APScheduler-based scheduler for desktop applications.
Replaces Celery - no separate worker process needed.
"""

from __future__ import annotations

import asyncio
from datetime import datetime, timezone
from typing import Any, Callable, Optional
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.date import DateTrigger
from apscheduler.jobstores.memory import MemoryJobStore
try:
    from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
    _HAS_SQLA_JOBSTORE = True
except ImportError:
    _HAS_SQLA_JOBSTORE = False

from app.core.config import settings
import structlog

logger = structlog.get_logger()


class SchedulerService:
    """
    Desktop-friendly scheduler using APScheduler.
    Runs in same process as FastAPI - no Redis or separate worker needed.
    """
    
    _instance: Optional[SchedulerService] = None
    _scheduler: Optional[AsyncIOScheduler] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._scheduler is None:
            self._setup_scheduler()
    
    def _setup_scheduler(self):
        """
        FIX 7: Initialize scheduler with SQLite-backed persistent job store.
        Jobs survive process restarts — no longer lost on shutdown.
        Falls back to MemoryJobStore if the SQLAlchemy jobstore is unavailable.
        """
        if _HAS_SQLA_JOBSTORE:
            db_url = settings.DATABASE_URL_SYNC  # e.g. sqlite:///./applivo.db
            jobstores = {
                "default": SQLAlchemyJobStore(url=db_url, tablename="apscheduler_jobs")
            }
            logger.info("APScheduler using SQLite persistent job store")
        else:
            jobstores = {"default": MemoryJobStore()}
            logger.warning("APScheduler using in-memory job store (jobs lost on restart)")

        job_defaults = {
            "coalesce": True,           # Combine missed runs into one
            "max_instances": 1,         # Only one instance at a time
            "misfire_grace_time": 300,  # 5 minutes grace period
        }

        # BackgroundScheduler runs in a daemon thread — doesn't block FastAPI
        self._scheduler = BackgroundScheduler(
            jobstores=jobstores,
            job_defaults=job_defaults,
            timezone="UTC",
        )

        logger.info("APScheduler initialized", persistent=_HAS_SQLA_JOBSTORE)
    
    @property
    def scheduler(self) -> BackgroundScheduler:
        """Get the scheduler instance."""
        if self._scheduler is None:
            self._setup_scheduler()
        return self._scheduler
    
    def ensure_started(self):
        """Ensure scheduler is running (called from main.py)."""
        if not self._scheduler.running:
            self.start()
    
    def start(self):
        """Start the scheduler."""
        if not self.scheduler.running:
            self.scheduler.start()
            logger.info("Scheduler started")
    
    def shutdown(self):
        """Stop the scheduler."""
        if self.scheduler.running:
            self.scheduler.shutdown()
            logger.info("Scheduler stopped")
    
    def add_job(
        self,
        func: Callable,
        trigger: str = "interval",
        minutes: int = 60,
        job_id: Optional[str] = None,
        **kwargs
    ) -> str:
        """
        Add a job to the scheduler.
        
        Args:
            func: The function to run
            trigger: 'interval', 'cron', or 'date'
            minutes: Interval in minutes (for interval trigger)
            job_id: Optional unique job ID
            **kwargs: Additional arguments for the function
            
        Returns:
            Job ID
        """
        job_id = job_id or f"job_{func.__name__}_{datetime.now().timestamp()}"
        
        if trigger == "interval":
            job = self.scheduler.add_job(
                func,
                trigger=IntervalTrigger(minutes=minutes),
                id=job_id,
                replace_existing=True,
                **kwargs
            )
        elif trigger == "cron":
            # Example: "0 * * * *" = every hour
            job = self.scheduler.add_job(
                func,
                trigger=CronTrigger.from_crontab(trigger),
                id=job_id,
                replace_existing=True,
                **kwargs
            )
        elif trigger == "date":
            job = self.scheduler.add_job(
                func,
                trigger=DateTrigger(run_date=kwargs.get('run_date')),
                id=job_id,
                replace_existing=True,
                **kwargs
            )
        else:
            raise ValueError(f"Unknown trigger: {trigger}")
        
        logger.info(f"Job scheduled: {job_id}", trigger=trigger, minutes=minutes)
        return job_id
    
    def remove_job(self, job_id: str):
        """Remove a job by ID."""
        try:
            self.scheduler.remove_job(job_id)
            logger.info(f"Job removed: {job_id}")
        except Exception as e:
            logger.warning(f"Job not found: {job_id}", error=str(e))
    
    def list_jobs(self) -> list[dict]:
        """List all scheduled jobs."""
        jobs = self.scheduler.get_jobs()
        return [
            {
                "id": job.id,
                "name": job.name,
                "next_run": job.next_run_time.isoformat() if job.next_run_time else None,
                "trigger": str(job.trigger),
            }
            for job in jobs
        ]
    
    def pause_job(self, job_id: str):
        """Pause a job."""
        self.scheduler.pause_job(job_id)
        logger.info(f"Job paused: {job_id}")
    
    def resume_job(self, job_id: str):
        """Resume a paused job."""
        self.scheduler.resume_job(job_id)
        logger.info(f"Job resumed: {job_id}")
    
    def run_job_now(self, job_id: str):
        """Trigger a job to run immediately."""
        job = self.scheduler.get_job(job_id)
        if job:
            job.modify(next_run_time=datetime.now(timezone.utc))
            logger.info(f"Job triggered: {job_id}")
        else:
            logger.warning(f"Job not found: {job_id}")


# ── Predefined Jobs for Applivo ────────────────────────────────────────────

def setup_default_jobs():
    """Set up default scheduled jobs for the platform."""
    scheduler = SchedulerService()
    
    # Job scraping - every 6 hours
    scheduler.add_job(
        run_scrape_job,
        trigger="interval",
        minutes=settings.SCRAPE_INTERVAL_HOURS * 60,
        job_id="auto_scrape",
    )
    
    # Auto-apply check - every hour
    scheduler.add_job(
        run_auto_apply,
        trigger="interval",
        minutes=60,
        job_id="auto_apply_check",
    )
    
    # Email monitoring - every 30 minutes
    scheduler.add_job(
        check_emails,
        trigger="interval",
        minutes=30,
        job_id="email_monitor",
    )
    
    # Platform messages scan - every 5 minutes
    scheduler.add_job(
        scan_platform_messages_job,
        trigger="interval",
        minutes=5,
        job_id="platform_messages_scan",
    )
    
    logger.info("Default jobs configured")


_SCHEDULER_LOOP: asyncio.AbstractEventLoop | None = None


def _get_scheduler_loop() -> asyncio.AbstractEventLoop:
    """Return a stable event loop for APScheduler background thread.

    Reusing one loop avoids cross-loop asyncpg futures when SQLAlchemy keeps
    pooled connections across scheduled job executions.
    """
    global _SCHEDULER_LOOP

    if _SCHEDULER_LOOP is None or _SCHEDULER_LOOP.is_closed():
        _SCHEDULER_LOOP = asyncio.new_event_loop()

    return _SCHEDULER_LOOP


def scan_platform_messages_job():
    """Scan all user platform messages.

    DEV NOTE: This job uses asyncio in a BackgroundScheduler thread, which
    conflicts with the shared asyncpg engine pool. In production this should
    run via Celery; in dev we skip it to avoid cross-loop errors.
    """
    from app.core.config import settings

    # Skip in development — no real platform messages to scan and the shared
    # asyncpg engine causes cross-loop RuntimeErrors from BackgroundScheduler.
    if settings.APP_ENV in ("development", "testing"):
        logger.debug("Platform messages scan skipped in dev/test mode")
        return

    from app.services.message_scanner_service import message_scanner_service
    from app.models.user import User
    from sqlalchemy import select
    from app.core.database import get_db_context

    async def _scan():
        async with get_db_context() as db:
            result = await db.execute(
                select(User.id).where(User.is_active == True)
            )
            user_ids = [r[0] for r in result.fetchall()]

        for user_id in user_ids:
            try:
                await message_scanner_service.scan_user_messages(user_id, "internshala")
            except Exception as e:
                logger.error("Failed to scan messages for user", user_id=user_id, error=str(e))

    try:
        loop = _get_scheduler_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(_scan())
        logger.info("Platform messages scan completed")
    except RuntimeError as e:
        # Known issue: asyncpg connections from the shared pool are bound to
        # the main event loop and cannot be closed from the scheduler thread.
        logger.warning("Messages scan skipped due to cross-loop engine conflict", error=str(e)[:100])
    except Exception as e:
        logger.error("Failed to run messages scan", error=str(e))


def _run_async(coro):
    """Run an async coroutine from a sync BackgroundScheduler thread."""
    loop = _get_scheduler_loop()
    asyncio.set_event_loop(loop)
    return loop.run_until_complete(coro)


def run_scrape_job():
    """Sync wrapper: run internshala scrape + analysis pipeline."""
    try:
        from app.agents.tasks import run_main_agent_cycle
        run_main_agent_cycle()
    except Exception as e:
        logger.error("Scrape job failed", error=str(e))


def run_auto_apply():
    """Sync wrapper: queue and submit pending applications."""
    try:
        if settings.AUTO_APPLY_ENABLED:
            from app.agents.tasks import queue_auto_applications_task
            queue_auto_applications_task()
    except Exception as e:
        logger.error("Auto-apply job failed", error=str(e))


def check_emails():
    """Sync wrapper: check email inbox for recruiter messages."""
    try:
        from app.agents.tasks import check_email_inbox
        check_email_inbox()
    except Exception as e:
        logger.error("Email check failed", error=str(e))


# ── Decorator for Scheduled Tasks ──────────────────────────────────────────

def scheduled_job(trigger: str = "interval", minutes: int = 60):
    """
    Decorator to mark a function as a scheduled job.
    
    Usage:
        @scheduled_job(trigger="interval", minutes=60)
        async def my_task():
            ...
    """
    def decorator(func: Callable):
        job_id = f"scheduled_{func.__name__}"
        
        # Register with scheduler when app starts
        def on_startup():
            scheduler = SchedulerService()
            scheduler.add_job(func, trigger=trigger, minutes=minutes, job_id=job_id)
        
        # Store for later registration
        if not hasattr(func, '_scheduled_jobs'):
            func._scheduled_jobs = []
        func._scheduled_jobs.append({
            'trigger': trigger,
            'minutes': minutes,
            'job_id': job_id,
        })
        
        return func
    return decorator    