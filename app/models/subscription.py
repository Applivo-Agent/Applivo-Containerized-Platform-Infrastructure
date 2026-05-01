"""
app/models/subscription.py
──────────────────────────
Subscription and Payment models for the SaaS billing system.
Supports Starter, Pro, and Premium tiers with Razorpay integration.
"""

from __future__ import annotations

import enum
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import (
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import TimestampMixin, UUIDMixin


class PlanTier(str, enum.Enum):
    STARTER = "STARTER"
    PRO = "PRO"
    PREMIUM = "PREMIUM"


class SubscriptionStatus(str, enum.Enum):
    ACTIVE = "ACTIVE"
    EXPIRED = "EXPIRED"
    CANCELLED = "CANCELLED"
    PENDING = "PENDING"


class PaymentStatus(str, enum.Enum):
    CREATED = "CREATED"
    AUTHORIZED = "AUTHORIZED"
    CAPTURED = "CAPTURED"
    REFUNDED = "REFUNDED"
    FAILED = "FAILED"


# All amounts stored in paise (1 INR = 100 paise)
PLAN_PRICES = {
    PlanTier.STARTER: 19900,      # ₹199
    PlanTier.PRO: 39900,           # ₹399
    PlanTier.PREMIUM: 59900,       # ₹599
}

PLAN_DAILY_LIMITS = {
    PlanTier.STARTER: 50,
    PlanTier.PRO: 100,
    PlanTier.PREMIUM: 150,
}

PLAN_MONTHLY_AI_CREDITS = {
    PlanTier.STARTER: 50,    # 50 AI chat messages/month
    PlanTier.PRO: 100,       # 100 AI chat messages/month
    PlanTier.PREMIUM: 150,   # 150 AI chat messages/month
}

# Analyze token budgets (job analysis pipeline)
PLAN_ANALYZE_RUN_TOKEN_LIMITS = {
    PlanTier.STARTER: 25000,
    PlanTier.PRO: 60000,
    PlanTier.PREMIUM: 120000,
}

PLAN_ANALYZE_MONTHLY_TOKEN_LIMITS = {
    PlanTier.STARTER: 120000,
    PlanTier.PRO: 600000,
    PlanTier.PREMIUM: 1200000,
}

PLAN_PRIORITY = {
    PlanTier.STARTER: 1,
    PlanTier.PRO: 2,
    PlanTier.PREMIUM: 3,
}


class Subscription(Base, UUIDMixin, TimestampMixin):
    """
    User subscription record.
    Each user has one active subscription at a time.
    """
    __tablename__ = "subscriptions"

    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id"),
        nullable=False, index=True,
    )

    plan: Mapped[PlanTier] = mapped_column(
        Enum(PlanTier, name="plantier", values_callable=lambda obj: [e.value for e in obj]),
        nullable=False,
    )
    status: Mapped[SubscriptionStatus] = mapped_column(
        Enum(SubscriptionStatus, name="subscriptionstatus", values_callable=lambda obj: [e.value for e in obj]),
        default=SubscriptionStatus.PENDING,
        nullable=False,
        index=True,
    )

    start_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False,
    )
    end_date: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True,
    )

    # Razorpay subscription/order id for linking
    razorpay_subscription_id: Mapped[Optional[str]] = mapped_column(
        String(255), nullable=True,
    )

    # Relationship
    user: Mapped["User"] = relationship("User", back_populates="subscriptions")
    payments: Mapped[list["Payment"]] = relationship(
        "Payment", back_populates="subscription", cascade="all, delete-orphan",
    )

    @property
    def daily_limit(self) -> int:
        return PLAN_DAILY_LIMITS.get(PlanTier(self.plan), 50)

    @property
    def priority(self) -> int:
        return PLAN_PRIORITY.get(PlanTier(self.plan), 1)

    @property
    def ai_credits(self) -> int:
        return PLAN_MONTHLY_AI_CREDITS.get(PlanTier(self.plan), 0)

    @property
    def price(self) -> int:
        """Price in paise (1 INR = 100 paise)"""
        return PLAN_PRICES.get(PlanTier(self.plan), 20000)

    def is_active(self) -> bool:
        if self.status != SubscriptionStatus.ACTIVE:
            return False
        if self.end_date:
            end = self.end_date.replace(tzinfo=timezone.utc) if self.end_date.tzinfo is None else self.end_date
            if end < datetime.now(timezone.utc):
                return False
        return True

    def __repr__(self) -> str:
        return f"<Subscription {self.plan} [{self.status}] user={self.user_id}>"


class Payment(Base, UUIDMixin, TimestampMixin):
    """
    Payment record for Razorpay transactions.
    """
    __tablename__ = "payments"

    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id"),
        nullable=False, index=True,
    )
    subscription_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("subscriptions.id"),
        nullable=True, index=True,
    )

    amount: Mapped[int] = mapped_column(Integer, nullable=False)
    currency: Mapped[str] = mapped_column(String(10), default="INR", nullable=False)
    status: Mapped[PaymentStatus] = mapped_column(
        Enum(PaymentStatus, name="paymentstatus", values_callable=lambda obj: [e.value for e in obj]),
        default=PaymentStatus.CREATED,
        nullable=False,
    )

    # Razorpay identifiers
    razorpay_order_id: Mapped[Optional[str]] = mapped_column(
        String(255), nullable=True,
    )
    razorpay_payment_id: Mapped[Optional[str]] = mapped_column(
        String(255), nullable=True, index=True,
    )
    razorpay_signature: Mapped[Optional[str]] = mapped_column(
        String(500), nullable=True,
    )

    # Plan snapshot at payment time
    plan: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    # Relationship
    user: Mapped["User"] = relationship("User", back_populates="payments")
    subscription: Mapped[Optional["Subscription"]] = relationship(
        "Subscription", back_populates="payments",
    )

    def __repr__(self) -> str:
        return f"<Payment {self.amount} {self.currency} [{self.status}] user={self.user_id}>"
