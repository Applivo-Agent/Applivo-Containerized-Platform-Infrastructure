"""
app/agents/apply_bot_internshala.py

FIXES in this version vs document-6:
  1. _get_form_errors: Python adjacent string literals inside JS caused
     "SyntaxError: Unexpected string" — collapsed to a single string.
  2. _fill_all_fields text inputs: inp.fill() requires element to be visible
     and times out 30 s on hidden fields (e.g. id=link).  Switched to JS
     direct value assignment so hidden fields are set without a timeout.
  3. _check_submission_result: after a successful AJAX submit Internshala
     sometimes opens a NEW confirmation modal (.modal.show) — so the old
     "wait for modal to disappear" check saw it and returned None, causing
     the crash path to run.  Now also checks for success text INSIDE the
     modal before declaring failure.
"""

from __future__ import annotations

import asyncio
import hashlib
import json
import random
import re
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import structlog

logger = structlog.get_logger()

# Paths resolved from centralized settings — avoids CWD-dependent bugs (Fix #4)
from app.core.config import settings as _path_settings
COOKIE_FILE = _path_settings.storage_path / "internshala_cookies.json"
SCREENSHOT_DIR = _path_settings.storage_path / "screenshots"
ANSWER_CACHE_FILE = _path_settings.storage_path / "internshala_answer_cache.json"

BAD_PATTERNS = (
    "we are excited",
    "our company",
    "our organization",
    "dear hiring manager",
    "as a company",
    "[your_email@example.com]",
    "your_email@example.com",
    "we invite candidates",
)

IDENTITY_FIELD_KEYS = (
    ("first name", "first_name"),
    ("firstname", "first_name"),
    ("given name", "first_name"),
    ("last name", "last_name"),
    ("lastname", "last_name"),
    ("surname", "last_name"),
    ("family name", "last_name"),
    ("full name", "full_name"),
    ("name", "full_name"),
    ("email", "email"),
    ("phone", "phone"),
    ("mobile", "phone"),
    ("linkedin", "linkedin_url"),
    ("github", "github_url"),
    ("portfolio", "portfolio_url"),
    ("college", "college"),
    ("university", "college"),
    ("school", "college"),
    ("city", "city"),
    ("location", "city"),
)


def _normalize_text(value: Any) -> str:
    return re.sub(r"\s+", " ", str(value or "")).strip()


def _truncate(value: Any, limit: int = 140) -> str:
    text = _normalize_text(value)
    return text if len(text) <= limit else text[: limit - 1].rstrip() + "…"


def _profile_name(profile: Any, user_full_name: Optional[str] = None) -> str:
    candidates = [
        user_full_name,
        getattr(profile, "full_name", None),
        getattr(profile, "name", None),
    ]
    for candidate in candidates:
        cleaned = _normalize_text(candidate)
        if cleaned:
            return cleaned

    first = _normalize_text(getattr(profile, "first_name", ""))
    last = _normalize_text(getattr(profile, "last_name", ""))
    combined = _normalize_text(f"{first} {last}")
    return combined or "Candidate"


def _safe_attr(profile: Any, *names: str, default: str = "") -> str:
    for name in names:
        value = getattr(profile, name, None)
        cleaned = _normalize_text(value)
        if cleaned:
            return cleaned
    return default


def _configured_account_email(settings_obj: Any) -> str:
    """Return the best configured account email for Internshala flows.

    Prefer the site-specific login email, but fall back to the generic user
    email if that is the only populated value. Placeholder values are ignored.
    """
    placeholder_values = {
        "",
        "your_email@example.com",
        "[your_email@example.com]",
    }
    for attr in ("INTERNShALA_EMAIL", "USER_EMAIL"):
        cleaned = _safe_attr(settings_obj, attr, default="")
        if cleaned and cleaned.lower() not in placeholder_values:
            return cleaned
    return _safe_attr(settings_obj, "INTERNShALA_EMAIL", "USER_EMAIL", default="")


def _extract_sequence_text(items: Any, limit: int = 5) -> List[str]:
    results: List[str] = []
    if not items:
        return results
    for item in list(items)[:limit]:
        if isinstance(item, str):
            cleaned = _normalize_text(item)
            if cleaned:
                results.append(cleaned)
            continue
        if isinstance(item, dict):
            pieces = []
            for key in ("name", "title", "institution", "company", "degree", "field", "description", "summary"):
                if item.get(key):
                    pieces.append(_normalize_text(item.get(key)))
            tech = item.get("tech_stack") or item.get("skills") or item.get("bullets")
            if isinstance(tech, list):
                pieces.extend(_normalize_text(t) for t in tech[:5] if _normalize_text(t))
            text = _normalize_text(" | ".join(pieces))
            if text:
                results.append(text)
    return results


def _resume_text(resume: Any) -> str:
    if not resume:
        return ""
    pieces: List[str] = []
    for attr in ("content_markdown", "content_text"):
        value = getattr(resume, attr, None)
        if value:
            pieces.append(_normalize_text(value))
    content_json = getattr(resume, "content_json", None)
    if isinstance(content_json, dict):
        pieces.append(_normalize_text(json.dumps(content_json, ensure_ascii=False)))
    elif isinstance(content_json, list):
        pieces.append(_normalize_text(json.dumps(content_json, ensure_ascii=False)))
    return "\n".join(pieces)


def _resume_chunks(text: str, chunk_size: int = 700) -> List[str]:
    cleaned = _normalize_text(text)
    if not cleaned:
        return []
    words = cleaned.split()
    chunks = []
    for start in range(0, len(words), chunk_size):
        chunk = " ".join(words[start:start + chunk_size]).strip()
        if chunk:
            chunks.append(chunk)
    return chunks[:8]


def _retrieve_relevant_chunks(question: str, candidate_context: Dict[str, Any], max_chunks: int = 3) -> List[str]:
    tokens = [token for token in re.findall(r"[a-z0-9+#.-]+", question.lower()) if len(token) > 2]
    sources: List[str] = []
    sources.extend(_extract_sequence_text(candidate_context.get("projects"), limit=8))
    sources.extend(_extract_sequence_text(candidate_context.get("experience"), limit=8))
    sources.extend(_extract_sequence_text(candidate_context.get("education"), limit=5))
    sources.extend(_extract_sequence_text(candidate_context.get("skills"), limit=12))
    sources.extend(_resume_chunks(candidate_context.get("resume_text", ""), chunk_size=180))

    scored: List[Tuple[int, str]] = []
    for source in sources:
        lower = source.lower()
        score = sum(1 for token in tokens if token in lower)
        if score:
            scored.append((score, source))

    if not scored:
        return sources[:max_chunks]

    scored.sort(key=lambda item: item[0], reverse=True)
    selected = []
    for _, chunk in scored:
        if chunk not in selected:
            selected.append(chunk)
        if len(selected) >= max_chunks:
            break
    return selected


def _build_candidate_context(profile: Any, resume: Any, job: Any, question: str = "") -> Dict[str, Any]:
    education = getattr(profile, "education", None) or []
    projects = getattr(profile, "projects", None) or []
    experience = getattr(profile, "work_experience", None) or []
    certifications = getattr(profile, "certifications", None) or []
    awards = getattr(profile, "awards", None) or []
    publications = getattr(profile, "publications", None) or []
    skills = []
    raw_skills = getattr(profile, "skills", None) or []
    for skill in raw_skills:
        if isinstance(skill, str):
            skills.append(skill)
        else:
            name = getattr(skill, "name", None) or (skill.get("name") if isinstance(skill, dict) else None)
            if name:
                skills.append(name)

    return {
        "name": _profile_name(profile),
        "location": _safe_attr(profile, "location", default=""),
        "education": education,
        "skills": skills,
        "projects": projects,
        "experience": experience,
        "certifications": certifications,
        "awards": awards,
        "publications": publications,
        "resume_text": _resume_text(resume),
        "job_title": getattr(job, "title", "") or "",
        "job_company": getattr(job, "company_name", "") or "",
        "job_description": (getattr(job, "description_clean", None) or getattr(job, "description_raw", None) or "")[:3500],
        "question": question,
    }


def _render_candidate_context(candidate_context: Dict[str, Any], relevant_chunks: List[str]) -> str:
    payload = dict(candidate_context)
    payload["relevant_resume_chunks"] = relevant_chunks
    return json.dumps(payload, ensure_ascii=False, indent=2, default=str)


def classify_question(question: str) -> str:
    q = _normalize_text(question).lower()
    if not q:
        return "generic"
    if "who can apply" in q or "eligible" in q or "eligibility" in q:
        return "eligibility"
    if "why should we hire" in q or "why hire" in q or "why should i hire" in q:
        return "why_hire_you"
    if "available" in q or "joining" in q or "notice period" in q or "immediately" in q:
        return "availability"
    if "salary" in q or "stipend" in q or "compensation" in q or "expected pay" in q:
        return "salary"
    if "relocat" in q or "move to" in q or "shift" in q:
        return "relocation"
    if "experience" in q or "worked on" in q or "background" in q or "internship" in q:
        return "experience"
    if "skill" in q or "technolog" in q or "tool" in q or "stack" in q:
        return "skills"
    if "project" in q or "built" in q or "portfolio" in q or "github" in q:
        return "project_based"
    if "education" in q or "college" in q or "university" in q or "school" in q or "degree" in q:
        return "education"
    if "ai" in q or "llm" in q or "machine learning" in q or "ml" in q:
        return "ai_knowledge"
    if any(word in q for word in ("strength", "tell us about yourself", "introduce yourself")):
        return "strengths"
    return "generic"


def _identity_field_value(label: str, profile: Any, user_full_name: Optional[str] = None, settings_obj: Any = None) -> Optional[str]:
    label_lower = _normalize_text(label).lower()
    if not label_lower:
        return None
    if "username" in label_lower:
        return None

    for key, attr in IDENTITY_FIELD_KEYS:
        if key in label_lower:
            if attr == "email":
                value = _configured_account_email(settings_obj) if settings_obj else ""
            elif attr == "phone":
                value = _safe_attr(profile, "phone", default="")
            elif attr == "full_name":
                value = _profile_name(profile, user_full_name=user_full_name)
            elif attr == "first_name":
                full_name = _profile_name(profile, user_full_name=user_full_name)
                value = full_name.split()[0] if full_name else ""
            elif attr == "last_name":
                full_name = _profile_name(profile, user_full_name=user_full_name)
                value = full_name.split()[-1] if full_name and len(full_name.split()) > 1 else ""
            elif attr == "college":
                education_text = _extract_sequence_text(getattr(profile, "education", None), limit=1)
                value = education_text[0] if education_text else ""
            elif attr == "city":
                value = _safe_attr(profile, "location", default="")
            else:
                value = _safe_attr(profile, attr, default="")

            cleaned = _normalize_text(value)
            if cleaned:
                return cleaned
    return None


def _question_cache_key(question: str, category: str, candidate_context: Dict[str, Any], options: List[str]) -> str:
    basis = json.dumps(
        {
            "question": _normalize_text(question).lower(),
            "category": category,
            "name": candidate_context.get("name", ""),
            "job_title": candidate_context.get("job_title", ""),
            "options": options,
            "projects": candidate_context.get("projects", []),
            "skills": candidate_context.get("skills", []),
        },
        sort_keys=True,
        default=str,
    )
    return hashlib.sha256(basis.encode("utf-8")).hexdigest()


def _load_answer_memory() -> Dict[str, Any]:
    try:
        if ANSWER_CACHE_FILE.exists():
            return json.loads(ANSWER_CACHE_FILE.read_text())
    except Exception as e:
        logger.warning("Could not load answer memory", error=str(e))
    return {}


def _save_answer_memory(memory: Dict[str, Any]) -> None:
    try:
        ANSWER_CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)
        # keep the cache small and recent
        if len(memory) > 250:
            items = list(memory.items())[-200:]
            memory = dict(items)
        ANSWER_CACHE_FILE.write_text(json.dumps(memory, indent=2, ensure_ascii=False))
    except Exception as e:
        logger.warning("Could not save answer memory", error=str(e))


def _validate_answer(answer: str, category: str, max_words: int = 120) -> Tuple[bool, str]:
    text = _normalize_text(answer)
    if not text:
        return False, "empty"
    lower = text.lower()
    if any(pattern in lower for pattern in BAD_PATTERNS):
        return False, "blacklisted_phrase"
    if "mailto:" in lower or re.search(r"\b\d{10,}\b", lower):
        return False, "looks_like_placeholder_or_phone"
    if lower.startswith("we ") or lower.startswith("our "):
        return False, "recruiter_voice"
    if category in ("availability", "salary") and len(text.split()) > 25:
        return False, "too_verbose_for_fact_field"
    if len(text.split()) > max_words:
        return False, "too_long"
    return True, "ok"


def _fallback_answer(category: str, candidate_context: Dict[str, Any], question: str) -> str:
    name = candidate_context.get("name", "I")
    skills = candidate_context.get("skills", []) or []
    projects = candidate_context.get("projects", []) or []
    project_names = []
    for project in projects:
        if isinstance(project, dict):
            project_names.append(_normalize_text(project.get("name") or project.get("title") or ""))
    project_names = [p for p in project_names if p][:3]
    skill_text = ", ".join(_normalize_text(s) for s in skills[:5] if _normalize_text(s))

    if category == "eligibility":
        return f"I am a motivated candidate with experience in {skill_text or 'relevant technical skills'} and projects like {', '.join(project_names) or 'my recent work'}."
    if category == "why_hire_you":
        return f"I bring hands-on experience in {skill_text or 'relevant tools'}, a strong learning mindset, and projects such as {', '.join(project_names) or 'my recent projects'} that align with this role."
    if category == "experience":
        return f"I have worked on projects such as {', '.join(project_names) or 'recent academic projects'} and used {skill_text or 'relevant technologies'} to build practical solutions."
    if category == "skills":
        return f"My core skills include {skill_text or 'relevant technical skills'} and I have applied them in projects like {', '.join(project_names) or 'my recent projects'}."
    if category == "availability":
        return "I am available as required and can join immediately if selected."
    if category == "salary":
        return "I am open to the internship's standard stipend range and value the learning opportunity."
    if category == "education":
        education = candidate_context.get("education", []) or []
        if education:
            edu = education[0] if isinstance(education[0], dict) else {}
            degree = _normalize_text(edu.get("degree") or edu.get("name") or "")
            institution = _normalize_text(edu.get("institution") or edu.get("college") or "")
            if degree or institution:
                return f"I am pursuing {degree or 'my degree'} at {institution or 'my institution'} and have focused on building practical technical skills alongside coursework."
        return "I am currently focused on my education while building practical technical skills through projects and hands-on learning."
    if category == "project_based":
        return f"My project work includes {', '.join(project_names) or 'recent technical projects'}, where I applied {skill_text or 'core technical skills'} to solve practical problems."
    if category == "ai_knowledge":
        return f"I have practical exposure to {skill_text or 'AI/ML tools'} through projects such as {', '.join(project_names) or 'recent AI projects'}."
    return f"I am a motivated candidate with hands-on experience in {skill_text or 'relevant technical skills'} and projects like {', '.join(project_names) or 'my recent work'}."


async def _generate_candidate_answer(
    question: str,
    options: List[str],
    profile: Any,
    resume: Any,
    job: Any,
    settings_obj: Any,
    user_id: Optional[str] = None,
    user_full_name: Optional[str] = None,
) -> str:
    category = classify_question(question)
    candidate_context = _build_candidate_context(profile, resume, job, question=question)
    relevant_chunks = _retrieve_relevant_chunks(question, candidate_context)
    cache_key = _question_cache_key(question, category, candidate_context, options)
    answer_memory = _load_answer_memory()

    cached = answer_memory.get(cache_key)
    if cached and _validate_answer(cached.get("answer", ""), category)[0]:
        logger.info("Using cached screening answer", category=category, question=_truncate(question, 80))
        return cached["answer"]

    from app.services.ai_router import ai_router
    from app.core.config import settings

    context_text = _render_candidate_context(candidate_context, relevant_chunks)
    question_text = _normalize_text(question)

    prompts: List[str] = []
    if options:
        option_lines = "\n".join(f"- {opt}" for opt in options)
        prompts.append(
            f"You are the internship applicant.\n\n"
            f"Answer in first person only. Choose exactly one option that best fits the candidate.\n"
            f"Do not add explanation. Do not sound like a recruiter.\n\n"
            f"Question type: {category}\n"
            f"Candidate context:\n{context_text}\n\n"
            f"Question:\n{question_text}\n\n"
            f"Options:\n{option_lines}\n"
            f"Reply with only the exact option text."
        )
    else:
        prompt_templates = {
            "eligibility": (
                "You are answering as the internship applicant.\n\n"
                "Write a short eligibility response.\n\n"
                "Rules:\n"
                "- Answer in first person.\n"
                "- Mention relevant skills.\n"
                "- Mention relevant projects if applicable.\n"
                "- Keep under 80 words.\n"
                "- Sound human.\n"
                "- Never answer like a recruiter.\n"
                "- Never use phrases like 'We are excited', 'Our company', or 'We invite candidates'.\n\n"
                "Candidate Profile:\n{context}\n\nQuestion:\n{question}"
            ),
            "experience": (
                "You are answering as the applicant.\n\n"
                "Write a concise professional answer about experience.\n\n"
                "Requirements:\n"
                "- Mention real projects from the resume.\n"
                "- Mention actual technologies.\n"
                "- Mention measurable impact if available.\n"
                "- Do not invent fake experience.\n"
                "- Use first person.\n"
                "- Keep under 120 words.\n\n"
                "Candidate Context:\n{context}\n\nQuestion:\n{question}"
            ),
            "why_hire_you": (
                "You are the candidate applying for an internship.\n\n"
                "Write a confident but natural answer explaining why the candidate is a strong fit.\n\n"
                "Requirements:\n"
                "- Mention relevant technical strengths.\n"
                "- Mention adaptability and learning ability.\n"
                "- Mention projects aligned with the role.\n"
                "- Avoid arrogance.\n"
                "- Avoid generic AI phrases.\n"
                "- Sound like a real student/candidate.\n"
                "- Keep under 100 words.\n\n"
                "Candidate Context:\n{context}\n\nQuestion:\n{question}"
            ),
            "availability": (
                "You are the candidate. Answer briefly and naturally about availability or notice period.\n\n"
                "Keep it under 25 words. Use first person. Do not sound generic.\n\n"
                "Candidate Context:\n{context}\n\nQuestion:\n{question}"
            ),
            "skills": (
                "You are the candidate. Answer with concrete skills from the profile and resume.\n\n"
                "Keep it under 100 words, first person, and avoid recruiter language.\n\n"
                "Candidate Context:\n{context}\n\nQuestion:\n{question}"
            ),
            "project_based": (
                "You are the candidate. Mention only real projects and technologies from the context.\n\n"
                "Keep it under 110 words. First person. Human and specific.\n\n"
                "Candidate Context:\n{context}\n\nQuestion:\n{question}"
            ),
            "education": (
                "You are the candidate. Answer briefly about education, degree, institution, or coursework.\n\n"
                "Keep it under 80 words. First person.\n\n"
                "Candidate Context:\n{context}\n\nQuestion:\n{question}"
            ),
            "ai_knowledge": (
                "You are the candidate. Answer specifically about AI / ML / LLM experience from the provided projects and skills.\n\n"
                "Keep it under 110 words. First person. No recruiter voice.\n\n"
                "Candidate Context:\n{context}\n\nQuestion:\n{question}"
            ),
            "salary": (
                "You are the candidate. Answer about stipend or compensation briefly and professionally.\n\n"
                "Keep it under 25 words. First person.\n\n"
                "Candidate Context:\n{context}\n\nQuestion:\n{question}"
            ),
            "relocation": (
                "You are the candidate. Answer clearly about relocation, location preference, or remote work.\n\n"
                "Keep it under 30 words. First person.\n\n"
                "Candidate Context:\n{context}\n\nQuestion:\n{question}"
            ),
            "strengths": (
                "You are the candidate. Answer naturally about strengths, fit, and learning ability.\n\n"
                "Keep it under 100 words. First person.\n\n"
                "Candidate Context:\n{context}\n\nQuestion:\n{question}"
            ),
            "generic": (
                "You are answering as the internship applicant.\n\n"
                "Write a short, candidate-grounded answer in first person. Use only facts from the profile/resume context.\n"
                "Keep it natural, concise, and under 100 words. Never sound like a recruiter.\n\n"
                "Candidate Context:\n{context}\n\nQuestion:\n{question}"
            ),
        }
        prompts.append(prompt_templates.get(category, prompt_templates["generic"]).format(context=context_text, question=question_text))

    prompts.append(
        f"You are the internship applicant. Write in first person. Use only facts from the candidate context.\n"
        f"Avoid recruiter language such as 'we are excited' or 'our company'.\n"
        f"Do not invent experiences, projects, or credentials.\n\n"
        f"Candidate context:\n{context_text}\n\nQuestion:\n{question_text}\n"
        f"Options: {options if options else 'N/A'}"
    )

    last_result = ""
    for attempt, prompt in enumerate(prompts[:2], start=1):
        resp = await ai_router.chat_completions_create(
            model=settings.OPENAI_MODEL_LIGHT,
            max_tokens=180,
            temperature=0.25 if not options else 0.15,
            messages=[{"role": "user", "content": prompt}],
            user_id=user_id,
            endpoint="/api/agent/internshala/answer",
        )
        answer = _normalize_text(resp.get("content", "")).strip('"').strip("'")
        last_result = answer

        if options:
            selected = None
            for option in options:
                if answer.lower() == option.lower() or answer.lower() in option.lower() or option.lower() in answer.lower():
                    selected = option
                    break
            if not selected and options:
                selected = options[0]
            answer = selected or answer

        valid, reason = _validate_answer(answer, category)
        logger.info(
            "Screening answer generated",
            question=_truncate(question, 80),
            category=category,
            attempt=attempt,
            valid=valid,
            validation_reason=reason,
            answer=_truncate(answer, 160),
        )
        if valid:
            answer_memory[cache_key] = {
                "answer": answer,
                "category": category,
                "question": question,
                "updated_at": datetime.now(timezone.utc).isoformat(),
            }
            _save_answer_memory(answer_memory)
            return answer

    fallback = _fallback_answer(category, candidate_context, question)
    if options:
        for option in options:
            if fallback.lower() == option.lower() or fallback.lower() in option.lower():
                fallback = option
                break
    logger.warning(
        "Using fallback screening answer",
        question=_truncate(question, 80),
        category=category,
        generated=_truncate(last_result, 120),
        fallback=_truncate(fallback, 120),
    )
    answer_memory[cache_key] = {
        "answer": fallback,
        "category": category,
        "question": question,
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }
    _save_answer_memory(answer_memory)
    return fallback


async def _ai_answer(
    question: str,
    options: list,
    profile_summary: str,
    job_context: str = "",
    user_id: str = None,
    profile: Any = None,
    resume: Any = None,
    job: Any = None,
    settings_obj: Any = None,
    user_full_name: Optional[str] = None,
) -> str:
    """Backward-compatible wrapper for candidate-grounded answer generation."""
    if profile is None:
        class _ProfileProxy:
            pass
        profile = _ProfileProxy()
        setattr(profile, "professional_summary", profile_summary)
        setattr(profile, "desired_roles", [])
        setattr(profile, "projects", [])
        setattr(profile, "work_experience", [])
        setattr(profile, "education", [])
        setattr(profile, "skills", [])
        setattr(profile, "certifications", [])
        setattr(profile, "awards", [])
        setattr(profile, "publications", [])
        setattr(profile, "location", "")
        setattr(profile, "github_url", "")
        setattr(profile, "portfolio_url", "")
        setattr(profile, "linkedin_url", "")

    # Respect direct identity mapping before any AI call.
    direct = _identity_field_value(question, profile, user_full_name=user_full_name, settings_obj=settings_obj)
    if direct:
        return direct

    return await _generate_candidate_answer(
        question=question,
        options=list(options or []),
        profile=profile,
        resume=resume,
        job=job,
        settings_obj=settings_obj,
        user_id=user_id,
        user_full_name=user_full_name,
    )


def _build_profile_summary(profile, job=None) -> str:
    if not profile:
        return "Entry-level candidate, motivated and eager to learn."
    parts = []
    if profile.experience_level:
        parts.append(f"Experience level: {profile.experience_level}")
    if profile.professional_summary:
        parts.append(profile.professional_summary[:400])
    if profile.desired_roles:
        parts.append(f"Target roles: {', '.join(profile.desired_roles[:3])}")
    if getattr(profile, "work_experience", None):
        exp = profile.work_experience
        if exp:
            latest = exp[0]
            parts.append(
                f"Most recent experience: {latest.get('title', '')} at {latest.get('company', '')}"
            )
    if getattr(profile, "projects", None):
        proj_names = [p.get("name", "") for p in profile.projects[:3] if p.get("name")]
        if proj_names:
            parts.append(f"Projects: {', '.join(proj_names)}")
    if getattr(profile, "github_url", None):
        parts.append(f"GitHub: {profile.github_url}")
    if job:
        if getattr(job, "title", None):
            parts.append(f"Applying for: {job.title}")
        if getattr(job, "description_clean", None) or getattr(job, "description_raw", None):
            desc = (job.description_clean or job.description_raw or "")[:600]
            parts.append(f"Job description excerpt:\n{desc}")
    return "\n".join(parts) or "Entry-level candidate, motivated and eager to learn."


# ─────────────────────────────────────────────────────────────────────────────
#  LOW-LEVEL HELPERS
# ─────────────────────────────────────────────────────────────────────────────

async def _human_type(element, text: str) -> None:
    await element.click()
    await element.fill("")
    for char in text:
        await element.type(char, delay=random.uniform(40, 130))
        if random.random() < 0.05:
            await asyncio.sleep(random.uniform(0.1, 0.3))
    try:
        await element.press("Tab")
    except Exception:
        pass


def _load_cookies() -> list:
    if not COOKIE_FILE.exists():
        return []
    try:
        cookies = json.loads(COOKIE_FILE.read_text())
        for c in cookies:
            if c.get("sameSite") not in ("Strict", "Lax", "None"):
                c["sameSite"] = "Lax"
            if "domain" in c and not c["domain"].startswith("."):
                c["domain"] = "." + c["domain"].lstrip(".")
        return cookies
    except Exception as e:
        logger.warning("Could not load cookies", error=str(e))
        return []


async def _save_cookies(context) -> None:
    try:
        COOKIE_FILE.parent.mkdir(parents=True, exist_ok=True)
        cookies = await context.cookies()
        COOKIE_FILE.write_text(json.dumps(cookies, indent=2))
        logger.info("Cookies saved", count=len(cookies))
    except Exception as e:
        logger.warning("Could not save cookies", error=str(e))


async def _screenshot(page, name: str) -> None:
    try:
        SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        await page.screenshot(
            path=str(SCREENSHOT_DIR / f"{name}_{ts}.png"),
            full_page=True,
        )
    except Exception:
        pass


async def _has_captcha(page) -> bool:
    try:
        # Check for VISIBLE CAPTCHA challenge (iframe or interactive element)
        for frame in page.frames:
            if "recaptcha/api2/bframe" in frame.url or "hcaptcha.com/captcha" in frame.url:
                # Check if the frame is actually visible
                try:
                    box = await frame.frame_element().bounding_box()
                    if box and box["width"] > 0 and box["height"] > 0:
                        return True
                except Exception:
                    pass
        # Check for visible reCAPTCHA widget (not just script tags)
        recaptcha_div = await page.query_selector(".g-recaptcha:not([style*='display: none'])")
        if recaptcha_div and await recaptcha_div.is_visible():
            return True
        return False
    except Exception:
        return False


async def _wait_for_captcha_resolution(page, timeout_s: int = 120) -> bool:
    logger.info("Waiting for CAPTCHA", timeout=timeout_s)
    for _ in range(timeout_s):
        await asyncio.sleep(1)
        if not await _has_captcha(page):
            logger.info("CAPTCHA resolved")
            return True
    return False


async def _goto_lenient(page, url: str, timeout_ms: int = 60000) -> None:
    """Navigate without failing the whole batch on a slow page load.

    We use a low-friction navigation and then give the page a short chance to
    settle. This keeps slow proxy loads from aborting otherwise valid runs.
    """
    try:
        await page.goto(url, wait_until="commit", timeout=timeout_ms)
        try:
            await page.wait_for_load_state("domcontentloaded", timeout=min(15000, timeout_ms))
        except Exception:
            pass
    except Exception as exc:
        logger.warning("Navigation issue; continuing with current page", url=url, error=str(exc), timeout_ms=timeout_ms)
        try:
            await page.wait_for_load_state("domcontentloaded", timeout=10000)
        except Exception:
            pass


async def _is_logged_in(page) -> bool:
    try:
        # First check URL - most reliable indicator
        url = page.url
        if "/student/" in url and "/login" not in url:
            logger.debug("_is_logged_in found /student/ in URL")
            return True
        
        # Check for multiple logged-in indicators
        selectors = [
            ".profile-header", "#header-profile-img",
            "a[href*='/student/dashboard']", "a[href*='/student/profile']",
            ".student-profile-pic", ".logged-in-header",
            "a[href*='/student/']", ".user-profile",
            ".nav-item.profile", ".profile-dropdown",
            "img[alt*='profile' i]", ".avatar",
            "a:has-text('Logout')", "a:has-text('Sign Out')",
            "a[href*='logout']", "a[href*='signout']",
            # Internshala specific
            ".nav-link:has-text('Internships')", ".nav-link:has-text('Jobs')",
        ]
        for sel in selectors:
            try:
                el = await page.query_selector(sel)
                if el:
                    logger.debug("_is_logged_in found", selector=sel)
                    return True
            except Exception:
                continue
        
        # Check for security walls that aren't "Login" but prevent access
        content = await page.content()
        content_lower = content.lower()
        if "cloudflare" in content_lower or "verify you are human" in content_lower or "captcha" in content_lower:
            logger.warning("Security check detected during login check")
            return False

        # If none of the above specific selectors or keywords were found, we are likely not logged in
        logger.debug("_is_logged_in returning False", url=url)
        return False
    except Exception as e:
        logger.debug("_is_logged_in exception", error=str(e))
        return False


async def _take_failure_screenshot(page, name: str):
    """Utility to capture what went wrong visually."""
    try:
        from app.core.config import settings
        path = settings.storage_path / "recordings" / f"failure_{name}_{int(datetime.now().timestamp())}.png"
        path.parent.mkdir(parents=True, exist_ok=True)
        await page.screenshot(path=str(path))
        logger.info(f"📸 Failure screenshot saved", path=str(path))
    except Exception as e:
        logger.warning(f"Failed to take failure screenshot: {e}")


async def _is_on_login_wall(page) -> bool:
    url = page.url
    if "/login" in url or "/signup" in url:
        return True
    try:
        pw = await page.query_selector("input[type='password'], #login-modal input[type='password']")
        return pw is not None
    except Exception:
        return False


async def _dismiss_blocking_modals_only(page) -> None:
    """Dismiss login/promo modals without touching the application form modal."""
    try:
        for sel in (
            "#login-modal .close", "#login-modal button.close_action",
            "#signup-modal .close", "#register-modal .close",
            ".skilling-modal .close", ".training-popup .close",
            "button.modal_secondary_btn.close_action",
        ):
            try:
                btns = await page.query_selector_all(sel)
                for btn in btns:
                    if await btn.is_visible():
                        await btn.click()
                        await asyncio.sleep(0.3)
            except Exception:
                pass

        await page.keyboard.press("Escape")
        await asyncio.sleep(0.5)

        await page.evaluate("""
            () => {
                var blockingIds = [
                    'login-modal', 'signup-modal', 'register-modal',
                    'skilling-modal', 'training-popup', 'cookie-modal',
                    'cookieModal', 'cookie-consent'
                ];
                blockingIds.forEach(function(id) {
                    var el = document.getElementById(id);
                    if (el) el.remove();
                });
                
                // Remove modal backdrops first
                document.querySelectorAll('.modal-backdrop.show').forEach(function(el) {
                    el.remove();
                });
                
                // Handle generic aria-modal dialogs (including "One time offer" signup modals)
                document.querySelectorAll('[role="dialog"][aria-modal="true"]').forEach(function(dialog) {
                    // Check if it's a signup/offer modal (don't close if it's the application form)
                    var text = (dialog.innerText || '').toLowerCase();
                    var isSignupModal = text.includes('sign up') || text.includes('one time offer') || text.includes('free ai career');
                    
                    if (isSignupModal) {
                        // Try to close it first
                        var closeBtn = dialog.querySelector('[aria-label="Close"], .close, .modal-close, button[class*="close"], .signup-modal-close');
                        if (closeBtn) {
                            closeBtn.click();
                        }
                        // If not closed, remove it
                        setTimeout(() => dialog.remove(), 500);
                    }
                });
                
                // Also remove any visible signup/offer modals by selector
                document.querySelectorAll('.modal.show, [class*="signup-modal"]:not(form), [class*="offer-modal"]:not(form)').forEach(function(el) {
                    var text = (el.innerText || '').toLowerCase();
                    if (text.includes('sign up') || text.includes('one time offer')) {
                        el.remove();
                    }
                });
                
                // Always remove modal backdrops
                document.querySelectorAll('.modal-backdrop').forEach(function(el) {
                    el.remove();
                });
                document.body.classList.remove('modal-open');
                document.body.style.overflow = 'auto';
            }
        """)
        await asyncio.sleep(0.3)
    except Exception:
        pass


async def _do_login(page, email: str, password: str) -> dict:
    logger.info("Attempting login")
    if "/login" not in page.url:
        await page.goto(
            "https://internshala.com/login/user",
            wait_until="domcontentloaded", timeout=30000,
        )
        await asyncio.sleep(random.uniform(2, 3))

    if await _has_captcha(page):
        if not await _wait_for_captcha_resolution(page, timeout_s=180):
            return {"success": False, "error": "CAPTCHA timed out on login page"}

    email_input = await page.wait_for_selector(
        "input#email, input[name='email'], input[type='email']", timeout=10000
    )
    if not email_input:
        return {"success": False, "error": "Email input not found"}

    await _human_type(email_input, email)
    await asyncio.sleep(random.uniform(0.5, 1.2))

    pwd_input = await page.query_selector(
        "input#password, input[name='password'], input[type='password']"
    )
    if not pwd_input:
        return {"success": False, "error": "Password input not found"}

    await _human_type(pwd_input, password)
    await asyncio.sleep(random.uniform(0.5, 1.0))

    submit_btn = await page.query_selector(
        "#login_submit, button[type='submit'], button:has-text('Login'), input[type='submit']"
    )
    if not submit_btn:
        return {"success": False, "error": "Login submit not found"}

    await page.evaluate("function(el) { el.click(); }", submit_btn)
    await asyncio.sleep(2)

    if await _has_captcha(page):
        if not await _wait_for_captcha_resolution(page, timeout_s=180):
            return {"success": False, "error": "CAPTCHA timed out after login"}

    await asyncio.sleep(random.uniform(4, 7))
    current_url = page.url

    if "verify" in current_url or "otp" in current_url.lower():
        return {"success": False, "error": "OTP verification required. Log in manually and run save_cookies.py."}

    if await _is_logged_in(page):
        logger.info("Login successful")
        return {"success": True}

    # Log debug info for failed login
    logger.warning("Login failed - checking page state", 
                   url=current_url,
                   has_captcha=await _has_captcha(page),
                   page_title=await page.title())
    await _screenshot(page, "login_failed")
    
    return {"success": False, "error": "Login failed — check credentials. Run save_cookies.py to login manually."}


def _next_join_date() -> str:
    d = datetime.now(timezone.utc) + timedelta(days=30)
    return d.strftime("%d/%m/%Y")


# ─────────────────────────────────────────────────────────────────────────────
#  ALREADY-APPLIED CHECK  (scoped — avoids false positives from page body text)
# ─────────────────────────────────────────────────────────────────────────────

async def _is_already_applied(page) -> bool:
    """
    Return True ONLY when Internshala's own per-internship status badge shows
    the current user has already applied.
    """
    try:
        # 1. Check scoped action area first (most reliable)
        action_area = await page.query_selector(
            ".internship_apply, .apply-button-container, "
            ".application-actions, .job-apply-section, "
            ".apply-now-button, #apply-section, .button_container"
        )
        if action_area:
            area_text = (await action_area.inner_text() or "").lower()
            # Look for explicit badges or button state inside the action area
            if any(p in area_text for p in ["applied", "you have applied", "already applied"]):
                # Confirm it's not "apply now" or similar
                if "apply now" not in area_text:
                    logger.info("Already-applied indicator found in action area")
                    return True

        # 2. Check for specific badges anywhere, but with more precise selectors
        badge = await page.query_selector(
            ".already-applied, .applied-badge, .application-status-applied, "
            "span.applied:not(:empty)"
        )
        if badge and await badge.is_visible():
            # Check proximity to known non-job sections (e.g. footer, similar jobs)
            # This is hard to do perfectly, so we trust visible badges for now.
            logger.info("Already-applied badge found")
            return True

        # 3. Check official apply buttons specifically
        for btn_sel in ("#easy_apply_button", "#apply_button", "#btn-apply"):
            btn = await page.query_selector(btn_sel)
            if btn:
                btn_text = (await btn.inner_text() or "").strip().lower()
                is_disabled = await btn.get_attribute("disabled") is not None
                if "applied" in btn_text and is_disabled:
                    logger.info("Apply button is disabled with 'Applied' label")
                    return True

        return False
    except Exception as e:
        logger.warning("Error in _is_already_applied", error=str(e))
        return False


# ─────────────────────────────────────────────────────────────────────────────
#  LABEL EXTRACTION
# ─────────────────────────────────────────────────────────────────────────────

async def _get_field_label(page, el_handle) -> str:
    """
    Find the human-readable question label for a form field.
    Handles Internshala's custom_question_text_XXXXXXX pattern where the
    question text is a sibling/cousin several DOM levels up.
    """
    try:
        return await page.evaluate("""
            function(el) {
                // 1. label[for=id]
                if (el.id) {
                    var lbl = document.querySelector('label[for="' + el.id + '"]');
                    if (lbl) return (lbl.innerText || '').trim();
                }

                // 2. Walk previous siblings broadly (not just label tags)
                var sib = el.previousElementSibling;
                var sibDepth = 0;
                while (sib && sibDepth < 5) {
                    var t = (sib.innerText || '').trim();
                    if (t && t.length > 8 && t.length < 500) return t.split('\\n')[0].trim();
                    sib = sib.previousElementSibling;
                    sibDepth++;
                }

                // 3. Walk up DOM — scan each ancestor for question text
                var parent = el.parentElement;
                for (var i = 0; i < 10; i++) {
                    if (!parent) break;

                    // Look for explicit label or question containers
                    var candidates = parent.querySelectorAll(
                        'label, .question-label, .field-label, .custom-question-text, ' +
                        '.question_text, [class*="question"], p, h4, h5, strong, b'
                    );
                    for (var j = 0; j < candidates.length; j++) {
                        var c = candidates[j];
                        if (c === el || c.contains(el)) continue;
                        var ct = (c.innerText || '').trim();
                        if (ct && ct.length > 8 && ct.length < 400) {
                            return ct.split('\\n')[0].trim();
                        }
                    }

                    // Raw parent text (minus inputs) — catches bare text nodes
                    var cloned = parent.cloneNode(true);
                    cloned.querySelectorAll('input, textarea, select, button').forEach(
                        function(n) { n.remove(); }
                    );
                    var parentText = (cloned.innerText || '').trim();
                    if (parentText && parentText.length > 8 && parentText.length < 400) {
                        return parentText.split('\\n')[0].trim();
                    }

                    parent = parent.parentElement;
                }
                return el.placeholder || '';
            }
        """, el_handle)
    except Exception:
        return ""


# ─────────────────────────────────────────────────────────────────────────────
#  JS VALUE SETTER  — sets a field value without requiring visibility
# ─────────────────────────────────────────────────────────────────────────────

async def _js_set_value(page, el_handle, value: str) -> None:
    """
    Set a form field value via JS native setter + fire input/change events.
    Works on both visible and hidden elements (unlike Playwright's fill()
    which requires the element to be visible, enabled, and editable —
    causing a 30-second timeout on hidden fields).
    """
    await page.evaluate(
        """function(args) {
            var el = args[0];
            var val = args[1];
            // Use the native setter so React/Vue internal state also updates
            try {
                var tag = el.tagName.toLowerCase();
                if (tag === 'textarea') {
                    var setter = Object.getOwnPropertyDescriptor(
                        window.HTMLTextAreaElement.prototype, 'value').set;
                    setter.call(el, val);
                } else if (tag === 'input') {
                    var setter = Object.getOwnPropertyDescriptor(
                        window.HTMLInputElement.prototype, 'value').set;
                    setter.call(el, val);
                } else {
                    el.value = val;
                }
            } catch(e) {
                el.value = val;
            }
            el.dispatchEvent(new Event('input', {bubbles: true}));
            el.dispatchEvent(new Event('change', {bubbles: true}));
            el.dispatchEvent(new KeyboardEvent('keyup', {bubbles: true}));
            el.dispatchEvent(new Event('focusout', {bubbles: true}));
            el.dispatchEvent(new Event('blur', {bubbles: true}));
        }""",
        [el_handle, value],
    )


# ─────────────────────────────────────────────────────────────────────────────
#  FILL ALL FORM FIELDS  (visible AND hidden)
# ─────────────────────────────────────────────────────────────────────────────

async def _fill_all_fields(page, profile, resume, settings_obj, profile_summary: str, cover_answer: str, job_context: str = "", user_id: str = None, user_full_name: str = None, job: Any = None) -> None:
    """
    Fill every textarea, select, range, text input, and radio — including
    fields that are hidden/collapsed. Internshala validates all required fields
    on submit regardless of visibility.
    Uses JS direct value assignment for hidden fields to avoid Playwright
    fill() timeouts.
    """

    async def _get_scope_handle():
        for selector in (
            ".modal.show form",
            ".modal.show .modal-content form",
            "#application_form",
            ".application-modal form",
            ".modal.show",
            "form",
        ):
            handle = await page.query_selector(selector)
            if handle:
                try:
                    if await handle.is_visible():
                        return handle
                except Exception:
                    return handle
        return page

    async def _looks_like_login_modal() -> bool:
        """Detect if modal is a login/auth form instead of an application form.
        
        Checks for:
        1. Password field anywhere in the modal (even if hidden)
        2. Login-related text in modal heading/instructions
        3. First name + Last name + Password pattern (typical login form)
        """
        try:
            # Check for password field - even if hidden (visible=false)
            password_field = await page.query_selector(
                ".modal.show input[type='password'], .modal.show input[name='password'], "
                "#login-modal input[type='password'], #login-modal input[name='password'], "
                ".modal input[type='password']"
            )
            if password_field:
                logger.warning("Detected password field in modal - likely login form")
                return True
            
            # Check for login-related text
            login_modal = await page.query_selector("#login-modal, #signup-modal, #register-modal, .modal.show")
            if login_modal:
                modal_text = _normalize_text(await login_modal.inner_text()).lower()
                if any(token in modal_text for token in ("sign in", "login", "forgot password", "register", "email address", "password")):
                    logger.warning("Detected login-related text in modal")
                    return True
            
            # Check for login form field pattern: email + password + first_name
            has_email = await page.query_selector("input[type='email'], input[name='email']")
            has_password = await page.query_selector("input[type='password'], input[name='password']")
            has_first_name = await page.query_selector("input[name='first_name']")
            has_g_recaptcha = await page.query_selector("textarea[name='g-recaptcha-response'], #g-recaptcha-response-100000")
            
            # If we find email+password+first_name+recaptcha, it's a login form
            if has_email and has_password and has_first_name and has_g_recaptcha:
                logger.warning("Detected login form pattern (email+password+first_name+recaptcha) instead of application form")
                return True
                
        except Exception as e:
            logger.warning("Error checking for login modal", error=str(e))
            return False
        return False

    scope = await _get_scope_handle()

    if await _looks_like_login_modal():
        logger.error("Login modal opened instead of application form; aborting")
        await _screenshot(page, "login_modal_instead_of_application_form")
        raise ValueError("Login modal opened instead of application form - Internshala detected bot")

    def _is_boilerplate_label(label: str) -> bool:
        text = (label or "").strip().lower()
        if not text:
            return False
        return any(
            phrase in text
            for phrase in (
                "new to internshala",
                "register (student / company)",
                "sign in",
                "login",
                "forgot password",
                "create account",
                "already have an account",
            )
        )

    async def _scope_query_all(selector: str):
        if scope is page:
            return await page.query_selector_all(selector)
        return await scope.query_selector_all(selector)

    # ── Textareas (ALL — including hidden) ───────────────────────────────────
    for ta in await _scope_query_all("textarea"):
        try:
            current = (await ta.input_value()).strip()
            if current:
                continue

            label = await _get_field_label(page, ta)
            logger.info("Textarea found", label=(label or "(no label)")[:80])

            if _is_boilerplate_label(label):
                logger.info("Skipping boilerplate textarea", label=(label or "(no label)")[:80])
                continue

            if label:
                answer = await _ai_answer(
                    label,
                    [],
                    profile_summary,
                    job_context=job_context,
                    user_id=user_id,
                    profile=profile,
                    resume=resume,
                    job=job,
                    settings_obj=settings_obj,
                    user_full_name=user_full_name,
                )
            else:
                answer = cover_answer

            await _js_set_value(page, ta, answer)
            logger.info("Filled textarea", label=(label or "(no label)")[:60], chars=len(answer))
        except Exception as e:
            logger.warning("Could not fill textarea", error=str(e))

    # ── SELECT dropdowns ──────────────────────────────────────────────────────
    for sel_el in await _scope_query_all("select"):
        try:
            current_val = await sel_el.evaluate("function(el) { return el.value; }")
            if current_val and current_val not in ("", "0", "Select", "-- Select --"):
                continue

            options_data = await sel_el.evaluate("""
                function(el) {
                    return Array.from(el.options).map(function(o) {
                        return {value: o.value, text: o.text.trim()};
                    });
                }
            """)
            real_options = [
                o for o in options_data
                if o["value"] and o["value"] not in ("", "0", "Select")
                and not o["text"].lower().startswith("select")
                and not o["text"].startswith("--")
            ]
            if not real_options:
                continue

            option_texts = [o["text"] for o in real_options]
            label = await _get_field_label(page, sel_el)
            if not label:
                placeholder_opt = next(
                    (o for o in options_data if not o["value"] or o["value"] in ("", "0")), None
                )
                label = placeholder_opt["text"] if placeholder_opt else "Please select an option"

            if _is_boilerplate_label(label):
                logger.info("Skipping boilerplate select", label=(label or "(no label)")[:80])
                continue

            logger.info("Select field", label=label[:80], options=option_texts)
            chosen_text = await _ai_answer(
                label,
                option_texts,
                profile_summary,
                job_context=job_context,
                user_id=user_id,
                profile=profile,
                resume=resume,
                job=job,
                settings_obj=settings_obj,
                user_full_name=user_full_name,
            )

            chosen_value = None
            for o in real_options:
                if o["text"].lower() == chosen_text.lower():
                    chosen_value = o["value"]
                    break
            if not chosen_value:
                for o in real_options:
                    if chosen_text.lower() in o["text"].lower() or o["text"].lower() in chosen_text.lower():
                        chosen_value = o["value"]
                        break
            if not chosen_value:
                chosen_value = real_options[len(real_options) // 2]["value"]

            try:
                # Use short timeout and fallback to JS for hidden/sticky elements
                await sel_el.select_option(value=chosen_value, timeout=2000)
            except Exception:
                await page.evaluate("function(data) { data.el.value = data.val; data.el.dispatchEvent(new Event('change', {bubbles: true})); }", {"el": sel_el, "val": chosen_value})
            
            await page.evaluate(
                "function(el) { el.dispatchEvent(new Event('change', {bubbles:true})); }", sel_el
            )
            logger.info("Selected dropdown", label=label[:60], chosen=chosen_text[:60])
            await asyncio.sleep(0.3)
        except Exception as e:
            logger.warning("Could not fill select", error=str(e))

    # ── Range / number inputs ─────────────────────────────────────────────────
    for inp in await _scope_query_all("input[type='range'], input[type='number']"):
        try:
            if (await inp.input_value()).strip():
                continue
            label = await _get_field_label(page, inp)
            if _is_boilerplate_label(label):
                logger.info("Skipping boilerplate number field", label=(label or "(no label)")[:80])
                continue
            mn = int(float(await inp.evaluate("function(el) { return el.min || '1'; }") or "1"))
            mx = int(float(await inp.evaluate("function(el) { return el.max || '5'; }") or "5"))
            step = int(float(await inp.evaluate("function(el) { return el.step || '1'; }") or "1"))
            opts = [str(v) for v in range(mn, mx + 1, step)]
            chosen = await _ai_answer(
                label or "Rate your skill level (1=lowest)",
                opts,
                profile_summary,
                job_context=job_context,
                user_id=user_id,
                profile=profile,
                resume=resume,
                job=job,
                settings_obj=settings_obj,
                user_full_name=user_full_name,
            )
            try:
                cv = max(mn, min(mx, int(float(chosen))))
                chosen = str(cv)
            except Exception:
                chosen = opts[len(opts) // 2]
            await _js_set_value(page, inp, chosen)
            logger.info("Filled range/number", label=(label or "?")[:60], value=chosen)
        except Exception as e:
            logger.warning("Could not fill range input", error=str(e))

    # ── Custom text / url / email inputs ─────────────────────────────────────
    # FIX: Use _js_set_value instead of inp.fill() so hidden inputs don't
    # cause a 30-second Playwright timeout (fill() requires visibility).
    for inp in await _scope_query_all(
        "input[type='text'], input[type='url'], input[type='email']"
    ):
        try:
            inp_id = await inp.evaluate("function(el) { return el.id || ''; }")
            inp_name = await inp.evaluate("function(el) { return el.name || ''; }")
            inp_type_attr = await inp.evaluate("function(el) { return el.type || 'text'; }")

            # Skip fields handled elsewhere or hidden system fields
            if inp_id in ("last_working_date", "phone_number") or \
               inp_name in ("last_working_date", "phone_number", "phone"):
                continue
            # Skip Internshala internal hidden fields we shouldn't touch
            if inp_id in ("status", "csrf", "csrf_test_name") or \
               inp_name in ("internshipId", "source", "csrf_test_name",
                            "is_sequential_apply_flow", "sequential_apply_referral",
                            "last_applied_application_id", "last_applied_job_profile",
                            "current_job_profile"):
                continue

            if (await inp.input_value()).strip():
                continue

            label = await _get_field_label(page, inp)
            if not label:
                continue  # Can't fill without knowing what the field is asking

            if _is_boilerplate_label(label):
                logger.info("Skipping boilerplate text input", label=(label or "(no label)")[:80])
                continue

            direct_value = _identity_field_value(label, profile, user_full_name=user_full_name, settings_obj=settings_obj)
            if direct_value:
                answer = direct_value
            elif inp_type_attr == "email":
                answer = _configured_account_email(settings_obj)
            elif inp_type_attr == "url" or any(w in label.lower() for w in ("url", "link", "portfolio", "website")):
                answer = (
                    getattr(profile, "portfolio_url", "") or
                    getattr(profile, "github_url", "") or
                    "Available upon request"
                )
            elif "linkedin" in label.lower():
                answer = getattr(profile, "linkedin_url", "") or "Available upon request"
            elif "github" in label.lower():
                answer = getattr(profile, "github_url", "") or "Available upon request"
            else:
                # Fallback to AI for general free-text questions, but keep answers short
                answer = await _ai_answer(
                    label,
                    [],
                    profile_summary,
                    job_context=job_context,
                    user_id=user_id,
                    profile=profile,
                    resume=resume,
                    job=job,
                    settings_obj=settings_obj,
                    user_full_name=user_full_name,
                )

            if answer:
                await _js_set_value(page, inp, str(answer))
                logger.info("Filled text input", label=label[:60], value=(str(answer)[:120] if len(str(answer))>120 else str(answer)))
        except Exception as e:
            logger.warning("Could not fill text input", error=str(e))

    # ── Radio buttons ─────────────────────────────────────────────────────────
    radio_groups = await page.evaluate("""
        () => {
            var groups = {};
            document.querySelectorAll('input[type="radio"]').forEach(function(r) {
                var name = r.name || r.id;
                if (!groups[name]) groups[name] = [];
                groups[name].push({id: r.id, value: r.value, checked: r.checked});
            });
            return groups;
        }
    """)
    logger.info("Radio groups", groups=list(radio_groups.keys()))
    for group_name, radios in radio_groups.items():
        if any(r["checked"] for r in radios):
            continue
        target = next(
            (r for r in radios if r["id"] == "radio1" or r["id"].startswith("Yes_")),
            radios[0] if radios else None,
        )
        if not target:
            continue
        try:
            rid = target["id"]
            el = await page.query_selector(f"#{rid}")
            if el:
                lbl = await page.query_selector(f"label[for='{rid}']")
                await (lbl or el).click()
                logger.info("Selected radio", group=group_name, id=rid)
                await asyncio.sleep(0.3)
        except Exception as e:
            logger.warning("Could not click radio", group=group_name, error=str(e))

    # ── Phone ─────────────────────────────────────────────────────────────────
    if profile and profile.phone:
        for sel in ("#phone_number", "input[name='phone_number']", "input[name='phone']", "input[type='tel']"):
            el = await page.query_selector(sel)
            if el and await el.is_visible():
                if not (await el.input_value()).strip():
                    await _human_type(el, profile.phone)
                    logger.info("Filled phone")
                break

    # ── Join date ─────────────────────────────────────────────────────────────
    join_date = _next_join_date()
    for sel in (
        "#last_working_date", "input[name='last_working_date']",
        "input[id*='join']", "input[name*='join']",
        "input[placeholder*='join' i]", "input[placeholder*='latest' i]",
        "input[placeholder*='date' i]",
    ):
        try:
            el = await page.query_selector(sel)
            if el and await el.is_visible():
                if not (await el.input_value()).strip():
                    await el.click()
                    await el.fill(join_date)
                    await page.evaluate(
                        "function(el) { el.dispatchEvent(new Event('input',{bubbles:true})); el.dispatchEvent(new Event('change',{bubbles:true})); }",
                        el,
                    )
                    logger.info("Filled join-date", value=join_date)
                break
        except Exception:
            pass

    # ── Resume upload ─────────────────────────────────────────────────────────
    if resume and resume.file_path:
        resume_path = Path(settings_obj.LOCAL_STORAGE_PATH) / resume.file_path
        if resume_path.exists():
            file_input = await page.query_selector("input[type='file']")
            if file_input:
                await file_input.set_input_files(str(resume_path))
                logger.info("Uploaded resume")
                await asyncio.sleep(2)


# ─────────────────────────────────────────────────────────────────────────────
#  FIND SUBMIT BUTTON
# ─────────────────────────────────────────────────────────────────────────────

async def _find_submit_button(page):
    """Try a wide set of selectors (scoped first, then page-wide) to find the submit/confirm CTA."""
    submit_selectors = [
        "button[type='submit']",
        "input[type='submit']",
        "button:has-text('Submit application')",
        "button:has-text('Submit')",
        "button:has-text('Apply now')",
        "button:has-text('Apply Now')",
        "button:has-text('Apply')",
        "button.btn-primary",
        ".submit_application",
        ".submit-btn",
        ".submit-button",
        ".btn-primary",
        "input[type='button'][value*='Submit']",
        "button:has-text('Proceed')",
        "button:has-text('Continue')",
    ]

    # Scoped search inside likely modal/form containers first
    container_selectors = (
        "#application_form", ".application-modal", "#apply-modal",
        "form[id*='apply']", "form[action*='apply']", ".modal.show",
        ".modal[style*='block']", ".internship-apply-modal", ".modal-content form", "form",
    )

    for container_sel in container_selectors:
        container = await page.query_selector(container_sel)
        if not container:
            continue
        for sel in submit_selectors:
            try:
                btn = await container.query_selector(sel)
                if btn and await btn.is_visible():
                    logger.info("Found submit (scoped)", container=container_sel, selector=sel)
                    return btn
            except Exception:
                continue

    # Page-wide search fallback
    for sel in submit_selectors:
        try:
            btn = await page.query_selector(sel)
            if btn and await btn.is_visible():
                logger.info("Found submit (page-wide)", selector=sel)
                return btn
        except Exception:
            continue

    # Last resort: scan generic buttons for helpful text
    for btn in await page.query_selector_all("button, input[type='submit'], input[type='button'], a[role='button']"):
        try:
            if not await btn.is_visible():
                continue
            txt = ((await btn.inner_text()) or "").strip().lower()
            aria = ((await btn.get_attribute("aria-label")) or "").strip().lower()
            label = txt or aria
            if not label or len(label) > 80:
                continue
            if any(w in label for w in ("submit", "send application", "submit application", "proceed", "continue", "next", "apply")):
                logger.info("Found submit by text fallback", txt=label)
                return btn
        except Exception:
            pass
    return None


# ─────────────────────────────────────────────────────────────────────────────
#  SUCCESS / ERROR DETECTION
# ─────────────────────────────────────────────────────────────────────────────

# Known success phrases Internshala shows after a successful submit
_SUCCESS_SIGNALS = (
    "your application has been submitted",
    "successfully applied",
    "applied successfully",
    "thank you for applying",
    "you have successfully applied",
    "application sent successfully",
    "application has been sent",
    "you have applied",
    "application submitted",
    "congratulations",
)


async def _check_submission_result(page, internship_id: Optional[str] = None) -> Optional[dict]:
    """
    Return a success dict if submission succeeded, None if it clearly failed.
    """
    url = page.url
    logger.info("Checking submission result", url=url, id=internship_id)

    async def _read_detail_cta_state() -> dict:
        return await page.evaluate("""
            () => {
                var pageText = (document.body && document.body.innerText ? document.body.innerText : '').toLowerCase();
                var cta = document.querySelector('.top_apply_now_cta, .apply_now_cta, button.top_apply_now_cta');
                var text = cta ? (cta.innerText || '').toLowerCase().trim() : '';
                var cls = cta ? (cta.className || '').toLowerCase() : '';

                var visibleButtons = Array.from(document.querySelectorAll('button, a[role="button"], input[type="button"], input[type="submit"]'))
                    .filter(function(el) { return !!(el.offsetParent !== null); })
                    .map(function(el) { return ((el.innerText || el.value || el.getAttribute('aria-label') || '')).toLowerCase().trim(); })
                    .filter(function(t) { return t && t.length < 120; });

                var anyButtonText = visibleButtons.join(' | ');

                var notEligible = text.includes('not eligible') ||
                                  pageText.includes('not eligible') ||
                                  pageText.includes('not eligible for this internship') ||
                                  anyButtonText.includes('not eligible') ||
                                  cls.includes('not-eligible') ||
                                  cls.includes('not_eligible');

                var appliedLike = text.includes('applied') ||
                                  text.includes('application sent') ||
                                  text.includes('withdraw') ||
                                  pageText.includes('already applied') ||
                                  pageText.includes('application submitted') ||
                                  anyButtonText.includes('applied') ||
                                  anyButtonText.includes('withdraw') ||
                                  anyButtonText.includes('application sent') ||
                                  cls.includes('applied');

                var applyNow = text === 'apply now' || text.includes('apply now');

                if (notEligible) {
                    return { state: 'not_eligible', text: text };
                }
                if (appliedLike) {
                    return { state: 'applied', text: text };
                }
                if (applyNow) {
                    return { state: 'apply_now', text: text };
                }
                return { state: 'unknown', text: text };
            }
        """)

    # 0. Check for explicit success URL redirect
    if "/application_submitted" in url or "application/success" in url or "matching-preferences" in url:
        logger.info("Confirmed via success URL redirect")
        return {"success": True, "ats": "internshala", "verified": True}
    
    modal = await page.query_selector('.modal.show')
    if modal:
        modal_text = (await modal.inner_text() or "").lower()
        
        # 1a. Check for SUCCESS inside modal FIRST
        for sig in _SUCCESS_SIGNALS:
            if sig in modal_text:
                logger.info("Confirmed via modal success text", signal=sig)
                return {"success": True, "ats": "internshala", "verified": True}
        
        # 1b. Check for ERRORS inside modal (more specific keywords to avoid footer links)
        if "invalid job" in modal_text:
            logger.warning("Invalid Job error detected")
            return {"success": False, "error": "Invalid Job - posting may be closed"}
            
        error_keywords = ["error occurred", "please try again", "application failed", "could not submit"]
        for kw in error_keywords:
            if kw in modal_text:
                logger.warning("Explicit error detected in modal", text=modal_text[:100])
                return {"success": False, "error": f"Application failed: {modal_text[:50]}"}
        
        # 1c. If a modal is open but has no clear success/error, it might be the form still being open
        # or a post-apply survey. We continue to other checks.

    # 1. Check for visible success overlays / dedicated confirmation areas
    # We avoid broad 'html' search to prevent false positives from 'Related Internships'
    success_selectors = [
        ".success_modal", ".application_submitted_overlay", "#application_submitted_container",
        ".congrats-modal", ".thank-you-page", ".recommended-internships", "#post-apply-modal"
    ]
    for sel in success_selectors:
        if await page.query_selector(f"{sel}:visible"):
            logger.info("Confirmed via success overlay/selector", selector=sel)
            return {"success": True, "ats": "internshala", "verified": True}

    # 1b. Explicit negative signal should win over weak positive heuristics.
    cta_state = await _read_detail_cta_state()
    if cta_state.get("state") == "not_eligible":
        logger.info("Submission rejected by eligibility", text=cta_state.get("text", ""))
        return {"success": False, "ineligible": True, "error": "Internshala marked this job as Not eligible", "verified": True}

    # 2. Applied badge / button state (SCOPED to current internship if possible)
    # If we have internship_id, we look for indicators near links containing that ID
    if internship_id:
        scoped_indicator = await page.evaluate(f"""
            () => {{
                var id = '{internship_id}';
                // Find any element containing the internship ID in its href (the main detail link or similar)
                var links = Array.from(document.querySelectorAll('a[href*="' + id + '"]'));
                for (var link of links) {{
                    // Traversal: look at siblings or parent containers for "Applied" status
                    var container = link.closest('.internship_meta, .card, .individual_internship, .job-card');
                    if (container) {{
                        var text = (container.innerText || '').toLowerCase();
                        if (text.includes('applied') || text.includes('application submitted')) return true;
                    }}
                }}
                // Final fallback: check any button that has "applied" and is not inside "Similar Internships"
                var applied_btns = Array.from(document.querySelectorAll('button'));
                for (var btn of applied_btns) {{
                    if (btn.innerText.toLowerCase().includes('applied')) {{
                        if (!btn.closest('.similar_internships, #similar_internships')) return true;
                    }}
                }}
                return false;
            }}
        """)
        if scoped_indicator:
            logger.info("Confirmed via scoped applied indicator", id=internship_id)
            return {"success": True, "ats": "internshala", "verified": True}
    else:
        # Fallback to broader check if no ID (not ideal)
        if await page.query_selector(".already-applied, .applied-badge, button:has-text('Applied')"):
            logger.info("Confirmed via fallback applied badge")
            return {"success": True, "ats": "internshala", "verified": True}

    # 3. Success text inside any currently-open modal (confirmation overlay)
    modal_text = await page.evaluate("""
        () => {
            var modal = document.querySelector('.modal.show');
            return modal ? (modal.innerText || '').toLowerCase() : '';
        }
    """)
    for sig in _SUCCESS_SIGNALS:
        if sig in modal_text:
            logger.info("Confirmed via modal text", signal=sig)
            return {"success": True, "ats": "internshala", "verified": True}

    # 4. Strict final-state verification with reload.
    # Modal close alone is not proof; we require a clear detail-page state.
    for attempt in range(3):
        await asyncio.sleep(2.0 if attempt == 0 else 1.0)
        final_state = await _read_detail_cta_state()
        logger.info("Post-submit detail state", attempt=attempt, state=final_state.get("state"), text=final_state.get("text", ""))

        if final_state.get("state") == "not_eligible":
            return {"success": False, "ineligible": True, "error": "Internshala marked this job as Not eligible", "verified": True}
        if final_state.get("state") == "applied":
            return {"success": True, "ats": "internshala", "verified": True}

        if attempt < 2:
            try:
                await page.reload(wait_until="domcontentloaded", timeout=30000)
            except Exception as e:
                logger.warning("Post-submit reload failed", error=str(e))

    logger.warning("Submission confirmation still ambiguous after reload checks; will allow retry", url=url, id=internship_id)
    return None


async def _get_form_errors(page) -> str:
    """
    Extract validation error messages from the open application modal.

    FIX: The original code used Python adjacent string literals inside the JS
    string:
        var selector = (
            '.error-message, ...'   ← first string
            '[class*="error"], ...' ← second string, adjacent — Python joins,
        );                            but JS sees two tokens → SyntaxError
    Fixed by using a single unbroken string for the selector.
    """
    return await page.evaluate("""
        () => {
            var modal = document.querySelector('.modal.show');
            if (!modal) return '';
            var selector = '.error-message, .field-error, .invalid-feedback, [class*="error"], [style*="color: red"], [style*="color:red"]';
            var msgs = [];
            modal.querySelectorAll(selector).forEach(function(el) {
                var t = (el.innerText || '').trim();
                if (t && t.length < 300) msgs.push(t);
            });
            return msgs.join(' | ');
        }
    """)


# ─────────────────────────────────────────────────────────────────────────────
#  FILL + SUBMIT (with one retry on validation error)
# ─────────────────────────────────────────────────────────────────────────────

async def _fill_application_form(
    page, profile, resume, settings_obj,
    internship_id=None, job_title_for_verify=None, job=None,
    user_id: str = None,
    user_full_name: str = None,
) -> dict:
    await _screenshot(page, "application_form_open")
    await asyncio.sleep(2)

    profile_summary = _build_profile_summary(profile, job=job)

    # Build a concise job context string passed to every AI answer call
    # so answers reference the actual role, not placeholder text
    job_context_parts = []
    if job:
        if getattr(job, 'title', None):
            job_context_parts.append(f"Role: {job.title}")
        if getattr(job, 'company_name', None):
            job_context_parts.append(f"Company: {job.company_name}")
        # Include a snippet of the job description so AI can write specific answers
        desc = getattr(job, 'description_clean', None) or getattr(job, 'description_raw', None) or ""
        if desc:
            job_context_parts.append(f"Description excerpt:\n{desc[:800]}")
    job_context = "\n".join(job_context_parts)

    cover_answer = (
        profile.professional_summary[:500]
        if profile and profile.professional_summary
        else (
            "I am a motivated and quick learner with strong interest in this role. "
            "I am eager to contribute my skills and grow professionally through this internship."
        )
    )

    await asyncio.sleep(1.5)

    # Log all fields
    form_content = await page.evaluate("""
        () => {
            var fields = [];
            document.querySelectorAll('textarea, input, select').forEach(function(el) {
                fields.push({
                    tag: el.tagName, type: el.type || '',
                    name: el.name || '', id: el.id || '',
                    placeholder: el.placeholder || '',
                    required: el.required,
                    visible: el.offsetParent !== null
                });
            });
            return fields;
        }
    """)
    logger.info("Total form fields (visible + hidden)", count=len(form_content))
    for f in form_content:
        logger.info("  field", tag=f["tag"], type=f["type"], name=f["name"],
                    id=f["id"], visible=f["visible"], required=f["required"])

    await _fill_all_fields(page, profile, resume, settings_obj, profile_summary, cover_answer, job_context=job_context, user_id=user_id, user_full_name=user_full_name, job=job)

    await asyncio.sleep(1)
    await _screenshot(page, "before_submit")

    submit_btn = await _find_submit_button(page)
    if not submit_btn:
        await _screenshot(page, "no_submit_found")
        return {"success": False, "error": "No submit button found in application form"}

    # First submit attempt - try multiple strategies
    submission_successful = False
    submit_responses = []

    def _capture_submit_request(request):
        try:
            url = (request.url or "").lower()
            if "internshala.com" not in url:
                return
            if any(token in url for token in ("apply", "application", "submit", "captcha", "login", "verify")):
                submit_responses.append({
                    "event": "request",
                    "method": getattr(request, "method", None),
                    "url": request.url,
                    "resource_type": getattr(request, "resource_type", None),
                    "post_data": (_truncate(getattr(request, "post_data", None), 3000) if getattr(request, "post_data", None) else None),
                })
        except Exception:
            pass

    def _capture_submit_response(response):
        # Schedule an async task to record richer details (post data + response body)
        try:
            url = (response.url or "").lower()
            if "internshala.com" not in url:
                return
            # Only record potentially relevant endpoints (apply/submit/captcha/login) or non-2xx statuses
            if response.status >= 300 or any(token in url for token in ("apply", "application", "submit", "captcha", "login", "verify")):
                try:
                    asyncio.create_task(_record_submit_response(response))
                except Exception:
                    # Fallback: shallow record if tasks can't be scheduled
                    try:
                        submit_responses.append({
                            "status": response.status,
                            "method": getattr(response.request, "method", None),
                            "url": response.url,
                        })
                    except Exception:
                        pass
        except Exception:
            pass

    async def _record_submit_response(response):
        try:
            req = response.request
            method = getattr(req, "method", None)
            post_data = None
            # Try multiple ways to access post data depending on Playwright version
            try:
                if hasattr(req, "post_data"):
                    maybe = req.post_data
                    post_data = maybe() if callable(maybe) else maybe
            except Exception:
                try:
                    post_data = await req.post_data()
                except Exception:
                    post_data = None

            resp_text = None
            try:
                resp_text = await response.text()
            except Exception:
                resp_text = None

            entry = {
                "status": response.status,
                "method": method,
                "url": response.url,
                "post_data": (post_data[:3000] if isinstance(post_data, str) and len(post_data) > 3000 else post_data),
                "response_text": (resp_text[:3000] if isinstance(resp_text, str) and len(resp_text) > 3000 else resp_text),
            }
            submit_responses.append(entry)
        except Exception:
            pass

    page.on("request", _capture_submit_request)
    page.on("response", _capture_submit_response)

    # Strategy 1: Prefer the site's own submit flow via a native click.
    try:
        await page.evaluate("window.onerror = () => false;")
        await submit_btn.scroll_into_view_if_needed()
        await submit_btn.click(timeout=5000)
        logger.info("Clicked submit via native click")
        submission_successful = True
        await asyncio.sleep(8)  # Wait much longer for form processing
    except Exception as e:
        logger.warning("Native submit click failed", error=str(e))

    # Strategy 2: Fallback to a direct form submission if the click path fails.
    # CRITICAL: Target the APPLICATION form specifically, not the first form on page
    # (which could be a Google Analytics tracking form that navigates to blank page)
    if not submission_successful:
        try:
            submit_via_form = await page.evaluate("""
                () => {
                    // Target application form specifically, never a tracking/analytics form
                    var selectors = [
                        '#application_form',
                        'form[action*="apply"]',
                        'form[action*="application"]',
                        '.modal.show form',
                        '#apply-modal form',
                        '.application-modal form',
                        'form[method="POST"][id]',  // Named form, likely not tracking
                    ];
                    for (var i = 0; i < selectors.length; i++) {
                        var form = document.querySelector(selectors[i]);
                        if (form && form.offsetParent !== null) {  // Check if visible
                            window.onerror = () => false;
                            form.submit();
                            return selectors[i];
                        }
                    }
                    return false;
                }
            """)
            if submit_via_form:
                logger.info("Submitted via form.submit()", form=submit_via_form)
                submission_successful = True
                await asyncio.sleep(8)
        except Exception as e:
            logger.warning("form.submit() failed", error=str(e))

    if not submission_successful:
        try:
            await page.evaluate("function(el) { el.scrollIntoView({block:'center'}); el.click(); }", submit_btn)
            logger.info("Clicked submit via page.evaluate click")
            submission_successful = True
            await asyncio.sleep(8)
        except Exception:
            try:
                await page.evaluate("(el)=>{ ['mousedown','mouseup','click'].forEach(evt=>el.dispatchEvent(new MouseEvent(evt,{bubbles:true,cancelable:true}))); }", submit_btn)
                logger.info("Clicked submit via dispatched events")
                submission_successful = True
                await asyncio.sleep(8)
            except Exception as e:
                logger.warning("All submit click attempts failed", error=str(e))

    if await _has_captcha(page):
        if not await _wait_for_captcha_resolution(page, timeout_s=180):
            page.remove_listener("request", _capture_submit_request)
            page.remove_listener("response", _capture_submit_response)
            return {"success": False, "captcha": True, "error": "reCAPTCHA on submit"}

    await _screenshot(page, "after_submit")

    try:
        submit_dom_snapshot = await page.evaluate("""
            () => {
                var bodyText = (document.body && document.body.innerText ? document.body.innerText : '').replace(/\s+/g, ' ').trim();
                var buttons = Array.from(document.querySelectorAll('button, a[role="button"], input[type="button"], input[type="submit"]'))
                    .filter(function(el) { return !!(el.offsetParent !== null); })
                    .map(function(el) {
                        return (el.innerText || el.value || el.getAttribute('aria-label') || '').replace(/\s+/g, ' ').trim();
                    })
                    .filter(function(text) { return text && text.length < 120; });
                var modalText = '';
                var modal = document.querySelector('.modal.show');
                if (modal) modalText = (modal.innerText || '').replace(/\s+/g, ' ').trim();
                return {
                    url: location.href,
                    title: document.title || '',
                    body_excerpt: bodyText.slice(0, 1200),
                    modal_excerpt: modalText.slice(0, 500),
                    buttons: buttons.slice(0, 15),
                };
            }
        """)
        logger.info("Post-submit DOM snapshot", snapshot=submit_dom_snapshot)
    except Exception as e:
        logger.warning("Could not capture post-submit DOM snapshot", error=str(e))

    result = await _check_submission_result(page, internship_id=internship_id)
    page.remove_listener("request", _capture_submit_request)
    page.remove_listener("response", _capture_submit_response)

    if submit_responses:
        logger.info("Post-submit network responses", responses=submit_responses[:20])

    if result:
        return result

    # Do not retry the submit path here: a second submit can tear down the
    # modal and destroy the evidence we need to diagnose the backend response.
    final_error = await _get_form_errors(page)
    await _screenshot(page, "submit_failed_final")
    return {
        "success": False,
        "error": f"Form submission failed: {final_error[:150] if final_error else 'unknown reason'}",
    }


# ─────────────────────────────────────────────────────────────────────────────
#  MAIN ENTRY POINT
# ─────────────────────────────────────────────────────────────────────────────

async def apply_internshala(page, job, profile, resume, settings_obj, user_id: Optional[str] = None, user_full_name: Optional[str] = None) -> dict:
    context = page.context

    # First try to load from file (legacy)
    cookies = _load_cookies()
    
    # If no file cookies, try to load from database
    if not cookies and user_id:
        try:
            from app.services.cookie_service import cookie_service
            cookies = await cookie_service.get_cookies(user_id, "internshala")
            if cookies:
                logger.info("Loaded cookies from database", count=len(cookies))
        except Exception as e:
            logger.warning("Could not load cookies from database", error=str(e))
    
    if cookies:
        # ── Advanced Stealth Fingerprinting ──────────────────────
        await page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
            Object.defineProperty(navigator, 'languages', { get: () => ['en-IN', 'en-US', 'en'] });
            Object.defineProperty(navigator, 'platform', { get: () => 'Win32' });
            Object.defineProperty(navigator, 'hardwareConcurrency', { get: () => 8 });
            Object.defineProperty(navigator, 'deviceMemory', { get: () => 8 });
            Object.defineProperty(navigator, 'plugins', {
                get: () => [
                    { name: 'Chrome PDF Plugin', filename: 'internal-pdf-viewer' },
                    { name: 'Chrome PDF Viewer', filename: 'mhjfbmdgcfjbbpaeojofohoefgiehjai' },
                    { name: 'Native Client', filename: 'internal-nacl-plugin' }
                ]
            });
            window.chrome = {
                runtime: { connect: () => ({}), sendMessage: () => {} },
                loadTimes: () => ({}),
                csi: () => ({})
            };

            const originalQuery = window.navigator.permissions && window.navigator.permissions.query;
            if (originalQuery) {
                window.navigator.permissions.query = (parameters) =>
                    parameters && parameters.name === 'notifications'
                        ? Promise.resolve({ state: Notification.permission })
                        : originalQuery(parameters);
            }

            delete window.__playwright;
            delete window.__pw_manual;
            delete window.playwrightBinding;
        """)
        # ─────────────────────────────────────────────────────────────

        # Inject cookies first
        try:
            await context.add_cookies(cookies)
            logger.info("Injected cookies", count=len(cookies))
        except Exception as e:
            logger.warning("Could not inject cookies", error=str(e))


    await _goto_lenient(page, "https://internshala.com/", timeout_ms=60000)
    await asyncio.sleep(random.uniform(2, 3))
    await _dismiss_blocking_modals_only(page)

    logged_in = await _is_logged_in(page)
    if not logged_in:
        await page.reload(wait_until="domcontentloaded")
        await asyncio.sleep(2)
        logged_in = await _is_logged_in(page)

    if not logged_in:
        email = getattr(settings_obj, "INTERNShALA_EMAIL", "")
        password = getattr(settings_obj, "INTERNShALA_PASSWORD", "")
        if not email or not password:
            await _take_failure_screenshot(page, "not_logged_in")
            return {"success": False, "error": "Not logged in. Run save_cookies.py."}
        
        logger.info("Session expired/invalid; attempting auto-login")
        result = await _do_login(page, email, password)
        if not result["success"]:
            return result
        
        # Save cookies to file AND database
        await _save_cookies(context)
        if user_id:
            try:
                from app.services.cookie_service import cookie_service
                new_cookies = await context.cookies()
                await cookie_service.save_cookies(user_id, "internshala", new_cookies)
                logger.info("Automatic login cookies saved to database", user_id=user_id)
            except Exception as e:
                logger.warning("Failed to save automatic login cookies to database", error=str(e))

    logger.info("Logged in", status=True)

    # Extract internship ID from URL — handles three URL formats:
    #   /internships/detail/3086913               → pure numeric
    #   /internship/detail/...at-company1773918293 → slug with trailing digits
    #   /internships/detail/isp_v_57              → short slug (no 7-digit number)
    slug = job.source_url.rstrip("/").split("/")[-1]
    nums = re.findall(r"\d{7,}", slug)
    if nums:
        internship_id = nums[-1]   # last 7+ digit number in slug
    else:
        # Fewer-digit numeric ID (e.g. 3086913) or slug like isp_v_57
        nums6 = re.findall(r"\d{6,}", slug)
        if nums6:
            internship_id = nums6[-1]
        else:
            internship_id = slug   # use full slug — href matching still works
    logger.info("Internship ID extracted", internship_id=internship_id, slug=slug)

    logger.info("Loading detail page", url=job.source_url)
    await _goto_lenient(page, job.source_url, timeout_ms=60000)

    await asyncio.sleep(2)
    
    # First check if we got an error/crashed page instead of job content
    raw_html = await page.content()
    raw_lower = raw_html.lower()
    logger.debug("raw_html length", length=len(raw_html))
    
    # Check for error/crashed/bot detection pages
    error_indicators = [
        "access denied", "blocked", "suspicious activity",
        "rate limit", "too many requests", "captcha",
        "verify you are human", "cloudflare", 
        "something went wrong", "server error", "500",
        "we're sorry", "page not found", "404"
    ]
    
    # Check for employer blocked modal specifically - employer has closed applications
    if "employer_blocked_error_modal" in raw_lower:
        logger.debug("Found employer_blocked_error_modal")
        blocked_modal = await page.query_selector("#employer_blocked_error_modal")
        if blocked_modal:
            is_visible = await blocked_modal.is_visible()
            logger.debug("blocked_modal visible", is_visible=is_visible)
            if is_visible:
                modal_text = await blocked_modal.inner_text()
                logger.debug("Blocked modal text", modal_text=modal_text[:200])
                return {"success": False, "error": "Employer has closed applications for this internship"}
    
    # Check for rate limiting
    if "too many requests" in raw_lower:
        logger.warning("Detected rate limiting")
        return {"success": False, "error": "Internshala rate limiting - try again later"}

    try:
        await page.wait_for_selector(
            ".internship_details, #internship_detail_container, "
            ".detail_view, .job-detail, [class*='internship-detail'], "
            ".internship-overview-main-container",
            timeout=10000,
        )
        logger.info("Job content loaded")
    except Exception:
        logger.warning("Job content container not found — proceeding anyway")

    await asyncio.sleep(2)
    await _dismiss_blocking_modals_only(page)
    await asyncio.sleep(0.5)
    await _dismiss_blocking_modals_only(page)

    if await _is_on_login_wall(page):
        # Double check - sometimes a modal flickers during load
        logger.info("Possible login wall detected - waiting 5s to confirm")
        await asyncio.sleep(5)
        await _dismiss_blocking_modals_only(page)
        if await _is_on_login_wall(page):
            # Triple check - are we actually logged in despite the modal?
            if not await _is_logged_in(page):
                logger.warning("Confirmed session expired on login wall")
                return {"success": False, "error": "Session expired. Run save_cookies.py."}
            else:
                logger.info("Login wall was a false positive - proceeding")

    await _screenshot(page, "detail_page")

    # Scoped already-applied check
    if await _is_already_applied(page):
        logger.info("Already applied — skipping")
        return {
            "success": True, "already_applied": True,
            "ats": "internshala", "verified": True,
            "note": "Already applied — DB synced, no new submission",
        }

    html_check = (await page.content()).lower()
    logger.debug("html_check length", length=len(html_check))
    logger.debug("html_check eligibility check", not_eligible=('not eligible' in html_check))
    
    # Check for explicit eligibility rejection - look for specific banner/text
    # The message "As your Internshala resume lists X as your location, you are not eligible" is the key indicator
    eligibility_rejection_patterns = [
        "as your internshala resume lists",
        "you are not eligible for this internship",
        "you're not eligible for this internship",
        "you do not meet the eligibility criteria for this internship",
    ]
    
    # Check if there's a visible rejection message in the eligibility section
    try:
        who_can_apply = await page.query_selector('.who_can_apply, .eligibility-section, [class*="who_can"]')
        if who_can_apply:
            section_text = (await who_can_apply.inner_text() or "").lower()
            logger.debug("who_can_apply section eligibility check", not_eligible=('not eligible' in section_text))
            if "as your internshala resume lists" in section_text:
                logger.debug("Location-based ineligibility detected")
                return {"success": False, "ineligible": True, "error": "Not eligible - profile location does not match job requirements"}
    except Exception as e:
        logger.debug("Error checking eligibility section", error=str(e))
    
    # Check for eligibility banner element
    eligibility_banner = await page.query_selector(
        ".not-eligible, .ineligible, [class*='not-eligible'], [class*='ineligible']"
    )
    logger.debug("eligibility_banner state", found=(eligibility_banner is not None))
    if eligibility_banner:
        is_visible = await eligibility_banner.is_visible()
        logger.debug("eligibility_banner visible", is_visible=is_visible)
        if is_visible:
            banner_text = await eligibility_banner.inner_text() or ""
            logger.debug("banner_text", text=banner_text[:100])
            logger.warning("Eligibility banner found - marking as ineligible", text=banner_text[:200])
            return {"success": False, "ineligible": True, "error": "Not eligible - Internshala profile requirements not met"}
    
    if any(x in html_check for x in (
        "hiring closed", "no longer accepting", "internship closed", "applications closed"
    )):
        return {"success": False, "error": "Internship is no longer accepting applications"}

    # Find Apply button (poll up to 10 s)
    apply_btn = None
    
    # Debug: get page content for analysis
    page_html = await page.content()
    logger.info("Page content length for debug", length=len(page_html))
    
    # Check if already applied via scoped check
    if await _is_already_applied(page):
        logger.info("User already applied to this internship")
        return {"success": True, "already_applied": True, "ats": "internshala", "verified": True}
    
    for attempt in range(20):
        # Prefer specific button IDs first
        if not apply_btn:
            for btn_id in ("easy_apply_button", "apply_button", "btn-apply", "apply_now_button", "apply-button", "easy-apply", "make_application"):
                el = await page.query_selector(f"#{btn_id}")
                if el and await el.is_visible():
                    apply_btn = el
                    logger.info("Found apply button by ID", id=btn_id)
                    break
        if not apply_btn:
            for sel in (
                ".top_apply_now_cta", "#make_application", "#easy_apply_button",
                "button:has-text('Apply now')", "button.btn-primary:has-text('Apply')",
                "button:has-text('Easy Apply')", "button:has-text('Apply Now')",
                "a:has-text('Apply Now')", "a:has-text('Easy Apply')",
                # Additional Internshala-specific selectors
                "a.button_apply_big", "a.apply-button",
                "button[type='submit']:has-text('Apply')",
                "a:has-text('Apply for this internship')",
                "button:has-text('Apply for this internship')",
                "a.cta-button", "button.cta-button",
                # More Internshala selectors based on current UI
                "a[id*='apply']", "button[id*='apply']",
                ".apply-now-btn", ".applyButton", ".apply_btn",
                "a[class*='apply']", "button[class*='apply']",
                # Generic fallback
                ".apply-btn", ".application-btn", "[class*='apply-button']",
                "[data-testid*='apply']", "button[data-testid*='apply']",
            ):
                el = await page.query_selector(sel)
                if el and await el.is_visible() and len(((await el.inner_text()) or "").strip()) < 30:
                    apply_btn = el
                    logger.info("Found apply button by text", selector=sel)
                    break
        if apply_btn:
            break
        await asyncio.sleep(0.5)
        if attempt == 5:
            await _dismiss_blocking_modals_only(page)
        if attempt == 10:
            # Debug: get the action area HTML
            action_area = await page.query_selector(
                ".internship_details_container, .job-detail-ctc, .detail-view, main"
            )
            if action_area:
                logger.info("Action area found, taking debug screenshot")
                await page.screenshot(path=str(SCREENSHOT_DIR / f"debug_apply_{internship_id}.png"))

    if not apply_btn:
        await _screenshot(page, "no_apply_button")
        return {"success": False, "error": "No Apply button found on detail page"}

    # Check if button is disabled with specific message before trying to click
    btn_text = ((await apply_btn.inner_text()) or "").strip().lower()
    is_disabled = await apply_btn.get_attribute("disabled")
    
    logger.info("Checking apply button state", text=btn_text[:100], has_disabled_attr=is_disabled is not None)
    
    # DEBUG: Log the full button HTML for analysis
    btn_html = (await apply_btn.evaluate("function(el) { return el.outerHTML; }")) or ""
    logger.info("Apply button HTML", html=btn_html[:500])
    
    # Check for "already applied" on button text (this is scoped to the button we found)
    if "already applied" in btn_text or (is_disabled and "applied" in btn_text):
        logger.info("Already applied to this internship (detected on button)")
        return {"success": True, "already_applied": True, "ats": "internshala", "verified": True}
    
    # Check for "closed" state - don't try to click if closed
    closed_phrases = ["closed", "no longer accepting", "not accepting"]
    if any(p in btn_text for p in closed_phrases):
        logger.warning("Internship is closed for applications", text=btn_text)
        return {"success": False, "error": "Internship is closed for applications"}
    
    # Check if button shows "not eligible" - return ineligible immediately
    btn_text_lower = btn_text.lower()
    logger.debug("Button text", text=btn_text)
    logger.debug("Button disabled", is_disabled=is_disabled)
    logger.debug("Button eligibility check", not_eligible=('not eligible' in btn_text_lower))
    
    # Check ALL possible places that could return ineligible
    # First check the button text
    if "not eligible" in btn_text_lower:
        logger.debug("Returning ineligible from button text check")
        logger.warning("Button shows 'not eligible' - marking as ineligible immediately")
        return {"success": False, "ineligible": True, "error": "Not eligible - Internshala profile requirements not met"}
    
    # Check for other blocked states - button might show different text when disabled
    blocked_phrases = ["sign in to apply", "login to apply", "register to apply"]
    if any(phrase in btn_text for phrase in blocked_phrases):
        logger.warning("Button shows login required - checking session")
        # Try to see if this is a login wall - reload and check
        await page.reload(wait_until="domcontentloaded")
        await asyncio.sleep(2)
        if await _is_on_login_wall(page):
            return {"success": False, "error": "Session expired. Run save_cookies.py."}
        return {"success": False, "ineligible": True, "error": "Login required to apply"}
    
    # Check if button is disabled but not "not eligible" - still try to click
    if is_disabled is not None:
        logger.warning("Button is disabled but not showing 'not eligible' - will attempt click anyway")
        btn_was_disabled = True
    else:
        btn_was_disabled = False

    # Skip waiting loop for disabled buttons - go directly to click attempt
        # Try to scroll button into view and wait for it to be enabled
        try:
            await apply_btn.scroll_into_view_if_needed()
            await page.evaluate("function(el) { el.scrollIntoView({behavior: 'smooth', block: 'center'}); }", apply_btn)
            await asyncio.sleep(2)
            
            # Wait for button to be enabled (max 10 seconds)
            for wait_attempt in range(20):
                is_disabled = await apply_btn.get_attribute("disabled")
                is_enabled = await apply_btn.is_enabled()
                
                if is_enabled and not is_disabled:
                    logger.info("Apply button is now enabled")
                    break
                
                # If button has "apply" text and looks like the right button, try JS click anyway
                btn_text = ((await apply_btn.inner_text()) or "").lower()
                if "apply" in btn_text and len(btn_text) < 30:
                    logger.info("Button has apply text but reports disabled - attempting JS click anyway")
                    break
                    
                await asyncio.sleep(0.5)
        except Exception as e:
            logger.warning("Could not wait for button enablement", error=str(e))

    href = await apply_btn.get_attribute("href") or ""
    logger.info("Apply button", href=href)

    # Check for external redirect URLs - these are NOT Internshala applications
    external_domains = ["appcast.io", ".applytojob", "careerbliss", "indeed", "linkedin", "glassdoor", "naukri", "monster"]
    if href and any(domain in href.lower() for domain in external_domains):
        logger.warning("External application URL detected - skipping", url=href)
        return {"success": False, "error": "External job posting - requires manual application", "external": True}

    if False and href and href not in ("#", "") and "javascript" not in href:
        full_url = href if href.startswith("http") else f"https://internshala.com{href}"
        logger.info("Navigating to apply URL", url=full_url)
        await _goto_lenient(page, full_url, timeout_ms=60000)
        await asyncio.sleep(2)
        await _dismiss_blocking_modals_only(page)
    else:
        logger.info("Clicking Apply (AJAX modal)")

        # Human-like pre-click motion to avoid a cold, direct apply trigger.
        try:
            for _ in range(3):
                await page.mouse.wheel(0, random.randint(120, 320))
                await asyncio.sleep(random.uniform(0.2, 0.5))
            await page.mouse.wheel(0, -random.randint(80, 220))
            await asyncio.sleep(random.uniform(0.3, 0.7))
            bbox = await apply_btn.bounding_box()
            if bbox:
                await page.mouse.move(
                    bbox["x"] + random.uniform(-40, 40),
                    bbox["y"] + random.uniform(20, 70),
                )
                await asyncio.sleep(random.uniform(0.25, 0.6))
                await page.mouse.move(
                    bbox["x"] + bbox["width"] / 2,
                    bbox["y"] + bbox["height"] / 2,
                )
                await asyncio.sleep(random.uniform(0.15, 0.4))
        except Exception as e:
            logger.debug("Human-like pre-click motion skipped", error=str(e))
        
        # SAFETY: Strip href from parent <a> tags to absolutely prevent native fallback navigation
        try:
            await page.evaluate("""(btn) => {
                let a = btn.closest('a');
                if (a) {
                    a.dataset.originalHref = a.getAttribute('href');
                    a.removeAttribute('href');
                }
            }""", apply_btn)
        except Exception as e:
            logger.warning("Failed to strip href from parent anchor", error=str(e))
            
        await asyncio.sleep(1)
        
        # Strategy 1: Directly invoke Internshala's own JS modal function
        # This bypasses click-detection entirely by calling the same function the button calls
        logger.info("Attempting direct JS modal trigger")
        click_success = False
        try:
            js_modal_result = await page.evaluate(f"""async () => {{
                const internshipId = '{internship_id}';
                
                // Try Internshala's known global functions
                if (typeof openApplicationModal === 'function') {{
                    openApplicationModal(internshipId);
                    return 'openApplicationModal';
                }}
                if (typeof apply_now === 'function') {{
                    apply_now(internshipId);
                    return 'apply_now';
                }}
                // Try jQuery trigger
                if (typeof $ !== 'undefined') {{
                    const btn = $('.top_apply_now_cta');
                    if (btn.length) {{
                        btn.trigger('click');
                        return 'jquery_trigger';
                    }}
                }}
                // Trigger all click handlers registered on the button
                const btn = document.querySelector('.top_apply_now_cta');
                if (btn) {{
                    const events = ['mousedown', 'mouseup', 'click'];
                    events.forEach(evt => {{
                        btn.dispatchEvent(new MouseEvent(evt, {{bubbles: true, cancelable: true, view: window}}));
                    }});
                    return 'dispatched_events';
                }}
                return 'no_method_found';
            }}""")
            logger.info("JS modal trigger result", result=js_modal_result)
            click_success = True
        except Exception as js_e:
            logger.warning("JS modal trigger failed", error=str(js_e))
        
        # Strategy 2: Physical click as fallback
        if not click_success:
            try:
                await apply_btn.click(timeout=3000)
                click_success = True
                logger.info("Physical click succeeded")
            except Exception as e:
                logger.warning("Physical click failed", error=str(e))
        
        await asyncio.sleep(3)
        
        # DIAGNOSTIC: Capture console messages and errors
        page_console_logs = []
        page_errors = []
        
        def on_console_msg(msg):
            page_console_logs.append({"type": msg.type, "text": msg.text})
        
        def on_page_error(error):
            page_errors.append(str(error))
        
        page.on("console", on_console_msg)
        page.on("pageerror", on_page_error)
        
        # Wait a bit more for async JS to finish
        await asyncio.sleep(2)
        
        # Log console output
        if page_console_logs:
            logger.info("Page console messages after click", messages=page_console_logs[:10])
        if page_errors:
            logger.warning("Page errors after click", errors=page_errors[:5])
        
        # Check what's on the page after clicking
        page_content = await page.content()
        page_html = page_content.lower() if page_content else ""
        current_url = page.url
        
        logger.info("After click", url=current_url, has_not_eligible="not eligible" in page_html)
        
        # Check if navigation happened (some internships navigate to a new page)
        if "apply" in current_url or "application" in current_url:
            logger.info("URL changed to application page")
            # This is good - we're on the application form page
            modal_opened = True
        else:
            # Check if any modal or form appeared
            modal_opened = False
            has_error = False
            checked_without_form = 0
            
            for check_num in range(30):  # Longer wait
                await asyncio.sleep(0.5)
                
                # Check for any application form
                modal = await page.query_selector(
                    "#application_form, .application-modal, form[id*='apply'], "
                    ".modal.show form, .modal[style*='block'] form, .apply-modal, #easy-apply-modal, .application-form-container, "
                    "#apply_now_modal, .internship-apply-modal, .modal-content form"
                )
                visible_tas = [ta for ta in await page.query_selector_all("textarea") if await ta.is_visible()]
                
                # Also check for any form with inputs
                visible_inputs = await page.query_selector_all("input:not([type='hidden'])")
                visible_inputs = [inp for inp in visible_inputs if await inp.is_visible()]
                
                # Check for "Proceed" or "Update" buttons that might block the form
                proceed_text_btn = await page.query_selector("button:has-text('Proceed'), button:has-text('Update'), .btn-primary:has-text('Proceed')")
                
                logger.info(f"Modal check #{check_num}", modal=bool(modal), textareas=len(visible_tas), inputs=len(visible_inputs), has_proceed=bool(proceed_text_btn))
                
                if modal or visible_tas or len(visible_inputs) > 3:
                    modal_opened = True
                    logger.info("Application modal/form opened", inputs=len(visible_inputs))
                    break
                
                if proceed_text_btn and await proceed_text_btn.is_visible():
                    logger.info("Found potential blocker button - clicking it")
                    await proceed_text_btn.click()
                    await asyncio.sleep(1)
                
                # If no form found after 5 checks, try clicking the button again
                if check_num == 10 and not modal_opened:
                    logger.info("Modal not opening - retrying Apply click")
                    try:
                        await page.evaluate("""() => {
                            const btn = document.querySelector('.top_apply_now_cta') || document.querySelector('button:has-text("Apply now")');
                            if (btn) btn.click();
                        }""")
                    except Exception:
                        pass
                
                # If no form found after several checks, try refreshing the page - sometimes form loads after a moment
                if check_num == 15 and not modal_opened:
                    logger.info("No form found after 15 checks - refreshing page")
                    await page.reload(wait_until="domcontentloaded")
                    await asyncio.sleep(2)
                    
                # If no form found after 5 checks, try direct navigation as a strong fallback
                if check_num == 5 and not modal_opened:
                    logger.info("Modal not opening - trying direct navigate as fallback")
                    current_url = page.url
                    if "internshala.com/internship/detail/" in current_url:
                        # 1. Jiggle mouse near the button first to trigger any lazy-load behavioral scripts
                        try:
                            bbox = await apply_btn.bounding_box()
                            if bbox:
                                await page.mouse.move(bbox['x'] - 10, bbox['y'] - 10)
                                await asyncio.sleep(0.1)
                                await page.mouse.move(bbox['x'] + bbox['width'] + 5, bbox['y'] + 5)
                                await asyncio.sleep(0.1)
                                await page.mouse.move(bbox['x'] + bbox['width']/2, bbox['y'] + bbox['height']/2)
                        except Exception: pass

                        apply_url = current_url.replace("/internship/detail/", "/internship/apply/") + "/"
                        logger.info("Navigating directly to apply URL", url=apply_url)
                        try:
                            # Use a longer timeout and wait for load
                            await _goto_lenient(page, apply_url, timeout_ms=60000)
                            await asyncio.sleep(4) # Give it plenty of time to render
                            
                            # Check if we were redirected back to the home or detail page
                            if "apply" not in page.url:
                                logger.warning("Redirected away from apply page - session may be restricted", final_url=page.url)
                                break

                            # Re-check for form on the new page
                            has_form = await page.query_selector("form, textarea, input[type='text']")
                            if has_form:
                                logger.info("Application form found after direct navigation")
                                modal_opened = True
                                break
                            
                            # Check for "Not Eligible" or "Already Applied"
                            page_text = (await page.content()).lower()
                            if "already applied" in page_text or "not eligible" in page_text:
                                logger.warning("Direct URL shows not eligible or already applied")
                                break
                        except Exception as nav_err:
                            logger.warning("Direct navigation failed", error=str(nav_err))
                    
                # Check for error messages
                error_elements = await page.query_selector_all(
                    ".error-message, .alert-danger, [class*='error'], .warning-message, .not-eligible, [class*='not-eligible']"
                )
                # Check for visible error elements (but don't fail immediately)
                has_error = False
                for err in error_elements:
                    if await err.is_visible():
                        err_text = (await err.inner_text()) or ""
                        logger.warning("Error element found after click", text=err_text[:100])
                        has_error = True
    
    # ─ CRITICAL FIX: After modal confirms open, check if it's the LOGIN modal
    # If login modal appears instead of app form, session CSRF is expired
    if modal_opened:
        try:
            password_field = await page.query_selector(".modal.show input[type='password'], .modal.show input[name='password']")
            if password_field:
                logger.error("LOGIN MODAL opened instead of application form - session CSRF expired")
                
                # Close this modal
                try:
                    close_btn = await page.query_selector(".modal.show button[aria-label='Close'], .modal.show .close, .modal.show button.close")
                    if close_btn:
                        await close_btn.click()
                        await asyncio.sleep(1)
                except Exception:
                    pass
                
                # Re-navigate to homepage to refresh session
                logger.info("Refreshing session by navigating to Internshala homepage")
                await _goto_lenient(page, "https://internshala.com/", timeout_ms=30000)
                await asyncio.sleep(3)
                
                # Verify we're still logged in
                if not await _is_logged_in(page):
                    return {"success": False, "error": "Session lost after CSRF refresh - need to re-authenticate"}
                
                logger.info("Session refreshed - retrying apply on internship")
                # Navigate back to internship detail page
                try:
                    await _goto_lenient(page, url, timeout_ms=60000)
                    await asyncio.sleep(2)
                except Exception:
                    logger.warning("Could not navigate back to internship detail page")
                    return {"success": False, "error": "Could not return to internship after session refresh"}
                
                # One more try: click Apply again
                apply_btn_retry = await page.query_selector(".top_apply_now_cta, .apply_now_cta, button:has-text('Apply now')")
                if apply_btn_retry:
                    try:
                        await apply_btn_retry.click(timeout=5000)
                        logger.info("Retried apply click after session refresh")
                        await asyncio.sleep(4)
                        # Re-check if modal is now the application form
                        modal_check = await page.query_selector(".modal.show")
                        if modal_check:
                            # Check again for password field
                            still_login = await page.query_selector(".modal.show input[type='password']")
                            if still_login:
                                logger.error("Login modal STILL appearing after session refresh - bot detection active")
                                return {"success": False, "error": "Internshala login modal persists - bot detection active", "bot_detected": True}
                            logger.info("Application form now open after session refresh")
                            # Continue with form filling
                        else:
                            logger.warning("No modal after retry - internship may require additional steps")
                            return {"success": False, "error": "Modal did not reopen after session refresh"}
                    except Exception as retry_err:
                        logger.warning("Retry apply click failed", error=str(retry_err))
                        return {"success": False, "error": "Could not retry apply after session refresh"}
                else:
                    logger.error("Apply button not found on retry")
                    return {"success": False, "error": "Apply button not found on detail page retry"}
        except Exception as session_err:
            logger.error("Session refresh check failed", error=str(session_err))
            # Don't completely fail - continue with current state
            pass
            
            if not modal_opened:
                # DIAGNOSTIC: Comprehensive logging of what's on the page
                try:
                    final_html = await page.content()

                    # Count different element types
                    all_forms = await page.query_selector_all("form")
                    all_modals = await page.query_selector_all(".modal, [role='dialog']")
                    all_iframes = await page.query_selector_all("iframe")
                    all_buttons = await page.query_selector_all("button")

                    form_count = len(all_forms)
                    modal_count = len(all_modals)
                    iframe_count = len(all_iframes)
                    button_count = len(all_buttons)

                    logger.warning(
                        "Modal fail comprehensive diagnostic",
                        url=page.url,
                        form_count=form_count,
                        modal_count=modal_count,
                        iframe_count=iframe_count,
                        button_count=button_count,
                        page_title=await page.title(),
                        console_logs=page_console_logs[-3:] if page_console_logs else [],
                        page_errors=page_errors[-3:] if page_errors else [],
                        html_length=len(final_html),
                        html_sample=final_html[1000:3000].replace('\n', ' '),
                    )
                except Exception as e:
                    logger.error("Failed to gather diagnostics", error=str(e))

                # Some Internshala flows open an interstitial page with a "Proceed"
                # button instead of rendering the application form immediately. Give
                # that path a chance before failing the application.
                proceed_btn = await page.query_selector(
                    "button:has-text('Proceed to application'), button:has-text('Update resume and proceed'), .education_incomplete_proceed_btn, #resume_proceed_btn"
                )
                if proceed_btn and await proceed_btn.is_visible():
                    logger.info("Found interstitial 'Proceed' button after modal failure - clicking it")
                    try:
                        await proceed_btn.click(timeout=5000)
                        await asyncio.sleep(2)
                        for _ in range(20):
                            if await page.query_selector("#application_form, .application-modal, form[id*='apply']"):
                                modal_opened = True
                                break
                            await asyncio.sleep(0.5)
                    except Exception as e:
                        logger.warning("Could not click interstitial proceed button", error=str(e))

                if not modal_opened:
                    await _screenshot(page, "modal_did_not_open")
                    return {"success": False, "error": "Application modal did not open after clicking Apply"}
    if "/registration/" in page.url:
        try:
            page_text = await page.evaluate("document.body.innerText")
            logger.warning("Redirected to registration page. Page content:", text=page_text[:1500])
            
            # Check for specific blocks like mobile verification
            if "verify" in page_text.lower() and "mobile" in page_text.lower():
                return {"success": False, "error": "Internshala is asking for mobile verification due to high-risk login (VPS IP)."}
        except Exception:
            pass
            
        return {"success": False, "error": "Profile incomplete on Internshala or blocked by step-up verification. Please check the logs."}

    if not modal_opened and await _is_on_login_wall(page):
        return {"success": False, "error": "Login wall after apply click. Session expired."}

    try:
        return await _fill_application_form(
            page, profile, resume, settings_obj,
            internship_id=internship_id,
            job_title_for_verify=(getattr(job, "title", "") or "").lower()[:25],
            job=job,
            user_id=user_id,
            user_full_name=user_full_name,
        )
    except ValueError as e:
        if "Login modal" in str(e):
            logger.warning("Login modal detected during form fill", error=str(e))
            return {"success": False, "error": "Internshala anti-bot detection: login modal served instead of application form", "bot_detected": True}
        raise   