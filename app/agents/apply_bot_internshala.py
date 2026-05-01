"""
app/agents/apply_bot_internshala.py

FIXES in this version vs document-6:
  1. _get_form_errors: Python adjacent string literals inside JS caused
     "SyntaxError: Unexpected string" — collapsed to a single string.
  2. _fill_all_fields text inputs: inp.fill() requires element to be visible
     and times out 30 s on hidden fields (e.g. id=link).  Switched to JS
     direct value assignment so hidden fields are set without a timeout.
  3. _check_submission_result: after a successful AJAX submit Internshala
     sometimes opens a NEW confirmation modal (.modal.show) — so the old
     "wait for modal to disappear" check saw it and returned None, causing
     the crash path to run.  Now also checks for success text INSIDE the
     modal before declaring failure.
"""

from __future__ import annotations

import asyncio
import json
import random
import re
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Optional

import structlog

logger = structlog.get_logger()

# Paths resolved from centralized settings — avoids CWD-dependent bugs (Fix #4)
from app.core.config import settings as _path_settings
COOKIE_FILE = _path_settings.storage_path / "internshala_cookies.json"
SCREENSHOT_DIR = _path_settings.storage_path / "screenshots"


# ─────────────────────────────────────────────────────────────────────────────
#  AI SCREENING ANSWER
# ─────────────────────────────────────────────────────────────────────────────

async def _ai_answer(question: str, options: list, profile_summary: str, job_context: str = "") -> str:
    """
    Ask Groq to answer a screening question.
    - options non-empty → pick the best option (dropdown/radio/select).
    - options empty     → write a short professional free-text answer.
    job_context: extra job-specific info (title, required skills, description excerpt).
    Falls back gracefully on any error.
    """
    try:
        from openai import AsyncOpenAI
        from app.core.config import settings

        client = AsyncOpenAI(
            api_key=settings.ai_api_key,      # uses GROQ_API_KEY if set, else OPENAI_API_KEY
            base_url="https://api.groq.com/openai/v1",
        )

        if options:
            opts_text = "\n".join(f"  - {o}" for o in options)
            job_ctx_line = f"Job context:\n{job_context}\n\n" if job_context else ""
            prompt = (
                f"You are filling a job application form for a candidate.\n\n"
                f"Candidate profile summary:\n{profile_summary}\n\n"
                f"{job_ctx_line}"
                f"Question: {question}\n\n"
                f"Available options:\n{opts_text}\n\n"
                f"Reply with ONLY the exact text of the best option — nothing else."
            )
        else:
            job_ctx_line = f"Job context:\n{job_context}\n\n" if job_context else ""
            prompt = (
                f"You are filling a job application form for a candidate.\n\n"
                f"Candidate profile summary:\n{profile_summary}\n\n"
                f"{job_ctx_line}"
                f"Question: {question}\n\n"
                f"Write a concise, enthusiastic, professional answer (2-4 sentences). "
                f"Be specific about the candidate's actual skills matching the job. "
                f"Never use placeholder text like [specific skills] — use real skill names from the profile. "
                f"If asked for links or URLs and none are available, say 'Available upon request'. "
                f"If asked for a number (e.g. years of experience), reply with just the number."
            )

        resp = await client.chat.completions.create(
            model=settings.OPENAI_MODEL_LIGHT,
            max_tokens=150,
            temperature=0.3,
            messages=[{"role": "user", "content": prompt}],
        )
        answer = (resp.choices[0].message.content or "").strip().strip('"').strip("'")
        logger.info("AI answered screening question",
                    question=question[:80], answer=answer[:80])
        return answer
    except Exception as e:
        logger.warning("AI screening answer failed, using fallback", error=str(e))
        if options:
            return options[len(options) // 2]
        return (
            "I am a motivated and quick learner with relevant experience in this domain. "
            "I am eager to contribute my skills and grow professionally through this opportunity."
        )


def _build_profile_summary(profile, job=None) -> str:
    if not profile:
        return "Entry-level candidate, motivated and eager to learn."
    parts = []
    if profile.experience_level:
        parts.append(f"Experience level: {profile.experience_level}")
    if profile.professional_summary:
        parts.append(profile.professional_summary[:400])
    if profile.desired_roles:
        parts.append(f"Target roles: {', '.join(profile.desired_roles[:3])}")
    if getattr(profile, "work_experience", None):
        exp = profile.work_experience
        if exp:
            latest = exp[0]
            parts.append(
                f"Most recent experience: {latest.get('title', '')} at {latest.get('company', '')}"
            )
    if getattr(profile, "projects", None):
        proj_names = [p.get("name", "") for p in profile.projects[:3] if p.get("name")]
        if proj_names:
            parts.append(f"Projects: {', '.join(proj_names)}")
    if getattr(profile, "github_url", None):
        parts.append(f"GitHub: {profile.github_url}")
    if job:
        if getattr(job, "title", None):
            parts.append(f"Applying for: {job.title}")
        if getattr(job, "description_clean", None) or getattr(job, "description_raw", None):
            desc = (job.description_clean or job.description_raw or "")[:600]
            parts.append(f"Job description excerpt:\n{desc}")
    return "\n".join(parts) or "Entry-level candidate, motivated and eager to learn."


# ─────────────────────────────────────────────────────────────────────────────
#  LOW-LEVEL HELPERS
# ─────────────────────────────────────────────────────────────────────────────

async def _human_type(element, text: str) -> None:
    await element.click()
    await element.fill("")
    for char in text:
        await element.type(char, delay=random.uniform(40, 130))
        if random.random() < 0.05:
            await asyncio.sleep(random.uniform(0.1, 0.3))


def _load_cookies() -> list:
    if not COOKIE_FILE.exists():
        return []
    try:
        cookies = json.loads(COOKIE_FILE.read_text())
        for c in cookies:
            if c.get("sameSite") not in ("Strict", "Lax", "None"):
                c["sameSite"] = "Lax"
            if "domain" in c and not c["domain"].startswith("."):
                c["domain"] = "." + c["domain"].lstrip(".")
        return cookies
    except Exception as e:
        logger.warning("Could not load cookies", error=str(e))
        return []


async def _save_cookies(context) -> None:
    try:
        COOKIE_FILE.parent.mkdir(parents=True, exist_ok=True)
        cookies = await context.cookies()
        COOKIE_FILE.write_text(json.dumps(cookies, indent=2))
        logger.info("Cookies saved", count=len(cookies))
    except Exception as e:
        logger.warning("Could not save cookies", error=str(e))


async def _screenshot(page, name: str) -> None:
    try:
        SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        await page.screenshot(
            path=str(SCREENSHOT_DIR / f"{name}_{ts}.png"),
            full_page=True,
        )
    except Exception:
        pass


async def _has_captcha(page) -> bool:
    try:
        # Check for VISIBLE CAPTCHA challenge (iframe or interactive element)
        for frame in page.frames:
            if "recaptcha/api2/bframe" in frame.url or "hcaptcha.com/captcha" in frame.url:
                # Check if the frame is actually visible
                try:
                    box = await frame.frame_element().bounding_box()
                    if box and box["width"] > 0 and box["height"] > 0:
                        return True
                except Exception:
                    pass
        # Check for visible reCAPTCHA widget (not just script tags)
        recaptcha_div = await page.query_selector(".g-recaptcha:not([style*='display: none'])")
        if recaptcha_div and await recaptcha_div.is_visible():
            return True
        return False
    except Exception:
        return False


async def _wait_for_captcha_resolution(page, timeout_s: int = 120) -> bool:
    logger.info("Waiting for CAPTCHA", timeout=timeout_s)
    for _ in range(timeout_s):
        await asyncio.sleep(1)
        if not await _has_captcha(page):
            logger.info("CAPTCHA resolved")
            return True
    return False


async def _is_logged_in(page) -> bool:
    try:
        # First check URL - most reliable indicator
        url = page.url
        if "/student/" in url and "/login" not in url:
            logger.debug("_is_logged_in found /student/ in URL")
            return True
        
        # Check for multiple logged-in indicators
        selectors = [
            ".profile-header", "#header-profile-img",
            "a[href*='/student/dashboard']", "a[href*='/student/profile']",
            ".student-profile-pic", ".logged-in-header",
            # Additional selectors for current Internshala
            "a[href*='/student/']", ".user-profile",
            ".nav-item.profile", ".profile-dropdown",
            "img[alt*='profile' i]", ".avatar",
            # Check for logout link
            "a:has-text('Logout')", "a:has-text('Sign Out')",
            "a[href*='logout']", "a[href*='signout']",
        ]
        for sel in selectors:
            try:
                el = await page.query_selector(sel)
                if el:
                    logger.debug("_is_logged_in found", selector=sel)
                    return True
            except Exception:
                continue
        
        # Also check page content for logged-in indicators
        content = await page.content()
        if "logout" in content.lower() or "sign out" in content.lower():
            logger.debug("_is_logged_in found 'logout' in content")
            return True
        if "/student/" in content:
            logger.debug("_is_logged_in found /student/ in content")
            return True
            
        logger.debug("_is_logged_in returning False")
        return False
    except Exception as e:
        logger.debug("_is_logged_in exception", error=str(e))
        return False


async def _is_on_login_wall(page) -> bool:
    url = page.url
    if "/login" in url or "/signup" in url:
        return True
    try:
        el = await page.query_selector(
            "#login-modal input[type='email'], .modal input[type='email'], .login-modal"
        )
        return el is not None
    except Exception:
        return False


async def _dismiss_blocking_modals_only(page) -> None:
    """Dismiss login/promo modals without touching the application form modal."""
    try:
        for sel in (
            "#login-modal .close", "#login-modal button.close_action",
            "#signup-modal .close", "#register-modal .close",
            ".skilling-modal .close", ".training-popup .close",
            "button.modal_secondary_btn.close_action",
        ):
            try:
                btns = await page.query_selector_all(sel)
                for btn in btns:
                    if await btn.is_visible():
                        await btn.click()
                        await asyncio.sleep(0.3)
            except Exception:
                pass

        await page.keyboard.press("Escape")
        await asyncio.sleep(0.5)

        await page.evaluate("""
            () => {
                var blockingIds = [
                    'login-modal', 'signup-modal', 'register-modal',
                    'skilling-modal', 'training-popup', 'cookie-modal',
                    'cookieModal', 'cookie-consent'
                ];
                blockingIds.forEach(function(id) {
                    var el = document.getElementById(id);
                    if (el) el.remove();
                });
                
                // Remove modal backdrops first
                document.querySelectorAll('.modal-backdrop.show').forEach(function(el) {
                    el.remove();
                });
                
                // Handle generic aria-modal dialogs (including "One time offer" signup modals)
                document.querySelectorAll('[role="dialog"][aria-modal="true"]').forEach(function(dialog) {
                    // Check if it's a signup/offer modal (don't close if it's the application form)
                    var text = (dialog.innerText || '').toLowerCase();
                    var isSignupModal = text.includes('sign up') || text.includes('one time offer') || text.includes('free ai career');
                    
                    if (isSignupModal) {
                        // Try to close it first
                        var closeBtn = dialog.querySelector('[aria-label="Close"], .close, .modal-close, button[class*="close"], .signup-modal-close');
                        if (closeBtn) {
                            closeBtn.click();
                        }
                        // If not closed, remove it
                        setTimeout(() => dialog.remove(), 500);
                    }
                });
                
                // Also remove any visible signup/offer modals by selector
                document.querySelectorAll('.modal.show, [class*="signup-modal"]:not(form), [class*="offer-modal"]:not(form)').forEach(function(el) {
                    var text = (el.innerText || '').toLowerCase();
                    if (text.includes('sign up') || text.includes('one time offer')) {
                        el.remove();
                    }
                });
                
                // Always remove modal backdrops
                document.querySelectorAll('.modal-backdrop').forEach(function(el) {
                    el.remove();
                });
                document.body.classList.remove('modal-open');
                document.body.style.overflow = 'auto';
            }
        """)
        await asyncio.sleep(0.3)
    except Exception:
        pass


async def _do_login(page, email: str, password: str) -> dict:
    logger.info("Attempting login")
    if "/login" not in page.url:
        await page.goto(
            "https://internshala.com/login/user",
            wait_until="domcontentloaded", timeout=30000,
        )
        await asyncio.sleep(random.uniform(2, 3))

    if await _has_captcha(page):
        if not await _wait_for_captcha_resolution(page, timeout_s=180):
            return {"success": False, "error": "CAPTCHA timed out on login page"}

    email_input = await page.wait_for_selector(
        "input#email, input[name='email'], input[type='email']", timeout=10000
    )
    if not email_input:
        return {"success": False, "error": "Email input not found"}

    await _human_type(email_input, email)
    await asyncio.sleep(random.uniform(0.5, 1.2))

    pwd_input = await page.query_selector(
        "input#password, input[name='password'], input[type='password']"
    )
    if not pwd_input:
        return {"success": False, "error": "Password input not found"}

    await _human_type(pwd_input, password)
    await asyncio.sleep(random.uniform(0.5, 1.0))

    submit_btn = await page.query_selector(
        "#login_submit, button[type='submit'], button:has-text('Login'), input[type='submit']"
    )
    if not submit_btn:
        return {"success": False, "error": "Login submit not found"}

    await page.evaluate("function(el) { el.click(); }", submit_btn)
    await asyncio.sleep(2)

    if await _has_captcha(page):
        if not await _wait_for_captcha_resolution(page, timeout_s=180):
            return {"success": False, "error": "CAPTCHA timed out after login"}

    await asyncio.sleep(random.uniform(4, 7))
    current_url = page.url

    if "verify" in current_url or "otp" in current_url.lower():
        return {"success": False, "error": "OTP verification required. Log in manually and run save_cookies.py."}

    if await _is_logged_in(page):
        logger.info("Login successful")
        return {"success": True}

    # Log debug info for failed login
    logger.warning("Login failed - checking page state", 
                   url=current_url,
                   has_captcha=await _has_captcha(page),
                   page_title=await page.title())
    await _screenshot(page, "login_failed")
    
    return {"success": False, "error": "Login failed — check credentials. Run save_cookies.py to login manually."}


def _next_join_date() -> str:
    d = datetime.now(timezone.utc) + timedelta(days=30)
    return d.strftime("%d/%m/%Y")


# ─────────────────────────────────────────────────────────────────────────────
#  ALREADY-APPLIED CHECK  (scoped — avoids false positives from page body text)
# ─────────────────────────────────────────────────────────────────────────────

async def _is_already_applied(page) -> bool:
    """
    Return True ONLY when Internshala's own per-internship status badge shows
    the current user has already applied.
    """
    try:
        # 1. Check scoped action area first (most reliable)
        action_area = await page.query_selector(
            ".internship_apply, .apply-button-container, "
            ".application-actions, .job-apply-section, "
            ".apply-now-button, #apply-section, .button_container"
        )
        if action_area:
            area_text = (await action_area.inner_text() or "").lower()
            # Look for explicit badges or button state inside the action area
            if any(p in area_text for p in ["applied", "you have applied", "already applied"]):
                # Confirm it's not "apply now" or similar
                if "apply now" not in area_text:
                    logger.info("Already-applied indicator found in action area")
                    return True

        # 2. Check for specific badges anywhere, but with more precise selectors
        badge = await page.query_selector(
            ".already-applied, .applied-badge, .application-status-applied, "
            "span.applied:not(:empty)"
        )
        if badge and await badge.is_visible():
            # Check proximity to known non-job sections (e.g. footer, similar jobs)
            # This is hard to do perfectly, so we trust visible badges for now.
            logger.info("Already-applied badge found")
            return True

        # 3. Check official apply buttons specifically
        for btn_sel in ("#easy_apply_button", "#apply_button", "#btn-apply"):
            btn = await page.query_selector(btn_sel)
            if btn:
                btn_text = (await btn.inner_text() or "").strip().lower()
                is_disabled = await btn.get_attribute("disabled") is not None
                if "applied" in btn_text and is_disabled:
                    logger.info("Apply button is disabled with 'Applied' label")
                    return True

        return False
    except Exception as e:
        logger.warning("Error in _is_already_applied", error=str(e))
        return False


# ─────────────────────────────────────────────────────────────────────────────
#  LABEL EXTRACTION
# ─────────────────────────────────────────────────────────────────────────────

async def _get_field_label(page, el_handle) -> str:
    """
    Find the human-readable question label for a form field.
    Handles Internshala's custom_question_text_XXXXXXX pattern where the
    question text is a sibling/cousin several DOM levels up.
    """
    try:
        return await page.evaluate("""
            function(el) {
                // 1. label[for=id]
                if (el.id) {
                    var lbl = document.querySelector('label[for="' + el.id + '"]');
                    if (lbl) return (lbl.innerText || '').trim();
                }

                // 2. Walk previous siblings broadly (not just label tags)
                var sib = el.previousElementSibling;
                var sibDepth = 0;
                while (sib && sibDepth < 5) {
                    var t = (sib.innerText || '').trim();
                    if (t && t.length > 8 && t.length < 500) return t.split('\\n')[0].trim();
                    sib = sib.previousElementSibling;
                    sibDepth++;
                }

                // 3. Walk up DOM — scan each ancestor for question text
                var parent = el.parentElement;
                for (var i = 0; i < 10; i++) {
                    if (!parent) break;

                    // Look for explicit label or question containers
                    var candidates = parent.querySelectorAll(
                        'label, .question-label, .field-label, .custom-question-text, ' +
                        '.question_text, [class*="question"], p, h4, h5, strong, b'
                    );
                    for (var j = 0; j < candidates.length; j++) {
                        var c = candidates[j];
                        if (c === el || c.contains(el)) continue;
                        var ct = (c.innerText || '').trim();
                        if (ct && ct.length > 8 && ct.length < 400) {
                            return ct.split('\\n')[0].trim();
                        }
                    }

                    // Raw parent text (minus inputs) — catches bare text nodes
                    var cloned = parent.cloneNode(true);
                    cloned.querySelectorAll('input, textarea, select, button').forEach(
                        function(n) { n.remove(); }
                    );
                    var parentText = (cloned.innerText || '').trim();
                    if (parentText && parentText.length > 8 && parentText.length < 400) {
                        return parentText.split('\\n')[0].trim();
                    }

                    parent = parent.parentElement;
                }
                return el.placeholder || '';
            }
        """, el_handle)
    except Exception:
        return ""


# ─────────────────────────────────────────────────────────────────────────────
#  JS VALUE SETTER  — sets a field value without requiring visibility
# ─────────────────────────────────────────────────────────────────────────────

async def _js_set_value(page, el_handle, value: str) -> None:
    """
    Set a form field value via JS native setter + fire input/change events.
    Works on both visible and hidden elements (unlike Playwright's fill()
    which requires the element to be visible, enabled, and editable —
    causing a 30-second timeout on hidden fields).
    """
    await page.evaluate(
        """function(args) {
            var el = args[0];
            var val = args[1];
            // Use the native setter so React/Vue internal state also updates
            try {
                var tag = el.tagName.toLowerCase();
                if (tag === 'textarea') {
                    var setter = Object.getOwnPropertyDescriptor(
                        window.HTMLTextAreaElement.prototype, 'value').set;
                    setter.call(el, val);
                } else if (tag === 'input') {
                    var setter = Object.getOwnPropertyDescriptor(
                        window.HTMLInputElement.prototype, 'value').set;
                    setter.call(el, val);
                } else {
                    el.value = val;
                }
            } catch(e) {
                el.value = val;
            }
            el.dispatchEvent(new Event('input', {bubbles: true}));
            el.dispatchEvent(new Event('change', {bubbles: true}));
            el.dispatchEvent(new KeyboardEvent('keyup', {bubbles: true}));
        }""",
        [el_handle, value],
    )


# ─────────────────────────────────────────────────────────────────────────────
#  FILL ALL FORM FIELDS  (visible AND hidden)
# ─────────────────────────────────────────────────────────────────────────────

async def _fill_all_fields(page, profile, resume, settings_obj, profile_summary: str, cover_answer: str, job_context: str = "") -> None:
    """
    Fill every textarea, select, range, text input, and radio — including
    fields that are hidden/collapsed. Internshala validates all required fields
    on submit regardless of visibility.
    Uses JS direct value assignment for hidden fields to avoid Playwright
    fill() timeouts.
    """

    # ── Textareas (ALL — including hidden) ───────────────────────────────────
    for ta in await page.query_selector_all("textarea"):
        try:
            current = (await ta.input_value()).strip()
            if current:
                continue

            label = await _get_field_label(page, ta)
            logger.info("Textarea found", label=(label or "(no label)")[:80])

            if label:
                answer = await _ai_answer(label, [], profile_summary, job_context=job_context)
            else:
                answer = cover_answer

            await _js_set_value(page, ta, answer)
            logger.info("Filled textarea", label=(label or "(no label)")[:60], chars=len(answer))
        except Exception as e:
            logger.warning("Could not fill textarea", error=str(e))

    # ── SELECT dropdowns ──────────────────────────────────────────────────────
    for sel_el in await page.query_selector_all("select"):
        try:
            current_val = await sel_el.evaluate("function(el) { return el.value; }")
            if current_val and current_val not in ("", "0", "Select", "-- Select --"):
                continue

            options_data = await sel_el.evaluate("""
                function(el) {
                    return Array.from(el.options).map(function(o) {
                        return {value: o.value, text: o.text.trim()};
                    });
                }
            """)
            real_options = [
                o for o in options_data
                if o["value"] and o["value"] not in ("", "0", "Select")
                and not o["text"].lower().startswith("select")
                and not o["text"].startswith("--")
            ]
            if not real_options:
                continue

            option_texts = [o["text"] for o in real_options]
            label = await _get_field_label(page, sel_el)
            if not label:
                placeholder_opt = next(
                    (o for o in options_data if not o["value"] or o["value"] in ("", "0")), None
                )
                label = placeholder_opt["text"] if placeholder_opt else "Please select an option"

            logger.info("Select field", label=label[:80], options=option_texts)
            chosen_text = await _ai_answer(label, option_texts, profile_summary, job_context=job_context)

            chosen_value = None
            for o in real_options:
                if o["text"].lower() == chosen_text.lower():
                    chosen_value = o["value"]
                    break
            if not chosen_value:
                for o in real_options:
                    if chosen_text.lower() in o["text"].lower() or o["text"].lower() in chosen_text.lower():
                        chosen_value = o["value"]
                        break
            if not chosen_value:
                chosen_value = real_options[len(real_options) // 2]["value"]

            try:
                # Use short timeout and fallback to JS for hidden/sticky elements
                await sel_el.select_option(value=chosen_value, timeout=2000)
            except Exception:
                await page.evaluate("function(data) { data.el.value = data.val; data.el.dispatchEvent(new Event('change', {bubbles: true})); }", {"el": sel_el, "val": chosen_value})
            
            await page.evaluate(
                "function(el) { el.dispatchEvent(new Event('change', {bubbles:true})); }", sel_el
            )
            logger.info("Selected dropdown", label=label[:60], chosen=chosen_text[:60])
            await asyncio.sleep(0.3)
        except Exception as e:
            logger.warning("Could not fill select", error=str(e))

    # ── Range / number inputs ─────────────────────────────────────────────────
    for inp in await page.query_selector_all("input[type='range'], input[type='number']"):
        try:
            if (await inp.input_value()).strip():
                continue
            label = await _get_field_label(page, inp)
            mn = int(float(await inp.evaluate("function(el) { return el.min || '1'; }") or "1"))
            mx = int(float(await inp.evaluate("function(el) { return el.max || '5'; }") or "5"))
            step = int(float(await inp.evaluate("function(el) { return el.step || '1'; }") or "1"))
            opts = [str(v) for v in range(mn, mx + 1, step)]
            chosen = await _ai_answer(label or "Rate your skill level (1=lowest)", opts, profile_summary, job_context=job_context)
            try:
                cv = max(mn, min(mx, int(float(chosen))))
                chosen = str(cv)
            except Exception:
                chosen = opts[len(opts) // 2]
            await _js_set_value(page, inp, chosen)
            logger.info("Filled range/number", label=(label or "?")[:60], value=chosen)
        except Exception as e:
            logger.warning("Could not fill range input", error=str(e))

    # ── Custom text / url / email inputs ─────────────────────────────────────
    # FIX: Use _js_set_value instead of inp.fill() so hidden inputs don't
    # cause a 30-second Playwright timeout (fill() requires visibility).
    for inp in await page.query_selector_all(
        "input[type='text'], input[type='url'], input[type='email']"
    ):
        try:
            inp_id = await inp.evaluate("function(el) { return el.id || ''; }")
            inp_name = await inp.evaluate("function(el) { return el.name || ''; }")
            inp_type_attr = await inp.evaluate("function(el) { return el.type || 'text'; }")

            # Skip fields handled elsewhere or hidden system fields
            if inp_id in ("last_working_date", "phone_number") or \
               inp_name in ("last_working_date", "phone_number", "phone"):
                continue
            # Skip Internshala internal hidden fields we shouldn't touch
            if inp_id in ("status", "csrf", "csrf_test_name") or \
               inp_name in ("internshipId", "source", "csrf_test_name",
                            "is_sequential_apply_flow", "sequential_apply_referral",
                            "last_applied_application_id", "last_applied_job_profile",
                            "current_job_profile"):
                continue

            if (await inp.input_value()).strip():
                continue

            label = await _get_field_label(page, inp)
            if not label:
                continue  # Can't fill without knowing what the field is asking

            if inp_type_attr == "email":
                from app.core.config import settings as _s
                answer = _s.USER_EMAIL or ""
            elif inp_type_attr == "url" or any(w in label.lower() for w in ("url", "link", "portfolio", "website")):
                answer = (
                    getattr(profile, "portfolio_url", "") or
                    getattr(profile, "github_url", "") or
                    "Available upon request"
                )
            elif "linkedin" in label.lower():
                answer = getattr(profile, "linkedin_url", "") or "Available upon request"
            elif "github" in label.lower():
                answer = getattr(profile, "github_url", "") or "Available upon request"
            else:
                answer = await _ai_answer(label, [], profile_summary, job_context=job_context)

            if answer:
                await _js_set_value(page, inp, str(answer))
                logger.info("Filled text input", label=label[:60], value=str(answer)[:60])
        except Exception as e:
            logger.warning("Could not fill text input", error=str(e))

    # ── Radio buttons ─────────────────────────────────────────────────────────
    radio_groups = await page.evaluate("""
        () => {
            var groups = {};
            document.querySelectorAll('input[type="radio"]').forEach(function(r) {
                var name = r.name || r.id;
                if (!groups[name]) groups[name] = [];
                groups[name].push({id: r.id, value: r.value, checked: r.checked});
            });
            return groups;
        }
    """)
    logger.info("Radio groups", groups=list(radio_groups.keys()))
    for group_name, radios in radio_groups.items():
        if any(r["checked"] for r in radios):
            continue
        target = next(
            (r for r in radios if r["id"] == "radio1" or r["id"].startswith("Yes_")),
            radios[0] if radios else None,
        )
        if not target:
            continue
        try:
            rid = target["id"]
            el = await page.query_selector(f"#{rid}")
            if el:
                lbl = await page.query_selector(f"label[for='{rid}']")
                await (lbl or el).click()
                logger.info("Selected radio", group=group_name, id=rid)
                await asyncio.sleep(0.3)
        except Exception as e:
            logger.warning("Could not click radio", group=group_name, error=str(e))

    # ── Phone ─────────────────────────────────────────────────────────────────
    if profile and profile.phone:
        for sel in ("#phone_number", "input[name='phone_number']", "input[name='phone']", "input[type='tel']"):
            el = await page.query_selector(sel)
            if el and await el.is_visible():
                if not (await el.input_value()).strip():
                    await _human_type(el, profile.phone)
                    logger.info("Filled phone")
                break

    # ── Join date ─────────────────────────────────────────────────────────────
    join_date = _next_join_date()
    for sel in (
        "#last_working_date", "input[name='last_working_date']",
        "input[id*='join']", "input[name*='join']",
        "input[placeholder*='join' i]", "input[placeholder*='latest' i]",
        "input[placeholder*='date' i]",
    ):
        try:
            el = await page.query_selector(sel)
            if el and await el.is_visible():
                if not (await el.input_value()).strip():
                    await el.click()
                    await el.fill(join_date)
                    await page.evaluate(
                        "function(el) { el.dispatchEvent(new Event('input',{bubbles:true})); el.dispatchEvent(new Event('change',{bubbles:true})); }",
                        el,
                    )
                    logger.info("Filled join-date", value=join_date)
                break
        except Exception:
            pass

    # ── Resume upload ─────────────────────────────────────────────────────────
    if resume and resume.file_path:
        resume_path = Path(settings_obj.LOCAL_STORAGE_PATH) / resume.file_path
        if resume_path.exists():
            file_input = await page.query_selector("input[type='file']")
            if file_input:
                await file_input.set_input_files(str(resume_path))
                logger.info("Uploaded resume")
                await asyncio.sleep(2)


# ─────────────────────────────────────────────────────────────────────────────
#  FIND SUBMIT BUTTON
# ─────────────────────────────────────────────────────────────────────────────

async def _find_submit_button(page):
    for container_sel in (
        "#application_form", ".application-modal", "#apply-modal",
        "form[id*='apply']", "form[action*='apply']",
        ".modal.show", ".modal[style*='block']",
    ):
        container = await page.query_selector(container_sel)
        if container:
            for btn_sel in (
                "#submit", "button[type='submit']", "input[type='submit']",
                "button:has-text('Submit')", "button:has-text('Submit Application')",
            ):
                btn = await container.query_selector(btn_sel)
                if btn and await btn.is_visible():
                    logger.info("Found submit", container=container_sel, btn=btn_sel)
                    return btn

    for btn in await page.query_selector_all("button, input[type='submit']"):
        try:
            if not await btn.is_visible():
                continue
            txt = ((await btn.inner_text()) or "").strip().lower()
            if txt in ("apply now", "apply", "easy apply") or len(txt) > 50:
                continue
            if any(w in txt for w in ("submit", "send application", "submit application")):
                logger.info("Found submit by text", txt=txt)
                return btn
        except Exception:
            pass
    return None


# ─────────────────────────────────────────────────────────────────────────────
#  SUCCESS / ERROR DETECTION
# ─────────────────────────────────────────────────────────────────────────────

# Known success phrases Internshala shows after a successful submit
_SUCCESS_SIGNALS = (
    "your application has been submitted",
    "successfully applied",
    "applied successfully",
    "thank you for applying",
    "you have successfully applied",
    "application sent successfully",
    "application has been sent",
    "you have applied",
    "application submitted",
    "recommended internships for you",
    "recommended internships",
    "congratulations",
)


async def _check_submission_result(page, internship_id: Optional[str] = None) -> Optional[dict]:
    """
    Return a success dict if submission succeeded, None if it clearly failed.
    """
    html = (await page.content()).lower()
    url = page.url
    logger.info("Checking submission result", url=url, id=internship_id)

    # 0. Check for explicit success URL redirect
    if "/application_submitted" in url or "application/success" in url or "matching-preferences" in url:
        logger.info("Confirmed via success URL redirect")
        return {"success": True, "ats": "internshala", "verified": True}
    
    modal = await page.query_selector('.modal.show')
    if modal:
        modal_text = (await modal.inner_text() or "").lower()
        
        # 1a. Check for SUCCESS inside modal FIRST
        for sig in _SUCCESS_SIGNALS:
            if sig in modal_text:
                logger.info("Confirmed via modal success text", signal=sig)
                return {"success": True, "ats": "internshala", "verified": True}
        
        # 1b. Check for ERRORS inside modal (more specific keywords to avoid footer links)
        if "invalid job" in modal_text:
            logger.warning("Invalid Job error detected")
            return {"success": False, "error": "Invalid Job - posting may be closed"}
            
        error_keywords = ["error occurred", "please try again", "application failed", "could not submit"]
        for kw in error_keywords:
            if kw in modal_text:
                logger.warning("Explicit error detected in modal", text=modal_text[:100])
                return {"success": False, "error": f"Application failed: {modal_text[:50]}"}
        
        # 1c. If a modal is open but has no clear success/error, it might be the form still being open
        # or a post-apply survey. We continue to other checks.

    # 1. Check for visible success overlays / dedicated confirmation areas
    # We avoid broad 'html' search to prevent false positives from 'Related Internships'
    success_selectors = [
        ".success_modal", ".application_submitted_overlay", "#application_submitted_container",
        ".congrats-modal", ".thank-you-page", ".recommended-internships", "#post-apply-modal"
    ]
    for sel in success_selectors:
        if await page.query_selector(f"{sel}:visible"):
            logger.info("Confirmed via success overlay/selector", selector=sel)
            return {"success": True, "ats": "internshala", "verified": True}

    # 2. Applied badge / button state (SCOPED to current internship if possible)
    # If we have internship_id, we look for indicators near links containing that ID
    if internship_id:
        scoped_indicator = await page.evaluate(f"""
            () => {{
                var id = '{internship_id}';
                // Find any element containing the internship ID in its href (the main detail link or similar)
                var links = Array.from(document.querySelectorAll('a[href*="' + id + '"]'));
                for (var link of links) {{
                    // Traversal: look at siblings or parent containers for "Applied" status
                    var container = link.closest('.internship_meta, .card, .individual_internship, .job-card');
                    if (container) {{
                        var text = (container.innerText || '').toLowerCase();
                        if (text.includes('applied') || text.includes('application submitted')) return true;
                    }}
                }}
                // Final fallback: check any button that has "applied" and is not inside "Similar Internships"
                var applied_btns = Array.from(document.querySelectorAll('button'));
                for (var btn of applied_btns) {{
                    if (btn.innerText.toLowerCase().includes('applied')) {{
                        if (!btn.closest('.similar_internships, #similar_internships')) return true;
                    }}
                }}
                return false;
            }}
        """)
        if scoped_indicator:
            logger.info("Confirmed via scoped applied indicator", id=internship_id)
            return {"success": True, "ats": "internshala", "verified": True}
    else:
        # Fallback to broader check if no ID (not ideal)
        if await page.query_selector(".already-applied, .applied-badge, button:has-text('Applied')"):
            logger.info("Confirmed via fallback applied badge")
            return {"success": True, "ats": "internshala", "verified": True}

    # 3. Success text inside any currently-open modal (confirmation overlay)
    modal_text = await page.evaluate("""
        () => {
            var modal = document.querySelector('.modal.show');
            return modal ? (modal.innerText || '').toLowerCase() : '';
        }
    """)
    for sig in _SUCCESS_SIGNALS:
        if sig in modal_text:
            logger.info("Confirmed via modal text", signal=sig)
            return {"success": True, "ats": "internshala", "verified": True}

    # 4. Application form modal closed (AJAX success, no confirmation overlay)
    for _ in range(16):
        await asyncio.sleep(0.5)
        modal_gone = await page.evaluate("""
            () => {
                var m = document.querySelector('.modal.show');
                if (!m) return true;
                // Modal is open but it's a SUCCESS confirmation — not a form
                var t = (m.innerText || '').toLowerCase();
                return t.includes('applied') || t.includes('submitted') || t.includes('thank you');
            }
        """)
        if modal_gone:
            logger.info("Confirmed — application form modal gone or shows success")
            return {"success": True, "ats": "internshala", "verified": True}

    return {"success": False, "error": "Could not verify application success - check manually"}  # Modal still open with no success signal


async def _get_form_errors(page) -> str:
    """
    Extract validation error messages from the open application modal.

    FIX: The original code used Python adjacent string literals inside the JS
    string:
        var selector = (
            '.error-message, ...'   ← first string
            '[class*="error"], ...' ← second string, adjacent — Python joins,
        );                            but JS sees two tokens → SyntaxError
    Fixed by using a single unbroken string for the selector.
    """
    return await page.evaluate("""
        () => {
            var modal = document.querySelector('.modal.show');
            if (!modal) return '';
            var selector = '.error-message, .field-error, .invalid-feedback, [class*="error"], [style*="color: red"], [style*="color:red"]';
            var msgs = [];
            modal.querySelectorAll(selector).forEach(function(el) {
                var t = (el.innerText || '').trim();
                if (t && t.length < 300) msgs.push(t);
            });
            return msgs.join(' | ');
        }
    """)


# ─────────────────────────────────────────────────────────────────────────────
#  FILL + SUBMIT (with one retry on validation error)
# ─────────────────────────────────────────────────────────────────────────────

async def _fill_application_form(
    page, profile, resume, settings_obj,
    internship_id=None, job_title_for_verify=None, job=None,
) -> dict:
    await _screenshot(page, "application_form_open")
    await asyncio.sleep(2)

    profile_summary = _build_profile_summary(profile, job=job)

    # Build a concise job context string passed to every AI answer call
    # so answers reference the actual role, not placeholder text
    job_context_parts = []
    if job:
        if getattr(job, 'title', None):
            job_context_parts.append(f"Role: {job.title}")
        if getattr(job, 'company_name', None):
            job_context_parts.append(f"Company: {job.company_name}")
        # Include a snippet of the job description so AI can write specific answers
        desc = getattr(job, 'description_clean', None) or getattr(job, 'description_raw', None) or ""
        if desc:
            job_context_parts.append(f"Description excerpt:\n{desc[:800]}")
    job_context = "\n".join(job_context_parts)

    cover_answer = (
        profile.professional_summary[:500]
        if profile and profile.professional_summary
        else (
            "I am a motivated and quick learner with strong interest in this role. "
            "I am eager to contribute my skills and grow professionally through this internship."
        )
    )

    await asyncio.sleep(1.5)

    # Log all fields
    form_content = await page.evaluate("""
        () => {
            var fields = [];
            document.querySelectorAll('textarea, input, select').forEach(function(el) {
                fields.push({
                    tag: el.tagName, type: el.type || '',
                    name: el.name || '', id: el.id || '',
                    placeholder: el.placeholder || '',
                    required: el.required,
                    visible: el.offsetParent !== null
                });
            });
            return fields;
        }
    """)
    logger.info("Total form fields (visible + hidden)", count=len(form_content))
    for f in form_content:
        logger.info("  field", tag=f["tag"], type=f["type"], name=f["name"],
                    id=f["id"], visible=f["visible"], required=f["required"])

    await _fill_all_fields(page, profile, resume, settings_obj, profile_summary, cover_answer, job_context=job_context)

    await asyncio.sleep(1)
    await _screenshot(page, "before_submit")

    submit_btn = await _find_submit_button(page)
    if not submit_btn:
        await _screenshot(page, "no_submit_found")
        return {"success": False, "error": "No submit button found in application form"}

    # First submit attempt
    await page.evaluate(
        "function(el) { el.scrollIntoView({block:'center'}); el.click(); }", submit_btn
    )
    await asyncio.sleep(2)

    if await _has_captcha(page):
        if not await _wait_for_captcha_resolution(page, timeout_s=180):
            return {"success": False, "captcha": True, "error": "reCAPTCHA on submit"}

    await asyncio.sleep(random.uniform(3, 5))
    await _screenshot(page, "after_submit")

    result = await _check_submission_result(page, internship_id=internship_id)
    if result:
        return result

    # Modal still open — re-fill newly-visible fields and retry once
    error_msg = await _get_form_errors(page)
    logger.warning("Submit failed — refilling and retrying", errors=(error_msg or "none")[:200])

    await _fill_all_fields(page, profile, resume, settings_obj, profile_summary, cover_answer, job_context=job_context)
    await asyncio.sleep(1)
    await _screenshot(page, "before_retry_submit")

    submit_btn2 = await _find_submit_button(page)
    if submit_btn2:
        await page.evaluate(
            "function(el) { el.scrollIntoView({block:'center'}); el.click(); }", submit_btn2
        )
        await asyncio.sleep(random.uniform(3, 5))
        await _screenshot(page, "after_retry_submit")
        result = await _check_submission_result(page, internship_id=internship_id)
        if result:
            return result

    final_error = await _get_form_errors(page)
    await _screenshot(page, "submit_failed_final")
    return {
        "success": False,
        "error": f"Form submission failed: {final_error[:150] if final_error else 'unknown reason'}",
    }


# ─────────────────────────────────────────────────────────────────────────────
#  MAIN ENTRY POINT
# ─────────────────────────────────────────────────────────────────────────────

async def apply_internshala(page, job, profile, resume, settings_obj, user_id: Optional[str] = None) -> dict:
    context = page.context

    # First try to load from file (legacy)
    cookies = _load_cookies()
    
    # If no file cookies, try to load from database
    if not cookies and user_id:
        try:
            from app.services.cookie_service import cookie_service
            cookies = await cookie_service.get_cookies(user_id, "internshala")
            if cookies:
                logger.info("Loaded cookies from database", count=len(cookies))
        except Exception as e:
            logger.warning("Could not load cookies from database", error=str(e))
    
    if cookies:
        try:
            await context.add_cookies(cookies)
            logger.info("Injected cookies", count=len(cookies))
        except Exception as e:
            logger.warning("Could not inject cookies", error=str(e))

    await page.goto("https://internshala.com/", wait_until="domcontentloaded", timeout=30000)
    await asyncio.sleep(random.uniform(2, 3))
    await _dismiss_blocking_modals_only(page)

    logged_in = await _is_logged_in(page)
    if not logged_in:
        await page.reload(wait_until="domcontentloaded")
        await asyncio.sleep(2)
        logged_in = await _is_logged_in(page)

    if not logged_in:
        email = getattr(settings_obj, "INTERNShALA_EMAIL", "")
        password = getattr(settings_obj, "INTERNShALA_PASSWORD", "")
        if not email or not password:
            return {"success": False, "error": "Not logged in. Run save_cookies.py."}
        result = await _do_login(page, email, password)
        if not result["success"]:
            return result
        await _save_cookies(context)

    logger.info("Logged in", status=True)

    # Extract internship ID from URL — handles three URL formats:
    #   /internships/detail/3086913               → pure numeric
    #   /internship/detail/...at-company1773918293 → slug with trailing digits
    #   /internships/detail/isp_v_57              → short slug (no 7-digit number)
    slug = job.source_url.rstrip("/").split("/")[-1]
    nums = re.findall(r"\d{7,}", slug)
    if nums:
        internship_id = nums[-1]   # last 7+ digit number in slug
    else:
        # Fewer-digit numeric ID (e.g. 3086913) or slug like isp_v_57
        nums6 = re.findall(r"\d{6,}", slug)
        if nums6:
            internship_id = nums6[-1]
        else:
            internship_id = slug   # use full slug — href matching still works
    logger.info("Internship ID extracted", internship_id=internship_id, slug=slug)

    logger.info("Loading detail page", url=job.source_url)
    await page.goto(job.source_url, wait_until="networkidle", timeout=45000)

    await asyncio.sleep(2)
    
    # First check if we got an error/crashed page instead of job content
    raw_html = await page.content()
    raw_lower = raw_html.lower()
    logger.debug("raw_html length", length=len(raw_html))
    
    # Check for error/crashed/bot detection pages
    error_indicators = [
        "access denied", "blocked", "suspicious activity",
        "rate limit", "too many requests", "captcha",
        "verify you are human", "cloudflare", 
        "something went wrong", "server error", "500",
        "we're sorry", "page not found", "404"
    ]
    
    # Check for employer blocked modal specifically - employer has closed applications
    if "employer_blocked_error_modal" in raw_lower:
        logger.debug("Found employer_blocked_error_modal")
        blocked_modal = await page.query_selector("#employer_blocked_error_modal")
        if blocked_modal:
            is_visible = await blocked_modal.is_visible()
            logger.debug("blocked_modal visible", is_visible=is_visible)
            if is_visible:
                modal_text = await blocked_modal.inner_text()
                logger.debug("Blocked modal text", modal_text=modal_text[:200])
                return {"success": False, "error": "Employer has closed applications for this internship"}
    
    # Check for rate limiting
    if "too many requests" in raw_lower:
        logger.warning("Detected rate limiting")
        return {"success": False, "error": "Internshala rate limiting - try again later"}

    try:
        await page.wait_for_selector(
            ".internship_details, #internship_detail_container, "
            ".detail_view, .job-detail, [class*='internship-detail'], "
            ".internship-overview-main-container",
            timeout=10000,
        )
        logger.info("Job content loaded")
    except Exception:
        logger.warning("Job content container not found — proceeding anyway")

    await asyncio.sleep(2)
    await _dismiss_blocking_modals_only(page)
    await asyncio.sleep(0.5)
    await _dismiss_blocking_modals_only(page)

    if await _is_on_login_wall(page):
        return {"success": False, "error": "Session expired. Run save_cookies.py."}

    await _screenshot(page, "detail_page")

    # Scoped already-applied check
    if await _is_already_applied(page):
        logger.info("Already applied — skipping")
        return {
            "success": True, "already_applied": True,
            "ats": "internshala", "verified": True,
            "note": "Already applied — DB synced, no new submission",
        }

    html_check = (await page.content()).lower()
    logger.debug("html_check length", length=len(html_check))
    logger.debug("html_check eligibility check", not_eligible=('not eligible' in html_check))
    
    # Check for explicit eligibility rejection - look for specific banner/text
    # The message "As your Internshala resume lists X as your location, you are not eligible" is the key indicator
    eligibility_rejection_patterns = [
        "as your internshala resume lists",
        "you are not eligible for this internship",
        "you're not eligible for this internship",
        "you do not meet the eligibility criteria for this internship",
    ]
    
    # Check if there's a visible rejection message in the eligibility section
    try:
        who_can_apply = await page.query_selector('.who_can_apply, .eligibility-section, [class*="who_can"]')
        if who_can_apply:
            section_text = (await who_can_apply.inner_text() or "").lower()
            logger.debug("who_can_apply section eligibility check", not_eligible=('not eligible' in section_text))
            if "as your internshala resume lists" in section_text:
                logger.debug("Location-based ineligibility detected")
                return {"success": False, "ineligible": True, "error": "Not eligible - profile location does not match job requirements"}
    except Exception as e:
        logger.debug("Error checking eligibility section", error=str(e))
    
    # Check for eligibility banner element
    eligibility_banner = await page.query_selector(
        ".not-eligible, .ineligible, [class*='not-eligible'], [class*='ineligible']"
    )
    logger.debug("eligibility_banner state", found=(eligibility_banner is not None))
    if eligibility_banner:
        is_visible = await eligibility_banner.is_visible()
        logger.debug("eligibility_banner visible", is_visible=is_visible)
        if is_visible:
            banner_text = await eligibility_banner.inner_text() or ""
            logger.debug("banner_text", text=banner_text[:100])
            logger.warning("Eligibility banner found - marking as ineligible", text=banner_text[:200])
            return {"success": False, "ineligible": True, "error": "Not eligible - Internshala profile requirements not met"}
    
    if any(x in html_check for x in (
        "hiring closed", "no longer accepting", "internship closed", "applications closed"
    )):
        return {"success": False, "error": "Internship is no longer accepting applications"}

    # Find Apply button (poll up to 10 s)
    apply_btn = None
    
    # Debug: get page content for analysis
    page_html = await page.content()
    logger.info("Page content length for debug", length=len(page_html))
    
    # Check if already applied via scoped check
    if await _is_already_applied(page):
        logger.info("User already applied to this internship")
        return {"success": True, "already_applied": True, "ats": "internshala", "verified": True}
    
    for attempt in range(20):
        for link in await page.query_selector_all("a[href]"):
            href = await link.get_attribute("href") or ""
            if internship_id in href and "apply" in href:
                apply_btn = link
                logger.info("Found apply link by href+id", href=href)
                break
        if not apply_btn:
            for btn_id in ("easy_apply_button", "apply_button", "btn-apply", "apply_now_button", "apply-button", "easy-apply"):
                el = await page.query_selector(f"#{btn_id}")
                if el and await el.is_visible():
                    apply_btn = el
                    logger.info("Found apply button by ID", id=btn_id)
                    break
        if not apply_btn:
            for sel in (
                "button:has-text('Easy Apply')", "a:has-text('Apply Now')",
                "button:has-text('Apply Now')", "a:has-text('Easy Apply')",
                # Additional Internshala-specific selectors
                "a.button_apply_big", "a.apply-button",
                "button[type='submit']:has-text('Apply')",
                "a:has-text('Apply for this internship')",
                "button:has-text('Apply for this internship')",
                "a.cta-button", "button.cta-button",
                # More Internshala selectors based on current UI
                "a[id*='apply']", "button[id*='apply']",
                ".apply-now-btn", ".applyButton", ".apply_btn",
                "a[class*='apply']", "button[class*='apply']",
                # Generic fallback
                ".apply-btn", ".application-btn", "[class*='apply-button']",
                "[data-testid*='apply']", "button[data-testid*='apply']",
            ):
                el = await page.query_selector(sel)
                if el and await el.is_visible() and len(((await el.inner_text()) or "").strip()) < 30:
                    apply_btn = el
                    logger.info("Found apply button by text", selector=sel)
                    break
        if apply_btn:
            break
        await asyncio.sleep(0.5)
        if attempt == 5:
            await _dismiss_blocking_modals_only(page)
        if attempt == 10:
            # Debug: get the action area HTML
            action_area = await page.query_selector(
                ".internship_details_container, .job-detail-ctc, .detail-view, main"
            )
            if action_area:
                logger.info("Action area found, taking debug screenshot")
                await page.screenshot(path=str(SCREENSHOT_DIR / f"debug_apply_{internship_id}.png"))

    if not apply_btn:
        await _screenshot(page, "no_apply_button")
        return {"success": False, "error": "No Apply button found on detail page"}

    # Check if button is disabled with specific message before trying to click
    btn_text = ((await apply_btn.inner_text()) or "").strip().lower()
    is_disabled = await apply_btn.get_attribute("disabled")
    
    logger.info("Checking apply button state", text=btn_text[:100], has_disabled_attr=is_disabled is not None)
    
    # DEBUG: Log the full button HTML for analysis
    btn_html = (await apply_btn.evaluate("function(el) { return el.outerHTML; }")) or ""
    logger.info("Apply button HTML", html=btn_html[:500])
    
    # Check for "already applied" on button text (this is scoped to the button we found)
    if "already applied" in btn_text or (is_disabled and "applied" in btn_text):
        logger.info("Already applied to this internship (detected on button)")
        return {"success": True, "already_applied": True, "ats": "internshala", "verified": True}
    
    # Check for "closed" state - don't try to click if closed
    closed_phrases = ["closed", "no longer accepting", "not accepting"]
    if any(p in btn_text for p in closed_phrases):
        logger.warning("Internship is closed for applications", text=btn_text)
        return {"success": False, "error": "Internship is closed for applications"}
    
    # Check if button shows "not eligible" - return ineligible immediately
    btn_text_lower = btn_text.lower()
    logger.debug("Button text", text=btn_text)
    logger.debug("Button disabled", is_disabled=is_disabled)
    logger.debug("Button eligibility check", not_eligible=('not eligible' in btn_text_lower))
    
    # Check ALL possible places that could return ineligible
    # First check the button text
    if "not eligible" in btn_text_lower:
        logger.debug("Returning ineligible from button text check")
        logger.warning("Button shows 'not eligible' - marking as ineligible immediately")
        return {"success": False, "ineligible": True, "error": "Not eligible - Internshala profile requirements not met"}
    
    # Check for other blocked states - button might show different text when disabled
    blocked_phrases = ["sign in to apply", "login to apply", "register to apply"]
    if any(phrase in btn_text for phrase in blocked_phrases):
        logger.warning("Button shows login required - checking session")
        # Try to see if this is a login wall - reload and check
        await page.reload(wait_until="networkidle")
        await asyncio.sleep(2)
        if await _is_on_login_wall(page):
            return {"success": False, "error": "Session expired. Run save_cookies.py."}
        return {"success": False, "ineligible": True, "error": "Login required to apply"}
    
    # Check if button is disabled but not "not eligible" - still try to click
    if is_disabled is not None:
        logger.warning("Button is disabled but not showing 'not eligible' - will attempt click anyway")
        btn_was_disabled = True
    else:
        btn_was_disabled = False

    # Skip waiting loop for disabled buttons - go directly to click attempt
        # Try to scroll button into view and wait for it to be enabled
        try:
            await apply_btn.scroll_into_view_if_needed()
            await page.evaluate("function(el) { el.scrollIntoView({behavior: 'smooth', block: 'center'}); }", apply_btn)
            await asyncio.sleep(2)
            
            # Wait for button to be enabled (max 10 seconds)
            button_clicked = False
            for wait_attempt in range(20):
                is_disabled = await apply_btn.get_attribute("disabled")
                is_enabled = await apply_btn.is_enabled()
                
                if is_enabled and not is_disabled:
                    logger.info("Apply button is now enabled")
                    break
                
                # If button has "apply" text and looks like the right button, try JS click anyway
                btn_text = ((await apply_btn.inner_text()) or "").lower()
                if "apply" in btn_text and len(btn_text) < 30:
                    logger.info("Button has apply text but reports disabled - attempting JS click anyway")
                    break
                    
                # If button was disabled with "not eligible", still try JS click after waiting
                if btn_was_disabled and wait_attempt >= 5:
                    logger.info("Button still disabled but enough waiting - trying JS click")
                    break
                    
                logger.info("Apply button not ready, waiting...", is_enabled=is_enabled, is_disabled=is_disabled)
                await asyncio.sleep(0.5)
        except Exception as e:
            logger.warning("Could not wait for button enablement", error=str(e))

    href = await apply_btn.get_attribute("href") or ""
    logger.info("Apply button", href=href)

    # Check for external redirect URLs - these are NOT Internshala applications
    external_domains = ["appcast.io", ".applytojob", "careerbliss", "indeed", "linkedin", "glassdoor", "naukri", "monster"]
    if href and any(domain in href.lower() for domain in external_domains):
        logger.warning("External application URL detected - skipping", url=href)
        return {"success": False, "error": "External job posting - requires manual application", "external": True}

    if href and href not in ("#", "") and "javascript" not in href:
        full_url = href if href.startswith("http") else f"https://internshala.com{href}"
        logger.info("Navigating to apply URL", url=full_url)
        await page.goto(full_url, wait_until="networkidle", timeout=45000)
        await asyncio.sleep(2)
        await _dismiss_blocking_modals_only(page)
    else:
        logger.info("Clicking Apply (AJAX modal)")
        await asyncio.sleep(1)
        
        # Try multiple click methods - more aggressive approach
        click_success = False
        
        # 1. First try clicking WITHOUT force (normal behavior)
        try:
            await apply_btn.click(timeout=3000)
            click_success = True
            logger.info("Regular click succeeded")
        except Exception as e:
            logger.warning("Regular click failed, trying with force", error=str(e))
            try:
                await apply_btn.click(force=True, timeout=3000)
                click_success = True
                logger.info("Force click succeeded")
            except Exception as e2:
                logger.warning("Force click also failed", error=str(e2))
        
        # 2. If regular click didn't work, try JS clicks
        if not click_success:
            try:
                await page.evaluate("(btn) => btn.click()", apply_btn)
                click_success = True
                logger.info("JS click succeeded")
            except Exception as js_e:
                logger.warning("JS click failed", error=str(js_e))
        
        # 3. Try dispatchEvent as last resort
        if not click_success:
            try:
                await page.evaluate("""(btn) => {
                    btn.dispatchEvent(new MouseEvent('click', {bubbles: true, cancelable: true, view: window}));
                }""", apply_btn)
                click_success = True
                logger.info("dispatchEvent click succeeded")
            except Exception as de:
                logger.warning("dispatchEvent click failed", error=str(de))
        
        # 4. Last resort - directly navigate to apply URL if we can extract it
        if not click_success:
            # Try to get the href and navigate directly
            apply_href = await apply_btn.get_attribute("href")
            if apply_href and apply_href != "#":
                logger.info("Click failed, but found href - navigating directly", href=apply_href)
                if not apply_href.startswith("http"):
                    apply_href = "https://internshala.com" + apply_href
                await page.goto(apply_href, wait_until="networkidle", timeout=45000)
                click_success = True
                logger.info("Navigated to apply URL successfully")
        
        await asyncio.sleep(3)
        
        # Check what's on the page after clicking
        page_content = await page.content()
        page_html = page_content.lower() if page_content else ""
        current_url = page.url
        
        logger.info("After click", url=current_url, has_not_eligible="not eligible" in page_html)
        
        # Check if navigation happened (some internships navigate to a new page)
        if "apply" in current_url or "application" in current_url:
            logger.info("URL changed to application page")
            # This is good - we're on the application form page
            modal_opened = True
        else:
            # Check if any modal or form appeared
            modal_opened = False
            has_error = False
            checked_without_form = 0
            
            for check_num in range(30):  # Longer wait
                await asyncio.sleep(0.5)
                
                # Check for any application form
                modal = await page.query_selector(
                    "#application_form, .application-modal, form[id*='apply'], "
                    ".modal.show form, .modal[style*='block'] form, .apply-modal, #easy-apply-modal, .application-form-container"
                )
                visible_tas = [ta for ta in await page.query_selector_all("textarea") if await ta.is_visible()]
                
                # Also check for any form with inputs
                visible_inputs = await page.query_selector_all("input:not([type='hidden'])")
                visible_inputs = [inp for inp in visible_inputs if await inp.is_visible()]
                
                logger.info(f"Modal check #{check_num}", modal=bool(modal), textareas=len(visible_tas), inputs=len(visible_inputs))
                
                if modal or visible_tas or len(visible_inputs) > 3:
                    modal_opened = True
                    logger.info("Application modal/form opened", inputs=len(visible_inputs))
                    break
                
                # If no form found after several checks, try refreshing the page - sometimes form loads after a moment
                if check_num >= 10 and not modal_opened and checked_without_form == 0:
                    checked_without_form += 1
                    logger.info("No form found after 10 checks - refreshing page")
                    await page.reload(wait_until="networkidle")
                    await asyncio.sleep(2)
                    
                # Last resort: if still no form after 25 checks, try direct navigation to apply page
                if check_num >= 25 and not modal_opened:
                    # Try to get the current job URL and navigate to apply directly
                    current_url = page.url
                    if "internshala.com/internship/detail/" in current_url:
                        apply_url = current_url.replace("/internship/detail/", "/internship/apply/") + "/"
                        logger.info("No modal found - trying direct navigate to apply URL", url=apply_url)
                        try:
                            await page.goto(apply_url, wait_until="networkidle", timeout=30000)
                            await asyncio.sleep(3)
                            
                            # Check what we got on the direct apply page
                            page_content = await page.content()
                            has_form = "<form" in page_content.lower()
                            has_not_eligible = "not eligible" in page_content.lower()
                            
                            logger.info("Direct navigation result", url=apply_url, has_form=has_form, has_not_eligible=has_not_eligible)
                            
                            form_after_nav = await page.query_selector("form")
                            if form_after_nav:
                                logger.info("Form found after direct navigation!")
                                modal_opened = True
                                break
                            elif has_not_eligible:
                                # Even if no form, if page says not eligible, we know the answer
                                logger.warning("Direct URL shows not eligible - skipping")
                                break
                        except Exception as nav_err:
                            logger.warning("Direct navigation failed", error=str(nav_err))
                    
                # Check for error messages
                error_elements = await page.query_selector_all(
                    ".error-message, .alert-danger, [class*='error'], .warning-message, .not-eligible, [class*='not-eligible']"
                )
                # Check for visible error elements (but don't fail immediately)
                has_error = False
                for err in error_elements:
                    if await err.is_visible():
                        err_text = (await err.inner_text()) or ""
                        logger.warning("Error element found after click", text=err_text[:100])
                        has_error = True
            
            if not modal_opened:
                await _screenshot(page, "modal_did_not_open")
                return {"success": False, "error": "Application modal did not open after clicking Apply"}

    if await _is_on_login_wall(page):
        return {"success": False, "error": "Login wall after apply click. Session expired."}

    return await _fill_application_form(
        page, profile, resume, settings_obj,
        internship_id=internship_id,
        job_title_for_verify=(getattr(job, "title", "") or "").lower()[:25],
        job=job,
    )