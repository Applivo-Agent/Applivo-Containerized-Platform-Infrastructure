"""
app/services/internshala_login_service.py
───────────────────────────────────────
Handles Internshala login via Playwright - user manually logs in, we capture cookies.
"""

from __future__ import annotations

import asyncio
import random
from typing import Optional

import structlog
from playwright.async_api import async_playwright, Browser, BrowserContext, Page, Playwright

from app.core.config import settings as _path_settings
from app.services.cookie_service import cookie_service

logger = structlog.get_logger()


class InternshalaLoginService:
    """Service to log into Internshala and capture session cookies."""

    async def login_and_save_cookies(
        self,
        user_id: str,
        email: str = "",
        password: str = "",
    ) -> dict:
        """
        Open browser and let user manually log in, then capture cookies.
        """
        logger.info("Starting Internshala login - user will manually login")
        
        cookies = await self._perform_user_assisted_login()
        
        if not cookies:
            return {
                "success": False,
                "message": "Login failed - no cookies obtained. Please try again.",
                "needs_captcha": False,
            }
        
        await cookie_service.save_cookies(
            user_id=user_id,
            platform="internshala",
            cookies=cookies,
        )
        
        return {
            "success": True,
            "message": "Successfully logged in and saved cookies",
            "cookies_count": len(cookies),
            "needs_captcha": False,
        }

    async def _perform_user_assisted_login(self) -> Optional[list]:
        """
        Open browser to Internshala, let user manually login, then capture cookies.
        """
        playwright: Optional[Playwright] = None
        browser: Optional[Browser] = None
        context: Optional[BrowserContext] = None
        
        try:
            logger.info("Starting Playwright - opening browser for manual login")
            playwright = await async_playwright().start()
            
            # More stealth browser settings
            browser = await playwright.chromium.launch(
                headless=False,
                args=[
                    "--disable-blink-features=AutomationControlled",
                    "--disable-dev-shm-usage",
                    "--disable-setuid-sandbox",
                    "--no-sandbox",
                    "--disable-web-security",
                    "--disable-features=IsolateOrigins,site-per-process",
                ]
            )
            
            # Create context with more realistic settings
            context = await browser.new_context(
                user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                viewport={"width": 1440, "height": 900},
                locale="en-US",
                timezone_id="Asia/Kolkata",
                permissions=["geolocation"],
            )
            
            # Add extra headers to look more like real browser
            await context.set_extra_http_headers({
                "Accept-Language": "en-US,en;q=0.9",
            })
            
            page = await context.new_page()
            
            # Enable console logging from browser
            page.on("console", lambda msg: logger.info(f"Browser: {msg.text}"))
            
            logger.info("Navigating to Internshala")
            await page.goto("https://internshala.com/login", wait_until="domcontentloaded", timeout=60000)
            
            # Add random delay to appear more natural
            await asyncio.sleep(random.uniform(1, 3))
            
            logger.info("Browser opened - waiting for user to manually login")
            
            # Wait for user to login - check for various login success indicators
            login_success = await self._wait_for_login(page, timeout=300)
            
            if not login_success:
                logger.error("Login timeout - user did not complete login")
                return None
            
            await asyncio.sleep(2)
            
            # Verify we're logged in
            is_logged_in = await self._verify_login(page)
            if not is_logged_in:
                logger.error("Login verification failed")
                return None
            
            logger.info("Login successful, extracting cookies")
            cookies = await context.cookies()
            logger.info("Got cookies", count=len(cookies))
            
            await browser.close()
            await playwright.stop()
            
            return cookies
            
        except Exception as e:
            logger.error("Login failed with exception", error=str(e), error_type=type(e).__name__)
            try:
                if browser:
                    await browser.close()
                if playwright:
                    await playwright.stop()
            except:
                pass
            return None

    async def _wait_for_login(self, page: Page, timeout: int = 300) -> bool:
        """
        Wait for user to manually complete login.
        Returns True when login is detected.
        """
        logger.info("Waiting for manual login", timeout=timeout)
        
        login_indicators = [
            "a[href*='/student/dashboard']",
            "a[href*='/student/profile']",
            ".profile-header",
            ".student-profile-pic",
            "a:has-text('Logout')",
            "a:has-text('Sign Out')",
            "#header-profile-img",
            ".user-profile",
        ]
        
        for i in range(timeout):
            await asyncio.sleep(1)
            
            # Check URL - if redirected to student section, likely logged in
            url = page.url
            if "/student/" in url and "/login" not in url:
                logger.info("Detected login via URL")
                return True
            
            # Check for logout link - clear indicator of logged in state
            try:
                logout_btn = await page.query_selector("a:has-text('Logout'), a:has-text('Sign Out')")
                if logout_btn:
                    logger.info("Detected login via logout button")
                    return True
            except:
                pass
            
            # Check for profile elements
            for selector in login_indicators:
                try:
                    el = await page.query_selector(selector)
                    if el:
                        logger.info("Detected login via element", selector=selector)
                        return True
                except:
                    continue
            
            # Check page content
            try:
                content = await page.content()
                if "logout" in content.lower() and "/student/" in content:
                    logger.info("Detected login via page content")
                    return True
            except:
                pass
            
            if i % 30 == 0 and i > 0:
                logger.info("Still waiting for login...", seconds_remaining=timeout-i)
        
        return False

    async def _verify_login(self, page: Page) -> bool:
        """Verify if login was successful."""
        try:
            await page.wait_for_load_state("networkidle", timeout=5000)
        except:
            pass
        
        url = page.url
        if "login" in url.lower() and "student" not in url:
            return False
        
        indicators = [
            ".profile-header",
            "#header-profile-img",
            "a[href*='/student/dashboard']",
            "a[href*='/student/profile']",
            ".student-profile-pic",
            ".user-profile",
            "a:has-text('Logout')",
            "a:has-text('Sign Out')",
        ]
        
        for selector in indicators:
            try:
                el = await page.query_selector(selector)
                if el and await el.is_visible():
                    return True
            except:
                continue
        
        content = await page.content()
        if "logout" in content.lower() or "/student/" in content:
            return True
        
        return False

    async def refresh_cookies(self, user_id: str) -> dict:
        """Attempt to refresh cookies."""
        return {
            "success": False,
            "message": "Please login again manually",
        }


internshala_login_service = InternshalaLoginService()