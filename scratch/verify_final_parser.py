import re
from typing import Any, Dict, List, Optional

month_map = {
    "jan": "01", "january": "01", "feb": "02", "february": "02",
    "mar": "03", "march": "03", "apr": "04", "april": "04",
    "may": "05", "jun": "06", "june": "06", "jul": "07", "july": "07",
    "aug": "08", "august": "08", "sep": "09", "sept": "09", "september": "09",
    "oct": "10", "october": "10", "nov": "11", "november": "11", "dec": "12", "december": "12",
}

def _as_str(v): return str(v).strip() if v is not None else ""

def _extract_year(value: Any) -> Optional[int]:
    text = _as_str(value)
    if not text: return None
    match = re.search(r"\b(19|20)\d{2}\b", text)
    if match: return int(match.group(0))
    return None

def _normalize_month_year(value: Any, default_month: str = "01") -> Optional[str]:
    text = _as_str(value)
    if not text: return None
    lowered = text.lower().strip().strip(". \t\n")
    if lowered in {"present", "current", "ongoing", "now", "still"}: return None
    text = re.sub(r"^(?:Year|Date|Period|Time)[:\s]+", "", text, flags=re.IGNORECASE).strip()
    m = re.search(r"\b((?:19|20)\d{2})[./-]([01]?\d)\b", text)
    if m: return f"{m.group(1)}-{int(m.group(2)):02d}"
    m = re.search(r"\b([01]?\d)[./-]((?:19|20)\d{2})\b", text)
    if m: return f"{m.group(2)}-{int(m.group(1)):02d}"
    m = re.search(r"\b([A-Za-z]{3,9})[.,\s]+((?:19|20)\d{2})\b", text)
    if m:
        mon_str = m.group(1).lower().rstrip(".")
        month = month_map.get(mon_str)
        if not month:
            for k,v in month_map.items():
                if k.startswith(mon_str[:3]): month = v; break
        if month: return f"{m.group(2)}-{month}"
    m = re.search(r"\b([A-Za-z]{3,9})['\s]+(\d{2})\b", text)
    if m:
        mon_str = m.group(1).lower().rstrip(".")
        month = month_map.get(mon_str)
        if not month:
            for k,v in month_map.items():
                if k.startswith(mon_str[:3]): month = v; break
        if month: 
            y = int(m.group(2))
            fy = 2000 + y if y < 50 else 1900 + y
            return f"{fy}-{month}"
    year = _extract_year(text)
    return f"{year}-{default_month}" if year else None

def get_key(obj: dict, keys: List[str]) -> Any:
    for k in keys:
        if k in obj: return obj[k]
    obj_lower = {k.lower().replace("_", "").replace(" ", ""): v for k, v in obj.items()}
    for k in keys:
        k_norm = k.lower().replace("_", "").replace(" ", "")
        if k_norm in obj_lower:
            return obj_lower[k_norm]
    return None

def _parse_date_range(value: Any) -> Dict[str, Any]:
    text = _as_str(value)
    if not text: return {"start_date": None, "end_date": None, "is_current": False}
    parts = re.split(r"\s*(?:-|–|—|to|until|through)\s*", text, maxsplit=1, flags=re.IGNORECASE)
    start_raw = parts[0] if parts else ""
    end_raw = parts[1] if len(parts) > 1 else ""
    start_date = _normalize_month_year(start_raw, "01")
    end_date = _normalize_month_year(end_raw, "12") if end_raw else None
    is_current = "present" in text.lower() or "current" in text.lower()
    return {"start_date": start_date, "end_date": end_date, "is_current": is_current}


# Test inputs 
test_cases = [
    {"input": {"startDate": "Feb 2026", "end": "Present"}, "desc": "camelCase field names"},
    {"input": {"Start Date": "02-2026"}, "desc": "Title Case with space"},
    {"input": {"graduation_year": "2027-05"}, "desc": "Year as full YYYY-MM"},
    {"input": {"company": "ALKF+, Hong Kong"}, "desc": "Merged company/location"},
    {"input": {"duration": "Aug 2023 - May 2027"}, "desc": "Duration string fallback"}
]

print("--- Bulletproof Parser Verification (V2) ---")
for tc in test_cases:
    obj = tc["input"]
    range_info = _parse_date_range(get_key(obj, ["date_range", "duration", "date"]))
    s = _normalize_month_year(get_key(obj, ["start_date", "start", "from"]), "01") or range_info["start_date"]
    e = _normalize_month_year(get_key(obj, ["end_date", "end", "to"]), "12") or range_info["end_date"]
    y = _extract_year(get_key(obj, ["graduation_year", "year", "end_date"]))
    
    company_raw = get_key(obj, ["company"]) or ""
    company, location = company_raw, ""
    if "," in company_raw:
        parts = company_raw.split(",", 1)
        company, location = parts[0], parts[1].strip()
    
    print(f"Case: {tc['desc']}")
    print(f"  Parsed -> Start: {s}, End: {e}, Year: {y}, Location: {location}")
    print("-" * 20)
