"""
app/services/analyze_budget_service.py
─────────────────────────────────────
Analyze token budget service.
Enforces plan-based per-run and monthly token visibility for job analysis.
"""

from __future__ import annotations

from datetime import datetime, timezone

import structlog
from sqlalchemy import func, select, text
from sqlalchemy.exc import ProgrammingError

from app.core.database import get_db_context
from app.models.interview import Notification, NotificationChannel, NotificationStatus
from app.models.job import Job, JobAnalysis
from app.models.subscription import (
    PlanTier,
    PLAN_ANALYZE_MONTHLY_TOKEN_LIMITS,
    PLAN_ANALYZE_RUN_TOKEN_LIMITS,
)
from app.services.notification_service import NotificationService
from app.services.subscription_service import subscription_service

logger = structlog.get_logger()


ADMIN_UNLIMITED_SENTINEL = 999_999_999


class AnalyzeBudgetService:
    """Computes analyze token limits and monthly usage by plan."""

    async def _jobs_user_id_exists(self) -> bool:
        async with get_db_context() as db:
            result = await db.execute(
                text(
                    """
                    SELECT 1
                    FROM information_schema.columns
                    WHERE table_schema = current_schema()
                      AND table_name = 'jobs'
                      AND column_name = 'user_id'
                    LIMIT 1
                    """
                )
            )
            return result.scalar_one_or_none() is not None

    async def _maybe_send_usage_warning_email(
        self,
        user_id: str,
        plan: str,
        monthly_limit: int,
        used_month: int,
    ) -> None:
        """Send one user-specific 80% usage warning email per month."""
        if monthly_limit <= 0:
            return

        usage_ratio = used_month / monthly_limit
        if usage_ratio < 0.8 or used_month >= monthly_limit:
            return

        month_start = datetime.now(timezone.utc).replace(day=1, hour=0, minute=0, second=0, microsecond=0)

        async with get_db_context() as db:
            existing = await db.execute(
                select(Notification.id)
                .where(
                    Notification.user_id == user_id,
                    Notification.channel == NotificationChannel.EMAIL,
                    Notification.event_type == "analyze_token_usage_warning_80",
                    Notification.created_at >= month_start,
                )
                .limit(1)
            )
            if existing.scalar_one_or_none():
                return

            remaining = max(0, monthly_limit - used_month)
            notif = Notification(
                user_id=user_id,
                channel=NotificationChannel.EMAIL,
                status=NotificationStatus.PENDING,
                title="Analyze Token Usage Alert (80% Reached)",
                body=(
                    "You've used 80% or more of your monthly analyze token budget.\n\n"
                    f"Plan: {plan.upper()}\n"
                    f"Used this month: {used_month:,} tokens\n"
                    f"Remaining this month: {remaining:,} tokens\n"
                    f"Monthly limit: {monthly_limit:,} tokens\n\n"
                    "To avoid interruption, consider upgrading your plan."
                ),
                event_type="analyze_token_usage_warning_80",
                data={
                    "plan": plan,
                    "used_month_tokens": used_month,
                    "remaining_month_tokens": remaining,
                    "monthly_limit_tokens": monthly_limit,
                    "threshold": 0.8,
                },
            )
            db.add(notif)
            await db.flush()
            notif_id = notif.id
            await db.commit()

        try:
            await NotificationService().send_email(str(notif_id))
        except Exception as exc:
            logger.warning(
                "Failed to send analyze usage warning email",
                user_id=user_id,
                notification_id=str(notif_id),
                error=str(exc),
            )

    async def _maybe_send_limit_reached_email(
        self,
        user_id: str,
        plan: str,
        monthly_limit: int,
        used_month: int,
    ) -> None:
        """Send one user-specific token-limit email per month when analyze budget is exhausted."""
        month_start = datetime.now(timezone.utc).replace(day=1, hour=0, minute=0, second=0, microsecond=0)

        async with get_db_context() as db:
            existing = await db.execute(
                select(Notification.id)
                .where(
                    Notification.user_id == user_id,
                    Notification.channel == NotificationChannel.EMAIL,
                    Notification.event_type == "analyze_token_limit_reached",
                    Notification.created_at >= month_start,
                )
                .limit(1)
            )
            if existing.scalar_one_or_none():
                return

            notif = Notification(
                user_id=user_id,
                channel=NotificationChannel.EMAIL,
                status=NotificationStatus.PENDING,
                title="Analyze Token Limit Reached",
                body=(
                    "You've reached your monthly analyze token limit.\n\n"
                    f"Plan: {plan.upper()}\n"
                    f"Used this month: {used_month:,} tokens\n"
                    f"Monthly limit: {monthly_limit:,} tokens\n\n"
                    "Upgrade your plan or wait for the next monthly cycle to continue analyzing jobs."
                ),
                event_type="analyze_token_limit_reached",
                data={
                    "plan": plan,
                    "used_month_tokens": used_month,
                    "monthly_limit_tokens": monthly_limit,
                },
            )
            db.add(notif)
            await db.flush()
            notif_id = notif.id
            await db.commit()

        try:
            await NotificationService().send_email(str(notif_id))
        except Exception as exc:
            logger.warning(
                "Failed to send analyze limit reached email",
                user_id=user_id,
                notification_id=str(notif_id),
                error=str(exc),
            )

    async def get_analyze_budget(self, user_id: str) -> dict:
        from app.models.user import User

        async with get_db_context() as db:
            user_result = await db.execute(select(User).where(User.id == user_id))
            user = user_result.scalar_one_or_none()

        if not user:
            return {
                "allowed": False,
                "plan": "none",
                "is_unlimited": False,
                "run_limit_tokens": 0,
                "monthly_limit_tokens": 0,
                "daily_plan_tokens": 0,
                "used_day_tokens": 0,
                "used_month_tokens": 0,
                "remaining_month_tokens": 0,
                "reason": "User not found",
            }

        is_superuser = bool(user.is_superuser)

        if is_superuser:
            used_day = await self.get_daily_analyze_tokens_used(user_id)
            used_month = await self.get_monthly_analyze_tokens_used(user_id)

            return {
                "allowed": True,
                "plan": "premium",
                "is_unlimited": True,
                "run_limit_tokens": ADMIN_UNLIMITED_SENTINEL,
                "monthly_limit_tokens": ADMIN_UNLIMITED_SENTINEL,
                "daily_plan_tokens": ADMIN_UNLIMITED_SENTINEL,
                "used_day_tokens": used_day,
                "used_month_tokens": used_month,
                "remaining_month_tokens": ADMIN_UNLIMITED_SENTINEL,
                "reason": None,
            }

        sub = await subscription_service.get_active_subscription(user_id)
        if not sub:
            return {
                "allowed": False,
                "plan": "none",
                "is_unlimited": False,
                "run_limit_tokens": 0,
                "monthly_limit_tokens": 0,
                "daily_plan_tokens": 0,
                "used_day_tokens": 0,
                "used_month_tokens": 0,
                "remaining_month_tokens": 0,
                "reason": "No active subscription",
            }

        plan = PlanTier(sub.plan)
        run_limit = int(PLAN_ANALYZE_RUN_TOKEN_LIMITS.get(plan, 0))
        monthly_limit = int(PLAN_ANALYZE_MONTHLY_TOKEN_LIMITS.get(plan, 0))
        daily_plan_tokens = monthly_limit // 30 if monthly_limit > 0 else 0

        used_day = await self.get_daily_analyze_tokens_used(user_id)
        used_month = await self.get_monthly_analyze_tokens_used(user_id)
        remaining = max(0, monthly_limit - used_month)
        is_unlimited = False

        await self._maybe_send_usage_warning_email(
            user_id=user_id,
            plan=plan.value,
            monthly_limit=monthly_limit,
            used_month=used_month,
        )

        if remaining <= 0:
            await self._maybe_send_limit_reached_email(
                user_id=user_id,
                plan=plan.value,
                monthly_limit=monthly_limit,
                used_month=used_month,
            )

        return {
            "allowed": is_unlimited or remaining > 0,
            "plan": plan.value,
            "is_unlimited": is_unlimited,
            "run_limit_tokens": run_limit,
            "monthly_limit_tokens": monthly_limit,
            "daily_plan_tokens": daily_plan_tokens if not is_unlimited else 999999999,
            "used_day_tokens": used_day,
            "used_month_tokens": used_month,
            "remaining_month_tokens": remaining if not is_unlimited else 999999999,
            "reason": None if (is_unlimited or remaining > 0) else f"Monthly analyze token budget exhausted ({monthly_limit:,})",
        }

    async def get_daily_analyze_tokens_used(self, user_id: str) -> int:
        now = datetime.now(timezone.utc)
        day_start = datetime(now.year, now.month, now.day, tzinfo=timezone.utc)

        from app.models.ai_usage import AIUsageLog
        async with get_db_context() as db:
            try:
                result = await db.execute(
                    select(func.coalesce(func.sum(AIUsageLog.total_tokens), 0))
                    .where(
                        AIUsageLog.user_id == user_id,
                        AIUsageLog.created_at >= day_start,
                        AIUsageLog.success == True
                    )
                )
                return int(result.scalar() or 0)
            except Exception:
                await db.rollback()
                return 0

    async def get_monthly_analyze_tokens_used(self, user_id: str) -> int:
        now = datetime.now(timezone.utc)
        month_start = datetime(now.year, now.month, 1, tzinfo=timezone.utc)

        from app.models.ai_usage import AIUsageLog
        async with get_db_context() as db:
            try:
                result = await db.execute(
                    select(func.coalesce(func.sum(AIUsageLog.total_tokens), 0))
                    .where(
                        AIUsageLog.user_id == user_id,
                        AIUsageLog.created_at >= month_start,
                        AIUsageLog.success == True
                    )
                )
                return int(result.scalar() or 0)
            except Exception:
                await db.rollback()
                return 0


analyze_budget_service = AnalyzeBudgetService()
