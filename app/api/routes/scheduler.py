"""
app/api/routes/scheduler.py
──────────────────────────
API routes for APScheduler job management.
"""

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import Optional

from app.services.scheduler_service import SchedulerService

router = APIRouter(prefix="/api/scheduler", tags=["scheduler"])


class ScheduleJobRequest(BaseModel):
    """Request to schedule a new job."""
    func_name: str
    trigger: str = "interval"  # interval, cron, date
    minutes: Optional[int] = 60
    cron: Optional[str] = None


@router.get("/jobs")
async def list_jobs():
    """List all scheduled jobs."""
    scheduler = SchedulerService()
    return {"jobs": scheduler.list_jobs()}


@router.post("/jobs")
async def add_job(request: ScheduleJobRequest):
    """Add a new scheduled job."""
    scheduler = SchedulerService()
    
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
        minutes=request.minutes,
        job_id=f"{request.func_name}_{request.trigger}",
    )
    
    return {"status": "success", "job_id": job_id}


@router.delete("/jobs/{job_id}")
async def remove_job(job_id: str):
    """Remove a scheduled job."""
    scheduler = SchedulerService()
    scheduler.remove_job(job_id)
    return {"status": "success", "job_id": job_id}


@router.post("/jobs/{job_id}/run")
async def run_job_now(job_id: str):
    """Trigger a job to run immediately."""
    scheduler = SchedulerService()
    scheduler.run_job_now(job_id)
    return {"status": "success", "job_id": job_id}


@router.post("/jobs/{job_id}/pause")
async def pause_job(job_id: str):
    """Pause a job."""
    scheduler = SchedulerService()
    scheduler.pause_job(job_id)
    return {"status": "success", "job_id": job_id}


@router.post("/jobs/{job_id}/resume")
async def resume_job(job_id: str):
    """Resume a paused job."""
    scheduler = SchedulerService()
    scheduler.resume_job(job_id)
    return {"status": "success", "job_id": job_id}


@router.post("/trigger/{task_name}")
async def trigger_task(task_name: str):
    """
    Manually trigger a registered task by name.
    Available tasks: scrape_jobs, scrape_internshala, check_email_inbox,
                     analyze_new_jobs, check_follow_ups, daily_digest.
    """
    from app.agents.tasks import TASK_REGISTRY
    import asyncio

    task_fn = TASK_REGISTRY.get(task_name)
    if not task_fn:
        from fastapi import HTTPException
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