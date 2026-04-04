from __future__ import annotations

import asyncio
import json
import logging
import random
import re
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

import httpx
import structlog
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
    before_sleep_log,
)

from app.agents.scrapers.base import BaseScraper, ScrapedJob
from app.core.config import settings

log = structlog.get_logger()
logger = logging.getLogger(__name__)

_USER_AGENTS = [
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
]


def _get_parser():
    try:
        import lxml
        return "lxml"
    except ImportError:
        return "html.parser"


# ---------------- RETRY ----------------

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=10),
    retry=retry_if_exception_type((
        httpx.TimeoutException,
        httpx.ConnectError,
        httpx.RemoteProtocolError,
    )),
    before_sleep=before_sleep_log(logger, logging.WARNING),
    reraise=True,
)
async def _http_get_with_retry(
    client: httpx.AsyncClient,
    url: str,
    **kwargs,
) -> httpx.Response:
    """HTTP GET with exponential backoff retry using tenacity."""
    return await client.get(url, **kwargs)


# ---------------- SCRAPER ----------------

class InternshalaScaper(BaseScraper):

    source = "internshala"

    BASE_URL = "https://internshala.com"

    def __init__(self, user_id: str = None):

        super().__init__()

        self._ua = random.choice(_USER_AGENTS)
        self._user_id = user_id
        self._user_desired_roles = None

        self._cookies_file = (
            settings.storage_path /
            "internshala_cookies.json"
        )

        self._client: Optional[httpx.AsyncClient] = None

    async def _load_user_preferences(self):
        """Load user's desired roles from database if user_id provided."""
        if not self._user_id or self._user_desired_roles is not None:
            return
        
        try:
            from sqlalchemy import select
            from app.models.user import UserProfile
            from app.core.database import get_db_context
            
            async with get_db_context() as db:
                result = await db.execute(
                    select(UserProfile.desired_roles).where(UserProfile.user_id == self._user_id)
                )
                self._user_desired_roles = result.scalar_one_or_none() or []
        except Exception:
            self._user_desired_roles = []

    # REQUIRED METHOD

    async def _get_search_queries(
        self
    ) -> List[Dict[str, Any]]:

        await self._load_user_preferences()
        
        queries: List[Dict[str, Any]] = []

        seen: set = set()

        # Use user's desired roles from database, fallback to settings
        roles_to_use = self._user_desired_roles if self._user_desired_roles else settings.USER_DESIRED_ROLES

        for role in roles_to_use:

            role = role.strip()

            if role and role not in seen:

                seen.add(role)

                queries.append({
                    "category": role
                })

        if "Machine Learning" not in seen:

            queries.append({
                "category": "Machine Learning"
            })

        self.log.info(
            "Search queries generated",
            count=len(queries),
            queries=[q["category"] for q in queries]
        )

        return queries

    # CLIENT

    async def _get_client(self) -> httpx.AsyncClient:

        if self._client:

            return self._client

        cookies: Dict[str, str] = {}

        if self._cookies_file.exists():

            try:

                raw = json.loads(
                    self._cookies_file.read_text()
                )

                for c in raw:

                    name = c.get("name")
                    value = c.get("value")

                    if name and value:

                        cookies[name] = value

                self.log.info(
                    "Loaded cookies",
                    count=len(cookies)
                )

            except Exception as e:

                self.log.warning(
                    "Cookie load failed",
                    error=str(e)
                )

        self._client = httpx.AsyncClient(

            base_url=self.BASE_URL,

            headers={
                "User-Agent": self._ua,
                "Accept-Language": "en-IN,en;q=0.9",
                "Connection": "keep-alive",
            },

            cookies=cookies,

            follow_redirects=True,

            timeout=30,
        )

        return self._client

    # QUERY

    async def _scrape_query(
        self,
        query_params: Dict,
    ) -> List[ScrapedJob]:

        category = query_params["category"]

        client = await self._get_client()

        jobs: List[ScrapedJob] = []

        seen_ids: set = set()

        page = 1

        max_pages = 5

        while page <= max_pages:

            page_jobs = await self._fetch_html_page(
                client,
                category,
                page
            )

            if not page_jobs:
                break

            # Deduplicate across pages
            new_jobs = []
            for job in page_jobs:
                if job.source_job_id not in seen_ids:
                    seen_ids.add(job.source_job_id)
                    new_jobs.append(job)

            if not new_jobs:
                self.log.info(
                    "No new jobs on page, stopping",
                    page=page,
                    category=category,
                )
                break

            jobs.extend(new_jobs)

            page += 1

            await asyncio.sleep(
                random.uniform(1.5, 3.0)
            )

        self.log.info(
            "Query complete",
            category=category,
            count=len(jobs),
        )

        return jobs

    # FETCH

    async def _fetch_html_page(
        self,
        client: httpx.AsyncClient,
        category: str,
        page: int,
    ) -> List[ScrapedJob]:

        slug = category.lower().replace(" ", "-")

        start = (page - 1) * 10

        url = f"/internships/{slug}-internship"

        self.log.debug(
            "Fetching page",
            url=url,
            start=start,
            category=category,
        )

        resp = await _http_get_with_retry(

            client,

            url,

            params={
                "start": start,
                "wfh": 1,  # Filter for work-from-home to avoid location eligibility issues
            },

            headers={
                "Accept": "text/html,*/*",
                "Referer": f"{self.BASE_URL}/internships/",
            }
        )

        self.log.debug(
            "Response received",
            status=resp.status_code,
            url=str(resp.url),
            content_length=len(resp.text),
            category=category,
        )

        if resp.status_code != 200:

            self.log.warning(
                "HTML fetch failed",
                status=resp.status_code,
                page=page
            )

            return []

        # Check for login redirect (not just captcha scripts)
        if "/login" in str(resp.url):
            self.log.warning(
                "Redirected to login",
                url=str(resp.url),
                category=category,
            )
            return []

        return self._parse_html(
            resp.text,
            category,
        )

    # PARSER

    def _parse_html(
        self,
        html: str,
        category: str,
    ) -> List[ScrapedJob]:

        from bs4 import BeautifulSoup

        parser = _get_parser()

        soup = BeautifulSoup(html, parser)

        jobs: List[ScrapedJob] = []

        # ---------- NEXT_DATA ----------

        script = soup.find(
            "script",
            id="__NEXT_DATA__"
        )

        if script and script.string:

            try:

                data = json.loads(
                    script.string
                )

                props = (
                    data
                    .get("props", {})
                    .get("pageProps", {})
                )

                internships = (
                    props.get("internships", [])
                    or
                    props.get("internship_list", [])
                    or
                    props.get("internship_ids", [])
                )

                self.log.info(
                    "NEXT_DATA internships found",
                    count=len(internships),
                    category=category,
                    props_keys=list(props.keys())[:10],
                )

                if not internships:
                    self.log.warning(
                        "NEXT_DATA found but no internships in pageProps",
                        category=category,
                        props_keys=list(props.keys())[:10],
                    )

                for item in internships:

                    job_id = str(
                        item.get("id")
                        or
                        item.get("internship_id")
                        or
                        ""
                    )

                    if not job_id:
                        continue

                    title = (
                        item.get("title")
                        or
                        item.get("profile_name")
                        or
                        "Internship"
                    )

                    company = (
                        item.get("company_name")
                        or
                        "Unknown"
                    )

                    location = ", ".join(
                        item.get(
                            "location_names",
                            []
                        )
                    )

                    source_url = (
                        self.BASE_URL +
                        (
                            item.get("url")
                            or
                            f"/internship/detail/{job_id}"
                        )
                    )

                    jobs.append(

                        ScrapedJob(

                            source=self.source,

                            source_job_id=(
                                f"internshala_{job_id}"
                            ),

                            source_url=source_url,

                            title=title,

                            company_name=company,

                            location=location,

                            work_mode="remote"
                            if "work from home"
                            in location.lower()
                            else "onsite",

                            job_type="internship",

                            salary_min=0,

                            salary_max=0,

                            salary_currency="INR",

                            posted_at=datetime.now(
                                timezone.utc
                            ),

                            easy_apply=True,
                        )

                    )

                if jobs:

                    self.log.info(
                        "Parsed from NEXT_DATA",
                        count=len(jobs),
                        category=category,
                    )

                    return jobs

            except Exception as e:

                self.log.warning(
                    "NEXT_DATA parse failed",
                    error=str(e),
                )

        else:
            self.log.info(
                "No __NEXT_DATA__ script found, using HTML fallback",
                category=category,
            )

        # ---------- FALLBACK ----------

        # Try multiple selectors for internship cards
        # Priority: container divs first, then links
        cards = soup.find_all(
            "div",
            class_=re.compile(
                r"individual_internship",
                re.I
            )
        )

        if not cards:
            cards = soup.find_all(
                "a",
                href=re.compile(r"/internship/detail/")
            )

        if not cards:
            cards = soup.find_all(
                "div",
                attrs={
                    "data-internship-id": True
                }
            )

        self.log.info(
            "HTML fallback parse",
            cards_found=len(cards),
            category=category,
        )

        for card in cards:
            try:
                # Extract internship ID
                internship_id = (
                    card.get("internshipid")
                    or card.get("data-internship-id")
                    or card.get("data-id")
                )

                if not internship_id:
                    href = (
                        card.get("data-href")
                        or card.get("href", "")
                    )
                    # Try hyphen-separated ID first
                    match = re.search(
                        r"-(\d{6,})$",
                        href
                    )
                    if not match:
                        # Try ID at end of URL (no hyphen)
                        match = re.search(
                            r"(\d{6,})$",
                            href
                        )
                    if match:
                        internship_id = match.group(1)

                if not internship_id:
                    continue

                # Try to find title
                title_el = card.find(
                    "a",
                    id="job_title"
                )
                if not title_el:
                    title_el = card.find(
                        ["h3", "h4"],
                        class_=re.compile(r"job-internship-name", re.I)
                    )
                if not title_el:
                    title_el = card.find(
                        "a",
                        href=re.compile(r"/internship/detail/")
                    )
                title = (
                    title_el.get_text(strip=True)
                    if title_el
                    else "Internship"
                )

                # Try to find company
                company_el = card.find(
                    "p",
                    class_=re.compile(r"company-name", re.I)
                )
                if not company_el:
                    company_el = card.find(
                        ["a", "p", "span"],
                        class_=re.compile(r"company_name|company", re.I)
                    )
                company = (
                    company_el.get_text(strip=True)
                    if company_el
                    else "Unknown"
                )

                # Try to find location
                location_el = card.find(
                    "div",
                    class_=re.compile(r"row-1-item.*locations|locations", re.I)
                )
                if location_el:
                    location = location_el.get_text(
                        strip=True
                    )
                else:
                    location_el = card.find(
                        ["span", "p", "div"],
                        class_=re.compile(r"location|city", re.I)
                    )
                    location = (
                        location_el.get_text(strip=True)
                        if location_el
                        else ""
                    )

                # Build URL
                href = (
                    card.get("data-href")
                    or card.get("href", "")
                )
                if not href:
                    link_el = card.find(
                        "a",
                        href=re.compile(r"/internship/detail/")
                    )
                    href = (
                        link_el.get("href", "")
                        if link_el
                        else f"/internship/detail/internship-{internship_id}"
                    )
                source_url = self.BASE_URL + href

                jobs.append(
                    ScrapedJob(
                        source=self.source,
                        source_job_id=f"internshala_{internship_id}",
                        source_url=source_url,
                        title=title,
                        company_name=company,
                        location=location,
                        work_mode="remote"
                        if "work from home"
                        in location.lower()
                        else "onsite",
                        job_type="internship",
                        salary_min=0,
                        salary_max=0,
                        salary_currency="INR",
                        posted_at=datetime.now(timezone.utc),
                        easy_apply=True,
                    )
                )

            except Exception as e:
                self.log.warning(
                    "Card parse error",
                    error=str(e),
                )

        if jobs:
            self.log.info(
                "Parsed from HTML fallback",
                count=len(jobs),
                category=category,
            )

        # Debug: log page snippet if no jobs found
        if not jobs:
            snippet = html[:2000] if len(html) > 2000 else html
            self.log.debug(
                "Page HTML snippet for debugging",
                category=category,
                snippet=snippet[:500],
                has_next_data=bool(
                    soup.find("script", id="__NEXT_DATA__")
                ),
                page_length=len(html),
            )

        return jobs

    async def close(self):

        if self._client:

            await self._client.aclose()

            self._client = None


__all__ = [
    "InternshalaScaper",
    "IntershalaScraper",
]

IntershalaScraper = InternshalaScaper