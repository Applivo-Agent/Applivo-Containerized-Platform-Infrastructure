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

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query, Request, Body, Response
from sqlalchemy import func, select, desc, delete, text, String, or_
from sqlalchemy.exc import ProgrammingError, IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from typing import List, Optional
from types import SimpleNamespace
from datetime import datetime, timezone, timedelta

from app.core.database import get_db
from app.api.routes.auth import get_current_user
from app.models.user import User
from app.models.application import Application, ApplicationEvent, ApplicationStatus, ApplicationMethod
from app.models.job import Job, JobAnalysis
from app.models.platform_message import PlatformMessage
from app.schemas import (
    ApplicationCreate, ApplicationOut, ApplicationStatusUpdate,
    ApplicationStats, MessageResponse, PaginatedResponse
)
from app.services.subscription_service import subscription_service

applications_router = APIRouter(prefix="/applications", tags=["Applications"])


async def require_active_subscription(current_user: User = Depends(get_current_user)) -> User:
    """Dependency that ensures user has an active paid subscription."""
    if current_user.is_superuser:
        return current_user
    
    sub = await subscription_service.get_active_subscription(current_user.id)
    if not sub or not sub.is_active():
        raise HTTPException(
            status_code=403,
            detail="Active subscription required for this feature. Please upgrade your plan."
        )
    return current_user


def _is_missing_column_error(exc: Exception, column_name: str) -> bool:
    msg = str(exc).lower()
    return "undefinedcolumnerror" in msg and column_name.lower() in msg


async def _ensure_jobs_user_id_column(db: AsyncSession) -> None:
    # Runtime self-heal for legacy databases missing jobs.user_id.
    await db.execute(text("ALTER TABLE IF EXISTS jobs ADD COLUMN IF NOT EXISTS user_id VARCHAR"))
    await db.execute(text("CREATE INDEX IF NOT EXISTS ix_jobs_user_id ON jobs (user_id)"))
    await db.commit()


async def _ensure_agent_tasks_user_id_column(db: AsyncSession) -> None:
    # Runtime self-heal for legacy databases missing agent_tasks.user_id.
    await db.execute(text("ALTER TABLE IF EXISTS agent_tasks ADD COLUMN IF NOT EXISTS user_id VARCHAR"))
    await db.execute(text("CREATE INDEX IF NOT EXISTS ix_agent_tasks_user_id ON agent_tasks (user_id)"))
    await db.commit()


async def _table_has_column(db: AsyncSession, table_name: str, column_name: str) -> bool:
    result = await db.execute(
        text(
            """
            SELECT 1
            FROM information_schema.columns
            WHERE table_schema = current_schema()
              AND table_name = :table_name
              AND column_name = :column_name
            LIMIT 1
            """
        ),
        {"table_name": table_name, "column_name": column_name},
    )
    return result.scalar_one_or_none() is not None


async def _table_has_column(db: AsyncSession, table_name: str, column_name: str) -> bool:
    result = await db.execute(
        text(
            """
            SELECT 1
            FROM information_schema.columns
            WHERE table_schema = current_schema()
              AND table_name = :table_name
              AND column_name = :column_name
            LIMIT 1
            """
        ),
        {"table_name": table_name, "column_name": column_name},
    )
    return result.scalar_one_or_none() is not None


def _agent_task_namespace_from_row(row) -> SimpleNamespace:
    return SimpleNamespace(**dict(row._mapping))


def _serialize_job(job: Job) -> dict:
    return {
        "id": job.id,
        "source": getattr(job.source, "value", job.source),
        "source_url": job.source_url,
        "title": job.title,
        "company_name": job.company_name,
        "company_logo_url": job.company_logo_url,
        "description_clean": job.description_clean,
        "location": job.location,
        "work_mode": getattr(job.work_mode, "value", job.work_mode),
        "job_type": getattr(job.job_type, "value", job.job_type),
        "experience_level": getattr(job.experience_level, "value", job.experience_level),
        "salary_min": job.salary_min,
        "salary_max": job.salary_max,
        "salary_currency": job.salary_currency,
        "posted_at": job.posted_at,
        "scraped_at": job.scraped_at,
        "status": getattr(job.status, "value", job.status),
        "is_active": job.is_active,
        "applicant_count": job.applicant_count,
        "easy_apply": job.easy_apply,
        "analysis": None,
        "created_at": job.created_at,
    }


def _serialize_application(app: Application, job: Optional[Job] = None) -> dict:
    return {
        "id": app.id,
        "user_id": app.user_id,
        "job_id": app.job_id,
        "resume_id": app.resume_id,
        "job": _serialize_job(job) if job is not None else None,
        "status": getattr(app.status, "value", app.status),
        "method": getattr(app.method, "value", app.method),
        "applied_at": app.applied_at,
        "viewed_at": app.viewed_at,
        "shortlisted_at": app.shortlisted_at,
        "offer_received_at": app.offer_received_at,
        "rejected_at": app.rejected_at,
        "match_score_at_apply": app.match_score_at_apply,
        "job_title_snapshot": app.job_title_snapshot,
        "company_snapshot": app.company_snapshot,
        "recruiter_name": app.recruiter_name,
        "recruiter_email": app.recruiter_email,
        "follow_up_status": getattr(app.follow_up_status, "value", app.follow_up_status),
        "follow_up_count": app.follow_up_count,
        "interview_date": app.interview_date,
        "interview_type": app.interview_type,
        "interview_notes": app.interview_notes,
        "offer_salary": app.offer_salary,
        "notes": app.notes,
        "is_starred": app.is_starred,
        "bot_error": app.bot_error,
        "retry_count": app.retry_count,
        "created_at": app.created_at,
        "updated_at": app.updated_at,
    }


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
        query = query.where(func.lower(Application.status.cast(String)) == status.lower())
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

    recruiter_responses = (await db.execute(
        select(func.count(PlatformMessage.id)).where(
            PlatformMessage.user_id == current_user.id,
            PlatformMessage.is_important == True,
            PlatformMessage.sender_name.is_not(None),
            PlatformMessage.sender_name != "",
            PlatformMessage.sender_name.notilike("You%")
        )
    )).scalar() or 0

    return ApplicationStats(
        total_sent=total_sent,
        pending_approval=counts.get(ApplicationStatus.PENDING_APPROVAL, 0),
        recruiter_responses=recruiter_responses,
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
            func.lower(Application.status.cast(String)) == ApplicationStatus.PENDING_APPROVAL.value.lower()
        )
    )
    pending_approval = result.scalar() or 0
    
    # Count queued (ready to apply)
    result = await db.execute(
        select(func.count(Application.id)).where(
            Application.user_id == current_user.id,
            func.lower(Application.status.cast(String)) == ApplicationStatus.QUEUED.value.lower()
        )
    )
    queued = result.scalar() or 0
    
    # Count applied today
    from datetime import datetime, timedelta
    today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    result = await db.execute(
        select(func.count(Application.id)).where(
            Application.user_id == current_user.id,
            func.lower(Application.status.cast(String)) == ApplicationStatus.APPLIED.value.lower(),
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
    response: Response,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_active_subscription),
):
    """Queue a new application (manual or bot-assisted). Requires active subscription."""
    # Verify job exists
    job_result = await db.execute(select(Job).where(Job.id == payload.job_id))
    job = job_result.scalar_one_or_none()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    def _normalize_application_method(method_str: str):
        from app.models.application import ApplicationMethod
        if not method_str:
            return ApplicationMethod.MANUAL
        s = method_str.strip().upper().replace('-', '_')
        try:
            return ApplicationMethod(s)
        except Exception:
            if "AUTO" in s:
                return ApplicationMethod.AUTO_BOT
            if "EASY" in s:
                return ApplicationMethod.EASY_APPLY
            if "EMAIL" in s:
                return ApplicationMethod.EMAIL
            return ApplicationMethod.MANUAL

    norm_method = _normalize_application_method(payload.method)

    # Idempotency guard: if already present, return existing row instead of 500.
    existing_result = await db.execute(
        select(Application).where(
            Application.user_id == current_user.id,
            Application.job_id == payload.job_id,
        )
    )
    existing_app = existing_result.scalar_one_or_none()
    if existing_app:
        response.status_code = 200
        return _serialize_application(existing_app, job)

    app = Application(
        user_id=current_user.id,
        job_id=payload.job_id,
        resume_id=payload.resume_id,
        cover_letter_id=payload.cover_letter_id,
        method=norm_method,
        notes=payload.notes,
        job_title_snapshot=job.title,
        company_snapshot=job.company_name,
        status=ApplicationStatus.PENDING_APPROVAL if norm_method == ApplicationMethod.AUTO_BOT else ApplicationStatus.APPLIED,
    )
    db.add(app)
    try:
        await db.flush()
    except IntegrityError:
        await db.rollback()
        existing_result = await db.execute(
            select(Application).where(
                Application.user_id == current_user.id,
                Application.job_id == payload.job_id,
            )
        )
        existing_app = existing_result.scalar_one_or_none()
        if existing_app:
            response.status_code = 200
            return _serialize_application(existing_app, job)
        raise HTTPException(status_code=409, detail="Application already exists")

    # Log creation event
    event = ApplicationEvent(
        application_id=app.id,
        event_type="application_created",
        to_status=app.status,
        triggered_by="user",
        details={"method": getattr(norm_method, 'value', str(norm_method))},
    )
    db.add(event)
    await db.commit()
    await db.refresh(app)

    # Trigger auto-apply bot if approved
    if (
        norm_method == ApplicationMethod.AUTO_BOT
        and current_user.profile
        and not current_user.profile.require_apply_approval
    ):
        background_tasks.add_task(_trigger_auto_apply, app.id)

    return _serialize_application(app, job)


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


@applications_router.patch("/{app_id}/status", response_model=ApplicationOut)
async def update_application_status(
    app_id: str,
    status: str = Body(embed=True),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update application status manually (Fixes 404 in UI)."""
    result = await db.execute(
        select(Application).where(Application.id == app_id, Application.user_id == current_user.id)
    )
    app = result.scalar_one_or_none()
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")
    
    # Standardize to uppercase for database compatibility
    try:
        new_status = ApplicationStatus(status.upper())
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid status: {status}")
    
    app.status = new_status
    await db.commit()
    await db.refresh(app)
    return app


@applications_router.delete("/{app_id}", response_model=MessageResponse)
async def delete_application(
    app_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete an application record."""
    result = await db.execute(
        select(Application).where(Application.id == app_id, Application.user_id == current_user.id)
    )
    app = result.scalar_one_or_none()
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")
    
    await db.delete(app)
    await db.commit()
    return MessageResponse(message="Application deleted successfully")


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
try:
    import magic
except ImportError:
    magic = None
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
    resumes = result.scalars().all()
    return resumes


@resumes_router.post("/upload", response_model=ResumeOut, status_code=201)
async def upload_resume(
    file: UploadFile = File(...),
    name: Optional[str] = Query(default=None),
    resume_type: str = Query(default="base"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Upload a PDF resume file. Limits to 3 active resumes."""
    # Enforce limit of 3
    result = await db.execute(
        select(func.count(Resume.id)).where(Resume.user_id == current_user.id, Resume.is_active == True)
    )
    count = result.scalar()
    if count >= 3:
        raise HTTPException(
            status_code=400, 
            detail="Maximum 3 resumes allowed. Please delete an existing resume to upload a new one."
        )

    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are accepted")
    
    # Use provided name or fallback to filename without extension
    if not name:
        name = file.filename.replace(".pdf", "") if file.filename else "Untitled Resume"

    from app.core.config import settings
    import uuid
    
    content = await file.read()
    
    if magic:
        try:
            mime_type = magic.from_buffer(content[:2048], mime=True)
            if mime_type != "application/pdf":
                raise HTTPException(
                    status_code=400, 
                    detail=f"Invalid file type ({mime_type}). Only PDF files are accepted."
                )
        except Exception as e:
            # Graceful fallback if libmagic error occurs
            pass
    
    # Check file size (max 10MB)
    MAX_SIZE = 10 * 1024 * 1024
    if len(content) > MAX_SIZE:
        raise HTTPException(status_code=413, detail="File too large (max 10MB)")
    file_name = f"{uuid.uuid4()}.pdf"
    file_path = settings.resumes_path / file_name

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


@resumes_router.get("/{resume_id}/file")
async def download_resume_file(
    resume_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Download the resume PDF file."""
    from fastapi.responses import FileResponse
    
    result = await db.execute(select(Resume).where(Resume.id == resume_id, Resume.user_id == current_user.id))
    resume = result.scalar_one_or_none()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
    
    if not resume.file_path or not Path(resume.file_path).exists():
        raise HTTPException(status_code=404, detail="File not found")
    
    return FileResponse(
        resume.file_path,
        media_type="application/pdf",
        filename=f"{resume.name or 'resume'}.pdf"
    )


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
    }


@resumes_router.delete("/{resume_id}", response_model=MessageResponse)
async def delete_resume(
    resume_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Soft delete a resume and ensure a primary one remains."""
    result = await db.execute(
        select(Resume).where(Resume.id == resume_id, Resume.user_id == current_user.id)
    )
    resume = result.scalar_one_or_none()
    
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
        
    if not resume.is_active:
        return MessageResponse(message="Resume already deleted")

    was_default = resume.is_default
    resume.is_active = False
    resume.is_default = False
    
    # If we deleted the primary, try to promote another one
    if was_default:
        res = await db.execute(
            select(Resume)
            .where(Resume.user_id == current_user.id, Resume.is_active == True)
            .order_by(desc(Resume.is_active), Resume.created_at)
        )
        new_default = res.scalars().first()
        if new_default:
            new_default.is_default = True
            
    await db.commit()
    return MessageResponse(message="Resume deleted successfully")


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
    result = service.set_custom_template(latex_code, template_name="custom", user_id=current_user.id)
    return result


@resumes_router.get("/latex/templates", response_model=dict)
async def list_latex_templates(
    current_user: User = Depends(get_current_user),
):
    """List all available LaTeX resume templates with current selection."""
    from app.services.overleaf_service import OverleafService
    service = OverleafService()
    available = service.list_available_templates()
    selected = service.get_current_template_name(current_user.id)
    available_names = {t.get("name") for t in available}
    if selected not in available_names:
        selected = "default"
    return {"available": available, "selected": selected}


@resumes_router.get("/latex/template", response_model=dict)
async def get_latex_template(
    current_user: User = Depends(get_current_user),
):
    """Get the current LaTeX template (default or custom)."""
    from app.services.overleaf_service import OverleafService
    service = OverleafService()
    template = service.get_current_template(current_user.id)
    return {
        "template": template,
        "is_custom": current_user.id in OverleafService._custom_templates_by_user
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
        result = service.set_custom_template(
            template,
            template_name=template_name,
            user_id=current_user.id,
            validate_required_sections=False,
        )
        if not result.get("success"):
            return {"success": False, "error": result.get("error", "Failed to select template")}
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
    import structlog
    logger = structlog.get_logger()
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
    today = datetime.now(timezone.utc).date()

    # Look for today's recent tasks. Fall back if legacy DB misses agent_tasks.user_id.
    try:
        result = await db.execute(
            select(AgentTask)
            .where(
                AgentTask.user_id == current_user.id,
                func.date(AgentTask.created_at) == today
            )
            .order_by(desc(AgentTask.created_at))
        )
    except ProgrammingError as exc:
        await db.rollback()
        if not _is_missing_column_error(exc, "agent_tasks.user_id"):
            raise
        try:
            await _ensure_agent_tasks_user_id_column(db)
            result = await db.execute(
                select(AgentTask)
                .where(
                    AgentTask.user_id == current_user.id,
                    func.date(AgentTask.created_at) == today,
                )
                .order_by(desc(AgentTask.created_at))
            )
        except Exception:
            await db.rollback()
            result = await db.execute(
                select(
                    AgentTask.id.label("id"),
                    AgentTask.task_type.label("task_type"),
                    AgentTask.status.label("status"),
                    AgentTask.result.label("result"),
                    AgentTask.error.label("error"),
                    AgentTask.created_at.label("created_at"),
                    AgentTask.completed_at.label("completed_at"),
                )
                .where(func.date(AgentTask.created_at) == today)
                .order_by(desc(AgentTask.created_at))
            )
    tasks_today = result.scalars().all() if result is not None else []

    # --- SELF-HEALING: Auto-clean stuck tasks ---
    # If a task is RUNNING but older than 2 minutes, it's likely a zombie
    two_mins_ago = datetime.now(timezone.utc) - timedelta(minutes=2)
    stuck_tasks = [t for t in tasks_today if t.status == AgentTaskStatus.RUNNING and t.started_at and t.started_at < two_mins_ago]
    
    if stuck_tasks:
        for t in stuck_tasks:
            t.status = AgentTaskStatus.FAILED
            t.error = "Task timed out or worker crashed"
            db.add(t)
        await db.commit()
        # Refresh the list
        result = await db.execute(
            select(AgentTask)
            .where(AgentTask.user_id == current_user.id, func.date(AgentTask.created_at) == today)
            .order_by(desc(AgentTask.created_at))
        )
        tasks_today = result.scalars().all()
    # ---------------------------------------------
    # Calculate metrics after self-healing
    running = [t for t in tasks_today if t.status == AgentTaskStatus.RUNNING]
    succeeded = [t for t in tasks_today if t.status == AgentTaskStatus.SUCCESS]
    failed = [t for t in tasks_today if t.status == AgentTaskStatus.FAILED]

    # Jobs found today
    from app.models.job import Job
    from sqlalchemy import cast, Date
    try:
        jobs_today = (await db.execute(
            select(func.count(Job.id)).where(
                Job.user_id == current_user.id,
                func.date(Job.scraped_at) == today,
            )
        )).scalar()
    except ProgrammingError as exc:
        await db.rollback()
        if not _is_missing_column_error(exc, "jobs.user_id"):
            raise
        try:
            await _ensure_jobs_user_id_column(db)
            jobs_today = (await db.execute(
                select(func.count(Job.id)).where(
                    Job.user_id == current_user.id,
                    func.date(Job.scraped_at) == today,
                )
            )).scalar()
        except Exception:
            await db.rollback()
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
        last_run=last_task.created_at if last_task else None,
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
        query = query.where(func.lower(AgentTask.status.cast(String)) == status.lower())
    result = await db.execute(query)
    return result.scalars().all()


async def run_manual_agent_task(task_type: str, user_id: str, payload: dict):
    """Background worker for manually triggered agent tasks."""
    import structlog, time
    from datetime import datetime, timezone
    from app.core.database import get_db_context
    from app.models.interview import AgentTask, AgentTaskStatus, AgentTaskType
    
    log = structlog.get_logger().bind(task_type=task_type, user_id=user_id)
    t0 = time.perf_counter()
    
    # 1. Create the AgentTask record
    # Map API task names to DB enum values expected by PostgreSQL.
    _TASK_TYPE_MAP = {
        "scrape_jobs": AgentTaskType.SCRAPE_JOBS,
        "analyze_jobs": AgentTaskType.ANALYZE_JOB,
        "analyze_and_queue": AgentTaskType.ANALYZE_AND_QUEUE,
        "queue_jobs": AgentTaskType.ANALYZE_AND_QUEUE,
        "apply_queued": AgentTaskType.APPLY_QUEUED,
    }
    db_task_type = _TASK_TYPE_MAP.get(task_type)
    if db_task_type is None:
        raise ValueError(f"Unsupported task_type for DB enum mapping: {task_type}")

    task_id = None
    async with get_db_context() as db:
        new_task = AgentTask(
            task_type=db_task_type,
            user_id=user_id,
            status=AgentTaskStatus.RUNNING,
            triggered_by="user",
            started_at=datetime.now(timezone.utc),
            payload=payload
        )
        db.add(new_task)
        await db.commit()
        await db.refresh(new_task)
        task_id = new_task.id
    
    log.info("Agent task started", task_id=task_id)
    
    try:
        result = {}
        # ── scrape_jobs ─────────────────────────────────────────────────────
        if task_type == "scrape_jobs":
            from app.agents.scrapers.internshala import InternshalaScraper
            res = await InternshalaScraper(user_id=user_id).run()
            result = {
                "jobs_found": res.get("jobs_found", 0),
                "jobs_new": res.get("jobs_new", 0)
            }

        # ── analyze_jobs (Pure Analysis) ──────────────────────────────────
        elif task_type == "analyze_jobs":
            from app.services.job_analyzer import JobAnalyzerService
            from app.services.analyze_budget_service import analyze_budget_service

            analyzer = JobAnalyzerService()
            budget = await analyze_budget_service.get_analyze_budget(user_id)
            if not budget.get("allowed"):
                result = {
                    "analyzed": 0,
                    "tokens_used": 0,
                    "budget_exhausted": True,
                    "budget_reason": budget.get("reason") or "Analyze token budget exhausted",
                }
            else:
                run_limit = None if budget.get("is_unlimited") else int(budget.get("run_limit_tokens", 0))
                monthly_remaining = None if budget.get("is_unlimited") else int(budget.get("remaining_month_tokens", 0))
                res = await analyzer.analyze_user_new_or_unanalyzed(
                    user_id=user_id,
                    limit=100,
                    max_run_tokens=run_limit,
                    max_month_tokens_remaining=monthly_remaining,
                )
                result = {
                    **res,
                    "remaining_month_tokens": budget.get("remaining_month_tokens"),
                }

        # ── queue_jobs (Staging Applications) ──────────────────────────────
        elif task_type == "queue_jobs":
            from app.models.job import Job, JobAnalysis
            from app.models.application import Application, ApplicationStatus
            from app.models.user import UserProfile
            from app.core.config import settings

            profile = None
            threshold = settings.AUTO_APPLY_MATCH_THRESHOLD
            queued_count = 0
            async with get_db_context() as db:
                profile = (
                    await db.execute(
                        select(UserProfile).where(UserProfile.user_id == user_id)
                    )
                ).scalar_one_or_none()

                if profile and profile.auto_apply_threshold is not None:
                    threshold = profile.auto_apply_threshold

                # Find jobs already associated with an application
                existing_job_ids = {
                    row[0] for row in (await db.execute(
                        select(Application.job_id).where(Application.user_id == user_id)
                    )).all()
                }
                
                # Fetch candidate jobs:
                # 1. Not already applied
                # 2. MUST be for this user
                # 3. (EITHER high match score OR NO analysis at all) -> This is the user's fallback requirement
                query = (
                    select(Job)
                    .outerjoin(JobAnalysis, Job.id == JobAnalysis.job_id)
                    .where(
                        Job.is_active == True,
                        Job.user_id == user_id,
                        ~Job.id.in_(existing_job_ids)
                    )
                    .where(
                        (JobAnalysis.match_score >= threshold) | (JobAnalysis.id == None)
                    )
                    .limit(100)
                )

                new_jobs = (await db.execute(query)).scalars().all()

                for job in new_jobs:
                    try:
                        async with db.begin_nested():
                            db.add(Application(
                                user_id=user_id,
                                job_id=job.id,
                                status=ApplicationStatus.QUEUED,
                                job_title_snapshot=job.title,
                                company_snapshot=job.company_name,
                            ))
                            await db.flush()
                        queued_count += 1
                        existing_job_ids.add(job.id)
                    except IntegrityError:
                        # Concurrent writer already inserted this (user_id, job_id); skip safely.
                        continue
                await db.commit()
            result = {"queued": queued_count, "threshold_used": threshold}

        # ── analyze_and_queue (Legacy/Combined) ─────────────────────────────
        elif task_type == "analyze_and_queue":
            from app.services.job_analyzer import JobAnalyzerService
            from app.models.job import Job, JobAnalysis
            from app.models.application import Application, ApplicationStatus
            from app.core.config import settings
            from app.services.analyze_budget_service import analyze_budget_service

            analyzer = JobAnalyzerService()
            budget = await analyze_budget_service.get_analyze_budget(user_id)
            if not budget.get("allowed"):
                analyzed = 0
                analysis_result = {
                    "analyzed": 0,
                    "tokens_used": 0,
                    "budget_exhausted": True,
                    "budget_reason": budget.get("reason") or "Analyze token budget exhausted",
                }
            else:
                run_limit = None if budget.get("is_unlimited") else int(budget.get("run_limit_tokens", 0))
                monthly_remaining = None if budget.get("is_unlimited") else int(budget.get("remaining_month_tokens", 0))
                analysis_result = await analyzer.analyze_user_new_or_unanalyzed(
                    user_id=user_id,
                    limit=100,
                    max_run_tokens=run_limit,
                    max_month_tokens_remaining=monthly_remaining,
                )
                analyzed = analysis_result.get("analyzed", 0)

            threshold = settings.AUTO_APPLY_MATCH_THRESHOLD
            queued_count = 0
            async with get_db_context() as db:
                existing_job_ids = {
                    row[0] for row in (await db.execute(
                        select(Application.job_id).where(Application.user_id == user_id)
                    )).all()
                }
                new_jobs = (await db.execute(
                    select(Job).where(
                        Job.is_active == True,
                        Job.user_id == user_id,
                        ~Job.id.in_(existing_job_ids),
                    ).outerjoin(
                        JobAnalysis, Job.id == JobAnalysis.job_id
                    ).where(
                        (JobAnalysis.match_score >= threshold) | (JobAnalysis.match_score == None)
                    ).limit(100)
                )).scalars().all()

                for job in new_jobs:
                    try:
                        async with db.begin_nested():
                            db.add(Application(
                                user_id=user_id,
                                job_id=job.id,
                                status=ApplicationStatus.QUEUED,
                                job_title_snapshot=job.title,
                                company_snapshot=job.company_name,
                            ))
                            await db.flush()
                        queued_count += 1
                        existing_job_ids.add(job.id)
                    except IntegrityError:
                        # Concurrent writer already inserted this (user_id, job_id); skip safely.
                        continue
                await db.commit()
            result = {
                "analyzed": analyzed,
                "queued": queued_count,
                "tokens_used": analysis_result.get("tokens_used", 0),
                "budget_exhausted": analysis_result.get("budget_exhausted", False),
                "budget_reason": analysis_result.get("budget_reason"),
                "remaining_month_tokens": budget.get("remaining_month_tokens"),
                "monthly_limit_tokens": budget.get("monthly_limit_tokens"),
                "run_limit_tokens": budget.get("run_limit_tokens"),
            }

        # ── apply_queued (Staging Applications) ──────────────────────────────
        elif task_type == "apply_queued":
            from app.celery_tasks import apply_queued_batch

            async_result = apply_queued_batch.apply_async(args=[user_id], queue="apply")
            result = {
                "queued": True,
                "celery_task_id": async_result.id,
                "message": "apply_queued dispatched to browser worker",
            }

        # Update task as success
        elapsed = round(time.perf_counter() - t0, 1)
        async with get_db_context() as db:
            task = await db.get(AgentTask, task_id)
            if task:
                task.status = AgentTaskStatus.SUCCESS
                task.completed_at = datetime.now(timezone.utc)
                task.duration_ms = int(elapsed * 1000)
                task.result = result
            await db.commit()
        log.info("Agent task complete", task_id=task_id, result=result)

    except Exception as e:
        log.error("Agent task failed", task_id=task_id, error=str(e))
        async with get_db_context() as db:
            task = await db.get(AgentTask, task_id)
            if task:
                task.status = AgentTaskStatus.FAILED
                task.completed_at = datetime.now(timezone.utc)
                task.error = str(e)
            await db.commit()


@agent_router.post("/run")
async def trigger_agent_manually(
    payload: ManualAgentRunRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
):
    """
    Manually trigger an agent task in the background.
    """
    SUPPORTED_TASKS = {"scrape_jobs", "apply_queued", "analyze_and_queue", "analyze_jobs", "queue_jobs"}
    task_type = payload.task_type
    
    if task_type not in SUPPORTED_TASKS:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown task type: {task_type}. Supported: {sorted(SUPPORTED_TASKS)}",
        )

    if not current_user.is_superuser:
        from app.services.subscription_service import SubscriptionService
        sub = await SubscriptionService().get_active_subscription(current_user.id)
        if not sub or not sub.is_active():
            raise HTTPException(
                status_code=403,
                detail="Active subscription required. Please subscribe at /subscription",
            )

    # Launch background task properly detached from the request lifecycle
    import asyncio
    asyncio.create_task(
        run_manual_agent_task(
            task_type, 
            current_user.id, 
            payload.model_dump()
        )
    )

    return {"message": f"Task {task_type} started in background. Monitor progress on dashboard."}


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
            response=f"⚠️ You have only {remaining} AI credits remaining this month. Consider upgrading at /subscription for a higher monthly limit.",
            actions_taken=[]
        )
    
    # Process the chat
    from app.services.ai_assistant import CareerAssistant, AI_Persona
    assistant = CareerAssistant(db=db, user=current_user)
    
    # Set persona if provided
    persona = None
    if payload.persona:
        try:
            persona = AI_Persona(payload.persona)
            assistant.set_persona(persona)
        except ValueError:
            pass  # Use default persona
    
    response = await assistant.chat(
        message=payload.message,
        history=payload.conversation_history,
        persona=persona,
    )
    
    # Save chat messages to history
    from app.models.chat_message import ChatMessage
    from datetime import datetime, timezone
    import uuid
    
    user_msg = ChatMessage(
        id=str(uuid.uuid4()),
        user_id=current_user.id,
        role="user",
        content=payload.message,
        created_at=datetime.now(timezone.utc)
    )
    assistant_msg = ChatMessage(
        id=str(uuid.uuid4()),
        user_id=current_user.id,
        role="assistant",
        content=response.response,
        created_at=datetime.now(timezone.utc)
    )
    db.add(user_msg)
    db.add(assistant_msg)
    await db.commit()
    
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


# Chat history endpoints
from app.models.chat_message import ChatMessage

@chat_router.get("/history")
async def get_chat_history(
    limit: int = Query(50, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get user's chat history."""
    result = await db.execute(
        select(ChatMessage)
        .where(ChatMessage.user_id == current_user.id)
        .order_by(desc(ChatMessage.created_at))
        .limit(limit)
    )
    messages = result.scalars().all()
    return [
        {"id": m.id, "role": m.role, "content": m.content, "created_at": m.created_at.isoformat() if m.created_at else None}
        for m in messages
    ]


@chat_router.delete("/history")
async def clear_chat_history(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Clear user's chat history."""
    await db.execute(
        delete(ChatMessage).where(ChatMessage.user_id == current_user.id)
    )
    await db.commit()
    return {"message": "Chat history cleared"}


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
    """Full dashboard data with correct aggregations."""
    from app.models.application import ApplicationStatus
    from datetime import datetime, timezone, timedelta

    # 1. Get status counts for ALL applications of this user
    # This is much more accurate than counting from a limited set of recent apps.
    status_query = await db.execute(
        select(Application.status, func.count(Application.id))
        .where(Application.user_id == current_user.id)
        .group_by(Application.status)
    )
    res = status_query.all()
    counts = {row[0]: row[1] for row in res}
    
    # Standardize counts (using Enum members as keys)
    applied_count = counts.get(ApplicationStatus.APPLIED, 0)
    viewed = counts.get(ApplicationStatus.VIEWED, 0)
    shortlisted = counts.get(ApplicationStatus.SHORTLISTED, 0)
    interviews = (
        counts.get(ApplicationStatus.INTERVIEW_SCHEDULED, 0) + 
        counts.get(ApplicationStatus.INTERVIEW_COMPLETED, 0)
    )
    offers = (
        counts.get(ApplicationStatus.OFFER_RECEIVED, 0) + 
        counts.get(ApplicationStatus.OFFER_ACCEPTED, 0)
    )
    pending = counts.get(ApplicationStatus.PENDING_APPROVAL, 0)
    rejected = counts.get(ApplicationStatus.REJECTED, 0)
    
    # 2. Total all-time ACTUALLY APPLIED applications (excludes queued/pending/failed)
    # Success statuses that count towards the 'Applied' metric
    APPLIED_STATUSES = [
        ApplicationStatus.APPLIED,
        ApplicationStatus.VIEWED,
        ApplicationStatus.SHORTLISTED,
        ApplicationStatus.INTERVIEW_SCHEDULED,
        ApplicationStatus.INTERVIEW_COMPLETED,
        ApplicationStatus.OFFER_RECEIVED,
        ApplicationStatus.OFFER_ACCEPTED,
        ApplicationStatus.REJECTED,
    ]
    total_apps_result = await db.execute(
        select(func.count(Application.id)).where(
            Application.user_id == current_user.id,
            Application.status.in_(APPLIED_STATUSES)
        )
    )
    total_apps = total_apps_result.scalar() or 0

    # 3. Applications sent TODAY (only actually applied ones)
    today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    apps_today_result = await db.execute(
        select(func.count(Application.id)).where(
            Application.user_id == current_user.id,
            Application.applied_at >= today_start,
            Application.status.in_(APPLIED_STATUSES)
        )
    )
    apps_today = apps_today_result.scalar() or 0

    # 4. Job counts — scoped to this user
    today_date = datetime.now(timezone.utc).date()
    has_job_user_scope = await _table_has_column(db, "jobs", "user_id")
    if has_job_user_scope:
        total_jobs = (await db.execute(
            select(func.count(Job.id)).where(Job.user_id == current_user.id)
        )).scalar() or 0
        jobs_today = (await db.execute(
            select(func.count(Job.id)).where(
                Job.user_id == current_user.id,
                func.date(Job.scraped_at) == today_date
            )
        )).scalar() or 0

        high_match = (await db.execute(
            select(func.count(JobAnalysis.id))
            .outerjoin(Job, JobAnalysis.job_id == Job.id)
            .where(Job.user_id == current_user.id, JobAnalysis.match_score >= 75)
        )).scalar() or 0
    else:
        total_jobs = (await db.execute(
            select(func.count())
            .select_from(select(Job.id).where(Job.is_active == True).subquery())
        )).scalar() or 0
        jobs_today = (await db.execute(
            select(func.count())
            .select_from(select(Job.id).where(Job.is_active == True, func.date(Job.scraped_at) == today_date).subquery())
        )).scalar() or 0
        high_match = (await db.execute(
            select(func.count())
            .select_from(
                select(JobAnalysis.id)
                .outerjoin(Job, JobAnalysis.job_id == Job.id)
                .where(Job.is_active == True, JobAnalysis.match_score >= 75)
                .subquery()
            )
        )).scalar() or 0

    # 5. Response Rate
    # (Viewed + Shortlisted + Interview + Offer) / Total Applied
    positive_signals = viewed + shortlisted + interviews + offers
    response_rate = round((positive_signals / applied_count * 100), 1) if applied_count > 0 else 0.0

    # 6. Recent activity (the only part that stays limited)
    apps_result = await db.execute(
        select(Application)
        .options(selectinload(Application.job))
        .where(Application.user_id == current_user.id)
        .order_by(desc(Application.created_at))
        .limit(10)
    )
    recent_apps = apps_result.scalars().all()
    
    recent_activity = [
        {
            "id": str(a.id),
            "job_title": a.job_title_snapshot or (a.job.title if a.job else ""),
            "company": a.company_snapshot or (a.job.company_name if a.job else ""),
            "status": a.status.value if hasattr(a.status, 'value') else str(a.status),
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
        applications_today=apps_today,
        pending_approval=pending,
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
    from datetime import timedelta, date
    from app.models.application import ApplicationStatus
    
    # Compute start date based on days parameter
    start_date = datetime.now(timezone.utc) - timedelta(days=days)
    
    APPLIED_STATUSES = [
        ApplicationStatus.APPLIED, ApplicationStatus.VIEWED, ApplicationStatus.SHORTLISTED,
        ApplicationStatus.INTERVIEW_SCHEDULED, ApplicationStatus.INTERVIEW_COMPLETED,
        ApplicationStatus.OFFER_RECEIVED, ApplicationStatus.OFFER_ACCEPTED, ApplicationStatus.REJECTED
    ]
    
    result = await db.execute(
        select(Application)
        .where(
            Application.user_id == current_user.id,
            Application.status.in_(APPLIED_STATUSES),
            or_(
                Application.applied_at >= start_date,
                Application.created_at >= start_date
            )
        )
    )
    apps = result.scalars().all()
    
    # Group by date
    by_date: dict[str, int] = {}
    for app in apps:
        # Prefer applied_at, fallback to created_at if same-day application
        target_date = app.applied_at or app.created_at
        if target_date:
            date_str = target_date.date().isoformat()
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
    from app.models.application import ApplicationStatus
    result = await db.execute(
        select(Application.status, func.count(Application.id).label("count"))
        .where(Application.user_id == current_user.id)
        .group_by(Application.status)
    )
    # Ensure keys are the enum values (uppercase)
    counts = {row.status: row.count for row in result.all()}
    
    # Return as array for frontend chart compatibility
    return [
        {
            "name": "Applied", 
            "value": counts.get(ApplicationStatus.APPLIED, 0) + 
                     counts.get(ApplicationStatus.PENDING_APPROVAL, 0) + 
                     counts.get(ApplicationStatus.QUEUED, 0) + 
                     counts.get(ApplicationStatus.APPLYING, 0)
        },
        {"name": "Viewed", "value": counts.get(ApplicationStatus.VIEWED, 0)},
        {"name": "Shortlisted", "value": counts.get(ApplicationStatus.SHORTLISTED, 0)},
        {"name": "Interview", "value": counts.get(ApplicationStatus.INTERVIEW_SCHEDULED, 0) + counts.get(ApplicationStatus.INTERVIEW_COMPLETED, 0)},
        {"name": "Offer", "value": counts.get(ApplicationStatus.OFFER_RECEIVED, 0) + counts.get(ApplicationStatus.OFFER_ACCEPTED, 0)},
    ]


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