import asyncio
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

engine = create_engine("postgresql://applivo:applivo_password@localhost:5432/applivo")
SessionLocal = sessionmaker(bind=engine)
db = SessionLocal()

result = db.execute("SELECT * FROM platform_settings WHERE user_id = '82adea84-d4dc-4bde-a16f-b24565c37ba5'")
for row in result:
    print(row)
