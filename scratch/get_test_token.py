import asyncio
import jwt
from datetime import datetime, timezone, timedelta
from sqlalchemy import select
from app.core.database import get_db_context
from app.core.config import settings
from app.models.user import User

async def main():
    async with get_db_context() as db:
        user = (await db.execute(select(User).where(User.email == "dhruvxpnt@gmail.com"))).scalar_one()
        expire = datetime.now(timezone.utc) + timedelta(minutes=60)
        payload = {
            "sub": user.id,
            "email": user.email,
            "exp": expire,
            "iat": datetime.now(timezone.utc),
        }
        token = jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
        print(token)

if __name__ == "__main__":
    asyncio.run(main())
