"""
app/celery_tasks.py
────────────────────
Celery task definitions for all background automation.
Each task is idempotent and handles errors gracefully.
"""

from __future__ import annotations

import asyncio
from datetime import datetime, timezone

import structlog

from app.celery_app import celery_app

logger = structlog.get_logger()


def _run_async(coro):
    """Run an async coroutine from a Celery worker."""
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


@celery_app.task(bind=True, max_retries=3, default_retry_delay=300)
def scrape_jobs(self):
    """Scrape jobs from all configured platforms for all active users."""
    try:
        from app.agents.tasks import run_main_agent_cycle
        _run_async(run_main_agent_cycle())
        logger.info("Job scraping completed")
    except Exception as e:
        logger.error("Job scraping failed", error=str(e))
        raise self.retry(exc=e)


@celery_app.task(bind=True, max_retries=2)
def analyze_jobs(self):
    """Run AI analysis on scraped jobs."""
    try:
        from app.agents.tasks import analyze_new_jobs
        _run_async(analyze_new_jobs())
        logger.info("Job analysis completed")
    except Exception as e:
        logger.error("Job analysis failed", error=str(e))
        raise self.retry(exc=e)


@celery_app.task(bind=True, max_retries=3)
def auto_apply(self):
    """Queue and submit applications for all eligible users."""
    try:
        from app.services.application_service import ApplicationService
        result = _run_async(ApplicationService().queue_batch_applications())
        logger.info("Auto-apply completed", result=result)
    except Exception as e:
        logger.error("Auto-apply failed", error=str(e))
        raise self.retry(exc=e)


@celery_app.task(bind=True, max_retries=3)
def apply_to_job(self, application_id: str):
    """Apply to a single job using the bot."""
    try:
        from app.agents.apply_bot import ApplyBot
        bot = ApplyBot()
        result = _run_async(bot.apply(application_id))
        logger.info("Apply to job completed", application_id=application_id, result=result)
    except Exception as e:
        logger.error("Apply to job failed", application_id=application_id, error=str(e))
        raise self.retry(exc=e)


@celery_app.task(bind=True, max_retries=2)
def send_notification(self, notification_id: str):
    """Send a specific notification."""
    try:
        from app.services.notification_service import NotificationService
        service = NotificationService()
        _run_async(service.send_telegram(notification_id))
        _run_async(service.send_email(notification_id))
    except Exception as e:
        logger.error("Notification send failed", notification_id=notification_id, error=str(e))
        raise self.retry(exc=e)


@celery_app.task(bind=True, max_retries=2)
def check_emails(self):
    """Check email inbox for recruiter messages."""
    try:
        from app.agents.tasks import check_email_inbox
        _run_async(check_email_inbox())
        logger.info("Email check completed")
    except Exception as e:
        logger.error("Email check failed", error=str(e))
        raise self.retry(exc=e)


@celery_app.task
def send_daily_digest():
    """Send daily summary notification to all active users."""
    try:
        from app.services.notification_service import NotificationService
        _run_async(NotificationService().send_daily_digest())
        logger.info("Daily digest sent")
    except Exception as e:
        logger.error("Daily digest failed", error=str(e))


@celery_app.task
def check_expired_subscriptions():
    """Deactivate expired subscriptions."""
    try:
        from app.core.database import get_db_context
        from app.models.subscription import Subscription, SubscriptionStatus
        from sqlalchemy import select
        from datetime import datetime, timezone

        async def _check():
            async with get_db_context() as db:
                result = await db.execute(
                    select(Subscription).where(
                        Subscription.status == SubscriptionStatus.ACTIVE,
                        Subscription.end_date < datetime.now(timezone.utc),
                    )
                )
                expired = result.scalars().all()
                for sub in expired:
                    sub.status = SubscriptionStatus.EXPIRED
                    logger.info("Subscription expired", user_id=sub.user_id, sub_id=sub.id)
                await db.commit()
                return len(expired)

        count = _run_async(_check())
        logger.info("Expired subscriptions checked", expired_count=count)
    except Exception as e:
        logger.error("Subscription check failed", error=str(e))


@celery_app.task
def check_expired_cookies():
    """Detect and mark expired platform cookies."""
    try:
        from app.core.database import get_db_context
        from app.models.cookie import PlatformCookie
        from sqlalchemy import select
        from datetime import datetime, timezone

        async def _check():
            async with get_db_context() as db:
                result = await db.execute(
                    select(PlatformCookie).where(
                        PlatformCookie.is_valid == True,
                        PlatformCookie.expires_at < datetime.now(timezone.utc),
                    )
                )
                expired = result.scalars().all()
                for cookie in expired:
                    cookie.is_valid = False
                    logger.info("Cookie expired", user_id=cookie.user_id, platform=cookie.platform)
                await db.commit()
                return len(expired)

        count = _run_async(_check())
        logger.info("Expired cookies checked", expired_count=count)
    except Exception as e:
        logger.error("Cookie check failed", error=str(e))


# ── Priority queue tasks (for Pro/Premium users) ────────────────────────────

@celery_app.task(bind=True, max_retries=3)
def priority_scrape(self, user_id: str):
    """Priority scrape for Pro/Premium users."""
    try:
        from app.agents.tasks import run_main_agent_cycle
        _run_async(run_main_agent_cycle())
        logger.info("Priority scrape completed", user_id=user_id)
    except Exception as e:
        logger.error("Priority scrape failed", user_id=user_id, error=str(e))
        raise self.retry(exc=e)


@celery_app.task(bind=True, max_retries=3)
def priority_apply(self, application_id: str):
    """Priority apply for Pro/Premium users."""
    try:
        from app.agents.apply_bot import auto_apply_single
        _run_async(auto_apply_single(application_id))
        logger.info("Priority apply completed", application_id=application_id)
    except Exception as e:
        logger.error("Priority apply failed", application_id=application_id, error=str(e))
        raise self.retry(exc=e)
