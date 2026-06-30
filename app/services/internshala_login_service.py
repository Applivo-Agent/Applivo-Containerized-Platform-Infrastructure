"""
app/services/internshala_login_service.py
───────────────────────────────────────
Handles Internshala login via Playwright - user manually logs in, we capture cookies.
"""

from __future__ import annotations

import asyncio
import random
from typing import Optional
import os
from pathlib import Path

import structlog
from playwright.async_api import async_playwright, Browser, BrowserContext, Page, Playwright
from app.services.cookie_service import cookie_service

logger = structlog.get_logger()


def _browser_headless() -> Union[bool, str]:
    """
    Return headless setting for server-side login.
    Defaults to 'shell' (new Chromium headless mode) which is far less detectable
    than the legacy headless=True. Use BROWSER_HEADLESS=1 for legacy mode or
    BROWSER_HEADLESS=0 for headed mode (requires a display).
    """
    headless_env = os.environ.get("INTERNSHALA_HEADLESS") or os.environ.get("BROWSER_HEADLESS")
    if headless_env is not None:
        val = headless_env.strip().lower()
        if val in ("0", "false", "no", "off"):
            return False
        if val == "shell":
            return "shell"
        return True
    # Default to new headless shell mode for better stealth.
    return "shell"


# Browser fingerprint config (must match apply_bot.py exactly)
import random as _rand
_CHROME_VER = _rand.choice(["122", "123", "124", "125", "126"])
_USER_AGENT = f"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{_CHROME_VER}.0.0.0 Safari/537.36"
_W, _H = _rand.choice([(1366, 768), (1440, 900), (1536, 864), (1920, 1080)])

# ── Context-level stealth script (applied to ALL pages) ──
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

_LAUNCH_ARGS = [
    "--no-sandbox",
    "--disable-dev-shm-usage",
    "--disable-blink-features=AutomationControlled",
    "--disable-infobars",
    "--start-maximized",
    "--disable-web-security",
    "--disable-features=IsolateOrigins,site-per-process",
    "--disable-gpu",
]

_CONTEXT_KWARGS = dict(
    user_agent=_USER_AGENT,
    viewport={"width": _W, "height": _H},
    locale="en-IN",
    timezone_id="Asia/Kolkata",
    permissions=["geolocation"],
    geolocation={"latitude": 12.9716, "longitude": 77.5946},
    color_scheme="light",
    java_script_enabled=True,
    extra_http_headers={
        "Accept-Language": "en-IN,en-US;q=0.9,en;q=0.8",
        "Accept-Encoding": "gzip, deflate, br",
        "DNT": "1",
    },
)

class InternshalaLoginService:
    """Service to log into Internshala and capture session cookies."""

    async def login_and_save_cookies(
        self,
        user_id: str,
        email: str = "",
        password: str = "",
    ) -> dict:
        """
        Open browser, attempt credential-based login, then capture cookies.
        """
        logger.info("Starting Internshala login", user_id=user_id)
        
        storage_state, fingerprint = await self._perform_login(
            user_id=user_id, page_email=email, page_password=password
        )
        
        if not storage_state:
            return {
                "success": False,
                "message": "Login failed - no cookies obtained. Please try again.",
                "needs_captcha": False,
            }
        
        await cookie_service.save_cookies(
            user_id=user_id,
            platform="internshala",
            cookies=storage_state,
            fingerprint=fingerprint,
        )
        
        return {
            "success": True,
            "message": "Successfully logged in and saved cookies",
            "cookies_count": len(storage_state.get("cookies", [])),
            "needs_captcha": False,
        }

    async def _perform_login(self, user_id: str = "", page_email: str = "", page_password: str = "") -> Optional[list]:
        """
        Open browser to Internshala, log in with credentials when available,
        and capture cookies from the authenticated session.
        """
        playwright: Optional[Playwright] = None
        browser: Optional[Browser] = None
        context: Optional[BrowserContext] = None
        
        try:
            logger.info("Starting Playwright login flow")
            playwright = await async_playwright().start()

            # Support proxy and persistent context via env vars for VPS automation
            proxy_server = os.environ.get("INTERNSHALA_PROXY_SERVER")
            proxy_user = os.environ.get("INTERNSHALA_PROXY_USERNAME")
            proxy_pass = os.environ.get("INTERNSHALA_PROXY_PASSWORD")
            headless = _browser_headless()

            launch_args = _LAUNCH_ARGS.copy()
            launch_args.extend([
                "--disable-web-security",
                "--disable-features=IsolateOrigins,site-per-process",
                "--disable-gpu",
            ])

            proxy = None
            if proxy_server:
                proxy = {"server": proxy_server}
                if proxy_user:
                    proxy["username"] = proxy_user
                if proxy_pass:
                    proxy["password"] = proxy_pass

            # Use shared context kwargs
            context_kwargs = _CONTEXT_KWARGS.copy()
            context_kwargs["accept_downloads"] = True
            if proxy:
                context_kwargs["proxy"] = proxy

            # Capture the fingerprint that will be paired with these cookies.
            # The apply bot reuses this exact fingerprint so Internshala doesn't
            # invalidate the session due to UA/viewport drift.
            fingerprint = {
                "user_agent": context_kwargs.get("user_agent"),
                "viewport": context_kwargs.get("viewport"),
                "locale": context_kwargs.get("locale"),
                "timezone_id": context_kwargs.get("timezone_id"),
                "geolocation": context_kwargs.get("geolocation"),
            }

            # Optionally use a persisted storage_state
            storage_state_path = os.environ.get("INTERNSHALA_STORAGE_STATE_PATH")

            if storage_state_path:
                try:
                    p = Path(storage_state_path)
                    if p.exists():
                        context_kwargs["storage_state"] = storage_state_path
                        logger.info("Using existing Internshala storage_state", path=storage_state_path)
                except Exception:
                    pass

            # If persistent user-data dir requested, use launch_persistent_context
            # Use user-specific subdirectory for multi-user SaaS
            raw_persistent_dir = os.environ.get("INTERNSHALA_PERSISTENT_DIR") or os.environ.get("INTERNShALA_PERSISTENT_DIR")
            persistent_dir = None
            if raw_persistent_dir:
                if user_id:
                    safe_user_id = str(user_id).replace("-", "_").replace(" ", "_")
                    persistent_dir = os.path.join(raw_persistent_dir, safe_user_id)
                    logger.info("Using user-specific persistent browser context", user_id=user_id, dir=persistent_dir)
                else:
                    persistent_dir = raw_persistent_dir
                    logger.info("Using shared persistent browser context (no user_id)", dir=persistent_dir)
                try:
                    Path(persistent_dir).mkdir(parents=True, exist_ok=True)
                except Exception:
                    pass

            if persistent_dir:
                logger.info("Launching persistent browser context", dir=persistent_dir, headless=headless)
                context = await playwright.chromium.launch_persistent_context(
                    user_data_dir=persistent_dir,
                    headless=headless,
                    proxy=proxy if proxy else None,
                    args=launch_args,
                    **context_kwargs,
                )
                # launch_persistent_context returns a BrowserContext
            else:
                browser = await playwright.chromium.launch(
                    headless=headless,
                    proxy=proxy if proxy else None,
                    args=launch_args,
                )
                # Create context with more realistic settings
                context = await browser.new_context(**context_kwargs)
                
            context.set_default_timeout(60000)
            
            # FIX 1: Apply stealth at CONTEXT level (matches apply_bot.py)
            await context.add_init_script(STEALTH_SCRIPT)
            
            page = await context.new_page()
            
            # Event set when a network response indicates successful auth (XHR or Set-Cookie)
            auth_event = asyncio.Event()

            async def _inspect_json_response(resp, event: asyncio.Event):
                try:
                    # Only inspect small JSON responses to avoid heavy work
                    ct = resp.headers.get("content-type") or resp.headers.get("Content-Type") or ""
                    if "application/json" not in ct.lower():
                        return
                    # Read json body
                    try:
                        j = await resp.json()
                    except Exception:
                        return
                    if isinstance(j, dict):
                        keys = set(k.lower() for k in j.keys())
                        if keys & {"user", "token", "access", "auth", "session", "authenticated", "success"}:
                            logger.info("Detected login via JSON response body", url=resp.url)
                            loop = asyncio.get_running_loop()
                            loop.call_soon_threadsafe(event.set)
                            return
                    # If response contains token-like strings anywhere, set event
                    try:
                        s = str(j)
                        if "token" in s.lower() or "access_token" in s.lower() or "authenticated" in s.lower():
                            logger.info("Detected login via JSON response content", url=resp.url)
                            loop = asyncio.get_running_loop()
                            loop.call_soon_threadsafe(event.set)
                    except Exception:
                        pass
                except Exception:
                    pass

            def _on_response(resp):
                try:
                    u = resp.url
                    headers = resp.headers
                    # Heuristics: student endpoints or auth API calls, or Set-Cookie with auth markers
                    if any(x in u for x in ("/student/", "/api/auth", "/auth", "/session", "/signin", "/signin/", "/login")):
                        logger.info("Detected login via network response", url=u)
                        loop = asyncio.get_running_loop()
                        loop.call_soon_threadsafe(auth_event.set)
                        return

                    # Detect redirects or location headers that point to student/dashboard
                    location = headers.get("location") or headers.get("Location") or ""
                    if location and any(p in location for p in ("/student/", "/dashboard", "/profile")):
                        logger.info("Detected login via redirect Location header", url=u, location=location)
                        loop = asyncio.get_running_loop()
                        loop.call_soon_threadsafe(auth_event.set)
                        return

                    sc = headers.get("set-cookie") or headers.get("Set-Cookie") or ""
                    if sc and any(m in sc.lower() for m in ("session", "auth", "token", "login", "internshala")):
                        logger.info("Detected login via Set-Cookie header", url=u)
                        loop = asyncio.get_running_loop()
                        loop.call_soon_threadsafe(auth_event.set)
                        return

                    # If JSON responses are returned by auth endpoints, inspect bodies for auth tokens/user
                    ct = headers.get("content-type") or headers.get("Content-Type") or ""
                    if "application/json" in ct.lower() or u.endswith(".json"):
                        loop = asyncio.get_running_loop()
                        loop.create_task(_inspect_json_response(resp, auth_event))
                except Exception:
                    pass

            page.on("response", _on_response)
            
            # Enable console logging from browser
            page.on("console", lambda msg: logger.info(f"Browser: {msg.text}"))
            
            logger.info("Navigating to Internshala")
            await page.goto("https://internshala.com/login", wait_until="networkidle", timeout=60000)
            
            # Add random delay to appear more natural
            await asyncio.sleep(random.uniform(1, 3))

            has_credentials = bool(page_email and page_password)

            if has_credentials:
                logger.info("Submitting Internshala credentials")
                await self._submit_credentials(page, page_email, page_password)
            else:
                logger.info("No credentials provided, waiting for manual login fallback")
            
            logger.info("Waiting for login completion")
            
            # Credential mode should verify quickly; manual mode can wait longer.
            wait_timeout = 45 if has_credentials else 300
            login_mode = "credential" if has_credentials else "manual"
            login_success = await self._wait_for_login(page, timeout=wait_timeout, mode=login_mode, auth_event=auth_event)
            
            if not login_success:
                logger.error("Login timeout - verification did not complete", mode=login_mode, timeout=wait_timeout)
                return None, None
            
            await asyncio.sleep(2)
            
            # Verify we're logged in
            is_logged_in = await self._verify_login(page)
            if not is_logged_in:
                logger.error("Login verification failed")
                return None, None
            
            logger.info("Login successful, extracting storage state")
            # Capture full storage state (cookies + localStorage/origins) because
            # modern sites like Internshala store session tokens in localStorage.
            storage_state = await context.storage_state()
            cookies = storage_state.get("cookies", [])
            logger.info("Got cookies", count=len(cookies))

            # Persist storage_state to a file if configured (for debugging)
            try:
                storage_state_path = os.environ.get("INTERNSHALA_STORAGE_STATE_PATH")
                if storage_state_path:
                    try:
                        parent = Path(storage_state_path).parent
                        if not parent.exists():
                            parent.mkdir(parents=True, exist_ok=True)
                        import json as _json
                        Path(storage_state_path).write_text(_json.dumps(storage_state))
                        logger.info("Saved Internshala storage_state", path=storage_state_path)
                    except Exception as e:
                        logger.info("Failed to save storage_state", error=str(e))
            except Exception:
                pass
            
            if browser:
                await browser.close()
            elif context:
                await context.close()
            await playwright.stop()
            
            return storage_state, fingerprint
            
        except Exception as e:
            logger.error("Login failed with exception", error=str(e), error_type=type(e).__name__)
            try:
                if browser:
                    await browser.close()
                if playwright:
                    await playwright.stop()
            except:
                pass
            return None, None

    async def _submit_credentials(self, page: Page, email: str, password: str) -> None:
        """Fill the login form using common Internshala selectors and submit it."""
        email_selectors = [
            "input[type='email']",
            "input[name='email']",
            "input[name='user_email']",
            "input[placeholder*='email' i]",
        ]
        password_selectors = [
            "input[type='password']",
            "input[name='password']",
            "input[placeholder*='password' i]",
        ]
        submit_selectors = [
            "button[type='submit']",
            "input[type='submit']",
            "button:has-text('Login')",
            "button:has-text('Log in')",
            "button:has-text('Sign in')",
        ]

        async def fill_first_human(selectors: list[str], value: str) -> bool:
            for selector in selectors:
                try:
                    element = await page.query_selector(selector)
                    if element:
                        await element.scroll_into_view_if_needed()
                        await element.click()
                        await element.fill("")
                        # Human-like typing with variable delay and occasional pauses
                        for char in value:
                            await element.type(char, delay=random.uniform(40, 130))
                            if random.random() < 0.05:
                                await asyncio.sleep(random.uniform(0.1, 0.3))
                        return True
                except Exception:
                    continue
            return False

        email_filled = await fill_first_human(email_selectors, email)
        if not email_filled:
            raise RuntimeError("Unable to find Internshala email field")

        await asyncio.sleep(random.uniform(0.4, 1.0))

        password_filled = await fill_first_human(password_selectors, password)
        if not password_filled:
            raise RuntimeError("Unable to find Internshala password field")

        await asyncio.sleep(random.uniform(0.5, 1.2))

        for selector in submit_selectors:
            try:
                button = await page.query_selector(selector)
                if button:
                    await button.scroll_into_view_if_needed()
                    await asyncio.sleep(random.uniform(0.2, 0.5))
                    await button.click()
                    return
            except Exception:
                continue

        # Final fallback: press Enter in the password field
        await page.keyboard.press("Enter")

    async def _wait_for_login(self, page: Page, timeout: int = 300, mode: str = "manual", auth_event: Optional[asyncio.Event] = None) -> bool:
        """
        Wait for user to manually complete login.
        Returns True when login is detected.
        """
        logger.info("Waiting for login", timeout=timeout, mode=mode)
        
        login_indicators = [
            "a[href*='/student/dashboard']",
            "a[href*='/student/profile']",
            ".profile-header",
            ".student-profile-pic",
            "a:has-text('Logout')",
            "a:has-text('Sign Out')",
            "#header-profile-img",
            ".user-profile",
            "#profile-menu-container",
        ]
        
        for i in range(timeout):
            await asyncio.sleep(1)
            
            # Check URL - if redirected to student section, likely logged in
            url = page.url
            if "/student/" in url and "/login" not in url:
                logger.info("Detected login via URL", url=url)
                return True

            # Session/auth cookies often appear before UI updates.
            # NOTE: PHPSESSID is set for anonymous users too — do NOT treat it as auth.
            try:
                cookies = await page.context.cookies()
                auth_cookie_names = {"isc", "ists", "internshala_user", "is_registered"}
                has_auth_cookie = any(
                    c.get("domain") and "internshala.com" in c["domain"] and c.get("name", "").lower() in auth_cookie_names
                    for c in cookies
                )
                if has_auth_cookie:
                    logger.info("Detected login via auth cookie")
                    return True
            except Exception:
                pass

            # Also allow network-based detection via auth_event if provided
            try:
                if auth_event and auth_event.is_set():
                    logger.info("Detected login via network auth event")
                    return True
            except Exception:
                pass
            
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

        # Verify with an authenticated endpoint route first.
        try:
            await page.goto("https://internshala.com/student/dashboard", wait_until="domcontentloaded", timeout=15000)
            current_url = page.url.lower()
            if "/student/" in current_url and "login" not in current_url:
                return True
        except Exception:
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

        try:
            cookies = await page.context.cookies()
            auth_cookie_markers = ("session", "auth", "token", "user", "login")
            has_auth_cookie = any(
                c.get("domain") and "internshala.com" in c["domain"] and any(m in c.get("name", "").lower() for m in auth_cookie_markers)
                for c in cookies
            )
            if has_auth_cookie:
                return True
        except Exception:
            pass
        
        return False

    async def refresh_cookies(self, user_id: str) -> dict:
        """Attempt to refresh cookies."""
        return {
            "success": False,
            "message": "Please login again manually",
        }


internshala_login_service = InternshalaLoginService()