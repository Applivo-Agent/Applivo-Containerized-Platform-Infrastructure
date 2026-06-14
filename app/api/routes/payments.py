"""
app/api/routes/payments.py
────────────────────────────
Payment processing API routes with Razorpay integration.
Handles order creation, payment verification, and payment history.
"""

from __future__ import annotations

import hmac
import hashlib
import json
import structlog
from datetime import datetime, timezone, timedelta
from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel

from app.api.routes.auth import get_current_user
from app.models.user import User
from app.models.subscription import PlanTier, Subscription, SubscriptionStatus
from app.services.payment_service import payment_service
from app.core.config import settings

logger = structlog.get_logger()

router = APIRouter(prefix="/payments", tags=["Payments"])


class CreateOrderRequest(BaseModel):
    plan: str  # "starter", "pro", "premium"


class VerifyPaymentRequest(BaseModel):
    razorpay_order_id: str
    razorpay_payment_id: str
    razorpay_signature: str


@router.post("/create-order")
async def create_order(
    data: CreateOrderRequest,
    current_user: User = Depends(get_current_user),
):
    """Create a Razorpay payment order for the selected plan."""
    try:
        plan = PlanTier(data.plan.upper())
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid plan: {data.plan}. Must be one of: starter, pro, premium",
        )

    try:
        order = await payment_service.create_order(
            user_id=current_user.id,
            plan=plan,
        )
        return order
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.post("/verify")
async def verify_payment(
    data: VerifyPaymentRequest,
    current_user: User = Depends(get_current_user),
):
    """
    Verify Razorpay payment and activate subscription.
    Called by the frontend after Razorpay checkout completes.
    """
    try:
        result = await payment_service.verify_payment(
            razorpay_order_id=data.razorpay_order_id,
            razorpay_payment_id=data.razorpay_payment_id,
            razorpay_signature=data.razorpay_signature,
        )
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.get("/history")
async def payment_history(
    current_user: User = Depends(get_current_user),
):
    """Get payment history for the current user."""
    history = await payment_service.get_payment_history(current_user.id)
    return {"payments": history}


@router.get("/autopay-manage-url")
async def get_autopay_manage_url(
    current_user: User = Depends(get_current_user),
):
    """
    Return Razorpay short_url for completing card setup or managing autopay.
    Frontend redirects the user to short_url when present.
    """
    try:
        return await payment_service.get_autopay_manage_url(current_user.id)
    except RuntimeError as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(e),
        )


@router.post("/cancel-autopay")
async def cancel_autopay(
    current_user: User = Depends(get_current_user),
):
    """Cancel Razorpay recurring billing and the local subscription."""
    try:
        return await payment_service.cancel_autopay_for_user(current_user.id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except RuntimeError as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(e),
        )


class StartTrialWithAutoPayRequest(BaseModel):
    plan: str  # "starter"


@router.post("/start-trial-with-autopay")
async def start_trial_with_autopay(
    data: StartTrialWithAutoPayRequest,
    current_user: User = Depends(get_current_user),
):
    """
    Start a trial subscription with automatic payment collection after trial ends.
    User saves their card and is charged after 7 days.
    """
    try:
        plan = PlanTier(data.plan.upper())
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid plan: {data.plan}. Currently only 'starter' trial is available.",
        )

    # Only Starter plan has trial
    if plan != PlanTier.STARTER:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only Starter plan offers a free trial.",
        )

    try:
        from app.core.database import get_db_context
        from sqlalchemy import select

        # Check if user already has active subscription or trial
        async with get_db_context() as db:
            result = await db.execute(
                select(Subscription).where(
                    Subscription.user_id == current_user.id,
                    Subscription.status.in_([
                        SubscriptionStatus.ACTIVE,
                        SubscriptionStatus.SUCCESS,
                        SubscriptionStatus.TRIAL,
                        SubscriptionStatus.PENDING,
                    ])
                )
            )
            existing = result.scalar_one_or_none()
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="User already has an active subscription or trial.",
                )

        # Create Razorpay subscription with autopay
        result = await payment_service.create_razorpay_subscription(
            user_id=current_user.id,
            plan=plan,
            charge_after_days=7,
            customer_email=current_user.email,
            customer_name=current_user.full_name,
        )
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "Failed to start trial with autopay",
            error=str(e),
            user_id=current_user.id,
            exc_info=True,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start trial: {str(e)}",
        )


@router.post("/webhook")
async def razorpay_webhook(request: Request):
    """
    Handle Razorpay webhook events for server-side payment verification.
    This ensures subscriptions are activated even if the browser crashes after payment.
    """
    if not settings.RAZORPAY_WEBHOOK_SECRET:
        logger.warning("RAZORPAY_WEBHOOK_SECRET not configured - ignoring webhook")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Webhook not configured",
        )

    body = await request.body()
    signature = request.headers.get("X-Razorpay-Signature", "")

    # Verify webhook signature
    expected_signature = hmac.new(
        settings.RAZORPAY_WEBHOOK_SECRET.encode(),
        body,
        hashlib.sha256,
    ).hexdigest()

    if not hmac.compare_digest(signature, expected_signature):
        logger.warning("Invalid Razorpay webhook signature")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid signature",
        )

    try:
        event = json.loads(body)
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid JSON",
        )

    event_type = event.get("event")
    payload = event.get("payload", {})
    payment_entity = payload.get("payment", {})
    order_entity = payload.get("order", {})
    subscription_entity = payload.get("subscription", {})

    logger.info(f"Razorpay webhook received: {event_type}")

    if event_type == "subscription.authenticated":
        # User saved their card and paid ₹5 auth charge. Trial has officially started.
        sub_data = subscription_entity.get("entity", subscription_entity)
        razorpay_subscription_id = sub_data.get("id")

        logger.info(f"Processing subscription authentication: {razorpay_subscription_id}")

        if razorpay_subscription_id:
            try:
                from app.core.database import get_db_context
                from sqlalchemy import select
                from app.models.subscription import Subscription, SubscriptionStatus
                from app.services.notification_service import NotificationService
                from app.models.user import User

                async with get_db_context() as db:
                    result = await db.execute(
                        select(Subscription).where(
                            Subscription.razorpay_subscription_id == razorpay_subscription_id
                        )
                    )
                    sub = result.scalar_one_or_none()
                    if sub:
                        sub.status = SubscriptionStatus.TRIAL
                        sub.is_trial = True
                        # trial_end_date is already set in create_razorpay_subscription
                        await db.commit()

                        # Send "Trial Started" email notification
                        try:
                            user_result = await db.execute(select(User).where(User.id == sub.user_id))
                            user = user_result.scalar_one_or_none()
                            if user:
                                trial_end_str = sub.trial_end_date.strftime('%B %d, %Y') if sub.trial_end_date else 'in 7 days'
                                from app.services import email_service
                                await email_service.send_trial_started(
                                    user.email,
                                    user.full_name or user.email,
                                    trial_end_str,
                                )
                                await NotificationService().notify(
                                    title="Your 7-Day Free Trial Has Started!",
                                    body=f"Trial active until {trial_end_str}. Your agent is running.",
                                    event_type="trial_started",
                                    data={"plan": sub.plan.value, "trial_end_date": sub.trial_end_date.isoformat() if sub.trial_end_date else None},
                                    user_id=sub.user_id,
                                )
                        except Exception as ne:
                            logger.warning("Failed to send trial started notification", error=str(ne))

                        logger.info(f"Subscription authenticated: {razorpay_subscription_id}")
            except Exception as e:
                logger.error(f"Failed to handle subscription authentication: {e}")

    elif event_type == "payment.captured":
        # Extract from nested 'entity' if present, otherwise direct
        p_data = payment_entity.get("entity", payment_entity)
        o_data = order_entity.get("entity", order_entity)

        razorpay_payment_id = p_data.get("id")
        # Try to get order_id from payment entity first (more reliable)
        razorpay_order_id = p_data.get("order_id") or o_data.get("id")

        logger.info(f"Processing captured payment: {razorpay_payment_id} for order: {razorpay_order_id}")

        if razorpay_payment_id and razorpay_order_id:
            try:
                await payment_service.activate_from_webhook(
                    razorpay_order_id=razorpay_order_id,
                    razorpay_payment_id=razorpay_payment_id,
                )
                logger.info(f"Subscription activated via webhook: {razorpay_order_id}")
            except Exception as e:
                logger.error(f"Failed to activate subscription from webhook: {e}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to activate subscription",
                )

    elif event_type == "subscription.charged":
        # Razorpay charged the saved card for recurring billing
        sub_data = subscription_entity.get("entity", subscription_entity)
        razorpay_subscription_id = sub_data.get("id")

        logger.info(f"Processing subscription charge: {razorpay_subscription_id}")

        if razorpay_subscription_id:
            try:
                from app.core.database import get_db_context
                from sqlalchemy import select
                from app.models.subscription import Subscription, SubscriptionStatus
                from app.services.notification_service import NotificationService

                async with get_db_context() as db:
                    result = await db.execute(
                        select(Subscription).where(
                            Subscription.razorpay_subscription_id == razorpay_subscription_id
                        )
                    )
                    sub = result.scalar_one_or_none()
                    if sub:
                        sub.status = SubscriptionStatus.ACTIVE
                        sub.start_date = datetime.now(timezone.utc)
                        sub.end_date = datetime.now(timezone.utc) + timedelta(days=30)
                        await db.commit()

                        # Send notification
                        try:
                            from app.models.user import User
                            user_result = await db.execute(select(User).where(User.id == sub.user_id))
                            user = user_result.scalar_one_or_none()
                            if user:
                                try:
                                    from app.services import email_service as es
                                    await es.send_subscription_activated(
                                        user.email,
                                        user.full_name or user.email,
                                        sub.plan.value.capitalize(),
                                        "Auto-billed",
                                        sub.end_date.strftime('%B %d, %Y'),
                                    )
                                except Exception:
                                    pass
                                await NotificationService().notify(
                                    title="Payment Successful - Subscription Active",
                                    body=f"Your {sub.plan.value} plan is now active until {sub.end_date.strftime('%B %d, %Y')}.",
                                    event_type="subscription_charged",
                                    data={"plan": sub.plan.value},
                                    user_id=sub.user_id,
                                )
                        except Exception as ne:
                            logger.warning("Failed to send subscription success notification", error=str(ne))

                        logger.info(f"Subscription activated via charge: {razorpay_subscription_id}")
            except Exception as e:
                logger.error(f"Failed to handle subscription charge: {e}")

    elif event_type == "subscription.halted":
        # Payment failed for recurring billing
        sub_data = subscription_entity.get("entity", subscription_entity)
        razorpay_subscription_id = sub_data.get("id")

        logger.warning(f"Subscription halted (payment failed): {razorpay_subscription_id}")

        if razorpay_subscription_id:
            try:
                from app.core.database import get_db_context
                from sqlalchemy import select
                from app.models.subscription import Subscription, SubscriptionStatus
                from app.models.user import User
                from app.services.notification_service import NotificationService

                async with get_db_context() as db:
                    result = await db.execute(
                        select(Subscription).where(
                            Subscription.razorpay_subscription_id == razorpay_subscription_id
                        )
                    )
                    sub = result.scalar_one_or_none()
                    if sub:
                        sub.status = SubscriptionStatus.TRIAL_EXPIRED
                        await db.commit()

                        # Disable auto-apply
                        try:
                            from app.models.user import UserProfile
                            profile_result = await db.execute(
                                select(UserProfile).where(UserProfile.user_id == sub.user_id)
                            )
                            profile = profile_result.scalar_one_or_none()
                            if profile:
                                profile.auto_apply_enabled = False
                                await db.commit()
                        except Exception as pe:
                            logger.warning("Failed to disable auto-apply after subscription halt", error=str(pe))

                        # Send notification
                        try:
                            user_result = await db.execute(select(User).where(User.id == sub.user_id))
                            user = user_result.scalar_one_or_none()
                            if user:
                                try:
                                    from app.services import email_service as es
                                    await es.send_payment_failed(
                                        user.email,
                                        user.full_name or user.email,
                                        sub.plan.value.capitalize(),
                                        "72 hours",
                                    )
                                except Exception:
                                    pass
                                await NotificationService().notify(
                                    title="Payment Failed - Please Update Your Card",
                                    body=f"Your payment for the {sub.plan.value} plan failed. Update your payment method to continue.",
                                    event_type="subscription_halted",
                                    data={"plan": sub.plan.value},
                                    user_id=sub.user_id,
                                )
                        except Exception as ne:
                            logger.warning("Failed to send subscription halted notification", error=str(ne))

                        logger.info(f"Subscription halted: {razorpay_subscription_id}")
            except Exception as e:
                logger.error(f"Failed to handle subscription halt: {e}")

    elif event_type == "payment.failed":
        razorpay_order_id = order_entity.get("id")
        logger.warning(f"Payment failed for order: {razorpay_order_id}")

    return {"status": "ok"}
