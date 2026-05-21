
import asyncio
from sqlalchemy import select
from app.core.database import get_db_context
from app.models.subscription import Payment, Subscription, PlanTier, SubscriptionStatus
from app.models.user import User
from datetime import datetime, timezone, timedelta

async def fix_user():
    import os
    # Temporarily override DATABASE_URL to use 127.0.0.1
    db_url = os.environ.get("DATABASE_URL", "postgresql+asyncpg://applivo:change_me_in_prod@127.0.0.1:5432/applivo")
    if "@database" in db_url:
        db_url = db_url.replace("@database", "@127.0.0.1")
    os.environ["DATABASE_URL"] = db_url
    
    payment_id = "pay_SkTL8uRqIQeLFd"
    async with get_db_context() as db:
        # Find payment
        result = await db.execute(select(Payment).where(Payment.razorpay_payment_id == payment_id))
        payment = result.scalar_one_or_none()
        
        if not payment:
            print(f"Payment {payment_id} not found by razorpay_payment_id. Checking razorpay_order_id...")
            result = await db.execute(select(Payment).where(Payment.razorpay_order_id == "order_SkRWSV6qNpyUyl")) # Looking at previous logs for order ID if needed
            payment = result.scalar_one_or_none()
            
        if not payment:
            print("Payment not found. Searching for 'B. Ravi Shankar'...")
            result = await db.execute(select(User).where(User.full_name.ilike("%Ravi Shankar%")))
            user = result.scalar_one_or_none()
        else:
            user_res = await db.execute(select(User).where(User.id == payment.user_id))
            user = user_res.scalar_one_or_none()

        if not user:
            print("User not found.")
            return

        print(f"Found User: {user.full_name} ({user.id})")
        
        # Check current subscription
        result = await db.execute(
            select(Subscription).where(Subscription.user_id == user.id)
        )
        subs = result.scalars().all()
        print(f"User has {len(subs)} subscriptions.")
        for s in subs:
            print(f" - ID: {s.id}, Plan: {s.plan}, Status: {s.status}")

        # Activate STARTER plan
        now = datetime.now(timezone.utc)
        new_sub = Subscription(
            user_id=user.id,
            plan=PlanTier.STARTER,
            status=SubscriptionStatus.ACTIVE,
            start_date=now,
            end_date=now + timedelta(days=30),
            razorpay_payment_id=payment_id if payment else None
        )
        db.add(new_sub)
        
        if payment:
            payment.status = "captured"
            payment.subscription_id = new_sub.id
            
        await db.commit()
        print(f"Successfully activated STARTER plan for {user.full_name}")

if __name__ == "__main__":
    asyncio.run(fix_user())
