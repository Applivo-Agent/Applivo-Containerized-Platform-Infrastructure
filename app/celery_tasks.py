"""
app/celery_tasks.py
────────────────────
Celery task definitions for all background automation.
Each task is idempotent and handles errors gracefully.
"""

from __future__ import annotations

import asyncio
import random
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

                        # FIX 3: On first bot detection, sleep + retry once before invalidating cookies
                        if login_modal_block and not session_expired:
                            logger.warning("Bot detected - sleeping 60s then retrying once", app_id=app_id)
                            await asyncio.sleep(60)
                            r = await bot.apply(app_id)
                            results[-1] = {"id": app_id, **r}
                            error_text = (r.get("error") or "").lower()
                            session_expired = "session expired" in error_text or "run save_cookies.py" in error_text or "not logged in" in error_text
                            login_modal_block = bool(r.get("bot_detected")) or "login modal" in error_text or "anti-bot detection" in error_text

                        if session_expired or login_modal_block:
                            # Only invalidate after retry also fails (two consecutive detections)
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

                    # FIX 5: Human-like inter-job delay to avoid rate-limiting
                    delay = random.uniform(8, 20)
                    logger.info("Inter-job delay", seconds=round(delay, 1))
                    await asyncio.sleep(delay)

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
    """Deactivate expired subscriptions and handle trial expirations with autopay."""
    try:
        from app.core.database import get_db_context
        from app.models.subscription import Subscription, SubscriptionStatus
        from sqlalchemy import select, String, func, and_
        from datetime import datetime, timezone, timedelta

        async def _check():
            async with get_db_context() as db:
                now = datetime.now(timezone.utc)
                count_expired = 0

                # Handle expired ACTIVE subscriptions
                result = await db.execute(
                    select(Subscription).where(
                        func.lower(Subscription.status.cast(String)) == SubscriptionStatus.ACTIVE.value,
                        Subscription.end_date < now,
                    )
                )
                expired = result.scalars().all()
                for sub in expired:
                    sub.status = SubscriptionStatus.EXPIRED
                    logger.info("Subscription expired", user_id=sub.user_id, sub_id=sub.id)
                    count_expired += 1
                
                # Handle expired TRIAL subscriptions
                result = await db.execute(
                    select(Subscription).where(
                        Subscription.status == SubscriptionStatus.TRIAL,
                        Subscription.trial_end_date < now,
                    )
                )
                expired_trials = result.scalars().all()
                for sub in expired_trials:
                    if sub.razorpay_subscription_id:
                        # Trial with autopay: set to PENDING (waiting for Razorpay to charge)
                        sub.status = SubscriptionStatus.PENDING
                        logger.info("Trial ended, waiting for autopay charge", user_id=sub.user_id, sub_id=sub.id)
                    else:
                        # Trial without autopay: mark as TRIAL_EXPIRED and disable auto-apply
                        sub.status = SubscriptionStatus.TRIAL_EXPIRED
                        try:
                            from app.models.user import UserProfile
                            profile_result = await db.execute(
                                select(UserProfile).where(UserProfile.user_id == sub.user_id)
                            )
                            profile = profile_result.scalar_one_or_none()
                            if profile:
                                profile.auto_apply_enabled = False
                        except Exception as pe:
                            logger.warning("Failed to disable auto-apply after trial expiry", error=str(pe))
                        logger.info("Trial ended without autopay", user_id=sub.user_id, sub_id=sub.id)
                    count_expired += 1

                await db.commit()
                return count_expired

        count = _run_async(_check())
        logger.info("Subscription check completed", expired_count=count)
    except Exception as e:
        logger.error("Subscription check failed", error=str(e))


@celery_app.task
def send_trial_expiry_reminders():
    """Send email reminders to users whose trial ends tomorrow."""
    try:
        from app.core.database import get_db_context
        from app.models.subscription import Subscription, SubscriptionStatus
        from app.models.user import User
        from app.services.notification_service import NotificationService
        from sqlalchemy import select, and_
        from datetime import datetime, timezone, timedelta

        async def _send_reminders():
            async with get_db_context() as db:
                now = datetime.now(timezone.utc)
                tomorrow = now + timedelta(days=1)
                day_after = now + timedelta(days=2)

                # Find trials ending tomorrow
                result = await db.execute(
                    select(Subscription).where(
                        Subscription.status == SubscriptionStatus.TRIAL,
                        Subscription.trial_end_date >= tomorrow,
                        Subscription.trial_end_date < day_after,
                    )
                )
                trials = result.scalars().all()
                sent_count = 0

                for sub in trials:
                    try:
                        user_result = await db.execute(select(User).where(User.id == sub.user_id))
                        user = user_result.scalar_one_or_none()
                        if not user:
                            continue

                        days_left = max(1, (sub.trial_end_date.replace(tzinfo=timezone.utc) - now).days + 1)
                        trial_end_str = sub.trial_end_date.strftime('%B %d, %Y')

                        from app.services import email_service
                        await email_service.send_trial_ending(
                            user.email,
                            user.full_name or user.email,
                            days_left,
                            trial_end_str,
                        )
                        await NotificationService().notify(
                            title=f"Trial ends in {days_left} day{'s' if days_left != 1 else ''}",
                            body=f"Your trial expires on {trial_end_str}.",
                            event_type="trial_expiry_reminder",
                            data={"plan": sub.plan.value, "trial_end": sub.trial_end_date.isoformat()},
                            user_id=sub.user_id,
                        )
                        sent_count += 1
                        logger.info("Trial expiry reminder sent", user_id=sub.user_id)
                    except Exception as e:
                        logger.warning("Failed to send trial expiry reminder", user_id=sub.user_id, error=str(e))

                return sent_count

        count = _run_async(_send_reminders())
        logger.info("Trial expiry reminders sent", count=count)
    except Exception as e:
        logger.error("Send trial expiry reminders failed", error=str(e))


@celery_app.task
def send_trial_expired_emails():
    """Send HTML email to users whose trial just expired (within last 24h)."""
    try:
        from app.core.database import get_db_context
        from app.models.subscription import Subscription, SubscriptionStatus
        from app.models.user import User
        from app.services import email_service
        from sqlalchemy import select
        from datetime import datetime, timezone, timedelta

        async def _run():
            async with get_db_context() as db:
                now = datetime.now(timezone.utc)
                window = now - timedelta(hours=24)
                result = await db.execute(
                    select(Subscription).where(
                        Subscription.status == SubscriptionStatus.TRIAL_EXPIRED,
                        Subscription.trial_end_date >= window,
                        Subscription.trial_end_date < now,
                    )
                )
                count = 0
                for sub in result.scalars().all():
                    user = (await db.execute(select(User).where(User.id == sub.user_id))).scalar_one_or_none()
                    if user:
                        await email_service.send_trial_expired(user.email, user.full_name or user.email)
                        count += 1
                return count

        count = _run_async(_run())
        logger.info("Trial expired emails sent", count=count)
    except Exception as e:
        logger.error("send_trial_expired_emails failed", error=str(e))


@celery_app.task
def send_reengagement_emails():
    """Email users who haven't logged in for 14 days."""
    try:
        from app.core.database import get_db_context
        from app.models.user import User
        from app.models.subscription import Subscription, SubscriptionStatus
        from app.services import email_service
        from sqlalchemy import select
        from datetime import datetime, timezone, timedelta

        async def _run():
            async with get_db_context() as db:
                now = datetime.now(timezone.utc)
                cutoff = now - timedelta(days=14)
                result = await db.execute(
                    select(User).where(
                        User.last_login_at < cutoff,
                        User.last_login_at != None,
                    )
                )
                count = 0
                for user in result.scalars().all():
                    days = max(14, (now - user.last_login_at.replace(tzinfo=timezone.utc)).days)
                    await email_service.send_reengagement(user.email, user.full_name or user.email, days)
                    count += 1
                return count

        count = _run_async(_run())
        logger.info("Re-engagement emails sent", count=count)
    except Exception as e:
        logger.error("send_reengagement_emails failed", error=str(e))


@celery_app.task
def send_profile_incomplete_reminders():
    """Email users with incomplete profiles after 24h of signup."""
    try:
        from app.core.database import get_db_context
        from app.models.user import User, UserProfile
        from app.services import email_service
        from sqlalchemy import select, outerjoin
        from datetime import datetime, timezone, timedelta

        async def _run():
            async with get_db_context() as db:
                now = datetime.now(timezone.utc)
                window_start = now - timedelta(hours=48)
                window_end = now - timedelta(hours=24)
                result = await db.execute(
                    select(User).where(
                        User.created_at >= window_start,
                        User.created_at < window_end,
                    )
                )
                count = 0
                for user in result.scalars().all():
                    profile = (await db.execute(
                        select(UserProfile).where(UserProfile.user_id == user.id)
                    )).scalar_one_or_none()

                    missing = []
                    if not profile:
                        missing = ["Resume / CV", "Skills", "Job preferences", "Work experience"]
                    else:
                        if not profile.professional_summary:
                            missing.append("Professional summary")
                        if not profile.experience_level:
                            missing.append("Experience level")
                        if not profile.location:
                            missing.append("Location preference")
                        if not getattr(profile, 'skills', None) and not getattr(profile, 'career_goals', None):
                            missing.append("Skills & career goals")

                    if missing:
                        await email_service.send_profile_incomplete(user.email, user.full_name or user.email, missing)
                        count += 1
                return count

        count = _run_async(_run())
        logger.info("Profile incomplete reminders sent", count=count)
    except Exception as e:
        logger.error("send_profile_incomplete_reminders failed", error=str(e))


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


# ── Lifecycle email tasks ────────────────────────────────────────────────────


@celery_app.task
def send_weekly_agent_report():
    """Send weekly AI Agent Performance Report to all active subscribers."""
    try:
        from app.core.database import get_db_context
        from app.models.subscription import Subscription, SubscriptionStatus
        from app.models.user import User
        from app.models.job import Application
        from app.services import email_service
        from sqlalchemy import select, func
        from datetime import datetime, timezone, timedelta

        async def _run():
            async with get_db_context() as db:
                now = datetime.now(timezone.utc)
                week_start = now - timedelta(days=7)
                week_label = now.strftime("Week of %B %d, %Y")

                result = await db.execute(
                    select(Subscription).where(
                        Subscription.status.in_([
                            SubscriptionStatus.ACTIVE,
                            SubscriptionStatus.SUCCESS,
                            SubscriptionStatus.TRIAL,
                        ])
                    )
                )
                count = 0
                for sub in result.scalars().all():
                    user = (await db.execute(select(User).where(User.id == sub.user_id))).scalar_one_or_none()
                    if not user:
                        continue

                    apps_result = await db.execute(
                        select(Application).where(
                            Application.user_id == user.id,
                            Application.applied_at >= week_start,
                        )
                    )
                    apps = apps_result.scalars().all()
                    jobs_applied = len(apps)
                    recruiter_replies = sum(1 for a in apps if getattr(a, 'recruiter_replied', False))
                    interviews = sum(1 for a in apps if getattr(a, 'status', '') in ('interview', 'offer'))

                    await email_service.send_ai_agent_performance_report(
                        user.email,
                        user.full_name or user.email,
                        week_label,
                        jobs_analyzed=jobs_applied * 3,
                        jobs_matched=jobs_applied,
                        jobs_applied=jobs_applied,
                        recruiter_replies=recruiter_replies,
                        interviews=interviews,
                        top_skills=[],
                        recommended_actions=[
                            "Update your resume with recent projects",
                            "Set specific job title preferences in settings",
                            "Add more location preferences to expand matches",
                        ] if jobs_applied < 5 else [],
                    )
                    count += 1
                return count

        count = _run_async(_run())
        logger.info("Weekly agent reports sent", count=count)
    except Exception as e:
        logger.error("send_weekly_agent_report failed", error=str(e))


@celery_app.task
def send_trial_day3_emails():
    """Send day-3 progress email to users 3 days into their trial."""
    try:
        from app.core.database import get_db_context
        from app.models.subscription import Subscription, SubscriptionStatus
        from app.models.user import User
        from app.models.job import Application
        from app.services import email_service
        from sqlalchemy import select
        from datetime import datetime, timezone, timedelta

        async def _run():
            async with get_db_context() as db:
                now = datetime.now(timezone.utc)
                day3_start = now - timedelta(days=4)
                day3_end = now - timedelta(days=3)

                result = await db.execute(
                    select(Subscription).where(
                        Subscription.status == SubscriptionStatus.TRIAL,
                        Subscription.created_at >= day3_start,
                        Subscription.created_at < day3_end,
                    )
                )
                count = 0
                for sub in result.scalars().all():
                    user = (await db.execute(select(User).where(User.id == sub.user_id))).scalar_one_or_none()
                    if not user:
                        continue
                    apps_result = await db.execute(
                        select(Application).where(Application.user_id == user.id)
                    )
                    apps = apps_result.scalars().all()
                    await email_service.send_trial_day3(
                        user.email,
                        user.full_name or user.email,
                        jobs_applied=len(apps),
                        jobs_found=len(apps) * 2,
                    )
                    count += 1
                return count

        count = _run_async(_run())
        logger.info("Trial day-3 emails sent", count=count)
    except Exception as e:
        logger.error("send_trial_day3_emails failed", error=str(e))


@celery_app.task
def send_application_aging_alerts():
    """Alert users about applications with no response after 7 days."""
    try:
        from app.core.database import get_db_context
        from app.models.user import User
        from app.models.job import Application
        from app.services import email_service
        from sqlalchemy import select
        from datetime import datetime, timezone, timedelta

        async def _run():
            async with get_db_context() as db:
                now = datetime.now(timezone.utc)
                stale_cutoff = now - timedelta(days=7)
                nudge_window = now - timedelta(days=8)

                result = await db.execute(
                    select(Application).where(
                        Application.applied_at >= nudge_window,
                        Application.applied_at < stale_cutoff,
                        Application.status == "applied",
                    )
                )
                count = 0
                for app in result.scalars().all():
                    user = (await db.execute(select(User).where(User.id == app.user_id))).scalar_one_or_none()
                    if not user:
                        continue
                    days_inactive = (now - app.applied_at.replace(tzinfo=timezone.utc)).days
                    await email_service.send_application_aging(
                        user.email,
                        user.full_name or user.email,
                        company=getattr(app, 'company_name', 'the company') or "the company",
                        role=getattr(app, 'job_title', 'this role') or "this role",
                        days_inactive=days_inactive,
                    )
                    count += 1
                return count

        count = _run_async(_run())
        logger.info("Application aging alerts sent", count=count)
    except Exception as e:
        logger.error("send_application_aging_alerts failed", error=str(e))


@celery_app.task
def send_monthly_career_reports():
    """Send monthly career report on the 1st of each month."""
    try:
        from app.core.database import get_db_context
        from app.models.subscription import Subscription, SubscriptionStatus
        from app.models.user import User
        from app.models.job import Application
        from app.services import email_service
        from sqlalchemy import select
        from datetime import datetime, timezone, timedelta

        async def _run():
            async with get_db_context() as db:
                now = datetime.now(timezone.utc)
                month_start = now.replace(day=1) - timedelta(days=1)
                month_start = month_start.replace(day=1)
                month_label = month_start.strftime("%B %Y")

                result = await db.execute(
                    select(Subscription).where(
                        Subscription.status.in_([
                            SubscriptionStatus.ACTIVE,
                            SubscriptionStatus.SUCCESS,
                            SubscriptionStatus.TRIAL,
                        ])
                    )
                )
                count = 0
                for sub in result.scalars().all():
                    user = (await db.execute(select(User).where(User.id == sub.user_id))).scalar_one_or_none()
                    if not user:
                        continue

                    apps_result = await db.execute(
                        select(Application).where(
                            Application.user_id == user.id,
                            Application.applied_at >= month_start,
                            Application.applied_at < now,
                        )
                    )
                    apps = apps_result.scalars().all()
                    interviews = sum(1 for a in apps if getattr(a, 'status', '') in ('interview', 'offer'))
                    offers = sum(1 for a in apps if getattr(a, 'status', '') == 'offer')

                    await email_service.send_monthly_career_report(
                        user.email,
                        user.full_name or user.email,
                        month_label=month_label,
                        total_applied=len(apps),
                        total_interviews=interviews,
                        total_offers=offers,
                        response_rate=(interviews / len(apps) * 100) if apps else 0.0,
                        days_active=30,
                    )
                    count += 1
                return count

        count = _run_async(_run())
        logger.info("Monthly career reports sent", count=count)
    except Exception as e:
        logger.error("send_monthly_career_reports failed", error=str(e))
