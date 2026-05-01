"""
app/services/onboarding_service.py
─────────────────────────────────
Comprehensive user onboarding service.
Collects all user details: profile, skills, experience, preferences.
Manages onboarding state and progress.
"""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional

import structlog
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db_context
from app.models.user import User, UserProfile, UserSkill, ExperienceLevel
from app.models.resume import Resume

logger = structlog.get_logger()


class OnboardingStep(str, Enum):
    """Steps in the onboarding flow."""
    WELCOME = "welcome"
    BASIC_INFO = "basic_info"
    CONTACT_INFO = "contact_info"
    EDUCATION = "education"
    WORK_EXPERIENCE = "work_experience"
    SKILLS = "skills"
    RESUME = "resume"
    JOB_PREFERENCES = "job_preferences"
    PLATFORM_SETUP = "platform_setup"
    COMPLETE = "complete"


class OnboardingService:
    """
    Manages user onboarding flow.
    Collects comprehensive profile data in steps.
    """

    def _normalize_experience_level(self, value: Any) -> ExperienceLevel:
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

    def __init__(self, db: AsyncSession, user: User):
        self.db = db
        self.user = user

    async def get_onboarding_status(self) -> Dict[str, Any]:
        """Get current onboarding status and progress."""
        profile = await self._get_or_create_profile()
        
        completed_steps = []
        
        # Check what data exists to determine completed steps
        if profile.full_name:
            completed_steps.append(OnboardingStep.BASIC_INFO.value)
        if profile.location or profile.phone:
            completed_steps.append(OnboardingStep.CONTACT_INFO.value)
        if profile.education:
            completed_steps.append(OnboardingStep.EDUCATION.value)
        if profile.work_experience:
            completed_steps.append(OnboardingStep.WORK_EXPERIENCE.value)
        
        # Check skills
        skills_result = await self.db.execute(
            select(UserSkill).where(UserSkill.user_id == self.user.id)
        )
        skills = skills_result.scalars().all()
        if skills:
            completed_steps.append(OnboardingStep.SKILLS.value)
        
        # Check resume
        resume_result = await self.db.execute(
            select(Resume).where(Resume.user_id == self.user.id)
        )
        resume = resume_result.scalars().first()
        if resume:
            completed_steps.append(OnboardingStep.RESUME.value)
        
        # Check job preferences
        if profile.desired_roles or profile.experience_level:
            completed_steps.append(OnboardingStep.JOB_PREFERENCES.value)
        
        # Check platform setup
        if profile.auto_apply_enabled is not None or profile.notify_via_telegram:
            completed_steps.append(OnboardingStep.PLATFORM_SETUP.value)
        
        if len(completed_steps) >= 7:
            completed_steps.append(OnboardingStep.COMPLETE.value)
        
        current_step = self._determine_next_step(completed_steps)
        
        return {
            "user_id": self.user.id,
            "email": self.user.email,
            "full_name": self.user.full_name,
            "completed_steps": completed_steps,
            "current_step": current_step,
            "progress_percentage": int(len(completed_steps) / 9 * 100),
            "profile": await self._get_profile_summary(profile)
        }

    def _determine_next_step(self, completed: List[str]) -> str:
        """Determine the next incomplete step."""
        steps_order = [
            OnboardingStep.BASIC_INFO,
            OnboardingStep.CONTACT_INFO,
            OnboardingStep.EDUCATION,
            OnboardingStep.WORK_EXPERIENCE,
            OnboardingStep.SKILLS,
            OnboardingStep.RESUME,
            OnboardingStep.JOB_PREFERENCES,
            OnboardingStep.PLATFORM_SETUP,
            OnboardingStep.COMPLETE,
        ]
        
        for step in steps_order:
            if step.value not in completed:
                return step.value
        return OnboardingStep.COMPLETE.value

    async def _get_or_create_profile(self) -> UserProfile:
        """Get existing profile or create new one."""
        result = await self.db.execute(
            select(UserProfile).where(UserProfile.user_id == self.user.id)
        )
        profile = result.scalar_one_or_none()
        
        if not profile:
            profile = UserProfile(
                user_id=self.user.id,
                experience_level=ExperienceLevel.ENTRY,
                desired_roles=[],
                desired_locations=[],
                open_to_remote=True,
                open_to_hybrid=True,
                min_salary=0,
                preferred_company_size=[],
                preferred_industries=[],
                avoid_companies=[],
                education=[],
                work_experience=[],
                projects=[],
                certifications=[],
                awards=[],
                publications=[],
                auto_apply_enabled=False,
                auto_apply_threshold=75,
                auto_apply_daily_limit=10,
                require_apply_approval=True,
                notify_new_jobs=True,
                notify_applications=True,
                notify_interviews=True,
                notify_via_telegram=True,
                notify_via_email=True,
            )
            self.db.add(profile)
            await self.db.commit()
            await self.db.refresh(profile)
        
        return profile

    async def _get_profile_summary(self, profile: UserProfile) -> Dict[str, Any]:
        """Get a summary of the profile for display."""
        # Get skills count
        skills_result = await self.db.execute(
            select(UserSkill).where(UserSkill.user_id == self.user.id)
        )
        skills = skills_result.scalars().all()
        
        return {
            "experience_level": profile.experience_level.value if profile.experience_level else "not set",
            "desired_roles": profile.desired_roles or [],
            "location": profile.location,
            "skills_count": len(skills),
            "has_resume": False,  # Will be checked separately
            "auto_apply_enabled": profile.auto_apply_enabled,
        }

    # ── Step 1: Basic Info ────────────────────────────────────────

    async def update_basic_info(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Update basic personal information."""
        profile = await self._get_or_create_profile()
        
        if "full_name" in data:
            self.user.full_name = data["full_name"]
        
        if "professional_summary" in data:
            profile.professional_summary = data["professional_summary"]
        
        if "career_goals" in data:
            profile.career_goals = data["career_goals"]
        
        if "unique_value_proposition" in data:
            profile.unique_value_proposition = data["unique_value_proposition"]
        
        await self.db.commit()
        
        logger.info("Basic info updated", user_id=self.user.id)
        
        return {"status": "success", "step": OnboardingStep.BASIC_INFO.value}

    # ── Step 2: Contact Info ───────────────────────────────────────

    async def update_contact_info(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Update contact information."""
        profile = await self._get_or_create_profile()
        
        if "phone" in data:
            profile.phone = data["phone"]
        if "location" in data:
            profile.location = data["location"]
        if "linkedin_url" in data:
            profile.linkedin_url = data["linkedin_url"]
        if "github_url" in data:
            profile.github_url = data["github_url"]
        if "portfolio_url" in data:
            profile.portfolio_url = data["portfolio_url"]
        if "notification_email" in data:
            profile.notification_email = data["notification_email"]
        
        await self.db.commit()
        
        logger.info("Contact info updated", user_id=self.user.id)
        
        return {"status": "success", "step": OnboardingStep.CONTACT_INFO.value}

    # ── Step 3: Education ──────────────────────────────────────────

    async def update_education(self, education: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Update education history."""
        profile = await self._get_or_create_profile()
        
        # Validate and clean education entries
        cleaned_education = []
        for edu in education:
            cleaned_edu = {
                "degree": edu.get("degree", ""),
                "field": edu.get("field", ""),
                "institution": edu.get("institution", ""),
                "year": edu.get("year"),
                "gpa": edu.get("gpa"),
                "description": edu.get("description", ""),
            }
            if cleaned_edu["degree"] and cleaned_edu["institution"]:
                cleaned_education.append(cleaned_edu)
        
        profile.education = cleaned_education
        await self.db.commit()
        
        logger.info("Education updated", user_id=self.user.id, count=len(cleaned_education))
        
        return {
            "status": "success", 
            "step": OnboardingStep.EDUCATION.value,
            "education_count": len(cleaned_education)
        }

    # ── Step 4: Work Experience ─────────────────────────────────────

    async def update_work_experience(self, experience: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Update work experience history."""
        profile = await self._get_or_create_profile()
        
        # Validate and clean experience entries
        cleaned_experience = []
        for exp in experience:
            cleaned_exp = {
                "title": exp.get("title", ""),
                "company": exp.get("company", ""),
                "start_date": exp.get("start_date"),
                "end_date": exp.get("end_date"),
                "is_current": exp.get("is_current", False),
                "description": exp.get("description", ""),
                "bullets": exp.get("bullets", []),
            }
            if cleaned_exp["title"] and cleaned_exp["company"]:
                cleaned_experience.append(cleaned_exp)
        
        profile.work_experience = cleaned_experience
        await self.db.commit()
        
        logger.info("Work experience updated", user_id=self.user.id, count=len(cleaned_experience))
        
        return {
            "status": "success",
            "step": OnboardingStep.WORK_EXPERIENCE.value,
            "experience_count": len(cleaned_experience)
        }

    # ── Step 5: Skills ─────────────────────────────────────────────

    async def update_skills(self, skills: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Update user skills."""
        from sqlalchemy import delete
        
        # Use proper delete statement with await
        await self.db.execute(
            delete(UserSkill).where(UserSkill.user_id == self.user.id)
        )
        
        # Add new skills
        added_skills = []
        for skill in skills:
            if not skill.get("name"):
                continue
                
            user_skill = UserSkill(
                user_id=self.user.id,
                name=skill.get("name", ""),
                category=skill.get("category"),
                proficiency=skill.get("proficiency"),
                years_experience=skill.get("years_experience"),
                is_primary=skill.get("is_primary", False),
            )
            self.db.add(user_skill)
            added_skills.append(skill.get("name"))
        
        await self.db.commit()
        
        logger.info("Skills updated", user_id=self.user.id, count=len(added_skills))
        
        return {
            "status": "success",
            "step": OnboardingStep.SKILLS.value,
            "skills_count": len(added_skills)
        }

    # ── Step 6: Resume ─────────────────────────────────────────────

    async def set_primary_resume(self, resume_id: str) -> Dict[str, Any]:
        """Set the primary resume for applications."""
        # Verify resume belongs to user
        result = await self.db.execute(
            select(Resume).where(
                Resume.id == resume_id,
                Resume.user_id == self.user.id
            )
        )
        resume = result.scalar_one_or_none()
        
        if not resume:
            raise ValueError("Resume not found or does not belong to user")
        
        # Update all resumes to non-primary
        await self.db.execute(
            Resume.__table__.update().where(Resume.user_id == self.user.id).values(is_primary=False)
        )
        
        # Set this one as primary
        resume.is_primary = True
        await self.db.commit()
        
        logger.info("Primary resume set", user_id=self.user.id, resume_id=resume_id)
        
        return {
            "status": "success",
            "step": OnboardingStep.RESUME.value,
            "resume_id": resume_id
        }

    # ── Step 7: Job Preferences ───────────────────────────────────

    async def update_job_preferences(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Update job search preferences."""
        profile = await self._get_or_create_profile()
        
        if "experience_level" in data:
            profile.experience_level = self._normalize_experience_level(data["experience_level"])
        
        if "desired_roles" in data:
            profile.desired_roles = data["desired_roles"]
        
        if "desired_locations" in data:
            profile.desired_locations = data["desired_locations"]
        
        if "open_to_remote" in data:
            profile.open_to_remote = data["open_to_remote"]
        
        if "open_to_hybrid" in data:
            profile.open_to_hybrid = data["open_to_hybrid"]
        
        if "min_salary" in data:
            profile.min_salary = data["min_salary"]
        
        if "preferred_company_size" in data:
            profile.preferred_company_size = data["preferred_company_size"]
        
        if "preferred_industries" in data:
            profile.preferred_industries = data["preferred_industries"]
        
        if "avoid_companies" in data:
            profile.avoid_companies = data["avoid_companies"]
        
        await self.db.commit()
        
        logger.info("Job preferences updated", user_id=self.user.id)
        
        return {
            "status": "success",
            "step": OnboardingStep.JOB_PREFERENCES.value
        }

    # ── Step 8: Platform Setup ─────────────────────────────────────

    async def update_platform_setup(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Update platform/notification settings."""
        profile = await self._get_or_create_profile()
        
        if "auto_apply_enabled" in data:
            profile.auto_apply_enabled = data["auto_apply_enabled"]
        
        if "auto_apply_threshold" in data:
            profile.auto_apply_threshold = data["auto_apply_threshold"]
        
        if "auto_apply_daily_limit" in data:
            profile.auto_apply_daily_limit = data["auto_apply_daily_limit"]
        
        if "require_apply_approval" in data:
            profile.require_apply_approval = data["require_apply_approval"]
        
        if "notify_new_jobs" in data:
            profile.notify_new_jobs = data["notify_new_jobs"]
        
        if "notify_applications" in data:
            profile.notify_applications = data["notify_applications"]
        
        if "notify_interviews" in data:
            profile.notify_interviews = data["notify_interviews"]
        
        if "notify_via_telegram" in data:
            profile.notify_via_telegram = data["notify_via_telegram"]
        
        if "notify_via_email" in data:
            profile.notify_via_email = data["notify_via_email"]
        
        if "telegram_chat_id" in data:
            profile.telegram_chat_id = data["telegram_chat_id"]
        
        await self.db.commit()
        
        logger.info("Platform setup updated", user_id=self.user.id)
        
        return {
            "status": "success",
            "step": OnboardingStep.PLATFORM_SETUP.value
        }

    # ── Complete Onboarding ─────────────────────────────────────────

    async def complete_onboarding(self) -> Dict[str, Any]:
        """Mark onboarding as complete. RESUME IS MANDATORY."""
        profile = await self._get_or_create_profile()
        
        # CHECK: Resume is MANDATORY before completing onboarding
        resume_result = await self.db.execute(
            select(Resume).where(
                Resume.user_id == self.user.id,
                Resume.is_default == True
            )
        )
        default_resume = resume_result.scalar_one_or_none()
        
        if not default_resume:
            # Check if any resume exists
            any_resume_result = await self.db.execute(
                select(Resume).where(Resume.user_id == self.user.id)
            )
            any_resume = any_resume_result.scalar_one_or_none()
            
            if not any_resume:
                raise ValueError(
                    "Resume is REQUIRED to complete onboarding. "
                    "Please upload a resume before proceeding. "
                    "The resume is needed for job applications."
                )
            else:
                # Set first resume as default
                any_resume.is_default = True
                await self.db.commit()
                default_resume = any_resume
        
        # Validate: Basic info required
        if not profile.full_name:
            raise ValueError(
                "Basic info (name) is REQUIRED. Please enter your name."
            )
        
        # Validate: At least one skill recommended
        skills_result = await self.db.execute(
            select(UserSkill).where(UserSkill.user_id == self.user.id)
        )
        skills = skills_result.scalars().all()
        
        # Send registration / onboarding completion notification
        try:
            from app.services.notification_service import NotificationService

            completion_subject, completion_body = self._build_completion_notification(
                profile=profile,
                skills=skills,
                resume=default_resume,
            )

            notif_service = NotificationService()
            await notif_service.notify(
                title=completion_subject,
                body=completion_body,
                event_type="registration_complete",
                  user_id=self.user.id,
            )
        except Exception as e:
            logger.warning("Completion notification failed", error=str(e))
        
        return {
            "status": "success",
            "step": OnboardingStep.COMPLETE.value,
            "message": "Onboarding completed successfully!"
        }

    def _format_list(self, values: List[str], fallback: str = "Not set", limit: int = 5) -> str:
        cleaned = [str(value).strip() for value in values if str(value).strip()]
        if not cleaned:
            return fallback
        if len(cleaned) <= limit:
            return ", ".join(cleaned)
        remaining = len(cleaned) - limit
        return f"{', '.join(cleaned[:limit])} (+{remaining} more)"

    def _format_resume_label(self, resume: Optional[Resume]) -> str:
        if not resume:
            return "No resume uploaded"
        resume_type = getattr(resume.resume_type, "value", resume.resume_type)
        label = resume.name
        if resume_type:
            label = f"{label} ({resume_type})"
        if resume.role_category:
            label = f"{label} - {resume.role_category}"
        return label

    def _build_completion_notification(
        self,
        profile: UserProfile,
        skills: List[UserSkill],
        resume: Optional[Resume],
    ) -> tuple[str, str]:
        skill_names = [skill.name for skill in skills]
        primary_skills = [skill.name for skill in skills if skill.is_primary]
        education_entries = profile.education or []
        experience_entries = profile.work_experience or []

        education_lines: List[str] = []
        for entry in education_entries[:3]:
            degree = str(entry.get("degree", "")).strip()
            field = str(entry.get("field", "")).strip()
            institution = str(entry.get("institution", "")).strip()
            year = entry.get("year")
            parts = [part for part in [degree, field] if part]
            line = " ".join(parts) if parts else "Education entry"
            if institution:
                line = f"{line} at {institution}"
            if year:
                line = f"{line} ({year})"
            education_lines.append(line)

        experience_lines: List[str] = []
        for entry in experience_entries[:3]:
            title = str(entry.get("title", "")).strip()
            company = str(entry.get("company", "")).strip()
            line = title or "Experience entry"
            if company:
                line = f"{line} at {company}"
            experience_lines.append(line)

        subject = "Registration Successful - Your Applivo profile is ready"
        body = (
            f"Hi {self.user.full_name},\n\n"
            "Your registration and onboarding are complete. Here is your saved profile summary:\n\n"
            f"Account\n"
            f"• Name: {self.user.full_name}\n"
            f"• Email: {self.user.email}\n"
            f"• Verified: Yes\n\n"
            f"Contact\n"
            f"• Phone: {profile.phone or 'Not set'}\n"
            f"• Location: {profile.location or 'Not set'}\n"
            f"• LinkedIn: {profile.linkedin_url or 'Not set'}\n"
            f"• GitHub: {profile.github_url or 'Not set'}\n"
            f"• Portfolio: {profile.portfolio_url or 'Not set'}\n\n"
            f"Career Profile\n"
            f"• Experience level: {profile.experience_level.value if profile.experience_level else 'Not set'}\n"
            f"• Desired roles: {self._format_list(profile.desired_roles or [], fallback='Not set')}\n"
            f"• Desired locations: {self._format_list(profile.desired_locations or [], fallback='Not set')}\n"
            f"• Open to remote: {'Yes' if profile.open_to_remote else 'No'}\n"
            f"• Open to hybrid: {'Yes' if profile.open_to_hybrid else 'No'}\n"
            f"• Minimum salary: {profile.min_salary or 0}\n"
            f"• Preferred company size: {self._format_list(profile.preferred_company_size or [], fallback='Not set')}\n"
            f"• Preferred industries: {self._format_list(profile.preferred_industries or [], fallback='Not set')}\n"
            f"• Companies to avoid: {self._format_list(profile.avoid_companies or [], fallback='None')}\n\n"
            f"Skills\n"
            f"• Total skills: {len(skills)}\n"
            f"• Primary skills: {self._format_list(primary_skills, fallback='None', limit=5)}\n"
            f"• All skills: {self._format_list(skill_names, fallback='No skills added', limit=8)}\n\n"
            f"Education\n"
            f"• {('; '.join(education_lines) if education_lines else 'Not provided')}\n\n"
            f"Work Experience\n"
            f"• {('; '.join(experience_lines) if experience_lines else 'Not provided')}\n\n"
            f"Resume\n"
            f"• {self._format_resume_label(resume)}\n"
            f"• ATS score: {resume.ats_score if resume and resume.ats_score is not None else 'Not calculated'}\n\n"
            f"Automation and notifications\n"
            f"• Auto apply enabled: {'Yes' if profile.auto_apply_enabled else 'No'}\n"
            f"• Auto apply threshold: {profile.auto_apply_threshold}\n"
            f"• Daily limit: {profile.auto_apply_daily_limit}\n"
            f"• Approval required: {'Yes' if profile.require_apply_approval else 'No'}\n"
            f"• Email notifications: {'On' if profile.notify_via_email else 'Off'}\n"
            f"• Telegram notifications: {'On' if profile.notify_via_telegram else 'Off'}\n\n"
            "You can now browse jobs, let Applivo track matches, and receive interview notifications."
        )

        return subject, body

    # ── Get Profile for AI ─────────────────────────────────────────

    async def get_profile_for_ai(self) -> str:
        """Get a comprehensive profile summary for AI context."""
        profile = await self._get_or_create_profile()
        
        # Get skills
        skills_result = await self.db.execute(
            select(UserSkill).where(UserSkill.user_id == self.user.id)
        )
        skills = skills_result.scalars().all()
        
        # Get resume
        resume_result = await self.db.execute(
            select(Resume).where(
                Resume.user_id == self.user.id,
                Resume.is_primary == True
            )
        )
        resume = resume_result.scalars().first()
        
        # Build comprehensive profile string
        profile_text = f"""
USER PROFILE:
- Name: {self.user.full_name}
- Email: {self.user.email}
- Location: {profile.location or 'Not specified'}
- Phone: {profile.phone or 'Not specified'}

CAREER:
- Experience Level: {profile.experience_level.value if profile.experience_level else 'Not specified'}
- Desired Roles: {', '.join(profile.desired_roles) if profile.desired_roles else 'Not specified'}
- Desired Locations: {', '.join(profile.desired_locations) if profile.desired_locations else 'Anywhere'}
- Open to Remote: {'Yes' if profile.open_to_remote else 'No'}
- Open to Hybrid: {'Yes' if profile.open_to_hybrid else 'No'}
- Min Salary: ${profile.min_salary:,}

SKILLS ({len(skills)} total):
{', '.join([s.name for s in skills]) if skills else 'No skills added'}

PROFESSIONAL SUMMARY:
{profile.professional_summary or 'Not provided'}

CAREER GOALS:
{profile.career_goals or 'Not provided'}

EDUCATION:
{self._format_education(profile.education)}

WORK EXPERIENCE:
{self._format_experience(profile.work_experience)}

RESUME: {'Uploaded - ' + (resume.filename if resume else 'Unknown)' if resume else 'No resume uploaded')}

AUTO-APPLY: {'Enabled' if profile.auto_apply_enabled else 'Disabled'}
- Threshold: {profile.auto_apply_threshold}%
- Daily Limit: {profile.auto_apply_daily_limit}
- Approval Required: {'Yes' if profile.require_apply_approval else 'No'}
"""
        return profile_text

    def _format_education(self, education: List[Dict]) -> str:
        if not education:
            return "No education added"
        
        lines = []
        for edu in education:
            line = f"- {edu.get('degree')} in {edu.get('field')} at {edu.get('institution')}"
            if edu.get('year'):
                line += f" ({edu.get('year')})"
            lines.append(line)
        return '\n'.join(lines)

    def _format_experience(self, experience: List[Dict]) -> str:
        if not experience:
            return "No work experience added"
        
        lines = []
        for exp in experience:
            line = f"- {exp.get('title')} at {exp.get('company')}"
            if exp.get('start_date'):
                line += f" ({exp.get('start_date')}"
                if exp.get('is_current'):
                    line += " - Present)"
                elif exp.get('end_date'):
                    line += f" - {exp.get('end_date')})"
            lines.append(line)
        return '\n'.join(lines)


# ── Helper Functions ─────────────────────────────────────────────

async def get_onboarding_service(user_id: str) -> OnboardingService:
    """Factory function to create onboarding service."""
    async with get_db_context() as db:
        result = await db.execute(
            select(User).where(User.id == user_id)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            raise ValueError(f"User {user_id} not found")
        
        return OnboardingService(db, user)
