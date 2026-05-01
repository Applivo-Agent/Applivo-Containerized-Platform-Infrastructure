import re
from typing import Any, Dict, List, Optional

month_map = {
    "jan": "01", "january": "01",
    "feb": "02", "february": "02",
    "mar": "03", "march": "03",
    "apr": "04", "april": "04",
    "may": "05",
    "jun": "06", "june": "06",
    "jul": "07", "july": "07",
    "aug": "08", "august": "08",
    "sep": "09", "sept": "09", "september": "09",
    "oct": "10", "october": "10",
    "nov": "11", "november": "11",
    "dec": "12", "december": "12",
}

def _as_str(value: Any) -> str:
    return value.strip() if isinstance(value, str) else ""

def _extract_year(value: Any) -> Optional[int]:
    if value is None:
        return None
    text = _as_str(value)
    if not text:
        return None
    match = re.search(r"\b(19|20)\d{2}\b", text)
    if match:
        try:
            return int(match.group(0))
        except (TypeError, ValueError):
            return None
    return None

def _normalize_month_year(value: Any, default_month: str = "01") -> Optional[str]:
    text = _as_str(value)
    if not text:
        return None

    lowered = text.lower().strip().strip(".")
    if lowered in {"present", "current", "ongoing", "now", "till date", "to date", "still"}:
        return None

    # YYYY-MM or YYYY/MM
    m = re.search(r"\b((19|20)\d{2})[./-]([01]?\d)\b", text)
    if m:
        month = int(m.group(3))
        if 1 <= month <= 12:
            return f"{m.group(1)}-{month:02d}"

    # MM/YYYY or MM-YYYY
    m = re.search(r"\b([01]?\d)[./-]((19|20)\d{2})\b", text)
    if m:
        month = int(m.group(1))
        if 1 <= month <= 12:
            return f"{m.group(2)}-{month:02d}"

    # Month YYYY (e.g., January 2024, Jan. 2024, Aug 2023)
    m = re.search(r"\b([A-Za-z]{3,9})[.,\s]+((19|20)\d{2})\b", text)
    if m:
        mon_str = m.group(1).lower().rstrip(".")
        month = month_map.get(mon_str)
        if not month and len(mon_str) >= 3:
            for k, v in month_map.items():
                if k.startswith(mon_str[:3]):
                    month = v
                    break
        if month:
            return f"{m.group(2)}-{month}"

    year = _extract_year(text)
    if year:
        return f"{year}-{default_month}"

    return None

def _parse_date_range(value: Any) -> Dict[str, Any]:
    text = _as_str(value)
    if not text:
        return {"start_date": None, "end_date": None, "is_current": False}

    # Split by various dash types or "to/until/through"
    parts = re.split(r"\s*(?:-|–|—|to|until|through)\s*", text, maxsplit=1, flags=re.IGNORECASE)
    start_raw = parts[0] if parts else ""
    end_raw = parts[1] if len(parts) > 1 else ""

    start_date = _normalize_month_year(start_raw, "01")
    end_date = _normalize_month_year(end_raw, "12") if end_raw else None

    is_current = False
    if end_raw:
        lowered_end = end_raw.lower().strip().strip(".")
        is_current = lowered_end in {"present", "current", "ongoing", "now", "till date", "to date", "still"}
    elif "present" in text.lower() or "current" in text.lower():
        is_current = True

    return {
        "start_date": start_date,
        "end_date": None if is_current else end_date,
        "is_current": is_current,
    }

# Test suite
test_cases = [
    "Jan 2024 - Present",
    "August, 2023 to Now",
    "08/2022 — 05/2023",
    "Sept. 2021 through current",
    "2020-01 to 2021-12",
    "Oct 2019 - Present",
    "Jan. 2024",
    "01/24", # Might still fail if strictly 4-digit, but LLM usually gives 4
    "2024",
]

print(f"{'Input':<30} | {'Start':<10} | {'End':<10} | {'Current':<8}")
print("-" * 70)
for tc in test_cases:
    res = _parse_date_range(tc)
    print(f"{tc:<30} | {str(res['start_date']):<10} | {str(res['end_date']):<10} | {str(res['is_current']):<8}")
