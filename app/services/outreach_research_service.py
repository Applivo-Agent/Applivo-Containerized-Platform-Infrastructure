"""
app/services/outreach_research_service.py
──────────────────────────────────────────
Company Intelligence Engine.
Researches a target company using web search + LLM synthesis,
then produces a structured intelligence report with personalization hooks.
"""
from __future__ import annotations

import asyncio
import json
import re
from datetime import datetime, timezone, timedelta
from typing import Optional
import structlog
import httpx

from app.services.ai_router import chat_complete
from app.core.config import settings

logger = structlog.get_logger()

# ── Web search helper ──────────────────────────────────────────────────────────

async def _web_search(query: str, num_results: int = 5) -> list[dict]:
    """Call Serper.dev or fall back to a structured empty result."""
    api_key = getattr(settings, "SERPER_API_KEY", "") or ""
    if not api_key:
        logger.warning("SERPER_API_KEY not set — skipping web search", query=query)
        return []
    try:
        async with httpx.AsyncClient(timeout=15) as client:
            r = await client.post(
                "https://google.serper.dev/search",
                headers={"X-API-KEY": api_key, "Content-Type": "application/json"},
                json={"q": query, "num": num_results},
            )
            r.raise_for_status()
            data = r.json()
            results = []
            for item in data.get("organic", [])[:num_results]:
                results.append({
                    "title": item.get("title", ""),
                    "url": item.get("link", ""),
                    "snippet": item.get("snippet", ""),
                })
            return results
    except Exception as e:
        logger.warning("Web search failed", error=str(e))
        return []


async def _fetch_page_text(url: str, max_chars: int = 3000) -> str:
    """Fetch a URL and return stripped text content."""
    try:
        async with httpx.AsyncClient(timeout=10, follow_redirects=True) as client:
            headers = {"User-Agent": "Mozilla/5.0 (compatible; Applivo/1.0; +https://applivo.in)"}
            r = await client.get(url, headers=headers)
            if r.status_code != 200:
                return ""
            text = r.text
            # Strip HTML tags
            text = re.sub(r"<[^>]+>", " ", text)
            text = re.sub(r"\s+", " ", text).strip()
            return text[:max_chars]
    except Exception:
        return ""


# ── Main research function ─────────────────────────────────────────────────────

async def research_company(
    company_name: str,
    domain: Optional[str] = None,
    user_career_summary: Optional[str] = None,
    user_skills: Optional[list[str]] = None,
) -> dict:
    """
    Full company intelligence pipeline.
    Returns structured report dict consumed by the API and stored in OutreachIntelligence.
    """
    logger.info("Starting company research", company=company_name, domain=domain)

    search_target = domain or company_name

    # ── Phase 1: parallel web searches ────────────────────────────────────────
    searches = await asyncio.gather(
        _web_search(f"{company_name} company about products mission engineering"),
        _web_search(f"{company_name} engineering blog tech stack backend"),
        _web_search(f"{company_name} funding raised news 2025 2026"),
        _web_search(f"{company_name} careers jobs hiring culture remote"),
        return_exceptions=True,
    )

    all_snippets = []
    for result in searches:
        if isinstance(result, list):
            for item in result:
                all_snippets.append(f"[{item['title']}] {item['snippet']} (source: {item['url']})")

    snippets_text = "\n".join(all_snippets[:20]) if all_snippets else "No web data available."

    # ── Phase 2: optionally fetch homepage ────────────────────────────────────
    homepage_text = ""
    if domain:
        homepage_url = f"https://{domain}" if not domain.startswith("http") else domain
        homepage_text = await _fetch_page_text(homepage_url, max_chars=2000)

    # ── Phase 3: LLM synthesis ────────────────────────────────────────────────
    user_context = ""
    if user_career_summary:
        user_context = f"\n\nUSER CAREER CONTEXT (for match scoring):\n{user_career_summary}"
        if user_skills:
            user_context += f"\nUser skills: {', '.join(user_skills[:20])}"

    prompt = f"""You are a company intelligence analyst preparing a structured briefing before a professional outreach.

COMPANY: {company_name}
DOMAIN: {domain or 'unknown'}

WEB SEARCH RESULTS:
{snippets_text}

HOMEPAGE CONTENT (if available):
{homepage_text[:1500] if homepage_text else 'Not available'}
{user_context}

Produce a JSON intelligence report with EXACTLY this structure:
{{
  "executive_summary": "2-3 sentence summary of what this company does, their stage, and why they're notable",
  "industry": "primary industry",
  "sub_industry": "specific sub-sector",
  "business_model": "SaaS / marketplace / API / etc.",
  "stage": "startup / series-a / series-b / series-c / public / bootstrapped / unknown",
  "size_estimate": "1-10 / 11-50 / 51-200 / 201-1000 / 1000+",
  "location": "headquarters location or Remote",
  "remote_policy": "remote / hybrid / in-office / unknown",
  "tech_stack": ["list", "of", "detected", "technologies"],
  "engineering_culture": {{
    "description": "brief culture description",
    "signals": ["signal1", "signal2"]
  }},
  "funding": {{
    "total_raised": "amount or unknown",
    "last_round": "round name or unknown",
    "last_round_date": "date or unknown",
    "investors": ["investor names if known"]
  }},
  "recent_news": [
    {{"headline": "news headline", "summary": "1 sentence", "relevance": "high/medium/low"}}
  ],
  "personalization_hooks": [
    {{
      "hook": "specific fact about the company",
      "suggested_reference": "how to naturally reference this in an email",
      "confidence": "high/medium/low"
    }}
  ],
  "outreach_recommendation": {{
    "primary_angle": "what angle to lead with",
    "tone": "direct / conversational / formal / technical",
    "key_emphasis": ["point1", "point2"],
    "avoid": ["what not to say"],
    "best_contact_type": "recruiter / hiring_manager / founder",
    "timing_note": "any timing observations"
  }},
  "match_score": 70,
  "match_reasoning": "why this company is or isn't a good fit for the user (use user context if provided)",
  "confidence": 0.75,
  "sources": ["list of source urls used"]
}}

Return ONLY valid JSON. No markdown, no explanation outside the JSON."""

    try:
        raw = await chat_complete(
            messages=[{"role": "user", "content": prompt}],
            max_tokens=2000,
            endpoint="outreach_research",
        )
        # Extract JSON from response
        raw = raw.strip()
        if raw.startswith("```"):
            raw = re.sub(r"^```[a-z]*\n?", "", raw)
            raw = re.sub(r"\n?```$", "", raw)
        report = json.loads(raw)
    except json.JSONDecodeError as e:
        logger.warning("Research LLM returned invalid JSON", error=str(e))
        report = _fallback_report(company_name, domain)
    except Exception as e:
        logger.error("Research LLM call failed", error=str(e))
        report = _fallback_report(company_name, domain)

    # Ensure required keys exist
    report.setdefault("personalization_hooks", [])
    report.setdefault("recent_news", [])
    report.setdefault("tech_stack", [])
    report.setdefault("confidence", 0.5)
    report.setdefault("executive_summary", f"Intelligence report for {company_name}.")
    report.setdefault("match_score", 70)

    logger.info("Company research complete", company=company_name,
                hooks=len(report.get("personalization_hooks", [])),
                confidence=report.get("confidence"))
    return report


def _fallback_report(company_name: str, domain: Optional[str]) -> dict:
    return {
        "executive_summary": f"{company_name} is a company we were unable to fully research at this time.",
        "industry": "Unknown",
        "sub_industry": "Unknown",
        "business_model": "Unknown",
        "stage": "unknown",
        "size_estimate": "unknown",
        "location": "Unknown",
        "remote_policy": "unknown",
        "tech_stack": [],
        "engineering_culture": {"description": "Unknown", "signals": []},
        "funding": {"total_raised": "unknown", "last_round": "unknown"},
        "recent_news": [],
        "personalization_hooks": [],
        "outreach_recommendation": {
            "primary_angle": "Express genuine interest and ask about open roles",
            "tone": "professional",
            "key_emphasis": [],
            "avoid": [],
            "best_contact_type": "recruiter",
            "timing_note": "",
        },
        "match_score": 70,
        "match_reasoning": "Insufficient data to score match.",
        "confidence": 0.2,
        "sources": [],
    }


# ── Contact discovery ──────────────────────────────────────────────────────────

async def discover_contacts(company_name: str, domain: str, target_role: str = "engineer") -> list[dict]:
    """
    Attempt to discover public recruiter/HM contacts for a company.
    Returns list of contact dicts with confidence scores.
    """
    logger.info("Discovering contacts", company=company_name, domain=domain)

    results = await asyncio.gather(
        _web_search(f"{company_name} recruiter hiring talent email site:linkedin.com OR site:wellfound.com"),
        _web_search(f'"{domain}" recruiter OR "talent acquisition" OR "engineering manager" contact email'),
        return_exceptions=True,
    )

    all_snippets = []
    for r in results:
        if isinstance(r, list):
            for item in r:
                all_snippets.append(f"[{item['title']}] {item['snippet']} (url: {item['url']})")

    snippets_text = "\n".join(all_snippets[:15]) if all_snippets else "No contact data found."

    prompt = f"""You are a contact discovery agent. Extract any publicly visible professional contacts for {company_name} (domain: {domain}).

SEARCH RESULTS:
{snippets_text}

Return a JSON array of contacts found. Each contact:
{{
  "name": "full name or null",
  "title": "job title",
  "email": "email if found, else null",
  "linkedin_url": "linkedin profile url if found, else null",
  "role_type": "recruiter / hiring_manager / founder / other",
  "email_confidence": 0.0-1.0,
  "source": "where this was found (url or description)",
  "notes": "any other relevant info"
}}

Rules:
- Only include people who appear to WORK at {company_name} currently
- Only include contacts from PUBLIC sources
- If email not directly found but name + domain known, infer common pattern (first.last@{domain}) and set confidence 0.5
- careers@{domain} is always a valid fallback at confidence 0.9
- Return 1-5 contacts maximum, ranked by relevance
- Always include careers@{domain} as last resort if nothing better found
- Return ONLY a JSON array, no markdown

Example fallback: [{{"name": null, "title": "Talent Team", "email": "careers@{domain}", "linkedin_url": null, "role_type": "recruiter", "email_confidence": 0.7, "source": "Standard careers email pattern", "notes": "General hiring inbox"}}]"""

    try:
        raw = await chat_complete(
            messages=[{"role": "user", "content": prompt}],
            max_tokens=800,
            endpoint="outreach_contacts",
        )
        raw = raw.strip()
        if raw.startswith("```"):
            raw = re.sub(r"^```[a-z]*\n?", "", raw)
            raw = re.sub(r"\n?```$", "", raw)
        contacts = json.loads(raw)
        if not isinstance(contacts, list):
            contacts = []
    except Exception as e:
        logger.warning("Contact discovery failed", error=str(e))
        contacts = []

    # Always ensure careers@ fallback
    has_fallback = any(c.get("email", "").startswith("careers@") for c in contacts)
    if not has_fallback and domain:
        contacts.append({
            "name": None,
            "title": "Hiring Team",
            "email": f"careers@{domain}",
            "linkedin_url": None,
            "role_type": "recruiter",
            "email_confidence": 0.7,
            "source": "Standard careers email pattern",
            "notes": "General hiring inbox — use if direct contact not available",
        })

    logger.info("Contact discovery complete", company=company_name, contacts_found=len(contacts))
    return contacts
