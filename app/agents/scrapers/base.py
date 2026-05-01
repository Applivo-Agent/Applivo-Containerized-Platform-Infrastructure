"""
app/agents/scrapers/base.py
────────────────────────────
Abstract base class for all job scrapers.
Handles: rate limiting, deduplication, DB persistence, error recovery.
Every platform scraper (LinkedIn, Indeed, etc.) inherits from this.
"""

from __future__ import annotations

import asyncio
import random
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

import structlog
from sqlalchemy import select, cast, String

from app.core.config import settings
from app.core.database import get_db_context
from app.models.job import Job, JobSource, JobStatus, ExperienceLevel, JobType, WorkMode

logger = structlog.get_logger()


class ScrapedJob:
    """
    Raw scraped job data — platform-agnostic intermediate representation.
    Scrapers produce these; the base class saves them to the DB.
    """
    def __init__(
        self,
        source: str,
        source_job_id: str,
        source_url: str,
        title: str,
        company_name: str,
        description_raw: str = "",
        location: Optional[str] = None,
        work_mode: str = "unknown",
        job_type: str = "full_time",
        salary_min: Optional[int] = None,
        salary_max: Optional[int] = None,
        salary_currency: Optional[str] = None,
        posted_at: Optional[datetime] = None,
        applicant_count: Optional[int] = None,
        easy_apply: bool = False,
        company_logo_url: Optional[str] = None,
        experience_level: str = "unknown",
        raw_html: Optional[str] = None,
        extra: Optional[Dict] = None,
    ):
        self.source = source
        self.source_job_id = source_job_id
        self.source_url = source_url
        self.title = title
        self.company_name = company_name
        self.description_raw = description_raw
        self.location = location
        self.work_mode = work_mode
        self.job_type = job_type
        self.experience_level = experience_level
        self.salary_min = salary_min
        self.salary_max = salary_max
        self.salary_currency = salary_currency
        self.posted_at = posted_at
        self.applicant_count = applicant_count
        self.easy_apply = easy_apply
        self.company_logo_url = company_logo_url
        self.raw_html = raw_html
        self.extra = extra or {}


class BaseScraper(ABC):
    """
    Abstract base scraper.
    Subclasses implement: _get_search_urls() and _scrape_page().
    This base class handles everything else.
    """

    source: str = ""  # Override in subclass e.g. "linkedin"

    def __init__(self, user_id: Optional[str] = None):
        self.log = structlog.get_logger(scraper=self.source)
        self._jobs_found = 0
        self._jobs_new = 0
        self._jobs_duplicate = 0
        self._errors = 0
        self._user_id = user_id

    def _normalize_experience_level(self, value: Any) -> ExperienceLevel:
        """Convert scraper values like 'entry' into the DB enum members expected by PostgreSQL."""
        if isinstance(value, ExperienceLevel):
            return value

        normalized = str(value or "unknown").strip().upper().replace("-", "_")
        mapping = {
            "ENTRY": ExperienceLevel.ENTRY,
            "MID": ExperienceLevel.MID,
            "MID_LEVEL": ExperienceLevel.MID,
            "SENIOR": ExperienceLevel.SENIOR,
            "LEAD": ExperienceLevel.LEAD,
            "EXECUTIVE": ExperienceLevel.EXECUTIVE,
            "UNKNOWN": ExperienceLevel.UNKNOWN,
        }
        return mapping.get(normalized, ExperienceLevel.UNKNOWN)

    def _normalize_job_source(self, value: Any) -> JobSource:
        if isinstance(value, JobSource):
            return value
        normalized = str(value or self.source or "MANUAL").strip().upper().replace("-", "_")
        mapping = {
            "LINKEDIN": JobSource.LINKEDIN,
            "INDEED": JobSource.INDEED,
            "INTERNSHALA": JobSource.INTERNSHALA,
            "REMOTEOK": JobSource.REMOTEOK,
            "WELLFOUND": JobSource.WELLFOUND,
            "GLASSDOOR": JobSource.GLASSDOOR,
            "COMPANY_SITE": JobSource.COMPANY_SITE,
            "MANUAL": JobSource.MANUAL,
        }
        return mapping.get(normalized, JobSource.MANUAL)

    def _normalize_work_mode(self, value: Any) -> WorkMode:
        """Convert scraper work mode values like 'remote' into canonical WorkMode enum."""
        if isinstance(value, WorkMode):
            return value
        normalized = str(value or "unknown").strip().upper().replace("-", "_")
        mapping = {
            "REMOTE": WorkMode.REMOTE,
            "ONSITE": WorkMode.ONSITE,
            "ON_SITE": WorkMode.ONSITE,
            "HYBRID": WorkMode.HYBRID,
            "UNKNOWN": WorkMode.UNKNOWN,
        }
        return mapping.get(normalized, WorkMode.UNKNOWN)

    def _normalize_job_type(self, value: Any) -> JobType:
        """Convert scraper job type values like 'full_time' into canonical JobType enum."""
        if isinstance(value, JobType):
            return value
        normalized = str(value or "full_time").strip().upper().replace("-", "_")
        mapping = {
            "FULL_TIME": JobType.FULL_TIME,
            "PART_TIME": JobType.PART_TIME,
            "INTERNSHIP": JobType.INTERNSHIP,
            "CONTRACT": JobType.CONTRACT,
            "FREELANCE": JobType.FREELANCE,
        }
        return mapping.get(normalized, JobType.FULL_TIME)

    # ── Abstract interface ───────────────────────────────────────────────────

    @abstractmethod
    async def _get_search_queries(self) -> List[Dict[str, Any]]:
        """
        Return list of search parameter sets to run.
        Each dict maps to one search page sequence.
        Example: [{"query": "ML engineer", "location": "remote"}, ...]
        """
        ...

    @abstractmethod
    async def _scrape_query(self, query_params: Dict) -> List[ScrapedJob]:
        """
        Given one set of search parameters, scrape and return jobs.
        May involve multiple pages of pagination.
        """
        ...

    # ── Main entry point ─────────────────────────────────────────────────────

    async def run(self) -> Dict:
        """
        Full scrape cycle for this platform.
        Returns summary dict for logging/chaining.
        """
        self.log.info("Starting scrape cycle")

        try:
            queries = await self._get_search_queries()
            all_jobs: List[ScrapedJob] = []

            for query in queries:
                try:
                    jobs = await self._scrape_query(query)
                    all_jobs.extend(jobs)
                    self._jobs_found += len(jobs)
                    # Polite delay between queries
                    await self._sleep()
                except Exception as e:
                    self._errors += 1
                    self.log.error("Query failed", query=query, error=str(e))

            # Save to database (dedup handled here)
            if all_jobs:
                await self._save_jobs(all_jobs[:settings.MAX_JOBS_PER_CYCLE])

        except Exception as e:
            self.log.error("Scrape cycle failed", error=str(e))
            raise

        result = {
            "source": self.source,
            "jobs_found": self._jobs_found,
            "jobs_new": self._jobs_new,
            "jobs_duplicate": self._jobs_duplicate,
            "errors": self._errors,
        }
        self.log.info("Scrape cycle complete", **result)
        return result

    # ── Database persistence ─────────────────────────────────────────────────

    async def _save_jobs(self, scraped_jobs: List[ScrapedJob]) -> None:
        """
        Batch-save scraped jobs. Skips duplicates per user (same source + source_job_id + user_id).
        Cleans description text before saving.
        """
        async with get_db_context() as db:
            # Fetch existing source_job_ids for THIS user to detect duplicates
            normalized_source = self._normalize_job_source(scraped_jobs[0].source if scraped_jobs else self.source)
            dup_query = select(Job.source_job_id).where(
                cast(Job.source, String) == normalized_source.value,
                Job.user_id == self._user_id,
            )
            existing_result = await db.execute(dup_query)
            existing_ids = {row[0] for row in existing_result.all()}

            new_jobs = []
            for scraped in scraped_jobs:
                if scraped.source_job_id in existing_ids:
                    self._jobs_duplicate += 1
                    continue

                job = Job(
                    user_id=self._user_id,
                    source=self._normalize_job_source(scraped.source),
                    source_job_id=scraped.source_job_id,
                    source_url=scraped.source_url,
                    title=self._clean_title(scraped.title),
                    company_name=scraped.company_name.strip(),
                    company_logo_url=scraped.company_logo_url,
                    description_raw=scraped.description_raw,
                    description_clean=self._clean_description(scraped.description_raw),
                    location=scraped.location,
                    work_mode=self._normalize_work_mode(scraped.work_mode),
                    job_type=self._normalize_job_type(scraped.job_type),
                    experience_level=self._normalize_experience_level(getattr(scraped, "experience_level", "unknown")),
                    salary_min=scraped.salary_min,
                    salary_max=scraped.salary_max,
                    salary_currency=scraped.salary_currency,
                    posted_at=scraped.posted_at,
                    applicant_count=scraped.applicant_count,
                    easy_apply=scraped.easy_apply,
                    raw_html=scraped.raw_html,
                    scraped_at=datetime.now(timezone.utc),
                    status=JobStatus.NEW,
                    is_active=True,
                )
                new_jobs.append(job)
                existing_ids.add(scraped.source_job_id)

            if new_jobs:
                db.add_all(new_jobs)
                await db.commit()
                self._jobs_new += len(new_jobs)
                self.log.info(f"Saved {len(new_jobs)} new jobs", user_id=self._user_id)

    # ── Utilities ────────────────────────────────────────────────────────────

    async def _sleep(self, extra: float = 0.0) -> None:
        """Polite random delay between requests."""
        delay = random.uniform(
            settings.SCRAPE_DELAY_MIN_SECONDS,
            settings.SCRAPE_DELAY_MAX_SECONDS,
        ) + extra
        await asyncio.sleep(delay)

    def _clean_title(self, title: str) -> str:
        return title.strip()[:500]

    def _clean_description(self, raw: str) -> str:
        """Strip HTML tags and normalize whitespace."""
        if not raw:
            return ""
        try:
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(raw, "html.parser")
            text = soup.get_text(separator="\n")
            lines = [line.strip() for line in text.splitlines() if line.strip()]
            return "\n".join(lines)[:50000]  # Cap at 50k chars
        except Exception:
            return raw[:50000]

    def _detect_work_mode(self, text: str) -> str:
        """Heuristic detection of remote/hybrid/onsite from text."""
        text_lower = text.lower()
        if any(w in text_lower for w in ["fully remote", "100% remote", "remote only", "work from home"]):
            return "remote"
        if any(w in text_lower for w in ["hybrid", "flexible"]):
            return "hybrid"
        if any(w in text_lower for w in ["onsite", "on-site", "in-office", "in office"]):
            return "onsite"
        if "remote" in text_lower:
            return "remote"
        return "unknown"

    def _detect_job_type(self, text: str) -> str:
        """Detect full-time, internship, contract from text."""
        text_lower = text.lower()
        if any(w in text_lower for w in ["intern", "internship", "trainee"]):
            return "internship"
        if any(w in text_lower for w in ["contract", "contractor", "freelance"]):
            return "contract"
        if "part-time" in text_lower or "part time" in text_lower:
            return "part_time"
        return "full_time"

    def _parse_salary(self, text: str) -> tuple[Optional[int], Optional[int], Optional[str]]:
        """Extract salary range from text. Returns (min, max, currency)."""
        import re
        if not text:
            return None, None, None

        # Common patterns: $80k-$120k, ₹15,00,000 - ₹25,00,000, $80,000 - $120,000
        currency = None
        if "$" in text:
            currency = "USD"
        elif "₹" in text or "INR" in text:
            currency = "INR"
        elif "€" in text:
            currency = "EUR"
        elif "£" in text:
            currency = "GBP"

        # Extract numbers
        # FIX 12: strip commas first, then match digits only (no comma in char class)
        clean_text = text.replace(",", "")
        numbers = re.findall(r"\d+(?:k|K|lpa|LPA)?", clean_text)
        parsed = []
        for num in numbers:
            n = num.lower()
            # lpa = lakhs per annum: e.g. "5lpa" → 500000
            if n.endswith("lpa"):
                try:
                    parsed.append(int(float(n[:-3]) * 100_000))
                except ValueError:
                    pass
            elif n.endswith("k"):
                try:
                    parsed.append(int(float(n[:-1]) * 1_000))
                except ValueError:
                    pass
            else:
                try:
                    parsed.append(int(n))
                except ValueError:
                    pass

        if len(parsed) >= 2:
            return min(parsed[:2]), max(parsed[:2]), currency
        elif len(parsed) == 1:
            return parsed[0], None, currency
        return None, None, None