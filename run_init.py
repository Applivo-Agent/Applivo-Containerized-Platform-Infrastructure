import asyncio
import sys
from app.core.database import init_db

async def main():
    print("Initializing database...")
    await init_db()
    print("Database initialized.")

if __name__ == "__main__":
    asyncio.run(main())
