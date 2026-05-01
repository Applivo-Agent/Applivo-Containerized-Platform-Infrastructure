"""
app/services/job_analyzer.py
───────────────────────────
Module 2: Lightweight Job Analyzer
Optimized version:
  - Batch 5 jobs per API call
    - Title/metadata-based AI analysis (no full JD parsing)
    - Rule-based match scoring
  - Dual AI provider: Groq (primary) + Gemini (fallback)
  - Smaller output tokens
"""

from __future__ import annotations

import json
import time
import asyncio
from datetime import datetime, timezone
from typing import Optional

import structlog
from sqlalchemy import select, or_

from app.core.config import settings
from app.core.database import get_db_context
from app.models.job import Job, JobAnalysis, JobStatus
from app.models.user import User, UserSkill, UserProfile
from app.services.ai_router import ai_router

logger = structlog.get_logger()

BATCH_SIZE = 5
MAX_TOKENS_PER_JOB = 220

ANALYSIS_SYSTEM_PROMPT = """
You are an expert technical recruiter. Analyze ONLY job title + metadata (no full description) and return ONLY valid JSON.
Process up to 5 jobs at once. Return a JSON ARRAY with results for each job.
Each job result must have exactly these fields:
{
  "job_index": 0,
  "required_skills": ["skill1", "skill2"],
  "preferred_skills": ["skill3"],
  "tech_stack": ["Python", "PyTorch"],
  "ats_keywords": ["keyword1", "keyword2"],
  "min_years_experience": 0,
  "education_requirement": "bachelor|master|phd|none",
  "key_responsibilities": ["responsibility1"],
  "role_category": "computer_vision|nlp|mlops|data_science|software_engineering|other",
  "seniority_detected": "entry|mid|senior|lead",
  "is_internship": true,
  "job_difficulty": "easy|medium|hard",
  "ai_summary": "2-sentence summary"
}
"""


class JobAnalyzerService:
    """AI-powered job description analysis with batching and rule-based matching."""

    async def analyze_user_new_or_unanalyzed(
        self,
        user_id: str,
        limit: int = 100,
        max_run_tokens: Optional[int] = None,
        max_month_tokens_remaining: Optional[int] = None,
    ) -> dict:
        """Analyze only NEW or not-yet-analyzed jobs for a specific user using 5-job batching."""
        async with get_db_context() as db:
            result = await db.execute(
                select(Job)
                .outerjoin(JobAnalysis, Job.id == JobAnalysis.job_id)
                .where(
                    Job.is_active == True,
                    Job.user_id == user_id,
                    or_(Job.status == JobStatus.NEW, JobAnalysis.id == None),
                )
                .limit(limit)
            )
            candidate_jobs = result.scalars().all()

        if not candidate_jobs:
            return {
                "analyzed": 0,
                "total_candidates": 0,
                "batches": 0,
                "tokens_used": 0,
                "budget_exhausted": False,
                "budget_reason": None,
            }

        analyzed = 0
        batch_count = 0
        tokens_used_total = 0
        budget_exhausted = False
        budget_reason = None

        for i in range(0, len(candidate_jobs), BATCH_SIZE):
            batch = candidate_jobs[i:i + BATCH_SIZE]
            remaining_budget = None
            if max_run_tokens is not None:
                remaining_budget = max(0, max_run_tokens - tokens_used_total)
            if max_month_tokens_remaining is not None:
                monthly_remaining_after_run = max(0, max_month_tokens_remaining - tokens_used_total)
                remaining_budget = monthly_remaining_after_run if remaining_budget is None else min(remaining_budget, monthly_remaining_after_run)

            if remaining_budget is not None and remaining_budget <= 0:
                budget_exhausted = True
                budget_reason = "Analyze token budget reached"
                break

            batch_count += 1
            try:
                results, batch_tokens = await self._analyze_batch_with_usage(batch)
                tokens_used_total += int(batch_tokens or 0)
                for job, analysis in zip(batch, results):
                    if analysis:
                        await self._save_analysis(job, analysis)
                        analyzed += 1
            except Exception as e:
                logger.error("User batch analysis failed", user_id=user_id, batch=i // BATCH_SIZE, error=str(e))

        return {
            "analyzed": analyzed,
            "total_candidates": len(candidate_jobs),
            "batches": batch_count,
            "tokens_used": tokens_used_total,
            "budget_exhausted": budget_exhausted,
            "budget_reason": budget_reason,
        }

    async def analyze(self, job_id: str) -> dict:
        """Analyze a single job."""
        async with get_db_context() as db:
            result = await db.execute(select(Job).where(Job.id == job_id))
            job = result.scalar_one_or_none()
            if not job:
                raise ValueError(f"Job {job_id} not found")

            profile_result = await db.execute(select(UserProfile).limit(1))
            profile = profile_result.scalar_one_or_none()
            
            skills_result = await db.execute(select(UserSkill).limit(1000))
            skills = skills_result.scalars().all()

            analysis_data = await self._analyze_single(job)
            match_data = self._rule_based_match(analysis_data, profile, skills)

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

            logger.info("Job analyzed", job_id=job_id, match_score=match_data.get("match_score"))
            return {"job_id": job_id, "match_score": match_data.get("match_score")}

    async def analyze_new_batch(self) -> dict:
        """Analyze all NEW jobs using batched approach."""
        async with get_db_context() as db:
            result = await db.execute(
                select(Job).where(Job.status == JobStatus.NEW).limit(100)
            )
            new_jobs = result.scalars().all()

        if not new_jobs:
            return {"analyzed": 0, "total_new": 0, "batches": 0}

        jobs_list = list(new_jobs)
        analyzed = 0
        batch_count = 0

        for i in range(0, len(jobs_list), BATCH_SIZE):
            batch = jobs_list[i:i + BATCH_SIZE]
            batch_count += 1
            try:
                results = await self._analyze_batch(batch)
                for job, analysis in zip(batch, results):
                    if analysis:
                        await self._save_analysis(job, analysis)
                        analyzed += 1
            except Exception as e:
                logger.error("Batch analysis failed", batch=i//BATCH_SIZE, error=str(e))

        return {"analyzed": analyzed, "total_new": len(jobs_list), "batches": batch_count}

    async def _analyze_single(self, job: Job) -> dict:
        """Analyze a single job description."""
        return (await self._analyze_batch([job]))[0] or self._empty_analysis()

    async def _analyze_batch(self, jobs: list) -> list:
        """Analyze a batch and return only job-wise analysis payloads."""
        results, _ = await self._analyze_batch_with_usage(jobs)
        return results

    async def _analyze_batch_with_usage(self, jobs: list) -> tuple[list, int]:
        """Analyze a batch of jobs in one API call using title-only metadata."""
        if not jobs:
            return [], 0

        start = time.time()
        jobs_content = []
        
        for idx, job in enumerate(jobs):
            jobs_content.append(
                "\n".join([
                    f"---JOB {idx}---",
                    f"Title: {job.title or ''}",
                    f"Company: {job.company_name or ''}",
                    f"Location: {job.location or job.city or ''}",
                    f"Job Type: {job.job_type or ''}",
                    f"Work Mode: {job.work_mode or ''}",
                    f"Experience Level: {job.experience_level or ''}",
                ])
            )

        combined_content = "\n\n".join(jobs_content)
        max_tokens = MAX_TOKENS_PER_JOB * len(jobs)

        try:
            # Use AI router for dual-provider support (Groq + Gemini fallback)
            result = await ai_router.chat_completions_create(
                messages=[
                    {"role": "system", "content": ANALYSIS_SYSTEM_PROMPT},
                    {"role": "user", "content": combined_content},
                ],
                model=settings.OPENAI_MODEL_LIGHT,
                max_tokens=max_tokens,
                temperature=0.1,
            )
            
            content = result["content"]
            tokens_used = result.get("usage", {}).get("total_tokens", 0)
            provider = result.get("provider", "unknown")
            
            try:
                results = self._extract_json(content)
                if not isinstance(results, list):
                    results = [results]
            except Exception:
                logger.error("Failed to parse batch response", content=content[:500])
                return [self._empty_analysis() for _ in jobs], 0

            while len(results) < len(jobs):
                results.append(self._empty_analysis())
            
            for r in results:
                r["model_used"] = settings.OPENAI_MODEL_LIGHT
                r["ai_provider"] = provider
                r["tokens_used"] = tokens_used // len(jobs)
                r["processing_time_ms"] = int((time.time() - start) * 1000)

            return results, tokens_used

        except Exception as e:
            logger.error("Batch API call failed", error=str(e))
            return [self._empty_analysis() for _ in jobs], 0

    def _rule_based_match(
        self,
        analysis: dict,
        profile: Optional[UserProfile],
        skills: list,
    ) -> dict:
        """Rule-based match scoring - no API calls needed."""
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
        preferred_match = (len([s for s in preferred if s in user_skills]) / max(len(preferred), 1)) * 100 if preferred else 50.0
        
        match_score = (skill_match * 0.7) + (preferred_match * 0.3)
        
        exp_level = profile.experience_level or "mid"
        seniority = analysis.get("seniority_detected", "mid")
        
        if exp_level == "senior" and seniority in ["entry", "mid"]:
            exp_match = 80
        elif exp_level == "entry" and seniority in ["senior", "lead"]:
            exp_match = 40
        else:
            exp_match = 70

        final_score = (match_score * 0.6) + (exp_match * 0.4)
        priority = final_score * 0.7 if final_score > 50 else final_score * 0.5

        recommendation = self._generate_recommendation(match_score, matching, missing, final_score)

        return {
            "match_score": round(final_score, 1),
            "skill_match_score": round(match_score, 1),
            "experience_match_score": exp_match,
            "matching_skills": matching,
            "missing_skills": missing,
            "skill_gap_count": len(missing),
            "competition_level": "low" if final_score > 70 else "medium" if final_score > 40 else "high",
            "interview_probability": final_score / 200,
            "priority_score": round(priority, 1),
            "ai_recommendation": recommendation,
            "_used_heavy_model": False,
        }

    def _generate_recommendation(self, skill_match: float, matching: list, missing: list, final: float) -> str:
        """Generate a recommendation string."""
        if final > 70:
            return f"Strong match! {len(matching)} skills align. Apply now."
        elif final > 50:
            missing_str = ", ".join(missing[:3]) if missing else "none"
            return f"Good match ({skill_match:.0f}% skill). Missing: {missing_str}"
        elif final > 30:
            return f"Partial match ({skill_match:.0f}%). Consider if desperate."
        else:
            return "Low match score. Skip unless no other options."

    async def _save_analysis(self, job: Job, analysis: dict):
        """Save analysis results to database."""
        async with get_db_context() as db:
            profile_result = await db.execute(select(UserProfile).limit(1))
            profile = profile_result.scalar_one_or_none()
            
            skills_result = await db.execute(select(UserSkill).limit(1000))
            skills = skills_result.scalars().all()
            
            match_data = self._rule_based_match(analysis, profile, skills)
            
            existing = (await db.execute(
                select(JobAnalysis).where(JobAnalysis.job_id == job.id)
            )).scalar_one_or_none()

            combined = {**analysis, **match_data}

            if existing:
                for key, value in combined.items():
                    if hasattr(existing, key):
                        setattr(existing, key, value)
            else:
                analysis_obj = JobAnalysis(job_id=job.id, **{
                    k: v for k, v in combined.items() if hasattr(JobAnalysis, k)
                })
                db.add(analysis_obj)

            # Re-attach and persist the job to save dynamically fetched descriptions & status
            merged_job = await db.merge(job)
            merged_job.status = JobStatus.ANALYZED
            await db.commit()

    def _extract_json(self, content: str) -> list | dict:
        """Robustly extract JSON from AI response that might have markdown or notes."""
        content = content.strip()
        
        # Try direct load first
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            pass
            
        # Try extracting from markdown blocks
        import re
        json_pattern = re.compile(r"```json\s*((\[|\{).*?(\]|\}))\s*```", re.DOTALL)
        match = json_pattern.search(content)
        if match:
            try:
                return json.loads(match.group(1))
            except json.JSONDecodeError:
                pass
                
        # Try finding the first [ and last ] or first { and last }
        try:
            array_start = content.find("[")
            array_end = content.rfind("]")
            if array_start != -1 and array_end != -1:
                return json.loads(content[array_start:array_end+1])
                
            obj_start = content.find("{")
            obj_end = content.rfind("}")
            if obj_start != -1 and obj_end != -1:
                return json.loads(content[obj_start:obj_end+1])
        except Exception:
            pass
            
        raise ValueError("Could not extract valid JSON from content")

    def _empty_analysis(self) -> dict:
        return {
            "required_skills": [], "preferred_skills": [], "tech_stack": [],
            "ats_keywords": [], "key_responsibilities": [], "role_category": "other",
            "seniority_detected": "unknown", "is_internship": False,
            "job_difficulty": "medium", "ai_summary": "Title-only analysis fallback.", "model_used": None,
            "ai_provider": None,
            "tokens_used": 0, "processing_time_ms": 0,
        }

    async def _fetch_missing_descriptions(self, jobs: list):
        """Fetch missing HTML text for jobs on-the-fly if description is empty."""
        import httpx
        from bs4 import BeautifulSoup
        import re

        async def fetch_desc(job: Job):
            if not job.description_raw and not job.description_clean:
                if job.source_url:
                    try:
                        async with httpx.AsyncClient(follow_redirects=True, timeout=10) as client:
                            resp = await client.get(
                                job.source_url, 
                                headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
                            )
                            if resp.status_code == 200:
                                soup = BeautifulSoup(resp.text, 'html.parser')
                                # Try specific container, fallback to body
                                details = soup.find("div", class_=re.compile(r"detail_view|internship_details|text-container|job-description", re.I))
                                if not details:
                                    details = soup.body
                                if details:
                                    text = details.get_text(" ", strip=True)
                                    job.description_raw = text
                                    job.description_clean = text
                    except Exception as e:
                        logger.warning("Failed to fetch missing JD", job_id=job.id, error=str(e))
                        
        import asyncio
        await asyncio.gather(*(fetch_desc(j) for j in jobs))