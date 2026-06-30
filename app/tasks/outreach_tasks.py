"""
app/tasks/outreach_tasks.py
─────────────────────────────
Celery tasks for the Outreach Platform.

Tasks:
  • send_scheduled_outreach_emails  – every 15 min: deliver approved/scheduled emails
  • poll_outreach_replies           – every hour: detect replies via Gmail History API
  • schedule_outreach_followups     – daily: queue follow-up emails for no-reply threads
"""
from __future__ import annotations

import asyncio
import uuid
from datetime import datetime, timezone, timedelta

import structlog

from app.celery_app import celery_app

log = structlog.get_logger()

_LOOP: asyncio.AbstractEventLoop | None = None


def _get_loop() -> asyncio.AbstractEventLoop:
    global _LOOP
    if _LOOP is None or _LOOP.is_closed():
        _LOOP = asyncio.new_event_loop()
    return _LOOP


def _run(coro):
    loop = _get_loop()
    asyncio.set_event_loop(loop)
    return loop.run_until_complete(coro)


# ── 1. Send scheduled emails ───────────────────────────────────────────────────

@celery_app.task(bind=True, max_retries=2, default_retry_delay=300)
def send_scheduled_outreach_emails(self):
    """Send all outreach emails that are approved or scheduled and due now."""
    try:
        _run(_do_send_scheduled())
    except Exception as exc:
        log.error("send_scheduled_outreach_emails failed", error=str(exc))
        raise self.retry(exc=exc)


async def _do_send_scheduled():
    from sqlalchemy import select
    from sqlalchemy.orm import selectinload

    from app.core.database import get_db_context
    from app.models.outreach import (
        OutreachEmail, OutreachConversation, OutreachCompany,
        OutreachEmailConnector, OutreachEmailStatus, OutreachConversationStatus,
        OutreachCompanyStatus, OutreachEmailProvider,
    )
    from app.services.encryption import EncryptionService
    from app.services import gmail_oauth_service as gmail

    now = datetime.now(timezone.utc)
    enc = EncryptionService()

    async with get_db_context() as db:
        # Fetch all approved/scheduled emails that are due
        result = await db.execute(
            select(OutreachEmail)
            .options(selectinload(OutreachEmail.contact))
            .where(
                OutreachEmail.status.in_(["APPROVED", "SCHEDULED"]),
                (OutreachEmail.scheduled_at == None) | (OutreachEmail.scheduled_at <= now),
            )
        )
        emails = result.scalars().all()
        log.info("outreach send sweep", due_count=len(emails))

        for email_obj in emails:
            try:
                await _send_single_email(db, email_obj, enc, gmail, now)
            except Exception as exc:
                log.warning("outreach email send failed", email_id=email_obj.id, error=str(exc))

        await db.commit()


async def _send_single_email(db, email_obj, enc, gmail, now):
    """Send one outreach email via Gmail and update DB records."""
    from sqlalchemy import select, update
    from app.models.outreach import (
        OutreachEmailConnector, OutreachConversation, OutreachCompany,
        OutreachEmailStatus, OutreachConversationStatus, OutreachCompanyStatus,
    )

    # Load connector for this user
    conn_result = await db.execute(
        select(OutreachEmailConnector).where(
            OutreachEmailConnector.user_id == email_obj.user_id,
            OutreachEmailConnector.is_active == True,
        )
    )
    connector = conn_result.scalar_one_or_none()
    if not connector:
        log.info("no connector for user, skipping", user_id=email_obj.user_id)
        return

    from app.services import gmail_oauth_service as gmail_svc
    access_token = await gmail_svc.get_valid_token(connector, enc)

    to_address = email_obj.to_address
    if not to_address and email_obj.contact:
        to_address = email_obj.contact.email
    if not to_address:
        log.warning("no recipient for email", email_id=email_obj.id)
        return

    sent = gmail_svc.send_email(
        access_token=access_token,
        to=to_address,
        subject=email_obj.subject or "(no subject)",
        body=email_obj.body or "",
        from_email=connector.email_address,
    )

    email_obj.status = OutreachEmailStatus.SENT
    email_obj.sent_at = now
    email_obj.from_address = connector.email_address
    email_obj.to_address = to_address
    email_obj.provider_message_id = sent["message_id"]
    email_obj.provider_thread_id  = sent["thread_id"]

    # Upsert conversation
    conv_result = await db.execute(
        select(OutreachConversation).where(
            OutreachConversation.user_id == email_obj.user_id,
            OutreachConversation.company_id == email_obj.company_id,
        )
    )
    conv = conv_result.scalar_one_or_none()
    if not conv:
        conv = OutreachConversation(
            id=str(uuid.uuid4()),
            user_id=email_obj.user_id,
            contact_id=email_obj.contact_id,
            company_id=email_obj.company_id,
            campaign_id=email_obj.campaign_id,
            thread_id=sent["thread_id"],
            status=OutreachConversationStatus.AWAITING_REPLY,
            last_message_at=now,
        )
        db.add(conv)
    else:
        conv.thread_id = sent["thread_id"]
        conv.last_message_at = now

    if email_obj.company_id:
        await db.execute(
            update(OutreachCompany)
            .where(OutreachCompany.id == email_obj.company_id)
            .values(status=OutreachCompanyStatus.CONTACTED)
        )

    log.info("outreach email sent", email_id=email_obj.id, to=to_address, thread=sent["thread_id"])


# ── 2. Poll for replies ────────────────────────────────────────────────────────

@celery_app.task(bind=True, max_retries=2, default_retry_delay=600)
def poll_outreach_replies(self):
    """Check Gmail History API for replies to outreach threads."""
    try:
        _run(_do_poll_replies())
    except Exception as exc:
        log.error("poll_outreach_replies failed", error=str(exc))
        raise self.retry(exc=exc)


async def _do_poll_replies():
    from sqlalchemy import select

    from app.core.database import get_db_context
    from app.models.outreach import (
        OutreachEmailConnector, OutreachConversation, OutreachConversationStatus,
    )
    from app.services.encryption import EncryptionService
    from app.services import gmail_oauth_service as gmail_svc

    enc = EncryptionService()
    now = datetime.now(timezone.utc)

    async with get_db_context() as db:
        # Get all active connectors
        result = await db.execute(
            select(OutreachEmailConnector).where(OutreachEmailConnector.is_active == True)
        )
        connectors = result.scalars().all()

        for connector in connectors:
            try:
                await _poll_connector_replies(db, connector, enc, gmail_svc, now)
            except Exception as exc:
                log.warning("reply poll failed for connector", connector_id=connector.id, error=str(exc))

        await db.commit()


async def _poll_connector_replies(db, connector, enc, gmail_svc, now):
    """Poll one connector for new replies using Gmail History API."""
    from sqlalchemy import select

    from app.models.outreach import OutreachConversation, OutreachConversationStatus

    if not connector.last_history_id:
        # First-time: just capture the current historyId as baseline
        try:
            access_token = await gmail_svc.get_valid_token(connector, enc)
            profile = gmail_svc.get_profile(access_token)
            connector.last_history_id = profile.get("historyId")
            connector.last_sync_at = now
        except Exception:
            pass
        return

    try:
        access_token = await gmail_svc.get_valid_token(connector, enc)
    except ValueError:
        connector.is_active = False
        return

    history_records = gmail_svc.get_history(access_token, connector.last_history_id)
    if not history_records:
        connector.last_sync_at = now
        return

    # Collect thread IDs that received new messages
    reply_thread_ids: set[str] = set()
    for record in history_records:
        for msg_added in record.get("messagesAdded", []):
            msg = msg_added.get("message", {})
            tid = msg.get("threadId")
            label_ids = msg.get("labelIds", [])
            if tid and "INBOX" in label_ids and "SENT" not in label_ids:
                reply_thread_ids.add(tid)

    if reply_thread_ids:
        # Find conversations matching these thread IDs
        conv_result = await db.execute(
            select(OutreachConversation).where(
                OutreachConversation.user_id == connector.user_id,
                OutreachConversation.thread_id.in_(reply_thread_ids),
                OutreachConversation.status == OutreachConversationStatus.AWAITING_REPLY,
            )
        )
        conversations = conv_result.scalars().all()
        for conv in conversations:
            conv.status = OutreachConversationStatus.REPLIED
            conv.last_message_at = now
            log.info("reply detected", conv_id=conv.id, thread_id=conv.thread_id)

    # Update the history baseline to the latest historyId
    try:
        profile = gmail_svc.get_profile(access_token)
        connector.last_history_id = profile.get("historyId")
    except Exception:
        pass
    connector.last_sync_at = now


# ── 3. Schedule follow-ups ─────────────────────────────────────────────────────

@celery_app.task(bind=True, max_retries=1)
def schedule_outreach_followups(self):
    """
    For outreach conversations still awaiting reply after 5 days,
    create a follow-up email draft (if campaign has sequence enabled).
    """
    try:
        _run(_do_schedule_followups())
    except Exception as exc:
        log.error("schedule_outreach_followups failed", error=str(exc))
        raise self.retry(exc=exc)


async def _do_schedule_followups():
    from sqlalchemy import select

    from app.core.database import get_db_context
    from app.models.outreach import (
        OutreachConversation, OutreachConversationStatus,
        OutreachEmail, OutreachEmailStatus, OutreachFollowUp,
    )

    followup_window = datetime.now(timezone.utc) - timedelta(days=5)

    async with get_db_context() as db:
        result = await db.execute(
            select(OutreachConversation).where(
                OutreachConversation.status == OutreachConversationStatus.AWAITING_REPLY,
                OutreachConversation.last_message_at <= followup_window,
                OutreachConversation.campaign_id != None,
            )
        )
        stale_convs = result.scalars().all()
        log.info("followup check", stale_count=len(stale_convs))

        for conv in stale_convs:
            # Check if a follow-up already exists for this conversation
            fu_result = await db.execute(
                select(OutreachFollowUp).where(
                    OutreachFollowUp.company_id == conv.company_id,
                    OutreachFollowUp.user_id == conv.user_id,
                    OutreachFollowUp.status == "PENDING",
                )
            )
            if fu_result.scalar_one_or_none():
                continue  # already scheduled

            followup = OutreachFollowUp(
                id=str(uuid.uuid4()),
                user_id=conv.user_id,
                contact_id=conv.contact_id,
                company_id=conv.company_id,
                campaign_id=conv.campaign_id,
                sequence_position=2,
                scheduled_at=datetime.now(timezone.utc) + timedelta(hours=1),
                status="PENDING",
            )
            db.add(followup)
            log.info("followup scheduled", conv_id=conv.id)

        await db.commit()
