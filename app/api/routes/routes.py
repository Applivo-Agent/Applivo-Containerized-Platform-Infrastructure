"""
app/api/routes/applications.py  — Application tracking
app/api/routes/resumes.py       — Resume version control
app/api/routes/agent.py         — Agent control panel
app/api/routes/analytics.py     — Dashboard stats
app/api/routes/chat.py          — AI assistant
"""

# ═══════════════════════════════════════════════════════════════════════════
#  applications.py
# ═══════════════════════════════════════════════════════════════════════════

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query, Request
from sqlalchemy import func, select, desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from typing import List, Optional
from datetime import datetime, timezone

from app.core.database import get_db
from app.api.routes.auth import get_current_user
from app.models.user import User
from app.models.application import Application, ApplicationEvent, ApplicationStatus
from app.models.job import Job, JobAnalysis
from app.schemas import (
    ApplicationCreate, ApplicationOut, ApplicationStatusUpdate,
    ApplicationStats, MessageResponse, PaginatedResponse
)

applications_router = APIRouter(prefix="/applications", tags=["Applications"])


@applications_router.get("", response_model=PaginatedResponse)
async def list_applications(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    status: Optional[str] = Query(default=None),
    is_starred: Optional[bool] = Query(default=None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = (
        select(Application)
        .options(selectinload(Application.job).selectinload(Job.analysis))
        .where(Application.user_id == current_user.id)
        .order_by(desc(Application.created_at))
    )
    if status:
        query = query.where(Application.status == status)
    if is_starred is not None:
        query = query.where(Application.is_starred == is_starred)

    total = (await db.execute(select(func.count()).select_from(query.subquery()))).scalar()
    result = await db.execute(query.offset((page - 1) * page_size).limit(page_size))
    apps = result.scalars().all()

    return PaginatedResponse(
        total=total, page=page, page_size=page_size,
        pages=-(-total // page_size),
        items=[ApplicationOut.model_validate(a) for a in apps],
    )


@applications_router.get("/stats", response_model=ApplicationStats)
async def get_application_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Dashboard statistics for the application funnel."""
    result = await db.execute(
        select(Application.status, func.count(Application.id).label("count"))
        .where(Application.user_id == current_user.id)
        .group_by(Application.status)
    )
    counts = {row.status: row.count for row in result.all()}

    applied = counts.get(ApplicationStatus.APPLIED, 0)
    viewed = counts.get(ApplicationStatus.VIEWED, 0)
    shortlisted = counts.get(ApplicationStatus.SHORTLISTED, 0)
    interviews = counts.get(ApplicationStatus.INTERVIEW_SCHEDULED, 0) + \
                 counts.get(ApplicationStatus.INTERVIEW_COMPLETED, 0)
    offers = counts.get(ApplicationStatus.OFFER_RECEIVED, 0) + \
             counts.get(ApplicationStatus.OFFER_ACCEPTED, 0)
    rejected = counts.get(ApplicationStatus.REJECTED, 0)

    total_sent = applied + viewed + shortlisted + interviews + offers + rejected
    positive = viewed + shortlisted + interviews + offers

    return ApplicationStats(
        total_sent=total_sent,
        pending_approval=counts.get(ApplicationStatus.PENDING_APPROVAL, 0),
        applied=applied,
        viewed=viewed,
        shortlisted=shortlisted,
        interviews=interviews,
        offers=offers,
        rejected=rejected,
        response_rate=round(positive / applied * 100, 1) if applied > 0 else 0.0,
        interview_rate=round(interviews / applied * 100, 1) if applied > 0 else 0.0,
        offer_rate=round(offers / applied * 100, 1) if applied > 0 else 0.0,
    )


@applications_router.get("/queue-status")
async def get_queue_status(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get queue status for auto-apply."""
    from app.models.application import ApplicationStatus
    
    # Count pending approval
    result = await db.execute(
        select(func.count(Application.id)).where(
            Application.user_id == current_user.id,
            Application.status == ApplicationStatus.PENDING_APPROVAL
        )
    )
    pending_approval = result.scalar() or 0
    
    # Count queued (ready to apply)
    result = await db.execute(
        select(func.count(Application.id)).where(
            Application.user_id == current_user.id,
            Application.status == ApplicationStatus.QUEUED
        )
    )
    queued = result.scalar() or 0
    
    # Count applied today
    from datetime import datetime, timedelta
    today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    result = await db.execute(
        select(func.count(Application.id)).where(
            Application.user_id == current_user.id,
            Application.status == ApplicationStatus.APPLIED,
            Application.applied_at >= today_start
        )
    )
    applied_today = result.scalar() or 0
    
    return {
        "pendingApproval": pending_approval,
        "queued": queued,
        "appliedToday": applied_today
    }


@applications_router.get("/{app_id}", response_model=ApplicationOut)
async def get_application(
    app_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Application)
        .options(selectinload(Application.job).selectinload(Job.analysis))
        .where(Application.id == app_id, Application.user_id == current_user.id)
    )
    app = result.scalar_one_or_none()
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")
    return app


@applications_router.post("", response_model=ApplicationOut, status_code=201)
async def create_application(
    payload: ApplicationCreate,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Queue a new application (manual or bot-assisted)."""
    # Verify job exists
    job_result = await db.execute(select(Job).where(Job.id == payload.job_id))
    job = job_result.scalar_one_or_none()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    app = Application(
        user_id=current_user.id,
        job_id=payload.job_id,
        resume_id=payload.resume_id,
        cover_letter_id=payload.cover_letter_id,
        method=payload.method,
        notes=payload.notes,
        job_title_snapshot=job.title,
        company_snapshot=job.company_name,
        status=ApplicationStatus.PENDING_APPROVAL if
            payload.method == "auto_bot" else ApplicationStatus.APPLIED,
    )
    db.add(app)
    await db.flush()

    # Log creation event
    event = ApplicationEvent(
        application_id=app.id,
        event_type="application_created",
        to_status=app.status,
        triggered_by="user",
        details={"method": payload.method},
    )
    db.add(event)
    await db.commit()
    await db.refresh(app)

    # Trigger auto-apply bot if approved
    if payload.method == "auto_bot" and not current_user.profile.require_apply_approval:
        background_tasks.add_task(_trigger_auto_apply, app.id)

    return app


@applications_router.patch("/{app_id}/status", response_model=ApplicationOut)
async def update_application_status(
    app_id: str,
    payload: ApplicationStatusUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Application).where(Application.id == app_id, Application.user_id == current_user.id)
    )
    app = result.scalar_one_or_none()
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")

    old_status = app.status
    app.status = payload.status
    if payload.notes:
        app.notes = payload.notes
    if payload.recruiter_name:
        app.recruiter_name = payload.recruiter_name
    if payload.recruiter_email:
        app.recruiter_email = payload.recruiter_email
    if payload.interview_date:
        app.interview_date = payload.interview_date
    if payload.offer_salary:
        app.offer_salary = payload.offer_salary

    # Auto-set timestamps
    now = datetime.now(timezone.utc)
    status_timestamps = {
        "applied": "applied_at",
        "viewed": "viewed_at",
        "shortlisted": "shortlisted_at",
        "interview_scheduled": "interview_scheduled_at",
        "rejected": "rejected_at",
    }
    if payload.status in status_timestamps:
        setattr(app, status_timestamps[payload.status], now)

    # Log event
    event = ApplicationEvent(
        application_id=app.id,
        event_type="status_changed",
        from_status=old_status,
        to_status=payload.status,
        triggered_by="user",
    )
    db.add(event)
    await db.commit()
    await db.refresh(app)
    return app


@applications_router.post("/{app_id}/approve", response_model=MessageResponse)
async def approve_application(
    app_id: str,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Approve a pending application — triggers the auto-apply bot."""
    result = await db.execute(
        select(Application).where(Application.id == app_id, Application.user_id == current_user.id)
    )
    app = result.scalar_one_or_none()
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")
    if app.status != ApplicationStatus.PENDING_APPROVAL:
        raise HTTPException(status_code=400, detail=f"Application is not pending approval (current: {app.status})")

    app.status = ApplicationStatus.QUEUED
    db.add(ApplicationEvent(
        application_id=app.id,
        event_type="status_changed",
        from_status=ApplicationStatus.PENDING_APPROVAL,
        to_status=ApplicationStatus.QUEUED,
        triggered_by="user",
        details={"action": "approved"},
    ))
    await db.commit()
    background_tasks.add_task(_trigger_auto_apply, app.id)
    return MessageResponse(message="Application approved and queued for bot")


@applications_router.patch("/{app_id}/star", response_model=ApplicationOut)
async def toggle_star(
    app_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Application).where(Application.id == app_id, Application.user_id == current_user.id)
    )
    app = result.scalar_one_or_none()
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")
    app.is_starred = not app.is_starred
    await db.commit()
    await db.refresh(app)
    return app


@applications_router.post("/{app_id}/apply-now", response_model=MessageResponse)
async def apply_now(
    app_id: str,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Trigger immediate auto-apply for a single application."""
    result = await db.execute(
        select(Application).where(Application.id == app_id, Application.user_id == current_user.id)
    )
    app = result.scalar_one_or_none()
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")
    
    if app.status == ApplicationStatus.APPLIED:
        raise HTTPException(status_code=400, detail="Already applied to this job")
    
    if app.status == ApplicationStatus.APPLYING:
        raise HTTPException(status_code=400, detail="Application is already being processed")
    
    # Trigger the bot to apply
    background_tasks.add_task(_trigger_auto_apply, app.id)
    
    return MessageResponse(message="Application process started")


async def _trigger_auto_apply(application_id: str):
    """Trigger auto-apply for an application - uses actual bot."""
    try:
        from app.core.database import get_db_context
        from app.models.application import Application, ApplicationStatus
        from sqlalchemy import select
        from datetime import datetime, timezone
        
        async with get_db_context() as db:
            result = await db.execute(
                select(Application).where(Application.id == application_id)
            )
            app = result.scalar_one_or_none()
            if app:
                # Use the actual bot instead of just marking as applied
                from app.agents.apply_bot import ApplyBot
                bot = ApplyBot()
                result = await bot.apply(application_id)
                
                import structlog
                structlog.get_logger().info("Application auto-applied via bot", app_id=application_id, result=result)
    except Exception as e:
        import structlog
        structlog.get_logger().error("Failed to auto-apply via bot", app_id=application_id, error=str(e))


# ═══════════════════════════════════════════════════════════════════════════
#  resumes.py
# ═══════════════════════════════════════════════════════════════════════════

resumes_router = APIRouter(prefix="/resumes", tags=["Resumes"])

from app.models.resume import Resume, CoverLetter
from app.schemas import ResumeOut, CoverLetterOut, ResumeGenerateRequest, CoverLetterGenerateRequest
import aiofiles
from fastapi import UploadFile, File
from pathlib import Path


@resumes_router.get("", response_model=List[ResumeOut])
async def list_resumes(
    is_active: bool = Query(default=True),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Resume)
        .where(Resume.user_id == current_user.id, Resume.is_active == is_active)
        .order_by(desc(Resume.created_at))
    )
    return result.scalars().all()


@resumes_router.post("/upload", response_model=ResumeOut, status_code=201)
async def upload_resume(
    file: UploadFile = File(...),
    name: Optional[str] = Query(default=None),
    resume_type: str = Query(default="base"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Upload a PDF resume file."""
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are accepted")
    
    # Use provided name or fallback to filename without extension
    if not name:
        name = file.filename.replace(".pdf", "") if file.filename else "Untitled Resume"

    from app.core.config import settings
    import uuid
    file_name = f"{uuid.uuid4()}.pdf"
    file_path = settings.resumes_path / file_name

    content = await file.read()
    async with aiofiles.open(file_path, "wb") as f:
        await f.write(content)

    resume = Resume(
        user_id=current_user.id,
        name=name,
        resume_type=resume_type,
        file_path=str(file_path.relative_to(settings.storage_path)),
        file_size_bytes=len(content),
    )
    db.add(resume)
    await db.commit()
    await db.refresh(resume)
    return resume


@resumes_router.post("/generate", response_model=MessageResponse, status_code=202)
async def generate_tailored_resume(
    payload: ResumeGenerateRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """AI-generate a tailored resume for a specific job."""
    background_tasks.add_task(_trigger_resume_generation, current_user.id, payload.job_id, payload.base_resume_id)
    return MessageResponse(message="Resume generation queued")


@resumes_router.patch("/{resume_id}/set-default", response_model=ResumeOut)
async def set_default_resume(
    resume_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Set a resume as the default for applications."""
    # Unset all defaults first
    result = await db.execute(select(Resume).where(Resume.user_id == current_user.id, Resume.is_default == True))
    for r in result.scalars().all():
        r.is_default = False

    result = await db.execute(select(Resume).where(Resume.id == resume_id, Resume.user_id == current_user.id))
    resume = result.scalar_one_or_none()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
    resume.is_default = True
    await db.commit()
    await db.refresh(resume)
    return resume


@resumes_router.post("/auto-set-default")
async def auto_set_default_resume(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Automatically set the first available resume as default."""
    # Find first resume
    result = await db.execute(
        select(Resume).where(Resume.user_id == current_user.id).order_by(Resume.created_at)
    )
    resume = result.scalars().first()
    
    if not resume:
        raise HTTPException(status_code=404, detail="No resumes found. Please upload a resume first.")
    
    # Unset all defaults
    all_default = await db.execute(
        select(Resume).where(Resume.user_id == current_user.id, Resume.is_default == True)
    )
    for r in all_default.scalars().all():
        r.is_default = False
    
    # Set this one as default
    resume.is_default = True
    await db.commit()
    await db.refresh(resume)
    
    return {
        "success": True,
        "resume_id": resume.id,
        "resume_name": resume.name,
        "message": f"Resume '{resume.name}' set as default"
    }


@resumes_router.get("/latex", response_model=dict)
async def generate_latex_resume(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    use_custom: bool = True,
):
    """Generate a LaTeX resume for Overleaf.
    
    Args:
        use_custom: If True, uses your custom template. If False, uses default moderncv.
    """
    from app.services.overleaf_service import OverleafService
    result = await OverleafService().generate_latex_resume(current_user.id, use_custom=use_custom)
    return result


@resumes_router.post("/latex/template", response_model=dict)
async def set_custom_latex_template(
    latex_code: str,
    current_user: User = Depends(get_current_user),
):
    """Set your custom LaTeX resume template.
    
    Provide your own LaTeX code template. Must include \\section{} and \\begin{document}
    The template will be filled with your profile data when generating resumes.
    """
    from app.services.overleaf_service import OverleafService
    service = OverleafService()
    result = service.set_custom_template(latex_code)
    return result


@resumes_router.get("/latex/templates", response_model=dict)
async def list_latex_templates():
    """List all available LaTeX resume templates with current selection."""
    from app.services.overleaf_service import OverleafService
    service = OverleafService()
    available = service.list_available_templates()
    current = service.get_current_template()
    selected = "default"
    # Find which template is currently selected
    if service._custom_template:
        for t in available:
            if t.get("filename"):
                try:
                    if service.load_template(t["name"]) == service._custom_template:
                        selected = t["name"]
                        break
                except:
                    pass
    return {"available": available, "selected": selected}


@resumes_router.get("/latex/template", response_model=dict)
async def get_latex_template():
    """Get the current LaTeX template (default or custom)."""
    from app.services.overleaf_service import OverleafService
    template = OverleafService().get_current_template()
    return {
        "template": template,
        "is_custom": OverleafService._custom_template is not None
    }

@resumes_router.post("/latex/template/select", response_model=dict)
async def select_latex_template(
    request: Request,
    current_user: User = Depends(get_current_user),
):
    """Select a template by name (e.g., 'default', 'mteck')."""
    body = await request.json()
    template_name = body.get("template_name")
    
    if not template_name:
        return {"success": False, "error": "template_name is required"}
    
    from app.services.overleaf_service import OverleafService
    service = OverleafService()
    try:
        template = service.load_template(template_name)
        service.set_custom_template(template)
        return {
            "success": True,
            "template_name": template_name,
            "message": f"Template '{template_name}' selected successfully"
        }
    except ValueError as e:
        return {"success": False, "error": str(e)}


@resumes_router.get("/analyze", response_model=dict)
async def analyze_all_resumes(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Analyze all resumes in the user's profile."""
    from app.services.overleaf_service import OverleafService
    result = await OverleafService().analyze_all_resumes(current_user.id)
    return result


async def _trigger_resume_generation(user_id: str, job_id: str, base_resume_id: Optional[str]):
    try:
        from app.agents.tasks import generate_resume_task
        generate_resume_task.delay(user_id, job_id, base_resume_id)
    except Exception as e:
        import structlog
        structlog.get_logger().error("Failed to queue resume gen", error=str(e))


# ── Cover Letters ────────────────────────────────────────────────────────────

cover_letters_router = APIRouter(prefix="/cover-letters", tags=["Cover Letters"])


@cover_letters_router.post("/generate", status_code=202)
async def generate_cover_letter(
    payload: CoverLetterGenerateRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    background_tasks.add_task(_trigger_cover_letter_gen, current_user.id, payload.job_id, payload.tone)
    return {"message": "Cover letter generation started", "job_id": payload.job_id}


@cover_letters_router.get("", response_model=List[CoverLetterOut])
async def list_cover_letters(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(CoverLetter)
        .where(CoverLetter.user_id == current_user.id)
        .order_by(desc(CoverLetter.created_at))
    )
    return result.scalars().all()


@cover_letters_router.delete("/{letter_id}")
async def delete_cover_letter(
    letter_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(CoverLetter).where(
            CoverLetter.id == letter_id,
            CoverLetter.user_id == current_user.id
        )
    )
    letter = result.scalar_one_or_none()
    if not letter:
        raise HTTPException(status_code=404, detail="Cover letter not found")
    
    await db.delete(letter)
    await db.commit()
    return {"success": True, "message": "Cover letter deleted"}


@cover_letters_router.get("/{letter_id}")
async def get_cover_letter(
    letter_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(CoverLetter).where(
            CoverLetter.id == letter_id,
            CoverLetter.user_id == current_user.id
        )
    )
    letter = result.scalar_one_or_none()
    if not letter:
        raise HTTPException(status_code=404, detail="Cover letter not found")
    return letter


async def _trigger_cover_letter_gen(user_id: str, job_id: str, tone: str):
    from app.services.cover_letter_service import CoverLetterService
    try:
        await CoverLetterService().generate(user_id, job_id, tone)
    except Exception as e:
        logger.error(f"Cover letter generation failed: {e}")


# ═══════════════════════════════════════════════════════════════════════════
#  agent.py — Agent control panel
# ═══════════════════════════════════════════════════════════════════════════

agent_router = APIRouter(prefix="/agent", tags=["Agent"])

from app.models.interview import AgentTask, AgentTaskStatus
from app.schemas import AgentTaskOut, AgentStatusResponse, ManualAgentRunRequest


@agent_router.post("/apply/{application_id}")
async def apply_to_job(
    application_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Apply to a specific job - triggers the apply bot."""
    import structlog
    from app.agents.apply_bot import ApplyBot
    
    log = structlog.get_logger()
    
    # Get the application
    result = await db.execute(
        select(Application).where(
            Application.id == application_id,
            Application.user_id == current_user.id
        )
    )
    app = result.scalar_one_or_none()
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")
    
    # Run the apply bot
    try:
        bot = ApplyBot()
        result = await bot.apply(application_id)
        return result
    except Exception as e:
        log.error("Apply failed", application_id=application_id, error=str(e))
        raise HTTPException(status_code=500, detail=f"Apply failed: {str(e)}")


@agent_router.get("/status", response_model=AgentStatusResponse)
async def get_agent_status(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get current background agent status."""
    from datetime import date
    today = datetime.now(timezone.utc).date()

    result = await db.execute(
        select(AgentTask)
        .where(func.date(AgentTask.created_at) == today)
        .order_by(desc(AgentTask.created_at))
    )
    tasks_today = result.scalars().all()

    running = [t for t in tasks_today if t.status == AgentTaskStatus.RUNNING]
    succeeded = [t for t in tasks_today if t.status == AgentTaskStatus.SUCCESS]
    failed = [t for t in tasks_today if t.status == AgentTaskStatus.FAILED]

    # Jobs found today
    from app.models.job import Job
    from sqlalchemy import cast, Date
    jobs_today = (await db.execute(
        select(func.count(Job.id)).where(func.date(Job.scraped_at) == today)
    )).scalar()

    # Applications today
    apps_today = (await db.execute(
        select(func.count(Application.id))
        .where(
            Application.user_id == current_user.id,
            func.date(Application.applied_at) == today,
        )
    )).scalar()

    last_task = tasks_today[0] if tasks_today else None

    return AgentStatusResponse(
        is_running=len(running) > 0,
        current_task=running[0].task_type if running else None,
        last_run_at=last_task.created_at if last_task else None,
        next_run_at=None,  # Populated by scheduler
        tasks_today=len(tasks_today),
        tasks_succeeded=len(succeeded),
        tasks_failed=len(failed),
        jobs_found_today=jobs_today or 0,
        applications_today=apps_today or 0,
    )


@agent_router.get("/tasks", response_model=List[AgentTaskOut])
async def list_agent_tasks(
    limit: int = Query(default=50, le=200),
    status: Optional[str] = Query(default=None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = select(AgentTask).order_by(desc(AgentTask.created_at)).limit(limit)
    if status:
        query = query.where(AgentTask.status == status)
    result = await db.execute(query)
    return result.scalars().all()


@agent_router.post("/run")
async def trigger_agent_manually(
    payload: ManualAgentRunRequest,
    current_user: User = Depends(get_current_user),
):
    """
    Manually trigger an agent task. Runs SYNCHRONOUSLY and returns real counts.
    Desktop mode: no Celery, no background tasks — caller waits for the result.
    Supported task_types: scrape_jobs | apply_queued | analyze_and_queue
    """
    import structlog, time
    log = structlog.get_logger()

    SUPPORTED_TASKS = {"scrape_jobs", "apply_queued", "analyze_and_queue"}

    task_type = payload.task_type
    if task_type not in SUPPORTED_TASKS:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown task type: {task_type}. Supported: {sorted(SUPPORTED_TASKS)}",
        )

    # Check if user has active subscription for any agent tasks
    from app.services.subscription_service import SubscriptionService
    sub_service = SubscriptionService()
    sub = await sub_service.get_active_subscription(current_user.id)
    
    if not sub or not sub.is_active:
        raise HTTPException(
            status_code=403,
            detail="Active subscription required to use agent features. Please subscribe at /subscription",
        )

    log.info("Triggering task", task_type=task_type)
    t0 = time.perf_counter()

    try:
        # ── scrape_jobs ─────────────────────────────────────────────────────
        if task_type == "scrape_jobs":
            from app.agents.scrapers.internshala import IntershalaScraper
            result = await IntershalaScraper(user_id=current_user.id).run()
            elapsed = round(time.perf_counter() - t0, 1)
            jobs_found = result.get("jobs_found", 0)
            log.info("Scrape complete", jobs_found=jobs_found, elapsed=elapsed)
            return {
                "task_type": "scrape_jobs",
                "jobs_found": jobs_found,
                "jobs_new": result.get("jobs_new", 0),
                "duration_seconds": elapsed,
                "message": f"Scraped {jobs_found} jobs in {elapsed}s",
            }

        # ── analyze_and_queue ───────────────────────────────────────────────
        elif task_type == "analyze_and_queue":
            # First run AI analysis on new jobs, then create QUEUED Application rows.
            from app.core.database import get_db_context
            from app.core.config import settings
            from app.models.job import Job, JobAnalysis
            from app.models.application import Application, ApplicationStatus
            from app.services.job_analyzer import JobAnalyzerService
            from sqlalchemy import select

            analyzer = JobAnalyzerService()
            analyzed = 0
            
            async with get_db_context() as db:
                new_jobs_result = await db.execute(
                    select(Job).where(Job.is_active == True).limit(50)
                )
                new_jobs = new_jobs_result.scalars().all()
            
            for job in new_jobs:
                try:
                    await analyzer.analyze(job.id)
                    analyzed += 1
                except Exception as e:
                    log.error("Analysis failed", job_id=job.id, error=str(e))

            threshold = settings.AUTO_APPLY_MATCH_THRESHOLD
            queued_count = 0
            async with get_db_context() as db:
                # Get existing job IDs from applications (excluding SKIPPED so we can re-queue those if they become eligible - but for now exclude all existing)
                existing_job_ids = {
                    row[0] for row in (await db.execute(
                        select(Application.job_id).where(
                            Application.user_id == current_user.id,
                            Application.status != ApplicationStatus.SKIPPED  # Don't re-queue failed/skipped - only re-queue APPLIED/QUEUED/FAILED
                        )
                    )).all()
                }
                new_jobs = (await db.execute(
                    select(Job).where(
                        Job.is_active == True,
                        ~Job.id.in_(existing_job_ids),
                    ).outerjoin(
                        JobAnalysis, Job.id == JobAnalysis.job_id
                    ).where(
                        (JobAnalysis.match_score >= threshold) | (JobAnalysis.match_score == None)
                    ).limit(50)
                )).scalars().all()

                for job in new_jobs:
                    db.add(Application(
                        user_id=current_user.id,
                        job_id=job.id,
                        status=ApplicationStatus.QUEUED,
                        job_title_snapshot=job.title,
                        company_snapshot=job.company_name,
                    ))
                    queued_count += 1
                await db.commit()

            elapsed = round(time.perf_counter() - t0, 1)
            log.info("Analyze and queue complete", analyzed=analyzed, queued=queued_count, elapsed=elapsed)
            return {
                "task_type": "analyze_and_queue",
                "analyzed": analyzed,
                "queued": queued_count,
                "match_threshold": threshold,
                "duration_seconds": elapsed,
                "message": f"Analyzed {analyzed} jobs, queued {queued_count} (threshold: {threshold}%)",
            }

        # ── apply_queued ────────────────────────────────────────────────────
        elif task_type == "apply_queued":
            # Run synchronously so we can return real counts to the UI.
            from app.core.database import get_db_context
            from app.core.config import settings
            from app.models.application import Application, ApplicationStatus
            from app.models.job import JobAnalysis
            from app.agents.apply_bot import ApplyBot
            from sqlalchemy import select

            threshold = settings.AUTO_APPLY_MATCH_THRESHOLD

            async with get_db_context() as db:
                result = await db.execute(
                    select(Application).where(
                        Application.status == ApplicationStatus.QUEUED
                    ).outerjoin(
                        JobAnalysis, Application.job_id == JobAnalysis.job_id
                    ).where(
                        (JobAnalysis.match_score >= threshold) | (JobAnalysis.match_score == None)
                    ).order_by(Application.created_at.asc()).limit(10)
                )
                queued = result.scalars().all()
                app_ids = [a.id for a in queued]

            skipped_by_threshold = 0
            total = 0
            async with get_db_context() as db:
                total_queued = await db.execute(
                    select(func.count(Application.id)).where(Application.status == ApplicationStatus.QUEUED)
                )
                total = total_queued.scalar() or 0
                below_threshold = await db.execute(
                    select(func.count(Application.id)).where(
                        Application.status == ApplicationStatus.QUEUED
                    ).outerjoin(
                        JobAnalysis, Application.job_id == JobAnalysis.job_id
                    ).where(JobAnalysis.match_score < threshold)
                )
                skipped_by_threshold = below_threshold.scalar() or 0

            if not app_ids:
                return {
                    "task_type": "apply_queued",
                    "applied": 0,
                    "failed": 0,
                    "total_queued": 0,
                    "duration_seconds": 0.0,
                    "message": (
                        "No queued applications found. "
                        "Run Scrape first, then Queue Jobs to create applications."
                    ),
                }

            bot = ApplyBot()
            applied_count = 0
            failed_count = 0
            skipped_count = 0
            already_applied_count = 0
            results = []

            for app_id in app_ids:
                try:
                    r = await bot.apply(app_id)
                    if r.get("success"):
                        if r.get("already_applied"):
                            # Already applied externally - sync status
                            already_applied_count += 1
                            async with get_db_context() as db:
                                app = await db.get(Application, app_id)
                                if app:
                                    app.status = ApplicationStatus.APPLIED
                                    app.applied_at = datetime.now(timezone.utc)
                                    await db.commit()
                            log.info("Already applied - synced", app_id=app_id)
                        else:
                            applied_count += 1
                            log.info("Applied", app_id=app_id)
                    elif r.get("ineligible"):
                        # Mark as SKIPPED so it won't be retried
                        skipped_count += 1
                        async with get_db_context() as db:
                            app = await db.get(Application, app_id)
                            if app:
                                app.status = ApplicationStatus.SKIPPED
                                app.bot_error = r.get("error", "Not eligible")
                                await db.commit()
                        log.warning("Job not eligible - marked as SKIPPED", app_id=app_id)
                    elif r.get("error") and "external" in r.get("error", "").lower():
                        # External job posting - mark as FAILED so it won't retry
                        failed_count += 1
                        async with get_db_context() as db:
                            app = await db.get(Application, app_id)
                            if app:
                                app.status = ApplicationStatus.FAILED
                                app.bot_error = r.get("error", "External posting")
                                app.retry_count = 999
                                await db.commit()
                        log.warning("External job - marked as FAILED", app_id=app_id)
                    else:
                        failed_count += 1
                        log.warning("Apply failed", app_id=app_id, error=r.get("error"))
                    results.append({"id": app_id, **r})
                except Exception as exc:
                    failed_count += 1
                    log.error("Apply exception", app_id=app_id, error=str(exc))
                    results.append({"id": app_id, "success": False, "error": str(exc)})

            elapsed = round(time.perf_counter() - t0, 1)
            log.info("Apply run complete", applied=applied_count, failed=failed_count, elapsed=elapsed)
            return {
                "task_type": "apply_queued",
                "applied": applied_count,
                "failed": failed_count,
                "skipped": skipped_count,
                "total_queued": len(app_ids),
                "skipped_below_threshold": skipped_by_threshold,
                "match_threshold": threshold,
                "duration_seconds": elapsed,
                "message": f"Applied to {applied_count}/{len(app_ids)} jobs (skipped: {skipped_count}, threshold: {threshold}%) in {elapsed}s",
                "results": results,
            }

    except HTTPException:
        raise
    except Exception as e:
        log.error("Task failed", task_type=task_type, error=str(e))
        import traceback
        raise HTTPException(status_code=500, detail=f"{type(e).__name__}: {e}\n{traceback.format_exc()}")


@agent_router.post("/pause", response_model=MessageResponse)
async def pause_agent(current_user: User = Depends(get_current_user)):
    """Pause background automation."""
    # In production: update Redis key that worker checks
    return MessageResponse(message="Agent paused")


@agent_router.post("/resume", response_model=MessageResponse)
async def resume_agent(current_user: User = Depends(get_current_user)):
    """Resume background automation."""
    return MessageResponse(message="Agent resumed")


# ═══════════════════════════════════════════════════════════════════════════
#  chat.py — AI Career Assistant
# ═══════════════════════════════════════════════════════════════════════════

chat_router = APIRouter(prefix="/chat", tags=["AI Assistant"])

from app.schemas import ChatRequest, ChatResponse
from app.services.credit_service import credit_service


@chat_router.post("", response_model=ChatResponse)
async def chat_with_assistant(
    payload: ChatRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Conversational AI assistant with access to the user's career data.
    Handles natural language commands like:
    - "Find AI internships in Europe"
    - "Apply to the top 3 jobs"
    - "What skills should I learn next?"
    - "How many applications did I send this week?"
    """
    # Check AI credits before processing
    credits = await credit_service.get_user_credits(current_user.id)
    
    if not credits["allowed"]:
        return ChatResponse(
            response=f"❌ No AI credits available. {credits['reason']}. Please upgrade your plan at /subscription to continue using the AI assistant.",
            actions_taken=[]
        )
    
    if not credits["is_unlimited"] and credits["remaining"] <= 10:
        remaining = credits["remaining"]
        return ChatResponse(
            response=f"⚠️ You have only {remaining} AI credits remaining this month. Consider upgrading at /subscription for unlimited access.",
            actions_taken=[]
        )
    
    # Process the chat
    from app.services.ai_assistant import CareerAssistant
    assistant = CareerAssistant(db=db, user=current_user)
    response = await assistant.chat(
        message=payload.message,
        history=payload.conversation_history,
    )
    
    # Consume credit
    await credit_service.consume_credit(current_user.id)
    
    return response


# Credit status endpoint
@chat_router.get("/credits")
async def get_ai_credits(
    current_user: User = Depends(get_current_user),
):
    """Get user's AI credit status."""
    return await credit_service.get_user_credits(current_user.id)


# ═══════════════════════════════════════════════════════════════════════════
#  analytics.py
# ═══════════════════════════════════════════════════════════════════════════

analytics_router = APIRouter(prefix="/analytics", tags=["Analytics"])

from app.schemas import DashboardStats, MarketInsightResponse
from app.models.interview import MarketSnapshot, SkillGap
from app.schemas import SkillGapOut


@analytics_router.get("/dashboard", response_model=DashboardStats)
async def get_dashboard(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Full dashboard data in a single API call — fields match DashboardStats schema."""

    # Application status counts
    app_result = await db.execute(
        select(Application.status, func.count(Application.id).label("count"))
        .where(Application.user_id == current_user.id)
        .group_by(Application.status)
    )
    counts = {row.status: row.count for row in app_result.all()}

    applied      = counts.get("applied", 0)
    interviews   = counts.get("interview_scheduled", 0) + counts.get("interview_completed", 0)
    offers       = counts.get("offer_received", 0) + counts.get("offer_accepted", 0)
    total_apps   = sum(counts.values())
    total_positive = counts.get("viewed", 0) + counts.get("shortlisted", 0) + interviews + offers
    response_rate  = round(total_positive / applied * 100, 1) if applied else 0.0

    # Job counts
    today = datetime.now(timezone.utc).date()
    total_jobs = (await db.execute(select(func.count(Job.id)))).scalar() or 0
    jobs_today  = (await db.execute(
        select(func.count(Job.id)).where(func.date(Job.scraped_at) == today)
    )).scalar() or 0

    # High match jobs (score >= 70)
    high_match = (await db.execute(
        select(func.count(JobAnalysis.id)).where(JobAnalysis.match_score >= 70)
    )).scalar() or 0

    # Recent activity (last 10 applications as simple dicts)
    recent_apps_result = await db.execute(
        select(Application)
        .options(selectinload(Application.job))
        .where(Application.user_id == current_user.id)
        .order_by(desc(Application.created_at))
        .limit(10)
    )
    recent_apps = recent_apps_result.scalars().all()
    recent_activity = [
        {
            "id": str(a.id),
            "job_title": a.job_title_snapshot or (a.job.title if a.job else ""),
            "company": a.company_snapshot or (a.job.company_name if a.job else ""),
            "status": a.status,
            "applied_at": a.applied_at.isoformat() if a.applied_at else None,
            "created_at": a.created_at.isoformat() if a.created_at else None,
        }
        for a in recent_apps
    ]

    return DashboardStats(
        total_jobs=total_jobs,
        jobs_today=jobs_today,
        high_match_jobs=high_match,
        total_applications=total_apps,
        applications_today=counts.get("applied", 0),
        pending_approval=counts.get("pending_approval", 0),
        interviews_scheduled=interviews,
        offers_received=offers,
        response_rate=response_rate,
        top_skill_gaps=[],
        recent_activity=recent_activity,
    )


@analytics_router.get("/skill-gaps", response_model=List[SkillGapOut])
async def get_skill_gaps(
    resolved: bool = Query(default=False),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(SkillGap)
        .where(SkillGap.user_id == current_user.id, SkillGap.resolved == resolved)
        .order_by(desc(SkillGap.demand_count))
    )
    return result.scalars().all()


@analytics_router.get("/market", response_model=MarketInsightResponse)
async def get_market_insights(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Latest job market intelligence snapshot."""
    result = await db.execute(
        select(MarketSnapshot).order_by(desc(MarketSnapshot.snapshot_date)).limit(1)
    )
    snapshot = result.scalar_one_or_none()
    if not snapshot:
        raise HTTPException(status_code=404, detail="No market data available yet. Run the agent first.")
    return MarketInsightResponse(
        snapshot_date=snapshot.snapshot_date,
        total_jobs_analyzed=snapshot.total_jobs_analyzed,
        top_skills=snapshot.top_skills,
        top_companies_hiring=snapshot.top_companies_hiring,
        emerging_roles=snapshot.emerging_roles,
        salary_data=snapshot.salary_data,
        by_work_mode=snapshot.by_work_mode,
    )


@analytics_router.get("/resume-performance")
async def get_resume_performance(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Which resume versions are getting the most responses."""
    from app.models.resume import Resume
    result = await db.execute(
        select(Resume)
        .where(Resume.user_id == current_user.id, Resume.times_used > 0)
        .order_by(desc(Resume.response_rate))
    )
    resumes = result.scalars().all()
    return [
        {
            "id": r.id,
            "name": r.name,
            "version": r.version,
            "times_used": r.times_used,
            "response_count": r.response_count,
            "response_rate": r.response_rate,
            "ats_score": r.ats_score,
        }
        for r in resumes
    ]


@analytics_router.get("/velocity")
async def get_application_velocity(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    days: int = Query(default=7, le=30),
):
    """Application velocity over time."""
    from datetime import timedelta
    start_date = datetime.now(timezone.utc) - timedelta(days=days)
    
    result = await db.execute(
        select(Application)
        .where(
            Application.user_id == current_user.id,
            Application.created_at >= start_date
        )
    )
    apps = result.scalars().all()
    
    # Group by date
    by_date: dict[str, int] = {}
    for app in apps:
        date_str = app.created_at.date().isoformat()
        by_date[date_str] = by_date.get(date_str, 0) + 1
    
    # Format for chart
    timeline = []
    for i in range(days):
        from datetime import date
        d = date.today() - timedelta(days=days - i - 1)
        timeline.append({
            "name": d.strftime("%a"),
            "applied": by_date.get(d.isoformat(), 0),
            "interviews": 0,
        })
    
    return timeline


@analytics_router.get("/funnel")
async def get_conversion_funnel(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Application conversion funnel."""
    result = await db.execute(
        select(Application.status, func.count(Application.id).label("count"))
        .where(Application.user_id == current_user.id)
        .group_by(Application.status)
    )
    counts = {row.status: row.count for row in result.all()}
    
    return {
        "applied": counts.get("applied", 0) + counts.get("pending_approval", 0) + counts.get("queued", 0) + counts.get("applying", 0),
        "viewed": counts.get("viewed", 0),
        "shortlisted": counts.get("shortlisted", 0),
        "interview": counts.get("interview_scheduled", 0) + counts.get("interview_completed", 0),
        "offer": counts.get("offer_received", 0) + counts.get("offer_accepted", 0),
    }


# ═══════════════════════════════════════════════════════════════════════════
#  Interviews API
# ═══════════════════════════════════════════════════════════════════════════

from app.models.interview import MockInterviewSession


@cover_letters_router.post("/interview/start")
async def start_mock_interview(
    job_role: str,
    interview_type: str = Query(default="technical"),
    current_user: User = Depends(get_current_user),
):
    """Start a new mock interview session."""
    from app.agents.tasks import start_mock_interview_task
    task = start_mock_interview_task.delay(current_user.id, job_role, interview_type)
    return {"session_id": task.id, "status": "started", "job_role": job_role}


@cover_letters_router.get("/interview/sessions")
async def list_interview_sessions(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List all mock interview sessions."""
    result = await db.execute(
        select(MockInterviewSession)
        .where(MockInterviewSession.user_id == current_user.id)
        .order_by(desc(MockInterviewSession.created_at))
    )
    sessions = result.scalars().all()
    return [
        {
            "id": s.id,
            "job_role": s.interview_id if s.interview_id else "General",
            "overall_score": s.overall_score,
            "duration_seconds": s.duration_seconds,
            "created_at": s.created_at.isoformat() if s.created_at else None,
        }
        for s in sessions
    ]