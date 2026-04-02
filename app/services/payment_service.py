"""
app/services/payment_service.py
────────────────────────────────
Razorpay payment integration for subscription billing.
Handles order creation, payment verification, and subscription activation.
"""

from __future__ import annotations

import hashlib
import hmac
import json
from datetime import datetime, timezone
from typing import Optional

import httpx
import structlog
from sqlalchemy import select

from app.core.config import settings
from app.core.database import get_db_context
from app.models.subscription import (
    Payment,
    PaymentStatus,
    PlanTier,
    PLAN_PRICES,
)
from app.services.subscription_service import subscription_service

logger = structlog.get_logger()


class PaymentService:
    """Razorpay payment processing service."""

    @property
    def _razorpay_auth(self) -> tuple[str, str]:
        return (settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)

    @property
    def _base_url(self) -> str:
        return "https://api.razorpay.com/v1"

    async def create_order(
        self,
        user_id: str,
        plan: PlanTier,
    ) -> dict:
        """
        Create a Razorpay order for the given plan.
        Returns the order details needed by the frontend to open Razorpay checkout.
        """
        amount = PLAN_PRICES.get(plan, 200)
        if amount <= 0:
            raise ValueError(f"Invalid plan price: {plan}")

        async with get_db_context() as db:
            # Create payment record
            payment = Payment(
                user_id=user_id,
                amount=amount,
                currency="INR",
                status=PaymentStatus.CREATED,
                plan=plan.value,
            )
            db.add(payment)
            await db.flush()

            # Create Razorpay order
            order_payload = {
                "amount": amount * 100,  # Razorpay uses paise
                "currency": "INR",
                "receipt": payment.id,
                "notes": {
                    "user_id": user_id,
                    "plan": plan.value,
                    "payment_id": payment.id,
                },
            }

            try:
                async with httpx.AsyncClient(timeout=30) as client:
                    response = await client.post(
                        f"{self._base_url}/orders",
                        auth=self._razorpay_auth,
                        json=order_payload,
                    )
                    response.raise_for_status()
                    order_data = response.json()

                payment.razorpay_order_id = order_data["id"]
                await db.commit()

                logger.info(
                    "Razorpay order created",
                    order_id=order_data["id"],
                    user_id=user_id,
                    plan=plan.value,
                    amount=amount,
                )

                return {
                    "order_id": order_data["id"],
                    "amount": amount,
                    "currency": "INR",
                    "payment_id": payment.id,
                    "key_id": settings.RAZORPAY_KEY_ID,
                }

            except httpx.HTTPStatusError as e:
                logger.error("Razorpay order creation failed", error=str(e), status=e.response.status_code)
                raise RuntimeError(f"Payment order creation failed: {e.response.text}")
            except Exception as e:
                logger.error("Razorpay order creation failed", error=str(e))
                raise RuntimeError(f"Payment order creation failed: {str(e)}")

    async def verify_payment(
        self,
        razorpay_order_id: str,
        razorpay_payment_id: str,
        razorpay_signature: str,
    ) -> dict:
        """
        Verify Razorpay payment signature and activate subscription.
        Returns the subscription details on success.
        """
        # Verify signature
        expected_signature = hmac.new(
            settings.RAZORPAY_KEY_SECRET.encode("utf-8"),
            f"{razorpay_order_id}|{razorpay_payment_id}".encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()

        if not hmac.compare_digest(expected_signature, razorpay_signature):
            logger.error("Payment signature verification failed", order_id=razorpay_order_id)
            raise ValueError("Payment signature verification failed")

        async with get_db_context() as db:
            # Find the payment record
            result = await db.execute(
                select(Payment).where(Payment.razorpay_order_id == razorpay_order_id)
            )
            payment = result.scalar_one_or_none()
            if not payment:
                raise ValueError(f"Payment not found for order: {razorpay_order_id}")

            # Update payment
            payment.razorpay_payment_id = razorpay_payment_id
            payment.razorpay_signature = razorpay_signature
            payment.status = PaymentStatus.CAPTURED
            await db.commit()

            # Activate subscription
            plan = PlanTier(payment.plan) if payment.plan else PlanTier.STARTER
            sub = await subscription_service.create_subscription(
                user_id=payment.user_id,
                plan=plan,
                duration_days=30,
            )

            # Link payment to subscription
            payment.subscription_id = sub.id
            await db.commit()

            logger.info(
                "Payment verified and subscription activated",
                user_id=payment.user_id,
                plan=plan.value,
                payment_id=payment.id,
                sub_id=sub.id,
            )

            return {
                "status": "success",
                "plan": plan.value,
                "subscription_id": sub.id,
                "start_date": sub.start_date.isoformat(),
                "end_date": sub.end_date.isoformat() if sub.end_date else None,
            }

    async def get_payment_history(self, user_id: str, limit: int = 20) -> list[dict]:
        """Get payment history for a user."""
        async with get_db_context() as db:
            result = await db.execute(
                select(Payment)
                .where(Payment.user_id == user_id)
                .order_by(Payment.created_at.desc())
                .limit(limit)
            )
            payments = result.scalars().all()
            return [
                {
                    "id": p.id,
                    "amount": p.amount,
                    "currency": p.currency,
                    "status": p.status.value if hasattr(p.status, "value") else p.status,
                    "plan": p.plan,
                    "razorpay_payment_id": p.razorpay_payment_id,
                    "created_at": p.created_at.isoformat(),
                }
                for p in payments
            ]


payment_service = PaymentService()
