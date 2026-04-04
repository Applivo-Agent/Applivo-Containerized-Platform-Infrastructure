"""
app/models/subscription.py
──────────────────────────
Subscription and Payment models for the SaaS billing system.
Supports Starter, Pro, and Premium tiers with Razorpay integration.
"""

from __future__ import annotations

import enum
from datetime import datetime
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
    STARTER = "starter"
    PRO = "pro"
    PREMIUM = "premium"


class SubscriptionStatus(str, enum.Enum):
    ACTIVE = "active"
    EXPIRED = "expired"
    CANCELLED = "cancelled"
    PENDING = "pending"


class PaymentStatus(str, enum.Enum):
    CREATED = "created"
    AUTHORIZED = "authorized"
    CAPTURED = "captured"
    REFUNDED = "refunded"
    FAILED = "failed"


PLAN_PRICES = {
    PlanTier.STARTER: 200,
    PlanTier.PRO: 400,
    PlanTier.PREMIUM: 800,
}

PLAN_DAILY_LIMITS = {
    PlanTier.STARTER: 150,
    PlanTier.PRO: 250,
    PlanTier.PREMIUM: 500,
}

PLAN_MONTHLY_AI_CREDITS = {
    PlanTier.STARTER: 100,    # 100 AI chat messages/month
    PlanTier.PRO: 500,        # 500 AI chat messages/month
    PlanTier.PREMIUM: 999999, # Unlimited for premium
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

    plan: Mapped[str] = mapped_column(
        Enum(PlanTier),
        nullable=False,
    )
    status: Mapped[str] = mapped_column(
        Enum(SubscriptionStatus),
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
        return PLAN_DAILY_LIMITS.get(PlanTier(self.plan), 150)

    @property
    def priority(self) -> int:
        return PLAN_PRIORITY.get(PlanTier(self.plan), 1)

    @property
    def ai_credits(self) -> int:
        return PLAN_MONTHLY_AI_CREDITS.get(PlanTier(self.plan), 0)

    @property
    def price(self) -> int:
        return PLAN_PRICES.get(PlanTier(self.plan), 200)

    def is_active(self) -> bool:
        if self.status != SubscriptionStatus.ACTIVE:
            return False
        if self.end_date and self.end_date < datetime.utcnow():
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
    status: Mapped[str] = mapped_column(
        Enum(PaymentStatus),
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
