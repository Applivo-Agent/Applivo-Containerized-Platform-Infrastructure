"""
app/services/market_service.py
────────────────────────────────
Module 22: Job Market Intelligence
Aggregates scraped job data into market snapshots.
Detects trending skills, top hiring companies, salary trends.
"""

from __future__ import annotations

from collections import Counter
from datetime import datetime, timezone, timedelta
from typing import List

import structlog
from sqlalchemy import select, func

from app.core.database import get_db_context
from app.models.job import Job, JobAnalysis
from app.models.interview import MarketSnapshot, SkillGap
from app.models.user import User

logger = structlog.get_logger()


class MarketIntelligenceService:

    async def take_snapshot(self) -> dict:
        """Aggregate current job data into a market snapshot."""
        async with get_db_context() as db:
            # Get all recent jobs with analysis (last 30 days)
            cutoff = datetime.now(timezone.utc) - timedelta(days=30)

            result = await db.execute(
                select(Job, JobAnalysis)
                .join(JobAnalysis, Job.id == JobAnalysis.job_id)
                .where(Job.scraped_at >= cutoff, Job.is_active == True)
            )
            rows = result.all()

            if not rows:
                logger.info("No jobs to snapshot")
                return {"snapshot": False, "reason": "No data"}

            # Aggregate skills
            all_required = []
            all_preferred = []
            companies = []
            roles = []
            salaries_min = []
            salaries_max = []
            by_source = Counter()
            by_work_mode = Counter()

            for job, analysis in rows:
                all_required.extend(analysis.required_skills)
                all_preferred.extend(analysis.preferred_skills)
                companies.append(job.company_name)
                roles.append(analysis.role_category or "other")
                by_source[job.source] += 1
                by_work_mode[job.work_mode] += 1
                if job.salary_min:
                    salaries_min.append(job.salary_min)
                if job.salary_max:
                    salaries_max.append(job.salary_max)

            # Top skills
            skill_counts = Counter(all_required + all_preferred)
            total_jobs = len(rows)
            top_skills = [
                {
                    "skill": skill,
                    "count": count,
                    "percentage": round(count / total_jobs * 100, 1)
                }
                for skill, count in skill_counts.most_common(20)
            ]

            # Top companies
            company_counts = Counter(companies)
            top_companies = [
                {"company": c, "openings": n}
                for c, n in company_counts.most_common(10)
            ]

            # Emerging roles
            role_counts = Counter(roles)
            emerging_roles = [r for r, _ in role_counts.most_common(5)]

            # Salary data
            salary_data = None
            if salaries_min or salaries_max:
                salary_data = {
                    "avg_min": int(sum(salaries_min) / len(salaries_min)) if salaries_min else None,
                    "avg_max": int(sum(salaries_max) / len(salaries_max)) if salaries_max else None,
                    "sample_size": len(salaries_min),
                }

            # Save snapshot
            snapshot = MarketSnapshot(
                snapshot_date=datetime.now(timezone.utc),
                total_jobs_scraped=total_jobs,
                total_jobs_analyzed=total_jobs,
                top_skills=top_skills,
                top_companies_hiring=top_companies,
                emerging_roles=emerging_roles,
                salary_data=salary_data,
                by_source=dict(by_source),
                by_work_mode=dict(by_work_mode),
            )
            db.add(snapshot)

            # Update skill gaps for the user
            user = (await db.execute(select(User).limit(1))).scalar_one_or_none()
            if user:
                await self._update_skill_gaps(db, user.id, top_skills)

            await db.commit()

            logger.info("Market snapshot saved", jobs=total_jobs, top_skill=top_skills[0]["skill"] if top_skills else "N/A")
            return {
                "snapshot": True,
                "jobs_analyzed": total_jobs,
                "top_skill": top_skills[0]["skill"] if top_skills else None,
            }

    async def _update_skill_gaps(self, db, user_id: str, top_skills: List[dict]) -> None:
        """Update skill gap records based on market data."""
        from app.models.user import UserSkill

        # Get user's current skills
        user_skill_names = {
            s.lower() for s in (
                await db.execute(select(UserSkill.name).where(UserSkill.user_id == user_id))
            ).scalars().all()
        }

        for skill_data in top_skills[:15]:
            skill_name = skill_data["skill"]
            has_skill = skill_name.lower() in user_skill_names

            # Check if gap record exists
            existing = (await db.execute(
                select(SkillGap).where(
                    SkillGap.user_id == user_id,
                    SkillGap.skill_name == skill_name,
                )
            )).scalar_one_or_none()

            percentage = skill_data["percentage"]
            priority = "critical" if percentage > 60 else "high" if percentage > 40 else "medium" if percentage > 20 else "low"

            if existing:
                existing.demand_count = skill_data["count"]
                existing.demand_percentage = percentage
                existing.priority = priority
                existing.user_has_skill = has_skill
                if has_skill:
                    existing.resolved = True
            else:
                if not has_skill:  # Only add gaps for skills user doesn't have
                    gap = SkillGap(
                        user_id=user_id,
                        skill_name=skill_name,
                        demand_count=skill_data["count"],
                        demand_percentage=percentage,
                        priority=priority,
                        user_has_skill=False,
                        resolved=False,
                    )
                    db.add(gap)
