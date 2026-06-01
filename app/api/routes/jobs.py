"""
app/api/routes/jobs.py
───────────────────────
Job discovery, filtering, and analysis endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status, BackgroundTasks
from sqlalchemy import func, select, and_, or_, desc, asc, text, cast, String
from sqlalchemy.exc import ProgrammingError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from typing import List, Optional
from types import SimpleNamespace

from app.core.database import get_db
from app.api.routes.auth import get_current_user
from app.models.user import User
from app.models.job import Job, JobAnalysis, JobStatus, JobSource
from app.schemas import JobOut, JobCreate, JobFilter, PaginatedResponse, MessageResponse
from app.services.subscription_service import subscription_service

router = APIRouter(prefix="/jobs", tags=["Jobs"])


async def require_active_subscription(current_user: User = Depends(get_current_user)) -> User:
    """Dependency that ensures user has an active paid subscription."""
    if current_user.is_superuser:
        return current_user
    
    sub = await subscription_service.get_active_subscription(current_user.id)
    if not sub or not sub.is_active():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Active subscription required for this feature. Please upgrade your plan."
        )
    return current_user


def _is_missing_column_error(exc: Exception, column_name: str) -> bool:
    msg = str(exc).lower()
    return "undefinedcolumnerror" in msg and column_name.lower() in msg


async def _ensure_jobs_user_id_column(db: AsyncSession) -> None:
    # Runtime self-heal for drifted DBs where jobs.user_id is missing.
    await db.execute(text("ALTER TABLE IF EXISTS jobs ADD COLUMN IF NOT EXISTS user_id VARCHAR"))
    await db.execute(text("CREATE INDEX IF NOT EXISTS ix_jobs_user_id ON jobs (user_id)"))
    await db.commit()


async def _jobs_user_id_exists(db: AsyncSession) -> bool:
    result = await db.execute(
        text(
            """
            SELECT 1
            FROM information_schema.columns
            WHERE table_schema = current_schema()
              AND table_name = 'jobs'
              AND column_name = 'user_id'
            LIMIT 1
            """
        )
    )
    return result.scalar_one_or_none() is not None


def _job_namespace_from_row(row) -> SimpleNamespace:
    data = dict(row._mapping)
    data.setdefault("analysis", None)
    return SimpleNamespace(**data)


def _normalize_job_source_filter(value: Optional[str]) -> Optional[JobSource]:
    if value is None:
        return None
    normalized = str(value).strip().upper().replace("-", "_")
    try:
        return JobSource[normalized]
    except KeyError:
        return None


def _normalize_job_status_filter(value: Optional[str]) -> Optional[JobStatus]:
    if value is None:
        return None
    normalized = str(value).strip().upper().replace("-", "_")
    try:
        return JobStatus[normalized]
    except KeyError:
        return None


@router.get("/count")
async def get_job_count(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get job count statistics for the current user."""
    from datetime import datetime, timedelta
    
    include_user_scope = await _jobs_user_id_exists(db)
    if not include_user_scope:
        try:
            await _ensure_jobs_user_id_column(db)
            include_user_scope = await _jobs_user_id_exists(db)
        except Exception:
            await db.rollback()
            include_user_scope = False

    # Total active jobs
    total_filters = [Job.is_active == True]
    if include_user_scope:
        total_filters.append(Job.user_id == current_user.id)
    result = await db.execute(select(func.count(Job.id)).where(*total_filters))
    total = result.scalar() or 0
    
    # New jobs today
    today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    today_filters = [Job.is_active == True, Job.created_at >= today_start]
    if include_user_scope:
        today_filters.append(Job.user_id == current_user.id)
    result = await db.execute(select(func.count(Job.id)).where(*today_filters))
    new_today = result.scalar() or 0
    
    # Jobs with match score >= 75 (join with JobAnalysis)
    matching_filters = [Job.is_active == True, JobAnalysis.match_score >= 75]
    if include_user_scope:
        matching_filters.append(Job.user_id == current_user.id)
    result = await db.execute(
        select(func.count(Job.id))
        .join(JobAnalysis, Job.id == JobAnalysis.job_id)
        .where(*matching_filters)
    )
    matching = result.scalar() or 0
    
    return {
        "total": total,
        "newToday": new_today,
        "matching": matching
    }


@router.post("/scrape")
async def trigger_scrape(
    source: Optional[str] = Query(default=None, description="Specific source to scrape: internshala, remoteok, indeed, linkedin"),
    current_user: User = Depends(require_active_subscription),
):
    """Trigger the job scraping agent to run for the current user. Requires active subscription."""
    import structlog
    log = structlog.get_logger()

    effective_source = source or "internshala"
    effective_source_lower = str(effective_source).strip().lower()
    log.info("Starting scrape", source=effective_source, user_id=current_user.id)

    import time
    t0 = time.perf_counter()
    
    try:
        jobs_found = 0
        jobs_new = 0
        jobs_duplicate = 0
        notes = []

        if effective_source_lower in ("internshala", "all"):
            from app.agents.scrapers.internshala import IntershalaScraper
            # Pass user_id so jobs are stored under this user's account
            result = await IntershalaScraper(user_id=current_user.id).run()
            jobs_found = result.get("jobs_found", 0)
            jobs_new = result.get("jobs_new", 0)
            jobs_duplicate = result.get("jobs_duplicate", 0)

            elapsed = round(time.perf_counter() - t0, 1)
            log.info("Internshala scrape complete",
                     user_id=current_user.id, jobs_found=jobs_found, jobs_new=jobs_new, duration_seconds=elapsed)

            if jobs_found == 0:
                notes.append(
                    "Internshala returned 0 jobs. "
                    "Connect your Internshala session in the Session tab "
                    "so the scraper can use your login cookies."
                )

        elapsed = round(time.perf_counter() - t0, 1)
        msg = f"Scraping complete — {jobs_found} job(s) found, {jobs_new} new in {elapsed}s."
        if notes:
            msg += " Note: " + " ".join(notes)

        return {
            "message": msg,
            "duration_seconds": elapsed,
            "jobs_found": jobs_found,
            "jobs_new": jobs_new,
            "jobs_duplicate": jobs_duplicate,
            "source": effective_source_lower,
        }

    except Exception as e:
        import traceback
        tb = traceback.format_exc()
        log.error("Scrape failed", source=effective_source, error=str(e), traceback=tb)
        raise HTTPException(
            status_code=500,
            detail=f"Scrape failed: {type(e).__name__}: {str(e)}\n\nTraceback:\n{tb}"
        )


@router.get("", response_model=PaginatedResponse)
async def list_jobs(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    source: Optional[str] = Query(default=None),
    job_type: Optional[str] = Query(default=None),
    work_mode: Optional[str] = Query(default=None),
    min_match_score: Optional[float] = Query(default=None, ge=0, le=100),
    keyword: Optional[str] = Query(default=None),
    status: Optional[str] = Query(default=None),
    sort_by: str = Query(default="match_score"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    List jobs belonging to the current user with filtering, sorting, and pagination.
    Joins with JobAnalysis to include match scores.
    """
    # ── Redis Caching ──────────────────────────────────────────
    from app.services.cache_service import cache_service
    import hashlib
    
    # Generate unique cache key based on user and filtering parameters
    cache_params = f"{current_user.id}:{page}:{page_size}:{source}:{job_type}:{work_mode}:{min_match_score}:{keyword}:{status}:{sort_by}"
    cache_key = f"jobs:list:{hashlib.md5(cache_params.encode()).hexdigest()}"
    
    cached_data = await cache_service.get(cache_key)
    if cached_data:
        return PaginatedResponse.model_validate(cached_data)
    # ─────────────────────────────────────────────────────────────

    normalized_source = _normalize_job_source_filter(source)

    include_user_scope = await _jobs_user_id_exists(db)
    if not include_user_scope:
        try:
            await _ensure_jobs_user_id_column(db)
            include_user_scope = await _jobs_user_id_exists(db)
        except Exception:
            await db.rollback()
            include_user_scope = False

    if not include_user_scope:
        explicit_query = (
            select(
                Job.id.label("id"),
                Job.source.label("source"),
                Job.source_url.label("source_url"),
                Job.title.label("title"),
                Job.company_name.label("company_name"),
                Job.company_logo_url.label("company_logo_url"),
                Job.description_clean.label("description_clean"),
                Job.location.label("location"),
                Job.work_mode.label("work_mode"),
                Job.job_type.label("job_type"),
                Job.experience_level.label("experience_level"),
                Job.salary_min.label("salary_min"),
                Job.salary_max.label("salary_max"),
                Job.salary_currency.label("salary_currency"),
                Job.posted_at.label("posted_at"),
                Job.scraped_at.label("scraped_at"),
                Job.status.label("status"),
                Job.is_active.label("is_active"),
                Job.applicant_count.label("applicant_count"),
                Job.easy_apply.label("easy_apply"),
                Job.created_at.label("created_at"),
            )
            .outerjoin(JobAnalysis, Job.id == JobAnalysis.job_id)
        )

        if normalized_source:
            explicit_query = explicit_query.where(cast(Job.source, String) == normalized_source.value)
        if job_type:
            explicit_query = explicit_query.where(Job.job_type == job_type)
        if work_mode:
            explicit_query = explicit_query.where(Job.work_mode == work_mode)
        if min_match_score is not None:
            explicit_query = explicit_query.where(JobAnalysis.match_score >= min_match_score)
        if keyword:
            explicit_query = explicit_query.where(
                or_(
                    Job.title.ilike(f"%{keyword}%"),
                    Job.company_name.ilike(f"%{keyword}%"),
                    Job.description_clean.ilike(f"%{keyword}%"),
                )
            )
        if status:
            explicit_query = explicit_query.where(func.lower(cast(Job.status, String)) == status.lower())

        sort_col_map = {
            "match_score": JobAnalysis.match_score,
            "priority_score": JobAnalysis.priority_score,
            "posted_at": Job.posted_at,
            "created_at": Job.created_at,
        }
        sort_col = sort_col_map.get(sort_by, JobAnalysis.match_score)
        explicit_query = explicit_query.order_by(desc(sort_col).nulls_last())

        count_query = select(func.count()).select_from(explicit_query.subquery())
        total = (await db.execute(count_query)).scalar() or 0
        offset = (page - 1) * page_size
        result = await db.execute(explicit_query.offset(offset).limit(page_size))
        jobs = [JobOut.model_validate(_job_namespace_from_row(row)) for row in result.all()]

        response = PaginatedResponse(
            total=total,
            page=page,
            page_size=page_size,
            pages=-(-total // page_size) if total else 0,
            items=jobs,
        )
        await cache_service.set(cache_key, response.model_dump(mode='json'), ttl=60)
        return response

    base_filters = [Job.is_active == True]
    if include_user_scope:
        base_filters.append(Job.user_id == current_user.id)

    query = (
        select(Job)
        .outerjoin(JobAnalysis, Job.id == JobAnalysis.job_id)
        .options(selectinload(Job.analysis))
        .where(*base_filters)
    )

    if normalized_source:
        query = query.where(cast(Job.source, String) == normalized_source.value)
    if job_type:
        query = query.where(Job.job_type == job_type)
    if work_mode:
        query = query.where(Job.work_mode == work_mode)
    if min_match_score is not None:
        query = query.where(JobAnalysis.match_score >= min_match_score)
    if keyword:
        query = query.where(
            or_(
                Job.title.ilike(f"%{keyword}%"),
                Job.company_name.ilike(f"%{keyword}%"),
                Job.description_clean.ilike(f"%{keyword}%"),
            )
        )
    normalized_status = _normalize_job_status_filter(status)
    if normalized_status:
        query = query.where(Job.status == normalized_status)

    # Sorting
    sort_col_map = {
        "match_score": JobAnalysis.match_score,
        "priority_score": JobAnalysis.priority_score,
        "posted_at": Job.posted_at,
        "created_at": Job.created_at,
    }
    sort_col = sort_col_map.get(sort_by, JobAnalysis.match_score)
    query = query.order_by(desc(sort_col).nulls_last())

    try:
        # Count
        count_query = select(func.count()).select_from(query.subquery())
        total = (await db.execute(count_query)).scalar() or 0

        # Paginate
        offset = (page - 1) * page_size
        query = query.offset(offset).limit(page_size)
        result = await db.execute(query)
        jobs = result.scalars().all()

        response = PaginatedResponse(
            total=total,
            page=page,
            page_size=page_size,
            pages=-(-total // page_size) if total else 0,
            items=[JobOut.model_validate(j) for j in jobs],
        )
    except ProgrammingError as exc:
        await db.rollback()
        if not _is_missing_column_error(exc, "jobs.user_id"):
            raise

        explicit_query = (
            select(
                Job.id.label("id"),
                Job.source.label("source"),
                Job.source_url.label("source_url"),
                Job.title.label("title"),
                Job.company_name.label("company_name"),
                Job.company_logo_url.label("company_logo_url"),
                Job.description_clean.label("description_clean"),
                Job.location.label("location"),
                Job.work_mode.label("work_mode"),
                Job.job_type.label("job_type"),
                Job.experience_level.label("experience_level"),
                Job.salary_min.label("salary_min"),
                Job.salary_max.label("salary_max"),
                Job.salary_currency.label("salary_currency"),
                Job.posted_at.label("posted_at"),
                Job.scraped_at.label("scraped_at"),
                Job.status.label("status"),
                Job.is_active.label("is_active"),
                Job.applicant_count.label("applicant_count"),
                Job.easy_apply.label("easy_apply"),
                Job.created_at.label("created_at"),
            )
            .outerjoin(JobAnalysis, Job.id == JobAnalysis.job_id)
        )
        if normalized_source:
            explicit_query = explicit_query.where(cast(Job.source, String) == normalized_source.value)
        if job_type:
            explicit_query = explicit_query.where(Job.job_type == job_type)
        if work_mode:
            explicit_query = explicit_query.where(Job.work_mode == work_mode)
        if min_match_score is not None:
            explicit_query = explicit_query.where(JobAnalysis.match_score >= min_match_score)
        if keyword:
            explicit_query = explicit_query.where(
                or_(
                    Job.title.ilike(f"%{keyword}%"),
                    Job.company_name.ilike(f"%{keyword}%"),
                    Job.description_clean.ilike(f"%{keyword}%"),
                )
            )
        normalized_status = _normalize_job_status_filter(status)
        if normalized_status:
            explicit_query = explicit_query.where(Job.status == normalized_status)

        sort_col_map = {
            "match_score": JobAnalysis.match_score,
            "priority_score": JobAnalysis.priority_score,
            "posted_at": Job.posted_at,
            "created_at": Job.created_at,
        }
        sort_col = sort_col_map.get(sort_by, JobAnalysis.match_score)
        explicit_query = explicit_query.order_by(desc(sort_col).nulls_last())

        total = (await db.execute(select(func.count()).select_from(explicit_query.subquery()))).scalar() or 0
        offset = (page - 1) * page_size
        result = await db.execute(explicit_query.offset(offset).limit(page_size))
        jobs = [JobOut.model_validate(_job_namespace_from_row(row)) for row in result.all()]
        response = PaginatedResponse(
            total=total,
            page=page,
            page_size=page_size,
            pages=-(-total // page_size) if total else 0,
            items=jobs,
        )

    # Cache the response for 60 seconds
    await cache_service.set(cache_key, response.model_dump(mode='json'), ttl=60)

    return response


@router.get("/{job_id}", response_model=JobOut)
async def get_job(
    job_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        result = await db.execute(
            select(Job).options(selectinload(Job.analysis)).where(
                Job.id == job_id,
                Job.user_id == current_user.id
            )
        )
    except ProgrammingError as exc:
        await db.rollback()
        if not _is_missing_column_error(exc, "jobs.user_id"):
            raise
        try:
            await _ensure_jobs_user_id_column(db)
            result = await db.execute(
                select(Job).options(selectinload(Job.analysis)).where(
                    Job.id == job_id,
                    Job.user_id == current_user.id,
                )
            )
        except Exception:
            await db.rollback()
            fallback = await db.execute(
                select(
                    Job.id.label("id"),
                    Job.source.label("source"),
                    Job.source_url.label("source_url"),
                    Job.title.label("title"),
                    Job.company_name.label("company_name"),
                    Job.company_logo_url.label("company_logo_url"),
                    Job.description_clean.label("description_clean"),
                    Job.location.label("location"),
                    Job.work_mode.label("work_mode"),
                    Job.job_type.label("job_type"),
                    Job.experience_level.label("experience_level"),
                    Job.salary_min.label("salary_min"),
                    Job.salary_max.label("salary_max"),
                    Job.salary_currency.label("salary_currency"),
                    Job.posted_at.label("posted_at"),
                    Job.scraped_at.label("scraped_at"),
                    Job.status.label("status"),
                    Job.is_active.label("is_active"),
                    Job.applicant_count.label("applicant_count"),
                    Job.easy_apply.label("easy_apply"),
                    Job.created_at.label("created_at"),
                ).where(Job.id == job_id)
            )
            row = fallback.first()
            if not row:
                raise HTTPException(status_code=404, detail="Job not found")
            return JobOut.model_validate(_job_namespace_from_row(row))
    job = result.scalar_one_or_none()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job


@router.post("", response_model=JobOut, status_code=201)
async def create_job_manual(
    payload: JobCreate,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Manually add a job (user found it themselves)."""
    from datetime import datetime, timezone
    job = Job(
        user_id=current_user.id,
        source="manual",
        source_job_id=f"manual_{datetime.now(timezone.utc).timestamp()}",
        source_url=payload.source_url,
        title=payload.title,
        company_name=payload.company_name,
        description_raw=payload.description_raw,
        description_clean=payload.description_raw,
        location=payload.location,
        job_type=payload.job_type,
        work_mode=payload.work_mode,
        salary_min=payload.salary_min,
        salary_max=payload.salary_max,
        scraped_at=datetime.now(timezone.utc),
    )
    db.add(job)
    await db.commit()
    await db.refresh(job)

    background_tasks.add_task(_trigger_job_analysis, job.id)
    return job


@router.post("/{job_id}/analyze", response_model=MessageResponse)
async def trigger_analysis(
    job_id: str,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Manually trigger AI analysis for a job."""
    result = await db.execute(select(Job).where(Job.id == job_id))
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Job not found")
    background_tasks.add_task(_trigger_job_analysis, job_id)
    return MessageResponse(message=f"Analysis queued for job {job_id}")


@router.post("/{job_id}/skip", response_model=MessageResponse)
async def skip_job(
    job_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Mark a job as skipped so it won't be auto-applied."""
    result = await db.execute(
        select(Job).where(Job.id == job_id, Job.user_id == current_user.id)
    )
    job = result.scalar_one_or_none()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    job.status = JobStatus.SKIPPED
    await db.commit()
    return MessageResponse(message="Job marked as skipped")


async def _trigger_job_analysis(job_id: str):
    """Background task wrapper — runs analysis directly."""
    try:
        from app.agents.tasks import analyze_new_jobs_batch_task
        from app.core.database import get_db_context
        from sqlalchemy import select
        from app.models.job import Job

        async with get_db_context() as db:
            result = await db.execute(select(Job).where(Job.id == job_id))
            job = result.scalar_one_or_none()
            if job:
                from app.services.job_analyzer import JobAnalyzerService
                await JobAnalyzerService().analyze(job_id)
                import structlog
                log = structlog.get_logger()
                log.info("Job analysis completed", job_id=job_id)
    except Exception as e:
        import structlog
        log = structlog.get_logger()
        log.error("Failed to analyze job", job_id=job_id, error=str(e))
