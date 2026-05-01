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
import logging
from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel

from app.api.routes.auth import get_current_user
from app.models.user import User
from app.models.subscription import PlanTier
from app.services.payment_service import payment_service
from app.core.config import settings

logger = logging.getLogger(__name__)

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

    logger.info(f"Razorpay webhook received: {event_type}")

    if event_type == "payment.captured":
        razorpay_payment_id = payment_entity.get("id")
        razorpay_order_id = order_entity.get("id")

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

    elif event_type == "payment.failed":
        razorpay_order_id = order_entity.get("id")
        logger.warning(f"Payment failed for order: {razorpay_order_id}")

    return {"status": "ok"}
