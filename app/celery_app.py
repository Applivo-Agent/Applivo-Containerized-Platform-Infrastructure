"""
app/celery_app.py
──────────────────
Celery worker and beat configuration for background task processing.
All long-running automation tasks run through Celery workers.
"""

from __future__ import annotations

from celery import Celery
from celery.schedules import crontab

from app.core.config import settings

celery_app = Celery(
    "app",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=["app.celery_tasks"],
)

# Keep autodiscovery for conventional task modules while explicitly including
# app.celery_tasks where this project defines all Celery tasks.
celery_app.autodiscover_tasks(["app"])

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
    task_reject_on_worker_lost=True,
    task_acks_on_failure_or_timeout=False,
    broker_connection_retry_on_startup=True,
    beat_schedule_filename="/tmp/celerybeat-schedule",
    task_default_queue="default",
    task_routes={
        "app.celery_tasks.scrape_jobs": {"queue": "scraping"},
        "app.celery_tasks.analyze_jobs": {"queue": "analysis"},
        "app.celery_tasks.auto_apply": {"queue": "apply"},
        "app.celery_tasks.apply_queued_batch": {"queue": "apply"},
        "app.celery_tasks.send_notification": {"queue": "notifications"},
        "app.celery_tasks.check_emails": {"queue": "email_monitor"},
        "app.celery_tasks.send_daily_digest": {"queue": "notifications"},
        # Priority queues by plan tier
        "app.celery_tasks.priority_scrape": {"queue": "priority"},
        "app.celery_tasks.priority_apply": {"queue": "priority"},
    },
)

# ── Periodic tasks (Celery Beat schedule) ────────────────────────────────────

celery_app.conf.beat_schedule = {
    "scrape-jobs-every-6-hours": {
        "task": "app.celery_tasks.scrape_jobs",
        "schedule": crontab(minute=0, hour="*/6"),
    },
    "auto-apply-hourly": {
        "task": "app.celery_tasks.auto_apply",
        "schedule": crontab(minute=0),
    },
    "check-emails-every-30-minutes": {
        "task": "app.celery_tasks.check_emails",
        "schedule": crontab(minute="*/30"),
    },
    "daily-digest": {
        "task": "app.celery_tasks.send_daily_digest",
        "schedule": crontab(hour=9, minute=0),
    },
    "send-trial-expiry-reminders": {
        "task": "app.celery_tasks.send_trial_expiry_reminders",
        "schedule": crontab(hour=9, minute=0),
    },
    "check-expired-subscriptions": {
        "task": "app.celery_tasks.check_expired_subscriptions",
        "schedule": crontab(hour=0, minute=0),
    },
    "check-expired-cookies": {
        "task": "app.celery_tasks.check_expired_cookies",
        "schedule": crontab(hour="*/4", minute=30),
    },
    "reset-monthly-credits": {
        "task": "app.celery_tasks.reset_all_monthly_credits",
        "schedule": crontab(hour=0, minute=0, day_of_month=1),
    },
}
