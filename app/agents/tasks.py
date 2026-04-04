"""
app/agents/tasks.py
────────────────────
Async task functions for the Applivo automation pipeline.

Architecture: APScheduler-only (Celery + Redis removed per Fix #10).
All functions are plain async — called directly by APScheduler or the API.
Retry logic is handled per-function using the tenacity-style backoff pattern.
"""

from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timezone
from typing import Optional

logger = logging.getLogger(__name__)

# ── Helper: retry with exponential backoff ───────────────────────────────────

async def _retry(coro_fn, *args, max_retries: int = 3, label: str = "", **kwargs):
    """Run an async callable with exponential-backoff retry (1s, 2s, 4s)."""
    last_exc: Exception = RuntimeError("no attempts")
    for attempt in range(max_retries):
        try:
            return await coro_fn(*args, **kwargs)
        except Exception as exc:
            last_exc = exc
            if attempt < max_retries - 1:
                wait = 2 ** attempt
                logger.warning(f"[retry] {label} attempt {attempt+1} failed — retrying in {wait}s: {exc}")
                await asyncio.sleep(wait)
            else:
                logger.error(f"[retry] {label} failed after {max_retries} attempts: {exc}")
    raise last_exc


# ═══════════════════════════════════════════════════════════════════════════
#  SCRAPING
# ═══════════════════════════════════════════════════════════════════════════

async def scrape_internshala_task(**kwargs):
    """Scrape Internshala for internships."""
    from app.agents.scrapers.internshala import InternshalaScaper
    results = await _retry(InternshalaScaper().run, label="internshala_scrape")
    logger.info(f"Internshala scrape: {results.get('jobs_found', 0)} jobs found")
    return results


# ═══════════════════════════════════════════════════════════════════════════
#  ANALYSIS
# ═══════════════════════════════════════════════════════════════════════════

async def analyze_new_jobs_batch_task():
    """Batch analyze all new jobs."""
    try:
        from app.services.job_analyzer import JobAnalyzerService
        result = await JobAnalyzerService().analyze_new_batch()
        logger.info(f"Batch analysis complete: {result.get('analyzed', 0)} jobs")
        return result
    except Exception as exc:
        logger.error(f"Batch analysis failed: {exc}")
        return {"analyzed": 0, "error": str(exc)}


# ═══════════════════════════════════════════════════════════════════════════
#  AUTO APPLY
# ═══════════════════════════════════════════════════════════════════════════

async def auto_apply_task(application_id: str):
    """Run Playwright bot to submit a single application."""
    from app.agents.apply_bot import ApplyBot
    result = await ApplyBot().apply(application_id)
    # FIX 2: was result['status'] — key does not exist; use result.get('success')
    logger.info(f"Auto-apply {application_id}: success={result.get('success')}, error={result.get('error')}")
    return result


async def queue_auto_applications_task():
    """Queue applications for all eligible jobs."""
    try:
        from app.services.application_service import ApplicationService
        result = await ApplicationService().queue_batch_applications()
        logger.info(f"Queued {result.get('queued', 0)} applications")
        return result
    except Exception as exc:
        logger.error(f"Batch queue failed: {exc}")
        return {"queued": 0}


# ═══════════════════════════════════════════════════════════════════════════
#  NOTIFICATIONS
# ═══════════════════════════════════════════════════════════════════════════

async def send_telegram_notification(notification_id: str):
    """Send a Telegram notification by ID."""
    from app.services.notification_service import NotificationService
    return await _retry(
        NotificationService().send_telegram,
        notification_id,
        label="telegram_notify",
    )


async def send_email_notification(notification_id: str):
    """Send an email notification by ID."""
    from app.services.notification_service import NotificationService
    return await _retry(
        NotificationService().send_email,
        notification_id,
        label="email_notify",
    )


async def send_daily_digest_task():
    """Send daily digest summary."""
    try:
        from app.services.notification_service import NotificationService
        return await NotificationService().send_daily_digest()
    except Exception as exc:
        logger.error(f"Daily digest failed: {exc}")


# ═══════════════════════════════════════════════════════════════════════════
#  FOLLOW-UPS
# ═══════════════════════════════════════════════════════════════════════════

async def check_follow_ups():
    """Process due follow-up emails."""
    try:
        from app.services.follow_up_service import FollowUpService
        result = await FollowUpService().process_due_follow_ups()
        logger.info(f"Follow-ups processed: {result}")
        return result
    except Exception as exc:
        logger.error(f"Follow-up check failed: {exc}")


# ═══════════════════════════════════════════════════════════════════════════
#  EMAIL INBOX
# ═══════════════════════════════════════════════════════════════════════════

async def check_email_inbox():
    """Check inbox for recruiter messages."""
    try:
        from app.services.email_monitor_service import get_email_monitor
        service = get_email_monitor()
        messages = await service.check_inbox(limit=10)
        logger.info(f"Found {len(messages)} recruiter messages")
        for msg in messages:
            await service.forward_to_user(msg)
        return {"checked": True, "messages_found": len(messages)}
    except Exception as exc:
        logger.error(f"Email inbox check failed: {exc}")
        return {"error": str(exc)}


# ═══════════════════════════════════════════════════════════════════════════
#  ORCHESTRATION
# ═══════════════════════════════════════════════════════════════════════════

async def run_main_agent_cycle():
    """
    Master pipeline — scrape → analyze → queue → apply.
    Called by APScheduler on the configured interval.
    """
    logger.info("Starting main agent cycle")
    try:
        await scrape_internshala_task()
        await analyze_new_jobs_batch_task()
        await queue_auto_applications_task()
        logger.info("Main agent cycle complete")
        return {"status": "ok"}
    except Exception as exc:
        logger.error(f"Main cycle failed: {exc}")
        return {"status": "error", "error": str(exc)}


# ── Task Registry (for API triggering) ──────────────────────────────────────

TASK_REGISTRY = {
    "scrape_jobs": run_main_agent_cycle,
    "scrape_internshala": scrape_internshala_task,
    "check_email_inbox": check_email_inbox,
    "analyze_new_jobs": analyze_new_jobs_batch_task,
    "check_follow_ups": check_follow_ups,
    "daily_digest": send_daily_digest_task,
    "check_expiring_subscriptions": check_expiring_subscriptions,
}


# ═══════════════════════════════════════════════════════════════════════════
#  COVER LETTERS
# ═══════════════════════════════════════════════════════════════════════════

async def generate_cover_letter_task(user_id: str, job_id: str, tone: str = "professional"):
    """Generate a cover letter for a specific job."""
    try:
        from app.services.cover_letter_service import CoverLetterService
        result = await CoverLetterService().generate(user_id, job_id, tone)
        logger.info(f"Cover letter generated: {result.get('cover_letter_id')}")
        return result
    except Exception as exc:
        logger.error(f"Cover letter generation failed: {exc}")
        return {"error": str(exc)}


async def check_expiring_subscriptions():
    """Check for subscriptions expiring in 3 days and send notifications."""
    from datetime import timedelta
    from sqlalchemy import select
    from app.models.subscription import Subscription
    from app.core.database import get_db_context

    async with get_db_context() as db:
        from datetime import datetime, timezone
        three_days = datetime.now(timezone.utc) + timedelta(days=3)
        
        result = await db.execute(
            select(Subscription).where(
                Subscription.end_date <= three_days,
                Subscription.end_date >= datetime.now(timezone.utc),
                Subscription.is_active == True,
            )
        )
        expiring = result.scalars().all()
        
        for sub in expiring:
            try:
                from app.services.notification_service import NotificationService
                days_left = (sub.end_date - datetime.now(timezone.utc)).days
                plan_name = sub.plan.value if hasattr(sub.plan, 'value') else str(sub.plan)
                await NotificationService().notify(
                    title="⏰ Subscription Expiring Soon",
                    body=f"""Your {plan_name.upper()} subscription expires in {days_left} day(s) ({sub.end_date.strftime('%B %d, %Y')}).

Don't lose access to:
• Unlimited job applications
• AI-powered resume tailoring
• Auto-apply features
• Interview prep materials

Renew now to continue your job search without interruption!

Visit your dashboard to renew → /subscription

— Team Applivo""",
                    event_type="subscription_expiring",
                    user_id=sub.user_id,
                )
            except Exception as e:
                logger.error(f"Expiry notification failed: {e}")
        
        return {"checked": len(expiring)}