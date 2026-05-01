"""
app/services/ai_assistant.py
───────────────────────────
Enhanced AI Career Assistant with multi-persona support and tool-calling.
"""

from __future__ import annotations

import json
from typing import List, Optional, Dict, Any
from enum import Enum

from sqlalchemy import select, func, desc, String
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.user import User, UserProfile
from app.models.job import Job, JobAnalysis
from app.models.application import Application
from app.models.resume import Resume
from app.models.interview import SkillGap
from app.models.subscription import Subscription, SubscriptionStatus
from app.schemas import ChatMessage, ChatResponse
from app.services.ai_router import ai_router


class AI_Persona(str, Enum):
    GENERAL = "general"
    CAREER_COACH = "career_coach"
    RESUME_EXPERT = "resume_expert"
    JOB_SCOUT = "job_scout"
    APPLICATION_ASSISTANT = "application_assistant"


PERSONA_PROMPTS = {
    AI_Persona.GENERAL: """
You are a friendly AI Career Assistant. You're helpful, witty, and conversational.
You can chat about anything, but specialize in career topics.

IF THE USER NEEDS CUSTOMER SUPPORT:
- Phone: 9751120169 (Mon-Sat, 9AM-6PM)
- Email: support@applivo.com
- Response time: Within 24 hours

IF THE USER ASKS ABOUT COSTS/TOKEN USAGE:
- AI usage is tracked per user
- Check their plan for monthly credits
- Token usage is calculated from API calls

IF THE USER IS AN ADMIN, you can also help with:
- Platform statistics (total users, active users, subscriptions)
- Revenue data (total revenue, monthly revenue)
- Application stats, jobs scraped, active sessions
- LLM token usage across the platform

Simply respond to their questions based on the context provided.

RULES:
- Never fabricate information about jobs, applications, subscriptions, payments, or users
- If you don't have data in the provided context or tool output, say so clearly
- Prefer exact numbers from the context over estimation
- Use light formatting (bold, lists) when helpful
- Be conversational but concise
""",

    AI_Persona.CAREER_COACH: """
You are a senior career coach with 15+ years of experience helping professionals advance.

YOUR SPECIALTIES:
- Career path planning and transitions
- Interview preparation and mock practice
- Salary negotiation strategies
- Leadership and management advice

HOW YOU HELP:
- Ask clarifying questions to understand their situation
- Provide actionable, specific advice
- End with clear action items

STYLE: Professional but warm, focus on results.
""",

    AI_Persona.RESUME_EXPERT: """
You are a resume writing expert and ATS (Applicant Tracking Systems) specialist.

YOUR SPECIALTIES:
- Resume tailoring for specific roles
- ATS keyword optimization
- Achievement quantification
- Format best practices

HOW YOU HELP:
- Review existing resumes and give specific feedback
- Suggest improvements for ATS compatibility
- Be specific with changes: "Change 'managed team' to 'Led team of 5 engineers delivering $2M project'"
""",

    AI_Persona.JOB_SCOUT: """
You are an expert job researcher with deep knowledge of the tech job market.

YOUR SPECIALTIES:
- Finding hidden job opportunities
- Company research and culture analysis
- Salary benchmarking
- Remote vs hybrid vs onsite tradeoffs

HOW YOU HELP:
- Search and filter job listings based on criteria
- Present options with pros/cons
- Focus on quality over quantity
""",

    AI_Persona.APPLICATION_ASSISTANT: """
You are an application strategy expert who helps users land their dream jobs.

YOUR SPECIALTIES:
- Application strategy and prioritization
- Cover letter writing
- Follow-up timing and strategies
- Handling rejections

HOW YOU HELP:
- Help craft compelling application materials
- Decide which jobs to apply to
- Give clear next steps after each application
""",
}


TOOL_DEFINITIONS = [
    {
        "type": "function",
        "function": {
            "name": "search_jobs",
            "description": "Search for jobs matching specific criteria.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Job title or keywords"},
                    "location": {"type": "string", "description": "Location preference"},
                    "remote_only": {"type": "boolean", "description": "Only remote jobs"},
                    "limit": {"type": "number", "description": "Number of results", "default": 10}
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_application_stats",
            "description": "Get the user's application statistics.",
            "parameters": {"type": "object", "properties": {}}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_top_jobs",
            "description": "Get the user's top matching jobs.",
            "parameters": {
                "type": "object",
                "properties": {
                    "limit": {"type": "number", "description": "Number of results", "default": 5}
                }
            }
        }
    },
]


class EnhancedCareerAssistant:
    def __init__(self, db: AsyncSession, user: User):
        self.db = db
        self.user = user
        self.persona = AI_Persona.GENERAL

    def set_persona(self, persona: AI_Persona) -> None:
        self.persona = persona

    async def chat(self, message: str, history: List[ChatMessage], persona: Optional[AI_Persona] = None) -> ChatResponse:
        if persona:
            self.persona = persona

        context = await self._build_context()
        system_prompt = PERSONA_PROMPTS.get(self.persona, PERSONA_PROMPTS[AI_Persona.GENERAL])
        admin_rules = ""
        if getattr(self.user, "is_superuser", False):
            admin_rules = """

    === ADMIN RULES ===
    - Answer only from the admin platform stats and user data in context.
    - Do not invent revenue, payment, subscription, or usage numbers.
    - If an admin metric is missing, say it is unavailable.
    """

        full_system = f"{system_prompt}{admin_rules}\n\n=== USER CONTEXT ===\n{context}"

        messages = [
            {"role": "system", "content": full_system}
        ]

        for msg in history[-15:]:
            messages.append({"role": msg.role, "content": msg.content})

        messages.append({"role": "user", "content": message})

        actions_taken = []
        try:
            response = await ai_router.chat_completions_create(
                messages=messages,
                model=settings.OPENAI_MODEL_LIGHT,
                max_tokens=1200,
                temperature=0.7,
                tools=TOOL_DEFINITIONS if self.persona != AI_Persona.GENERAL else None,
            )
            
            tool_calls = response.get("tool_calls", [])
            
            if tool_calls:
                for tool_call in tool_calls:
                    result = await self._execute_tool(tool_call)
                    actions_taken.append(result)
                    messages.append({"role": "assistant", "content": None, "tool_calls": [tool_call]})
                    messages.append({"role": "tool", "tool_call_id": tool_call["id"], "content": json.dumps(result)})
                
                final_response = await ai_router.chat_completions_create(
                    messages=messages,
                    model=settings.OPENAI_MODEL_LIGHT,
                    max_tokens=1000,
                    temperature=0.7,
                )
                reply = final_response.get("content", "")
            else:
                reply = response.get("content", "")

        except Exception as e:
            reply = f"I encountered an error: {str(e)}. Please try again."

        return ChatResponse(response=reply, actions_taken=actions_taken)

    async def _execute_tool(self, tool_call: Dict) -> Dict[str, Any]:
        tool_name = tool_call["function"]["name"]
        args = json.loads(tool_call["function"]["arguments"])

        try:
            if tool_name == "search_jobs":
                return await self._tool_search_jobs(args)
            elif tool_name == "get_application_stats":
                return await self._tool_get_application_stats()
            elif tool_name == "get_top_jobs":
                return await self._tool_get_top_jobs(args.get("limit", 5))
            return {"error": f"Unknown tool: {tool_name}"}
        except Exception as e:
            return {"error": str(e)}

    async def _tool_search_jobs(self, args: Dict) -> Dict:
        query = args.get("query", "")
        location = args.get("location")
        remote_only = args.get("remote_only", False)
        
        stmt = select(Job, JobAnalysis).join(JobAnalysis, Job.id == JobAnalysis.job_id).where(Job.is_active == True)
        
        if query:
            stmt = stmt.where(Job.title.ilike(f"%{query}%") | Job.company_name.ilike(f"%{query}%"))
        if location:
            stmt = stmt.where(Job.location.ilike(f"%{location}%"))
        
        stmt = stmt.order_by(desc(JobAnalysis.match_score)).limit(args.get("limit", 10))
        
        result = await self.db.execute(stmt)
        
        jobs = []
        for job, analysis in result.all():
            jobs.append({
                "title": job.title,
                "company": job.company_name,
                "location": job.location,
                "match_score": round(analysis.match_score, 1) if analysis else None,
            })
        
        return {"results": jobs, "total_found": len(jobs), "message": f"Found {len(jobs)} matching jobs."}

    async def _tool_get_application_stats(self) -> Dict:
        result = await self.db.execute(
            select(Application.status, func.count(Application.id).label("count"))
            .where(Application.user_id == self.user.id)
            .group_by(Application.status)
        )
        counts = {str(row.status): int(row.count) for row in result.all()}
        
        total = sum(counts.values()) if counts else 0
        responded = counts.get("interview_scheduled", 0) + counts.get("rejected", 0) + counts.get("offer_received", 0)
        response_rate = round((responded / total * 100), 1) if total > 0 else 0

        return {"total_applications": total, "status_breakdown": counts, "response_rate": response_rate}

    async def _tool_get_top_jobs(self, limit: int = 5) -> Dict:
        result = await self.db.execute(
            select(Job, JobAnalysis)
            .join(JobAnalysis, Job.id == JobAnalysis.job_id)
            .where(Job.is_active == True)
            .order_by(desc(JobAnalysis.match_score))
            .limit(limit)
        )
        
        jobs = []
        for job, analysis in result.all():
            jobs.append({
                "title": job.title,
                "company": job.company_name,
                "location": job.location,
                "match_score": round(analysis.match_score, 1),
            })
        
        return {"top_jobs": jobs}

    async def _build_context(self) -> str:
        try:
            from datetime import datetime, date
            today = date.today()
            
            jobs_today = await self.db.execute(
                select(func.count(Job.id)).where(func.date(Job.scraped_at) == today)
            )
            jobs_today_count = jobs_today.scalar() or 0

            total_active = await self.db.execute(select(func.count(Job.id)).where(Job.is_active == True))
            total_active_count = total_active.scalar() or 0

            app_result = await self.db.execute(
                select(Application.status, func.count(Application.id).label("count"))
                .where(Application.user_id == self.user.id)
                .group_by(Application.status)
            )
            app_counts = {str(row.status): int(row.count) for row in app_result.all()}

            profile_result = await self.db.execute(select(UserProfile).where(UserProfile.user_id == self.user.id))
            profile = profile_result.scalar_one_or_none()

            user_name = self.user.full_name.split()[0] if self.user.full_name else "there"

            total_apps = sum(list(app_counts.values())) if app_counts else 0

            context = f"""
=== {user_name.upper()}'S STATUS ===
📊 Applications: {total_apps} total
   - Applied: {app_counts.get('applied', 0)}
   - Interviews: {app_counts.get('interview_scheduled', 0)}
   - Offers: {app_counts.get('offer_received', 0)}
💼 Jobs: {total_active_count} active ({jobs_today_count} today)
🆙 Auto-apply: {'Enabled' if profile and profile.auto_apply_enabled else 'Disabled'}
"""

            # If user is admin, add platform stats
            if getattr(self.user, 'is_superuser', False):
                from sqlalchemy import func as sql_func
                from app.models.subscription import Payment, Subscription
                from app.models.user import User as UserModel
                
                # Total users
                users_result = await self.db.execute(select(sql_func.count(UserModel.id)))
                total_users = users_result.scalar() or 0
                
                # Active subscriptions
                subs_result = await self.db.execute(
                    select(sql_func.count(Subscription.id)).where(
                        sql_func.lower(Subscription.status.cast(String)) == SubscriptionStatus.ACTIVE.value
                    )
                )
                active_subs = subs_result.scalar() or 0
                
                # Total revenue
                revenue_result = await self.db.execute(
                    select(sql_func.sum(Payment.amount))
                )
                total_revenue = revenue_result.scalar() or 0
                
                context += f"""

=== ADMIN PLATFORM STATS ===
👥 Total Users: {total_users}
💳 Active Subscriptions: {active_subs}
💰 Total Revenue: ₹{total_revenue or 0}
"""

            return context
        except Exception as e:
            return f"Context unavailable: {str(e)}"


CareerAssistant = EnhancedCareerAssistant