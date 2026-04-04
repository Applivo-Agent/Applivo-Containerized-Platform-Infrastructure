"""
app/services/cover_letter_service.py
──────────────────────────────────────
Module 4: Cover Letter Generator
Generates tailored cover letters per job using GPT-4o.
"""

from __future__ import annotations

import json
from typing import Optional

import structlog
from openai import AsyncOpenAI

from app.core.config import settings

logger = structlog.get_logger()

if settings.ai_api_key:
    client = AsyncOpenAI(
        api_key=settings.ai_api_key,
        base_url="https://api.groq.com/openai/v1",
    )
else:
    client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

COVER_LETTER_PROMPT = """
You are an expert career coach writing a personalized cover letter.

Write a compelling, specific cover letter that:
- Opens with a strong hook mentioning the company and role
- Highlights 2-3 specific skills/projects that match the job requirements
- Shows genuine interest in the company (reference their products/mission)
- Ends with a confident call to action
- Sounds human, not AI-generated
- Is {tone} in tone
- Is 250-300 words maximum
- Include your profile links at the end in the signature

Return ONLY valid JSON:
{{
  "content": "Full cover letter text here...",
  "highlighted_skills": ["skill1", "skill2", "skill3"],
  "word_count": 275
}}
"""


class CoverLetterService:

    async def generate(
        self,
        user_id: str,
        job_id: str,
        tone: str = "professional",
        additional_context: Optional[str] = None,
    ) -> dict:
        """Generate a tailored cover letter for a specific job."""
        async with get_db_context() as db:
            # Load job + analysis
            job_result = await db.execute(
                select(Job, JobAnalysis)
                .join(JobAnalysis, Job.id == JobAnalysis.job_id)
                .where(Job.id == job_id)
            )
            row = job_result.first()
            if not row:
                raise ValueError(f"Job {job_id} not found or not analyzed")
            job, analysis = row

            # Load profile
            profile = (await db.execute(
                select(UserProfile).where(UserProfile.user_id == user_id)
            )).scalar_one_or_none()

            skills = (await db.execute(
                select(UserSkill).where(UserSkill.user_id == user_id)
            )).scalars().all()

            # Build context
            user_context = self._build_user_context(profile, skills, analysis)
            job_context = f"""
Company: {job.company_name}
Role: {job.title}
Location: {job.location or 'Remote/Flexible'}
Required Skills: {', '.join(analysis.required_skills[:8])}
Key Responsibilities: {'; '.join(analysis.key_responsibilities[:3])}
Job Summary: {analysis.ai_summary or job.description_clean[:500] if job.description_clean else ''}
"""
            if additional_context:
                job_context += f"\nExtra context: {additional_context}"

            prompt = COVER_LETTER_PROMPT.format(tone=tone)

            try:
                response = await client.chat.completions.create(
                    model=settings.OPENAI_MODEL_HEAVY,
                    max_tokens=800,
                    temperature=0.4,
                    messages=[
                        {"role": "system", "content": prompt},
                        {"role": "user", "content": f"USER PROFILE:\n{user_context}\n\nJOB:\n{job_context}"},
                    ],
                    response_format={"type": "json_object"},
                )
                data = json.loads(response.choices[0].message.content)
                tokens_used = response.usage.total_tokens
            except Exception as e:
                logger.error("Cover letter generation failed", error=str(e))
                raise

            # Save to DB
            cover_letter = CoverLetter(
                user_id=user_id,
                job_id=job_id,
                content=data.get("content", ""),
                tone=tone,
                target_company=job.company_name,
                target_role=job.title,
                highlighted_skills=data.get("highlighted_skills", []),
                word_count=data.get("word_count"),
                model_used=settings.OPENAI_MODEL_HEAVY,
                tokens_used=tokens_used,
            )
            db.add(cover_letter)
            await db.commit()
            await db.refresh(cover_letter)

            logger.info("Cover letter generated", cl_id=cover_letter.id, job_id=job_id)
            return {
                "cover_letter_id": cover_letter.id,
                "target_company": job.company_name,
                "target_role": job.title,
                "word_count": cover_letter.word_count,
                "tokens_used": tokens_used,
            }

    def _build_user_context(self, profile: Optional[UserProfile], skills: list, analysis: JobAnalysis) -> str:
        if not profile:
            return "No profile available."

        matching = ", ".join(analysis.matching_skills[:10])
        skill_names = ", ".join(s.name for s in skills[:20])
        projects = "; ".join(
            p.get("name", "") + ": " + p.get("description", "")[:80]
            for p in (profile.projects or [])[:3]
        )
        
        # Get profile links from settings
        linkedin_url = settings.USER_LINKEDIN_URL or "https://linkedin.com/in/yourprofile"
        github_url = settings.USER_GITHUB_URL or "https://github.com/yourusername"

        return f"""
Experience Level: {profile.experience_level}
Location: {profile.location}
Summary: {profile.professional_summary or 'Passionate AI/ML developer'}
Skills: {skill_names}
Matching skills for this job: {matching}
Key projects: {projects or 'Available on portfolio'}
Career goals: {profile.career_goals or 'Seeking impactful AI/ML role'}

PROFILE LINKS (include in your signature):
- LinkedIn: {linkedin_url}
- GitHub: {github_url}
"""
