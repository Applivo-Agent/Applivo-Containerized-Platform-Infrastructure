"""
app/services/follow_up_service.py
────────────────────────────────────
Module 7: Follow-up Automation
Auto follow-up emails to recruiters, interview thank-you emails,
and application reminder notifications.
"""

from __future__ import annotations

from datetime import datetime, timezone, timedelta

import structlog
from openai import AsyncOpenAI
from sqlalchemy import select, and_

from app.core.config import settings
from app.core.database import get_db_context
from app.models.application import Application, ApplicationStatus, FollowUpStatus
from app.models.user import UserProfile

logger = structlog.get_logger()
client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

FOLLOW_UP_PROMPT = """
Write a brief, professional follow-up email for a job application.
Keep it under 100 words. Be polite, not pushy.
Reference the role and company specifically.
Return only the email body text, no subject line.
"""

THANK_YOU_PROMPT = """
Write a brief thank-you email after a job interview.
Keep it under 120 words. Mention one specific thing discussed.
Express continued enthusiasm for the role.
Return only the email body text, no subject line.
"""


class FollowUpService:

    async def process_due_follow_ups(self) -> dict:
        """Check for applications needing follow-up and send emails."""
        now = datetime.now(timezone.utc)
        sent = 0

        async with get_db_context() as db:
            # Applications applied 7 days ago with no response
            week_ago = now - timedelta(days=7)
            stale_apps = (await db.execute(
                select(Application).where(
                    and_(
                        Application.status == ApplicationStatus.APPLIED,
                        Application.applied_at <= week_ago,
                        Application.follow_up_status == FollowUpStatus.NONE,
                        Application.recruiter_email.isnot(None),
                    )
                )
            )).scalars().all()

            for app in stale_apps:
                try:
                    await self._send_follow_up_email(app, db)
                    app.follow_up_status = FollowUpStatus.SENT
                    app.last_follow_up_at = now
                    app.follow_up_count += 1
                    sent += 1
                except Exception as e:
                    logger.error("Follow-up failed", app_id=app.id, error=str(e))

            # Interview thank-you emails (24h after interview)
            day_ago = now - timedelta(hours=24)
            completed_interviews = (await db.execute(
                select(Application).where(
                    and_(
                        Application.status == ApplicationStatus.INTERVIEW_COMPLETED,
                        Application.interview_date <= day_ago,
                        Application.interview_date >= day_ago - timedelta(hours=24),
                        Application.recruiter_email.isnot(None),
                    )
                )
            )).scalars().all()

            for app in completed_interviews:
                try:
                    await self._send_thank_you_email(app, db)
                    sent += 1
                except Exception as e:
                    logger.error("Thank-you email failed", app_id=app.id, error=str(e))

            await db.commit()

        return {"follow_ups_sent": sent}

    async def _send_follow_up_email(self, app: Application, db) -> None:
        """Generate and send a follow-up email."""
        try:
            response = await client.chat.completions.create(
                model=settings.OPENAI_MODEL_LIGHT,
                max_tokens=200,
                temperature=0.4,
                messages=[
                    {"role": "system", "content": FOLLOW_UP_PROMPT},
                    {"role": "user", "content": f"Role: {app.job_title_snapshot}\nCompany: {app.company_snapshot}\nApplied: {app.applied_at.strftime('%B %d') if app.applied_at else 'recently'}"},
                ],
            )
            email_body = response.choices[0].message.content
        except Exception:
            email_body = (
                f"Dear Hiring Team,\n\nI wanted to follow up on my application for the "
                f"{app.job_title_snapshot} position at {app.company_snapshot}. "
                f"I remain very interested in this opportunity and would love to discuss "
                f"how my skills align with your needs.\n\nThank you for your consideration.\n\nBest regards"
            )

        # Send via email service
        if app.recruiter_email:
            import aiosmtplib
            from email.mime.text import MIMEText
            from email.mime.multipart import MIMEMultipart

            msg = MIMEMultipart()
            msg["Subject"] = f"Following up: {app.job_title_snapshot} Application"
            msg["From"] = f"{settings.SMTP_FROM_NAME} <{settings.SMTP_FROM_EMAIL}>"
            msg["To"] = app.recruiter_email
            msg.attach(MIMEText(email_body, "plain"))

            await aiosmtplib.send(
                msg,
                hostname=settings.SMTP_HOST,
                port=settings.SMTP_PORT,
                username=settings.SMTP_USERNAME,
                password=settings.SMTP_PASSWORD,
                start_tls=True,
            )
            logger.info("Follow-up email sent", app_id=app.id, to=app.recruiter_email)

    async def _send_thank_you_email(self, app: Application, db) -> None:
        """Generate and send a post-interview thank-you email."""
        try:
            response = await client.chat.completions.create(
                model=settings.OPENAI_MODEL_LIGHT,
                max_tokens=200,
                temperature=0.5,
                messages=[
                    {"role": "system", "content": THANK_YOU_PROMPT},
                    {"role": "user", "content": f"Role: {app.job_title_snapshot}\nCompany: {app.company_snapshot}\nInterview type: {app.interview_type or 'technical'}"},
                ],
            )
            email_body = response.choices[0].message.content
        except Exception:
            email_body = (
                f"Dear {app.recruiter_name or 'Hiring Team'},\n\n"
                f"Thank you for taking the time to interview me for the {app.job_title_snapshot} "
                f"role at {app.company_snapshot}. I enjoyed our conversation and am even more "
                f"excited about the opportunity.\n\nI look forward to hearing from you.\n\nBest regards"
            )

        if app.recruiter_email:
            import aiosmtplib
            from email.mime.text import MIMEText
            from email.mime.multipart import MIMEMultipart

            msg = MIMEMultipart()
            msg["Subject"] = f"Thank you — {app.job_title_snapshot} Interview"
            msg["From"] = f"{settings.SMTP_FROM_NAME} <{settings.SMTP_FROM_EMAIL}>"
            msg["To"] = app.recruiter_email
            msg.attach(MIMEText(email_body, "plain"))

            await aiosmtplib.send(
                msg,
                hostname=settings.SMTP_HOST,
                port=settings.SMTP_PORT,
                username=settings.SMTP_USERNAME,
                password=settings.SMTP_PASSWORD,
                start_tls=True,
            )
            logger.info("Thank-you email sent", app_id=app.id)
