import asyncio
from sqlalchemy import select
from app.core.database import get_db_context
from app.models.user import User

async def list_users():
    async with get_db_context() as db:
        result = await db.execute(select(User))
        users = result.scalars().all()
        print(f"Total users: {len(users)}")
        for u in users:
            print(f"- {u.email} (Verified: {u.is_verified}, Active: {u.is_active})")

if __name__ == "__main__":
    asyncio.run(list_users())
