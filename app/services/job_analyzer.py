"""
app/services/job_analyzer.py
─────────────────────────────
Module 2: Job Description Analyzer
Two-tier analysis:
  Tier 1 (gpt-4o-mini): Fast extraction of skills, requirements, ATS keywords
  Tier 2 (gpt-4o):      Deep match scoring for jobs above 30% skill threshold
"""

from __future__ import annotations

import json
import time
from datetime import datetime, timezone
from typing import Optional

import structlog
from openai import AsyncOpenAI
from sqlalchemy import select

from app.core.config import settings
from app.core.database import get_db_context
from app.models.job import Job, JobAnalysis, JobStatus
from app.models.user import User, UserSkill, UserProfile

logger = structlog.get_logger()
client = AsyncOpenAI(
    api_key=settings.ai_api_key,
    base_url="https://api.groq.com/openai/v1",
)


ANALYSIS_SYSTEM_PROMPT = """
You are an expert technical recruiter and career analyst.
Analyze the provided job description and return ONLY a valid JSON object.
Do not include any text outside the JSON.

The JSON must have exactly these fields:
{
  "required_skills": ["skill1", "skill2"],
  "preferred_skills": ["skill3"],
  "tech_stack": ["Python", "PyTorch"],
  "ats_keywords": ["keyword1", "keyword2"],
  "min_years_experience": 0,
  "max_years_experience": null,
  "education_requirement": "bachelor|master|phd|none",
  "key_responsibilities": ["responsibility1"],
  "role_category": "computer_vision|nlp|mlops|data_science|software_engineering|other",
  "seniority_detected": "entry|mid|senior|lead",
  "is_internship": true,
  "estimated_salary_min": null,
  "estimated_salary_max": null,
  "job_difficulty": "easy|medium|hard",
  "ai_summary": "2-sentence summary of the role",
  "ai_recommendation": null
}
"""

MATCH_SCORING_PROMPT = """
You are a career matching expert. Given a user's profile and a job analysis,
compute a match score and provide a recommendation.

Return ONLY valid JSON:
{
  "match_score": 75.0,
  "skill_match_score": 80.0,
  "experience_match_score": 70.0,
  "matching_skills": ["Python", "PyTorch"],
  "missing_skills": ["Docker", "AWS"],
  "skill_gap_count": 2,
  "competition_level": "medium",
  "interview_probability": 0.35,
  "priority_score": 65.0,
  "ai_recommendation": "Strong match — your PyTorch and OpenCV experience directly aligns. Missing: Docker, AWS (learnable). Apply immediately."
}
"""

# Skill match threshold above which we use the heavy model for deeper scoring
_DEEP_ANALYSIS_THRESHOLD = 30.0


class JobAnalyzerService:
    """
    AI-powered job description analysis service.

    Tier 1 (gpt-4o-mini): Extracts skills, ATS keywords, and job metadata
                           for ALL new jobs quickly and cheaply.
    Tier 2 (gpt-4o):      Deep semantic match scoring for jobs that pass the
                           basic skill-match threshold. This is the model that
                           writes the personalized ai_recommendation.
    """

    async def analyze(self, job_id: str) -> dict:
        """Analyze a single job — full two-tier pipeline."""
        async with get_db_context() as db:
            result = await db.execute(select(Job).where(Job.id == job_id))
            job = result.scalar_one_or_none()
            if not job:
                raise ValueError(f"Job {job_id} not found")

            # Get the first user profile for analysis
            profile_result = await db.execute(select(UserProfile).limit(1))
            profile = profile_result.scalar_one_or_none()
            
            # Get user skills for matching
            skills_result = await db.execute(select(UserSkill).limit(1000))
            skills = skills_result.scalars().all()

            # Tier 1: fast extraction (always runs)
            analysis_data = await self._analyze_description(job)

            # Tier 2: deep match scoring (only for promising jobs)
            match_data = await self._compute_match(analysis_data, profile, skills)

            # Persist
            existing = (await db.execute(
                select(JobAnalysis).where(JobAnalysis.job_id == job_id)
            )).scalar_one_or_none()

            combined = {**analysis_data, **match_data}

            if existing:
                for key, value in combined.items():
                    if hasattr(existing, key):
                        setattr(existing, key, value)
            else:
                analysis = JobAnalysis(job_id=job_id, **{
                    k: v for k, v in combined.items() if hasattr(JobAnalysis, k)
                })
                db.add(analysis)

            job.status = JobStatus.ANALYZED
            await db.commit()

            logger.info(
                "Job analyzed",
                job_id=job_id,
                match_score=match_data.get("match_score"),
                model_tier="heavy" if match_data.get("_used_heavy_model") else "light",
            )
            return {"job_id": job_id, "match_score": match_data.get("match_score")}

    async def analyze_new_batch(self) -> dict:
        """Analyze all NEW jobs using tiered approach."""
        async with get_db_context() as db:
            result = await db.execute(
                select(Job).where(Job.status == JobStatus.NEW).limit(100)
            )
            new_jobs = result.scalars().all()

        analyzed = 0
        for job in new_jobs:
            try:
                await self.analyze(job.id)
                analyzed += 1
            except Exception as e:
                logger.error("Job analysis failed", job_id=job.id, error=str(e))

        return {"analyzed": analyzed, "total_new": len(new_jobs)}

    async def _analyze_description(self, job: Job) -> dict:
        """
        Tier 1: Extract structured data using gpt-4o-mini.
        Fast and cheap — runs on every job.
        """
        description = job.description_clean or job.description_raw or ""
        if not description:
            return self._empty_analysis()

        start = time.time()
        try:
            response = await client.chat.completions.create(
                model=settings.OPENAI_MODEL_LIGHT,  # gpt-4o-mini
                max_tokens=1000,
                temperature=0.1,
                messages=[
                    {"role": "system", "content": ANALYSIS_SYSTEM_PROMPT},
                    {
                        "role": "user",
                        "content": (
                            f"Job Title: {job.title}\n"
                            f"Company: {job.company_name}\n\n"
                            f"Description:\n{description[:8000]}"
                        ),
                    },
                ],
                
            )
            data = json.loads(response.choices[0].message.content)
            data["model_used"] = settings.OPENAI_MODEL_LIGHT
            data["tokens_used"] = response.usage.total_tokens
            data["processing_time_ms"] = int((time.time() - start) * 1000)
            return data
        except Exception as e:
            logger.error("Tier-1 analysis failed", job_id=job.id, error=str(e))
            return self._empty_analysis()

    async def _compute_match(
        self,
        analysis: dict,
        profile: Optional[UserProfile],
        skills: list,
    ) -> dict:
        """
        Tier 2: Score the match against the user profile.

        Uses gpt-4o (heavy model) for jobs with skill_match > threshold.
        Falls back to rule-based scoring for weak matches — saves tokens
        on jobs we'd never apply to anyway.
        """
        if not profile:
            return {
                "match_score": 0.0,
                "matching_skills": [],
                "missing_skills": [],
                "skill_gap_count": 0,
            }

        user_skills = {s.name.lower() for s in skills}
        required = [s.lower() for s in analysis.get("required_skills", [])]
        preferred = [s.lower() for s in analysis.get("preferred_skills", [])]

        matching = [s for s in required + preferred if s in user_skills]
        missing = [s for s in required if s not in user_skills]
        skill_match = (len(matching) / max(len(required), 1)) * 100 if required else 50.0

        # ── Tier 2: heavy model for promising jobs ───────────────
        if skill_match >= _DEEP_ANALYSIS_THRESHOLD:
            try:
                profile_summary = self._build_profile_summary(profile, skills)
                response = await client.chat.completions.create(
                    model=settings.OPENAI_MODEL_HEAVY,  # gpt-4o — the real deal
                    max_tokens=600,
                    temperature=0.1,
                    messages=[
                        {"role": "system", "content": MATCH_SCORING_PROMPT},
                        {
                            "role": "user",
                            "content": (
                                f"USER PROFILE:\n{profile_summary}\n\n"
                                f"JOB ANALYSIS:\n{json.dumps(analysis, indent=2)[:3000]}"
                            ),
                        },
                    ],
                    response_format={"type": "json_object"},
                )
                match_data = json.loads(response.choices[0].message.content)
                # Override with our computed lists (more accurate than LLM's guess)
                match_data["matching_skills"] = matching
                match_data["missing_skills"] = missing
                match_data["skill_gap_count"] = len(missing)
                match_data["_used_heavy_model"] = True
                return match_data
            except Exception as e:
                logger.error("Tier-2 match scoring failed", error=str(e))
                # Fall through to rule-based

        # ── Fallback: rule-based scoring for weak/failed matches ─
        return {
            "match_score": round(skill_match, 1),
            "skill_match_score": round(skill_match, 1),
            "experience_match_score": 50.0,
            "matching_skills": matching,
            "missing_skills": missing,
            "skill_gap_count": len(missing),
            "competition_level": "medium",
            "interview_probability": skill_match / 200,
            "priority_score": skill_match * 0.6,
            "ai_recommendation": (
                f"Skill match: {skill_match:.0f}%. "
                f"Missing: {', '.join(missing[:3]) or 'none'}."
            ),
            "_used_heavy_model": False,
        }

    def _build_profile_summary(self, profile: UserProfile, skills: list) -> str:
        skill_names = ", ".join(s.name for s in skills[:30])
        roles = ", ".join(profile.desired_roles[:5]) if profile.desired_roles else "ML/AI roles"
        return (
            f"Experience Level: {profile.experience_level}\n"
            f"Target Roles: {roles}\n"
            f"Skills: {skill_names}\n"
            f"Summary: {profile.professional_summary or 'AI/ML developer'}"
        )

    def _empty_analysis(self) -> dict:
        return {
            "required_skills": [], "preferred_skills": [], "tech_stack": [],
            "ats_keywords": [], "key_responsibilities": [], "role_category": "other",
            "seniority_detected": "unknown", "is_internship": False,
            "job_difficulty": "medium", "ai_summary": "", "model_used": None,
            "tokens_used": 0, "processing_time_ms": 0,
        }


# Canonical re-export — NotificationService lives in its own module
from app.services.notification_service import NotificationService  # noqa: F401