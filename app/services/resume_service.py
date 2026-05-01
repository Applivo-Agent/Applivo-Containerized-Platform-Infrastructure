"""
app/services/resume_service.py
────────────────────────────────
Module 3: Resume Optimization Engine
AI-powered resume tailoring using GPT-4o.
Rewrites bullet points, injects ATS keywords, generates PDFs.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Optional

import structlog
from openai import AsyncOpenAI
from sqlalchemy import select, desc

from app.core.config import settings
from app.core.database import get_db_context
from app.models.job import Job, JobAnalysis
from app.models.resume import Resume, ResumeType
from app.models.user import User, UserProfile, UserSkill
from app.models.application import Application

logger = structlog.get_logger()
client = AsyncOpenAI(
    api_key=settings.ai_api_key,
    base_url="https://api.groq.com/openai/v1",
)

RESUME_TAILORING_PROMPT = """
You are an expert resume writer and ATS optimization specialist.

Given the user's base resume content and a job description analysis, 
rewrite and optimize the resume to maximize ATS score and match score.

Rules:
- Inject the required ATS keywords naturally into bullet points
- Rewrite bullet points to highlight relevant experience
- Use strong action verbs (Developed, Implemented, Optimized, Built, Designed)
- Keep all facts truthful — only reword, never fabricate
- Prioritize experiences most relevant to this job
- Keep it to 1 page worth of content

Return ONLY valid JSON:
{
  "summary": "Rewritten professional summary targeting this role",
  "experience_bullets": {
    "job_title_at_company": ["bullet 1", "bullet 2"]
  },
  "project_bullets": {
    "project_name": ["bullet 1", "bullet 2"]
  },
  "skills_to_highlight": ["skill1", "skill2"],
  "keywords_injected": ["keyword1", "keyword2"],
  "ats_score_estimate": 82
}
"""


class ResumeService:

    async def generate_tailored(
        self,
        user_id: str,
        job_id: str,
        base_resume_id: Optional[str] = None,
    ) -> dict:
        """Generate a tailored resume for a specific job using GPT-4o."""
        async with get_db_context() as db:
            # Load job + analysis
            job_result = await db.execute(
                select(Job, JobAnalysis)
                .join(JobAnalysis, Job.id == JobAnalysis.job_id)
                .where(Job.id == job_id)
            )
            row = job_result.first()
            if not row:
                raise ValueError(f"Job {job_id} not found or not analyzed yet")
            job, analysis = row

            # Load user profile + skills
            profile = (await db.execute(
                select(UserProfile).where(UserProfile.user_id == user_id)
            )).scalar_one_or_none()

            skills = (await db.execute(
                select(UserSkill).where(UserSkill.user_id == user_id)
            )).scalars().all()

            # Load base resume content
            base_resume = None
            if base_resume_id:
                base_resume = (await db.execute(
                    select(Resume).where(Resume.id == base_resume_id)
                )).scalar_one_or_none()
            else:
                # Use default base resume
                base_resume = (await db.execute(
                    select(Resume).where(
                        Resume.user_id == user_id,
                        Resume.is_default == True,
                        Resume.resume_type == ResumeType.BASE,
                    )
                )).scalar_one_or_none()

            # Build profile context
            profile_context = self._build_profile_context(profile, skills, base_resume)
            job_context = self._build_job_context(job, analysis)

            # Call GPT-4o for tailoring
            try:
                response = await client.chat.completions.create(
                    model=settings.OPENAI_MODEL_HEAVY,
                    max_tokens=2000,
                    temperature=0.2,
                    messages=[
                        {"role": "system", "content": RESUME_TAILORING_PROMPT},
                        {"role": "user", "content": f"BASE RESUME:\n{profile_context}\n\nTARGET JOB:\n{job_context}"},
                    ],
                
                )
                content = response.choices[0].message.content
                if not content or content.startswith("% Error"):
                    logger.warning("Resume generation returned empty or error", content=content)
                    raise ValueError("LLM returned empty response")
                # Strip markdown code blocks if present
                content = content.strip()
                if content.startswith("```"):
                    content = content.split("```")[1]
                    if content.startswith("json"):
                        content = content[4:]
                    content = content.strip()
                tailored_data = json.loads(content)
                tokens_used = response.usage.total_tokens
            except Exception as e:
                logger.error("Resume generation LLM failed", error=str(e))
                raise

            # Create resume record
            version = await self._get_next_version(db, user_id, job.title)
            resume_name = f"resume_{job.company_name.lower().replace(' ', '_')}_{job.title.lower().replace(' ', '_')[:20]}"

            new_resume = Resume(
                user_id=user_id,
                name=resume_name,
                version=version,
                resume_type=ResumeType.TAILORED,
                role_category=analysis.role_category,
                target_job_id=job_id,
                content_json=tailored_data,
                keywords_injected=tailored_data.get("keywords_injected", []),
                ats_score=tailored_data.get("ats_score_estimate"),
                is_active=True,
            )
            db.add(new_resume)
            await db.commit()
            await db.refresh(new_resume)

            # Generate PDF
            try:
                pdf_path = await self._generate_pdf(new_resume, profile, tailored_data)
                new_resume.file_path = pdf_path
                await db.commit()
            except Exception as e:
                logger.warning("PDF generation failed", error=str(e))

            logger.info("Resume generated", resume_id=new_resume.id, job_id=job_id)
            return {
                "resume_id": new_resume.id,
                "name": new_resume.name,
                "ats_score": new_resume.ats_score,
                "keywords_injected": new_resume.keywords_injected,
                "tokens_used": tokens_used,
            }

    async def generate_for_top_jobs(self) -> dict:
        """Generate resumes for all high-match jobs that don't have one yet."""
        async with get_db_context() as db:
            from app.models.job import JobStatus
            result = await db.execute(
                select(Job)
                .join(JobAnalysis, Job.id == JobAnalysis.job_id)
                .where(
                    Job.is_active == True,
                    Job.status == JobStatus.ANALYZED,
                    JobAnalysis.match_score >= settings.AUTO_APPLY_MATCH_THRESHOLD,
                )
                .order_by(desc(JobAnalysis.match_score))
                .limit(10)
            )
            jobs = result.scalars().all()

            # Get user_id from first user
            user_result = await db.execute(select(User).limit(1))
            user = user_result.scalar_one_or_none()
            if not user:
                return {"generated": 0}

        generated = 0
        for job in jobs:
            try:
                await self.generate_tailored(user.id, job.id)
                generated += 1
            except Exception as e:
                logger.error("Failed to generate resume for job", job_id=job.id, error=str(e))

        return {"generated": generated}

    async def update_performance_metrics(self) -> None:
        """Recalculate response_rate for all resume versions."""
        async with get_db_context() as db:
            resumes = (await db.execute(
                select(Resume).where(Resume.times_used > 0)
            )).scalars().all()

            for resume in resumes:
                if resume.times_used > 0:
                    resume.response_rate = round(
                        resume.response_count / resume.times_used * 100, 1
                    )
            await db.commit()

    def _build_profile_context(
        self,
        profile: Optional[UserProfile],
        skills: list,
        base_resume: Optional[Resume],
    ) -> str:
        if not profile:
            return "No profile data available."

        skill_names = ", ".join(s.name for s in skills[:30])
        projects = "\n".join(
            f"  - {p.get('name', '')}: {p.get('description', '')} | Stack: {', '.join(p.get('tech_stack', []))}"
            for p in (profile.projects or [])[:5]
        )
        experience = "\n".join(
            f"  - {e.get('title', '')} at {e.get('company', '')} ({e.get('start', '')} - {e.get('end', 'Present')})"
            for e in (profile.work_experience or [])[:3]
        )

        # If we have existing resume JSON, use it
        base_content = ""
        if base_resume and base_resume.content_json:
            base_content = f"\nExisting resume content:\n{json.dumps(base_resume.content_json, indent=2)[:2000]}"

        return f"""
Name: {profile.user_id}
Experience Level: {profile.experience_level}
Summary: {profile.professional_summary or 'AI/ML student and developer'}
Skills: {skill_names}

Work Experience:
{experience or '  None listed'}

Projects:
{projects or '  None listed'}
{base_content}
"""

    def _build_job_context(self, job: Job, analysis: JobAnalysis) -> str:
        return f"""
Title: {job.title}
Company: {job.company_name}
Required Skills: {', '.join(analysis.required_skills)}
Preferred Skills: {', '.join(analysis.preferred_skills)}
ATS Keywords: {', '.join(analysis.ats_keywords)}
Key Responsibilities: {chr(10).join(f'  - {r}' for r in analysis.key_responsibilities[:5])}
Role Category: {analysis.role_category}
Missing from user profile: {', '.join(analysis.missing_skills)}
"""

    async def _get_next_version(self, db, user_id: str, role: str) -> int:
        result = await db.execute(
            select(Resume)
            .where(Resume.user_id == user_id, Resume.resume_type == ResumeType.TAILORED)
            .order_by(desc(Resume.version))
            .limit(1)
        )
        latest = result.scalar_one_or_none()
        return (latest.version + 1) if latest else 1

    async def _generate_pdf(
        self,
        resume: Resume,
        profile: Optional[UserProfile],
        tailored_data: dict,
    ) -> str:
        """Generate a PDF resume file. Returns relative file path."""
        from app.core.config import settings
        import uuid

        file_name = f"{uuid.uuid4()}.pdf"
        file_path = settings.resumes_path / file_name

        # Build HTML template for PDF
        html = self._build_resume_html(profile, tailored_data)

        try:
            # Try WeasyPrint first
            import weasyprint
            weasyprint.HTML(string=html).write_pdf(str(file_path))
        except ImportError:
            # Fallback: save as HTML if WeasyPrint not available
            html_path = settings.resumes_path / f"{uuid.uuid4()}.html"
            with open(html_path, "w", encoding="utf-8") as f:
                f.write(html)
            return str(html_path.relative_to(settings.storage_path))

        return str(file_path.relative_to(settings.storage_path))

    def _build_resume_html(self, profile: Optional[UserProfile], data: dict) -> str:
        name = profile.user_id if profile else "Candidate"
        summary = data.get("summary", "")
        skills = ", ".join(data.get("skills_to_highlight", []))

        exp_html = ""
        for role, bullets in data.get("experience_bullets", {}).items():
            bullet_html = "".join(f"<li>{b}</li>" for b in bullets)
            exp_html += f"<h3>{role}</h3><ul>{bullet_html}</ul>"

        proj_html = ""
        for proj, bullets in data.get("project_bullets", {}).items():
            bullet_html = "".join(f"<li>{b}</li>" for b in bullets)
            proj_html += f"<h3>{proj}</h3><ul>{bullet_html}</ul>"

        return f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
  body {{ font-family: Arial, sans-serif; margin: 40px; font-size: 11pt; color: #222; }}
  h1 {{ color: #1a1a2e; border-bottom: 2px solid #00d4ff; padding-bottom: 6px; }}
  h2 {{ color: #16213e; font-size: 13pt; margin-top: 20px; border-bottom: 1px solid #ddd; }}
  h3 {{ font-size: 11pt; margin: 8px 0 4px 0; color: #333; }}
  ul {{ margin: 4px 0; padding-left: 18px; }}
  li {{ margin-bottom: 3px; }}
  .skills {{ background: #f5f5f5; padding: 8px; border-radius: 4px; }}
</style>
</head>
<body>
  <h1>{name}</h1>
  <p>{summary}</p>

  <h2>Skills</h2>
  <div class="skills">{skills}</div>

  <h2>Experience</h2>
  {exp_html or '<p>See projects below.</p>'}

  <h2>Projects</h2>
  {proj_html or '<p>Available upon request.</p>'}
</body>
</html>
"""