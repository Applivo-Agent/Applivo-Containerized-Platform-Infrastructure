"""
app/services/screening_question_service.py
───────────────────────────────────────────
Service to handle job application screening questions.
Uses AI to generate intelligent answers based on user profile.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

import structlog
from openai import AsyncOpenAI
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db_context
from app.models.application import Application, ApplicationEvent, ApplicationStatus
from app.models.job import Job
from app.models.resume import Resume
from app.models.user import UserProfile, UserSkill

logger = structlog.get_logger()

client = AsyncOpenAI(
    api_key=settings.ai_api_key,
    base_url="https://api.groq.com/openai/v1",
)


class ScreeningQuestionService:
    """
    Handles job application screening questions.
    Uses AI to generate personalized answers based on user profile.
    """

    def __init__(self, db: AsyncSession, user_id: str):
        self.db = db
        self.user_id = user_id

    async def get_user_context(self) -> str:
        """Get user context for answering questions."""
        async with get_db_context() as db:
            # Get profile
            result = await db.execute(
                select(UserProfile).where(UserProfile.user_id == self.user_id)
            )
            profile = result.scalar_one_or_none()
            
            # Get skills
            result = await db.execute(
                select(UserSkill).where(UserSkill.user_id == self.user_id)
            )
            skills = result.scalars().all()
            
            # Get primary resume
            result = await db.execute(
                select(Resume).where(
                    Resume.user_id == self.user_id,
                    Resume.is_primary == True
                )
            )
            resume = result.scalar_one_or_none()
            
            # Build context
            context = f"""
USER PROFILE:
- Experience Level: {profile.experience_level.value if profile else 'Not specified'}
- Location: {profile.location or 'Not specified'}
- Desired Roles: {', '.join(profile.desired_roles) if profile and profile.desired_roles else 'Flexible'}

SKILLS ({len(skills) if skills else 0}):
{', '.join([s.name for s in skills]) if skills else 'Not specified'}

KEY QUALIFICATIONS:
{profile.professional_summary or 'Not specified'}

WORK EXPERIENCE SUMMARY:
"""
            if profile and profile.work_experience:
                for exp in profile.work_experience[:3]:  # Top 3 experiences
                    context += f"- {exp.get('title')} at {exp.get('company')}\n"
            
            context += f"\nRESUME: {'Uploaded' if resume else 'Not uploaded'}"
            
            return context

    async def answer_question(
        self, 
        question: str, 
        question_type: str = "general",
        job_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate an answer to a screening question.
        
        Args:
            question: The screening question text
            question_type: Type of question (years_experience, authorization, skills, etc.)
            job_context: Optional job details for context
            
        Returns:
            dict with 'answer' and 'confidence' score
        """
        user_context = await self.get_user_context()
        
        # Build job context if provided
        job_info = ""
        if job_context:
            job_info = f"""
JOB CONTEXT:
- Title: {job_context.get('title', 'N/A')}
- Company: {job_context.get('company', 'N/A')}
- Requirements: {job_context.get('requirements', 'N/A')}
"""
        
        system_prompt = f"""You are a career assistant helping a job seeker answer screening questions accurately and professionally.

IMPORTANT RULES:
1. Only answer based on the user's actual profile and experience
2. Never lie or fabricate information
3. If you don't have the information, say so honestly
4. Keep answers concise and relevant (50-150 words)
5. Use professional but conversational tone

{user_context}
{job_info}

Generate a truthful, professional answer to this screening question:
Question: {question}
Question Type: {question_type}

Respond with a JSON object:
{{
    "answer": "your answer here",
    "confidence": 0.0-1.0,
    "notes": "any relevant notes about the answer"
}}
"""

        try:
            response = await client.chat.completions.create(
                model=settings.OPENAI_MODEL_LIGHT,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Answer this question: {question}"}
                ],
                temperature=0.3,
                max_tokens=500,
                response_format={"type": "json_object"}
            )
            
            import json
            result = json.loads(response.choices[0].message.content)
            
            return {
                "question": question,
                "question_type": question_type,
                "answer": result.get("answer", ""),
                "confidence": result.get("confidence", 0.5),
                "notes": result.get("notes", ""),
                "generated_ai": True
            }
            
        except Exception as e:
            logger.error("Failed to generate answer", error=str(e))
            return {
                "question": question,
                "question_type": question_type,
                "answer": "",
                "confidence": 0.0,
                "notes": "Could not generate answer - please provide manually",
                "generated_ai": False,
                "error": str(e)
            }

    async def generate_answer(self, question: str, user_context: str = None) -> str:
        """
        Generate a direct answer to a screening question.
        Returns the answer text directly.
        """
        if user_context is None:
            user_context = await self.get_user_context()
        
        system_prompt = """You are a career assistant helping answer screening questions.
        Keep answers concise (50-100 words), professional, and truthful.
        Only answer based on the user's actual experience."""
        
        try:
            response = await client.chat.completions.create(
                model=settings.OPENAI_MODEL_LIGHT,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"User Profile:\n{user_context}\n\nQuestion: {question}\n\nProvide a professional answer:"}
                ],
                temperature=0.3,
                max_tokens=300,
            )
            
            return response.choices[0].message.content
        except Exception as e:
            logger.error("Failed to generate answer", error=str(e))
            return "Please answer this question based on your profile."

    async def answer_batch(
        self, 
        questions: List[Dict[str, Any]],
        job_context: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Answer multiple screening questions."""
        answers = []
        
        for q in questions:
            answer = await self.answer_question(
                question=q.get("question", ""),
                question_type=q.get("type", "general"),
                job_context=job_context
            )
            answers.append(answer)
        
        return answers

    async def prepare_application_answers(
        self, 
        job_id: str
    ) -> Dict[str, Any]:
        """
        Prepare common screening answers for a job application.
        Uses AI to predict likely questions and generate answers.
        """
        async with get_db_context() as db:
            # Get job details
            result = await db.execute(
                select(Job).where(Job.id == job_id)
            )
            job = result.scalar_one_or_none()
            
            if not job:
                raise ValueError(f"Job {job_id} not found")
            
            job_context = {
                "title": job.title,
                "company": job.company,
                "requirements": job.description[:500] if job.description else ""
            }
            
            # Common screening question types to prepare for
            common_questions = [
                {"question": "How many years of experience do you have?", "type": "years_experience"},
                {"question": "Are you authorized to work in this location?", "type": "authorization"},
                {"question": "What is your expected salary?", "type": "salary"},
                {"question": "Are you willing to relocate?", "type": "relocation"},
                {"question": "Notice period?", "type": "availability"},
                {"question": "Are you currently employed?", "type": "employment_status"},
            ]
            
            # Generate answers for each
            prepared_answers = []
            for q in common_questions:
                answer = await self.answer_question(
                    question=q["question"],
                    question_type=q["type"],
                    job_context=job_context
                )
                prepared_answers.append(answer)
            
            return {
                "job_id": job_id,
                "job_title": job.title,
                "company": job.company,
                "prepared_answers": prepared_answers,
                "ready_for_apply": True
            }


class JobUpdateMonitor:
    """
    Monitors applied jobs for updates.
    Checks for status changes, new messages, interview requests, etc.
    """

    def __init__(self, db: AsyncSession, user_id: str):
        self.db = db
        self.user_id = user_id

    async def check_applications_for_updates(self) -> List[Dict[str, Any]]:
        """Check all applied jobs for any updates."""
        async with get_db_context() as db:
            result = await db.execute(
                select(Application).where(
                    Application.user_id == self.user_id,
                    Application.status.in_([
                        ApplicationStatus.APPLIED,
                        ApplicationStatus.VIEWED,
                        ApplicationStatus.SHORTLISTED,
                        ApplicationStatus.INTERVIEW_SCHEDULED,
                    ])
                )
            )
            applications = result.scalars().all()
            
            updates = []
            for app in applications:
                update = await self._check_single_application(app)
                if update:
                    updates.append(update)
            
            return updates

    async def _check_single_application(self, application: Application) -> Optional[Dict[str, Any]]:
        """Check a single application for updates."""
        # Get the job
        result = await self.db.execute(
            select(Job).where(Job.id == application.job_id)
        )
        job = result.scalar_one_or_none()
        
        if not job:
            return None
        
        # Check for various update indicators
        updates_detected = []
        
        # 1. Check if job is still active
        if job.is_active is False:
            updates_detected.append({
                "type": "job_closed",
                "message": f"The position at {job.company} is no longer accepting applications"
            })
        
        # 2. Check for new dates/info
        if job.posted_date and not application.applied_at:
            # Job was posted but we haven't applied yet - might be new
            pass
        
        # 3. Check status-based updates
        status_messages = {
                ApplicationStatus.VIEWED: f"Your application for {job.title} at {job.company} was viewed",
                ApplicationStatus.SHORTLISTED: f"Congratulations! You've been shortlisted for {job.title} at {job.company}",
                ApplicationStatus.INTERVIEW_SCHEDULED: f"Interview scheduled for {job.title} at {job.company}",
                ApplicationStatus.REJECTED: f"Update on {job.title} at {job.company} - not moving forward",
            }
            
            current_status = application.status
            if current_status in status_messages:
                return {
                    "application_id": application.id,
                    "job_id": job.id,
                    "job_title": job.title,
                    "company": job.company,
                    "current_status": current_status.value,
                    "update_message": status_messages[current_status],
                    "last_updated": str(application.updated_at),
                    "requires_action": current_status == ApplicationStatus.INTERVIEW_SCHEDULED
                }
            
            return None

    async def get_recent_updates(self, days: int = 7) -> Dict[str, Any]:
        """Get all application updates in the last N days."""
        from datetime import datetime, timedelta
        
        cutoff = datetime.now(timezone.utc) - timedelta(days=days)
        
        async with get_db_context() as db:
            result = await db.execute(
                select(Application).where(
                    Application.user_id == self.user_id,
                    Application.updated_at >= cutoff
                ).order_by(Application.updated_at.desc())
            )
            applications = result.scalars().all()
            
            updates = []
            for app in applications:
                # Get job
                result = await db.execute(
                    select(Job).where(Job.id == app.job_id)
                )
                job = result.scalar_one_or_none()
                
                if job:
                    updates.append({
                        "application_id": app.id,
                        "job_title": job.title,
                        "company": job.company,
                        "status": app.status.value,
                        "updated_at": str(app.updated_at),
                        "applied_at": str(app.applied_at) if app.applied_at else None
                    })
            
            return {
                "total_updates": len(updates),
                "days_lookback": days,
                "updates": updates
            }

    async def notify_new_matches(self) -> Dict[str, Any]:
        """Check for new jobs matching user preferences."""
        async with get_db_context() as db:
            # Get user profile
            result = await db.execute(
                select(UserProfile).where(UserProfile.user_id == self.user_id)
            )
            profile = result.scalar_one_or_none()
            
            if not profile:
                return {"matches": [], "count": 0}
            
            # Get jobs matching preferences
            query = select(Job).where(Job.is_active == True)
            
            # Filter by desired roles if specified
            if profile.desired_roles:
                # Simple match - in production, use full-text search
                role_conditions = []
                for role in profile.desired_roles:
                    role_conditions.append(Job.title.ilike(f"%{role}%"))
                
            result = await db.execute(
                query.where(Job.is_active == True)
                .order_by(Job.posted_date.desc())
                .limit(20)
            )
            jobs = result.scalars().all()
            
            # Filter based on preferences
            matches = []
            for job in jobs:
                # Check if already applied
                result = await db.execute(
                    select(Application).where(
                        Application.user_id == self.user_id,
                        Application.job_id == job.id
                    )
                )
                existing_app = result.scalar_one_or_none()
                
                if existing_app:
                    continue
                
                # Simple matching logic
                match_score = 0
                if profile.desired_roles:
                    for role in profile.desired_roles:
                        if role.lower() in job.title.lower():
                            match_score += 30
                
                if profile.location:
                    if profile.location.lower() in (job.location or "").lower():
                        match_score += 20
                
                if profile.open_to_remote and (job.is_remote or "remote" in (job.location or "").lower()):
                    match_score += 20
                
                if match_score >= 30:
                    matches.append({
                        "job_id": job.id,
                        "title": job.title,
                        "company": job.company,
                        "location": job.location,
                        "is_remote": job.is_remote,
                        "match_score": match_score,
                        "posted_date": str(job.posted_date) if job.posted_date else None,
                        "job_url": job.job_url
                    })
            
            # Sort by match score
            matches.sort(key=lambda x: x["match_score"], reverse=True)
            
            return {
                "matches": matches[:10],
                "count": len(matches)
            }