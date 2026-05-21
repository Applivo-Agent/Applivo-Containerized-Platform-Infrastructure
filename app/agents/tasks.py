"""
app/agents/tasks.py
────────────────────
Celery task definitions for the Applivo automation pipeline.
All long-running automation tasks run through Celery workers.
"""

from __future__ import annotations

import asyncio
import structlog
from datetime import datetime, timezone
from typing import Optional

from app.celery_app import celery_app
from app.celery_tasks import _run_async

logger = structlog.get_logger(__name__)

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
                logger.warning(f"Task attempt failed — retrying", 
                             label=label, attempt=attempt+1, wait=wait, error=str(exc))
                await asyncio.sleep(wait)
            else:
                logger.error(f"Task failed after maximum retries", 
                           label=label, max_retries=max_retries, error=str(exc))
    raise last_exc


# ═══════════════════════════════════════════════════════════════════════════
#  SCRAPING
# ═══════════════════════════════════════════════════════════════════════════

@celery_app.task(name="app.agents.tasks.scrape_internshala_task")
def scrape_internshala_task(**kwargs):
    """Scrape Internshala for internships."""
    from app.agents.scrapers.internshala import InternshalaScraper
    
    async def _run():
        scraper = InternshalaScraper()
        return await _retry(scraper.run, label="internshala_scrape")
    
    results = _run_async(_run())
    logger.info("Internshala scrape complete", jobs_found=results.get('jobs_found', 0))
    return results


# ═══════════════════════════════════════════════════════════════════════════
#  ANALYSIS
# ═══════════════════════════════════════════════════════════════════════════

@celery_app.task(name="app.agents.tasks.analyze_new_jobs_batch_task")
def analyze_new_jobs_batch_task():
    """Batch analyze all new jobs."""
    from app.services.job_analyzer import JobAnalyzerService
    
    async def _run():
        return await JobAnalyzerService().analyze_new_batch()
    
    try:
        result = _run_async(_run())
        logger.info("Batch analysis complete", analyzed=result.get('analyzed', 0))
        return result
    except Exception as exc:
        logger.error("Batch analysis failed", error=str(exc))
        return {"analyzed": 0, "error": str(exc)}


# ═══════════════════════════════════════════════════════════════════════════
#  AUTO APPLY
# ═══════════════════════════════════════════════════════════════════════════

@celery_app.task(name="app.agents.tasks.auto_apply_task")
def auto_apply_task(application_id: str):
    """Run Playwright bot to submit a single application."""
    from app.agents.apply_bot import ApplyBot
    
    async def _run():
        return await ApplyBot().apply(application_id)
        
    result = _run_async(_run())
    logger.info("Auto-apply task complete", 
                application_id=application_id, 
                success=result.get('success'), 
                error=result.get('error'))
    return result


@celery_app.task(name="app.agents.tasks.queue_auto_applications_task")
def queue_auto_applications_task():
    """Queue applications for all eligible jobs."""
    from app.services.application_service import ApplicationService
    
    async def _run():
        return await ApplicationService().queue_batch_applications()
        
    try:
        result = _run_async(_run())
        logger.info("Batch application queuing complete", queued=result.get('queued', 0))
        return result
    except Exception as exc:
        logger.error("Batch queue failed", error=str(exc))
        return {"queued": 0}


# ═══════════════════════════════════════════════════════════════════════════
#  RESUME GENERATION
# ═══════════════════════════════════════════════════════════════════════════

@celery_app.task(name="app.agents.tasks.generate_resume_task")
def generate_resume_task(user_id: str, job_id: str, base_resume_id: Optional[str] = None):
    """AI-generate a tailored resume for a job."""
    from app.services.resume_service import ResumeService
    
    async def _run():
        service = ResumeService()
        return await service.generate_tailored(user_id, job_id, base_resume_id)
        
    try:
        result = _run_async(_run())
        logger.info("Resume generation complete", 
                   user_id=user_id, 
                   job_id=job_id, 
                   resume_id=result.get('resume_id'))
        return result
    except Exception as exc:
        logger.error("Resume generation failed", user_id=user_id, job_id=job_id, error=str(exc))
        return {"error": str(exc)}


# ═══════════════════════════════════════════════════════════════════════════
#  NOTIFICATIONS
# ═══════════════════════════════════════════════════════════════════════════

@celery_app.task(name="app.agents.tasks.send_telegram_notification")
def send_telegram_notification(notification_id: str):
    """Send a Telegram notification by ID."""
    from app.services.notification_service import NotificationService
    
    async def _run():
        return await _retry(
            NotificationService().send_telegram,
            notification_id,
            label="telegram_notify",
        )
    return _run_async(_run())


@celery_app.task(name="app.agents.tasks.send_email_notification")
def send_email_notification(notification_id: str):
    """Send an email notification by ID."""
    from app.services.notification_service import NotificationService
    
    async def _run():
        return await _retry(
            NotificationService().send_email,
            notification_id,
            label="email_notify",
        )
    return _run_async(_run())


@celery_app.task(name="app.agents.tasks.send_daily_digest_task")
def send_daily_digest_task():
    """Send daily digest summary."""
    from app.services.notification_service import NotificationService
    
    async def _run():
        return await NotificationService().send_daily_digest()
        
    try:
        return _run_async(_run())
    except Exception as exc:
        logger.error("Daily digest failed", error=str(exc))


# ═══════════════════════════════════════════════════════════════════════════
#  FOLLOW-UPS & INBOX
# ═══════════════════════════════════════════════════════════════════════════

@celery_app.task(name="app.agents.tasks.check_follow_ups")
def check_follow_ups():
    """Process due follow-up emails."""
    from app.services.follow_up_service import FollowUpService
    
    async def _run():
        return await FollowUpService().process_due_follow_ups()
        
    try:
        result = _run_async(_run())
        logger.info("Follow-ups processed", count=result)
        return result
    except Exception as exc:
        logger.error("Follow-up check failed", error=str(exc))


@celery_app.task(name="app.agents.tasks.check_email_inbox")
def check_email_inbox():
    """Check inbox for recruiter messages."""
    from app.services.email_monitor_service import get_email_monitor
    
    async def _run():
        service = get_email_monitor()
        messages = await service.check_inbox(limit=10)
        for msg in messages:
            await service.forward_to_user(msg)
        return {"checked": True, "messages_found": len(messages)}
        
    try:
        result = _run_async(_run())
        logger.info("Email inbox check complete", found=result.get("messages_found", 0))
        return result
    except Exception as exc:
        logger.error("Email inbox check failed", error=str(exc))
        return {"error": str(exc)}


# ═══════════════════════════════════════════════════════════════════════════
#  ORCHESTRATION
# ═══════════════════════════════════════════════════════════════════════════

@celery_app.task(name="app.agents.tasks.run_main_agent_cycle")
def run_main_agent_cycle():
    """Master pipeline — scrape → analyze → queue → apply."""
    logger.info("Starting main agent cycle")

    try:
        # These task functions are synchronous wrappers that already manage
        # their own async execution internally via asyncio.run.
        scrape_internshala_task()
        analyze_new_jobs_batch_task()
        queue_auto_applications_task()
        logger.info("Main agent cycle complete")
        return {"status": "ok"}
    except Exception as exc:
        logger.error("Main cycle failed", error=str(exc))
        return {"status": "error", "error": str(exc)}


# ═══════════════════════════════════════════════════════════════════════════
#  COVER LETTERS
# ═══════════════════════════════════════════════════════════════════════════

@celery_app.task(name="app.agents.tasks.generate_cover_letter_task")
def generate_cover_letter_task(user_id: str, job_id: str, tone: str = "professional"):
    """Generate a cover letter for a specific job."""
    from app.services.cover_letter_service import CoverLetterService
    
    async def _run():
        return await CoverLetterService().generate(user_id, job_id, tone)
        
    try:
        result = _run_async(_run())
        logger.info("Cover letter generated", 
                   user_id=user_id, 
                   job_id=job_id, 
                   letter_id=result.get('cover_letter_id'))
        return result
    except Exception as exc:
        logger.error("Cover letter generation failed", error=str(exc))
        return {"error": str(exc)}


@celery_app.task(name="app.agents.tasks.check_expiring_subscriptions")
def check_expiring_subscriptions():
    """Check for subscriptions expiring in 3 days and send notifications."""
    from datetime import timedelta
    from sqlalchemy import select
    from app.models.subscription import Subscription
    from app.core.database import get_db_context
    
    async def _run():
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
                        body=f"""Your {plan_name.upper()} subscription expires in {days_left} day(s). Renew now to continue!""",
                        event_type="subscription_expiring",
                        user_id=sub.user_id,
                    )
                except Exception as e:
                    logger.error("Expiry notification failed", user_id=sub.user_id, error=str(e))
            
            return {"checked": len(expiring)}
            
    return _run_async(_run())


# ── Task Registry (for API triggering) ──────────────────────────────────────

TASK_REGISTRY = {
    "scrape_jobs": run_main_agent_cycle,
    "scrape_internshala": scrape_internshala_task,
    "check_email_inbox": check_email_inbox,
    "analyze_new_jobs": analyze_new_jobs_batch_task,
    "check_follow_ups": check_follow_ups,
    "daily_digest": send_daily_digest_task,
    "check_expiring_subscriptions": check_expiring_subscriptions,
    "generate_resume": generate_resume_task,
    "generate_cover_letter": generate_cover_letter_task,
}