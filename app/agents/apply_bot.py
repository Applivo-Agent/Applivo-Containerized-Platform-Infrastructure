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


def _browser_headless() -> Union[bool, str]:
    """Return a safe Playwright headless setting for the worker.

    Defaults to 'shell' (new Chromium headless mode) which is much less detectable
    than legacy headless=True. Use BROWSER_HEADLESS=1 for legacy mode or
    BROWSER_HEADLESS=0 for headed mode (requires a display).
    """
    import os

    headless_env = os.environ.get("BROWSER_HEADLESS")
    if headless_env is not None:
        val = headless_env.strip().lower()
        if val in ("0", "false", "no", "off"):
            return False
        if val == "shell":
            return "shell"
        return True

    # Default to new headless shell mode for better stealth.
    return "shell"


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
        "wellfound": "wellfound.com",
    }

    async def apply(self, application_id: str) -> dict:
        """Main entry point — apply to a single job application."""
        async with get_db_context() as db:
            # Load application
            app = (await db.execute(
                select(Application).where(Application.id == application_id)
            )).scalar_one_or_none()
            if not app:
                raise ValueError(f"Application {application_id} not found")

            job = (await db.execute(
                select(Job).where(Job.id == app.job_id)
            )).scalar_one_or_none()

            # Check if this job has already been successfully applied to
            existing_applied = (await db.execute(
                select(Application).where(
                    Application.job_id == app.job_id,
                    Application.user_id == app.user_id,
                    Application.status == ApplicationStatus.APPLIED,
                    Application.id != application_id,
                )
            )).scalar_one_or_none()
            
            if existing_applied:
                logger.info(f"Job already applied via another application {existing_applied.id[:8]}")
                app.status = ApplicationStatus.FAILED
                app.bot_error = "Duplicate - already applied"
                db.add(ApplicationEvent(
                    application_id=application_id,
                    event_type="duplicate_detected",
                    from_status=ApplicationStatus.QUEUED,
                    to_status=ApplicationStatus.FAILED,
                    triggered_by="agent",
                    details={"existing_application_id": existing_applied.id},
                ))
                await db.commit()
                return {"success": True, "already_applied": True, "duplicate": True}

            profile = (await db.execute(
                select(UserProfile).where(UserProfile.user_id == app.user_id)
            )).scalar_one_or_none()

            user_full_name = None
            if profile:
                user = (await db.execute(
                    select(User).where(User.id == app.user_id)
                )).scalar_one_or_none()
                if user:
                    user_full_name = user.full_name

            resume = None
            if app.resume_id:
                resume = (await db.execute(
                    select(Resume).where(Resume.id == app.resume_id)
                )).scalar_one_or_none()
            else:
                # Try to find a default resume
                default_resume = (await db.execute(
                    select(Resume).where(
                        Resume.user_id == app.user_id,
                        Resume.is_default == True
                    )
                )).scalar_one_or_none()
                if default_resume:
                    resume = default_resume
                    app.resume_id = resume.id
                else:
                    # LAST RESORT: Find ANY resume and use it
                    any_resume = (await db.execute(
                        select(Resume).where(Resume.user_id == app.user_id)
                    )).scalars().first()
                    if any_resume:
                        resume = any_resume
                        any_resume.is_default = True
                        app.resume_id = resume.id
                        await db.commit()
                        logger.info(f"Set resume {resume.id} as default for application")
                    else:
                        # Try to generate a PDF from profile if no resume exists
                        logger.warning(f"No resume found for user {app.user_id} - attempting to generate one")
                        try:
                            from app.services.resume_service import ResumeService
                            resume_service = ResumeService()
                            # Try to generate for first available job
                            jobs_result = await db.execute(
                                select(Job).where(Job.is_active == True).limit(1)
                            )
                            resume_gen_job = jobs_result.scalar_one_or_none()
                            if resume_gen_job:
                                result = await resume_service.generate_tailored(app.user_id, resume_gen_job.id)
                                # Load the generated resume
                                resume = (await db.execute(
                                    select(Resume).where(Resume.id == result['resume_id'])
                                )).scalar_one_or_none()
                                if resume:
                                    app.resume_id = resume.id
                                    await db.commit()
                                    logger.info(f"Generated resume {resume.id} for application")
                        except Exception as e:
                            logger.error(f"Failed to generate resume: {e}")
                    
                    if not resume:
                        logger.warning(f"No resume found for application {app.id} - application will proceed without resume")

            # Generate cover letter only when explicitly enabled.
            cover_letter_content = ""
            if settings.USE_COVER_LETTER and job:
                try:
                    from app.services.cover_letter_service import CoverLetterService

                    logger.info(f"Generating cover letter for job {job.id}")
                    cover_letter_service = CoverLetterService()
                    result = await cover_letter_service.generate(app.user_id, job.id)
                    cover_letter_content = result.get("content", "") or ""
                except Exception as e:
                    logger.warning(f"Could not generate cover letter: {e}")
                    cover_letter_content = ""
            else:
                logger.info("Cover letter generation disabled; proceeding without one")

            # Update status to applying
            app.status = ApplicationStatus.APPLYING
            db.add(ApplicationEvent(
                application_id=app.id,
                event_type="bot_started",
                from_status=ApplicationStatus.QUEUED,
                to_status=ApplicationStatus.APPLYING,
                triggered_by="agent",
            ))
            await db.commit()

            # Run the bot
            import sys
            if sys.platform == "win32":
                result = self._run_playwright_sync(app, job, profile, resume, user_full_name)
            else:
                result = await self._run_playwright(app, job, profile, resume, user_full_name)

            # Update final status
            # Reclean app object to ensure it's still attached (though it should be)
            await db.refresh(app)
            app_record = app

            # ── Resolve company name ──────────────────────────────────
            # Priority: URL slug > DB snapshot > job.company_name
            import re as _re
            company = ""
            if job and job.source_url:
                m = _re.search(r"-at-([a-z0-9][a-z0-9-]+?)(\d{7,})", job.source_url)
                if m:
                    company = m.group(1).replace("-", " ").title()
            if not company or company.lower() in ("unknown", "company", ""):
                company = (
                    (app_record.company_snapshot or "").strip()
                    or (job.company_name if job else "").strip()
                    or "Company"
                )

            role = (
                (app_record.job_title_snapshot or "").strip()
                or (job.title if job else "").strip()
                or "Role"
            )

            if result["success"]:
                app_record.status = ApplicationStatus.APPLIED
                app_record.applied_at = datetime.now(timezone.utc)

                already_applied = result.get("already_applied", False)

                db.add(ApplicationEvent(
                    application_id=application_id,
                    event_type="already_applied_detected" if already_applied else "application_submitted",
                    from_status=ApplicationStatus.APPLYING,
                    to_status=ApplicationStatus.APPLIED,
                    triggered_by="agent",
                    details=result,
                ))

                if already_applied:
                    logger.info("Already applied — syncing DB status only", app_id=application_id, job=job.title if job else "?")
                else:
                    logger.info("Application submitted", app_id=application_id, job=job.title if job else "?")

                    if app_record.resume_id:
                        resume_record = (await db.execute(
                            select(Resume).where(Resume.id == app_record.resume_id)
                        )).scalar_one_or_none()
                        if resume_record:
                            resume_record.times_used += 1

                    # Send rich success notification
                    from app.services.notification_service import NotificationService
                    lines = []
                    lines.append(f"Company: {company}")
                    lines.append(f"Role: {role}")

                    if job:
                        work_mode_str = ""
                        if job.work_mode:
                            wm = job.work_mode
                            work_mode_str = wm.value if hasattr(wm, "value") else str(wm)
                            if work_mode_str and work_mode_str != "unknown":
                                lines.append(f"Mode: {work_mode_str.title()}")

                        if job.job_type:
                            jt = job.job_type
                            jt_str = jt.value if hasattr(jt, "value") else str(jt)
                            if jt_str:
                                lines.append(f"Type: {jt_str.replace('_', ' ').title()}")

                    # AI analysis fields (Use the same session 'db')
                    try:
                        from app.models.job import JobAnalysis
                        analysis = (await db.execute(
                            select(JobAnalysis).where(JobAnalysis.job_id == job.id)
                        )).scalar_one_or_none() if job else None

                        if analysis:
                            if analysis.ai_recommendation:
                                rec = analysis.ai_recommendation.strip()
                                sentences = rec.split(". ")
                                short_rec = ". ".join(sentences[:2])
                                lines.append(f"\nAI: {short_rec}")
                            if analysis.missing_skills:
                                missing = ", ".join(analysis.missing_skills[:4])
                                lines.append(f"Gap skills: {missing}")
                    except Exception:
                        pass

                    if job and job.source_url:
                        lines.append(f"\n🔗 {job.source_url}")

                    await NotificationService().notify(
                        title=f"🎉 Application Sent - {role} at {company}",
                        body="✅ " + "\n".join(lines),
                        event_type="application_submitted",
                        user_id=app_record.user_id,
                    )

            elif result.get("captcha"):
                app_record.status = ApplicationStatus.QUEUED
                app_record.bot_error = "CAPTCHA detected — manual intervention required"
                db.add(ApplicationEvent(
                    application_id=application_id,
                    event_type="captcha_detected",
                    triggered_by="agent",
                    details=result,
                ))
            elif result.get("ineligible"):
                app_record.status = ApplicationStatus.SKIPPED
                app_record.bot_error = result.get("error", "Not eligible")
                db.add(ApplicationEvent(
                    application_id=application_id,
                    event_type="ineligible",
                    from_status=ApplicationStatus.APPLYING,
                    to_status=ApplicationStatus.SKIPPED,
                    triggered_by="agent",
                    details={"reason": result.get("error")},
                ))
            elif result.get("error") and "external" in result.get("error", "").lower():
                app_record.status = ApplicationStatus.FAILED
                app_record.bot_error = result.get("error", "External posting")
                app_record.retry_count = 999
            else:
                app_record.status = ApplicationStatus.FAILED
                app_record.bot_error = result.get("error", "Unknown error")
                app_record.retry_count += 1

            await db.commit()
            return result

        return result

    async def _run_playwright(
        self,
        app: Application,
        job: Optional[Job],
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
                persistent_dir = os.environ.get("INTERNSHALA_PERSISTENT_DIR") or os.environ.get("INTERNShALA_PERSISTENT_DIR")
                
                # Detect ATS early so we can load the stored fingerprint for
                # cookie-based platforms (e.g. Internshala) before creating context.
                ats = self._detect_ats(job.source_url)
                internshala_cookies = None
                internshala_storage_state = None
                internshala_fingerprint = None
                if ats == "internshala" and app.user_id:
                    try:
                        from app.services.cookie_service import cookie_service
                        cookie_data = await cookie_service.get_cookies(app.user_id, "internshala")
                        if cookie_data:
                            internshala_cookies = cookie_data.get("cookies")
                            internshala_storage_state = cookie_data.get("storage_state")
                            internshala_fingerprint = cookie_data.get("fingerprint")
                            if internshala_fingerprint:
                                logger.info(
                                    "Loaded Internshala fingerprint from DB",
                                    user_id=str(app.user_id),
                                    user_agent=internshala_fingerprint.get("user_agent", "")[:40],
                                    viewport=internshala_fingerprint.get("viewport"),
                                )
                            if internshala_storage_state:
                                logger.info(
                                    "Loaded full Internshala storage_state (cookies + localStorage)",
                                    user_id=str(app.user_id),
                                    cookie_count=len(internshala_storage_state.get("cookies", [])),
                                    origin_count=len(internshala_storage_state.get("origins", [])),
                                )
                    except Exception as e:
                        logger.warning("Could not load Internshala cookies/fingerprint", error=str(e))
                
                # FIX 4: Randomize User-Agent and viewport per session
                _chrome_ver = _rand.choice(["122", "123", "124", "125", "126"])
                _ua = f"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{_chrome_ver}.0.0.0 Safari/537.36"
                _w, _h = _rand.choice([(1366, 768), (1440, 900), (1536, 864), (1920, 1080)])
                
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
                    user_agent=_ua,
                    viewport={"width": _w, "height": _h},
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
                
                # Reuse the exact fingerprint that captured these cookies so
                # Internshala doesn't flag the session as stolen/suspicious.
                if internshala_fingerprint:
                    fp_ua = internshala_fingerprint.get("user_agent")
                    fp_vp = internshala_fingerprint.get("viewport")
                    fp_locale = internshala_fingerprint.get("locale")
                    fp_tz = internshala_fingerprint.get("timezone_id")
                    fp_geo = internshala_fingerprint.get("geolocation")
                    if fp_ua:
                        context_kwargs["user_agent"] = fp_ua
                    if fp_vp and isinstance(fp_vp, dict) and "width" in fp_vp and "height" in fp_vp:
                        context_kwargs["viewport"] = fp_vp
                    if fp_locale:
                        context_kwargs["locale"] = fp_locale
                    if fp_tz:
                        context_kwargs["timezone_id"] = fp_tz
                    if fp_geo:
                        context_kwargs["geolocation"] = fp_geo
                    logger.info("Applied stored Internshala fingerprint for context creation")
                
                # Add proxy only when explicitly configured
                proxy_server = os.environ.get("BROWSER_PROXY_SERVER")
                proxy_user = os.environ.get("BROWSER_PROXY_USER")
                proxy_pass = os.environ.get("BROWSER_PROXY_PASS")

                if proxy_server:
                    proxy_dict = {"server": proxy_server}
                    if proxy_user:
                        proxy_dict["username"] = proxy_user
                    if proxy_pass:
                        proxy_dict["password"] = proxy_pass
                    context_kwargs["proxy"] = proxy_dict
                    logger.info("Using configured browser proxy", server=proxy_server, user=proxy_user)
                else:
                    logger.info("Browser proxy disabled")

                # FIX 6: Always use fresh context per application (no persistent profile)
                browser = await p.chromium.launch(
                    headless=_browser_headless(),
                    args=launch_args,
                )
                # Restore full storage state (cookies + localStorage) for Internshala
                # so sessions that depend on localStorage tokens keep working.
                new_context_kwargs = dict(context_kwargs)
                if internshala_storage_state:
                    new_context_kwargs["storage_state"] = internshala_storage_state
                context = await browser.new_context(**new_context_kwargs)
                logger.info("Using fresh browser context (no persistent profile)")
                
                context.set_default_timeout(60000)

                # FIX 1: Apply stealth at CONTEXT level (always, no persistent guard)
                await context.add_init_script(STEALTH_SCRIPT)
                logger.info("Applied context-level stealth script")
                
                # FIX 6: Extra HTTP headers to look more like real browser
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
                
                # FIX 6: Random delay after context creation before navigation
                await asyncio.sleep(_rand.uniform(1, 3))

                # Only add stealth init script for non-persistent contexts
                # Persistent profiles already have the fingerprint from login
                if not persistent_dir:
                    await context.add_init_script("""
                        () => {
                            Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
                            Object.defineProperty(navigator, 'plugins', {
                                get: () => {
                                    var arr = [
                                        { name: 'Chrome PDF Plugin', filename: 'internal-pdf-viewer', description: 'Portable Document Format' },
                                        { name: 'Chrome PDF Viewer', filename: 'mhjfbmdgcfjbbpaeojofohoefgiehjai', description: '' },
                                        { name: 'Native Client', filename: 'internal-nacl-plugin', description: '' }
                                    ];
                                    arr.item = function(i) { return arr[i]; };
                                    arr.namedItem = function(n) { return arr.find(function(p) { return p.name === n; }) || null; };
                                    arr.refresh = function() {};
                                    Object.setPrototypeOf(arr, PluginArray.prototype);
                                    return arr;
                                }
                            });
                            Object.defineProperty(navigator, 'languages', { get: () => ['en-IN', 'en-GB', 'en'] });
                            window.chrome = {
                                app: {
                                    isInstalled: false,
                                    InstallState: { DISABLED: 'disabled', INSTALLED: 'installed', NOT_INSTALLED: 'not_installed' },
                                    RunningState: { CANNOT_RUN: 'cannot_run', READY_TO_RUN: 'ready_to_run', RUNNING: 'running' }
                                },
                                runtime: { connect: function() {}, sendMessage: function() {} },
                                loadTimes: function() {},
                                csi: function() {},
                            };
                            Object.defineProperty(navigator, 'hardwareConcurrency', { get: () => 8 });
                            Object.defineProperty(navigator, 'deviceMemory', { get: () => 8 });
                            const getParameter = WebGLRenderingContext.prototype.getParameter;
                            WebGLRenderingContext.prototype.getParameter = function(parameter) {
                                if (parameter === 37445) return 'Intel Inc.';
                                if (parameter === 37446) return 'Intel(R) UHD Graphics 620';
                                return getParameter.call(this, parameter);
                            };
                            const originalQuery = window.navigator.permissions.query;
                            window.navigator.permissions.query = (parameters) => (
                                parameters.name === 'notifications'
                                    ? Promise.resolve({ state: Notification.permission })
                                    : originalQuery(parameters)
                            );
                            if (!navigator.getBattery) {
                                navigator.getBattery = () => Promise.resolve({
                                    charging: true, chargingTime: 0,
                                    dischargingTime: Infinity, level: 1.0
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
                        }
                    """)

                page = await context.new_page()
                

                try:
                    logger.info("Detected ATS", ats=ats, url=job.source_url)

                    if ats == "internshala":
                        # If storage_state was restored, cookies are already in context.
                        cookies_to_inject = internshala_cookies if not internshala_storage_state else None
                        result = await apply_internshala(
                            page, job, profile, resume, settings,
                            user_id=app.user_id,
                            user_full_name=user_full_name,
                            preloaded_cookies=cookies_to_inject,
                        )
                    elif ats == "linkedin":
                        result = await self._apply_linkedin(page, job, profile, resume)
                    elif ats == "greenhouse":
                        result = await self._apply_greenhouse(page, job, profile, resume, user_full_name)
                    elif ats == "lever":
                        result = await self._apply_lever(page, job, profile, resume)
                    elif ats == "workday":
                        result = await self._apply_workday(page, job, profile, resume)
                    elif ats == "indeed":
                        result = await self._apply_indeed(page, job, profile, resume)
                    elif ats == "wellfound":
                        result = await self._apply_wellfound(page, job, profile, resume)
                    else:
                        result = await self._apply_generic(page, job, profile, resume)

                    return result

                except Exception as e:
                    import traceback
                    error_str = str(e)
                    # Check for the coroutine issue specifically
                    if "coroutine" in error_str and "lower" in error_str:
                        import traceback
                        logger.error("Coroutine error in apply_bot", traceback=traceback.format_exc())
                    
                    # DEBUG: Log full traceback for any error
                    logger.error("Apply exception", app_id=app.id, error=error_str, trace=traceback.format_exc())
                    
                    is_captcha = any(w in error_str.lower() for w in ["captcha", "recaptcha", "verify you are human"])
                    return {
                        "success": False,
                        "captcha": is_captcha,
                        "error": error_str,
                    }
                finally:
                    try:
                        await context.close()
                    except Exception:
                        pass
                    if browser:
                        try:
                            await browser.close()
                        except Exception:
                            pass
        except ImportError:
            logger.error("Playwright not installed. Run: pip install playwright && playwright install chromium")
            return {"success": False, "error": "Playwright not installed"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _run_playwright_sync(self, app, job, profile, resume, user_full_name: Optional[str] = None) -> dict:
        """Synchronous wrapper for Windows — runs Playwright with ProactorEventLoop."""
        import asyncio, sys
        if sys.platform == "win32":
            asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

        async def _inner():
            from playwright.async_api import async_playwright
            try:
                async with async_playwright() as p:
                    ats = self._detect_ats(job.source_url)
                    internshala_cookies = None
                    internshala_storage_state = None
                    internshala_fingerprint = None
                    if ats == "internshala" and app.user_id:
                        try:
                            from app.services.cookie_service import cookie_service
                            cookie_data = await cookie_service.get_cookies(app.user_id, "internshala")
                            if cookie_data:
                                internshala_cookies = cookie_data.get("cookies")
                                internshala_storage_state = cookie_data.get("storage_state")
                                internshala_fingerprint = cookie_data.get("fingerprint")
                        except Exception as e:
                            logger.warning("Could not load Internshala cookies/fingerprint (sync wrapper)", error=str(e))

                    context_kwargs = dict(
                        user_agent=(
                            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                            "AppleWebKit/537.36 (KHTML, like Gecko) "
                            "Chrome/124.0.0.0 Safari/537.36"
                        ),
                        viewport={"width": 1366, "height": 768},
                        locale="en-IN",
                        timezone_id="Asia/Kolkata",
                    )
                    if internshala_fingerprint:
                        fp_ua = internshala_fingerprint.get("user_agent")
                        fp_vp = internshala_fingerprint.get("viewport")
                        if fp_ua:
                            context_kwargs["user_agent"] = fp_ua
                        if fp_vp and isinstance(fp_vp, dict) and "width" in fp_vp and "height" in fp_vp:
                            context_kwargs["viewport"] = fp_vp

                    browser = await p.chromium.launch(
                        headless=_browser_headless(),
                        args=[
                            "--no-sandbox",
                            "--disable-blink-features=AutomationControlled",
                            "--disable-dev-shm-usage",
                            "--disable-setuid-sandbox",
                            "--window-size=1366,768",
                        ],
                    )
                    if internshala_storage_state:
                        context_kwargs["storage_state"] = internshala_storage_state
                    context = await browser.new_context(**context_kwargs)
                    await context.add_init_script(STEALTH_SCRIPT)
                    page = await context.new_page()
                    try:
                        if ats == "internshala":
                            from app.core.config import settings as _s
                            from app.agents.apply_bot_internshala import apply_internshala
                            cookies_to_inject = internshala_cookies if not internshala_storage_state else None
                            result = await apply_internshala(page, job, profile, resume, _s, user_id=app.user_id, preloaded_cookies=cookies_to_inject)
                        elif ats == "linkedin":
                            result = await self._apply_linkedin(page, job, profile, resume)
                        elif ats == "greenhouse":
                            result = await self._apply_greenhouse(page, job, profile, resume, user_full_name)
                        elif ats == "lever":
                            result = await self._apply_lever(page, job, profile, resume)
                        else:
                            result = await self._apply_generic(page, job, profile, resume)
                        return result
                    except Exception as e:
                        return {"success": False, "error": str(e)}
                    finally:
                        await browser.close()
            except Exception as e:
                return {"success": False, "error": str(e)}

        return asyncio.run(_inner())

    def _detect_ats(self, url: str) -> str:
        """Detect which ATS the job URL belongs to."""
        url_lower = url.lower()
        for ats, domain in self.ATS_HANDLERS.items():
            if domain in url_lower:
                return ats
        return "generic"

    async def _apply_linkedin(self, page, job, profile, resume) -> dict:
        """Handle LinkedIn Easy Apply."""
        await page.goto(job.source_url, wait_until="domcontentloaded")
        await asyncio.sleep(2)

        # Check for Easy Apply button
        easy_apply_btn = await page.query_selector("button[aria-label*='Easy Apply']")
        if not easy_apply_btn:
            return {"success": False, "error": "No Easy Apply button found — requires manual application"}

        await easy_apply_btn.click()
        await asyncio.sleep(1)

        # Fill multi-step form
        max_steps = 10
        for step in range(max_steps):
            await self._fill_linkedin_step(page, profile)
            await asyncio.sleep(1)

            # Check for submit button
            submit_btn = await page.query_selector("button[aria-label='Submit application']")
            if submit_btn:
                await submit_btn.click()
                await asyncio.sleep(2)
                return {"success": True, "ats": "linkedin", "steps": step + 1}

            # Next button
            next_btn = (
                await page.query_selector("button[aria-label='Continue to next step']") or
                await page.query_selector("button[aria-label='Review your application']")
            )
            if next_btn:
                await next_btn.click()
                await asyncio.sleep(1)
            else:
                break

        return {"success": False, "error": "Could not complete LinkedIn Easy Apply form"}

    async def _fill_linkedin_step(self, page, profile):
        """Fill visible form fields in current LinkedIn step."""
        if not profile:
            return

        # Phone number
        phone_field = await page.query_selector("input[id*='phone']")
        if phone_field:
            val = await phone_field.input_value()
            if not val and profile.phone:
                await phone_field.fill(profile.phone)

        # Common text fields
        field_mappings = {
            "input[id*='city']": profile.location or "",
            "input[id*='location']": profile.location or "",
        }
        for selector, value in field_mappings.items():
            if value:
                field = await page.query_selector(selector)
                if field:
                    existing = await field.input_value()
                    if not existing:
                        await field.fill(value)

        # Yes/No radio buttons — default to "Yes" for standard questions
        yes_radios = await page.query_selector_all("input[type='radio'][value='Yes']")
        for radio in yes_radios:
            if not await radio.is_checked():
                await radio.check()

    async def _apply_greenhouse(self, page, job, profile, resume, user_full_name: Optional[str] = None) -> dict:
        """Handle Greenhouse ATS applications."""
        await page.goto(job.source_url, wait_until="domcontentloaded")
        await asyncio.sleep(2)

        if not profile:
            return {"success": False, "error": "No profile configured"}

        # Use user's actual name if available
        if user_full_name:
            name_parts = user_full_name.split()
            first_name = name_parts[0] if name_parts else ""
            last_name = " ".join(name_parts[1:]) if len(name_parts) > 1 else ""
        else:
            first_name = "Applicant"
            last_name = ""
        
        await self._fill_field(page, "input#first_name", first_name)
        await self._fill_field(page, "input#last_name", last_name)
        await self._fill_field(page, "input#email", settings.USER_EMAIL)
        await self._fill_field(page, "input#phone", profile.phone or "")

        # Upload resume
        if resume and resume.file_path:
            resume_full_path = settings.storage_path / resume.file_path
            if resume_full_path.exists():
                resume_input = await page.query_selector("input[type='file']")
                if resume_input:
                    await resume_input.set_input_files(str(resume_full_path))
                    await asyncio.sleep(2)

        # Submit
        submit_btn = await page.query_selector("input[type='submit'], button[type='submit']")
        if submit_btn:
            await submit_btn.click()
            await asyncio.sleep(3)
            return {"success": True, "ats": "greenhouse"}

        return {"success": False, "error": "Could not find submit button"}

    async def _apply_lever(self, page, job, profile, resume) -> dict:
        """Handle Lever ATS applications."""
        await page.goto(job.source_url, wait_until="domcontentloaded")
        await asyncio.sleep(2)

        if not profile:
            return {"success": False, "error": "No profile configured"}

        await self._fill_field(page, "input[name='name']", settings.USER_NAME)
        await self._fill_field(page, "input[name='email']", settings.USER_EMAIL)
        await self._fill_field(page, "input[name='phone']", profile.phone or "")

        # Resume upload
        if resume and resume.file_path:
            resume_full_path = settings.storage_path / resume.file_path
            if resume_full_path.exists():
                file_input = await page.query_selector("input[type='file']")
                if file_input:
                    await file_input.set_input_files(str(resume_full_path))
                    await asyncio.sleep(2)

        submit_btn = await page.query_selector("button[type='submit'], input[type='submit']")
        if submit_btn:
            await submit_btn.click()
            await asyncio.sleep(3)
            return {"success": True, "ats": "lever"}

        return {"success": False, "error": "Submit button not found"}

    async def _apply_workday(self, page, job, profile, resume) -> dict:
        """Handle Workday ATS — most complex, requires login."""
        # Workday requires account creation — flag for manual
        return {
            "success": False,
            "error": "Workday requires account creation. Please apply manually.",
            "url": job.source_url,
        }

    async def _apply_generic(self, page, job, profile, resume) -> dict:
        """Generic form filler for unknown ATS systems."""
        await page.goto(job.source_url, wait_until="domcontentloaded")
        await asyncio.sleep(2)

        if not profile:
            return {"success": False, "error": "No profile configured"}

        # Try common field patterns
        field_patterns = [
            ("input[name*='name'], input[placeholder*='name' i]", settings.USER_NAME),
            ("input[name*='email'], input[type='email']", settings.USER_EMAIL),
            ("input[name*='phone'], input[type='tel']", profile.phone or ""),
        ]

        for selector, value in field_patterns:
            if value:
                try:
                    field = await page.query_selector(selector)
                    if field:
                        await field.fill(value)
                except Exception:
                    pass

        # Look for submit
        submit_btn = await page.query_selector(
            "button[type='submit'], input[type='submit'], button:has-text('Apply'), button:has-text('Submit')"
        )
        if submit_btn:
            await submit_btn.click()
            await asyncio.sleep(3)
            return {"success": True, "ats": "generic"}

        return {"success": False, "error": "No submit button found on generic form"}

    async def _fill_field(self, page, selector: str, value: str) -> None:
        """Safely fill a form field if it exists and is empty."""
        if not value:
            return
        try:
            field = await page.query_selector(selector)
            if field:
                existing = await field.input_value()
                if not existing:
                    await field.fill(value)
        except Exception:
            pass

    async def _close_popups(self, page) -> None:
        """Close any subscription or overlay popups that may block interactions."""
        try:
            # Wait a moment for any popup to appear
            await asyncio.sleep(1)
            
            # Try pressing Escape first (works for many modals)
            await page.keyboard.press("Escape")
            await asyncio.sleep(0.5)
            
            # Use JavaScript to remove modal overlays that block interactions
            await page.evaluate("""
                () => {
                    // Find and remove any modal overlays
                    const modals = document.querySelectorAll('.modal, .modal-backdrop, [class*="subscription"], .overlay');
                    modals.forEach(modal => {
                        modal.style.display = 'none';
                        modal.style.visibility = 'hidden';
                        modal.style.opacity = '0';
                    });
                    
                    // Also try to find and click any visible close buttons
                    const closeButtons = document.querySelectorAll('button[class*="close"], button[aria-label="Close"], .modal-header button');
                    closeButtons.forEach(btn => {
                        if (btn.offsetParent !== null) { // if visible
                            btn.click();
                        }
                    });
                }
            """)
            await asyncio.sleep(0.5)
            
        except Exception as e:
            # Silently ignore popup close errors
            pass

    async def _check_and_wait_for_captcha(self, page, screenshot_dir) -> bool:
        """Check if captcha is present and wait for user to solve it."""
        try:
            # Look for various captcha indicators - use simpler selectors only
            captcha_selectors = [
                "[class*='captcha']",
                "iframe[src*='captcha']",
                ".g-recaptcha",
                "[class*='verification']",
            ]
            
            for selector in captcha_selectors:
                try:
                    captcha = await page.query_selector(selector)
                    if captcha:
                        logger.info(f"Captcha detected: {selector}")
                        # Save screenshot
                        try:
                            await page.screenshot(path=str(screenshot_dir / f"captcha_detected_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"))
                        except:
                            pass
                        return True
                except Exception as e:
                    # Skip selectors that fail to parse
                    continue
            
            return False
            
        except Exception as e:
            logger.warning(f"Error checking for captcha: {e}")
            return False

    async def _apply_indeed(self, page, job, profile, resume) -> dict:
        """Handle Indeed job applications - try without login first."""
        await page.goto(job.source_url, wait_until="domcontentloaded")
        await asyncio.sleep(2)

        # First, try to find and click Apply button WITHOUT logging in
        # Many Indeed jobs allow "Apply without account"
        
        # Look for "Apply without account" or "Easy Apply" button
        easy_apply_btn = await page.query_selector(
            "button[data-testid='apply-button'], "
            "button:has-text('Apply without account'), "
            "button:has-text('Apply Now'), "
            "a:has-text('Apply without account'), "
            "a:has-text('Apply to job')"
        )
        
        if easy_apply_btn:
            await easy_apply_btn.click()
            await asyncio.sleep(2)
            
            # Check if it went to a login page
            login_check = await page.query_selector("input[type='email'], input[id='identifier'], text='Sign in'")
            if login_check:
                # Login required - try with credentials if available
                if settings.INDEED_EMAIL and settings.INDEED_PASSWORD:
                    return await self._indeed_login_and_apply(page, profile, resume)
                else:
                    return {"success": False, "error": "Login required - please provide Indeed credentials in .env"}
            
            # Fill application form without login
            result = await self._indeed_fill_form(page, profile, resume)
            if result.get("success"):
                return result
        
        # Try direct application form
        result = await self._indeed_fill_form(page, profile, resume)
        if result.get("success"):
            return result

        return {"success": False, "error": "Could not apply to Indeed job - login may be required"}

    async def _indeed_login_and_apply(self, page, profile, resume) -> dict:
        """Handle Indeed login and then apply."""
        try:
            # Enter email
            email_input = await page.query_selector("input[type='email'], input[id='identifier']")
            if email_input:
                await email_input.fill(settings.INDEED_EMAIL)
                await asyncio.sleep(1)
                
                next_btn = await page.query_selector("button[type='submit'], button:has-text('Continue'), button:has-text('Next')")
                if next_btn:
                    await next_btn.click()
                    await asyncio.sleep(2)
                
                # Check for verification code
                if await page.query_selector("text=verification, text=code, text=OTP"):
                    return {"success": False, "error": "Indeed requires verification code - please use jobs that don't require login or apply manually"}
                
                # Enter password
                password_input = await page.query_selector("input[type='password'], input[id='password']")
                if password_input:
                    await password_input.fill(settings.INDEED_PASSWORD)
                    await asyncio.sleep(1)
                    
                    submit_btn = await page.query_selector("button[type='submit'], button:has-text('Sign in')")
                    if submit_btn:
                        await submit_btn.click()
                        await asyncio.sleep(3)
                        
                        # Check again for verification
                        if await page.query_selector("text=verification, text=code, text=OTP"):
                            return {"success": False, "error": "Indeed requires verification code - please use jobs that don't require login or apply manually"}
            
            # After login, try to fill form
            return await self._indeed_fill_form(page, profile, resume)
            
        except Exception as e:
            return {"success": False, "error": f"Indeed login failed: {str(e)}"}

    async def _indeed_fill_form(self, page, profile, resume) -> dict:
        """Fill Indeed application form."""
        # Fill form fields
        if profile:
            await self._fill_field(page, "input[name='phone'], input[id='phoneNumber'], input[name='phone_number']", profile.phone or "")
            await self._fill_field(page, "input[name='city'], input[id='city'], input[name='location']", profile.location or "")

        # Upload resume if available
        if resume and resume.file_path:
            resume_full_path = settings.storage_path / resume.file_path
            if resume_full_path.exists():
                resume_input = await page.query_selector("input[type='file']")
                if resume_input:
                    await resume_input.set_input_files(str(resume_full_path))
                    await asyncio.sleep(2)

        # Submit application
        submit_btn = await page.query_selector(
            "button[type='submit'], "
            "button:has-text('Submit application'), "
            "button:has-text('Submit'), "
            "button:has-text('Apply')"
        )
        if submit_btn:
            await submit_btn.click()
            await asyncio.sleep(3)
            
            # Check for success
            success_text = await page.query_selector("text=success, text=submitted, text=applied")
            if success_text:
                return {"success": True, "ats": "indeed"}

        return {"success": False, "error": "Could not complete Indeed form"}

    async def _apply_wellfound(self, page, job, profile, resume) -> dict:
        """Handle Wellfound (formerly AngelList) job applications."""
        await page.goto(job.source_url, wait_until="domcontentloaded")
        await asyncio.sleep(2)

        # Check for Apply button
        apply_btn = await page.query_selector("button:has-text('Apply'), button:has-text('Apply Now'), a:has-text('Apply')")
        if not apply_btn:
            return {"success": False, "error": "No Apply button found on Wellfound"}

        await apply_btn.click()
        await asyncio.sleep(2)

        # Fill application form
        if profile:
            await self._fill_field(page, "input[name='phone'], input[id='phone']", profile.phone or "")

        # Upload resume if available
        if resume and resume.file_path:
            resume_full_path = settings.storage_path / resume.file_path
            if resume_full_path.exists():
                resume_input = await page.query_selector("input[type='file']")
                if resume_input:
                    await resume_input.set_input_files(str(resume_full_path))
                    await asyncio.sleep(2)

        # Submit application
        submit_btn = await page.query_selector("button[type='submit'], button:has-text('Submit Application'), button:has-text('Submit')")
        if submit_btn:
            await submit_btn.click()
            await asyncio.sleep(3)
            return {"success": True, "ats": "wellfound"}

        return {"success": False, "error": "Could not complete Wellfound application"}