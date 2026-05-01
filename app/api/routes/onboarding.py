"""
app/api/routes/onboarding.py
────────────────────────────
API routes for user onboarding.
Step-by-step profile collection and onboarding flow.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional
import tempfile
import os
import re

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
import structlog

from app.core.config import settings
from app.core.database import get_db_context
from app.models.user import User
from app.services.onboarding_service import OnboardingService, OnboardingStep
from app.services.resume_parser import get_resume_parser

router = APIRouter(prefix="/v1/onboarding", tags=["onboarding"])
logger = structlog.get_logger()


# ── Request Models ────────────────────────────────────────────────

class BasicInfoUpdate(BaseModel):
    """Step 1: Basic personal information."""
    full_name: str = Field(..., min_length=1, max_length=255)
    professional_summary:Optional[str] = None
    career_goals:Optional[str] = None
    unique_value_proposition:Optional[str] = None


class ContactInfoUpdate(BaseModel):
    """Step 2: Contact information."""
    phone:Optional[str] = None
    location:Optional[str] = None
    linkedin_url:Optional[str] = None
    github_url:Optional[str] = None
    portfolio_url:Optional[str] = None
    notification_email:Optional[str] = None


class EducationEntry(BaseModel):
    """Single education entry."""
    degree: str = Field(..., description="Degree (e.g., B.Tech, M.S., PhD)")
    field: str = Field(..., description="Field of study (e.g., Computer Science)")
    institution: str = Field(..., description="University/College name")
    year:Optional[int] = Field(None, description="Graduation year")
    gpa:Optional[float] = Field(None, description="GPA (0-10 scale)")
    description:Optional[str] = None


class EducationUpdate(BaseModel):
    """Step 3: Education history."""
    education: List[EducationEntry] = Field(default_factory=list)


class WorkExperienceEntry(BaseModel):
    """Single work experience entry."""
    title: str = Field(..., description="Job title")
    company: str = Field(..., description="Company name")
    start_date: str = Field(..., description="Start date (YYYY-MM)")
    end_date:Optional[str] = Field(None, description="End date (YYYY-MM)")
    is_current: bool = Field(False, description="Currently working here")
    description:Optional[str] = None
    bullets: List[str] = Field(default_factory=list, description="Key achievements")


class WorkExperienceUpdate(BaseModel):
    """Step 4: Work experience."""
    experience: List[WorkExperienceEntry] = Field(default_factory=list)


class SkillEntry(BaseModel):
    """Single skill entry."""
    name: str = Field(..., description="Skill name")
    category:Optional[str] = Field(None, description="Category: programming, ml_framework, cloud, tool, soft_skill")
    proficiency:Optional[str] = Field(None, description="beginner, intermediate, advanced, expert")
    years_experience:Optional[float] = None
    is_primary: bool = Field(False, description="Primary skill for job matching")


class SkillsUpdate(BaseModel):
    """Step 5: Skills."""
    skills: List[SkillEntry] = Field(default_factory=list)


class ResumeSelect(BaseModel):
    """Step 6: Select primary resume."""
    resume_id: str = Field(..., description="Resume ID to set as primary")


class JobPreferencesUpdate(BaseModel):
    """Step 7: Job search preferences."""
    experience_level:Optional[str] = Field(None, description="entry, mid, senior")
    desired_roles: List[str] = Field(default_factory=list, description="Target job titles")
    desired_locations: List[str] = Field(default_factory=list, description="Preferred cities/countries")
    open_to_remote: bool = True
    open_to_hybrid: bool = True
    min_salary: int = Field(0, description="Minimum salary expectation")
    preferred_company_size: List[str] = Field(default_factory=list, description="startup, mid, large, enterprise")
    preferred_industries: List[str] = Field(default_factory=list)
    avoid_companies: List[str] = Field(default_factory=list)


class PlatformSetupUpdate(BaseModel):
    """Step 8: Platform and notification settings."""
    auto_apply_enabled:Optional[bool] = None
    auto_apply_threshold:Optional[int] = Field(None, ge=0, le=100)
    auto_apply_daily_limit:Optional[int] = Field(None, ge=1, le=100)
    require_apply_approval:Optional[bool] = None
    notify_new_jobs:Optional[bool] = None
    notify_applications:Optional[bool] = None
    notify_interviews:Optional[bool] = None
    notify_via_telegram:Optional[bool] = None
    notify_via_email:Optional[bool] = None
    telegram_chat_id:Optional[str] = None


# ── Dependencies ─────────────────────────────────────────────────

# FIXED: Use proper JWT auth instead of returning first user
from app.api.routes.auth import get_current_user


async def get_onboarding_service(user: User = Depends(get_current_user)) -> OnboardingService:
    """Get onboarding service instance."""
    async with get_db_context() as db:
        return OnboardingService(db, user)


# ── Routes ────────────────────────────────────────────────────────

@router.get("/status")
async def get_onboarding_status(
    service: OnboardingService = Depends(get_onboarding_service)
) -> Dict[str, Any]:
    """
    Get current onboarding status and progress.
    
    Returns:
        - completed_steps: List of completed onboarding steps
        - current_step: Next step to complete
        - progress_percentage: Overall progress (0-100)
        - profile: Summary of profile data
    """
    return await service.get_onboarding_status()


@router.post("/basic-info")
async def update_basic_info(
    data: BasicInfoUpdate,
    service: OnboardingService = Depends(get_onboarding_service)
) -> Dict[str, Any]:
    """Step 1: Update basic personal information."""
    return await service.update_basic_info(data.model_dump(exclude_none=True))


@router.post("/contact-info")
async def update_contact_info(
    data: ContactInfoUpdate,
    service: OnboardingService = Depends(get_onboarding_service)
) -> Dict[str, Any]:
    """Step 2: Update contact information."""
    return await service.update_contact_info(data.model_dump(exclude_none=True))


@router.post("/education")
async def update_education(
    data: EducationUpdate,
    service: OnboardingService = Depends(get_onboarding_service)
) -> Dict[str, Any]:
    """Step 3: Update education history."""
    return await service.update_education([e.model_dump() for e in data.education])


@router.post("/work-experience")
async def update_work_experience(
    data: WorkExperienceUpdate,
    service: OnboardingService = Depends(get_onboarding_service)
) -> Dict[str, Any]:
    """Step 4: Update work experience."""
    return await service.update_work_experience([e.model_dump() for e in data.experience])


@router.post("/skills")
async def update_skills(
    data: SkillsUpdate,
    service: OnboardingService = Depends(get_onboarding_service)
) -> Dict[str, Any]:
    """Step 5: Update skills."""
    return await service.update_skills([s.model_dump() for s in data.skills])


@router.post("/resume")
async def set_primary_resume(
    data: ResumeSelect,
    service: OnboardingService = Depends(get_onboarding_service)
) -> Dict[str, Any]:
    """Step 6: Set primary resume."""
    return await service.set_primary_resume(data.resume_id)


@router.post("/resume/parse")
async def parse_resume(
    file: UploadFile = File(..., description="Resume PDF file"),
    user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Parse resume PDF to extract structured data.
    Returns: name, email, phone, education, experience, skills, etc.
    User can then edit these fields before submitting.
    """
    # Validate file type
    if not file.filename or not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")
    
    if file.size and file.size > 10 * 1024 * 1024:  # 10MB
        raise HTTPException(status_code=400, detail="File size must be less than 10MB")
    
    try:
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
            contents = await file.read()
            temp_file.write(contents)
            temp_path = temp_file.name
        
        try:
            # Parse the resume
            parser = get_resume_parser()
            result = await parser.parse_pdf(temp_path)
            
            return result
        finally:
            # Clean up temp file
            if os.path.exists(temp_path):
                os.unlink(temp_path)
                
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to parse resume: {str(e)}")


@router.post("/resume/parse-and-fill")
async def parse_and_fill_profile(
    file: UploadFile = File(..., description="Resume PDF file"),
    service: OnboardingService = Depends(get_onboarding_service)
) -> Dict[str, Any]:
    """
    Parse resume and automatically fill profile fields.
    This endpoint combines parsing + profile update in one call.
    """
    # Validate file type
    if not file.filename or not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")
    
    if file.size and file.size > 10 * 1024 * 1024:  # 10MB
        raise HTTPException(status_code=400, detail="File size must be less than 10MB")
    
    try:
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
            contents = await file.read()
            temp_file.write(contents)
            temp_path = temp_file.name
        
        try:
            # Parse the resume
            parser = get_resume_parser()
            parse_result = await parser.parse_pdf(temp_path)
            
            if not parse_result.get("success"):
                raise HTTPException(status_code=400, detail=parse_result.get("error", "Failed to parse resume"))
            
            parsed_data = parse_result.get("data", {})
            
            # Auto-fill profile fields
            results = {}
            section_errors: Dict[str, str] = {}

            def _as_str(value: Any) -> str:
                return value.strip() if isinstance(value, str) else ""

            def _as_float(value: Any) -> Optional[float]:
                if value is None or value == "":
                    return None
                try:
                    return float(value)
                except (TypeError, ValueError):
                    return None

            def _as_list_of_str(value: Any) -> List[str]:
                if isinstance(value, list):
                    return [str(v).strip() for v in value if str(v).strip()]
                if isinstance(value, str):
                    parts = [p.strip() for p in value.replace("|", ",").replace(";", ",").split(",")]
                    return [p for p in parts if p]
                return []

            def _iter_items(value: Any) -> List[Any]:
                if value is None:
                    return []
                if isinstance(value, list):
                    return value
                if isinstance(value, dict):
                    return [value]
                if isinstance(value, str):
                    return [value]
                return []

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

            def _normalize_month_year(value: Any, default_month: str = "01") -> Optional[str]:
                text = _as_str(value)
                if not text:
                    return None

                lowered = text.lower().strip().strip(". \t\n")
                if lowered in {"present", "current", "ongoing", "now", "till date", "to date", "still"}:
                    return None

                # Clean up some common noise like "Year: ", "Date: ", etc.
                text = re.sub(r"^(?:Year|Date|Period|Time)[:\s]+", "", text, flags=re.IGNORECASE).strip()

                # 1. YYYY-MM or YYYY/MM
                m = re.search(r"\b((?:19|20)\d{2})[./-]([01]?\d)\b", text)
                if m:
                    month = int(m.group(2))
                    if 1 <= month <= 12:
                        return f"{m.group(1)}-{month:02d}"

                # 2. MM/YYYY or MM-YYYY
                m = re.search(r"\b([01]?\d)[./-]((?:19|20)\d{2})\b", text)
                if m:
                    month = int(m.group(1))
                    if 1 <= month <= 12:
                        return f"{m.group(2)}-{month:02d}"

                # 3. Month YYYY (e.g., January 2024, Jan. 2024, Aug 2023)
                m = re.search(r"\b([A-Za-z]{3,9})[.,\s]+((?:19|20)\d{2})\b", text)
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
                
                # 4. MMM YY or MMM'YY (e.g. Feb'26, Feb 26)
                m = re.search(r"\b([A-Za-z]{3,9})['\s]+(\d{2})\b", text)
                if m:
                    mon_str = m.group(1).lower().rstrip(".")
                    month = month_map.get(mon_str)
                    if not month and len(mon_str) >= 3:
                        for k, v in month_map.items():
                            if k.startswith(mon_str[:3]):
                                month = v
                                break
                    if month:
                        year = int(m.group(2))
                        full_year = 2000 + year if year < 50 else 1900 + year
                        return f"{full_year}-{month}"

                # Fallback to year extraction
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

            def _split_skill_text(text: str) -> List[str]:
                if not text:
                    return []

                # Handle categorized skills like "Programming: Python, C++ | ML: TensorFlow, Torch"
                # Split by major separators first
                raw_chunks = re.split(r"[\n;|•]+", text)
                tokens: List[str] = []
                for chunk in raw_chunks:
                    chunk = chunk.strip()
                    if not chunk:
                        continue

                    # Handle colons aggressively: "Programming: Python" -> ["Programming", "Python"]
                    # If multiple colons, split them all out
                    if ":" in chunk:
                        subparts = [p.strip() for p in re.split(r":", chunk) if p.strip()]
                        # Process each subpart as if it was a chunk
                        for subpart in subparts:
                            # Further split by comma
                            for piece in re.split(r",", subpart):
                                p = piece.strip(" .-\t\n")
                                if not p:
                                    continue
                                # Remove common level-indicators
                                p = re.sub(r"\s*[(\[]?\b(beginner|intermediate|advanced|expert|proficient|expertly)\b[)\]]?\s*", "", p, flags=re.IGNORECASE).strip()
                                # Clean up hanging parentheses/brackets
                                p = p.replace("()", "").replace("[]", "").strip(" .-\t\n")
                                # Clean up multiple spaces
                                p = re.sub(r"\s+", " ", p)
                                if p and len(p) > 1:
                                    tokens.append(p)
                        continue

                    # Regular chunk (no colon) - split by comma
                    for piece in re.split(r",", chunk):
                        p = piece.strip(" .-\t\n")
                        if not p:
                            continue
                        p = re.sub(r"\s*[(\[]?\b(beginner|intermediate|advanced|expert|proficient|expertly)\b[)\]]?\s*", "", p, flags=re.IGNORECASE).strip()
                        p = p.replace("()", "").replace("[]", "").strip(" .-\t\n")
                        p = re.sub(r"\s+", " ", p)
                        if p and len(p) > 1:
                            tokens.append(p)

                # Deduplicate
                deduped: List[str] = []
                seen: set[str] = set()
                for token in tokens:
                    key = token.lower()
                    if key in seen:
                        continue
                    seen.add(key)
                    deduped.append(token)

                return deduped

            def _normalize_education_item(item: Any) -> Optional[Dict[str, Any]]:
                if isinstance(item, str):
                    text = item.strip()
                    if not text:
                        return None
                    year_value = _extract_year(text)
                    parts = [p.strip() for p in re.split(r"\s*[|,]\s*", text) if p.strip()]
                    degree = parts[0] if parts else text
                    institution = ""
                    for part in parts[1:]:
                        if re.search(r"university|college|institute|school|academy|polytechnic|iit|nit|srm|technology", part, re.IGNORECASE):
                            institution = part
                            break
                    if not institution and len(parts) > 1:
                        institution = parts[1]
                    if not institution:
                        return None
                    return {
                        "degree": degree,
                        "field": "",
                        "institution": institution,
                        "year": year_value,
                        "gpa": None,
                        "description": "",
                    }

                if isinstance(item, dict):
                    # Robust Key Fallbacks
                    def get_key(obj: dict, keys: List[str]) -> Any:
                        for k in keys:
                            if k in obj: return obj[k]
                            # Try camelCase and Title Case transformations
                            k_cc = k.replace("_", "")
                            if k_cc in obj: return obj[k_cc]
                            k_tc = k.replace("_", " ").title()
                            if k_tc in obj: return obj[k_tc]
                        return None

                    degree = _as_str(get_key(item, ["degree", "qualification", "program", "course"]))
                    field = _as_str(get_key(item, ["field", "major", "specialization", "branch", "subject"]))
                    institution = _as_str(get_key(item, ["institution", "university", "college", "school", "campus"]))
                    
                    # Year/Date fallbacks
                    year_raw = get_key(item, ["end_date", "grad_year", "graduation_year", "year", "passout_year", "date"])
                    year_value = _extract_year(year_raw)

                    # GPA fallbacks
                    gpa_val = get_key(item, ["gpa", "cgpa", "grade", "marks", "percentage", "score"])
                    
                    # Handle merged strings
                    merged_text = _as_str(get_key(item, ["name", "education", "text", "summary"]))
                    if merged_text:
                        if not degree: degree = merged_text
                        if not institution:
                            parts = [p.strip() for p in re.split(r"\s*[|,]\s*", merged_text) if p.strip()]
                            for part in parts:
                                if re.search(r"university|college|institute|school|academy|polytechnic|iit|nit|srm|technology", part, re.IGNORECASE):
                                    institution = part; break
                        if not year_value: year_value = _extract_year(merged_text)
                        if not gpa_val:
                            m = re.search(r"(?:CGPA|GPA|Grade)[:\s]+([0-9.]+|[A-O][+-]?)", merged_text, re.IGNORECASE)
                            if m: gpa_val = m.group(1)

                    if not degree or not institution:
                        return None

                    return {
                        "degree": degree,
                        "field": field,
                        "institution": institution,
                        "year": year_value,
                        "gpa": _as_float(gpa_val) if re.match(r"^[0-9.]+$", str(gpa_val or "")) else None,
                        "description": _as_str(get_key(item, ["description", "summary", "details"]) or (f"Grade: {gpa_val}" if not re.match(r"^[0-9.]+$", str(gpa_val or "")) and gpa_val else "")),
                    }

                return None

            def _normalize_skill_item(item: Any) -> Optional[Dict[str, Any]]:
                if isinstance(item, str):
                    name = item.strip()
                    if not name:
                        return None
                    return {
                        "name": name,
                        "category": None,
                        "proficiency": "intermediate",
                        "years_experience": None,
                        "is_primary": False,
                    }

                if isinstance(item, dict):
                    name = _as_str(item.get("name") or item.get("skill") or item.get("technology"))
                    if not name:
                        return None
                    proficiency = _as_str(item.get("proficiency") or item.get("level")).lower() or "intermediate"
                    allowed_proficiency = {"beginner", "intermediate", "advanced", "expert"}
                    if proficiency not in allowed_proficiency:
                        proficiency = "intermediate"
                    return {
                        "name": name,
                        "category": _as_str(item.get("category") or item.get("type")) or None,
                        "proficiency": proficiency,
                        "years_experience": _as_float(item.get("years_experience") or item.get("years") or item.get("experience_years")),
                        "is_primary": False,
                    }

                return None

            def _normalize_experience_item(item: Any) -> Optional[Dict[str, Any]]:
                if isinstance(item, str):
                    text = item.strip()
                    if not text:
                        return None
                    return {
                        "title": text,
                        "company": "Unknown",
                        "start_date": "",
                        "end_date": None,
                        "description": "",
                        "is_current": False,
                        "bullets": [],
                    }

                if isinstance(item, dict):
                    # Robust Case-Insensitive Key Fallbacks
                    def get_key(obj: dict, keys: List[str]) -> Any:
                        # 1. Exact match first
                        for k in keys:
                            if k in obj: return obj[k]
                        
                        # 2. Case-insensitive and variation match
                        obj_lower = {k.lower().replace("_", "").replace(" ", ""): v for k, v in obj.items()}
                        for k in keys:
                            k_norm = k.lower().replace("_", "").replace(" ", "")
                            if k_norm in obj_lower:
                                return obj_lower[k_norm]
                        return None

                    title = _as_str(get_key(item, ["title", "role", "position", "designation", "job_title"]))
                    company = _as_str(get_key(item, ["company", "organization", "employer", "firm"]))
                    location = _as_str(get_key(item, ["location", "city", "address", "place"]))
                    
                    if not title:
                        return None
                    if not company:
                        company = "Unknown"
                    
                    # Extract location from company if needed (e.g. "ALKF+, Hong Kong")
                    if not location and ("," in company or "|" in company):
                        sep = "," if "," in company else "|"
                        parts = [p.strip() for p in company.split(sep, 1)]
                        if len(parts) > 1:
                            company = parts[0]
                            location = parts[1]

                    range_info = _parse_date_range(get_key(item, ["date_range", "duration", "period", "dates", "time", "date"]))
                    start_date = _normalize_month_year(get_key(item, ["start_date", "start", "from", "started"]), "01") or range_info["start_date"] or ""
                    end_date = _normalize_month_year(get_key(item, ["end_date", "end", "to", "until", "finished"]), "12")
                    end_date = end_date or range_info["end_date"]

                    is_current = get_key(item, ["is_current", "current"]) or (get_key(item, ["end_date", "end"]) or "").lower() == "present" or range_info["is_current"]
                    bullets_raw = get_key(item, ["highlights", "bullets", "responsibilities", "tasks", "achievements"]) or []
                    bullets = []
                    if isinstance(bullets_raw, str):
                        bullets = [p.strip() for p in bullets_raw.split("\n") if p.strip()]
                    else:
                        bullets = _iter_items(bullets_raw)

                    return {
                        "title": title,
                        "company": company,
                        "location": location,
                        "start_date": start_date,
                        "end_date": None if is_current else end_date,
                        "description": _as_str(get_key(item, ["description", "summary", "details"])),
                        "is_current": is_current,
                        "bullets": bullets,
                    }

                return None
            
            # Update basic info
            try:
                if parsed_data.get("name"):
                    basic_payload = {
                        "full_name": _as_str(parsed_data.get("name")),
                        "professional_summary": _as_str(parsed_data.get("professional_summary")) or None,
                        "career_goals": _as_str(parsed_data.get("career_goals")) or None,
                        "unique_value_proposition": _as_str(parsed_data.get("unique_value_proposition")) or None,
                    }
                    results["basic_info"] = await service.update_basic_info(
                        {k: v for k, v in basic_payload.items() if v is not None and v != ""}
                    )
            except Exception as e:
                section_errors["basic_info"] = str(e)
            
            # Update contact info
            try:
                contact_fields = {
                    "phone": _as_str(parsed_data.get("phone")) or None,
                    "location": _as_str(parsed_data.get("location")) or None,
                    "linkedin_url": _as_str(parsed_data.get("linkedin_url")) or None,
                    "github_url": _as_str(parsed_data.get("github_url")) or None,
                    "portfolio_url": _as_str(parsed_data.get("portfolio_url")) or None,
                }
                contact_payload = {k: v for k, v in contact_fields.items() if v}
                if contact_payload:
                    results["contact_info"] = await service.update_contact_info(contact_payload)
            except Exception as e:
                section_errors["contact_info"] = str(e)
            
            # Update education
            try:
                if parsed_data.get("education"):
                    education_entries = []
                    for edu in _iter_items(parsed_data["education"]):
                        normalized = _normalize_education_item(edu)
                        if normalized:
                            education_entries.append(normalized)
                    if education_entries:
                        results["education"] = await service.update_education(education_entries)
            except Exception as e:
                section_errors["education"] = str(e)
            
            # Update work experience
            try:
                raw_experience = (
                    parsed_data.get("work_experience")
                    or parsed_data.get("experience")
                    or parsed_data.get("professional_experience")
                )
                if raw_experience:
                    work_entries = []
                    for exp in _iter_items(raw_experience):
                        normalized = _normalize_experience_item(exp)
                        if normalized:
                            work_entries.append(normalized)
                    if work_entries:
                        results["work_experience"] = await service.update_work_experience(work_entries)
            except Exception as e:
                section_errors["work_experience"] = str(e)
            
            # Update skills
            try:
                raw_skills = (
                    parsed_data.get("skills")
                    or parsed_data.get("technical_skills")
                    or parsed_data.get("core_skills")
                )
                if raw_skills:
                    skill_entries = []
                    for skill in _iter_items(raw_skills):
                        if isinstance(skill, str):
                            for token in _split_skill_text(skill):
                                normalized = _normalize_skill_item(token)
                                if normalized:
                                    skill_entries.append(normalized)
                            continue

                        normalized = _normalize_skill_item(skill)
                        if normalized:
                            split_names = _split_skill_text(normalized["name"])
                            if len(split_names) > 1:
                                for name in split_names:
                                    skill_entries.append({
                                        **normalized,
                                        "name": name,
                                    })
                            else:
                                skill_entries.append(normalized)

                    # Handle skills as single comma-separated string too
                    if isinstance(raw_skills, str):
                        for token in _split_skill_text(raw_skills):
                            normalized = _normalize_skill_item(token)
                            if normalized:
                                skill_entries.append(normalized)

                    # Deduplicate by lowercase name
                    deduped: Dict[str, Dict[str, Any]] = {}
                    for entry in skill_entries:
                        deduped[entry["name"].lower()] = entry
                    skill_entries = list(deduped.values())

                    if skill_entries:
                        results["skills"] = await service.update_skills(skill_entries)
            except Exception as e:
                section_errors["skills"] = str(e)

            # Update projects
            try:
                if parsed_data.get("projects"):
                    project_entries = []
                    for prj in _iter_items(parsed_data["projects"]):
                        if isinstance(prj, str): continue
                        name = _as_str(prj.get("title") or prj.get("name"))
                        if name:
                            project_entries.append({
                                "title": name,
                                "description": _as_str(prj.get("description") or prj.get("summary")),
                                "link": _as_str(prj.get("link") or prj.get("url") or prj.get("github_url")),
                                "date": _normalize_month_year(prj.get("date"), "01"),
                            })
                    if project_entries:
                        # Assuming service has a way to update projects
                        if hasattr(service, "update_projects"):
                            results["projects"] = await service.update_projects(project_entries)
            except Exception as e:
                section_errors["projects"] = str(e)

            # Update awards
            try:
                if parsed_data.get("awards"):
                    award_entries = []
                    for awd in _iter_items(parsed_data["awards"]):
                        if isinstance(awd, str): continue
                        name = _as_str(awd.get("title") or awd.get("name"))
                        if name:
                            award_entries.append({
                                "title": name,
                                "date": _normalize_month_year(awd.get("date"), "01"),
                                "description": _as_str(awd.get("description") or awd.get("summary")),
                            })
                    if award_entries:
                        if hasattr(service, "update_awards"):
                            results["awards"] = await service.update_awards(award_entries)
            except Exception as e:
                section_errors["awards"] = str(e)

            if section_errors:
                logger.warning("resume_parse_and_fill_partial", user_id=str(service.user.id), section_errors=section_errors)
            
            return {
                "status": "success" if not section_errors else "partial_success",
                "message": "Resume parsed and profile auto-filled",
                "parsed_data": parsed_data,
                "updated_sections": list(results.keys()),
                "update_results": results,
                "section_errors": section_errors,
            }
            
        finally:
            # Clean up temp file
            if os.path.exists(temp_path):
                os.unlink(temp_path)
                
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to parse and fill resume: {str(e)}")


@router.post("/job-preferences")
async def update_job_preferences(
    data: JobPreferencesUpdate,
    service: OnboardingService = Depends(get_onboarding_service)
) -> Dict[str, Any]:
    """Step 7: Update job search preferences."""
    return await service.update_job_preferences(data.model_dump(exclude_none=True))


@router.post("/platform-setup")
async def update_platform_setup(
    data: PlatformSetupUpdate,
    service: OnboardingService = Depends(get_onboarding_service)
) -> Dict[str, Any]:
    """Step 8: Update platform and notification settings."""
    return await service.update_platform_setup(data.model_dump(exclude_none=True))


@router.post("/complete")
async def complete_onboarding(
    service: OnboardingService = Depends(get_onboarding_service)
) -> Dict[str, Any]:
    """Complete the onboarding process."""
    return await service.complete_onboarding()


# ── Bulk Update ─────────────────────────────────────────────────

class CompleteProfileUpdate(BaseModel):
    """Complete profile update in one call."""
    basic_info:Optional[BasicInfoUpdate] = None
    contact_info:Optional[ContactInfoUpdate] = None
    education:Optional[List[EducationEntry]] = None
    work_experience:Optional[List[WorkExperienceEntry]] = None
    skills:Optional[List[SkillEntry]] = None
    resume_id:Optional[str] = None
    job_preferences:Optional[JobPreferencesUpdate] = None
    platform_setup:Optional[PlatformSetupUpdate] = None


@router.post("/complete-profile")
async def update_complete_profile(
    data: CompleteProfileUpdate,
    service: OnboardingService = Depends(get_onboarding_service)
) -> Dict[str, Any]:
    """Update complete profile in one call (for power users)."""
    results = {}
    
    if data.basic_info:
        results["basic_info"] = await service.update_basic_info(
            data.basic_info.model_dump(exclude_none=True)
        )
    
    if data.contact_info:
        results["contact_info"] = await service.update_contact_info(
            data.contact_info.model_dump(exclude_none=True)
        )
    
    if data.education:
        results["education"] = await service.update_education(
            [e.model_dump() for e in data.education]
        )
    
    if data.work_experience:
        results["work_experience"] = await service.update_work_experience(
            [e.model_dump() for e in data.work_experience]
        )
    
    if data.skills:
        results["skills"] = await service.update_skills(
            [s.model_dump() for s in data.skills]
        )
    
    if data.resume_id:
        results["resume"] = await service.set_primary_resume(data.resume_id)
    
    if data.job_preferences:
        results["job_preferences"] = await service.update_job_preferences(
            data.job_preferences.model_dump(exclude_none=True)
        )
    
    if data.platform_setup:
        results["platform_setup"] = await service.update_platform_setup(
            data.platform_setup.model_dump(exclude_none=True)
        )
    
    return {
        "status": "success",
        "message": "Profile updated successfully",
        "completed_sections": list(results.keys())
    }
