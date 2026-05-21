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

_CELERY_LOOP: asyncio.AbstractEventLoop | None = None


def _get_worker_loop() -> asyncio.AbstractEventLoop:
    """Return a stable event loop for this Celery worker process.

    Reusing one loop avoids cross-loop asyncpg futures when SQLAlchemy keeps
    pooled connections across task executions.
    """
    global _CELERY_LOOP

    if _CELERY_LOOP is None or _CELERY_LOOP.is_closed():
        _CELERY_LOOP = asyncio.new_event_loop()

    return _CELERY_LOOP


def _run_async(coro):
    """Run an async coroutine on a persistent Celery worker event loop."""
    loop = _get_worker_loop()
    asyncio.set_event_loop(loop)
    return loop.run_until_complete(coro)


@celery_app.task(bind=True, max_retries=3, default_retry_delay=300)
def scrape_jobs(self):
    """Scrape jobs from all configured platforms for all active users."""
    try:
        from app.agents.tasks import run_main_agent_cycle
        run_main_agent_cycle()
        logger.info("Job scraping completed")
    except Exception as e:
        logger.error("Job scraping failed", error=str(e))
        raise self.retry(exc=e)


@celery_app.task(bind=True, max_retries=2)
def analyze_jobs(self):
    """Run AI analysis on scraped jobs."""
    try:
        from app.agents.tasks import analyze_new_jobs_batch_task
        analyze_new_jobs_batch_task()
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
def apply_queued_batch(self, user_id: str):
    """Apply to queued applications for a single user on the browser worker."""
    try:
        from sqlalchemy import select

        from app.core.config import settings
        from app.core.database import get_db_context
        from app.models.application import Application, ApplicationStatus
        from app.models.job import JobAnalysis
        from app.agents.apply_bot import ApplyBot
        from app.services.cookie_service import cookie_service

        threshold = settings.AUTO_APPLY_MATCH_THRESHOLD

        async def _run():
            async with get_db_context() as db:
                apps_to_run = (await db.execute(
                    select(Application).where(
                        Application.user_id == user_id,
                        Application.status == ApplicationStatus.QUEUED
                    ).outerjoin(
                        JobAnalysis, Application.job_id == JobAnalysis.job_id
                    ).where(
                        (JobAnalysis.match_score >= threshold) | (JobAnalysis.match_score == None)
                    ).limit(15)
                )).scalars().all()

                app_ids = [a.id for a in apps_to_run]

                if not app_ids:
                    return {"applied": 0, "skipped": 0, "failed": 0, "message": "No jobs in queue"}

                bot = ApplyBot()
                applied_count = 0
                skipped_count = 0
                failed_count = 0
                results = []

                for app_id in app_ids:
                    try:
                        r = await bot.apply(app_id)
                        results.append({"id": app_id, **r})

                        error_text = (r.get("error") or "").lower()
                        session_expired = "session expired" in error_text or "run save_cookies.py" in error_text or "not logged in" in error_text
                        login_modal_block = bool(r.get("bot_detected")) or "login modal" in error_text or "anti-bot detection" in error_text

                        if session_expired or login_modal_block:
                            await cookie_service.invalidate_cookies(user_id, "internshala")
                            failed_count += 1
                            logger.warning(
                                "Session blocked during apply batch",
                                app_id=app_id,
                                user_id=user_id,
                                reason="login_modal" if login_modal_block else "session_expired",
                            )
                            # Notify user immediately so they can re-upload cookies
                            try:
                                from app.services.notification_service import NotificationService
                                await NotificationService().notify(
                                    title="⚠️ Internshala Session Blocked — Action Required",
                                    body="""Internshala blocked the current session (expired or login wall detected), and the bot has stopped this apply batch.

To resume automation, please re-upload your cookies:
1. Log in to Internshala in your browser
2. Go to your Applivo dashboard → Settings → Connect Accounts
3. Follow the cookie upload guide

Applications are paused until this is fixed.

— Applivo AI""",
                                    event_type="cookie_expired",
                                    data={"platform": "internshala"},
                                    user_id=user_id,
                                )
                            except Exception as notif_err:
                                logger.error("Failed to send cookie expiry notification", user_id=user_id, error=str(notif_err))
                            break

                        if r.get("success"):
                            if r.get("already_applied"):
                                app = await db.get(Application, app_id)
                                if app:
                                    app.status = ApplicationStatus.APPLIED
                                    app.applied_at = datetime.now(timezone.utc)
                                    db.add(app)
                                    await db.commit()
                                logger.info("Already applied - synced", app_id=app_id)
                            else:
                                app = await db.get(Application, app_id)
                                if app:
                                    app.status = ApplicationStatus.APPLIED
                                    app.applied_at = datetime.now(timezone.utc)
                                    db.add(app)
                                    await db.commit()
                                applied_count += 1
                                logger.info("Applied successfully - marked as APPLIED", app_id=app_id)
                        elif r.get("ineligible"):
                            skipped_count += 1
                            app = await db.get(Application, app_id)
                            if app:
                                app.status = ApplicationStatus.SKIPPED
                                app.bot_error = r.get("error", "Not eligible")
                                db.add(app)
                                await db.commit()
                            logger.warning("Job not eligible - marked as SKIPPED", app_id=app_id)
                        elif r.get("error") and "external" in error_text:
                            failed_count += 1
                            app = await db.get(Application, app_id)
                            if app:
                                app.status = ApplicationStatus.FAILED
                                app.bot_error = r.get("error", "External posting")
                                app.retry_count = 999
                                db.add(app)
                                await db.commit()
                            logger.warning("External job - marked as FAILED", app_id=app_id)
                        else:
                            failed_count += 1
                            # Persist failure to DB so it doesn't keep getting retried
                            app = await db.get(Application, app_id)
                            if app:
                                app.status = ApplicationStatus.FAILED
                                app.bot_error = r.get("error", "Application submission failed")
                                app.retry_count = (app.retry_count or 0) + 1
                                db.add(app)
                                await db.commit()
                            logger.warning("Apply failed - marked as FAILED", app_id=app_id, error=r.get("error"), retry_count=app.retry_count if app else 0)
                    except Exception as exc:
                        failed_count += 1
                        # Persist exception to DB
                        app = await db.get(Application, app_id)
                        if app:
                            app.status = ApplicationStatus.FAILED
                            app.bot_error = f"Exception: {str(exc)[:500]}"
                            app.retry_count = (app.retry_count or 0) + 1
                            db.add(app)
                            await db.commit()
                        logger.error("Apply exception - marked as FAILED", app_id=app_id, error=str(exc), retry_count=app.retry_count if app else 0)

                return {
                    "applied": applied_count,
                    "failed": failed_count,
                    "skipped": skipped_count,
                    "total_queued": len(app_ids),
                    "results": results,
                }

        result = _run_async(_run())
        logger.info("Apply queued batch completed", user_id=user_id, result=result)
        return result
    except Exception as e:
        logger.error("Apply queued batch failed", user_id=user_id, error=str(e))
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
        check_email_inbox()
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
        from sqlalchemy import select, String, func
        from datetime import datetime, timezone

        async def _check():
            async with get_db_context() as db:
                result = await db.execute(
                    select(Subscription).where(
                        func.lower(Subscription.status.cast(String)) == SubscriptionStatus.ACTIVE.value,
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
    """Detect and mark expired platform cookies, notify affected users."""
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

                # Notify each affected user
                if expired:
                    from app.services.notification_service import NotificationService
                    ns = NotificationService()
                    for cookie in expired:
                        try:
                            await ns.notify(
                                title="⚠️ Internshala Session Expired — Action Required",
                                body=f"""Your {cookie.platform.title()} session has expired and the bot has paused applications.

To resume automation, please re-upload your cookies:
1. Log in to {cookie.platform.title()} in your browser
2. Go to your Applivo dashboard → Settings → Connect Accounts
3. Follow the cookie upload guide

Applications are paused until this is fixed.

— Applivo AI""",
                                event_type="cookie_expired",
                                data={"platform": cookie.platform},
                                user_id=cookie.user_id,
                            )
                        except Exception as ne:
                            logger.error("Failed to notify user of cookie expiry", user_id=cookie.user_id, error=str(ne))

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
        run_main_agent_cycle()
        logger.info("Priority scrape completed", user_id=user_id)
    except Exception as e:
        logger.error("Priority scrape failed", user_id=user_id, error=str(e))
        raise self.retry(exc=e)


@celery_app.task(bind=True, max_retries=3)
def priority_apply(self, application_id: str):
    """Priority apply for Pro/Premium users."""
    try:
        from app.agents.apply_bot import ApplyBot
        bot = ApplyBot()
        _run_async(bot.apply(application_id))
        logger.info("Priority apply completed", application_id=application_id)
    except Exception as e:
        logger.error("Priority apply failed", application_id=application_id, error=str(e))
        raise self.retry(exc=e)


@celery_app.task(bind=True, max_retries=2)
def scan_platform_messages(self, user_id: str, platform: str = "internshala"):
    """Scan platform inbox for new messages."""
    try:
        from app.services.message_scanner_service import message_scanner_service
        result = _run_async(message_scanner_service.scan_user_messages(user_id, platform))
        logger.info("Message scan completed", user_id=user_id, platform=platform, 
                    new_messages=result.get("new_messages", 0),
                    important=result.get("important_messages", 0))
        return result
    except Exception as e:
        logger.error("Message scan failed", user_id=user_id, platform=platform, error=str(e))
        raise self.retry(exc=e)


@celery_app.task(bind=True, max_retries=1)
def scan_all_user_messages(self):
    """Scan messages for all users with platform connections."""
    try:
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
                    await scan_platform_messages.apply_async(args=[user_id, "internshala"])
                except Exception as e:
                    logger.error("Failed to queue scan for user", user_id=user_id, error=str(e))
        
        _run_async(_scan())
        logger.info("All users message scan queued")
    except Exception as e:
        logger.error("Scan all messages failed", error=str(e))


@celery_app.task(bind=True, max_retries=2)
def reset_all_monthly_credits(self):
    """Reset AI chat credits for all users at the start of each month."""
    try:
        from app.models.user import User
        from sqlalchemy import select
        from app.core.database import get_db_context
        from app.services.credit_service import credit_service
        
        async def _reset():
            async with get_db_context() as db:
                result = await db.execute(
                    select(User.id).where(User.is_active == True)
                )
                user_ids = [r[0] for r in result.fetchall()]
            
            for user_id in user_ids:
                try:
                    await credit_service.reset_monthly_credits(user_id)
                except Exception as e:
                    logger.error("Failed to reset credits for user", user_id=user_id, error=str(e))
        
        _run_async(_reset())
        logger.info("Monthly credits reset for all users completed")
    except Exception as e:
        logger.error("Monthly credits reset failed", error=str(e))
        raise self.retry(exc=e)
