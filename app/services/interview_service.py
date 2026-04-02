"""
app/services/interview_service.py
────────────────────────────────────
Module 18: Interview Preparation Engine
Auto-generates company reports, question banks, and study plans
when an interview is scheduled.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone

import structlog
from openai import AsyncOpenAI
from sqlalchemy import select

from app.core.config import settings
from app.core.database import get_db_context
from app.models.application import Application
from app.models.job import Job, JobAnalysis
from app.models.interview import Interview
from app.models.user import UserProfile, UserSkill

logger = structlog.get_logger()
client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

INTERVIEW_PREP_PROMPT = """
You are an expert technical interview coach.
Given the job details and user profile, generate interview preparation material.

Return ONLY valid JSON:
{
  "technical_questions": [
    {
      "question": "Explain the difference between ResNet and EfficientNet",
      "expected_answer": "ResNet uses residual connections to...",
      "difficulty": "medium",
      "topic": "Deep Learning Architecture"
    }
  ],
  "behavioral_questions": [
    {
      "question": "Tell me about a time you debugged a complex ML model",
      "framework": "STAR",
      "key_points": ["Situation", "Action", "Result"]
    }
  ],
  "study_topics": ["CNN architectures", "Transfer Learning", "Model optimization"],
  "company_tips": "Focus on their use of PyTorch. They care about production-ready code.",
  "estimated_difficulty": "medium"
}
"""

COMPANY_RESEARCH_PROMPT = """
Generate a brief company intelligence report for interview preparation.
Return ONLY valid JSON:
{
  "company_overview": "2 sentence overview",
  "key_products": ["product1", "product2"],
  "tech_stack": ["Python", "PyTorch", "Kubernetes"],
  "company_culture": "Brief culture description",
  "interview_style": "Known interview style/format",
  "talking_points": ["Point 1 to mention", "Point 2"],
  "questions_to_ask": ["Question 1 for interviewer", "Question 2"]
}
"""


class InterviewPrepService:

    async def prepare(self, interview_id: str) -> dict:
        """
        Generate full interview prep package:
        - Company report
        - Technical questions
        - Behavioral questions
        - Study topics
        """
        async with get_db_context() as db:
            # Load interview
            interview = (await db.execute(
                select(Interview).where(Interview.id == interview_id)
            )).scalar_one_or_none()
            if not interview:
                raise ValueError(f"Interview {interview_id} not found")

            # Load application + job
            app = (await db.execute(
                select(Application).where(Application.id == interview.application_id)
            )).scalar_one_or_none()

            job_result = await db.execute(
                select(Job, JobAnalysis)
                .join(JobAnalysis, Job.id == JobAnalysis.job_id)
                .where(Job.id == app.job_id)
            )
            row = job_result.first()
            if not row:
                raise ValueError("Job not found")
            job, analysis = row

            # Load user profile
            profile = (await db.execute(
                select(UserProfile).where(UserProfile.user_id == interview.user_id)
            )).scalar_one_or_none()

            skills = (await db.execute(
                select(UserSkill).where(UserSkill.user_id == interview.user_id)
            )).scalars().all()

            # Generate company report
            company_report = await self._generate_company_report(job)

            # Generate question bank
            questions = await self._generate_questions(job, analysis, profile, skills, interview.interview_type)

            # Update interview record
            interview.company_report = company_report
            interview.technical_questions = questions.get("technical_questions", [])
            interview.behavioral_questions = questions.get("behavioral_questions", [])
            interview.study_topics = questions.get("study_topics", [])
            await db.commit()

            # Send notification
            from app.services.job_analyzer import NotificationService
            scheduled_str = interview.scheduled_at.strftime("%B %d at %I:%M %p") if interview.scheduled_at else "soon"
            await NotificationService().notify(
                title=f"🎯 Interview Prep Ready — {job.company_name}",
                body=(
                    f"Your {interview.interview_type} interview with {job.company_name} is scheduled {scheduled_str}.\n\n"
                    f"Prep material generated:\n"
                    f"• {len(interview.technical_questions)} technical questions\n"
                    f"• {len(interview.behavioral_questions)} behavioral questions\n"
                    f"• {len(interview.study_topics)} study topics\n\n"
                    f"Top tip: {company_report.get('company_tips', questions.get('company_tips', ''))}"
                ),
                event_type="interview_prep_ready",
            )

            logger.info("Interview prep complete", interview_id=interview_id, company=job.company_name)
            return {
                "interview_id": interview_id,
                "company": job.company_name,
                "technical_questions": len(interview.technical_questions),
                "behavioral_questions": len(interview.behavioral_questions),
                "study_topics": len(interview.study_topics),
            }

    async def _generate_company_report(self, job: Job) -> dict:
        """Generate company intelligence report."""
        try:
            response = await client.chat.completions.create(
                model=settings.OPENAI_MODEL_LIGHT,
                max_tokens=600,
                temperature=0.3,
                messages=[
                    {"role": "system", "content": COMPANY_RESEARCH_PROMPT},
                    {"role": "user", "content": f"Company: {job.company_name}\nRole: {job.title}\nJob description excerpt: {(job.description_clean or '')[:1000]}"},
                ],
                response_format={"type": "json_object"},
            )
            return json.loads(response.choices[0].message.content)
        except Exception as e:
            logger.error("Company report generation failed", error=str(e))
            return {
                "company_overview": f"{job.company_name} - details unavailable",
                "tech_stack": [],
                "talking_points": [],
                "questions_to_ask": ["What does a typical day look like in this role?"],
            }

    async def _generate_questions(
        self, job: Job, analysis: JobAnalysis,
        profile, skills: list, interview_type: str
    ) -> dict:
        """Generate tailored interview questions."""
        skill_names = ", ".join(s.name for s in skills[:20])
        missing = ", ".join(analysis.missing_skills[:5])

        try:
            response = await client.chat.completions.create(
                model=settings.OPENAI_MODEL_HEAVY,
                max_tokens=1500,
                temperature=0.3,
                messages=[
                    {"role": "system", "content": INTERVIEW_PREP_PROMPT},
                    {"role": "user", "content": (
                        f"Company: {job.company_name}\n"
                        f"Role: {job.title}\n"
                        f"Interview type: {interview_type}\n"
                        f"Required skills: {', '.join(analysis.required_skills)}\n"
                        f"User's skills: {skill_names}\n"
                        f"Skill gaps (study these): {missing}\n"
                        f"Role category: {analysis.role_category}"
                    )},
                ],
                response_format={"type": "json_object"},
            )
            return json.loads(response.choices[0].message.content)
        except Exception as e:
            logger.error("Question generation failed", error=str(e))
            return {
                "technical_questions": [
                    {"question": f"Describe your experience with {skill}", "difficulty": "medium", "topic": skill}
                    for skill in analysis.required_skills[:5]
                ],
                "behavioral_questions": [
                    {"question": "Tell me about a challenging project you completed.", "framework": "STAR"}
                ],
                "study_topics": analysis.required_skills[:5],
            }
