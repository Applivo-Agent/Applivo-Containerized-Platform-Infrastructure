import asyncio
from sqlalchemy import select, func
from app.core.database import get_db_context
from app.models.job import Job, JobAnalysis
from app.models.resume import CoverLetter

async def check():
    async with get_db_context() as db:
        # Job Analysis
        ja_count = (await db.execute(select(func.count(JobAnalysis.id)))).scalar()
        ja_tokens = (await db.execute(select(func.sum(JobAnalysis.tokens_used)))).scalar() or 0
        
        # Cover Letters
        cl_count = (await db.execute(select(func.count(CoverLetter.id)))).scalar()
        cl_tokens = (await db.execute(select(func.sum(CoverLetter.tokens_used)))).scalar() or 0
        
        print(f"Job Analysis: {ja_count} records, {ja_tokens} total tokens")
        print(f"Cover Letters: {cl_count} records, {cl_tokens} total tokens")
        
        # Check if any Job has user_id
        jobs_with_user = (await db.execute(select(func.count(Job.id)).where(Job.user_id != None))).scalar()
        total_jobs = (await db.execute(select(func.count(Job.id)))).scalar()
        print(f"Jobs: {total_jobs} total, {jobs_with_user} with user_id")

if __name__ == "__main__":
    asyncio.run(check())
