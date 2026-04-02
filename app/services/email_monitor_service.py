"""
app/services/email_monitor_service.py
────────────────────────────────────
Email inbox monitoring service for applivoagent@gmail.com
Monitors for recruiter messages and forwards them to the user.
"""

from __future__ import annotations

import asyncio
import email
import imaplib
import re
from datetime import datetime, timezone, timedelta
from typing import List, Optional
from email import policy
from email.parser import BytesParser

import structlog

from app.core.config import settings

logger = structlog.get_logger()


class EmailMonitorService:
    """
    Monitors applivoagent@gmail.com inbox for recruiter messages.
    Forwards important emails to the user via Telegram/Email.
    """
    
    # Keywords that indicate a recruiter message
    RECRUITER_KEYWORDS = [
        "interview", "hiring", "job", "position", "opportunity",
        "resume", "application", "vacancy", "offer", "candidate",
        "recruiter", "hr", "hiring manager", "selection",
        "schedule", "call", "meeting", "discussion"
    ]
    
    # Keywords that indicate screening questions
    SCREENING_KEYWORDS = [
        "question", "screening", "answer", "please answer",
        "tell us", "describe", "explain", "experience with",
        "how many years", "describe your", "what is your"
    ]

    def __init__(self):
        self.host = settings.IMAP_HOST
        self.port = settings.IMAP_PORT
        self.username = settings.IMAP_USERNAME or settings.SMTP_USERNAME
        self.password = settings.IMAP_PASSWORD or settings.SMTP_PASSWORD
        self.last_checked = None

    def _connect(self) -> imaplib.IMAP4_SSL:
        """Connect to IMAP server."""
        try:
            mail = imaplib.IMAP4_SSL(self.host, self.port)
            mail.login(self.username, self.password)
            logger.info("Connected to IMAP server")
            return mail
        except Exception as e:
            logger.error("Failed to connect to IMAP", error=str(e))
            raise

    def _is_recruiter_email(self, subject: str, body: str) -> bool:
        """Check if email is from a recruiter."""
        text = (subject + " " + body).lower()
        
        # Check for recruiter keywords
        keyword_count = sum(1 for kw in self.RECRUITER_KEYWORDS if kw in text)
        
        # Also check for common recruiter email patterns
        recruiter_patterns = [
            r"hr@", r"recruiter@", r"hiring@", r"careers@",
            r"jobs@", r"talent@", r"recruitment@"
        ]
        
        has_recruiter_pattern = any(
            re.search(p, text) for p in recruiter_patterns
        )
        
        return keyword_count >= 2 or has_recruiter_pattern

    def _has_screening_questions(self, body: str) -> bool:
        """Check if email contains screening questions."""
        text = body.lower()
        keyword_count = sum(1 for kw in self.SCREENING_KEYWORDS if kw in text)
        return keyword_count >= 2

    async def check_inbox(self, limit: int = 10) -> List[dict]:
        """
        Check inbox for new recruiter messages.
        Returns list of recruiter messages found.
        """
        messages = []
        
        def _sync_check():
            nonlocal messages
            mail = self._connect()
            try:
                # Select inbox
                status, _ = mail.select("INBOX")
                if status != "OK":
                    logger.warning("Failed to select inbox")
                    return
                
                # Search for unread emails from last 7 days
                since_date = (datetime.now() - timedelta(days=7)).strftime("%d-%b-%Y")
                search_criteria = f'(SINCE {since_date} UNSEEN)'
                
                status, message_ids = mail.search(None, search_criteria)
                if status != "OK":
                    return
                
                ids = message_ids[0].split()
                logger.info(f"Found {len(ids)} unread emails")
                
                # Process most recent emails
                for msg_id in reversed(ids[-limit:]):
                    try:
                        status, msg_data = mail.fetch(msg_id, "(RFC822)")
                        if status != "OK":
                            continue
                        
                        raw_email = msg_data[0][1]
                        msg = email.message_from_bytes(raw_email, policy=policy.default)
                        
                        # Parse email
                        subject = msg.get("subject", "")
                        from_addr = msg.get("from", "")
                        date = msg.get("date", "")
                        
                        # Get body
                        body = ""
                        if msg.is_multipart():
                            for part in msg.walk():
                                if part.get_content_type() == "text/plain":
                                    body = part.get_content()
                                    break
                        else:
                            body = msg.get_content()
                        
                        # Check if recruiter email
                        if self._is_recruiter_email(subject, body):
                            has_screening = self._has_screening_questions(body)
                            
                            messages.append({
                                "subject": subject,
                                "from": from_addr,
                                "date": date,
                                "body": body[:2000],  # Limit body length
                                "has_screening_questions": has_screening,
                                "message_id": msg_id.decode() if isinstance(msg_id, bytes) else msg_id,
                            })
                            
                            # Mark as read
                            mail.store(msg_id, '+FLAGS', '\\Seen')
                            
                    except Exception as e:
                        logger.warning("Failed to parse email", error=str(e))
                        continue
                        
            finally:
                mail.close()
                mail.logout()
        
        # Run IMAP in thread pool since it's sync
        loop = asyncio.get_event_loop()
        messages = await loop.run_in_executor(None, _sync_check)
        
        if messages is None:
            messages = []
            
        self.last_checked = datetime.now(timezone.utc)
        logger.info(f"Found {len(messages)} recruiter messages")
        
        return messages

    async def forward_to_user(self, message: dict) -> dict:
        """
        Forward a recruiter message to the user via Telegram AND email.
        If it contains screening questions, also generate AI answers.
        """
        from app.services.notification_service import NotificationService
        
        # Format message
        subject = message.get("subject", "No Subject")
        from_addr = message.get("from", "Unknown")
        body = message.get("body", "")[:1500]
        
        text = f"📧 **New Recruiter Message**\n\n"
        text += f"**From:** {from_addr}\n"
        text += f"**Subject:** {subject}\n\n"
        text += f"**Preview:**\n{body}...\n\n"
        
        # Check for screening questions
        if message.get("has_screening_questions"):
            text += "⚠️ **Contains screening questions - generating AI answers...**\n"
            
            # Generate AI answers
            try:
                from app.services.screening_question_service import ScreeningQuestionService
                from app.core.database import get_db_context
                
                # Get user context
                async with get_db_context() as db:
                    from app.models.user import UserProfile
                    result = await db.execute(select(UserProfile).limit(1))
                    profile = result.scalar_one_or_none()
                    
                    if profile:
                        # Extract questions from body
                        questions = self._extract_questions(body)
                        
                        if questions:
                            text += "\n**Generated Answers:**\n"
                            
                            # Generate answers for each question
                            screening_service = ScreeningQuestionService(db, profile.user_id)
                            user_context = await screening_service.get_user_context()
                            
                            for i, question in enumerate(questions[:5], 1):
                                answer = await screening_service.generate_answer(
                                    question, user_context
                                )
                                text += f"\n**Q{i}:** {question}\n"
                                text += f"**A{i}:** {answer}\n"
            except Exception as e:
                logger.error("Failed to generate screening answers", error=str(e))
                text += "\n⚠️ Failed to generate answers. Please answer manually.\n"
        
        # Send via Telegram
        try:
            notification_service = NotificationService()
            # Create a notification and send
            result = await notification_service.send_telegram_message(text)
        except Exception as e:
            logger.error("Failed to forward message via Telegram", error=str(e))
        
        # Also send via email to sudharsan97511@gmail.com
        try:
            from app.services.notification_service import NotificationService
            notification_service = NotificationService()
            await notification_service.send_email_to_user(
                subject=f"New Recruiter Message: {subject}",
                body=text
            )
        except Exception as e:
            logger.error("Failed to forward message via Email", error=str(e))
        
        return {"status": "sent", "telegram": True, "email": True}

    def _extract_questions(self, text: str) -> list:
        """Extract questions from email body."""
        import re
        # Find question marks or question patterns
        questions = re.findall(r'(?:\d+[\.\)]\s*)?([A-Z][^?]*\?)', text)
        return [q.strip() for q in questions if len(q.strip()) > 10]


# Singleton instance
_email_monitor = None

def get_email_monitor() -> EmailMonitorService:
    global _email_monitor
    if _email_monitor is None:
        _email_monitor = EmailMonitorService()
    return _email_monitor
