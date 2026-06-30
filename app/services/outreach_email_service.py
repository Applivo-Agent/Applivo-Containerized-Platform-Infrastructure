"""
app/services/outreach_email_service.py
───────────────────────────────────────
Email Composer + Quality Review agents for the Outreach Platform.
Generates personalized outreach emails and scores them before user approval.
"""
from __future__ import annotations

import json
import re
from typing import Optional
import structlog

from app.services.ai_router import chat_complete

logger = structlog.get_logger()

# ── Spam signal words (hard block) ───────────────────────────────────────────

SPAM_WORDS = [
    "urgent", "act now", "limited time", "free", "guarantee",
    "no obligation", "click here", "buy now", "order now",
    "make money", "work from home", "earn extra",
]

BAD_PHRASES = [
    "i hope this email finds you well",
    "i've been following your company for years",
    "i'm passionate about",
    "i would be a great fit",
    "synergy", "leverage", "circle back", "touch base", "ping you",
]

GOAL_CONTEXT = {
    "job_search": "The user is actively looking for a job and wants to land an interview.",
    "networking": "The user wants to build a professional relationship without immediately asking for a job.",
    "mentorship": "The user is looking for mentorship and career guidance from a senior professional.",
    "referral": "The user is asking a mutual connection for a referral to the company.",
    "research": "The user is researching the company and its work out of genuine curiosity.",
    "conference": "The user met or wants to connect with this person around a conference or event.",
}


# ── Main email generation function ────────────────────────────────────────────

async def generate_outreach_email(
    company_name: str,
    contact_name: Optional[str],
    contact_title: Optional[str],
    intelligence_report: Optional[dict],
    user_name: str,
    user_career_summary: str,
    user_skills: list[str],
    campaign_goal: str = "JOB_SEARCH",
    sequence_position: int = 1,
    voice_style: str = "professional",
    previous_email_summary: Optional[str] = None,
    job_description: Optional[str] = None,
) -> dict:
    """
    Generate a complete outreach email package:
      - subject (primary choice)
      - subject_options (5 alternatives)
      - body (the email body text)
      - personalization_hooks (list of hooks used)
      - quality_score + quality_breakdown
      - reply_probability estimate
    """
    # Build personalization context from intelligence report
    hooks_text = ""
    if intelligence_report:
        hooks = intelligence_report.get("personalization_hooks", [])
        if hooks:
            hooks_text = "PERSONALIZATION HOOKS AVAILABLE:\n" + "\n".join(
                f"- {h.get('hook', '')}: suggest saying '{h.get('suggested_reference', '')}'"
                for h in hooks[:5]
            )

    company_context = ""
    if intelligence_report:
        company_context = f"""COMPANY INTELLIGENCE:
Executive summary: {intelligence_report.get('executive_summary', '')}
Industry: {intelligence_report.get('industry', '')} | Stage: {intelligence_report.get('stage', '')} | Size: {intelligence_report.get('size_estimate', '')}
Tech stack: {', '.join(intelligence_report.get('tech_stack', [])[:8])}
Remote policy: {intelligence_report.get('remote_policy', 'unknown')}
Outreach angle: {intelligence_report.get('outreach_recommendation', {}).get('primary_angle', '')}
Tone recommendation: {intelligence_report.get('outreach_recommendation', {}).get('tone', 'professional')}
Avoid: {', '.join(intelligence_report.get('outreach_recommendation', {}).get('avoid', []))}"""

    goal_desc = GOAL_CONTEXT.get(campaign_goal, GOAL_CONTEXT["job_search"])

    followup_context = ""
    if sequence_position > 1 and previous_email_summary:
        followup_context = f"""
FOLLOW-UP CONTEXT (this is email #{sequence_position} in the sequence):
Previous email summary: {previous_email_summary}
This follow-up should NOT recap the previous email. It should add new value:
- Position 2: Share a relevant insight, article, or project update
- Position 3+: Brief, gracious final touchpoint — leave door open professionally"""

    jd_context = ""
    if job_description:
        jd_context = f"\nJOB DESCRIPTION (tailor email to this role):\n{job_description[:800]}"

    voice_instruction = {
        "professional": "Write in a polished, confident professional tone.",
        "conversational": "Write in a warm, human, conversational tone — like a message from a smart colleague.",
        "formal": "Write in a formal, structured business tone.",
        "technical": "Use precise technical language — this recipient is likely an engineer.",
        "startup": "Write with energy and directness. Bias toward short punchy sentences.",
    }.get(voice_style, "Write in a confident professional tone.")

    contact_salutation = f"Hi {contact_name.split()[0]}," if contact_name else "Hi,"

    prompt = f"""You are an expert career coach and email writer helping a job seeker write a highly personalized outreach email.

GOAL: {goal_desc}

USER:
Name: {user_name}
Career summary: {user_career_summary}
Key skills: {', '.join(user_skills[:15])}

TARGET:
Company: {company_name}
Contact: {contact_name or 'Unknown'} ({contact_title or 'Recruiter'})

{company_context}

{hooks_text}
{followup_context}
{jd_context}

WRITING RULES (strictly enforce):
- Maximum {180 if sequence_position == 1 else 120} words in the email body
- Must reference at least ONE specific detail about {company_name} (not generic praise)
- End with ONE clear, low-commitment CTA (suggest a call, ask one question, etc.)
- {voice_instruction}
- NEVER use: "I hope this email finds you well", "I'm passionate about", "I would be a great fit", "synergy", "touch base", "circle back"
- Do NOT mention salary, benefits, or equity in first outreach
- Sound like a real human wrote this, not an AI
- Start salutation: {contact_salutation}
- Sign off: Best,\\n{user_name}

Return ONLY valid JSON with this exact structure:
{{
  "subject": "the best subject line",
  "subject_options": [
    "option 1",
    "option 2",
    "option 3",
    "option 4",
    "option 5"
  ],
  "body": "the full email body text (plain text, no HTML, include salutation and sign-off)",
  "personalization_hooks_used": [
    "specific detail used from company research"
  ],
  "word_count": 0,
  "cta_type": "request_call / ask_question / share_work / open_question"
}}

Return ONLY JSON. No markdown, no preamble."""

    try:
        raw = await chat_complete(
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1200,
            endpoint="outreach_compose",
        )
        raw = raw.strip()
        if raw.startswith("```"):
            raw = re.sub(r"^```[a-z]*\n?", "", raw)
            raw = re.sub(r"\n?```$", "", raw)
        email_data = json.loads(raw)
    except Exception as e:
        logger.error("Email generation failed", error=str(e))
        email_data = _fallback_email(company_name, contact_name, user_name, contact_salutation)

    # Compute actual word count
    body = email_data.get("body", "")
    email_data["word_count"] = len(body.split())

    # ── Quality scoring ────────────────────────────────────────────────────────
    quality = _score_quality(email_data, intelligence_report)
    email_data["quality_score"] = quality["total"]
    email_data["quality_breakdown"] = quality["breakdown"]
    email_data["quality_suggestions"] = quality["suggestions"]

    # ── Reply probability ──────────────────────────────────────────────────────
    email_data["reply_probability"] = _estimate_reply_probability(
        quality["total"], len(email_data.get("personalization_hooks_used", [])),
        sequence_position, campaign_goal
    )

    return email_data


def _fallback_email(company_name: str, contact_name: Optional[str], user_name: str, salutation: str) -> dict:
    body = f"""{salutation}

I came across {company_name} and was impressed by the work your team is doing.

I'm a software engineer with experience building production systems and I'd love to learn more about opportunities on your team.

Would a brief conversation make sense? Happy to share more about my background.

Best,
{user_name}"""
    return {
        "subject": f"Quick note from a {company_name} admirer",
        "subject_options": [
            f"Quick note from a {company_name} admirer",
            f"Engineer interested in {company_name}",
            f"Your team caught my attention",
            f"Reaching out about {company_name} opportunities",
            f"Brief intro — software engineer interested in your work",
        ],
        "body": body,
        "personalization_hooks_used": [],
        "word_count": len(body.split()),
        "cta_type": "request_call",
    }


def _score_quality(email_data: dict, intelligence_report: Optional[dict]) -> dict:
    """Score the email on 7 dimensions and return total + breakdown + suggestions."""
    body = email_data.get("body", "").lower()
    subject = email_data.get("subject", "")
    word_count = email_data.get("word_count", 0)
    hooks_used = email_data.get("personalization_hooks_used", [])
    suggestions = []

    # 1. Personalization (0-25)
    personalization = 10
    if hooks_used:
        personalization = min(25, 10 + len(hooks_used) * 8)
    if intelligence_report and any(
        h.get("hook", "").lower()[:20] in body
        for h in intelligence_report.get("personalization_hooks", [])
    ):
        personalization = min(25, personalization + 5)
    if personalization < 18:
        suggestions.append("Add more company-specific details to increase personalization.")

    # 2. Length (0-20)
    if 100 <= word_count <= 180:
        length_score = 20
    elif 80 <= word_count <= 220:
        length_score = 15
    elif word_count < 80:
        length_score = 8
        suggestions.append("Email is too short — add more context about your background.")
    else:
        length_score = 10
        suggestions.append("Email is too long — aim for under 180 words for cold outreach.")

    # 3. Spam signals (0-20)
    spam_score = 20
    for word in SPAM_WORDS:
        if word in body:
            spam_score -= 5
            suggestions.append(f"Remove spam-signal word: '{word}'")
    for phrase in BAD_PHRASES:
        if phrase in body:
            spam_score -= 4
            suggestions.append(f"Remove overused phrase: '{phrase}'")
    spam_score = max(0, spam_score)

    # 4. CTA clarity (0-15)
    cta_signals = ["call", "chat", "conversation", "connect", "question", "thoughts", "available", "minutes"]
    cta_score = 15 if any(s in body for s in cta_signals) else 5
    if cta_score < 10:
        suggestions.append("Add a clear call-to-action at the end (e.g., ask for a call).")

    # 5. Professional tone (0-10)
    tone_score = 10
    if "!!!" in body or body.count("!") > 3:
        tone_score -= 3
        suggestions.append("Reduce exclamation marks — they lower perceived professionalism.")
    if body.count("?") > 3:
        tone_score -= 2
    tone_score = max(0, tone_score)

    # 6. Subject line (0-5)
    subject_score = 5 if 10 <= len(subject) <= 60 else 2
    if len(subject) > 60:
        suggestions.append("Subject line is too long — keep it under 60 characters.")

    # 7. Sign-off (0-5)
    signoff_score = 5 if any(s in body.lower() for s in ["best,", "regards,", "thanks,", "cheers,"]) else 3

    total = personalization + length_score + spam_score + cta_score + tone_score + subject_score + signoff_score
    total = min(100, total)

    return {
        "total": round(total, 1),
        "breakdown": {
            "personalization": personalization,
            "length": length_score,
            "spam_signals": spam_score,
            "cta_clarity": cta_score,
            "professional_tone": tone_score,
            "subject_line": subject_score,
            "sign_off": signoff_score,
        },
        "suggestions": suggestions[:5],
    }


def _estimate_reply_probability(
    quality_score: float,
    hooks_count: int,
    sequence_position: int,
    goal: str,
) -> float:
    """Rough reply probability estimate based on email quality signals."""
    base = 0.06  # 6% platform average

    # Quality lift
    if quality_score >= 85:
        base += 0.08
    elif quality_score >= 70:
        base += 0.04
    elif quality_score < 50:
        base -= 0.03

    # Personalization lift
    base += min(0.06, hooks_count * 0.02)

    # Sequence position decay
    if sequence_position == 2:
        base *= 0.7
    elif sequence_position >= 3:
        base *= 0.4

    # Goal factor
    if goal == "networking":
        base *= 1.3  # Networking asks get slightly higher response
    elif goal == "referral":
        base *= 1.5  # Warm referral emails perform better

    return round(min(0.40, max(0.01, base)), 3)
