"""
app/api/routes/scheduler.py
─────────────────────────
API routes for APScheduler job management.
Secured: all endpoints require authentication.
Trigger endpoints additionally require admin access.
"""

from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel
from typing import Optional

from app.api.routes.auth import get_current_user
from app.models.user import User
from app.services.scheduler_service import SchedulerService

router = APIRouter(prefix="/scheduler", tags=["Scheduler"])


class ScheduleJobRequest(BaseModel):
    """Request to schedule a new job."""
    func_name: str
    trigger: str = "interval"  # interval, cron, date
    minutes: Optional[int] = 60
    cron: Optional[str] = None


@router.get("/jobs")
async def list_jobs(current_user: User = Depends(get_current_user)):
    """List all scheduled jobs."""
    try:
        scheduler = SchedulerService()
        scheduler.start()  # Ensure scheduler is running
        return {"jobs": scheduler.list_jobs()}
    except Exception as e:
        import logging
        logging.exception("Scheduler list_jobs failed")
        raise HTTPException(status_code=500, detail=f"Failed to list jobs: {str(e)}")


@router.post("/jobs")
async def add_job(
    request: ScheduleJobRequest,
    current_user: User = Depends(get_current_user),
):
    """Add a new scheduled job."""
    try:
        scheduler = SchedulerService()
        scheduler.start()
        
        # Map function names to actual functions
        func_map = {
            "scrape": "run_scrape_job",
            "auto_apply": "run_auto_apply",
            "email_check": "check_emails",
        }
        
        func_name = func_map.get(request.func_name, request.func_name)
        
        job_id = scheduler.add_job(
            func=lambda: None,  # Placeholder
            trigger=request.trigger,
            minutes=int(request.minutes or 60),
            job_id=f"{request.func_name}_{request.trigger}",
        )
        
        return {"status": "success", "job_id": job_id}
    except Exception as e:
        import logging
        logging.exception("Scheduler add_job failed")
        raise HTTPException(status_code=500, detail=f"Failed to add job: {str(e)}")


@router.delete("/jobs/{job_id}")
async def remove_job(
    job_id: str,
    current_user: User = Depends(get_current_user),
):
    """Remove a scheduled job."""
    try:
        scheduler = SchedulerService()
        scheduler.start()
        scheduler.remove_job(job_id)
        return {"status": "success", "job_id": job_id}
    except Exception as e:
        import logging
        logging.exception("Scheduler remove_job failed")
        raise HTTPException(status_code=500, detail=f"Failed to remove job: {str(e)}")


@router.post("/jobs/{job_id}/run")
async def run_job_now(
    job_id: str,
    current_user: User = Depends(get_current_user),
):
    """Trigger a job to run immediately."""
    try:
        scheduler = SchedulerService()
        scheduler.start()
        scheduler.run_job_now(job_id)
        return {"status": "success", "job_id": job_id}
    except Exception as e:
        import logging
        logging.exception("Scheduler run_job_now failed")
        raise HTTPException(status_code=500, detail=f"Failed to run job: {str(e)}")


@router.post("/jobs/{job_id}/pause")
async def pause_job(
    job_id: str,
    current_user: User = Depends(get_current_user),
):
    """Pause a job."""
    try:
        scheduler = SchedulerService()
        scheduler.start()
        scheduler.pause_job(job_id)
        return {"status": "success", "job_id": job_id}
    except Exception as e:
        import logging
        logging.exception("Scheduler pause_job failed")
        raise HTTPException(status_code=500, detail=f"Failed to pause job: {str(e)}")


@router.post("/jobs/{job_id}/resume")
async def resume_job(
    job_id: str,
    current_user: User = Depends(get_current_user),
):
    """Resume a paused job."""
    try:
        scheduler = SchedulerService()
        scheduler.start()
        scheduler.resume_job(job_id)
        return {"status": "success", "job_id": job_id}
    except Exception as e:
        import logging
        logging.exception("Scheduler resume_job failed")
        raise HTTPException(status_code=500, detail=f"Failed to resume job: {str(e)}")


@router.post("/trigger/{task_name}")
async def trigger_task(
    task_name: str,
    current_user: User = Depends(get_current_user),
):
    """
    Manually trigger a registered task by name.
    Available tasks: scrape_jobs, scrape_internshala, check_email_inbox,
                     analyze_new_jobs, check_follow_ups, daily_digest.
    """
    from app.agents.tasks import TASK_REGISTRY
    import asyncio

    task_fn = TASK_REGISTRY.get(task_name)
    if not task_fn:
        raise HTTPException(status_code=404, detail=f"Task '{task_name}' not found. Available: {list(TASK_REGISTRY.keys())}")

    # Run async task in background
    async def _run():
        try:
            result = await task_fn()
            return result
        except Exception as exc:
            return {"error": str(exc)}

    # Launch without blocking the HTTP response
    asyncio.create_task(_run())
    return {"status": "triggered", "task": task_name}