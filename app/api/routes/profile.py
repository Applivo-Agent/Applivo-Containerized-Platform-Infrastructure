"""
app/api/routes/profile.py
──────────────────────────
User profile management — the data backbone for all AI services.
GET /api/profile        — fetch full profile
PATCH /api/profile      — update any profile fields
POST /api/profile/skills — add a skill
DELETE /api/profile/skills/{skill_id} — remove a skill
GET /api/profile/stats  — dashboard summary stats
"""

from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.api.routes.auth import get_current_user
from app.models.user import User, UserProfile, UserSkill
from app.models.job import Job, JobAnalysis
from app.models.application import Application, ApplicationStatus
from app.models.interview import SkillGap
from app.schemas import (
    UserProfileOut,
    UserProfileUpdate,
    UserSkillCreate,
    UserSkillOut,
    DashboardStats,
    MessageResponse,
)

router = APIRouter(prefix="/profile", tags=["Profile"])


def _normalize_experience_level(value):
    from app.models.user import ExperienceLevel

    if isinstance(value, ExperienceLevel):
        return value

    normalized = str(value or "").strip().upper().replace("-", "_")
    mapping = {
        "ENTRY": ExperienceLevel.ENTRY,
        "MID": ExperienceLevel.MID,
        "SENIOR": ExperienceLevel.SENIOR,
        "LEAD": ExperienceLevel.LEAD,
        "EXECUTIVE": ExperienceLevel.EXECUTIVE,
        "UNKNOWN": ExperienceLevel.UNKNOWN,
    }
    return mapping.get(normalized, ExperienceLevel.ENTRY)


@router.get("", response_model=UserProfileOut)
async def get_profile(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Return the current user's full career profile."""
    result = await db.execute(
        select(UserProfile).where(UserProfile.user_id == current_user.id)
    )
    profile = result.scalar_one_or_none()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found — register first")

    # Attach user fields so frontend can display full_name and email
    profile_dict = {
        c.name: getattr(profile, c.name)
        for c in profile.__table__.columns
    }
    profile_dict["full_name"] = current_user.full_name
    profile_dict["email"] = current_user.email
    return profile_dict


@router.patch("", response_model=UserProfileOut)
async def update_profile(
    payload: UserProfileUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Partial update of the user profile.
    Only provided fields are updated — omitted fields are left unchanged.
    This is the primary setup endpoint after registration.
    """
    result = await db.execute(
        select(UserProfile).where(UserProfile.user_id == current_user.id)
    )
    profile = result.scalar_one_or_none()
    if not profile:
        # Auto-create if somehow missing
        profile = UserProfile(user_id=current_user.id)
        db.add(profile)
        await db.flush()

    # Apply only the fields that were explicitly provided
    update_data = payload.model_dump(exclude_unset=True)

    # full_name and email belong to User model, not UserProfile
    if "full_name" in update_data:
        current_user.full_name = update_data.pop("full_name")
    if "email" in update_data:
        current_user.email = update_data.pop("email")

    for field, value in update_data.items():
        if hasattr(profile, field):
            if field == "experience_level":
                value = _normalize_experience_level(value)
            setattr(profile, field, value)

    await db.commit()
    await db.refresh(profile)
    return profile


@router.get("/skills", response_model=list[UserSkillOut])
async def list_skills(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(UserSkill)
        .where(UserSkill.user_id == current_user.id)
        .order_by(UserSkill.is_primary.desc(), UserSkill.name)
    )
    return result.scalars().all()


@router.post("/skills", response_model=UserSkillOut, status_code=201)
async def add_skill(
    payload: UserSkillCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Add a skill to the user's profile. Silently ignores duplicates."""
    # Check for duplicate
    existing = (await db.execute(
        select(UserSkill).where(
            UserSkill.user_id == current_user.id,
            UserSkill.name == payload.name,
        )
    )).scalar_one_or_none()

    if existing:
        # Update proficiency/years instead of creating a duplicate
        for field, value in payload.model_dump(exclude_unset=True).items():
            setattr(existing, field, value)
        await db.commit()
        await db.refresh(existing)
        return existing

    skill = UserSkill(user_id=current_user.id, **payload.model_dump())
    db.add(skill)
    await db.commit()
    await db.refresh(skill)
    return skill


@router.delete("/skills/{skill_id}", response_model=MessageResponse)
async def remove_skill(
    skill_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    skill = (await db.execute(
        select(UserSkill).where(
            UserSkill.id == skill_id,
            UserSkill.user_id == current_user.id,
        )
    )).scalar_one_or_none()
    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found")
    await db.delete(skill)
    await db.commit()
    return MessageResponse(message=f"Skill '{skill.name}' removed")


@router.post("/skills/bulk", response_model=list[UserSkillOut], status_code=201)
async def bulk_add_skills(
    skills: list[UserSkillCreate],
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Add multiple skills at once — useful for onboarding."""
    existing_names = {
        row[0] for row in (await db.execute(
            select(UserSkill.name).where(UserSkill.user_id == current_user.id)
        )).all()
    }
    new_skills = []
    for s in skills:
        if s.name not in existing_names:
            skill = UserSkill(user_id=current_user.id, **s.model_dump())
            db.add(skill)
            new_skills.append(skill)
            existing_names.add(s.name)

    await db.commit()
    for s in new_skills:
        await db.refresh(s)
    return new_skills


@router.get("/stats", response_model=DashboardStats)
async def get_dashboard_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Aggregate stats for the dashboard — single endpoint, one DB round-trip each."""
    today = datetime.now(timezone.utc).date()

    # Jobs
    total_jobs = (await db.execute(
        select(func.count(Job.id)).where(Job.is_active == True)
    )).scalar() or 0

    jobs_today = (await db.execute(
        select(func.count(Job.id)).where(func.date(Job.scraped_at) == today)
    )).scalar() or 0

    high_match_jobs = (await db.execute(
        select(func.count(JobAnalysis.id)).where(JobAnalysis.match_score >= 70)
    )).scalar() or 0

    # Applications
    app_counts_result = await db.execute(
        select(Application.status, func.count(Application.id).label("n"))
        .where(Application.user_id == current_user.id)
        .group_by(Application.status)
    )
    app_counts = {row.status: row.n for row in app_counts_result.all()}
    total_applications = sum(app_counts.values())

    apps_today = (await db.execute(
        select(func.count(Application.id)).where(
            Application.user_id == current_user.id,
            func.date(Application.created_at) == today,
        )
    )).scalar() or 0

    applied = app_counts.get(ApplicationStatus.APPLIED, 0)
    viewed = app_counts.get(ApplicationStatus.VIEWED, 0)
    shortlisted = app_counts.get(ApplicationStatus.SHORTLISTED, 0)
    interviews = (
        app_counts.get(ApplicationStatus.INTERVIEW_SCHEDULED, 0)
        + app_counts.get(ApplicationStatus.INTERVIEW_COMPLETED, 0)
    )
    offers = (
        app_counts.get(ApplicationStatus.OFFER_RECEIVED, 0)
        + app_counts.get(ApplicationStatus.OFFER_ACCEPTED, 0)
    )
    positive = viewed + shortlisted + interviews + offers
    response_rate = round(positive / applied * 100, 1) if applied > 0 else 0.0

    # Skill gaps
    gaps_result = await db.execute(
        select(SkillGap.skill_name, SkillGap.priority, SkillGap.demand_percentage)
        .where(SkillGap.user_id == current_user.id, SkillGap.resolved == False)
        .order_by(desc(SkillGap.demand_count))
        .limit(5)
    )
    top_skill_gaps = [
        {"skill": r.skill_name, "priority": r.priority, "demand_pct": r.demand_percentage}
        for r in gaps_result.all()
    ]

    # Recent activity (last 5 applications)
    recent_apps = await db.execute(
        select(Application.company_snapshot, Application.job_title_snapshot,
               Application.status, Application.created_at)
        .where(Application.user_id == current_user.id)
        .order_by(desc(Application.created_at))
        .limit(5)
    )
    recent_activity = [
        {
            "company": r.company_snapshot,
            "role": r.job_title_snapshot,
            "status": r.status,
            "date": r.created_at.isoformat(),
        }
        for r in recent_apps.all()
    ]

    return DashboardStats(
        total_jobs=total_jobs,
        jobs_today=jobs_today,
        high_match_jobs=high_match_jobs,
        total_applications=total_applications,
        applications_today=apps_today,
        pending_approval=app_counts.get(ApplicationStatus.PENDING_APPROVAL, 0),
        interviews_scheduled=interviews,
        offers_received=offers,
        response_rate=response_rate,
        top_skill_gaps=top_skill_gaps,
        recent_activity=recent_activity,
    )