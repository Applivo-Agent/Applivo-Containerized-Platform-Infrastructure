"""
app/api/routes/outreach.py
──────────────────────────
Outreach Platform API routes.
Companies · Contacts · Campaigns · Emails · Conversations · Gmail Connector
"""
from __future__ import annotations

import asyncio
from datetime import datetime, timezone, timedelta
from typing import Optional, List
import structlog

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Query, Request, status
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, Field
from sqlalchemy import select, update, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.routes.auth import get_current_user
from app.core.config import settings
from app.core.database import get_db
from app.models.user import User
from app.models.outreach import (
    OutreachCompany, OutreachIntelligence, OutreachContact,
    OutreachCampaign, OutreachEmail, OutreachConversation, OutreachFollowUp,
    OutreachEmailConnector,
    OutreachCompanyPriority, OutreachCompanyStatus, OutreachResearchStatus,
    OutreachCampaignStatus, OutreachEmailStatus, OutreachContactRelationship,
    OutreachContactRoleType, OutreachContactEmailValidity,
    OutreachConversationStatus, OutreachEmailProvider,
)
from app.services.outreach_research_service import research_company, discover_contacts
from app.services.outreach_email_service import generate_outreach_email
from app.services import gmail_oauth_service as gmail

router = APIRouter(prefix="/outreach", tags=["Outreach"])
log = structlog.get_logger()


# ── Pydantic schemas ───────────────────────────────────────────────────────────

class CompanyCreate(BaseModel):
    name: str
    domain: Optional[str] = None
    priority: str = "WARM"
    notes: Optional[str] = None

class CompanyUpdate(BaseModel):
    priority: Optional[str] = None
    status: Optional[str] = None
    notes: Optional[str] = None

class ContactCreate(BaseModel):
    company_id: str
    name: Optional[str] = None
    title: Optional[str] = None
    email: Optional[str] = None
    role_type: str = "RECRUITER"
    linkedin_url: Optional[str] = None
    notes: Optional[str] = None

class ContactUpdate(BaseModel):
    name: Optional[str] = None
    title: Optional[str] = None
    email: Optional[str] = None
    notes: Optional[str] = None
    do_not_contact: Optional[bool] = None
    relationship_status: Optional[str] = None

class CampaignCreate(BaseModel):
    name: str
    goal: str = "JOB_SEARCH"
    daily_limit: int = Field(default=5, ge=1, le=15)
    sequence_config: Optional[dict] = None
    send_window: Optional[dict] = None
    resume_id: Optional[str] = None

class CampaignUpdate(BaseModel):
    name: Optional[str] = None
    status: Optional[str] = None
    daily_limit: Optional[int] = None
    paused_reason: Optional[str] = None

class EmailGenerateRequest(BaseModel):
    company_id: str
    contact_id: Optional[str] = None
    campaign_id: Optional[str] = None
    campaign_goal: str = "JOB_SEARCH"
    sequence_position: int = 1
    voice_style: str = "professional"
    job_description: Optional[str] = None

class EmailUpdateRequest(BaseModel):
    subject: Optional[str] = None
    body: Optional[str] = None

class EmailApproveRequest(BaseModel):
    subject: str
    body: str
    scheduled_at: Optional[datetime] = None

class ConversationUpdate(BaseModel):
    status: Optional[str] = None
    notes: Optional[str] = None
    next_action: Optional[str] = None
    next_action_due: Optional[datetime] = None
    interview_date: Optional[datetime] = None

class ConversationNoteAdd(BaseModel):
    note: str


# ── Helpers ────────────────────────────────────────────────────────────────────

def _company_out(c: OutreachCompany, intel: Optional[OutreachIntelligence] = None) -> dict:
    return {
        "id": c.id,
        "name": c.name,
        "domain": c.domain,
        "industry": c.industry,
        "stage": c.stage,
        "size": c.size,
        "location": c.location,
        "remote_policy": c.remote_policy,
        "priority": c.priority,
        "status": c.status,
        "research_status": c.research_status,
        "researched_at": c.researched_at.isoformat() if c.researched_at else None,
        "match_score": c.match_score,
        "tech_stack": c.tech_stack or [],
        "open_roles_count": c.open_roles_count,
        "notes": c.notes,
        "created_at": c.created_at.isoformat(),
        "intelligence": _intel_out(intel or c.intelligence) if (intel or c.intelligence) else None,
    }


def _intel_out(i: Optional[OutreachIntelligence]) -> Optional[dict]:
    if not i:
        return None
    return {
        "executive_summary": i.executive_summary,
        "personalization_hooks": i.personalization_hooks or [],
        "tech_stack": i.tech_stack or [],
        "culture_profile": i.culture_profile,
        "recent_news": i.recent_news or [],
        "outreach_recommendation": i.outreach_recommendation,
        "sources": i.sources or [],
        "confidence": i.confidence,
        "report": i.report,
        "expires_at": i.expires_at.isoformat() if i.expires_at else None,
    }


def _contact_out(c: OutreachContact) -> dict:
    return {
        "id": c.id,
        "company_id": c.company_id,
        "name": c.name,
        "title": c.title,
        "email": c.email,
        "email_confidence": c.email_confidence,
        "email_validity": c.email_validity,
        "linkedin_url": c.linkedin_url,
        "role_type": c.role_type,
        "relationship_strength": c.relationship_strength,
        "relationship_status": c.relationship_status,
        "last_contacted": c.last_contacted.isoformat() if c.last_contacted else None,
        "last_replied": c.last_replied.isoformat() if c.last_replied else None,
        "do_not_contact": c.do_not_contact,
        "source": c.source,
        "notes": c.notes,
        "created_at": c.created_at.isoformat(),
    }


def _email_out(e: OutreachEmail) -> dict:
    return {
        "id": e.id,
        "company_id": e.company_id,
        "contact_id": e.contact_id,
        "campaign_id": e.campaign_id,
        "sequence_position": e.sequence_position,
        "subject": e.subject,
        "body": e.body,
        "subject_options": e.subject_options or [],
        "personalization_hooks": e.personalization_hooks or [],
        "quality_score": e.quality_score,
        "quality_breakdown": e.quality_breakdown,
        "reply_probability": e.reply_probability,
        "from_address": e.from_address,
        "to_address": e.to_address,
        "status": e.status,
        "scheduled_at": e.scheduled_at.isoformat() if e.scheduled_at else None,
        "sent_at": e.sent_at.isoformat() if e.sent_at else None,
        "replied_at": e.replied_at.isoformat() if e.replied_at else None,
        "created_at": e.created_at.isoformat(),
    }


def _conv_out(c: OutreachConversation) -> dict:
    return {
        "id": c.id,
        "company_id": c.company_id,
        "contact_id": c.contact_id,
        "campaign_id": c.campaign_id,
        "status": c.status,
        "sentiment": c.sentiment,
        "reply_classification": c.reply_classification,
        "ai_summary": c.ai_summary,
        "next_action": c.next_action,
        "next_action_due": c.next_action_due.isoformat() if c.next_action_due else None,
        "interview_date": c.interview_date.isoformat() if c.interview_date else None,
        "offer_details": c.offer_details,
        "last_message_at": c.last_message_at.isoformat() if c.last_message_at else None,
        "messages": c.messages or [],
        "notes": c.notes,
        "created_at": c.created_at.isoformat(),
    }


async def _get_user_career_context(user: User, db: AsyncSession) -> tuple[str, list[str]]:
    """Extract career summary and skills from user profile for personalization."""
    from sqlalchemy.orm import selectinload
    result = await db.execute(
        select(User).where(User.id == user.id).options(selectinload(User.profile))
    )
    u = result.scalar_one_or_none()
    profile = u.profile if u else None

    if not profile:
        return f"{user.full_name} is a professional looking for new opportunities.", []

    skills = []
    if hasattr(profile, "skills") and profile.skills:
        skills = profile.skills if isinstance(profile.skills, list) else []

    summary_parts = [f"{user.full_name}"]
    if hasattr(profile, "current_title") and profile.current_title:
        summary_parts.append(f"is a {profile.current_title}")
    if hasattr(profile, "years_of_experience") and profile.years_of_experience:
        summary_parts.append(f"with {profile.years_of_experience} years of experience")
    if hasattr(profile, "bio") and profile.bio:
        summary_parts.append(f". Bio: {profile.bio[:300]}")

    summary = " ".join(summary_parts) + "." if len(summary_parts) > 1 else f"{user.full_name} is a professional."
    return summary, skills


# ── COMPANIES ─────────────────────────────────────────────────────────────────

@router.get("/companies")
async def list_companies(
    status: Optional[str] = None,
    priority: Optional[str] = None,
    search: Optional[str] = None,
    limit: int = Query(default=50, le=200),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    q = select(OutreachCompany).where(OutreachCompany.user_id == current_user.id)
    if status:
        q = q.where(OutreachCompany.status == status)
    if priority:
        q = q.where(OutreachCompany.priority == priority)
    if search:
        q = q.where(OutreachCompany.name.ilike(f"%{search}%"))
    q = q.options(selectinload(OutreachCompany.intelligence)).order_by(OutreachCompany.created_at.desc()).limit(limit)
    result = await db.execute(q)
    companies = result.scalars().all()
    return [_company_out(c) for c in companies]


@router.post("/companies", status_code=status.HTTP_201_CREATED)
async def create_company(
    body: CompanyCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Check duplicate
    existing = await db.execute(
        select(OutreachCompany).where(
            OutreachCompany.user_id == current_user.id,
            OutreachCompany.name.ilike(body.name)
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="Company workspace already exists")

    company = OutreachCompany(
        user_id=current_user.id,
        name=body.name,
        domain=body.domain,
        priority=body.priority,
        notes=body.notes,
    )
    db.add(company)
    await db.commit()
    await db.refresh(company)
    log.info("Company workspace created", company=body.name, user=current_user.id)
    return _company_out(company)


@router.get("/companies/{company_id}")
async def get_company(
    company_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(OutreachCompany)
        .where(OutreachCompany.id == company_id, OutreachCompany.user_id == current_user.id)
        .options(selectinload(OutreachCompany.intelligence), selectinload(OutreachCompany.contacts))
    )
    company = result.scalar_one_or_none()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    out = _company_out(company)
    out["contacts"] = [_contact_out(c) for c in company.contacts]
    return out


@router.patch("/companies/{company_id}")
async def update_company(
    company_id: str,
    body: CompanyUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(OutreachCompany).where(OutreachCompany.id == company_id, OutreachCompany.user_id == current_user.id)
    )
    company = result.scalar_one_or_none()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    if body.priority is not None:
        company.priority = body.priority
    if body.status is not None:
        company.status = body.status
    if body.notes is not None:
        company.notes = body.notes
    await db.commit()
    await db.refresh(company)
    return _company_out(company)


@router.delete("/companies/{company_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_company(
    company_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(OutreachCompany).where(OutreachCompany.id == company_id, OutreachCompany.user_id == current_user.id)
    )
    company = result.scalar_one_or_none()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    await db.delete(company)
    await db.commit()


@router.post("/companies/{company_id}/research")
async def trigger_research(
    company_id: str,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Trigger async company intelligence research."""
    result = await db.execute(
        select(OutreachCompany).where(OutreachCompany.id == company_id, OutreachCompany.user_id == current_user.id)
    )
    company = result.scalar_one_or_none()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    # Mark as in-progress immediately
    company.research_status = OutreachResearchStatus.IN_PROGRESS
    await db.commit()

    background_tasks.add_task(
        _run_research_background, company_id, company.name, company.domain,
        current_user.id, current_user.full_name
    )
    return {"status": "research_started", "company_id": company_id}


async def _run_research_background(
    company_id: str, company_name: str, domain: Optional[str],
    user_id: str, user_name: str
):
    """Background task that runs research and stores results."""
    from app.core.database import get_db_context
    try:
        report = await research_company(company_name, domain)
        contacts_data = await discover_contacts(company_name, domain or "")

        async with get_db_context() as db:
            # Update company
            result = await db.execute(select(OutreachCompany).where(OutreachCompany.id == company_id))
            company = result.scalar_one_or_none()
            if not company:
                return

            company.research_status = OutreachResearchStatus.COMPLETE
            company.researched_at = datetime.now(timezone.utc)
            company.match_score = report.get("match_score")
            company.tech_stack = report.get("tech_stack", [])
            company.industry = report.get("industry")
            company.stage = report.get("stage")
            company.size = report.get("size_estimate")
            company.location = report.get("location")
            company.remote_policy = report.get("remote_policy")

            # Store intelligence
            intel_result = await db.execute(
                select(OutreachIntelligence).where(OutreachIntelligence.company_id == company_id)
            )
            intel = intel_result.scalar_one_or_none()
            if not intel:
                intel = OutreachIntelligence(company_id=company_id)
                db.add(intel)

            intel.report = report
            intel.executive_summary = report.get("executive_summary")
            intel.personalization_hooks = report.get("personalization_hooks", [])
            intel.tech_stack = report.get("tech_stack", [])
            intel.culture_profile = report.get("engineering_culture")
            intel.recent_news = report.get("recent_news", [])
            intel.outreach_recommendation = report.get("outreach_recommendation")
            intel.sources = report.get("sources", [])
            intel.confidence = report.get("confidence", 0.5)
            intel.expires_at = datetime.now(timezone.utc) + timedelta(days=7)

            # Store discovered contacts (skip duplicates)
            for cd in contacts_data[:5]:
                if not cd.get("email"):
                    continue
                existing = await db.execute(
                    select(OutreachContact).where(
                        OutreachContact.company_id == company_id,
                        OutreachContact.email == cd["email"]
                    )
                )
                if existing.scalar_one_or_none():
                    continue
                contact = OutreachContact(
                    user_id=user_id,
                    company_id=company_id,
                    name=cd.get("name"),
                    title=cd.get("title"),
                    email=cd.get("email"),
                    email_confidence=cd.get("email_confidence", 0.5),
                    role_type=cd.get("role_type", "RECRUITER"),
                    linkedin_url=cd.get("linkedin_url"),
                    source=cd.get("source"),
                    notes=cd.get("notes"),
                )
                db.add(contact)

            await db.commit()
            log.info("Research stored", company=company_name, contacts=len(contacts_data))

    except Exception as e:
        log.error("Background research failed", company=company_name, error=str(e))
        from app.core.database import get_db_context
        async with get_db_context() as db:
            result = await db.execute(select(OutreachCompany).where(OutreachCompany.id == company_id))
            company = result.scalar_one_or_none()
            if company:
                company.research_status = OutreachResearchStatus.FAILED
                await db.commit()


@router.get("/companies/{company_id}/intelligence")
async def get_intelligence(
    company_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(OutreachCompany)
        .where(OutreachCompany.id == company_id, OutreachCompany.user_id == current_user.id)
        .options(selectinload(OutreachCompany.intelligence))
    )
    company = result.scalar_one_or_none()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    if not company.intelligence:
        return {"status": "not_researched", "research_status": company.research_status}
    return _intel_out(company.intelligence)


# ── CONTACTS ──────────────────────────────────────────────────────────────────

@router.get("/contacts")
async def list_contacts(
    company_id: Optional[str] = None,
    relationship_status: Optional[str] = None,
    limit: int = Query(default=50, le=200),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    q = select(OutreachContact).where(OutreachContact.user_id == current_user.id)
    if company_id:
        q = q.where(OutreachContact.company_id == company_id)
    if relationship_status:
        q = q.where(OutreachContact.relationship_status == relationship_status)
    q = q.order_by(OutreachContact.created_at.desc()).limit(limit)
    result = await db.execute(q)
    return [_contact_out(c) for c in result.scalars().all()]


@router.post("/contacts", status_code=status.HTTP_201_CREATED)
async def create_contact(
    body: ContactCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Verify company belongs to user
    comp = await db.execute(
        select(OutreachCompany).where(OutreachCompany.id == body.company_id, OutreachCompany.user_id == current_user.id)
    )
    if not comp.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Company not found")

    contact = OutreachContact(
        user_id=current_user.id,
        company_id=body.company_id,
        name=body.name,
        title=body.title,
        email=body.email,
        role_type=body.role_type,
        linkedin_url=body.linkedin_url,
        notes=body.notes,
        source="manual",
    )
    db.add(contact)
    await db.commit()
    await db.refresh(contact)
    return _contact_out(contact)


@router.patch("/contacts/{contact_id}")
async def update_contact(
    contact_id: str,
    body: ContactUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(OutreachContact).where(OutreachContact.id == contact_id, OutreachContact.user_id == current_user.id)
    )
    contact = result.scalar_one_or_none()
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    for field, val in body.model_dump(exclude_none=True).items():
        setattr(contact, field, val)
    await db.commit()
    await db.refresh(contact)
    return _contact_out(contact)


@router.post("/contacts/{contact_id}/do-not-contact", status_code=status.HTTP_204_NO_CONTENT)
async def mark_do_not_contact(
    contact_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(OutreachContact).where(OutreachContact.id == contact_id, OutreachContact.user_id == current_user.id)
    )
    contact = result.scalar_one_or_none()
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    contact.do_not_contact = True
    await db.commit()


# ── CAMPAIGNS ─────────────────────────────────────────────────────────────────

@router.get("/campaigns")
async def list_campaigns(
    status_filter: Optional[str] = Query(default=None, alias="status"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    q = select(OutreachCampaign).where(OutreachCampaign.user_id == current_user.id)
    if status_filter:
        q = q.where(OutreachCampaign.status == status_filter)
    q = q.order_by(OutreachCampaign.created_at.desc())
    result = await db.execute(q)
    campaigns = result.scalars().all()
    return [
        {
            "id": c.id, "name": c.name, "goal": c.goal, "status": c.status,
            "daily_limit": c.daily_limit, "stats": c.stats or {},
            "start_date": c.start_date.isoformat() if c.start_date else None,
            "created_at": c.created_at.isoformat(),
        }
        for c in campaigns
    ]


@router.post("/campaigns", status_code=status.HTTP_201_CREATED)
async def create_campaign(
    body: CampaignCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    default_sequence = {
        "steps": [
            {"position": 1, "delay_days": 0, "type": "initial"},
            {"position": 2, "delay_days": 5, "type": "value_add"},
            {"position": 3, "delay_days": 12, "type": "final"},
        ]
    }
    default_window = {
        "days": ["monday", "tuesday", "wednesday", "thursday"],
        "start_hour": 8,
        "end_hour": 11,
    }
    campaign = OutreachCampaign(
        user_id=current_user.id,
        name=body.name,
        goal=body.goal,
        daily_limit=body.daily_limit,
        sequence_config=body.sequence_config or default_sequence,
        send_window=body.send_window or default_window,
        resume_id=body.resume_id,
        stats={"sent": 0, "opened": 0, "replied": 0, "interviews": 0, "offers": 0},
    )
    db.add(campaign)
    await db.commit()
    await db.refresh(campaign)
    log.info("Campaign created", name=body.name, user=current_user.id)
    return {"id": campaign.id, "name": campaign.name, "status": campaign.status, "goal": campaign.goal}


@router.patch("/campaigns/{campaign_id}")
async def update_campaign(
    campaign_id: str,
    body: CampaignUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(OutreachCampaign).where(OutreachCampaign.id == campaign_id, OutreachCampaign.user_id == current_user.id)
    )
    campaign = result.scalar_one_or_none()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    for field, val in body.model_dump(exclude_none=True).items():
        setattr(campaign, field, val)
    await db.commit()
    await db.refresh(campaign)
    return {"id": campaign.id, "name": campaign.name, "status": campaign.status}


@router.post("/campaigns/{campaign_id}/launch")
async def launch_campaign(
    campaign_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(OutreachCampaign).where(OutreachCampaign.id == campaign_id, OutreachCampaign.user_id == current_user.id)
    )
    campaign = result.scalar_one_or_none()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    if campaign.status not in ("DRAFT", "PAUSED"):
        raise HTTPException(status_code=400, detail=f"Cannot launch campaign in '{campaign.status}' status")
    campaign.status = OutreachCampaignStatus.ACTIVE
    campaign.start_date = datetime.now(timezone.utc)
    await db.commit()
    log.info("Campaign launched", campaign_id=campaign_id)
    return {"status": "ACTIVE", "campaign_id": campaign_id}


@router.post("/campaigns/{campaign_id}/pause")
async def pause_campaign(
    campaign_id: str,
    reason: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(OutreachCampaign).where(OutreachCampaign.id == campaign_id, OutreachCampaign.user_id == current_user.id)
    )
    campaign = result.scalar_one_or_none()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    campaign.status = OutreachCampaignStatus.PAUSED
    campaign.paused_reason = reason
    await db.commit()
    return {"status": "PAUSED", "campaign_id": campaign_id}


# ── EMAILS ────────────────────────────────────────────────────────────────────

@router.post("/emails/generate")
async def generate_email(
    body: EmailGenerateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """AI-generate a personalized outreach email draft."""
    # Load company + intelligence
    comp_result = await db.execute(
        select(OutreachCompany)
        .where(OutreachCompany.id == body.company_id, OutreachCompany.user_id == current_user.id)
        .options(selectinload(OutreachCompany.intelligence))
    )
    company = comp_result.scalar_one_or_none()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    # Load contact if specified
    contact = None
    if body.contact_id:
        c_result = await db.execute(
            select(OutreachContact).where(
                OutreachContact.id == body.contact_id,
                OutreachContact.user_id == current_user.id
            )
        )
        contact = c_result.scalar_one_or_none()

    # Get user career context
    career_summary, skills = await _get_user_career_context(current_user, db)

    # Generate email
    email_data = await generate_outreach_email(
        company_name=company.name,
        contact_name=contact.name if contact else None,
        contact_title=contact.title if contact else None,
        intelligence_report=company.intelligence.report if company.intelligence else None,
        user_name=current_user.full_name,
        user_career_summary=career_summary,
        user_skills=skills,
        campaign_goal=body.campaign_goal,
        sequence_position=body.sequence_position,
        voice_style=body.voice_style,
        job_description=body.job_description,
    )

    # Store as draft
    email = OutreachEmail(
        user_id=current_user.id,
        company_id=body.company_id,
        contact_id=body.contact_id,
        campaign_id=body.campaign_id,
        sequence_position=body.sequence_position,
        subject=email_data.get("subject"),
        body=email_data.get("body"),
        subject_options=email_data.get("subject_options", []),
        personalization_hooks=email_data.get("personalization_hooks_used", []),
        quality_score=email_data.get("quality_score"),
        quality_breakdown=email_data.get("quality_breakdown"),
        reply_probability=email_data.get("reply_probability"),
        to_address=contact.email if contact else None,
        status=OutreachEmailStatus.DRAFT,
    )
    db.add(email)
    await db.commit()
    await db.refresh(email)

    result = _email_out(email)
    result["quality_suggestions"] = email_data.get("quality_suggestions", [])
    return result


@router.get("/emails")
async def list_emails(
    campaign_id: Optional[str] = None,
    company_id: Optional[str] = None,
    status_filter: Optional[str] = Query(default=None, alias="status"),
    limit: int = Query(default=50, le=200),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    q = select(OutreachEmail).where(OutreachEmail.user_id == current_user.id)
    if campaign_id:
        q = q.where(OutreachEmail.campaign_id == campaign_id)
    if company_id:
        q = q.where(OutreachEmail.company_id == company_id)
    if status_filter:
        q = q.where(OutreachEmail.status == status_filter)
    q = q.order_by(OutreachEmail.created_at.desc()).limit(limit)
    result = await db.execute(q)
    return [_email_out(e) for e in result.scalars().all()]


@router.get("/emails/{email_id}")
async def get_email(
    email_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(OutreachEmail).where(OutreachEmail.id == email_id, OutreachEmail.user_id == current_user.id)
    )
    email = result.scalar_one_or_none()
    if not email:
        raise HTTPException(status_code=404, detail="Email not found")
    return _email_out(email)


@router.patch("/emails/{email_id}")
async def update_email(
    email_id: str,
    body: EmailUpdateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(OutreachEmail).where(OutreachEmail.id == email_id, OutreachEmail.user_id == current_user.id)
    )
    email = result.scalar_one_or_none()
    if not email:
        raise HTTPException(status_code=404, detail="Email not found")
    if email.status not in ("DRAFT", "APPROVED"):
        raise HTTPException(status_code=400, detail="Cannot edit a sent email")
    if body.subject is not None:
        email.subject = body.subject
    if body.body is not None:
        email.body = body.body
        # Re-score quality when body changes
        from app.services.outreach_email_service import _score_quality
        q = _score_quality({"body": body.body, "subject": email.subject or "", "word_count": len(body.body.split()), "personalization_hooks_used": email.personalization_hooks or []}, None)
        email.quality_score = q["total"]
        email.quality_breakdown = q["breakdown"]
    await db.commit()
    await db.refresh(email)
    return _email_out(email)


@router.post("/emails/{email_id}/approve")
async def approve_email(
    email_id: str,
    body: EmailApproveRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """User approves an email draft — saves final content and marks ready to schedule."""
    result = await db.execute(
        select(OutreachEmail).where(OutreachEmail.id == email_id, OutreachEmail.user_id == current_user.id)
    )
    email = result.scalar_one_or_none()
    if not email:
        raise HTTPException(status_code=404, detail="Email not found")
    if email.status not in ("DRAFT",):
        raise HTTPException(status_code=400, detail=f"Cannot approve email in '{email.status}' status")

    # Quality gate: must be >= 60 to approve
    if email.quality_score and email.quality_score < 60:
        raise HTTPException(
            status_code=422,
            detail=f"Email quality score {email.quality_score}/100 is below minimum (60). Please improve the email first."
        )

    email.subject = body.subject
    email.body = body.body
    email.status = OutreachEmailStatus.APPROVED
    if body.scheduled_at:
        email.scheduled_at = body.scheduled_at
        email.status = OutreachEmailStatus.SCHEDULED

    # Update contact relationship status
    if email.contact_id:
        c_result = await db.execute(select(OutreachContact).where(OutreachContact.id == email.contact_id))
        contact = c_result.scalar_one_or_none()
        if contact and contact.relationship_status == "NOT_CONTACTED":
            contact.relationship_status = OutreachContactRelationship.REACHED_OUT

    # Update company status
    if email.company_id:
        co_result = await db.execute(select(OutreachCompany).where(OutreachCompany.id == email.company_id))
        company = co_result.scalar_one_or_none()
        if company and company.status in ("WATCHING", "RESEARCHED"):
            company.status = OutreachCompanyStatus.CONTACTED

    await db.commit()
    await db.refresh(email)
    log.info("Email approved", email_id=email_id, scheduled_at=body.scheduled_at)
    return _email_out(email)


@router.post("/emails/{email_id}/regenerate")
async def regenerate_email(
    email_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Regenerate an email draft with fresh AI output."""
    result = await db.execute(
        select(OutreachEmail)
        .where(OutreachEmail.id == email_id, OutreachEmail.user_id == current_user.id)
    )
    email = result.scalar_one_or_none()
    if not email:
        raise HTTPException(status_code=404, detail="Email not found")
    if email.status != "DRAFT":
        raise HTTPException(status_code=400, detail="Can only regenerate draft emails")

    # Load company + contact for context
    comp_result = await db.execute(
        select(OutreachCompany)
        .where(OutreachCompany.id == email.company_id, OutreachCompany.user_id == current_user.id)
        .options(selectinload(OutreachCompany.intelligence))
    )
    company = comp_result.scalar_one_or_none()

    contact = None
    if email.contact_id:
        c_result = await db.execute(select(OutreachContact).where(OutreachContact.id == email.contact_id))
        contact = c_result.scalar_one_or_none()

    career_summary, skills = await _get_user_career_context(current_user, db)

    email_data = await generate_outreach_email(
        company_name=company.name if company else "the company",
        contact_name=contact.name if contact else None,
        contact_title=contact.title if contact else None,
        intelligence_report=company.intelligence.report if company and company.intelligence else None,
        user_name=current_user.full_name,
        user_career_summary=career_summary,
        user_skills=skills,
        sequence_position=email.sequence_position,
    )

    email.subject = email_data.get("subject")
    email.body = email_data.get("body")
    email.subject_options = email_data.get("subject_options", [])
    email.personalization_hooks = email_data.get("personalization_hooks_used", [])
    email.quality_score = email_data.get("quality_score")
    email.quality_breakdown = email_data.get("quality_breakdown")
    email.reply_probability = email_data.get("reply_probability")
    await db.commit()
    await db.refresh(email)

    out = _email_out(email)
    out["quality_suggestions"] = email_data.get("quality_suggestions", [])
    return out


# ── CONVERSATIONS ─────────────────────────────────────────────────────────────

@router.get("/conversations")
async def list_conversations(
    status_filter: Optional[str] = Query(default=None, alias="status"),
    company_id: Optional[str] = None,
    limit: int = Query(default=50, le=200),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    q = select(OutreachConversation).where(OutreachConversation.user_id == current_user.id)
    if status_filter:
        q = q.where(OutreachConversation.status == status_filter)
    if company_id:
        q = q.where(OutreachConversation.company_id == company_id)
    q = q.order_by(OutreachConversation.last_message_at.desc().nullslast()).limit(limit)
    result = await db.execute(q)
    return [_conv_out(c) for c in result.scalars().all()]


@router.get("/conversations/{conv_id}")
async def get_conversation(
    conv_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(OutreachConversation).where(
            OutreachConversation.id == conv_id,
            OutreachConversation.user_id == current_user.id
        )
    )
    conv = result.scalar_one_or_none()
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return _conv_out(conv)


@router.patch("/conversations/{conv_id}")
async def update_conversation(
    conv_id: str,
    body: ConversationUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(OutreachConversation).where(
            OutreachConversation.id == conv_id,
            OutreachConversation.user_id == current_user.id
        )
    )
    conv = result.scalar_one_or_none()
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")
    for field, val in body.model_dump(exclude_none=True).items():
        setattr(conv, field, val)
    await db.commit()
    await db.refresh(conv)
    return _conv_out(conv)


@router.post("/conversations/{conv_id}/notes")
async def add_note(
    conv_id: str,
    body: ConversationNoteAdd,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(OutreachConversation).where(
            OutreachConversation.id == conv_id,
            OutreachConversation.user_id == current_user.id
        )
    )
    conv = result.scalar_one_or_none()
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")
    existing = conv.notes or ""
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M")
    conv.notes = f"{existing}\n\n[{ts}] {body.note}".strip()
    await db.commit()
    return {"notes": conv.notes}


# ── DASHBOARD / ANALYTICS ─────────────────────────────────────────────────────

@router.get("/hub")
async def outreach_hub(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Outreach hub stats — shown on the main Outreach dashboard."""
    # Company counts by status
    comp_result = await db.execute(
        select(OutreachCompany.status, func.count(OutreachCompany.id))
        .where(OutreachCompany.user_id == current_user.id)
        .group_by(OutreachCompany.status)
    )
    company_counts = {row[0]: row[1] for row in comp_result.all()}

    # Email stats
    email_result = await db.execute(
        select(OutreachEmail.status, func.count(OutreachEmail.id))
        .where(OutreachEmail.user_id == current_user.id)
        .group_by(OutreachEmail.status)
    )
    email_counts = {row[0]: row[1] for row in email_result.all()}

    sent = email_counts.get("SENT", 0) + email_counts.get("DELIVERED", 0) + email_counts.get("OPENED", 0) + email_counts.get("REPLIED", 0)
    replied = email_counts.get("REPLIED", 0)
    reply_rate = round(replied / sent * 100, 1) if sent > 0 else 0.0

    # Active campaigns
    camp_result = await db.execute(
        select(func.count(OutreachCampaign.id))
        .where(OutreachCampaign.user_id == current_user.id, OutreachCampaign.status == "ACTIVE")
    )
    active_campaigns = camp_result.scalar() or 0

    # Pending approvals (drafts)
    pending_result = await db.execute(
        select(func.count(OutreachEmail.id))
        .where(OutreachEmail.user_id == current_user.id, OutreachEmail.status == "DRAFT")
    )
    pending_approvals = pending_result.scalar() or 0

    # Conversations needing attention
    attn_result = await db.execute(
        select(func.count(OutreachConversation.id))
        .where(
            OutreachConversation.user_id == current_user.id,
            OutreachConversation.status == "REPLIED"
        )
    )
    needs_attention = attn_result.scalar() or 0

    # Recent companies (hot)
    hot_result = await db.execute(
        select(OutreachCompany)
        .where(OutreachCompany.user_id == current_user.id, OutreachCompany.priority == "HOT")
        .order_by(OutreachCompany.updated_at.desc())
        .limit(5)
    )
    hot_companies = [
        {"id": c.id, "name": c.name, "status": c.status, "match_score": c.match_score}
        for c in hot_result.scalars().all()
    ]

    return {
        "pipeline": {
            "companies_added": sum(company_counts.values()),
            "contacted": company_counts.get("CONTACTED", 0),
            "replied": company_counts.get("REPLIED", 0),
            "interviewing": company_counts.get("INTERVIEWING", 0),
            "offer": company_counts.get("OFFER", 0),
        },
        "email_stats": {
            "sent": sent,
            "replied": replied,
            "reply_rate": reply_rate,
            "pending_approvals": pending_approvals,
        },
        "active_campaigns": active_campaigns,
        "needs_attention": needs_attention,
        "hot_companies": hot_companies,
    }


# ═══════════════════════════════════════════════════════════════════════════════
# Gmail OAuth Connector
# ═══════════════════════════════════════════════════════════════════════════════

def _connector_out(c: OutreachEmailConnector) -> dict:
    return {
        "id": c.id,
        "provider": c.provider,
        "email_address": c.email_address,
        "is_active": c.is_active,
        "last_sync_at": c.last_sync_at.isoformat() if c.last_sync_at else None,
        "created_at": c.created_at.isoformat() if c.created_at else None,
    }


@router.get("/connectors")
async def list_connectors(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Return the current user's email connectors."""
    result = await db.execute(
        select(OutreachEmailConnector).where(OutreachEmailConnector.user_id == current_user.id)
    )
    connectors = result.scalars().all()
    return [_connector_out(c) for c in connectors]


@router.post("/connectors/gmail/auth")
async def gmail_auth_start(
    current_user: User = Depends(get_current_user),
):
    """Generate a Gmail OAuth2 authorization URL for the current user."""
    if not settings.GOOGLE_CLIENT_ID or not settings.GOOGLE_CLIENT_SECRET:
        raise HTTPException(status_code=503, detail="Gmail OAuth not configured — set GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET")

    auth_url = gmail.get_auth_url(
        client_id=settings.GOOGLE_CLIENT_ID,
        redirect_uri=settings.OUTREACH_GMAIL_REDIRECT_URI,
        state=current_user.id,
    )
    return {"auth_url": auth_url}


@router.get("/connectors/gmail/callback")
async def gmail_auth_callback(
    code: str = Query(...),
    state: str = Query(...),
    db: AsyncSession = Depends(get_db),
):
    """
    OAuth2 callback from Google.
    Exchanges the code for tokens, upserts the connector, redirects to the frontend.
    `state` carries the user_id.
    """
    try:
        tokens = gmail.exchange_code(
            code=code,
            client_id=settings.GOOGLE_CLIENT_ID,
            client_secret=settings.GOOGLE_CLIENT_SECRET,
            redirect_uri=settings.OUTREACH_GMAIL_REDIRECT_URI,
        )
    except Exception as exc:
        log.error("Gmail token exchange failed", error=str(exc))
        return RedirectResponse(url=f"{settings.FRONTEND_URL}/outreach?error=oauth_failed")

    # Fetch the user's email address
    try:
        userinfo = gmail.get_userinfo(tokens["access_token"])
        email_address = userinfo.get("email", "")
    except Exception:
        email_address = ""

    # Encrypt tokens
    from app.services.encryption import EncryptionService
    enc = EncryptionService()
    access_enc  = enc.encrypt(tokens["access_token"])
    refresh_enc = enc.encrypt(tokens["refresh_token"]) if tokens.get("refresh_token") else None

    expires_at = None
    if tokens.get("expires_at"):
        try:
            expires_at = datetime.fromisoformat(tokens["expires_at"])
        except Exception:
            pass

    # Fetch Gmail historyId to use as baseline for reply polling
    try:
        profile = gmail.get_profile(tokens["access_token"])
        history_id = profile.get("historyId")
    except Exception:
        history_id = None

    # Upsert connector (one per user)
    result = await db.execute(
        select(OutreachEmailConnector).where(OutreachEmailConnector.user_id == state)
    )
    connector = result.scalar_one_or_none()

    if connector:
        connector.access_token_enc  = access_enc
        connector.refresh_token_enc = refresh_enc or connector.refresh_token_enc
        connector.token_expires     = expires_at
        connector.email_address     = email_address
        connector.scopes            = tokens.get("scopes", [])
        connector.is_active         = True
        connector.last_history_id   = history_id
    else:
        import uuid
        connector = OutreachEmailConnector(
            id=str(uuid.uuid4()),
            user_id=state,
            provider=OutreachEmailProvider.GMAIL,
            email_address=email_address,
            access_token_enc=access_enc,
            refresh_token_enc=refresh_enc,
            token_expires=expires_at,
            scopes=tokens.get("scopes", []),
            is_active=True,
            last_history_id=history_id,
        )
        db.add(connector)

    await db.commit()
    log.info("Gmail connector saved", user_id=state, email=email_address)
    return RedirectResponse(url=f"{settings.FRONTEND_URL}/outreach?connected=true")


@router.delete("/connectors/{connector_id}")
async def disconnect_connector(
    connector_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Disconnect (delete) a Gmail connector."""
    result = await db.execute(
        select(OutreachEmailConnector).where(
            OutreachEmailConnector.id == connector_id,
            OutreachEmailConnector.user_id == current_user.id,
        )
    )
    connector = result.scalar_one_or_none()
    if not connector:
        raise HTTPException(status_code=404, detail="Connector not found")
    await db.delete(connector)
    await db.commit()
    return {"status": "disconnected"}


# ── Send an approved email via Gmail ──────────────────────────────────────────

@router.post("/emails/{email_id}/send")
async def send_email(
    email_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Send an approved outreach email via the user's connected Gmail account.
    Creates or updates the OutreachConversation with the Gmail thread_id.
    """
    # Load email
    result = await db.execute(
        select(OutreachEmail)
        .options(selectinload(OutreachEmail.contact))
        .where(OutreachEmail.id == email_id, OutreachEmail.user_id == current_user.id)
    )
    email_obj = result.scalar_one_or_none()
    if not email_obj:
        raise HTTPException(status_code=404, detail="Email not found")
    if email_obj.status not in ("APPROVED", "SCHEDULED"):
        raise HTTPException(status_code=422, detail=f"Email status is '{email_obj.status}', must be approved or scheduled to send")

    # Load connector
    conn_result = await db.execute(
        select(OutreachEmailConnector).where(
            OutreachEmailConnector.user_id == current_user.id,
            OutreachEmailConnector.is_active == True,
        )
    )
    connector = conn_result.scalar_one_or_none()
    if not connector:
        raise HTTPException(status_code=422, detail="No Gmail account connected. Go to Outreach → Settings to connect Gmail.")

    # Get a valid access token (auto-refreshes if needed)
    from app.services.encryption import EncryptionService
    enc = EncryptionService()
    try:
        access_token = await gmail.get_valid_token(connector, enc)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))

    # Determine recipient
    to_address = email_obj.to_address
    if not to_address and email_obj.contact:
        to_address = email_obj.contact.email
    if not to_address:
        raise HTTPException(status_code=422, detail="No recipient email address found on this email or its contact")

    # Send via Gmail
    try:
        sent = gmail.send_email(
            access_token=access_token,
            to=to_address,
            subject=email_obj.subject or "(no subject)",
            body=email_obj.body or "",
            from_email=connector.email_address,
        )
    except Exception as exc:
        log.error("Gmail send failed", email_id=email_id, error=str(exc))
        raise HTTPException(status_code=502, detail=f"Gmail API error: {exc}")

    now = datetime.now(timezone.utc)

    # Update email record
    email_obj.status = OutreachEmailStatus.SENT
    email_obj.sent_at = now
    email_obj.from_address = connector.email_address
    email_obj.to_address = to_address
    email_obj.provider_message_id = sent["message_id"]
    email_obj.provider_thread_id  = sent["thread_id"]

    # Commit the updated access token too (if refreshed)
    await db.commit()

    # Upsert OutreachConversation
    conv_result = await db.execute(
        select(OutreachConversation).where(
            OutreachConversation.user_id == current_user.id,
            OutreachConversation.company_id == email_obj.company_id,
        )
    )
    conversation = conv_result.scalar_one_or_none()
    if not conversation:
        import uuid
        conversation = OutreachConversation(
            id=str(uuid.uuid4()),
            user_id=current_user.id,
            contact_id=email_obj.contact_id,
            company_id=email_obj.company_id,
            campaign_id=email_obj.campaign_id,
            thread_id=sent["thread_id"],
            status=OutreachConversationStatus.AWAITING_REPLY,
            last_message_at=now,
        )
        db.add(conversation)
    else:
        conversation.thread_id = sent["thread_id"]
        conversation.last_message_at = now

    # Mark company as contacted
    if email_obj.company_id:
        await db.execute(
            update(OutreachCompany)
            .where(OutreachCompany.id == email_obj.company_id)
            .values(status=OutreachCompanyStatus.CONTACTED)
        )

    await db.commit()

    return {
        "status": "sent",
        "message_id": sent["message_id"],
        "thread_id": sent["thread_id"],
        "sent_at": now.isoformat(),
    }


# ═══════════════════════════════════════════════════════════════════════════════
# GitHub OAuth Connector
# ═══════════════════════════════════════════════════════════════════════════════

from app.services import github_oauth_service as github
from app.models.outreach import OutreachGitHubConnector


def _github_connector_out(c: OutreachGitHubConnector) -> dict:
    return {
        "id": c.id,
        "github_username": c.github_username,
        "is_active": c.is_active,
        "repo_count": c.repo_count,
        "star_count": c.star_count,
        "last_sync_at": c.last_sync_at.isoformat() if c.last_sync_at else None,
        "created_at": c.created_at.isoformat() if c.created_at else None,
    }


@router.get("/connectors/github")
async def list_github_connectors(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Return the current user's GitHub connector."""
    result = await db.execute(
        select(OutreachGitHubConnector).where(OutreachGitHubConnector.user_id == current_user.id)
    )
    connector = result.scalar_one_or_none()
    if connector:
        return _github_connector_out(connector)
    return None


@router.post("/connectors/github/auth")
async def github_auth_start(
    current_user: User = Depends(get_current_user),
):
    """Generate a GitHub OAuth2 authorization URL for the current user."""
    if not settings.GITHUB_CLIENT_ID or not settings.GITHUB_CLIENT_SECRET:
        raise HTTPException(status_code=503, detail="GitHub OAuth not configured — set GITHUB_CLIENT_ID and GITHUB_CLIENT_SECRET")

    auth_url = github.get_auth_url(
        client_id=settings.GITHUB_CLIENT_ID,
        redirect_uri=settings.GITHUB_REDIRECT_URI,
        state=current_user.id,
    )
    return {"auth_url": auth_url}


@router.get("/connectors/github/callback")
async def github_auth_callback(
    code: str = Query(...),
    state: str = Query(...),
    db: AsyncSession = Depends(get_db),
):
    """
    OAuth2 callback from GitHub.
    Exchanges the code for tokens, upserts the connector, redirects to the frontend.
    `state` carries the user_id.
    """
    try:
        tokens = github.exchange_code(
            code=code,
            client_id=settings.GITHUB_CLIENT_ID,
            client_secret=settings.GITHUB_CLIENT_SECRET,
            redirect_uri=settings.GITHUB_REDIRECT_URI,
        )
    except Exception as exc:
        log.error("GitHub token exchange failed", error=str(exc))
        return RedirectResponse(url=f"{settings.FRONTEND_URL}/outreach/settings?error=oauth_failed")

    # Fetch the user's GitHub profile
    try:
        profile = github.get_user_profile(tokens["access_token"])
        github_username = profile.get("login", "")
        profile_json = {
            "avatar_url": profile.get("avatar_url"),
            "bio": profile.get("bio"),
            "blog": profile.get("blog"),
            "company": profile.get("company"),
            "location": profile.get("location"),
            "public_repos": profile.get("public_repos"),
            "followers": profile.get("followers"),
            "following": profile.get("following"),
        }
    except Exception:
        github_username = ""
        profile_json = {}

    # Fetch repo stats
    try:
        repos = github.get_user_repos(tokens["access_token"])
        stats = github.calculate_repo_stats(repos)
    except Exception:
        stats = {"repo_count": 0, "star_count": 0, "fork_count": 0, "top_languages": []}

    # Encrypt tokens
    from app.services.encryption import EncryptionService
    enc = EncryptionService()
    access_enc = enc.encrypt(tokens["access_token"])
    refresh_enc = enc.encrypt(tokens["refresh_token"]) if tokens.get("refresh_token") else None

    expires_at = None
    if tokens.get("expires_at"):
        try:
            expires_at = datetime.fromisoformat(tokens["expires_at"])
        except Exception:
            pass

    # Upsert connector (one per user)
    result = await db.execute(
        select(OutreachGitHubConnector).where(OutreachGitHubConnector.user_id == state)
    )
    connector = result.scalar_one_or_none()

    if connector:
        connector.access_token_enc = access_enc
        connector.refresh_token_enc = refresh_enc or connector.refresh_token_enc
        connector.token_expires = expires_at
        connector.github_username = github_username
        connector.scopes = tokens.get("scopes", [])
        connector.is_active = True
        connector.repo_count = stats.get("repo_count")
        connector.star_count = stats.get("star_count")
        connector.profile_json = profile_json
        connector.last_sync_at = datetime.now(timezone.utc)
    else:
        import uuid
        connector = OutreachGitHubConnector(
            id=str(uuid.uuid4()),
            user_id=state,
            github_username=github_username,
            access_token_enc=access_enc,
            refresh_token_enc=refresh_enc,
            token_expires=expires_at,
            scopes=tokens.get("scopes", []),
            is_active=True,
            repo_count=stats.get("repo_count"),
            star_count=stats.get("star_count"),
            profile_json=profile_json,
            last_sync_at=datetime.now(timezone.utc),
        )
        db.add(connector)

    await db.commit()
    log.info("GitHub connector saved", user_id=state, username=github_username)
    return RedirectResponse(url=f"{settings.FRONTEND_URL}/outreach/settings?github_connected=true")


@router.delete("/connectors/github/{connector_id}")
async def disconnect_github_connector(
    connector_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Disconnect (delete) a GitHub connector."""
    result = await db.execute(
        select(OutreachGitHubConnector).where(
            OutreachGitHubConnector.id == connector_id,
            OutreachGitHubConnector.user_id == current_user.id,
        )
    )
    connector = result.scalar_one_or_none()
    if not connector:
        raise HTTPException(status_code=404, detail="Connector not found")
    await db.delete(connector)
    await db.commit()
    return {"status": "disconnected"}
