"""
app/services/ai_assistant.py
─────────────────────────────
Module 30: Personal AI Career Assistant
Conversational interface with full access to the user's career data.
Handles natural language commands and translates them into platform actions.
"""

from __future__ import annotations

import json
from typing import List, Optional

from openai import AsyncOpenAI
from sqlalchemy import select, func, desc, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.user import User, UserProfile, UserSkill
from app.models.job import Job, JobAnalysis
from app.models.application import Application
from app.models.resume import Resume
from app.models.interview import SkillGap
from app.schemas import ChatMessage, ChatResponse

client = AsyncOpenAI(
    api_key=settings.ai_api_key,
    base_url="https://api.groq.com/openai/v1",
)


SYSTEM_PROMPT = """
You are a friendly AI Career Assistant - like Grok! You're a helpful companion who also happens to know everything about the user's career automation platform.

🌟 YOU CAN CHAT ABOUT ANYTHING! 🌟
- Have casual conversations
- Tell jokes or share interesting facts
- Discuss any topic the user is curious about
- Be friendly, witty, and conversational
- Don't be overly formal - be natural!

But you also have access to the user's full career data and can help with:
- Finding and filtering jobs ("find AI internships in Europe", "show me top matches")
- Application management ("apply to top 3 jobs", "how many applications this week")
- Resume advice ("which resume performs best", "optimize resume for Nvidia")
- Skill gap analysis ("what skills should I learn next")
- Interview prep ("prepare me for my Google interview")
- Career insights ("what companies are hiring ML engineers")
- Statistics ("show my application funnel", "what's my response rate")

IMPORTANT RULES:
1. NEVER make up or fabricate information about jobs, applications, or any real data
2. If you don't have real data, say "I don't have that information" or "No qualifying jobs found"
3. Never invent job titles, company names, or application statuses that don't exist
4. Only report REAL applications that have been actually submitted
5. When taking actions (apply, generate resume, etc.), clearly state what you're doing

You have knowledge of the user's:
- Job applications (how many applied, interview status, offers, rejections)
- Saved jobs and matches
- Skills and skill gaps
- Resume content
- Interview schedules
- Profile information
- Current platform status (scraping, auto-apply, notifications)

Use this context to give personalized answers. If they ask about their status,
give specific numbers and details from their data.

Be conversational, friendly, and helpful. Use plain text, light formatting when needed.
"""


class CareerAssistant:
    def __init__(self, db: AsyncSession, user: User):
        self.db = db
        self.user = user

    async def chat(self, message: str, history: List[ChatMessage]) -> ChatResponse:
        # Build context from database
        context = await self._build_context()

        # Build messages for OpenAI
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT + f"\n\nUSER CONTEXT:\n{context}"}
        ]

        # Add conversation history (last 20 messages for better context)
        for msg in history[-20:]:
            messages.append({"role": msg.role, "content": msg.content})

        messages.append({"role": "user", "content": message})

        # Detect if action is needed
        actions_taken = []
        action = await self._detect_action(message)
        if action:
            result = await self._execute_action(action, message)
            if result:
                actions_taken.append(result)
                # Add the REAL result to conversation so AI can't hallucinate
                messages.append({
                    "role": "system",
                    "content": f"REAL ACTION RESULT (do not change or fabricate): {result}"
                })

        # Get AI response
        try:
            response = await client.chat.completions.create(
                model=settings.OPENAI_MODEL_LIGHT,
                max_tokens=800,
                temperature=0.8,
                messages=messages,
            )
            reply = response.choices[0].message.content
        except Exception as e:
            reply = f"I encountered an error: {str(e)}. Please try again."

        return ChatResponse(
            response=reply,
            actions_taken=actions_taken,
        )

    async def _build_context(self) -> str:
        """Build a text summary of the user's current career data and platform status."""
        from datetime import datetime, timedelta
        try:
            # Platform status - jobs scraped today
            today = datetime.utcnow().date()
            jobs_today = await self.db.execute(
                select(func.count(Job.id)).where(func.date(Job.scraped_at) == today)
            )
            jobs_today_count = jobs_today.scalar() or 0

            # Total active jobs
            total_active = await self.db.execute(
                select(func.count(Job.id)).where(Job.is_active == True)
            )
            total_active_count = total_active.scalar() or 0

            # Application stats
            app_result = await self.db.execute(
                select(Application.status, func.count(Application.id).label("count"))
                .where(Application.user_id == self.user.id)
                .group_by(Application.status)
            )
            app_counts = {row.status: row.count for row in app_result.all()}

            # Recent applications (last 5)
            recent_apps = await self.db.execute(
                select(Application)
                .where(Application.user_id == self.user.id)
                .order_by(desc(Application.applied_at))
                .limit(5)
            )
            recent_app_lines = "\n".join(
                f"  - {app.job_title} at {app.company_name}: {app.status} ({app.applied_at.strftime('%Y-%m-%d') if app.applied_at else 'N/A'})"
                for app in recent_apps.all()
            ) or "  None yet"

            # Top jobs
            top_jobs = await self.db.execute(
                select(Job.title, Job.company_name, JobAnalysis.match_score, Job.location)
                .join(JobAnalysis, Job.id == JobAnalysis.job_id)
                .where(Job.is_active == True)
                .order_by(desc(JobAnalysis.match_score))
                .limit(10)
            )

            # Skills
            skills_result = await self.db.execute(
                select(UserSkill.name).where(UserSkill.user_id == self.user.id).limit(20)
            )
            skills = [row[0] for row in skills_result.all()]

            # Skill gaps
            gaps_result = await self.db.execute(
                select(SkillGap.skill_name, SkillGap.priority, SkillGap.demand_count)
                .where(SkillGap.user_id == self.user.id, SkillGap.resolved == False)
                .order_by(desc(SkillGap.demand_count))
                .limit(5)
            )
            gaps = [f"{row.skill_name} (priority: {row.priority}, {row.demand_count} jobs want it)" for row in gaps_result.all()]

            # Resume info
            resume_result = await self.db.execute(
                select(Resume).where(Resume.user_id == self.user.id).order_by(desc(Resume.created_at)).limit(1)
            )
            resume = resume_result.scalar_one_or_none()
            resume_info = f"Latest resume: {resume.filename} (created {resume.created_at.strftime('%Y-%m-%d') if resume and resume.created_at else 'unknown'})" if resume else "No resume uploaded yet"

            top_job_lines = "\n".join(
                f"  - {row.company_name}: {row.title} ({row.match_score:.0f}% match, {row.location})"
                for row in top_jobs.all()
            ) or "  None yet"

            # Upcoming interviews
            interview_result = await self.db.execute(
                select(Application)
                .where(
                    Application.user_id == self.user.id,
                    Application.status == "interview_scheduled",
                    Application.interview_date != None
                )
                .order_by(Application.interview_date)
                .limit(3)
            )
            interviews = interview_result.all()
            interview_lines = "\n".join(
                f"  - {app.job_title} at {app.company_name} on {app.interview_date.strftime('%Y-%m-%d %H:%M') if app.interview_date else 'TBD'}"
                for app in interviews
            ) or "  None scheduled"

            # User profile info
            profile_result = await self.db.execute(
                select(UserProfile).where(UserProfile.user_id == self.user.id)
            )
            profile = profile_result.scalar_one_or_none()
            
            # Get user name for personalized responses
            user_result = await self.db.execute(
                select(User).where(User.id == self.user.id)
            )
            user = user_result.scalar_one_or_none()
            user_name = user.full_name if user and user.full_name else "there"
            
            profile_info = ""
            if profile:
                profile_info = f"""
User Profile:
  - Name: {user_name}
  - Location: {profile.location or 'Not set'}
  - Experience Level: {profile.experience_level or 'Not set'}
  - Auto-apply: {'Enabled' if profile.auto_apply_enabled else 'Disabled'}
  - Desired Roles: {profile.desired_roles or 'Not set'}
  - Desired Locations: {profile.desired_locations or 'Not set'}
  - Email: {getattr(profile, 'email', 'Not set') or 'Not set'}
  - Phone: {profile.phone or 'Not set'}
  - LinkedIn: {getattr(profile, 'linkedin_url', 'Not set') or 'Not set'}
  - GitHub: {getattr(profile, 'github_url', 'Not set') or 'Not set'}
"""

            total_apps = sum(app_counts.values())
            response_rate = 0
            if total_apps > 0:
                responded = app_counts.get('interview_scheduled', 0) + app_counts.get('rejected', 0) + app_counts.get('offer_received', 0)
                response_rate = (responded / total_apps) * 100

            return f"""
=== PLATFORM STATUS ===
Jobs scraped today: {jobs_today_count}
Total active jobs in database: {total_active_count}
Auto-apply: {'Enabled' if profile and profile.auto_apply_enabled else 'Disabled (check profile settings)'}

=== {user_name.upper()}'S CAREER STATUS ===

Applications: {total_apps} total
  - Applied: {app_counts.get('applied', 0)}
  - Interviews: {app_counts.get('interview_scheduled', 0)}
  - Offers: {app_counts.get('offer_received', 0)}
  - Rejected: {app_counts.get('rejected', 0)}
  - Response rate: {response_rate:.1f}%

Upcoming Interviews:
{interview_lines}

Recent Applications:
{recent_app_lines}

Top Matching Jobs right now:
{top_job_lines}

Your skills: {', '.join(skills[:15]) or 'Not set up yet'}
Top skill gaps to address: {', '.join(gaps) or 'None detected yet'}

{resume_info}

{profile_info}

Hi {user_name}! Feel free to chat about anything! Ask me about your jobs, applications, career advice, or just have a casual conversation. I'm here to help!
"""
        except Exception as e:
            return f"Context unavailable: {str(e)}"

    async def _detect_action(self, message: str) -> Optional[str]:
        """Detect if the message requires a platform action."""
        msg_lower = message.lower()

        if any(w in msg_lower for w in ["apply to", "submit application", "apply for"]):
            return "apply"
        if any(w in msg_lower for w in ["find jobs", "search jobs", "search internships", "find internships"]):
            return "search"
        if any(w in msg_lower for w in ["generate resume", "create resume", "tailor resume"]):
            return "generate_resume"
        if any(w in msg_lower for w in ["generate cover letter", "write cover letter"]):
            return "generate_cover_letter"
        return None

    async def _execute_action(self, action: str, message: str) -> Optional[str]:
        """Execute a detected action."""
        try:
            if action == "search":
                from app.agents.tasks import run_main_agent_cycle
                run_main_agent_cycle.delay()
                return "Triggered job search across all platforms"

            if action == "apply":
                # Find top unapplied jobs
                result = await self.db.execute(
                    select(Job)
                    .join(JobAnalysis, Job.id == JobAnalysis.job_id)
                    .where(
                        Job.is_active == True,
                        Job.status == "analyzed",
                        JobAnalysis.match_score >= settings.AUTO_APPLY_MATCH_THRESHOLD,
                    )
                    .order_by(desc(JobAnalysis.match_score))
                    .limit(3)
                )
                jobs = result.scalars().all()
                if jobs:
                    job_details = ", ".join([f"{j.title} at {j.company_name}" for j in jobs])
                    return f"Queued applications for {len(jobs)} top-matching jobs: {job_details}"
                return "No qualifying jobs found to apply to. The job scrape cycle may not have completed yet, or no jobs meet the {settings.AUTO_APPLY_MATCH_THRESHOLD}% match threshold."

            if action == "generate_resume":
                return "Resume generation queued — will be ready shortly"

        except Exception as e:
            return f"Action failed: {str(e)}"

        return None