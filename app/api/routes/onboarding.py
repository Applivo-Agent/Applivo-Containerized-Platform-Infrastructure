"""
app/api/routes/onboarding.py
────────────────────────────
API routes for user onboarding.
Step-by-step profile collection and onboarding flow.
"""

from __future__ import annotations

from typing import Any, Dict, List

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db_context
from app.models.user import User
from app.services.onboarding_service import OnboardingService, OnboardingStep

router = APIRouter(prefix="/api/v1/onboarding", tags=["onboarding"])


# ── Request Models ────────────────────────────────────────────────

class BasicInfoUpdate(BaseModel):
    """Step 1: Basic personal information."""
    full_name: str = Field(..., min_length=1, max_length=255)
    professional_summary: str | None = None
    career_goals: str | None = None
    unique_value_proposition: str | None = None


class ContactInfoUpdate(BaseModel):
    """Step 2: Contact information."""
    phone: str | None = None
    location: str | None = None
    linkedin_url: str | None = None
    github_url: str | None = None
    portfolio_url: str | None = None
    notification_email: str | None = None


class EducationEntry(BaseModel):
    """Single education entry."""
    degree: str = Field(..., description="Degree (e.g., B.Tech, M.S., PhD)")
    field: str = Field(..., description="Field of study (e.g., Computer Science)")
    institution: str = Field(..., description="University/College name")
    year: int | None = Field(None, description="Graduation year")
    gpa: float | None = Field(None, description="GPA (0-10 scale)")
    description: str | None = None


class EducationUpdate(BaseModel):
    """Step 3: Education history."""
    education: List[EducationEntry] = Field(default_factory=list)


class WorkExperienceEntry(BaseModel):
    """Single work experience entry."""
    title: str = Field(..., description="Job title")
    company: str = Field(..., description="Company name")
    start_date: str = Field(..., description="Start date (YYYY-MM)")
    end_date: str | None = Field(None, description="End date (YYYY-MM)")
    is_current: bool = Field(False, description="Currently working here")
    description: str | None = None
    bullets: List[str] = Field(default_factory=list, description="Key achievements")


class WorkExperienceUpdate(BaseModel):
    """Step 4: Work experience."""
    experience: List[WorkExperienceEntry] = Field(default_factory=list)


class SkillEntry(BaseModel):
    """Single skill entry."""
    name: str = Field(..., description="Skill name")
    category: str | None = Field(None, description="Category: programming, ml_framework, cloud, tool, soft_skill")
    proficiency: str | None = Field(None, description="beginner, intermediate, advanced, expert")
    years_experience: float | None = None
    is_primary: bool = Field(False, description="Primary skill for job matching")


class SkillsUpdate(BaseModel):
    """Step 5: Skills."""
    skills: List[SkillEntry] = Field(default_factory=list)


class ResumeSelect(BaseModel):
    """Step 6: Select primary resume."""
    resume_id: str = Field(..., description="Resume ID to set as primary")


class JobPreferencesUpdate(BaseModel):
    """Step 7: Job search preferences."""
    experience_level: str | None = Field(None, description="entry, mid, senior")
    desired_roles: List[str] = Field(default_factory=list, description="Target job titles")
    desired_locations: List[str] = Field(default_factory=list, description="Preferred cities/countries")
    open_to_remote: bool = True
    open_to_hybrid: bool = True
    min_salary: int = Field(0, description="Minimum salary expectation")
    preferred_company_size: List[str] = Field(default_factory=list, description="startup, mid, large, enterprise")
    preferred_industries: List[str] = Field(default_factory=list)
    avoid_companies: List[str] = Field(default_factory=list)


class PlatformSetupUpdate(BaseModel):
    """Step 8: Platform and notification settings."""
    auto_apply_enabled: bool | None = None
    auto_apply_threshold: int | None = Field(None, ge=0, le=100)
    auto_apply_daily_limit: int | None = Field(None, ge=1, le=100)
    require_apply_approval: bool | None = None
    notify_new_jobs: bool | None = None
    notify_applications: bool | None = None
    notify_interviews: bool | None = None
    notify_via_telegram: bool | None = None
    notify_via_email: bool | None = None
    telegram_chat_id: str | None = None


# ── Dependencies ─────────────────────────────────────────────────

async def get_current_user() -> User:
    """Get current authenticated user."""
    async with get_db_context() as db:
        # For single-user system, get the first user
        result = await db.execute(select(User).limit(1))
        user = result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(status_code=401, detail="Not authenticated")
        
        return user


async def get_onboarding_service(user: User = Depends(get_current_user)) -> OnboardingService:
    """Get onboarding service instance."""
    async with get_db_context() as db:
        return OnboardingService(db, user)


# ── Routes ────────────────────────────────────────────────────────

@router.get("/status")
async def get_onboarding_status(
    service: OnboardingService = Depends(get_onboarding_service)
) -> Dict[str, Any]:
    """
    Get current onboarding status and progress.
    
    Returns:
        - completed_steps: List of completed onboarding steps
        - current_step: Next step to complete
        - progress_percentage: Overall progress (0-100)
        - profile: Summary of profile data
    """
    return await service.get_onboarding_status()


@router.post("/basic-info")
async def update_basic_info(
    data: BasicInfoUpdate,
    service: OnboardingService = Depends(get_onboarding_service)
) -> Dict[str, Any]:
    """Step 1: Update basic personal information."""
    return await service.update_basic_info(data.model_dump(exclude_none=False))


@router.post("/contact-info")
async def update_contact_info(
    data: ContactInfoUpdate,
    service: OnboardingService = Depends(get_onboarding_service)
) -> Dict[str, Any]:
    """Step 2: Update contact information."""
    return await service.update_contact_info(data.model_dump(exclude_none=False))


@router.post("/education")
async def update_education(
    data: EducationUpdate,
    service: OnboardingService = Depends(get_onboarding_service)
) -> Dict[str, Any]:
    """Step 3: Update education history."""
    return await service.update_education([e.model_dump() for e in data.education])


@router.post("/work-experience")
async def update_work_experience(
    data: WorkExperienceUpdate,
    service: OnboardingService = Depends(get_onboarding_service)
) -> Dict[str, Any]:
    """Step 4: Update work experience."""
    return await service.update_work_experience([e.model_dump() for e in data.experience])


@router.post("/skills")
async def update_skills(
    data: SkillsUpdate,
    service: OnboardingService = Depends(get_onboarding_service)
) -> Dict[str, Any]:
    """Step 5: Update skills."""
    return await service.update_skills([s.model_dump() for s in data.skills])


@router.post("/resume")
async def set_primary_resume(
    data: ResumeSelect,
    service: OnboardingService = Depends(get_onboarding_service)
) -> Dict[str, Any]:
    """Step 6: Set primary resume."""
    return await service.set_primary_resume(data.resume_id)


@router.post("/job-preferences")
async def update_job_preferences(
    data: JobPreferencesUpdate,
    service: OnboardingService = Depends(get_onboarding_service)
) -> Dict[str, Any]:
    """Step 7: Update job search preferences."""
    return await service.update_job_preferences(data.model_dump(exclude_none=False))


@router.post("/platform-setup")
async def update_platform_setup(
    data: PlatformSetupUpdate,
    service: OnboardingService = Depends(get_onboarding_service)
) -> Dict[str, Any]:
    """Step 8: Update platform and notification settings."""
    return await service.update_platform_setup(data.model_dump(exclude_none=False))


@router.post("/complete")
async def complete_onboarding(
    service: OnboardingService = Depends(get_onboarding_service)
) -> Dict[str, Any]:
    """Complete the onboarding process."""
    return await service.complete_onboarding()


# ── Bulk Update ─────────────────────────────────────────────────

class CompleteProfileUpdate(BaseModel):
    """Complete profile update in one call."""
    basic_info: BasicInfoUpdate | None = None
    contact_info: ContactInfoUpdate | None = None
    education: List[EducationEntry] | None = None
    work_experience: List[WorkExperienceEntry] | None = None
    skills: List[SkillEntry] | None = None
    resume_id: str | None = None
    job_preferences: JobPreferencesUpdate | None = None
    platform_setup: PlatformSetupUpdate | None = None


@router.post("/complete-profile")
async def update_complete_profile(
    data: CompleteProfileUpdate,
    service: OnboardingService = Depends(get_onboarding_service)
) -> Dict[str, Any]:
    """Update complete profile in one call (for power users)."""
    results = {}
    
    if data.basic_info:
        results["basic_info"] = await service.update_basic_info(
            data.basic_info.model_dump(exclude_none=False)
        )
    
    if data.contact_info:
        results["contact_info"] = await service.update_contact_info(
            data.contact_info.model_dump(exclude_none=False)
        )
    
    if data.education:
        results["education"] = await service.update_education(
            [e.model_dump() for e in data.education]
        )
    
    if data.work_experience:
        results["work_experience"] = await service.update_work_experience(
            [e.model_dump() for e in data.work_experience]
        )
    
    if data.skills:
        results["skills"] = await service.update_skills(
            [s.model_dump() for s in data.skills]
        )
    
    if data.resume_id:
        results["resume"] = await service.set_primary_resume(data.resume_id)
    
    if data.job_preferences:
        results["job_preferences"] = await service.update_job_preferences(
            data.job_preferences.model_dump(exclude_none=False)
        )
    
    if data.platform_setup:
        results["platform_setup"] = await service.update_platform_setup(
            data.platform_setup.model_dump(exclude_none=False)
        )
    
    return {
        "status": "success",
        "message": "Profile updated successfully",
        "completed_sections": list(results.keys())
    }
