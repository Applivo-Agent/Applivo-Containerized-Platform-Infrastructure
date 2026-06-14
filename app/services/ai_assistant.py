"""
app/services/ai_assistant.py
───────────────────────────
Enhanced AI Career Assistant with multi-persona support and tool-calling.
"""

from __future__ import annotations

import json
from typing import List, Optional, Dict, Any
from enum import Enum

from sqlalchemy import select, func, desc, String, cast
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
    "USER_LUMI": """
You are Lumi, the personal AI assistant for a single authenticated user inside the Applivo platform.
Your role is to act as a highly knowledgeable, personalized assistant for THIS USER ONLY.

CORE PRINCIPLE:
- You are a PERSONAL assistant, not a platform analyst.
- All responses must be based on the CURRENT USER only.
- You must deeply understand and use the user's own data, history, preferences, and activity to provide intelligent, tailored responses.

STRICT DATA ISOLATION:
- You must NEVER access, reference, or reveal admin statistics, platform-wide metrics, other users' data, revenue information, total user counts, or system infrastructure details.
- If the user asks about platform-wide stats (e.g., "How many users?"), respond: "I focus on your personal account data. I don't have access to platform-wide statistics."

NO HALLUCINATION RULE:
- Never guess numbers or invent values.
- If data is missing, say: "I don't currently have that information in your account."

OUTPUT STYLE:
- User-specific insights.
- Clear, actionable next steps.
- Relevant numbers from their account only.
- DO NOT use markdown bold stars (like **text**). Use plain text or simple capitalization for emphasis instead.
""",

    "ADMIN_LUMI": """
You are Lumi Admin, the system intelligence assistant for the Applivo platform.
You operate in ADMIN MODE. Your responsibility is to provide accurate, operational, infrastructure-level insights about the platform.

ADMIN DATA ACCESS SCOPE:
- System Health: process counts, success/failure rates, queue sizes, worker status (Celery, Redis).
- Business Metrics: revenue, active subscriptions, payment history, user activity counts.
- AI Metrics: token usage, latency, throughput across all users.
- Operations: failed jobs, scraper errors, session timeouts.

CRITICAL ADMIN BEHAVIOR:
- Always answer using real operational data, timestamps, and counts. Never guess or hallucinate.
- If data is unavailable, say: "That metric is not currently available."
- Be safe: reference users only in operational context (e.g., "User X has a failed task"). Never reveal passwords or secrets.

ERROR INTERPRETATION RULE:
1) Identify the failure cause (e.g., "Selector failed", "Session expired").
2) Identify the affected component (e.g., "Browser agent", "Worker").
3) Suggest corrective action (e.g., "Run save_cookies.py", "Restart Celery").

OUTPUT STYLE:
- System Status
- Root Cause
- Impact
- Recommended Action
- DO NOT use markdown bold stars (like **text**). Use plain text or simple capitalization for emphasis instead.
""",

    "ADMIN_FINANCE": """
You are Lumi Finance, the Revenue and Business Intelligence assistant for the Applivo platform.
You operate in ADMIN ANALYTICS MODE. Your responsibility is to monitor, calculate, and explain revenue performance, financial health, subscription metrics, and SaaS growth indicators.

PRIMARY REVENUE METRICS:
- MRR (Monthly Recurring Revenue): Sum of all ACTIVE subscription prices.
- ARR (Annual Recurring Revenue): MRR * 12.
- Conversion Rate: Paid Users / Total Users * 100.
- Churn Rate: Cancelled Users / (Active + Cancelled) * 100.
- ARPU (Average Revenue Per User): Total Revenue / Paying Users.

CRITICAL BEHAVIOR:
- Use real numbers and timestamps. Never guess or invent revenue.
- CALCULATE metrics using the provided context.
- Identify trends: "MRR is up 5% this week" if data supports it.
- Detect anomalies: sudden drops in revenue or spikes in failed payments.

OUTPUT STYLE:
- Metric Name
- Value
- Trend
- Interpretation
- Action
- DO NOT use markdown bold stars.
""",

    AI_Persona.CAREER_COACH: "You are Lumi, acting as a senior career coach. Use the user's specific history to give advice. DO NOT use markdown bold stars (like **text**). Use CAPS for emphasis.",
    AI_Persona.RESUME_EXPERT: "You are Lumi, acting as a resume expert. Suggest specific, quantifiable improvements to the user's resume. DO NOT use markdown bold stars (like **text**). Use CAPS for emphasis.",
    AI_Persona.JOB_SCOUT: "You are Lumi, acting as a job researcher. Filter jobs based ONLY on the user's stated preferences. DO NOT use markdown bold stars (like **text**). Use CAPS for emphasis.",
    AI_Persona.APPLICATION_ASSISTANT: "You are Lumi, acting as an application expert. Help the user prioritize their specific applications. DO NOT use markdown bold stars (like **text**). Use CAPS for emphasis.",
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

    async def chat(self, message: str, history: List[Any], persona: Optional[AI_Persona] = None) -> Dict[str, Any]:
        if persona:
            self.set_persona(persona)
            
        # Determine base persona based on role
        is_admin = getattr(self.user, "is_superuser", False)
        base_persona = "USER_LUMI"
        
        if is_admin:
            # Auto-switch to Finance persona if analytics context is detected
            finance_keywords = ["revenue", "mrr", "arr", "churn", "conversion", "sales", "profit", "analytics"]
            if any(k in message.lower() for k in finance_keywords):
                base_persona = "ADMIN_FINANCE"
            else:
                base_persona = "ADMIN_LUMI"
        
        # If persona requested, try to map it, otherwise use base
        system_prompt = PERSONA_PROMPTS.get(self.persona, PERSONA_PROMPTS[base_persona])
        
        # Build context
        context = await self._build_context()
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
            from app.services.ai_router import AIRouter
            ai_settings = await AIRouter.load_user_ai_settings(self.user.id) if self.user else None
            response = await ai_router.chat_completions_create(
                messages=messages,
                model=settings.OPENAI_MODEL_LIGHT,
                max_tokens=1200,
                temperature=0.7,
                tools=TOOL_DEFINITIONS if self.persona != AI_Persona.GENERAL else None,
                ai_settings=ai_settings,
                user_id=self.user.id if self.user else None,
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
            
            # Application stats
            app_result = await self.db.execute(
                select(Application.status, func.count(Application.id).label("count"))
                .where(Application.user_id == self.user.id)
                .group_by(Application.status)
            )
            app_counts = {str(row.status): int(row.count) for row in app_result.all()}
            total_apps = sum(list(app_counts.values())) if app_counts else 0

            # Job stats
            jobs_today = await self.db.execute(
                select(func.count(Job.id)).where(func.date(Job.scraped_at) == today)
            )
            jobs_today_count = jobs_today.scalar() or 0
            total_active = await self.db.execute(select(func.count(Job.id)).where(Job.is_active == True))
            total_active_count = total_active.scalar() or 0

            # Profile & Skills
            from app.models.user import UserSkill, UserProfile
            profile_result = await self.db.execute(select(UserProfile).where(UserProfile.user_id == self.user.id))
            profile = profile_result.scalar_one_or_none()
            
            skills_result = await self.db.execute(select(UserSkill).where(UserSkill.user_id == self.user.id))
            skills = [s.name for s in skills_result.scalars().all()]

            user_name = self.user.full_name.split()[0] if self.user.full_name else "there"
            
            # --- BUILD CONTEXT STRING ---
            context = f"=== {user_name.upper()}'S CAREER PROFILE ===\n"
            context += f"👤 Full Name: {self.user.full_name}\n"
            
            if profile:
                context += f"📍 Location: {profile.location or 'Unknown'}\n"
                context += f"🎯 Desired Roles: {', '.join(profile.desired_roles) if profile.desired_roles else 'Not specified'}\n"
                context += f"📜 Summary: {profile.professional_summary or 'No summary provided'}\n"
                
                if profile.education:
                    latest_edu = profile.education[0] if isinstance(profile.education, list) and profile.education else {}
                    context += f"🎓 Latest Education: {latest_edu.get('degree')} in {latest_edu.get('field')} ({latest_edu.get('institution')})\n"
                
                if profile.work_experience:
                    recent_jobs = [f"{exp.get('title')} at {exp.get('company')}" for exp in profile.work_experience[:2]]
                    context += f"💼 Recent Experience: {', '.join(recent_jobs)}\n"

            context += f"🛠️ Top Skills: {', '.join(skills[:15]) if skills else 'None listed'}\n"
            context += f"\n=== {user_name.upper()}'S PLATFORM STATUS ===\n"
            context += f"📊 Applications: {total_apps} total\n"
            for status, count in app_counts.items():
                context += f"   - {status.replace('_', ' ').title()}: {count}\n"
            
            context += f"💼 Job Market: {total_active_count} active listings ({jobs_today_count} found today)\n"
            context += f"🆙 Auto-apply: {'ENABLED' if profile and profile.auto_apply_enabled else 'DISABLED'}\n"

            # If user is admin, add platform stats
            if getattr(self.user, 'is_superuser', False):
                from sqlalchemy import func as sql_func
                from app.models.subscription import Payment, Subscription
                from app.models.user import User as UserModel
                
                # Total users
                users_result = await self.db.execute(select(sql_func.count(UserModel.id)))
                total_users = users_result.scalar() or 0
                
                # Active subscriptions (Cast status to string for comparison)
                from app.models.subscription import SubscriptionStatus
                subs_result = await self.db.execute(
                    select(sql_func.count(Subscription.id)).where(
                        sql_func.lower(cast(Subscription.status, String)) == SubscriptionStatus.ACTIVE.value.lower()
                    )
                )
                active_subs = subs_result.scalar() or 0
                
                # Total revenue
                revenue_result = await self.db.execute(
                    select(sql_func.sum(Payment.amount))
                )
                total_revenue = revenue_result.scalar() or 0
                
                # SaaS Metrics
                from app.models.subscription import PLAN_PRICES
                active_plans_result = await self.db.execute(
                    select(Subscription.plan).where(
                        sql_func.lower(cast(Subscription.status, String)) == SubscriptionStatus.ACTIVE.value.lower()
                    )
                )
                active_plans = active_plans_result.scalars().all()
                mrr_paise = sum(PLAN_PRICES.get(p, 0) for p in active_plans)
                
                paying_users_count = (await self.db.execute(
                    select(sql_func.count(sql_func.distinct(Payment.user_id)))
                    .where(sql_func.lower(cast(Payment.status, String)) == 'captured')
                )).scalar() or 0
                
                conversion_rate = round((paying_users_count / (total_users or 1)) * 100, 2)
                
                context += f"""
=== ADMIN PLATFORM STATS ===
👥 Total Users: {total_users}
💳 Active Subscriptions: {len(active_plans)}
💰 Total Revenue: ₹{(total_revenue or 0) / 100}
📈 MRR: ₹{mrr_paise / 100}
🚀 ARR: ₹{(mrr_paise * 12) / 100}
🎯 Conversion: {conversion_rate}%
"""

            return context
        except Exception as e:
            return f"Context unavailable: {str(e)}"


CareerAssistant = EnhancedCareerAssistant