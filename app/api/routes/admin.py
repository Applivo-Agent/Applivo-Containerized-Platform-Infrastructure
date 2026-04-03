"""
app/api/routes/admin.py
───────────────────────
Admin Service - User management, subscription management, payment monitoring,
system control, automation management, and analytics.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select, desc, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from typing import List, Optional
from datetime import datetime, timedelta, timezone
from pydantic import BaseModel, EmailStr

from app.core.database import get_db
from app.api.routes.auth import get_current_user
from app.models.user import User, UserProfile
from app.models.subscription import Subscription, SubscriptionStatus, PlanTier, Payment, PaymentStatus
from app.models.audit import AuditLog, AuditAction, create_audit_entry

admin_router = APIRouter(prefix="/admin", tags=["Admin"])


class AdminUserOut(BaseModel):
    id: str
    email: str
    full_name: str
    is_active: bool
    is_superuser: bool
    created_at: datetime
    last_login_at: Optional[datetime]
    subscription_plan: Optional[str]
    subscription_status: Optional[str]
    total_applications: int
    profile_complete: bool

    class Config:
        from_attributes = True


class AdminUserDetailOut(AdminUserOut):
    profile: Optional[dict]
    subscriptions: List[dict]
    payments: List[dict]


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
            Subscription.status == SubscriptionStatus.ACTIVE,
            or_(Subscription.end_date == None, Subscription.end_date > now)
        )
    )).scalar() or 0

    total_revenue = (await db.execute(
        select(func.sum(Payment.amount)).where(Payment.status == PaymentStatus.CAPTURED)
    )).scalar() or 0

    revenue_this_month = (await db.execute(
        select(func.sum(Payment.amount)).where(
            Payment.status == PaymentStatus.CAPTURED,
            Payment.created_at >= month_start
        )
    )).scalar() or 0

    from app.models.application import Application
    total_apps = (await db.execute(select(func.count(Application.id)))).scalar() or 0
    
    apps_this_month = (await db.execute(
        select(func.count(Application.id)).where(Application.created_at >= month_start)
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
            (User.email.ilike(f"%{search}%")) | (User.full_name.ilike(f"%{search}%"))
        )

    total = (await db.execute(select(func.count()).select_from(query.subquery()))).scalar()
    
    result = await db.execute(
        query.offset((page - 1) * page_size).limit(page_size)
    )
    users = result.scalars().all()

    from app.models.application import Application
    user_outputs = []
    for user in users:
        active_sub = (await db.execute(
            select(Subscription).where(
                Subscription.user_id == user.id,
                Subscription.status == SubscriptionStatus.ACTIVE,
            ).order_by(desc(Subscription.start_date)).limit(1)
        )).scalar_one_or_none()

        app_count = (await db.execute(
            select(func.count(Application.id)).where(Application.user_id == user.id)
        )).scalar() or 0

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
            total_applications=app_count,
            profile_complete=profile_complete,
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

    active_sub = next((s for s in user.subscriptions if s.status == SubscriptionStatus.ACTIVE), None)

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
    
    if payload.is_active is not None and payload.is_active != user.is_active:
        user.is_active = payload.is_active
        changes.append({"field": "is_active", "old": not payload.is_active, "new": payload.is_active})

        audit = create_audit_entry(
            action=AuditAction.ADMIN_USER_UPDATED,
            resource_type="user",
            resource_id=user.id,
            user_id=admin.id,
            user_email=admin.email,
            details={"action": "activation_change", "new_value": payload.is_active},
        )
        db.add(audit)

    if payload.plan:
        try:
            plan = PlanTier(payload.plan)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid plan: {payload.plan}")

        active_sub = (await db.execute(
            select(Subscription).where(
                Subscription.user_id == user.id,
                Subscription.status == SubscriptionStatus.ACTIVE,
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
        query = query.where(Subscription.status == status)
    if plan:
        query = query.where(Subscription.plan == plan)

    result = await db.execute(
        query.offset((page - 1) * page_size).limit(page_size)
    )
    subs = result.scalars().all()

    return [
        {
            "id": s.id,
            "user_email": s.user.email,
            "plan": s.plan.value,
            "status": s.status.value,
            "start_date": s.start_date.isoformat() if s.start_date else None,
            "end_date": s.end_date.isoformat() if s.end_date else None,
        }
        for s in subs
    ]


@admin_router.get("/payments", response_model=List[AdminPaymentOut])
async def list_payments(
    status: Optional[str] = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin),
):
    """List all payments with filters."""
    query = (
        select(Payment)
        .options(selectinload(Payment.user))
        .order_by(desc(Payment.created_at))
    )

    if status:
        query = query.where(Payment.status == status)

    result = await db.execute(
        query.offset((page - 1) * page_size).limit(page_size)
    )
    payments = result.scalars().all()

    return [
        AdminPaymentOut(
            id=p.id,
            user_email=p.user.email,
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


@admin_router.post("/payments/{payment_id}/refund")
async def refund_payment(
    payment_id: str,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin),
):
    """Refund a payment (updates status, actual refund via Razorpay API in production)."""
    result = await db.execute(
        select(Payment).options(selectinload(Payment.user)).where(Payment.id == payment_id)
    )
    payment = result.scalar_one_or_none()
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")

    if payment.status != PaymentStatus.CAPTURED:
        raise HTTPException(status_code=400, detail="Only captured payments can be refunded")

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
        "message": f"Payment of ₹{payment.amount/100} has been marked as refunded",
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
        r = redis.from_url(settings.REDIS_URL.decode() if isinstance(settings.REDIS_URL, bytes) else settings.REDIS_URL)
        r.ping()
        health["checks"]["redis"] = "healthy"
    except Exception as e:
        health["checks"]["redis"] = f"unhealthy: {str(e)}"
        health["status"] = "degraded"

    try:
        from app.core.celery_app import celery_app
        inspect = celery_app.control.inspect()
        stats = inspect.stats()
        if stats:
            health["checks"]["celery"] = "healthy"
            health["celery_workers"] = list(stats.keys())
        else:
            health["checks"]["celery"] = "no_workers"
    except Exception as e:
        health["checks"]["celery"] = f"error: {str(e)}"

    return health


@admin_router.get("/automation/status")
async def get_automation_status(
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin),
):
    """Get automation status across all users."""
    from app.models.application import Application
    from sqlalchemy import or_

    users_with_automation = (await db.execute(
        select(func.count(User.id)).where(User.is_active == True)
    )).scalar() or 0

    pending_apps = (await db.execute(
        select(func.count(Application.id)).where(
            Application.status == "pending_approval"
        )
    )).scalar() or 0

    queued_apps = (await db.execute(
        select(func.count(Application.id)).where(
            Application.status == "queued"
        )
    )).scalar() or 0

    applied_today = (await db.execute(
        select(func.count(Application.id)).where(
            Application.status == "applied",
            func.date(Application.applied_at) == datetime.now().date(),
        )
    )).scalar() or 0

    return {
        "users_with_active_accounts": users_with_automation,
        "pending_applications": pending_apps,
        "queued_applications": queued_apps,
        "applied_today": applied_today,
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