"""
app/services/workflow_service.py
────────────────────────────────
Workflow execution engine for the Scrape → Analyze → Queue → Deploy pipeline.
Persists step-level state and auto-advances through stages.
"""

from __future__ import annotations

import asyncio
from datetime import datetime, timezone
from typing import Optional

import structlog
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.core.config import settings
from app.core.database import get_db_context
from app.models.application import Application, ApplicationStatus
from app.models.job import Job, JobAnalysis, JobStatus
from app.models.user import UserProfile
from app.models.workflow import (
    WorkflowExecution,
    WorkflowStatus,
    WorkflowStep,
    WorkflowStepStatus,
    WorkflowStepType,
)
from app.services.analyze_budget_service import analyze_budget_service

logger = structlog.get_logger()

# Ordered pipeline steps
DEFAULT_PIPELINE = [
    WorkflowStepType.SCRAPE,
    WorkflowStepType.ANALYZE,
    WorkflowStepType.QUEUE,
    WorkflowStepType.DEPLOY,
]


class WorkflowService:
    """Orchestrates the Scrape → Analyze → Queue → Deploy pipeline."""

    async def trigger_workflow(
        self,
        user_id: str,
        pipeline: Optional[list[WorkflowStepType]] = None,
    ) -> WorkflowExecution:
        """Create a new workflow execution and spawn its runner."""
        pipeline = pipeline or DEFAULT_PIPELINE

        async with get_db_context() as db:
            # Mark any older running workflows for this user as failed/cancelled
            # so only one pipeline runs at a time per user.
            stuck = (
                await db.execute(
                    select(WorkflowExecution).where(
                        WorkflowExecution.user_id == user_id,
                        WorkflowExecution.status.in_([WorkflowStatus.PENDING, WorkflowStatus.RUNNING]),
                    )
                )
            ).scalars().all()
            for old in stuck:
                old.status = WorkflowStatus.CANCELLED
                old.error_message = "Superseded by new workflow run"
                for step in old.steps:
                    if step.status in (WorkflowStepStatus.PENDING, WorkflowStepStatus.RUNNING):
                        step.status = WorkflowStepStatus.SKIPPED

            workflow = WorkflowExecution(
                user_id=user_id,
                status=WorkflowStatus.PENDING,
                current_step_index=0,
            )
            db.add(workflow)
            await db.flush()

            for idx, step_type in enumerate(pipeline):
                step = WorkflowStep(
                    workflow_id=workflow.id,
                    step_index=idx,
                    step_type=step_type,
                    status=WorkflowStepStatus.PENDING,
                )
                db.add(step)

            await db.commit()
            await db.refresh(workflow)

        # Spawn the runner in the background so the API returns immediately
        task = asyncio.create_task(self._run_workflow(workflow.id))

        def _log_exception(t):
            if t.exception():
                logger.error(
                    "Workflow background task failed",
                    workflow_id=workflow.id,
                    error=str(t.exception()),
                )

        task.add_done_callback(_log_exception)

        return workflow

    async def _run_workflow(self, workflow_id: str) -> None:
        """Background runner that executes each step sequentially."""
        log = logger.bind(workflow_id=workflow_id)
        log.info("Workflow runner started")

        try:
            async with get_db_context() as db:
                workflow = (
                    await db.execute(
                        select(WorkflowExecution).where(WorkflowExecution.id == workflow_id)
                    )
                ).scalar_one_or_none()

                if not workflow:
                    log.warning("Workflow not found, aborting")
                    return

                workflow.status = WorkflowStatus.RUNNING
                workflow.started_at = datetime.now(timezone.utc)
                await db.commit()

            steps = sorted(workflow.steps, key=lambda s: s.step_index)
            overall_result = {}

            for step in steps:
                if workflow.status == WorkflowStatus.CANCELLED:
                    step.status = WorkflowStepStatus.SKIPPED
                    async with get_db_context() as db:
                        await db.merge(step)
                        await db.commit()
                    continue

                await self._run_step(workflow, step, overall_result)

                if step.status == WorkflowStepStatus.FAILED:
                    async with get_db_context() as db:
                        wf = await db.merge(workflow)
                        wf.status = WorkflowStatus.FAILED
                        wf.failed_at = datetime.now(timezone.utc)
                        wf.error_message = step.error_message
                        wf.result_summary = overall_result
                        await db.commit()
                    log.info("Workflow failed at step", step=step.step_type.value)
                    return

            async with get_db_context() as db:
                wf = await db.merge(workflow)
                wf.status = WorkflowStatus.COMPLETED
                wf.completed_at = datetime.now(timezone.utc)
                wf.current_step_index = len(steps)
                wf.result_summary = overall_result
                await db.commit()

            log.info("Workflow completed", result=overall_result)

        except Exception as exc:
            log.error("Workflow runner crashed", error=str(exc))
            try:
                async with get_db_context() as db:
                    workflow = (
                        await db.execute(
                            select(WorkflowExecution).where(WorkflowExecution.id == workflow_id)
                        )
                    ).scalar_one_or_none()
                    if workflow:
                        workflow.status = WorkflowStatus.FAILED
                        workflow.failed_at = datetime.now(timezone.utc)
                        workflow.error_message = f"Runner crashed: {exc}"
                        await db.commit()
            except Exception:
                pass

    async def _run_step(
        self,
        workflow: WorkflowExecution,
        step: WorkflowStep,
        overall_result: dict,
    ) -> None:
        """Execute a single workflow step."""
        log = logger.bind(
            workflow_id=workflow.id,
            step=step.step_type.value,
            step_index=step.step_index,
        )

        step.status = WorkflowStepStatus.RUNNING
        step.started_at = datetime.now(timezone.utc)
        async with get_db_context() as db:
            workflow.current_step_index = step.step_index
            await db.merge(workflow)
            await db.merge(step)
            await db.commit()

        try:
            if step.step_type == WorkflowStepType.SCRAPE:
                result = await self._step_scrape(workflow.user_id)
            elif step.step_type == WorkflowStepType.ANALYZE:
                result = await self._step_analyze(workflow.user_id)
            elif step.step_type == WorkflowStepType.QUEUE:
                result = await self._step_queue(workflow.user_id)
            elif step.step_type == WorkflowStepType.DEPLOY:
                result = await self._step_deploy(workflow.user_id)
            else:
                raise ValueError(f"Unknown step type: {step.step_type}")

            step.status = WorkflowStepStatus.COMPLETED
            step.completed_at = datetime.now(timezone.utc)
            step.result_summary = result
            overall_result[step.step_type.value.lower()] = result
            log.info("Step completed", result=result)

        except Exception as exc:
            step.status = WorkflowStepStatus.FAILED
            step.completed_at = datetime.now(timezone.utc)
            step.error_message = str(exc)
            log.error("Step failed", error=str(exc))

        async with get_db_context() as db:
            await db.merge(step)
            await db.commit()

    async def _step_scrape(self, user_id: str) -> dict:
        from app.agents.scrapers.internshala import InternshalaScraper

        res = await InternshalaScraper(user_id=user_id).run()
        return {
            "jobs_found": res.get("jobs_found", 0),
            "jobs_new": res.get("jobs_new", 0),
        }

    async def _step_analyze(self, user_id: str) -> dict:
        from app.services.job_analyzer import JobAnalyzerService

        budget = await analyze_budget_service.get_analyze_budget(user_id)
        if not budget.get("allowed"):
            return {
                "analyzed": 0,
                "tokens_used": 0,
                "budget_exhausted": True,
                "budget_reason": budget.get("reason") or "Analyze token budget exhausted",
            }

        run_limit = None if budget.get("is_unlimited") else int(budget.get("run_limit_tokens", 0))
        monthly_remaining = None if budget.get("is_unlimited") else int(budget.get("remaining_month_tokens", 0))

        res = await JobAnalyzerService().analyze_user_new_or_unanalyzed(
            user_id=user_id,
            limit=100,
            max_run_tokens=run_limit,
            max_month_tokens_remaining=monthly_remaining,
        )
        return {
            **res,
            "remaining_month_tokens": budget.get("remaining_month_tokens"),
        }

    async def _step_queue(self, user_id: str) -> dict:
        """Queue high-match analyzed jobs for the user."""
        async with get_db_context() as db:
            profile = (
                await db.execute(select(UserProfile).where(UserProfile.user_id == user_id))
            ).scalar_one_or_none()

            threshold = (
                profile.auto_apply_threshold
                if profile and profile.auto_apply_threshold is not None
                else settings.AUTO_APPLY_MATCH_THRESHOLD
            )

            existing_job_ids = {
                row[0] for row in (
                    await db.execute(select(Application.job_id).where(Application.user_id == user_id))
                ).all()
            }

            query = (
                select(Job)
                .outerjoin(JobAnalysis, Job.id == JobAnalysis.job_id)
                .where(
                    Job.is_active == True,
                    Job.user_id == user_id,
                    ~Job.id.in_(existing_job_ids),
                )
                .where(
                    (JobAnalysis.match_score >= threshold) | (JobAnalysis.id == None)
                )
                .limit(100)
            )

            new_jobs = (await db.execute(query)).scalars().all()

            queued_count = 0
            for job in new_jobs:
                try:
                    async with db.begin_nested():
                        db.add(
                            Application(
                                user_id=user_id,
                                job_id=job.id,
                                status=ApplicationStatus.QUEUED,
                                job_title_snapshot=job.title,
                                company_snapshot=job.company_name,
                            )
                        )
                        await db.flush()
                    queued_count += 1
                    existing_job_ids.add(job.id)
                except IntegrityError:
                    continue

            await db.commit()

        return {"queued": queued_count, "threshold_used": threshold}

    async def _step_deploy(self, user_id: str) -> dict:
        """Dispatch queued applications via Celery and wait for completion."""
        from app.celery_app import celery_app
        from app.celery_tasks import apply_queued_batch

        task = apply_queued_batch.delay(user_id)

        # Poll Celery task status until it finishes (or times out after ~10 min)
        result = AsyncResult(task.id, app=celery_app)
        max_wait_seconds = 600
        poll_interval = 5
        waited = 0

        while waited < max_wait_seconds:
            state = result.state
            if state in ("SUCCESS", "FAILURE", "REVOKED"):
                break
            await asyncio.sleep(poll_interval)
            waited += poll_interval

        if state == "SUCCESS":
            task_result = result.result or {}
            return {
                "celery_task_id": task.id,
                "applied": task_result.get("applied", 0),
                "skipped": task_result.get("skipped", 0),
                "failed": task_result.get("failed", 0),
                "message": task_result.get("message", "Deploy completed"),
            }

        if state == "FAILURE":
            raise Exception(f"Deploy task failed: {result.result}")

        # Timed out waiting; record as dispatched but not confirmed
        return {
            "celery_task_id": task.id,
            "applied": 0,
            "skipped": 0,
            "failed": 0,
            "message": "Deploy task dispatched but confirmation timed out",
            "timed_out": True,
        }

    async def get_workflow(self, workflow_id: str) -> Optional[WorkflowExecution]:
        async with get_db_context() as db:
            return (
                await db.execute(
                    select(WorkflowExecution).where(WorkflowExecution.id == workflow_id)
                )
            ).scalar_one_or_none()

    async def get_latest_workflow(self, user_id: str) -> Optional[WorkflowExecution]:
        async with get_db_context() as db:
            return (
                await db.execute(
                    select(WorkflowExecution)
                    .where(WorkflowExecution.user_id == user_id)
                    .order_by(WorkflowExecution.created_at.desc())
                    .limit(1)
                )
            ).scalar_one_or_none()

    async def cancel_workflow(self, workflow_id: str, user_id: str) -> bool:
        async with get_db_context() as db:
            workflow = (
                await db.execute(
                    select(WorkflowExecution).where(
                        WorkflowExecution.id == workflow_id,
                        WorkflowExecution.user_id == user_id,
                    )
                )
            ).scalar_one_or_none()

            if not workflow or workflow.status not in (
                WorkflowStatus.PENDING,
                WorkflowStatus.RUNNING,
            ):
                return False

            workflow.status = WorkflowStatus.CANCELLED
            for step in workflow.steps:
                if step.status in (WorkflowStepStatus.PENDING, WorkflowStepStatus.RUNNING):
                    step.status = WorkflowStepStatus.SKIPPED
            await db.commit()
            return True


# Need to import AsyncResult after celery_app is defined to avoid circular imports at module load
from celery.result import AsyncResult  # noqa: E402

workflow_service = WorkflowService()
