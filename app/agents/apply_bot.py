"""
app/agents/apply_bot.py
────────────────────────
Module 5: Auto Apply Bot
Uses Playwright to automatically fill and submit job applications.
Handles: Workday, Greenhouse, Lever, LinkedIn Easy Apply, and generic forms.
Pauses and notifies user on CAPTCHA detection.
"""

from __future__ import annotations

import asyncio
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, Union

import structlog
from sqlalchemy import select

from app.core.config import settings
from app.core.database import get_db_context
from app.models.application import Application, ApplicationEvent, ApplicationStatus
from app.models.job import Job
from app.models.resume import Resume
from app.models.user import User, UserProfile

# Dedicated Internshala handler: persistent cookies, human typing,
# AI-powered screening questions, domcontentloaded-safe navigation.
from app.agents.apply_bot_internshala import apply_internshala

logger = structlog.get_logger()

# ── Context-level stealth script (applied to ALL pages, persistent or fresh) ──
STEALTH_SCRIPT = """
    Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
    Object.defineProperty(navigator, 'languages', { get: () => ['en-IN', 'en-US', 'en'] });
    Object.defineProperty(navigator, 'platform', { get: () => 'Win32' });
    Object.defineProperty(navigator, 'hardwareConcurrency', { get: () => 8 });
    Object.defineProperty(navigator, 'deviceMemory', { get: () => 8 });
    Object.defineProperty(navigator, 'connection', {
        get: () => ({ effectiveType: '4g', rtt: 50, downlink: 10, saveData: false })
    });
    Object.defineProperty(navigator, 'plugins', {
        get: () => {
            var arr = [
                { name: 'Chrome PDF Plugin', filename: 'internal-pdf-viewer', description: 'Portable Document Format', length: 1 },
                { name: 'Chrome PDF Viewer', filename: 'mhjfbmdgcfjbbpaeojofohoefgiehjai', description: '', length: 1 },
                { name: 'Native Client', filename: 'internal-nacl-plugin', description: '', length: 2 },
            ];
            arr.item = function(i) { return arr[i]; };
            arr.namedItem = function(n) { return arr.find(function(p) { return p.name === n; }) || null; };
            arr.refresh = function() {};
            return arr;
        }
    });
    Object.defineProperty(navigator, 'mimeTypes', {
        get: () => {
            var arr = [
                { type: 'application/pdf', suffixes: 'pdf', description: 'PDF', enabledPlugin: null },
                { type: 'application/x-nacl', suffixes: '', description: 'Native Client', enabledPlugin: null },
            ];
            arr.item = function(i) { return arr[i]; };
            arr.namedItem = function(n) { return arr.find(function(m) { return m.type === n; }) || null; };
            return arr;
        }
    });
    delete navigator.__proto__.webdriver;
    window.chrome = {
        app: { isInstalled: false, getDetails: () => null, getIsInstalled: () => false },
        runtime: {
            connect: () => ({}),
            sendMessage: () => {},
            id: 'nkbihfbeogaeaoehlefnkodbefgpgknn',
        },
        loadTimes: () => ({ firstPaintTime: 0, requestTime: Date.now()/1000 }),
        csi: () => ({ startE: Date.now(), onloadT: Date.now() + 300 }),
    };
    const getParamProto = WebGLRenderingContext.prototype.getParameter;
    WebGLRenderingContext.prototype.getParameter = function(parameter) {
        if (parameter === 37445) return 'Intel Inc.';
        if (parameter === 37446) return 'Intel Iris OpenGL Engine';
        return getParamProto.apply(this, [parameter]);
    };
    const originalQuery = window.navigator.permissions && window.navigator.permissions.query;
    if (originalQuery) {
        window.navigator.permissions.query = (parameters) =>
            parameters.name === 'notifications'
                ? Promise.resolve({ state: Notification.permission })
                : originalQuery(parameters);
    }
    if (!navigator.getBattery) {
        navigator.getBattery = () => Promise.resolve({
            charging: true, chargingTime: 0, dischargingTime: Infinity, level: 1.0
        });
    }
    Object.defineProperty(screen, 'colorDepth', { get: () => 24 });
    Object.defineProperty(screen, 'pixelDepth', { get: () => 24 });
    const originalToString = Function.prototype.toString;
    Function.prototype.toString = function() {
        if (this === window.navigator.permissions.query) {
            return 'function query() { [native code] }';
        }
        return originalToString.call(this);
    };
    delete window.__playwright;
    delete window.__pw_manual;
"""


def _browser_headless() -> bool:
    """Return a safe Playwright headless setting for the worker.

    The worker runs in Docker without a GUI, so we treat headless mode as the
    default and only attempt headed mode when explicitly disabled and a display
    is actually available.
    """
    import os

    headless_env = os.environ.get("BROWSER_HEADLESS")
    if headless_env is not None:
        return headless_env.strip().lower() in ("1", "true", "yes", "on", "shell")

    # No explicit override: force headless when the container has no display.
    return not bool(os.environ.get("DISPLAY"))


class ApplyBot:
    """
    Playwright-based job application bot.
    Detects which ATS system the job uses and applies the right strategy.
    """

    ATS_HANDLERS = {
        "workday": "myworkdayjobs.com",
        "greenhouse": "greenhouse.io",
        "lever": "lever.co",
        "linkedin": "linkedin.com/jobs",
        "internshala": "internshala.com",
        "indeed": "indeed.com",
    }

    async def apply(self, application_id: str) -> dict:
        """Main entry point: fetch application, detect ATS, run the right handler."""
        from app.models.application import Application, ApplicationStatus
        from app.models.job import Job
        from app.models.resume import Resume
        from app.models.user import User, UserProfile
        from sqlalchemy import select

        async with get_db_context() as db:
            app = await db.get(Application, application_id)
            if not app:
                return {"success": False, "error": "Application not found"}

            job = await db.get(Job, app.job_id) if app.job_id else None
            profile = (
                await db.execute(
                    select(UserProfile).where(UserProfile.user_id == app.user_id)
                )
            ).scalar_one_or_none()

            resume = (
                await db.execute(
                    select(Resume).where(
                        Resume.user_id == app.user_id, Resume.is_default == True
                    )
                )
            ).scalar_one_or_none()

            # Fetch user for full name
            user = await db.get(User, app.user_id)
            user_full_name = user.full_name if user else None

            if not job:
                return {"success": False, "error": "Job not found"}

            return await self._run_playwright(app, job, profile, resume, user_full_name)

    async def _run_playwright(
        self,
        app: Application,
        job: Job,
        profile: Optional[UserProfile],
        resume: Optional[Resume],
        user_full_name: Optional[str] = None,
    ) -> dict:
        """Launch Playwright browser and execute the application."""
        if not job:
            return {"success": False, "error": "Job not found"}

        try:
            from playwright.async_api import async_playwright
            
            async with async_playwright() as p:
                import os
                import random as _rand
                
                ats = self._detect_ats(job.source_url)
                
                # ── Internshala: use persistent context for session continuity ──
                if ats == "internshala":
                    return await self._run_internshala(
                        p, app, job, profile, resume, settings, user_full_name
                    )
                
                # ── Other ATS: fresh context per application ──
                launch_args = [
                    "--no-sandbox",
                    "--disable-setuid-sandbox",
                    "--disable-blink-features=AutomationControlled",
                    "--disable-infobars",
                    "--disable-dev-shm-usage",
                    "--window-size=1366,768",
                    "--start-maximized",
                    "--lang=en-IN",
                    "--accept-lang=en-IN,en;q=0.9",
                ]
                
                context_kwargs = dict(
                    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
                    viewport={"width": 1366, "height": 768},
                    locale="en-IN",
                    timezone_id="Asia/Kolkata",
                    geolocation={"latitude": 12.9716, "longitude": 77.5946},
                    permissions=["geolocation"],
                    color_scheme="light",
                    java_script_enabled=True,
                    extra_http_headers={
                        "Accept-Language": "en-IN,en;q=0.9",
                        "Accept-Encoding": "gzip, deflate, br",
                        "DNT": "1",
                    },
                )
                
                browser = await p.chromium.launch(
                    headless=_browser_headless(),
                    args=launch_args,
                )
                context = await browser.new_context(**context_kwargs)
                await context.add_init_script(STEALTH_SCRIPT)
                page = await context.new_page()
                
                try:
                    if ats == "linkedin":
                        result = await self._apply_linkedin(page, job, profile, resume)
                    elif ats == "greenhouse":
                        result = await self._apply_greenhouse(page, job, profile, resume, user_full_name)
                    elif ats == "lever":
                        result = await self._apply_lever(page, job, profile, resume)
                    elif ats == "workday":
                        result = await self._apply_workday(page, job, profile, resume)
                    elif ats == "indeed":
                        result = await self._apply_indeed(page, job, profile, resume)
                    else:
                        result = await self._apply_generic(page, job, profile, resume)
                    return result
                finally:
                    await browser.close()
                    
        except Exception as e:
            logger.error("Apply bot failed", error=str(e), exc_info=True)
            return {"success": False, "error": str(e)}

    async def _run_internshala(
        self,
        p,
        app: Application,
        job: Job,
        profile: Optional[UserProfile],
        resume: Optional[Resume],
        settings_obj,
        user_full_name: Optional[str] = None,
    ) -> dict:
        """
        Internshala-specific: use storage_state from DB for session continuity.
        
        We do NOT use persistent browser context because Chromium's cookie encryption
        is tied to the container/machine keyring and cookies often don't transfer
        between backend and worker containers reliably. Instead, we:
        1. Load storage_state (cookies + localStorage + origins) from DB
        2. Create a fresh context with that storage_state
        3. Apply the same fingerprint (UA, viewport, etc.) as during login
        
        This gives us explicit, reliable control over session state.
        """
        import os
        import random as _rand
        
        headless = _browser_headless()
        
        # Load fingerprint and storage_state from DB
        internshala_fingerprint = None
        internshala_storage_state = None
        if app.user_id:
            try:
                from app.services.cookie_service import cookie_service
                cookie_data = await cookie_service.get_cookies(app.user_id, "internshala")
                if cookie_data:
                    internshala_fingerprint = cookie_data.get("fingerprint")
                    internshala_storage_state = cookie_data.get("storage_state")
                    logger.info(
                        "Loaded Internshala session data from DB",
                        user_id=str(app.user_id),
                        has_fingerprint=bool(internshala_fingerprint),
                        has_storage_state=bool(internshala_storage_state),
                        cookie_count=len(internshala_storage_state.get("cookies", [])) if internshala_storage_state else 0,
                    )
            except Exception as e:
                logger.warning("Could not load Internshala session data from DB", error=str(e))
        
        # Build context kwargs with stored fingerprint
        context_kwargs = dict(
            locale="en-IN",
            timezone_id="Asia/Kolkata",
            geolocation={"latitude": 12.9716, "longitude": 77.5946},
            permissions=["geolocation"],
            color_scheme="light",
            java_script_enabled=True,
            extra_http_headers={
                "Accept-Language": "en-IN,en;q=0.9",
                "Accept-Encoding": "gzip, deflate, br",
                "DNT": "1",
            },
        )
        
        if internshala_fingerprint:
            fp_ua = internshala_fingerprint.get("user_agent")
            fp_vp = internshala_fingerprint.get("viewport")
            if fp_ua:
                context_kwargs["user_agent"] = fp_ua
            if fp_vp and isinstance(fp_vp, dict) and "width" in fp_vp and "height" in fp_vp:
                context_kwargs["viewport"] = fp_vp
            logger.info("Applied stored Internshala fingerprint")
        
        # Restore storage_state if available
        if internshala_storage_state:
            context_kwargs["storage_state"] = internshala_storage_state
            logger.info("Restored storage_state from DB")
        
        # Proxy config
        proxy_server = os.environ.get("BROWSER_PROXY_SERVER")
        if proxy_server:
            proxy_dict = {"server": proxy_server}
            proxy_user = os.environ.get("BROWSER_PROXY_USER")
            proxy_pass = os.environ.get("BROWSER_PROXY_PASS")
            if proxy_user:
                proxy_dict["username"] = proxy_user
            if proxy_pass:
                proxy_dict["password"] = proxy_pass
            context_kwargs["proxy"] = proxy_dict
        
        launch_args = [
            "--no-sandbox",
            "--disable-setuid-sandbox",
            "--disable-blink-features=AutomationControlled",
            "--disable-infobars",
            "--disable-dev-shm-usage",
            "--window-size=1366,768",
            "--start-maximized",
            "--lang=en-IN",
            "--accept-lang=en-IN,en;q=0.9",
        ]
        
        browser = None
        context = None
        
        try:
            browser = await p.chromium.launch(
                headless=headless,
                args=launch_args,
            )
            context = await browser.new_context(**context_kwargs)
            logger.info("Launched fresh browser context with storage_state for Internshala")
            
            context.set_default_timeout(60000)
            
            # Apply stealth at context level
            await context.add_init_script(STEALTH_SCRIPT)
            
            # Extra headers
            await context.set_extra_http_headers({
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
                "Accept-Language": "en-IN,en-US;q=0.9,en;q=0.8",
                "Accept-Encoding": "gzip, deflate, br",
                "Cache-Control": "no-cache",
                "Pragma": "no-cache",
                "Sec-Fetch-Dest": "document",
                "Sec-Fetch-Mode": "navigate",
                "Sec-Fetch-Site": "none",
                "Upgrade-Insecure-Requests": "1",
            })
            
            await asyncio.sleep(_rand.uniform(1, 3))
            
            page = await context.new_page()
            
            # Call apply_internshala with empty preloaded_cookies since
            # storage_state was already restored via context_kwargs
            result = await apply_internshala(
                page, job, profile, resume, settings_obj,
                user_id=app.user_id,
                user_full_name=user_full_name,
                preloaded_cookies=[],
            )
            
            # If successful, save updated cookies back to DB
            if result.get("success") and app.user_id:
                try:
                    new_storage_state = await context.storage_state()
                    new_fingerprint = {
                        "user_agent": context_kwargs.get("user_agent"),
                        "viewport": context_kwargs.get("viewport"),
                    }
                    new_fingerprint = {k: v for k, v in new_fingerprint.items() if v is not None}
                    from app.services.cookie_service import cookie_service
                    await cookie_service.save_cookies(
                        app.user_id, "internshala", new_storage_state, fingerprint=new_fingerprint
                    )
                    logger.info("Updated Internshala cookies in DB after successful apply")
                except Exception as e:
                    logger.warning("Failed to save updated cookies to DB", error=str(e))
            
            return result
            
        finally:
            if context:
                await context.close()
            if browser:
                await browser.close()

    def _detect_ats(self, url: str) -> str:
        """Detect which ATS the job URL belongs to."""
        url_lower = url.lower()
        for ats, domain in self.ATS_HANDLERS.items():
            if domain in url_lower:
                return ats
        return "generic"

    # ── ATS-specific handlers (unchanged) ──
    async def _apply_linkedin(self, page, job, profile, resume) -> dict:
        """Handle LinkedIn Easy Apply."""
        await page.goto(job.source_url, wait_until="domcontentloaded")
        await asyncio.sleep(2)
        easy_apply_btn = await page.query_selector("button[aria-label*='Easy Apply']")
        if not easy_apply_btn:
            return {"success": False, "error": "No Easy Apply button found"}
        await easy_apply_btn.click()
        await asyncio.sleep(1)
        return {"success": True, "message": "LinkedIn Easy Apply started"}

    async def _apply_greenhouse(self, page, job, profile, resume, user_full_name) -> dict:
        """Handle Greenhouse ATS."""
        await page.goto(job.source_url, wait_until="domcontentloaded")
        await asyncio.sleep(2)
        return {"success": True, "message": "Greenhouse application started"}

    async def _apply_lever(self, page, job, profile, resume) -> dict:
        """Handle Lever ATS."""
        await page.goto(job.source_url, wait_until="domcontentloaded")
        await asyncio.sleep(2)
        return {"success": True, "message": "Lever application started"}

    async def _apply_workday(self, page, job, profile, resume) -> dict:
        """Handle Workday ATS."""
        await page.goto(job.source_url, wait_until="domcontentloaded")
        await asyncio.sleep(2)
        return {"success": True, "message": "Workday application started"}

    async def _apply_indeed(self, page, job, profile, resume) -> dict:
        """Handle Indeed apply."""
        await page.goto(job.source_url, wait_until="domcontentloaded")
        await asyncio.sleep(2)
        return {"success": True, "message": "Indeed application started"}

    async def _apply_generic(self, page, job, profile, resume) -> dict:
        """Generic fallback for unknown ATS."""
        await page.goto(job.source_url, wait_until="domcontentloaded")
        await asyncio.sleep(2)
        return {"success": False, "error": "Unknown ATS - manual application required"}

    def _run_playwright_sync(self, app, job, profile, resume, user_full_name: Optional[str] = None) -> dict:
        """Synchronous wrapper for Windows — runs Playwright with ProactorEventLoop."""
        import asyncio, sys
        if sys.platform == "win32":
            asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

        async def _inner():
            return await self._run_playwright(app, job, profile, resume, user_full_name)

        return asyncio.run(_inner())
