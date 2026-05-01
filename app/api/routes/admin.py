"""
app/api/routes/admin.py
──────────────────────
Admin Service - User management, subscription management, payment monitoring,
system control, automation management, and analytics.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select, desc, and_, or_, text, literal, String, Integer as SqlInteger
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from typing import List, Optional, Dict
from datetime import datetime, timedelta, timezone
from pydantic import BaseModel, EmailStr
import structlog

from app.core.database import get_db, get_db_context
from app.api.routes.auth import get_current_user
from app.models.user import User, UserProfile
from app.models.subscription import Subscription, SubscriptionStatus, PlanTier, Payment, PaymentStatus
from app.models.audit import AuditLog, AuditAction, create_audit_entry
from app.models.application import Application, ApplicationStatus
from app.models.job import Job, JobAnalysis
from app.models.ai_usage import AIUsageLog

logger = structlog.get_logger()

admin_router = APIRouter(prefix="/admin", tags=["Admin"])


class AdminUserOut(BaseModel):
    id: str
    email: str
    full_name: str
    is_active: bool
    is_superuser: bool
    created_at: datetime
    last_login_at: Optional[datetime]
    subscription_plan: Optional[str] = None
    subscription_status: Optional[str] = None
    applications_count: int = 0
    profile_complete: bool = False
    plan: Optional[str] = None
    ai_credits_used: int = 0
    ai_credits_limit: int = 0
    total_tokens: int = 0

    class Config:
        from_attributes = True


class AdminUserDetailOut(AdminUserOut):
    profile: Optional[dict]
    subscriptions: List[dict]
    payments: List[dict]


class AdminSubscriptionOut(BaseModel):
    id: str
    user_email: str
    plan: str
    status: str
    start_date: datetime
    end_date: Optional[datetime] = None
    daily_limit: int


class AdminPaymentOut(BaseModel):
    id: str
    user_email: str
    amount: int
    currency: str
    status: str
    created_at: datetime


class AdminStatsResponse(BaseModel):
    total_users: int
    active_users: int
    total_subscriptions: int
    active_subscriptions: int
    total_revenue: int
    revenue_this_month: int
    total_applications: int
    applications_this_month: int
    jobs_scraped: int
    active_sessions: int


class AdminLLMProviderUsage(BaseModel):
    provider: str
    model: str
    requests: int
    tokens_used: int
    prompt_tokens: int = 0
    completion_tokens: int = 0
    cached_tokens: int = 0
    average_tokens: float = 0.0
    success_rate: float = 100.0


class AdminLLMTimelinePoint(BaseModel):
    date: str
    total_requests: int
    total_tokens: int
    # Provider specifics
    groq_requests: int = 0
    groq_tokens: int = 0
    gemini_requests: int = 0
    gemini_tokens: int = 0
    # Status code specifics
    status_200: int = 0
    status_429: int = 0
    status_500: int = 0
    prompt_tokens: int = 0
    completion_tokens: int = 0
    cached_tokens: int = 0
    success_rate: float = 0.0
    total_errors: int = 0


class AdminLLMModelTimelinePoint(BaseModel):
    date: str
    requests: int = 0
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    errors: int = 0


class AdminLLMModelMetrics(BaseModel):
    model: str
    provider: str
    total_requests: int = 0
    total_tokens: int = 0
    success_rate: float = 0.0
    rate_limit: int = 900
    timeline: List[AdminLLMModelTimelinePoint]


class AdminLLMSystemOverview(BaseModel):
    avg_latency_ms: float = 0.0
    cache_hit_rate: float = 0.0
    tps: float = 0.0
    availability: float = 100.0


class AdminLLMFeatureMetric(BaseModel):
    feature: str
    tokens: int
    requests: int


class AdminLLMUserUsage(BaseModel):
    user_email: str
    total_tokens: int
    requests: int


class AdminLLMUsageResponse(BaseModel):
    total_requests: int
    total_tokens: int
    total_estimated_cost: float = 0.0
    providers: List[AdminLLMProviderUsage]
    timeline: List[AdminLLMTimelinePoint]
    models: List[AdminLLMModelMetrics] = []
    overview: AdminLLMSystemOverview
    features: List[AdminLLMFeatureMetric] = []
    top_users: List[AdminLLMUserUsage] = []
    error_distribution: Dict[str, int] = {}


class AdminUpdateUserRequest(BaseModel):
    is_active: Optional[bool] = None
    plan: Optional[str] = None
    auto_apply_enabled: Optional[bool] = None


class AdminPaymentOut(BaseModel):
    id: str
    user_email: str
    amount: int
    currency: str
    status: str
    plan: Optional[str]
    razorpay_order_id: Optional[str]
    razorpay_payment_id: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class AdminAuditLogOut(BaseModel):
    id: str
    user_email: Optional[str]
    action: str
    resource_type: str
    resource_id: Optional[str]
    ip_address: Optional[str]
    success: bool
    timestamp: datetime
    details: Optional[dict]

    class Config:
        from_attributes = True


def require_admin(current_user: User = Depends(get_current_user)):
    """Dependency to ensure only admin users can access endpoints."""
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user


@admin_router.get("/stats", response_model=AdminStatsResponse)
async def get_admin_stats(
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin),
):
    """Get system-wide statistics for admin dashboard."""
    now = datetime.now(timezone.utc)
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    total_users = (await db.execute(select(func.count(User.id)))).scalar() or 0
    
    active_users = (await db.execute(
        select(func.count(User.id)).where(User.is_active == True)
    )).scalar() or 0

    total_subs = (await db.execute(select(func.count(Subscription.id)))).scalar() or 0
    
    active_subs = (await db.execute(
        select(func.count(Subscription.id)).where(
            func.lower(Subscription.status.cast(String)) == SubscriptionStatus.ACTIVE.value.lower(),
            or_(Subscription.end_date == None, Subscription.end_date > now)
        )
    )).scalar() or 0

    total_revenue = (await db.execute(
        select(func.sum(Payment.amount)).where(func.lower(Payment.status.cast(String)) == PaymentStatus.CAPTURED.value.lower())
    )).scalar() or 0

    revenue_this_month = (await db.execute(
        select(func.sum(Payment.amount)).where(
            func.lower(Payment.status.cast(String)) == PaymentStatus.CAPTURED.value.lower(),
            Payment.created_at >= month_start
        )
    )).scalar() or 0

    from app.models.application import Application
    applied_statuses = [
        ApplicationStatus.APPLIED, ApplicationStatus.VIEWED, ApplicationStatus.SHORTLISTED,
        ApplicationStatus.INTERVIEW_SCHEDULED, ApplicationStatus.INTERVIEW_COMPLETED,
        ApplicationStatus.OFFER_RECEIVED, ApplicationStatus.OFFER_ACCEPTED,
        ApplicationStatus.OFFER_DECLINED, ApplicationStatus.REJECTED, ApplicationStatus.WITHDRAWN
    ]
    
    total_apps = (await db.execute(
        select(func.count(Application.id)).where(Application.status.in_(applied_statuses))
    )).scalar() or 0
    
    apps_this_month = (await db.execute(
        select(func.count(Application.id)).where(
            Application.created_at >= month_start,
            Application.status.in_(applied_statuses)
        )
    )).scalar() or 0

    from app.models.job import Job
    jobs_scraped = (await db.execute(select(func.count(Job.id)))).scalar() or 0

    return AdminStatsResponse(
        total_users=total_users,
        active_users=active_users,
        total_subscriptions=total_subs,
        active_subscriptions=active_subs,
        total_revenue=total_revenue,
        revenue_this_month=revenue_this_month,
        total_applications=total_apps,
        applications_this_month=apps_this_month,
        jobs_scraped=jobs_scraped,
        active_sessions=0,
    )


@admin_router.get("/llm-usage", response_model=AdminLLMUsageResponse)
async def get_llm_usage(
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin),
):
    """Get AI provider and model usage breakdown for the admin dashboard."""
    now = datetime.now(timezone.utc)
    start_date = (now - timedelta(days=13)).date()
    start_dt = datetime.combine(start_date, datetime.min.time(), tzinfo=timezone.utc)

    # Pricing per 1M tokens in USD
    PRICING = {
        "groq/llama-3.1-8b-instant": {"prompt": 0.05, "completion": 0.08},
        "groq/llama-3.1-70b-versatile": {"prompt": 0.59, "completion": 0.79},
        "groq/llama-3.1-405b-reasoning": {"prompt": 5.0, "completion": 10.0},
        "google/gemini-1.5-flash": {"prompt": 0.075, "completion": 0.30},
        "google/gemini-1.5-pro": {"prompt": 3.50, "completion": 10.50},
    }

    def estimate_cost(prov: str, mod: str, prompt: int, completion: int) -> float:
        key = f"{prov}/{mod}"
        # Fallback to general low-cost model pricing if not found
        p = PRICING.get(key, {"prompt": 0.1, "completion": 0.2})
        return (prompt * p["prompt"] / 1_000_000) + (completion * p["completion"] / 1_000_000)

    # 1. Aggregate usage by Provider + Model (All-time or bucketed)
    rows = (await db.execute(
        select(
            AIUsageLog.provider,
            AIUsageLog.model,
            func.count(AIUsageLog.id),
            func.sum(AIUsageLog.total_tokens),
            func.sum(AIUsageLog.prompt_tokens),
            func.sum(AIUsageLog.completion_tokens),
            func.sum(AIUsageLog.cached_tokens),
            func.avg(AIUsageLog.total_tokens),
            func.avg(AIUsageLog.success.cast(SqlInteger)) * 100,
            func.avg(AIUsageLog.latency_ms)
        )
        .group_by(AIUsageLog.provider, AIUsageLog.model)
    )).all()

    # 1.1 Global KPIs
    global_kpis = (await db.execute(
        select(
            func.avg(AIUsageLog.latency_ms),
            func.sum(AIUsageLog.cached_tokens),
            func.sum(AIUsageLog.total_tokens),
            func.avg(AIUsageLog.success.cast(SqlInteger)) * 100
        )
        .where(AIUsageLog.created_at >= start_dt)
    )).first()

    # 1.2 Feature Usage (Endpoint breakdown)
    feature_rows = (await db.execute(
        select(
            AIUsageLog.endpoint_path,
            func.sum(AIUsageLog.total_tokens),
            func.count(AIUsageLog.id)
        )
        .where(AIUsageLog.created_at >= start_dt)
        .group_by(AIUsageLog.endpoint_path)
        .order_by(desc(func.sum(AIUsageLog.total_tokens)))
        .limit(10)
    )).all()

    # 1.3 Top Consumers
    top_user_rows = (await db.execute(
        select(
            User.email,
            func.sum(AIUsageLog.total_tokens),
            func.count(AIUsageLog.id)
        )
        .join(User, AIUsageLog.user_id == User.id)
        .where(AIUsageLog.created_at >= start_dt)
        .group_by(User.email)
        .order_by(desc(func.sum(AIUsageLog.total_tokens)))
        .limit(5)
    )).all()

    # 2. Detailed Timeline aggregation (per model)
    timeline_rows = (await db.execute(
        select(
            func.date(AIUsageLog.created_at),
            AIUsageLog.provider,
            AIUsageLog.model,
            AIUsageLog.status_code,
            func.count(AIUsageLog.id),
            func.sum(AIUsageLog.total_tokens),
            func.sum(AIUsageLog.prompt_tokens),
            func.sum(AIUsageLog.completion_tokens),
            func.sum(AIUsageLog.cached_tokens),
        )
        .where(AIUsageLog.created_at >= start_dt)
        .group_by(func.date(AIUsageLog.created_at), AIUsageLog.provider, AIUsageLog.model, AIUsageLog.status_code)
        .order_by(func.date(AIUsageLog.created_at))
    )).all()

    # Pre-determined rate limits for models
    MODEL_LIMITS = {
        "llama-3.1-8b-instant": 900,
        "llama-3.3-70b-versatile": 900,
        "llama-3.1-405b-reasoning": 100,
        "gemini-1.5-flash": 15, # RPM for free tier
        "gemini-1.5-pro": 2,
    }

    providers = []
    total_requests = 0
    total_tokens = 0
    total_cost = 0.0
    error_dist = {}
    timeline_map: dict[str, dict] = {}

    # Pre-populate timeline map for the last 14 days
    for offset in range(14):
        day = (start_date + timedelta(days=offset)).isoformat()
        timeline_map[day] = {
            "date": day,
            "total_requests": 0,
            "total_tokens": 0,
            "groq_requests": 0,
            "groq_tokens": 0,
            "gemini_requests": 0,
            "gemini_tokens": 0,
            "status_200": 0,
            "status_429": 0,
            "status_500": 0,
            "prompt_tokens": 0,
            "completion_tokens": 0,
            "cached_tokens": 0,
            "success_rate": 0.0,
            "total_errors": 0,
        }

    model_timeline_map: dict[str, dict[str, dict]] = {} # {model_key: {day: data}}

    # Process provider/model rows
    for prov, mod, reqs, tokens, prompt, completion, cached, avg, success, latency in rows:
        reqs = int(reqs or 0)
        tokens = int(tokens or 0)
        total_requests += reqs
        prompt_v = int(prompt or 0)
        completion_v = int(completion or 0)
        total_cost += estimate_cost(prov, mod, prompt_v, completion_v)
        
        m_key = f"{prov}/{mod}"
        model_timeline_map[m_key] = {}
        for offset in range(14):
            day = (start_date + timedelta(days=offset)).isoformat()
            model_timeline_map[m_key][day] = {
                "date": day,
                "requests": 0,
                "prompt_tokens": 0,
                "completion_tokens": 0,
                "total_tokens": 0,
                "errors": 0,
            }

        providers.append(AdminLLMProviderUsage(
            provider=prov,
            model=mod,
            requests=reqs,
            tokens_used=tokens,
            prompt_tokens=prompt_v,
            completion_tokens=completion_v,
            cached_tokens=int(cached or 0),
            average_tokens=float(avg or 0),
            success_rate=float(success or 0)
        ))

    # Process timeline rows
    for day, prov, mod, status, reqs, tokens, prompt, completion, cached in timeline_rows:
        day_key = str(day)
        bucket = timeline_map.get(day_key)
        if not bucket:
            continue
            
        rc = int(reqs or 0)
        tc = int(tokens or 0)
        pc = int(prompt or 0)
        cc = int(completion or 0)
        cac = int(cached or 0)
        
        # Global aggregated bucket
        bucket["total_requests"] += rc
        bucket["total_tokens"] += tc
        bucket["prompt_tokens"] += pc
        bucket["completion_tokens"] += cc
        bucket["cached_tokens"] += cac
        
        # Provider aggregated filters
        p_name = str(prov).lower()
        if p_name == "groq":
            bucket["groq_requests"] += rc
            bucket["groq_tokens"] += tc
        elif p_name == "gemini":
            bucket["gemini_requests"] += rc
            bucket["gemini_tokens"] += tc
            
        # Status filters
        st = int(status or 200)
        s_code = str(st)
        if st == 200:
            bucket["status_200"] += rc
        else:
            bucket["total_errors"] += rc
            if st == 429: bucket["status_429"] += rc
            elif s_code.startswith("5"): bucket["status_500"] += rc
            error_dist[s_code] = error_dist.get(s_code, 0) + rc

        # Model-specific bucket
        m_key = f"{prov}/{mod}"
        if m_key in model_timeline_map and day_key in model_timeline_map[m_key]:
            m_bucket = model_timeline_map[m_key][day_key]
            m_bucket["requests"] += rc
            m_bucket["prompt_tokens"] += pc
            m_bucket["completion_tokens"] += cc
            m_bucket["total_tokens"] += tc
            if st != 200:
                m_bucket["errors"] += rc

    # Construct model metrics objects
    model_metrics = []
    for prov_mod_key, days_map in model_timeline_map.items():
        prov, mod = prov_mod_key.split("/", 1)
        # Find basic stats for this model from the first query results
        p_info = next((p for p in providers if p.provider == prov and p.model == mod), None)
        
        model_metrics.append(AdminLLMModelMetrics(
            model=mod,
            provider=prov,
            total_requests=p_info.requests if p_info else 0,
            total_tokens=p_info.tokens_used if p_info else 0,
            success_rate=p_info.success_rate if p_info else 100.0,
            rate_limit=MODEL_LIMITS.get(mod, 900),
            timeline=[AdminLLMModelTimelinePoint(**days_map[d]) for d in sorted(days_map.keys())]
        ))

    # Process timeline success rate
    for day_data in timeline_map.values():
        if day_data["total_requests"] > 0:
            day_data["success_rate"] = round((day_data["status_200"] / day_data["total_requests"]) * 100, 1)

    # 4. Build Advanced Metrics Objects
    def _map_feature(path: str) -> str:
        if not path: return "Core System"
        p = path.lower()
        if "analyze" in p or "resume" in p: return "Resume Intelligence"
        if "discovery" in p or "jobs" in p: return "Job Discovery"
        if "chat" in p: return "AI Assistant"
        if "apply" in p: return "Auto-Applier"
        return path.split("/")[-1].replace("_", " ").title()

    features = [
        AdminLLMFeatureMetric(feature=_map_feature(f), tokens=t, requests=r)
        for f, t, r in feature_rows
    ]

    top_users = [
        AdminLLMUserUsage(user_email=e, total_tokens=t, requests=r)
        for e, t, r in top_user_rows
    ]

    avg_lat, sum_cached, sum_total, avail = global_kpis if global_kpis else (0, 0, 0, 100)
    cache_rate = (sum_cached / sum_total * 100) if sum_total and sum_cached else 0
    tps = sum_total / (14 * 24 * 3600) if sum_total else 0

    overview = AdminLLMSystemOverview(
        avg_latency_ms=round(avg_lat or 0, 1),
        cache_hit_rate=round(cache_rate, 1),
        tps=round(tps, 2),
        availability=round(avail or 100, 1)
    )

    return AdminLLMUsageResponse(
        total_requests=total_requests,
        total_tokens=total_tokens,
        total_estimated_cost=round(total_cost, 4),
        providers=providers,
        timeline=[AdminLLMTimelinePoint(**timeline_map[d]) for d in sorted(timeline_map.keys())],
        models=model_metrics,
        overview=overview,
        features=features,
        top_users=top_users,
        error_distribution=error_dist
    )


@admin_router.get("/users", response_model=List[AdminUserOut])
async def list_users(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    is_active: Optional[bool] = Query(default=None),
    plan: Optional[str] = Query(default=None),
    search: Optional[str] = Query(default=None),
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin),
):
    """List all users with pagination and filters."""
    query = select(User).options(selectinload(User.profile)).order_by(desc(User.created_at))

    if is_active is not None:
        query = query.where(User.is_active == is_active)
    if search:
        query = query.where(
            (User.email.ilike(f"%{search}%")) | 
            (User.full_name.ilike(f"%{search}%")) |
            (User.id.ilike(f"%{search}%"))
        )

    total = (await db.execute(select(func.count()).select_from(query.subquery()))).scalar()
    
    result = await db.execute(
        query.offset((page - 1) * page_size).limit(page_size)
    )
    users = result.scalars().all()
    user_ids = [u.id for u in users]

    # Bulk fetch usage data
    from app.models.chat_usage import ChatUsage
    from app.models.resume import CoverLetter
    from app.models.job import JobAnalysis
    
    month = datetime.now(timezone.utc).strftime("%Y-%m")
    
    # 1. Chat Usage (current month)
    chat_query = await db.execute(
        select(ChatUsage.user_id, ChatUsage.message_count)
        .where(ChatUsage.user_id.in_(user_ids), ChatUsage.month == month)
    )
    chat_map = {r[0]: r[1] for r in chat_query.all()}

    # 2. Cover Letter Tokens
    cl_query = await db.execute(
        select(CoverLetter.user_id, func.sum(CoverLetter.tokens_used))
        .where(CoverLetter.user_id.in_(user_ids))
        .group_by(CoverLetter.user_id)
    )
    cl_map = {r[0]: r[1] or 0 for r in cl_query.all()}

    # 3. Job Analysis Tokens
    job_query = await db.execute(
        select(Job.user_id, func.sum(JobAnalysis.tokens_used))
        .join(JobAnalysis, Job.id == JobAnalysis.job_id)
        .where(Job.user_id.in_(user_ids))
        .group_by(Job.user_id)
    )
    job_map = {r[0]: r[1] or 0 for r in job_query.all()}

    from app.models.application import Application
    
    # 1. Bulk fetch active subscriptions
    sub_query = await db.execute(
        select(Subscription)
        .where(
            Subscription.user_id.in_(user_ids),
            func.lower(Subscription.status.cast(String)) == SubscriptionStatus.ACTIVE.value.lower()
        )
        .order_by(desc(Subscription.start_date))
    )
    all_subs = sub_query.scalars().all()
    sub_map = {}
    for s in all_subs:
        if s.user_id not in sub_map:
            sub_map[s.user_id] = s

    # 2. Bulk fetch application counts
    applied_statuses = [
        ApplicationStatus.APPLIED, ApplicationStatus.VIEWED, ApplicationStatus.SHORTLISTED,
        ApplicationStatus.INTERVIEW_SCHEDULED, ApplicationStatus.INTERVIEW_COMPLETED,
        ApplicationStatus.OFFER_RECEIVED, ApplicationStatus.OFFER_ACCEPTED,
        ApplicationStatus.OFFER_DECLINED, ApplicationStatus.REJECTED, ApplicationStatus.WITHDRAWN
    ]
    app_count_query = await db.execute(
        select(Application.user_id, func.count(Application.id))
        .where(
            Application.user_id.in_(user_ids),
            Application.status.in_(applied_statuses)
        )
        .group_by(Application.user_id)
    )
    app_count_map = {r[0]: r[1] for r in app_count_query.all()}

    user_outputs = []
    for user in users:
        active_sub = sub_map.get(user.id)
        # Avoid misleading default limits when user has no active subscription.
        limit = int(active_sub.ai_credits if active_sub else 0)
        used = int(chat_map.get(user.id, 0) or 0)
        tokens = int((cl_map.get(user.id, 0) or 0) + (job_map.get(user.id, 0) or 0))
        app_count = app_count_map.get(user.id, 0)
        profile_complete = user.profile is not None and bool(user.profile.desired_roles)

        user_outputs.append(AdminUserOut(
            id=user.id,
            email=user.email,
            full_name=user.full_name,
            is_active=user.is_active,
            is_superuser=user.is_superuser,
            created_at=user.created_at,
            last_login_at=user.last_login_at,
            subscription_plan=active_sub.plan.value if active_sub else None,
            subscription_status=active_sub.status.value if active_sub else None,
            applications_count=app_count,
            profile_complete=profile_complete,
            plan=active_sub.plan.value if active_sub else None,
            ai_credits_used=used,
            ai_credits_limit=limit,
            total_tokens=tokens
        ))

    return user_outputs


@admin_router.get("/users/{user_id}", response_model=AdminUserDetailOut)
async def get_user_detail(
    user_id: str,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin),
):
    """Get detailed user information including profile, subscriptions, and payments."""
    result = await db.execute(
        select(User)
        .options(
            selectinload(User.profile),
            selectinload(User.subscriptions),
            selectinload(User.payments),
        )
        .where(User.id == user_id)
    )
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    from app.models.application import Application
    app_count = (await db.execute(
        select(func.count(Application.id)).where(Application.user_id == user.id)
    )).scalar() or 0

    active_sub = next(
        (
            s
            for s in user.subscriptions
            if str(getattr(s.status, "value", s.status)).lower() == SubscriptionStatus.ACTIVE.value
        ),
        None,
    )

    profile_dict = None
    if user.profile:
        profile_dict = {
            "phone": user.profile.phone,
            "location": user.profile.location,
            "experience_level": user.profile.experience_level,
            "desired_roles": user.profile.desired_roles,
            "desired_locations": user.profile.desired_locations,
            "open_to_remote": user.profile.open_to_remote,
            "open_to_hybrid": user.profile.open_to_hybrid,
            "auto_apply_enabled": user.profile.auto_apply_enabled,
            "auto_apply_threshold": user.profile.auto_apply_threshold,
        }

    sub_list = [
        {
            "id": s.id,
            "plan": s.plan.value,
            "status": s.status.value,
            "start_date": s.start_date.isoformat() if s.start_date else None,
            "end_date": s.end_date.isoformat() if s.end_date else None,
            "razorpay_subscription_id": s.razorpay_subscription_id,
        }
        for s in user.subscriptions
    ]

    payment_list = [
        {
            "id": p.id,
            "amount": p.amount,
            "status": p.status.value,
            "plan": p.plan,
            "razorpay_order_id": p.razorpay_order_id,
            "razorpay_payment_id": p.razorpay_payment_id,
            "created_at": p.created_at.isoformat(),
        }
        for p in user.payments
    ]

    return AdminUserDetailOut(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        is_active=user.is_active,
        is_superuser=user.is_superuser,
        created_at=user.created_at,
        last_login_at=user.last_login_at,
        subscription_plan=active_sub.plan.value if active_sub else None,
        subscription_status=active_sub.status.value if active_sub else None,
        total_applications=app_count,
        profile_complete=bool(user.profile and user.profile.desired_roles),
        profile=profile_dict,
        subscriptions=sub_list,
        payments=payment_list,
    )


@admin_router.patch("/users/{user_id}")
async def update_user(
    user_id: str,
    payload: AdminUpdateUserRequest,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin),
):
    """Update user account - activate/deactivate, change plan, toggle automation."""
    result = await db.execute(
        select(User).options(selectinload(User.profile)).where(User.id == user_id)
    )
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    changes = []
    activation_changed = False
    
    if payload.is_active is not None and payload.is_active != user.is_active:
        old_active = user.is_active
        user.is_active = payload.is_active
        activation_changed = True
        changes.append({"field": "is_active", "old": old_active, "new": payload.is_active})

    if payload.plan:
        try:
            plan = PlanTier(payload.plan.upper())
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid plan: {payload.plan}")

        active_sub = (await db.execute(
            select(Subscription).where(
                Subscription.user_id == user.id,
                func.lower(Subscription.status.cast(String)) == SubscriptionStatus.ACTIVE.value.lower(),
            )
        )).scalar_one_or_none()

        if active_sub:
            changes.append({"field": "plan", "old": active_sub.plan.value, "new": payload.plan})
            active_sub.plan = plan
        else:
            from datetime import timedelta
            new_sub = Subscription(
                user_id=user.id,
                plan=plan,
                status=SubscriptionStatus.ACTIVE,
                start_date=datetime.now(timezone.utc),
                end_date=datetime.now(timezone.utc) + timedelta(days=30),
            )
            db.add(new_sub)
            changes.append({"field": "plan", "old": None, "new": payload.plan})

    if payload.auto_apply_enabled is not None and user.profile:
        user.profile.auto_apply_enabled = payload.auto_apply_enabled
        changes.append({"field": "auto_apply_enabled", "old": not payload.auto_apply_enabled, "new": payload.auto_apply_enabled})

    await db.commit()

    if activation_changed:
        try:
            audit = create_audit_entry(
                action=AuditAction.ADMIN_USER_UPDATED,
                resource_type="user",
                resource_id=user.id,
                user_id=admin.id,
                user_email=admin.email,
                details={"action": "activation_change", "new_value": payload.is_active},
            )
            db.add(audit)
            await db.commit()
        except Exception as exc:
            await db.rollback()
            logger.error(
                "Admin user update audit logging failed",
                user_id=user.id,
                admin_id=admin.id,
                error=str(exc),
            )

    await db.refresh(user)

    return {
        "success": True,
        "user_id": user.id,
        "changes": changes,
    }


@admin_router.delete("/users/{user_id}")
async def delete_user(
    user_id: str,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin),
):
    """Delete a user account (soft delete via is_active=False)."""
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.is_active = False
    await db.commit()

    try:
        audit = create_audit_entry(
            action=AuditAction.ADMIN_USER_DELETED,
            resource_type="user",
            resource_id=user.id,
            user_id=admin.id,
            user_email=admin.email,
            details={"action": "soft_delete", "email": user.email},
        )
        db.add(audit)
        await db.commit()
    except Exception as exc:
        await db.rollback()
        logger.error(
            "Admin user delete audit logging failed",
            user_id=user.id,
            admin_id=admin.id,
            error=str(exc),
        )

    return {"success": True, "message": f"User {user.email} has been deactivated"}


@admin_router.get("/subscriptions", response_model=List[dict])
async def list_subscriptions(
    status: Optional[str] = Query(default=None),
    plan: Optional[str] = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin),
):
    """List all subscriptions with filters."""
    query = (
        select(Subscription)
        .options(selectinload(Subscription.user))
        .order_by(desc(Subscription.created_at))
    )

    if status:
        query = query.where(func.lower(Subscription.status.cast(String)) == status.lower())
    if plan:
        query = query.where(Subscription.plan == plan)

    result = await db.execute(
        query.offset((page - 1) * page_size).limit(page_size)
    )
    subs = result.scalars().all()

    return [
        {
            "id": s.id,
            "user_email": s.user.email if s.user else "Unknown",
            "plan": s.plan.value,
            "status": s.status.value,
            "start_date": s.start_date.isoformat() if s.start_date else None,
            "end_date": s.end_date.isoformat() if s.end_date else None,
        }
        for s in subs
    ]


@admin_router.get("/payments", response_model=dict)
async def list_payments(
    status: Optional[str] = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin),
):
    """List all payments with filters."""
    total = (await db.execute(select(func.count(Payment.id)))).scalar() or 0

    query = (
        select(Payment)
        .options(selectinload(Payment.user))
        .order_by(desc(Payment.created_at))
    )

    if status:
        query = query.where(func.lower(Payment.status.cast(String)) == status.lower())

    result = await db.execute(
        query.offset((page - 1) * page_size).limit(page_size)
    )
    payments = result.scalars().all()

    items = [
        AdminPaymentOut(
            id=p.id,
            user_email=p.user.email if p.user else "Unknown",
            amount=p.amount,
            currency=p.currency,
            status=p.status.value,
            plan=p.plan,
            razorpay_order_id=p.razorpay_order_id,
            razorpay_payment_id=p.razorpay_payment_id,
            created_at=p.created_at,
        )
        for p in payments
    ]

    return {
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size,
    }


@admin_router.post("/payments/{payment_id}/refund")
async def refund_payment(
    payment_id: str,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin),
):
    """Refund a payment via Razorpay API."""
    from app.core.config import settings
    
    result = await db.execute(
        select(Payment).options(selectinload(Payment.user)).where(Payment.id == payment_id)
    )
    payment = result.scalar_one_or_none()
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")

    if payment.status != PaymentStatus.CAPTURED:
        raise HTTPException(status_code=400, detail="Only captured payments can be refunded")

    # Call Razorpay API to refund
    if payment.razorpay_payment_id:
        try:
            import httpx
            async with httpx.AsyncClient(timeout=30) as client:
                resp = await client.post(
                    f"https://api.razorpay.com/v1/payments/{payment.razorpay_payment_id}/refund",
                    auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET),
                    json={"amount": payment.amount}  # amount in paise
                )
                if resp.status_code != 200:
                    raise HTTPException(status_code=500, detail=f"Razorpay refund failed: {resp.text}")
                razorpay_refund = resp.json()
        except httpx.RequestError as e:
            raise HTTPException(status_code=500, detail=f"Failed to connect to Razorpay: {str(e)}")
    else:
        raise HTTPException(status_code=400, detail="No razorpay_payment_id found for this payment")

    payment.status = PaymentStatus.REFUNDED
    await db.commit()

    audit = create_audit_entry(
        action="payment.refunded",
        resource_type="payment",
        resource_id=payment.id,
        user_id=admin.id,
        user_email=admin.email,
        details={"amount": payment.amount, "user_email": payment.user.email},
    )
    db.add(audit)
    await db.commit()

    return {
        "success": True,
        "message": f"Payment of ₹{payment.amount/100} has been refunded via Razorpay",
    }


@admin_router.get("/audit-logs", response_model=List[AdminAuditLogOut])
async def get_audit_logs(
    user_id: Optional[str] = Query(default=None),
    action: Optional[str] = Query(default=None),
    resource_type: Optional[str] = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin),
):
    """Get audit logs with filters."""
    query = select(AuditLog).order_by(desc(AuditLog.timestamp))

    if user_id:
        query = query.where(AuditLog.user_id == user_id)
    if action:
        query = query.where(AuditLog.action.ilike(f"%{action}%"))
    if resource_type:
        query = query.where(AuditLog.resource_type == resource_type)

    result = await db.execute(
        query.offset((page - 1) * page_size).limit(page_size)
    )
    logs = result.scalars().all()

    return [
        AdminAuditLogOut(
            id=str(log.id),
            user_email=log.user_email,
            action=log.action,
            resource_type=log.resource_type,
            resource_id=log.resource_id,
            ip_address=log.ip_address,
            success=log.success,
            timestamp=log.timestamp,
            details=log.details,
        )
        for log in logs
    ]


@admin_router.get("/system/health")
async def system_health(
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin),
):
    """Check system health - database, Redis, worker status."""
    health = {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "checks": {},
    }

    try:
        await db.execute(select(1))
        health["checks"]["database"] = "healthy"
    except Exception as e:
        health["checks"]["database"] = f"unhealthy: {str(e)}"
        health["status"] = "degraded"

    try:
        import redis
        from app.core.config import settings
        redis_url = settings.REDIS_URL.decode() if isinstance(settings.REDIS_URL, bytes) else settings.REDIS_URL
        r = redis.from_url(redis_url, socket_connect_timeout=2, socket_timeout=2)
        r.ping()
        health["checks"]["redis"] = "healthy"
    except Exception as e:
        health["checks"]["redis"] = f"unavailable: {str(e)}"

    try:
        from app.celery_app import celery_app
        inspect = celery_app.control.inspect()
        stats = inspect.stats(timeout=3)
        if stats:
            health["checks"]["celery"] = "healthy"
            health["celery_workers"] = list(stats.keys())
        else:
            health["checks"]["celery"] = "no_workers"
    except Exception as e:
        health["checks"]["celery"] = f"unavailable: {str(e)}"

    return health


@admin_router.get("/automation/status")
async def get_automation_status(
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin),
):
    """Get automation status across all users."""
    from app.models.application import Application, ApplicationStatus
    from sqlalchemy import or_, func, case

    today = datetime.now(timezone.utc).date()
    
    # Users with automation enabled
    users_with_automation = (await db.execute(
        select(func.count(User.id)).where(User.is_active == True)
    )).scalar() or 0

    # Applications by status
    pending_apps = (await db.execute(
        select(func.count(Application.id)).where(
            func.lower(Application.status.cast(String)) == ApplicationStatus.QUEUED.value.lower()
        )
    )).scalar() or 0

    applying_apps = (await db.execute(
        select(func.count(Application.id)).where(
            func.lower(Application.status.cast(String)) == ApplicationStatus.APPLYING.value.lower()
        )
    )).scalar() or 0

    # Applications applied today
    applied_today = (await db.execute(
        select(func.count(Application.id)).where(
            func.lower(Application.status.cast(String)) == ApplicationStatus.APPLIED.value.lower(),
            func.date(Application.applied_at) == today,
        )
    )).scalar() or 0

    # Total applications ever
    total_apps = (await db.execute(
        select(func.count(Application.id))
    )).scalar() or 0

    # Success rate (applications that got a response)
    success_count = (await db.execute(
        select(func.count(Application.id)).where(
            func.lower(Application.status.cast(String)).in_([ApplicationStatus.APPLIED.value.lower(), ApplicationStatus.SHORTLISTED.value.lower()])
        )
    )).scalar() or 0
    
    success_rate = round((success_count / total_apps * 100), 1) if total_apps > 0 else 0

    # Failed applications
    failed_apps = (await db.execute(
        select(func.count(Application.id)).where(
            func.lower(Application.status.cast(String)) == ApplicationStatus.FAILED.value.lower()
        )
    )).scalar() or 0

    return {
        "applications_today": applied_today,
        "success_rate": success_rate,
        "failed": failed_apps,
        "queue_size": pending_apps + applying_apps,
        "pending_applications": pending_apps,
        "applying_applications": applying_apps,
        "applied_today": applied_today,
        "total_applications": total_apps,
        "users_with_automation": users_with_automation,
        "status": "running" if pending_apps > 0 or applying_apps > 0 else "idle",
    }


@admin_router.post("/automation/disable/{user_id}")
async def disable_user_automation(
    user_id: str,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin),
):
    """Disable automation for a specific user."""
    result = await db.execute(
        select(User).options(selectinload(User.profile)).where(User.id == user_id)
    )
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user.profile:
        user.profile.auto_apply_enabled = False

    audit = create_audit_entry(
        action="admin.automation_disabled",
        resource_type="user",
        resource_id=user.id,
        user_id=admin.id,
        user_email=admin.email,
        details={"reason": "admin_action"},
    )
    db.add(audit)
    await db.commit()

    return {
        "success": True,
        "message": f"Automation disabled for user {user.email}",
    }


@admin_router.get("/settings")
async def get_platform_settings(
    admin: User = Depends(require_admin),
):
    """Get platform settings."""
    return {
        "plans": {
            "starter": {"price": 200, "daily_limit": 150, "priority": 1},
            "pro": {"price": 400, "daily_limit": 250, "priority": 2},
            "premium": {"price": 800, "daily_limit": 500, "priority": 3},
        },
        "features": {
            "job_scraping": True,
            "ai_analysis": True,
            "auto_apply": True,
            "resume_generation": True,
            "cover_letter_generation": True,
        },
    }


@admin_router.get("/queue/status")
async def get_queue_status(
    admin: User = Depends(require_admin),
):
    """Get queue status with APScheduler."""
    from app.services.scheduler_service import SchedulerService
    from sqlalchemy import select, func, cast, String
    from app.models.application import Application, ApplicationStatus
    from app.models.job import Job
    
    scheduler = SchedulerService()
    scheduler_running = False
    try:
        scheduler_running = scheduler.scheduler.running
    except Exception:
        pass
    jobs = scheduler.list_jobs()
    
    queue_data = {
        "pending": 0,
        "applying": 0,
        "failed": 0,
        "total_jobs": 0,
        "scheduled_tasks": [],
        "scheduler_running": scheduler_running,
        "celery_workers": [],
        "celery_queues": {},
        "celery_error": None,
    }
    
    try:
        from app.celery_app import celery_app
        inspect = celery_app.control.inspect(timeout=2)
        
        stats = inspect.stats()
        if stats:
            queue_data["celery_workers"] = [
                {"name": name, "status": "active", "active_tasks": info.get("pool", {}).get("max", 0)}
                for name, info in stats.items()
            ]
        
        active = inspect.active()
        if active:
            for queue_name, tasks in active.items():
                queue_data["celery_queues"][queue_name] = len(tasks)
        
        reserved = inspect.reserved()
        if reserved:
            for queue_name, tasks in reserved.items():
                if queue_name in queue_data["celery_queues"]:
                    queue_data["celery_queues"][queue_name] += len(tasks)
                else:
                    queue_data["celery_queues"][queue_name] = len(tasks)
    except Exception as e:
        logger.warning("Celery inspection failed", error=str(e))
        queue_data["celery_error"] = f"Celery unavailable: {str(e)}"
    
    async with get_db_context() as db:
        pending_apps = (await db.execute(
            select(func.count(Application.id)).where(
                func.lower(Application.status.cast(String)) == ApplicationStatus.QUEUED.value.lower()
            )
        )).scalar() or 0
        
        applying_apps = (await db.execute(
            select(func.count(Application.id)).where(
                func.lower(Application.status.cast(String)) == ApplicationStatus.APPLYING.value.lower()
            )
        )).scalar() or 0
        
        failed_apps = (await db.execute(
            select(func.count(Application.id)).where(
                func.lower(Application.status.cast(String)) == ApplicationStatus.FAILED.value.lower()
            )
        )).scalar() or 0
        
        total_jobs = (await db.execute(
            select(func.count(Job.id))
        )).scalar() or 0
    
    scheduled_tasks = []
    for job in jobs:
        if isinstance(job, dict):
            scheduled_tasks.append({
                "id": job.get("id"),
                "name": job.get("name"),
                "next_run": str(job.get("next_run")) if job.get("next_run") else None,
            })
        else:
            scheduled_tasks.append({
                "id": getattr(job, "id", None),
                "name": getattr(job, "name", None),
                "next_run": str(getattr(job, "next_run_time", None)) if getattr(job, "next_run_time", None) else None,
            })
    
    return {
        **queue_data,
        "pending": pending_apps,
        "applying": applying_apps,
        "failed": failed_apps,
        "total_jobs": total_jobs,
        "scheduled_tasks": scheduled_tasks,
    }


@admin_router.get("/queue/failed")
async def get_failed_jobs(
    admin: User = Depends(require_admin),
    limit: int = 50,
):
    """Get failed applications with error details."""
    async with get_db_context() as db:
        result = await db.execute(
            select(Application)
            .where(Application.status == ApplicationStatus.FAILED)
            .order_by(Application.updated_at.desc())
            .limit(limit)
        )
        failed = result.scalars().all()
        
        return {
            "failed_jobs": [
                {
                    "id": app.id,
                    "user_id": app.user_id,
                    "job_title": app.job_title_snapshot,
                    "company": app.company_snapshot,
                    "error": app.bot_error,
                    "retry_count": app.retry_count,
                    "updated_at": app.updated_at.isoformat() if app.updated_at else None,
                }
                for app in failed
            ]
        }


@admin_router.post("/queue/retry/{application_id}")
async def retry_application(
    application_id: str,
    admin: User = Depends(require_admin),
):
    """Retry a failed application."""
    async with get_db_context() as db:
        result = await db.execute(
            select(Application).where(Application.id == application_id)
        )
        app = result.scalar_one_or_none()
        
        if not app:
            raise HTTPException(status_code=404, detail="Application not found")
        
        if app.status != ApplicationStatus.FAILED:
            raise HTTPException(status_code=400, detail="Only failed applications can be retried")
        
        app.status = ApplicationStatus.QUEUED
        app.bot_error = None
        app.retry_count = (app.retry_count or 0) + 1
        await db.commit()
        
        return {"success": True, "message": f"Application {application_id} queued for retry"}


@admin_router.post("/system/{action}")
async def system_action(
    action: str,
    admin: User = Depends(require_admin),
):
    """Execute system actions: run-scraper, clear-queue, restart-worker."""
    import structlog
    log = structlog.get_logger()
    
    if action == "run-scraper":
        from app.agents.scrapers.internshala import InternshalaScraper
        scraper = InternshalaScraper()
        try:
            result = await scraper.run()
            # Handle dict response from scraper
            if isinstance(result, dict):
                jobs_count = result.get("jobs", result.get("count", 0))
                message = f"Scraped {jobs_count} jobs"
            else:
                jobs_count = result if isinstance(result, int) else 0
                message = f"Scraped {jobs_count} jobs"
            return {"success": True, "message": message}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    elif action == "clear-queue":
        try:
            from app.celery_app import celery_app
            celery_app.control.purge()
            return {"success": True, "message": "Queue cleared"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    elif action == "restart-worker":
        try:
            from app.celery_app import celery_app
            celery_app.control.broadcast("shutdown", destination=["celery@*"])
            return {"success": True, "message": "Worker restart signal sent"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    return {"success": False, "error": "Unknown action"}


@admin_router.get("/applications")
async def list_applications(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin),
):
    """List all applications."""
    query = (
        select(Application)
        .options(selectinload(Application.user))
        .order_by(desc(Application.created_at))
    )
    
    total = await db.scalar(select(func.count()).select_from(query.subquery()))
    
    query = query.offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    applications = result.scalars().all()
    
    items = [
        {
            "id": str(a.id),
            "user_email": a.user.email if a.user else "Unknown",
            "job_title": a.job_title_snapshot or "Unknown",
            "company": a.company_snapshot or "Unknown",
            "status": a.status.value if hasattr(a.status, 'value') else str(a.status),
            "error": a.bot_error,
            "created_at": a.created_at.isoformat() if a.created_at else None,
        }
        for a in applications
    ]
    
    return {"items": items, "total": total, "page": page, "page_size": page_size}


@admin_router.get("/jobs")
async def list_jobs(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin),
):
    """List all jobs."""
    query = select(Job).order_by(desc(Job.scraped_at))
    
    total = await db.scalar(select(func.count()).select_from(query.subquery()))
    
    query = query.offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    jobs = result.scalars().all()
    
    items = [
        {
            "id": str(j.id),
            "title": j.title,
            "company": j.company_name,
            "source": getattr(j.source, "value", str(j.source)) if j.source else "internshala",
            "status": "active" if j.is_active else "inactive",
            "scraped_at": j.scraped_at.isoformat() if j.scraped_at else None,
        }
        for j in jobs
    ]
    
    return {"items": items, "total": total, "page": page, "page_size": page_size}


@admin_router.get("/analytics")
async def get_analytics(
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin),
):
    """Get analytics data for charts."""
    from datetime import timedelta
    from sqlalchemy import func
    
    today = datetime.now(timezone.utc).date()
    seven_days_ago = today - timedelta(days=6)
    
    app_query = (
        select(
            func.date(Application.created_at).label("date"),
            func.count().label("count")
        )
        .where(func.date(Application.created_at) >= seven_days_ago)
        .group_by(func.date(Application.created_at))
        .order_by(func.date(Application.created_at))
    )
    app_result = await db.execute(app_query)
    applications_by_day = [{"date": str(r.date), "count": r.count} for r in app_result.all()]
    
    pay_query = (
        select(
            func.date(Payment.created_at).label("date"),
            func.sum(Payment.amount).label("amount")
        )
        .where(
            func.lower(Payment.status.cast(String)) == PaymentStatus.CAPTURED.value.lower()
        )
        .where(func.date(Payment.created_at) >= seven_days_ago)
        .group_by(func.date(Payment.created_at))
        .order_by(func.date(Payment.created_at))
    )
    pay_result = await db.execute(pay_query)
    revenue_by_day = [{"date": str(r.date), "amount": float(r.amount or 0)} for r in pay_result.all()]
    
    user_query = (
        select(
            func.date(User.created_at).label("date"),
            func.count().label("count")
        )
        .where(func.date(User.created_at) >= seven_days_ago)
        .group_by(func.date(User.created_at))
        .order_by(func.date(User.created_at))
    )
    user_result = await db.execute(user_query)
    users_by_day = [{"date": str(r.date), "count": r.count} for r in user_result.all()]
    
    return {
        "applications_by_day": applications_by_day,
        "revenue_by_day": revenue_by_day,
        "users_by_day": users_by_day,
    }


@admin_router.get("/features")
async def get_feature_flags(
    admin: User = Depends(require_admin),
):
    """Get feature flags."""
    return [
        {"key": "auto_apply", "label": "Auto Apply", "description": "Automatically apply to matching jobs", "enabled": True},
        {"key": "ai_chat", "label": "AI Chat", "description": "AI-powered chat support", "enabled": True},
        {"key": "payments", "label": "Payments", "description": "Enable payment system", "enabled": True},
        {"key": "scraper", "label": "Scraper", "description": "Enable job scraping", "enabled": True},
        {"key": "maintenance", "label": "Maintenance Mode", "description": "Show maintenance page to users", "enabled": False},
    ]


@admin_router.post("/users/bulk")
async def bulk_user_action(
    user_ids: List[str],
    action: str,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin),
):
    """Bulk user actions - activate, deactivate, delete."""
    if action not in ["activate", "deactivate", "delete"]:
        raise HTTPException(status_code=400, detail="Invalid action")
    
    result = await db.execute(select(User).where(User.id.in_(user_ids)))
    users = result.scalars().all()
    
    updated = 0
    for user in users:
        if action == "activate":
            user.is_active = True
            updated += 1
        elif action == "deactivate":
            user.is_active = False
            updated += 1
        elif action == "delete":
            user.is_active = False
            updated += 1
    
    await db.commit()
    
    audit = create_audit_entry(
        action=AuditAction.ADMIN_USER_UPDATED,
        resource_type="user",
        resource_id="bulk",
        user_id=admin.id,
        user_email=admin.email,
        details={"action": f"bulk_{action}", "count": updated},
    )
    db.add(audit)
    await db.commit()
    
    return {"success": True, "updated": updated}


@admin_router.post("/users/{user_id}/change-plan")
async def change_user_plan(
    user_id: str,
    plan: str,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin),
):
    """Change a user's subscription plan."""
    from datetime import timedelta
    
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    try:
        plan_enum = PlanTier(plan)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid plan: {plan}")
    
    active_sub = (await db.execute(
        select(Subscription).where(
            Subscription.user_id == user.id,
            func.lower(Subscription.status.cast(String)) == SubscriptionStatus.ACTIVE.value.lower(),
        )
    )).scalar_one_or_none()
    
    if active_sub:
        active_sub.plan = plan_enum
    else:
        new_sub = Subscription(
            user_id=user.id,
            plan=plan_enum,
            status=SubscriptionStatus.ACTIVE,
            start_date=datetime.now(timezone.utc),
            end_date=datetime.now(timezone.utc) + timedelta(days=30),
        )
        db.add(new_sub)
    
    await db.commit()
    
    audit = create_audit_entry(
        action=AuditAction.ADMIN_USER_UPDATED,
        resource_type="user",
        resource_id=user.id,
        user_id=admin.id,
        user_email=admin.email,
        details={"action": "plan_change", "new_plan": plan},
    )
    db.add(audit)
    await db.commit()
    
    return {"success": True, "message": f"Plan changed to {plan} for {user.email}"}


@admin_router.get("/platforms/messages")
async def get_platform_messages(
    platform: Optional[str] = Query(default=None),
    important_only: bool = Query(default=False),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=50, le=100),
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin),
):
    """Get platform messages from all users."""
    from app.models.platform_message import PlatformMessage
    
    query = select(PlatformMessage).order_by(desc(PlatformMessage.created_at))
    
    if platform:
        query = query.where(PlatformMessage.platform == platform)
    if important_only:
        query = query.where(PlatformMessage.is_important == True)
    
    total = (await db.execute(select(func.count()).select_from(query.subquery()))).scalar()
    
    result = await db.execute(query.offset((page - 1) * page_size).limit(page_size))
    messages = result.scalars().all()
    
    items = [
        {
            "id": m.id,
            "user_id": m.user_id,
            "platform": m.platform,
            "subject": m.subject,
            "sender": m.sender_name,
            "is_important": m.is_important,
            "important_keywords": m.importance_keywords,
            "created_at": m.created_at.isoformat() if m.created_at else None,
        }
        for m in messages
    ]
    
    return {"items": items, "total": total, "page": page, "page_size": page_size}


@admin_router.get("/subscriptions", response_model=List[AdminSubscriptionOut])
async def list_subscriptions(
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin),
):
    """List all user subscriptions with user emails."""
    query = (
        select(
            Subscription.id,
            User.email.label("user_email"),
            Subscription.plan,
            Subscription.status,
            Subscription.start_date,
            Subscription.end_date,
        )
        .join(User, Subscription.user_id == User.id)
        .order_by(desc(Subscription.start_date))
    )
    
    result = await db.execute(query)
    subs = []
    for r in result.all():
        # Get daily limit based on plan
        from app.models.subscription import PLAN_DAILY_LIMITS, PlanTier
        daily_limit = PLAN_DAILY_LIMITS.get(PlanTier(r.plan), 50)
        
        subs.append(AdminSubscriptionOut(
            id=r.id,
            user_email=r.user_email,
            plan=r.plan.value if hasattr(r.plan, 'value') else str(r.plan),
            status=r.status.value if hasattr(r.status, 'value') else str(r.status),
            start_date=r.start_date,
            end_date=r.end_date,
            daily_limit=daily_limit
        ))
    return subs


@admin_router.get("/payments", response_model=dict)
async def list_payments(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin),
):
    """List all payments with user emails and pagination."""
    # Count total
    total = (await db.execute(select(func.count(Payment.id)))).scalar() or 0
    
    query = (
        select(
            Payment.id,
            User.email.label("user_email"),
            Payment.amount,
            Payment.currency,
            Payment.status,
            Payment.created_at,
        )
        .join(User, Payment.user_id == User.id)
        .order_by(desc(Payment.created_at))
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    
    result = await db.execute(query)
    items = []
    for r in result.all():
        items.append(AdminPaymentOut(
            id=r.id,
            user_email=r.user_email,
            amount=r.amount,
            currency=r.currency,
            status=r.status.value if hasattr(r.status, 'value') else str(r.status),
            created_at=r.created_at,
        ))
    
    return {
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size,
    }