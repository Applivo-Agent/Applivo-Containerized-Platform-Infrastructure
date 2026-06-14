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
from datetime import datetime, timezone, timedelta
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
    Subscription,
    SubscriptionStatus,
    PLAN_PRICES,
)
from app.services.subscription_service import subscription_service

logger = structlog.get_logger()


class PaymentService:
    """Razorpay payment processing service."""

    # Cache for Razorpay plan IDs to avoid creating duplicates
    _plan_cache: dict[PlanTier, str] = {}

    @property
    def _razorpay_auth(self) -> tuple[str, str]:
        return (settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)

    @property
    def _base_url(self) -> str:
        return "https://api.razorpay.com/v1"

    async def create_razorpay_plan(self, plan: PlanTier) -> str:
        """
        Create or retrieve a Razorpay Plan for monthly recurring billing.
        Caches plan_ids to avoid creating duplicates.
        Returns the razorpay plan_id.
        """
        # Check cache first
        if plan in self._plan_cache:
            logger.info("Using cached Razorpay plan", plan=plan.value, plan_id=self._plan_cache[plan])
            return self._plan_cache[plan]

        try:
            plan_payload = {
                "period": "monthly",
                "interval": 1,
                "item": {
                    "name": f"Applivo {plan.value} Plan",
                    "description": f"Monthly subscription for {plan.value} plan",
                    "amount": PLAN_PRICES[plan],
                    "currency": "INR",
                }
            }

            async with httpx.AsyncClient(timeout=30) as client:
                response = await client.post(
                    f"{self._base_url}/plans",
                    auth=self._razorpay_auth,
                    json=plan_payload,
                )
                response.raise_for_status()
                plan_data = response.json()

            plan_id = plan_data["id"]
            self._plan_cache[plan] = plan_id
            logger.info("Razorpay plan created", plan=plan.value, plan_id=plan_id)
            return plan_id

        except httpx.HTTPStatusError as e:
            logger.error("Razorpay plan creation failed", error=str(e), status=e.response.status_code)
            raise RuntimeError(f"Failed to create Razorpay plan: {e.response.text}")
        except Exception as e:
            logger.error("Razorpay plan creation failed", error=str(e))
            raise RuntimeError(f"Failed to create Razorpay plan: {str(e)}")

    async def create_razorpay_subscription(
        self,
        user_id: str,
        plan: PlanTier,
        charge_after_days: int = 7,
        customer_email: Optional[str] = None,
        customer_name: Optional[str] = None,
    ) -> dict:
        """
        Create a Razorpay Subscription that starts billing after trial ends.
        User saves card during checkout but is not charged until start_at.
        Returns the subscription response with short_url for frontend.
        """
        try:
            # Get or create Razorpay plan
            razorpay_plan_id = await self.create_razorpay_plan(plan)

            # Calculate when to start billing (after trial period)
            start_timestamp = int((datetime.now(timezone.utc) + timedelta(days=charge_after_days)).timestamp())

            subscription_payload = {
                "plan_id": razorpay_plan_id,
                "total_count": 12,
                "quantity": 1,
                "start_at": start_timestamp,
                "customer_notify": 1,
                "notes": {
                    "user_id": user_id,
                    "plan": plan.value,
                    "trial_days": charge_after_days,
                }
            }

            if customer_email:
                subscription_payload["customer_email"] = customer_email
            if customer_name:
                subscription_payload["customer_name"] = customer_name

            async with httpx.AsyncClient(timeout=30) as client:
                response = await client.post(
                    f"{self._base_url}/subscriptions",
                    auth=self._razorpay_auth,
                    json=subscription_payload,
                )
                response.raise_for_status()
                subscription_data = response.json()

            # Store the subscription in our database
            async with get_db_context() as db:
                sub = Subscription(
                    user_id=user_id,
                    plan=plan,
                    status=SubscriptionStatus.PENDING,
                    is_trial=False,
                    start_date=datetime.now(timezone.utc),
                    end_date=datetime.now(timezone.utc) + timedelta(days=charge_after_days),
                    trial_end_date=datetime.now(timezone.utc) + timedelta(days=charge_after_days),
                    razorpay_subscription_id=subscription_data["id"],
                )
                db.add(sub)
                await db.commit()
                await db.refresh(sub)

            logger.info(
                "Razorpay subscription created",
                plan=plan.value,
                user_id=user_id,
                subscription_id=subscription_data["id"],
                start_at=start_timestamp,
            )

            return {
                "subscription_id": subscription_data["id"],
                "short_url": subscription_data.get("short_url", ""),
                "user_id": user_id,
                "plan": plan.value,
                "trial_days": charge_after_days,
            }

        except httpx.HTTPStatusError as e:
            logger.error("Razorpay subscription creation failed", error=str(e), status=e.response.status_code)
            raise RuntimeError(f"Failed to create Razorpay subscription: {e.response.text}")
        except Exception as e:
            logger.error("Razorpay subscription creation failed", error=str(e))
            raise RuntimeError(f"Failed to create Razorpay subscription: {str(e)}")

    async def cancel_razorpay_subscription(self, razorpay_subscription_id: str) -> dict:
        """Cancel a Razorpay subscription immediately."""
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(
                f"{self._base_url}/subscriptions/{razorpay_subscription_id}/cancel",
                auth=self._razorpay_auth,
                json={"cancel_at_cycle_end": 0},
            )
            response.raise_for_status()
            return response.json()

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
                "amount": amount,  # Already in paise
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

            payment.subscription_id = sub.id
            await db.commit()

            # Generate Invoice PDF
            invoice_path = None
            try:
                from app.services.invoice_service import invoice_service
                from app.models.user import User
                user_res = await db.execute(select(User).where(User.id == payment.user_id))
                user_obj = user_res.scalar_one_or_none()
                
                invoice_path = await invoice_service.generate_invoice(
                    payment_id=payment.id,
                    order_id=payment.razorpay_order_id,
                    razorpay_payment_id=payment.razorpay_payment_id,
                    full_name=user_obj.full_name if user_obj else "Valued Customer",
                    email=user_obj.email if user_obj else "customer@example.com",
                    user_id=payment.user_id,
                    amount=payment.amount,
                    plan_name=plan.value
                )
            except Exception as ie:
                logger.error("Failed to generate invoice for payment email", error=str(ie))

            # Send payment success notification with invoice
            try:
                from app.services.notification_service import NotificationService
                await NotificationService().notify(
                    title="🎉 Payment Successful - You're All Set!",
                    body=f"""Congratulations! Your {plan.value.upper()} plan has been activated.

What's included:
• Unlimited job searches and applications
• AI-powered resume tailoring
• Auto-apply to matching opportunities
• Interview preparation materials
• Priority support

Your subscription is valid until {sub.end_date.strftime('%B %d, %Y') if sub.end_date else '30 days from now'}.

Need help? Reply to this email or visit your dashboard.

Welcome to Applivo — let's find your dream job!

— Team Applivo""",
                    event_type="payment_success",
                    data={"plan": plan.value, "amount": payment.amount},
                    user_id=payment.user_id,
                    attachment_path=invoice_path
                )
            except Exception as e:
                logger.warning("Failed to send payment notification", error=str(e))

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
                "payment_id": payment.id,
                "razorpay_payment_id": payment.razorpay_payment_id,
                "razorpay_order_id": payment.razorpay_order_id,
                "transaction_id": payment.razorpay_payment_id or payment.razorpay_order_id or payment.id,
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
                    "razorpay_order_id": p.razorpay_order_id,
                    "razorpay_payment_id": p.razorpay_payment_id,
                    "transaction_id": p.razorpay_payment_id or p.razorpay_order_id or p.id,
                    "created_at": p.created_at.isoformat(),
                }
                for p in payments
            ]

    async def activate_from_webhook(
        self,
        razorpay_order_id: str,
        razorpay_payment_id: str,
    ) -> dict:
        """
        Activate subscription from webhook without signature verification.
        Called by Razorpay webhook when payment is captured server-to-server.
        """
        async with get_db_context() as db:
            result = await db.execute(
                select(Payment).where(Payment.razorpay_order_id == razorpay_order_id)
            )
            payment = result.scalar_one_or_none()
            if not payment:
                raise ValueError(f"Payment not found for order: {razorpay_order_id}")

            if payment.status == PaymentStatus.CAPTURED:
                logger.info("Payment already captured", order_id=razorpay_order_id)
                return {"status": "already_captured"}

            payment.razorpay_payment_id = razorpay_payment_id
            payment.status = PaymentStatus.CAPTURED
            await db.commit()

            plan = PlanTier(payment.plan) if payment.plan else PlanTier.STARTER
            sub = await subscription_service.create_subscription(
                user_id=payment.user_id,
                plan=plan,
                duration_days=30,
            )

            payment.subscription_id = sub.id
            await db.commit()

            logger.info(
                "Subscription activated from webhook",
                user_id=payment.user_id,
                plan=plan.value,
                payment_id=payment.id,
                sub_id=sub.id,
            )

            return {
                "status": "success",
                "plan": plan.value,
                "subscription_id": sub.id,
            }


payment_service = PaymentService()
