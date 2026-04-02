"""
app/services/application_service.py
─────────────────────────────────────
Handles batch application queuing logic.
Respects daily limits, approval settings, match thresholds, and subscription quotas.
"""

from __future__ import annotations

import structlog
from sqlalchemy import select, func, desc
from datetime import datetime, timezone, date

from app.core.config import settings
from app.core.database import get_db_context
from app.models.job import Job, JobAnalysis, JobStatus
from app.models.application import Application, ApplicationStatus, ApplicationMethod
from app.models.user import User, UserProfile
from app.models.resume import Resume, ResumeType
from app.services.quota_service import quota_service
from app.services.subscription_service import subscription_service

logger = structlog.get_logger()


class ApplicationService:

    async def queue_batch_applications(self) -> dict:
        """
        Find all high-match analyzed jobs that haven't been applied to,
        and queue them for auto-apply respecting subscription quotas and daily limits.
        """
        async with get_db_context() as db:
            # Get all active users with subscriptions
            users = (await db.execute(
                select(User).where(User.is_active == True)
            )).scalars().all()

            total_queued = 0
            results = []

            for user in users:
                result = await self._queue_for_user(db, user)
                results.append(result)
                total_queued += result.get("queued", 0)

            await db.commit()

            return {
                "total_queued": total_queued,
                "user_results": results,
            }

    async def _queue_for_user(self, db, user: User) -> dict:
        """Queue applications for a single user with quota enforcement."""
        # Check subscription
        has_access = await subscription_service.check_access(user.id)
        if not has_access:
            return {"user_id": user.id, "queued": 0, "reason": "No active subscription"}

        # Check quota
        quota = await quota_service.check_quota(user.id)
        if not quota["allowed"]:
            return {"user_id": user.id, "queued": 0, "reason": quota["reason"]}

        profile = (await db.execute(
            select(UserProfile).where(UserProfile.user_id == user.id)
        )).scalar_one_or_none()

        if not profile or not profile.auto_apply_enabled:
            return {"user_id": user.id, "queued": 0, "reason": "Auto-apply disabled"}

        # Check daily limit from subscription (overrides profile setting)
        daily_limit = quota["limit"]
        remaining = quota["remaining"]

        if remaining <= 0:
            return {"user_id": user.id, "queued": 0, "reason": f"Daily limit of {daily_limit} reached"}

        # Find already-applied job IDs to exclude
        applied_job_ids = (await db.execute(
            select(Application.job_id).where(
                Application.user_id == user.id,
                Application.status.in_([
                    ApplicationStatus.APPLIED,
                    ApplicationStatus.QUEUED,
                    ApplicationStatus.PENDING_APPROVAL,
                ])
            )
        )).scalars().all()

        threshold = (
            profile.auto_apply_threshold
            if profile and profile.auto_apply_threshold
            else settings.AUTO_APPLY_MATCH_THRESHOLD
        )

        # Find top qualifying jobs
        result = await db.execute(
            select(Job)
            .join(JobAnalysis, Job.id == JobAnalysis.job_id)
            .where(
                Job.is_active == True,
                Job.status == JobStatus.ANALYZED,
                JobAnalysis.match_score >= threshold,
                ~Job.id.in_(applied_job_ids),
            )
            .order_by(desc(JobAnalysis.priority_score))
            .limit(remaining)
        )
        jobs = result.scalars().all()

        queued = 0
        for job in jobs:
            try:
                resume = await self._find_best_resume(db, user.id, job)

                status = (
                    ApplicationStatus.PENDING_APPROVAL
                    if profile.require_apply_approval
                    else ApplicationStatus.QUEUED
                )

                analysis = (await db.execute(
                    select(JobAnalysis).where(JobAnalysis.job_id == job.id)
                )).scalar_one_or_none()

                app = Application(
                    user_id=user.id,
                    job_id=job.id,
                    resume_id=resume.id if resume else None,
                    method=ApplicationMethod.AUTO_BOT,
                    status=status,
                    job_title_snapshot=job.title,
                    company_snapshot=job.company_name,
                    match_score_at_apply=analysis.match_score if analysis else None,
                )
                db.add(app)
                queued += 1

                if not profile.require_apply_approval:
                    await db.flush()
                    from app.agents.tasks import auto_apply_task
                    auto_apply_task.delay(app.id)

            except Exception as e:
                logger.error("Failed to queue application", user_id=user.id, job_id=job.id, error=str(e))

        if queued > 0:
            from app.services.notification_service import NotificationService
            await NotificationService().notify(
                title=f"{queued} Applications Queued",
                body=f"{queued} jobs matched your criteria and are {'waiting for approval' if profile.require_apply_approval else 'being applied to automatically'}.",
                event_type="applications_queued",
                data={"count": queued},
                user_id=user.id,
            )

        return {"user_id": user.id, "queued": queued, "daily_remaining": remaining - queued}

    async def _find_best_resume(self, db, user_id: str, job: Job) -> Resume | None:
        """Find the most appropriate resume for a job."""
        tailored = (await db.execute(
            select(Resume).where(
                Resume.user_id == user_id,
                Resume.target_job_id == job.id,
                Resume.is_active == True,
            )
        )).scalar_one_or_none()
        if tailored:
            return tailored

        analysis = (await db.execute(
            select(JobAnalysis).where(JobAnalysis.job_id == job.id)
        )).scalar_one_or_none()

        if analysis and analysis.role_category:
            variant = (await db.execute(
                select(Resume).where(
                    Resume.user_id == user_id,
                    Resume.resume_type == ResumeType.ROLE_VARIANT,
                    Resume.role_category == analysis.role_category,
                    Resume.is_active == True,
                )
            )).scalar_one_or_none()
            if variant:
                return variant

        return (await db.execute(
            select(Resume).where(
                Resume.user_id == user_id,
                Resume.is_default == True,
                Resume.is_active == True,
            )
        )).scalar_one_or_none()
