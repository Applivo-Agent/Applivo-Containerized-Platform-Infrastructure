"""
app/services/message_scanner_service.py
──────────────────────────────────────
Scans platform inboxes for new messages using Playwright browser automation.
Supports Internshala messages, with future support for LinkedIn, Indeed.
"""

from __future__ import annotations

import asyncio
import random
from datetime import datetime, timezone
from typing import Optional

import structlog
from playwright.async_api import async_playwright, Browser, BrowserContext, Page, Playwright

from app.core.config import settings
from app.services.cookie_service import cookie_service

logger = structlog.get_logger()

IMPORTANT_KEYWORDS = [
    "interview", "shortlisted", "selected", "offer",
    "assignment", "test", "assessment", "selection",
    "call", "schedule", "selection list", "result",
    "congratulations", "selection process", "group discussion",
]

PLATFORM_MESSAGE_URLS = {
    "internshala": "https://internshala.com/student/inbox",
}


class MessageScannerService:
    """Scans platform inboxes for new messages using Playwright."""

    async def scan_user_messages(self, user_id: str, platform: str = "internshala") -> dict:
        """
        Scan a user's platform inbox for new messages.
        Returns summary of new messages found.
        """
        logger.info("Starting message scan", user_id=user_id, platform=platform)
        
        cookie_data = await cookie_service.get_cookies(user_id, platform)
        if not cookie_data or not cookie_data.get("cookies"):
            logger.warning("No cookies found for user", user_id=user_id, platform=platform)
            return {
                "success": False,
                "message": "No cookies found. Please login to the platform first.",
                "new_messages": 0,
            }
        
        cookies = cookie_data["cookies"]
        messages = await self._scan_inbox(platform=platform, cookies=cookies)
        
        if not messages:
            logger.info("No messages found or scan failed")
            return {
                "success": True,
                "new_messages": 0,
                "important_messages": 0,
                "messages": [],
            }
        
        new_count = 0
        important_count = 0
        saved_messages = []
        
        for msg in messages:
            is_important, keywords = self._check_importance(msg["content"])
            
            saved_msg = await self._save_message(
                user_id=user_id,
                platform=platform,
                external_id=msg.get("id"),
                sender_name=msg.get("sender"),
                subject=msg.get("subject"),
                content=msg["content"],
                is_important=is_important,
                keywords=",".join(keywords) if keywords else None,
                received_at=msg.get("time"),
            )
            
            if saved_msg:
                new_count += 1
                if is_important:
                    important_count += 1
                    await self._send_notification(user_id, saved_msg, keywords)
                    saved_messages.append(saved_msg)
        
        logger.info("Message scan complete", user_id=user_id, new=new_count, important=important_count)
        
        return {
            "success": True,
            "new_messages": new_count,
            "important_messages": important_count,
            "messages": saved_messages,
        }

    async def _scan_inbox(self, platform: str, cookies: list) -> list:
        """Scan the platform inbox using Playwright."""
        if platform == "internshala":
            return await self._scan_internshala(cookies)
        
        logger.warning("Platform not supported", platform=platform)
        return []

    async def _scan_internshala(self, cookies: list) -> list:
        """Scan Internshala messages inbox."""
        playwright: Optional[Playwright] = None
        browser: Optional[Browser] = None
        context: Optional[BrowserContext] = None
        
        try:
            playwright = await async_playwright().start()
            
            browser = await playwright.chromium.launch(
                headless=True,
                args=[
                    "--disable-blink-features=AutomationControlled",
                    "--disable-dev-shm-usage",
                    "--disable-setuid-sandbox",
                    "--no-sandbox",
                ]
            )
            
            context = await browser.new_context(
                user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                viewport={"width": 1440, "height": 900},
                locale="en-US",
                timezone_id="Asia/Kolkata",
            )
            
            await context.add_cookies(cookies)
            
            page = await context.new_page()
            
            logger.info("Navigating to Internshala home first")
            try:
                await page.goto("https://internshala.com/", wait_until="domcontentloaded", timeout=60000)
            except Exception as e:
                logger.warning("Failed to load internshala home, trying direct chat URL")
                await page.goto("https://internshala.com/chat", wait_until="domcontentloaded", timeout=60000)
            await asyncio.sleep(3)
            
            # Check if logged in
            if "login" in page.url.lower():
                logger.warning("Session expired - redirecting to login")
                await browser.close()
                return []
            
            logger.info("Navigating to Internshala chat")
            try:
                await page.goto("https://internshala.com/chat", wait_until="domcontentloaded", timeout=60000)
            except:
                await page.goto("https://internshala.com/student/chat", wait_until="domcontentloaded", timeout=60000)
            await asyncio.sleep(3)
            
            chat_url = page.url
            logger.info("Chat URL", url=chat_url)
            
            all_links = await page.query_selector_all("a")
            logger.info("Total links on dashboard", count=len(all_links))
            
            for link in all_links[:30]:
                try:
                    href = await link.get_attribute("href")
                    text = await link.inner_text()
                    if href and ("message" in href.lower() or "inbox" in href.lower() or "chat" in href.lower()):
                        logger.info("Found message-related link", href=href, text=text[:50])
                except:
                    continue
            
            inbox_urls = [
                "https://internshala.com/chat",
                "https://internshala.com/student/chat",
                "https://internshala.com/student/inbox",
                "https://internshala.com/student/messages",
                "https://internshala.com/student/communication",
            ]
            
            for inbox_url in inbox_urls:
                logger.info("Trying inbox URL", url=inbox_url)
                try:
                    await page.goto(inbox_url, wait_until="domcontentloaded", timeout=45000)
                except Exception as e:
                    logger.warning("Failed to load URL", url=inbox_url, error=str(e))
                    continue
                await asyncio.sleep(3)
                
                if "404" not in await page.title():
                    logger.info("Valid inbox URL found", url=page.url)
                    break
            
            await page.wait_for_timeout(2000)
            
            messages = []
            
            message_items = await page.query_selector_all("a[href*='/message/detail/']")
            logger.info("Found message links with detail", count=len(message_items))
            
            if not message_items:
                message_items = await page.query_selector_all(".message, .inbox_message, .message-detail-link")
                logger.info("Found message elements", count=len(message_items))
            
            if not message_items:
                message_items = await page.query_selector_all("a[href*='/chat/']")
                logger.info("Found chat links", count=len(message_items))
            
            if not message_items:
                links = await page.query_selector_all("a")
                message_links = [l for l in links if "/message" in (await l.get_attribute("href") or "")]
                logger.info("Found any message-related links", count=len(message_links))
                for link in message_links[:5]:
                    href = await link.get_attribute("href")
                    text = await link.inner_text()
                    logger.info("Link", href=href, text=text[:50])
            
            if not message_items:
                logger.info("No messages found")
                return []
            
            last_seen_company = None
            for item in message_items[:30]:
                try:
                    item_text = await item.inner_text()
                    logger.info("Message item text preview", preview=item_text[:200])
                    
                    msg_id = await item.get_attribute("data-id") or str(hash(item_text[:50]))
                    
                    # ── Step 1: Try DOM — look for name element inside chat container ──
                    sender = None
                    try:
                        conv_info = await item.evaluate("""
                            el => {
                                let container = el.closest('[class*="conversation"], [class*="chat-item"], [class*="message"]');
                                if (!container) return null;
                                const nameEl = container.querySelector('.company_name, .text-truncate, .chat-individual-name, [data-company-name], [class*="name"], [class*="contact"], [class*="company"], h3, h4, h5, strong');
                                if (nameEl) return nameEl.textContent;
                                return null;
                            }
                        """)
                        if conv_info and conv_info.strip() and len(conv_info.strip()) > 2:
                            sender = conv_info.strip()[:100]
                    except Exception:
                        pass

                    # ── Step 2: Mark outgoing messages clearly ──────────────────────
                    if not sender and item_text.strip().startswith("You:"):
                        sender = "You (sent)"

                    # ── Step 3: Extract company name from message body ──────────────
                    if not sender and item_text:
                        import re
                        patterns = [
                            r"Opportunity from ([A-Z][A-Za-z \.\-&]{2,40})",
                            r"Application to ([A-Z][A-Za-z \.\-&]{2,40})",
                            # "internship at Mindenious Edutech"
                            r"(?:internship|role|position|opportunity) at ([A-Z][A-Za-z &\.\-]{2,40})",
                            # "from XYZ Ltd"
                            r"(?:message from|team from|on behalf of) ([A-Z][A-Za-z &\.\-]{2,40})",
                            # "We are XYZ" / "I'm from XYZ"
                            r"(?:We are|I'm from|from) ([A-Z][A-Za-z &\.\-]{2,40})",
                            # "XYZ is hiring"
                            r"([A-Z][A-Za-z &\.\-]{2,40}) (?:is hiring|would like to|wants to)",
                            # "Hi, XYZ here"
                            r"(?:Hi,|Hello,) ([A-Z][A-Za-z &\.\-]{2,40}) (?:here|team)",
                        ]
                        for pat in patterns:
                            m = re.search(pat, item_text[:800])
                            if m:
                                candidate = m.group(1).strip().rstrip(".,")
                                # Sanity: ignore generic words
                                skip = {"You", "Hi", "Hello", "We", "I", "This", "The", "Our", "Your", "Please"}
                                if candidate not in skip and len(candidate) > 3:
                                    sender = candidate
                                    break

                    # ── Step 4: Try first non-empty line if it looks like a name ────
                    if not sender and item_text:
                        import re
                        lines = [l.strip() for l in item_text.splitlines() if l.strip()]
                        if lines:
                            first_line = lines[0]
                            # If first line is short and title-case (≤ 5 words), treat as name
                            if len(first_line.split()) <= 5 and first_line[0].isupper() and not any(
                                first_line.lower().startswith(w) for w in ["you:", "hi", "hello", "final", "dear"]
                            ):
                                sender = first_line[:80]

                    final_sender = sender.strip()[:100] if sender and sender.strip() else "Internshala Chat"
                    
                    if not sender and last_seen_company and final_sender == "Internshala Chat":
                        final_sender = last_seen_company
                    elif sender and final_sender != "Internshala Chat" and "You" not in final_sender and "Internshala" not in final_sender:
                        last_seen_company = final_sender

                    final_content = item_text.strip()[:800] if item_text else "Chat message"

                    logger.info("Adding message", sender=final_sender[:40], content_preview=final_content[:50])

                    if final_content:
                        messages.append({
                            "id": msg_id,
                            "sender": final_sender,
                            "subject": self._extract_subject(final_content),
                            "content": final_content,
                            "time": None,
                        })
                except Exception as e:
                    logger.debug("Failed to parse message item", error=str(e))
                    continue
            
            logger.info("Parsed messages", count=len(messages))
            
            await browser.close()
            await playwright.stop()
            
            return messages
            
        except Exception as e:
            logger.error("Failed to scan Internshala", error=str(e))
            try:
                if browser: await browser.close()
                if playwright: await playwright.stop()
            except:
                pass
            return []

    async def _parse_internshala_messages(self, page: Page) -> list:
        """Parse messages from Internshala messages page."""
        messages = []
        
        try:
            await page.wait_for_load_state("networkidle", timeout=10000)
            
            url = page.url
            logger.info("Current URL", url=url)
            
            html = await page.content()
            
            if "login" in html.lower() and "student" not in html.lower():
                logger.warning("Not logged in - session may have expired")
                return []
            
            logger.info("Page title", title=await page.title())
            
            message_items = await page.query_selector_all("a[href*='/message/detail/']")
            logger.info("Found message links with detail", count=len(message_items))
            
            if not message_items:
                message_items = await page.query_selector_all(".message, .inbox_message, .message-detail-link")
                logger.info("Found message elements", count=len(message_items))
            
            if not message_items:
                links = await page.query_selector_all("a")
                message_links = [l for l in links if "/message" in (await l.get_attribute("href") or "")]
                logger.info("Found any message-related links", count=len(message_links))
                for link in message_links[:5]:
                    href = await link.get_attribute("href")
                    text = await link.inner_text()
                    logger.info("Link", href=href, text=text[:50])
            
            if not message_items:
                logger.info("No messages found")
                return []
            
            for item in message_items[:30]:
                try:
                    item_text = await item.inner_text()
                    logger.info("Message item text preview", preview=item_text[:200])
                    
                    msg_id = await item.get_attribute("data-id") or str(hash(item_text[:50]))
                    
                    sender_el = await item.query_selector(
                        ".company_name, .text-truncate, .chat-individual-name, [data-company-name], "
                        ".sender-name, .message-sender, .company-name, h3, h4, h5, "
                        ".name, .user-name, [class*='sender'], [class*='company']"
                    )
                    sender = await sender_el.inner_text() if sender_el else "Unknown"
                    
                    subject_el = await item.query_selector(
                        ".subject, .message-subject, .message-title, .title, "
                        "[class*='subject'], [class*='title']"
                    )
                    subject = await subject_el.inner_text() if subject_el else ""
                    
                    content_el = await item.query_selector(
                        ".message-body, .message-content, .message-text, p, "
                        ".description, .preview, [class*='content']"
                    )
                    content = await content_el.inner_text() if content_el else subject
                    
                    time_el = await item.query_selector(
                        ".time, .message-time, .timestamp, .date, [class*='time']"
                    )
                    time_str = await time_el.inner_text() if time_el else None
                    received_at = self._parse_time(time_str)
                    
                    if sender != "Unknown" or subject or content:
                        messages.append({
                            "id": msg_id,
                            "sender": sender.strip()[:100] if sender else "Unknown",
                            "subject": subject.strip()[:200] if subject else "",
                            "content": content.strip()[:500] if content else subject.strip()[:500],
                            "time": received_at,
                        })
                except Exception as e:
                    logger.debug("Failed to parse message item", error=str(e))
                    continue
                    
        except Exception as e:
            logger.error("Failed to parse Internshala messages", error=str(e))
        
        return messages

    def _extract_subject(self, content: str) -> str:
        """Generate a meaningful subject line from message content."""
        import re
        c = content.lower()

        # Priority order: most specific first
        if any(w in c for w in ["interview", "interview scheduled", "interview invite"]):
            return "Interview Invitation"
        if any(w in c for w in ["shortlisted", "selected for", "we are interested in your profile"]):
            return "Shortlisted for Internship"
        if any(w in c for w in ["assessment", "assignment", "test link", "assessment window"]):
            return "Assessment / Assignment"
        if any(w in c for w in ["offer letter", "offer accepted", "offer extended"]):
            return "Offer Letter"
        if any(w in c for w in ["fill out", "google form", "kindly fill", "form link"]):
            return "Form / Registration Request"
        if any(w in c for w in ["reminder", "expires", "deadline", "last chance"]):
            return "Reminder"
        if any(w in c for w in ["congratulations", "congrats"]):
            return "Congratulations!"
        if any(w in c for w in ["we came across your profile", "came across your profile"]):
            return "Recruiter Outreach"
        if any(w in c for w in ["group discussion", "gd round"]):
            return "Group Discussion"
        if content.strip().startswith("You:"):
            return "Sent by you"
        if "attachment" in c:
            return "Attachment"
        # Fallback: first 60 chars of message
        first_line = content.strip().splitlines()[0][:60].strip() if content.strip() else "Chat message"
        return first_line or "Chat message"

    def _parse_time(self, time_str: Optional[str]) -> Optional[datetime]:
        """Parse time string to datetime."""
        if not time_str:
            return None
        
        try:
            from dateutil import parser
            return parser.parse(time_str)
        except:
            return datetime.now(timezone.utc)

    def _check_importance(self, content: str) -> tuple[bool, list]:
        """Check if message contains important keywords."""
        content_lower = content.lower()
        found_keywords = [kw for kw in IMPORTANT_KEYWORDS if kw in content_lower]
        return len(found_keywords) > 0, found_keywords

    async def _save_message(self, user_id: str, platform: str, external_id: Optional[str],
                           sender_name: Optional[str], subject: Optional[str], content: str,
                           is_important: bool, keywords: Optional[str],
                           received_at: Optional[datetime]) -> Optional[dict]:
        """Save message to database."""
        from app.models.platform_message import PlatformMessage
        from app.core.database import get_db_context
        
        async with get_db_context() as db:
            if external_id:
                from sqlalchemy import select
                result = await db.execute(
                    select(PlatformMessage).where(
                        PlatformMessage.user_id == user_id,
                        PlatformMessage.platform == platform,
                        PlatformMessage.external_id == external_id,
                    )
                )
                existing = result.scalar_one_or_none()
                if existing:
                    return None
            
            msg = PlatformMessage(
                user_id=user_id,
                platform=platform,
                external_id=external_id,
                sender_name=sender_name,
                subject=subject,
                content=content[:2000],
                is_important=is_important,
                importance_keywords=keywords,
                status="unread",
                received_at=received_at or datetime.now(timezone.utc),
            )
            db.add(msg)
            await db.commit()
            await db.refresh(msg)
            
            return {
                "id": msg.id,
                "sender": sender_name,
                "subject": subject,
                "is_important": is_important,
            }

    async def _send_notification(self, user_id: str, message: dict, keywords: list):
        """Send notification for important message."""
        from app.services.notification_service import NotificationService
        
        notification_service = NotificationService()
        
        await notification_service.notify(
            user_id=user_id,
            title=f"Important message: {message.get('sender', 'Unknown')}",
            body=f"Subject: {message.get('subject', 'No subject')}\n\nKeywords: {', '.join(keywords)}",
            event_type="platform_message",
        )


message_scanner_service = MessageScannerService()