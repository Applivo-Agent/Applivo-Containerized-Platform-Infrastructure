"""
app/services/notification_service.py
──────────────────────────────────────
Module 8: Notification System
Sends notifications via Telegram Bot and Email (SMTP).
Every notification is logged in the Notification table for audit/history.
"""

from __future__ import annotations

from datetime import datetime, timezone
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Optional

import aiosmtplib
import structlog
from sqlalchemy import select, func

from app.core.config import settings
from app.core.database import get_db_context
from app.models.interview import Notification, NotificationStatus

logger = structlog.get_logger()


class NotificationService:
    """
    Central notification dispatcher.
    Supports Telegram Bot and Email channels.
    Automatically reads user preferences before sending.
    """

    async def notify(
        self,
        title: str,
        body: str,
        event_type: str,
        data: Optional[dict] = None,
        telegram_markup: Optional[dict] = None,
        user_id: Optional[str] = None,
        attachment_path: Optional[str] = None,  # For PDF invoices, etc.
        send_email: bool = True,
        send_telegram: bool = True,
    ) -> None:
        """
        Create and dispatch notifications to the specified user (or first user if not given).
        FIX 6: Accepts user_id for proper multi-user routing.
        Each user gets their own telegram_chat_id and notification_email.
        """
        async with get_db_context() as db:
            from app.models.user import User, UserProfile

            # Resolve user first. Profile is optional.
            if user_id:
                user_result = await db.execute(
                    select(User).where(User.id == user_id)
                )
            else:
                user_result = await db.execute(
                    select(User).where(User.is_active == True).limit(1)
                )
            user = user_result.scalar_one_or_none()

            if not user:
                logger.warning("No user found — skipping notification", user_id=user_id)
                return

            profile_result = await db.execute(
                select(UserProfile).where(UserProfile.user_id == user.id)
            )
            profile = profile_result.scalar_one_or_none()

            resolved_user_id = user.id

            # Resolve Telegram chat ID
            per_user_chat_id = (profile.telegram_chat_id if profile else None) or settings.TELEGRAM_CHAT_ID
            
            notify_telegram_pref = profile.notify_via_telegram if profile else True
            notify_email_pref = profile.notify_via_email if profile else True

            notify_telegram = bool(send_telegram and settings.TELEGRAM_BOT_TOKEN and per_user_chat_id and notify_telegram_pref)
            notify_email = bool(send_email and settings.SMTP_HOST and settings.SMTP_USERNAME and settings.SMTP_PASSWORD and notify_email_pref)

            if notify_telegram:
                tg_notif = Notification(
                    user_id=resolved_user_id,
                    channel="telegram",
                    title=title,
                    body=body,
                    event_type=event_type,
                    data=data,
                    telegram_reply_markup=telegram_markup,
                )
                db.add(tg_notif)
                await db.flush()
                # FIX 6: pass the per-user chat_id so _send_telegram uses it
                await self._send_telegram(tg_notif, db, chat_id=per_user_chat_id)

            if notify_email:
                # Fallback chain: notification_email -> user.email -> configured backup
                to_email = (profile.notification_email if profile else None) or user.email or settings.USER_EMAIL
                
                if not to_email:
                    logger.warning("No email address found for notification", user_id=resolved_user_id)
                    return
                    
                email_notif = Notification(
                    user_id=resolved_user_id,
                    channel="email",
                    title=title,
                    body=body,
                    event_type=event_type,
                    data=data,
                )
                db.add(email_notif)
                await db.flush()
                await self._send_email(email_notif, to_email, db, attachment_path=attachment_path)

            await db.commit()

    # ── Telegram ─────────────────────────────────────────────────────────────

    async def send_telegram(self, notification_id: str) -> dict:
        """Send a specific notification by ID via Telegram. Used by Celery tasks."""
        async with get_db_context() as db:
            result = await db.execute(
                select(Notification).where(Notification.id == notification_id)
            )
            notif = result.scalar_one_or_none()
            if not notif:
                return {"error": "Notification not found"}
            result = await self._send_telegram(notif, db)
            await db.commit()
            return result

    async def _send_telegram(self, notif: Notification, db, chat_id: str = None) -> dict:
        """Internal Telegram send. FIX 6: accepts per-user chat_id override."""
        try:
            import httpx

            # FIX 6: prefer the passed per-user chat_id over the global setting
            effective_chat_id = chat_id or settings.TELEGRAM_CHAT_ID
            text = f"*{notif.title}*\n\n{notif.body}"
            payload: dict = {
                "chat_id": effective_chat_id,
                "text": text,
                "parse_mode": "Markdown",
            }
            if notif.telegram_reply_markup:
                payload["reply_markup"] = notif.telegram_reply_markup

            # Retry Telegram POST up to 3 times with exponential backoff
            last_exc = None
            data = {}
            for attempt in range(3):
                try:
                    async with httpx.AsyncClient(timeout=15) as http:
                        response = await http.post(
                            f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage",
                            json=payload,
                        )
                        data = response.json()
                        break
                except Exception as exc:
                    last_exc = exc
                    if attempt < 2:
                        import asyncio
                        await asyncio.sleep(2 ** attempt)
            if not data and last_exc:
                raise last_exc

            if data.get("ok"):
                notif.status = NotificationStatus.SENT
                notif.sent_at = datetime.now(timezone.utc)
                notif.telegram_message_id = str(data["result"]["message_id"])
                logger.info("Telegram notification sent", title=notif.title)
                return {"sent": True}
            else:
                notif.status = NotificationStatus.FAILED
                error_data = data
                if data.get("error_code") == 403:
                    error_msg = "Forbidden: Bots can't send messages to bots. PLEASE ENSURE YOUR TELEGRAM_CHAT_ID IS YOUR USER ID, NOT YOUR BOT ID."
                    error_data["recommendation"] = error_msg
                    logger.error("Telegram forbidden — mapping bot to bot?", error=error_msg, chat_id=effective_chat_id)
                
                notif.error_message = str(error_data)
                logger.error("Telegram send failed", error=data)
                return {"error": str(data)}

        except Exception as e:
            notif.status = NotificationStatus.FAILED
            notif.error_message = str(e)
            logger.error("Telegram exception", error=str(e))
            return {"error": str(e)}

    # ── Email ─────────────────────────────────────────────────────────────────

    async def send_email(self, notification_id: str) -> dict:
        """Send a specific notification by ID via Email. Used by Celery tasks."""
        async with get_db_context() as db:
            result = await db.execute(
                select(Notification).where(Notification.id == notification_id)
            )
            notif = result.scalar_one_or_none()
            if not notif:
                return {"error": "Notification not found"}
            from app.models.user import User, UserProfile
            profile = (await db.execute(select(UserProfile).where(UserProfile.user_id == notif.user_id))).scalar_one_or_none()
            user_email = (await db.execute(select(User.email).where(User.id == notif.user_id))).scalar_one_or_none()
            to_email = (profile.notification_email if profile else None) or user_email or settings.USER_EMAIL or settings.SMTP_USERNAME
            result = await self._send_email(notif, to_email, db)
            await db.commit()
            return result

    async def _send_email(self, notif: Notification, to_email: str, db, attachment_path: Optional[str] = None) -> dict:
        """Internal email send with support for attachments."""
        try:
            from_email = settings.SMTP_FROM_EMAIL or settings.SMTP_USERNAME
            if not from_email:
                raise ValueError("SMTP_FROM_EMAIL/SMTP_USERNAME is not configured")

            msg = MIMEMultipart("alternative")
            msg["Subject"] = notif.title
            msg["From"] = f"{settings.SMTP_FROM_NAME} <{from_email}>"
            msg["To"] = to_email

            # Plain text — use UTF-8 to support emojis
            msg.attach(MIMEText(notif.body, "plain", "utf-8"))

            # HTML version
            html_body = f"""
            <html>
            <body style="font-family: Arial, sans-serif; max-width: 600px; margin: auto; padding: 20px; background: #f9f9f9;">
              <div style="background: white; padding: 24px; border-radius: 8px; border-left: 4px solid #00d4ff;">
                <h2 style="color: #1a1a2e; margin-top: 0;">{notif.title}</h2>
                <div style="color: #444; white-space: pre-line; line-height: 1.6;">{notif.body}</div>
              </div>
              <p style="color: #aaa; font-size: 11px; text-align: center; margin-top: 16px;">
                AI Career Platform &middot; Automated notification
              </p>
            </body>
            </html>
            """
            msg.attach(MIMEText(html_body, "html"))

            # Attachment (e.g. PDF Invoice)
            if attachment_path:
                try:
                    import os
                    from email.mime.application import MIMEApplication
                    if os.path.exists(attachment_path):
                        with open(attachment_path, "rb") as f:
                            part = MIMEApplication(f.read(), _subtype="pdf")
                            part.add_header(
                                "Content-Disposition",
                                "attachment",
                                filename=os.path.basename(attachment_path)
                            )
                            msg.attach(part)
                except Exception as ae:
                    logger.error("Failed to attach file to email", path=attachment_path, error=str(ae))

            await aiosmtplib.send(
                msg,
                hostname=settings.SMTP_HOST,
                port=settings.SMTP_PORT,
                username=settings.SMTP_USERNAME,
                password=settings.SMTP_PASSWORD,
                start_tls=True,
                timeout=30,
            )

            notif.status = NotificationStatus.SENT
            notif.sent_at = datetime.now(timezone.utc)
            logger.info("Email notification sent", title=notif.title, to=to_email)
            return {"sent": True}

        except Exception as e:
            notif.status = NotificationStatus.FAILED
            notif.error_message = str(e)
            logger.error("Email send failed", error=str(e))
            return {"error": str(e)}

    async def send_email_to_user(self, subject: str, body: str, to_email: str = None) -> dict:
        """
        Send an email directly to the user's email address.
        Used for forwarding recruiter messages from applivoagent@gmail.com inbox.
        Reads destination from UserProfile.notification_email → settings.USER_EMAIL → SMTP_USERNAME.
        """
        if not to_email:
            async with get_db_context() as _db:
                from app.models.user import UserProfile
                _profile = (await _db.execute(select(UserProfile).limit(1))).scalar_one_or_none()
            to_email = (
                (_profile.notification_email if _profile else "")
                or settings.USER_EMAIL
                or settings.SMTP_USERNAME
            )
        if not to_email:
            logger.warning("send_email_to_user: no destination email configured — skipping")
            return {"error": "No destination email configured"}
        
        try:
            from_email = settings.SMTP_FROM_EMAIL or settings.SMTP_USERNAME
            if not from_email:
                return {"error": "SMTP_FROM_EMAIL/SMTP_USERNAME is not configured"}

            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = f"{settings.SMTP_FROM_NAME} <{from_email}>"
            msg["To"] = to_email

            # Plain text
            msg.attach(MIMEText(body, "plain"))

            # HTML version
            html_body = f"""
            <html>
            <body style="font-family: Arial, sans-serif; max-width: 600px; margin: auto; padding: 20px; background: #f9f9f9;">
              <div style="background: white; padding: 24px; border-radius: 8px; border-left: 4px solid #00d4ff;">
                <h2 style="color: #1a1a2e; margin-top: 0;">{subject}</h2>
                <div style="color: #444; white-space: pre-line; line-height: 1.6;">{body}</div>
              </div>
              <p style="color: #aaa; font-size: 11px; text-align: center; margin-top: 16px;">
                AI Career Platform &middot; Automated notification
              </p>
            </body>
            </html>
            """
            msg.attach(MIMEText(html_body, "html"))

            await aiosmtplib.send(
                msg,
                hostname=settings.SMTP_HOST,
                port=settings.SMTP_PORT,
                username=settings.SMTP_USERNAME,
                password=settings.SMTP_PASSWORD,
                start_tls=True,
                timeout=30,
            )

            logger.info("User email sent successfully", to=to_email)
            return {"sent": True, "to": to_email}

        except Exception as e:
            logger.error("User email send failed", error=str(e))
            return {"error": str(e)}

    # ── Digest ────────────────────────────────────────────────────────────────

    async def send_daily_digest(self) -> dict:
        """
        Send daily summary per user: jobs found, applications sent, top matches.
        Only sent to users with an active subscription.
        Called by Celery beat daily.
        """
        from app.models.job import Job, JobAnalysis
        from app.models.application import Application
        from app.models.subscription import Subscription, SubscriptionStatus
        from app.models.user import User

        async with get_db_context() as db:
            today = datetime.now(timezone.utc).date()

            # Only notify users who have an ACTIVE subscription
            result = await db.execute(
                select(User.id)
                .join(Subscription, Subscription.user_id == User.id)
                .where(
                    User.is_active == True,
                    Subscription.status == SubscriptionStatus.ACTIVE,
                )
                .distinct()
            )
            user_ids = [row[0] for row in result.fetchall()]

        if not user_ids:
            logger.info("No active subscribers — skipping digest")
            return {"sent": False, "reason": "No active subscribers"}

        sent_count = 0
        for uid in user_ids:
            try:
                async with get_db_context() as db:
                    today = datetime.now(timezone.utc).date()

                    # Per-user: count jobs scraped today (global pool)
                    jobs_today = (await db.execute(
                        select(func.count(Job.id)).where(
                            func.date(Job.scraped_at) == today
                        )
                    )).scalar() or 0

                    # Per-user: count their own applications sent today
                    apps_today = (await db.execute(
                        select(func.count(Application.id)).where(
                            Application.user_id == uid,
                            func.date(Application.applied_at) == today,
                        )
                    )).scalar() or 0

                    # Per-user: top matching jobs from their own analyses
                    top_jobs = (await db.execute(
                        select(Job.title, Job.company_name, JobAnalysis.match_score)
                        .join(JobAnalysis, Job.id == JobAnalysis.job_id)
                        .where(
                            JobAnalysis.user_id == uid,
                            func.date(Job.scraped_at) == today,
                            JobAnalysis.match_score.isnot(None),
                        )
                        .order_by(JobAnalysis.match_score.desc())
                        .limit(5)
                    )).all()

                if not jobs_today and not apps_today:
                    logger.info("No activity today for user — skipping digest", user_id=uid)
                    continue

                job_lines = "\n".join(
                    f"• {j.company_name} — {j.title} ({j.match_score:.0f}% match)"
                    for j in top_jobs
                ) or "No top matches yet — check back tomorrow!"

                body = f"""📊 Your Daily Career Update

Jobs Found Today: {jobs_today}
Applications Sent: {apps_today}

🔥 Top Matches:
{job_lines}

Keep up the great work! Your next opportunity is just around the corner.

— Applivo AI"""

                await self.notify(
                    title="Daily Career Update",
                    body=body,
                    event_type="daily_digest",
                    data={"jobs_today": jobs_today, "apps_today": apps_today},
                    user_id=uid,
                )
                sent_count += 1
            except Exception as e:
                logger.error("Failed to send digest to user", user_id=uid, error=str(e))

        return {"sent": True, "users_notified": sent_count}