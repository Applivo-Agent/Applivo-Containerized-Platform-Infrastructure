import asyncio
from sqlalchemy import select, update
from app.core.database import get_db_context
from app.models.user import User
from app.core.security import get_password_hash

async def reset_password(email: str, new_password: str):
    async with get_db_context() as db:
        result = await db.execute(select(User).where(User.email == email))
        user = result.scalar_one_or_none()
        
        if not user:
            print(f"User {email} not found!")
            return
        
        hashed = get_password_hash(new_password)
        await db.execute(
            update(User)
            .where(User.id == user.id)
            .values(hashed_password=hashed)
        )
        print(f"Password reset successful for {email}")
        print(f"New password: {new_password}")

if __name__ == "__main__":
    email = "applivoagent@gmail.com"
    password = "Applivo@2025"
    asyncio.run(reset_password(email, password))
