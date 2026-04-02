"""
app/api/routes/payments.py
──────────────────────────
Payment processing API routes with Razorpay integration.
Handles order creation, payment verification, and payment history.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from app.api.routes.auth import get_current_user
from app.models.user import User
from app.models.subscription import PlanTier
from app.services.payment_service import payment_service

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
        plan = PlanTier(data.plan)
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
