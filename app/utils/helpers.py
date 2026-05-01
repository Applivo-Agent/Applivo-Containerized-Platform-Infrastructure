"""
app/utils/helpers.py
──────────────────────
Common utility functions used across the platform.
"""

from __future__ import annotations

import re
import uuid
from datetime import datetime, timezone
from typing import Optional


def generate_id() -> str:
    """Generate a new UUID string."""
    return str(uuid.uuid4())


def utcnow() -> datetime:
    """Return current UTC datetime (timezone-aware)."""
    return datetime.now(timezone.utc)


def slugify(text: str) -> str:
    """Convert text to a URL/filename-safe slug."""
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_-]+", "_", text)
    text = re.sub(r"^-+|-+$", "", text)
    return text[:50]


def truncate(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """Truncate text to max_length, appending suffix if truncated."""
    if len(text) <= max_length:
        return text
    return text[: max_length - len(suffix)] + suffix


def clean_html(html: str) -> str:
    """Strip HTML tags and normalize whitespace from a string."""
    if not html:
        return ""
    try:
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(html, "html.parser")
        text = soup.get_text(separator="\n")
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        return "\n".join(lines)
    except Exception:
        # Fallback: simple regex strip
        clean = re.sub(r"<[^>]+>", " ", html)
        return re.sub(r"\s+", " ", clean).strip()


def extract_salary(text: str) -> tuple[Optional[int], Optional[int], Optional[str]]:
    """
    Extract salary range from a text string.
    Returns (min_salary, max_salary, currency).
    """
    if not text:
        return None, None, None

    currency = None
    if "$" in text or "USD" in text:
        currency = "USD"
    elif "₹" in text or "INR" in text or "LPA" in text.upper():
        currency = "INR"
    elif "€" in text or "EUR" in text:
        currency = "EUR"
    elif "£" in text or "GBP" in text:
        currency = "GBP"

    # Normalize: remove commas, handle k/K suffix
    normalized = text.replace(",", "")
    numbers = re.findall(r"\d+(?:\.\d+)?(?:k|K|lpa|LPA)?", normalized)

    parsed = []
    for num in numbers:
        n = num.lower()
        try:
            if "k" in n:
                parsed.append(int(float(n.replace("k", "")) * 1000))
            elif "lpa" in n:
                parsed.append(int(float(n.replace("lpa", "")) * 100000))
            else:
                val = int(float(n))
                if val > 100:  # Ignore tiny numbers like "3 years"
                    parsed.append(val)
        except ValueError:
            pass

    if len(parsed) >= 2:
        return min(parsed[:2]), max(parsed[:2]), currency
    elif len(parsed) == 1:
        return parsed[0], None, currency
    return None, None, None


def detect_work_mode(text: str) -> str:
    """Detect remote/hybrid/onsite from job text."""
    text_lower = text.lower()
    if any(w in text_lower for w in ["fully remote", "100% remote", "work from home", "wfh", "remote only"]):
        return "remote"
    if any(w in text_lower for w in ["hybrid", "flexible location"]):
        return "hybrid"
    if any(w in text_lower for w in ["onsite", "on-site", "in-office", "in office", "on site"]):
        return "onsite"
    if "remote" in text_lower:
        return "remote"
    return "unknown"


def detect_job_type(text: str) -> str:
    """Detect job type (full_time, internship, contract) from text."""
    text_lower = text.lower()
    if any(w in text_lower for w in ["intern", "internship", "trainee", "apprentice"]):
        return "internship"
    if any(w in text_lower for w in ["contract", "contractor", "freelance", "consultant"]):
        return "contract"
    if "part-time" in text_lower or "part time" in text_lower:
        return "part_time"
    return "full_time"


def count_tokens_estimate(text: str) -> int:
    """Rough token count estimate (4 chars ≈ 1 token)."""
    return len(text) // 4
