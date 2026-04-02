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
        answer = resp.choices[0].message.content.strip().strip('"').strip("'")
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
                    return True
            except Exception:
                continue
        
        # Also check page content for logged-in indicators
        content = await page.content()
        if "logout" in content.lower() or "sign out" in content.lower():
            return True
        if "/student/" in content and "login" not in page.url:
            return True
            
        return False
    except Exception:
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
                var hasAppForm = document.querySelector(
                    '#application_form, .application-modal, form[id*="apply"]'
                );
                if (!hasAppForm) {
                    document.querySelectorAll('.modal-backdrop').forEach(function(el) {
                        el.remove();
                    });
                    document.body.classList.remove('modal-open');
                    document.body.style.overflow = 'auto';
                }
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
        badge = await page.query_selector(
            ".already-applied, .applied-badge, "
            "[class*='already_applied'], [class*='already-applied'], "
            "span.applied, .application-status-applied"
        )
        if badge and await badge.is_visible():
            logger.info("Already-applied badge found")
            return True

        for btn_sel in (
            "#easy_apply_button", "#apply_button", "#btn-apply", "button[id*='apply']",
        ):
            btn = await page.query_selector(btn_sel)
            if btn:
                btn_text = (await btn.inner_text() or "").strip().lower()
                btn_disabled = await btn.get_attribute("disabled")
                if "applied" in btn_text and btn_disabled is not None:
                    logger.info("Apply button is disabled with 'Applied' label")
                    return True

        action_area = await page.query_selector(
            ".internship_apply, .apply-button-container, "
            ".application-actions, .job-apply-section, "
            ".apply-now-button, #apply-section"
        )
        if action_area:
            area_text = (await action_area.inner_text() or "").lower()
            if "already applied" in area_text or "you have applied" in area_text:
                logger.info("Already-applied text found in action area")
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

            await sel_el.select_option(value=chosen_value)
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
            txt = (await btn.inner_text()).strip().lower()
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
)


async def _check_submission_result(page) -> dict | None:
    """
    Return a success dict if submission succeeded, None if it clearly failed.

    FIX: After a successful AJAX submit Internshala sometimes opens a NEW
    confirmation/feedback modal that also has class .modal.show.  The old code
    waited for .modal.show to disappear, found it still present (the new modal),
    and returned None — triggering the error path even though the submit worked.

    Now we ALSO scan the HTML for success text before waiting for modal close,
    and we check whether any currently-open modal CONTAINS success text.
    """
    html = (await page.content()).lower()
    url = page.url
    logger.info("Checking submission result", url=url)

    # 1. Success text anywhere on the page
    for sig in _SUCCESS_SIGNALS:
        if sig in html:
            logger.info("Confirmed via page text", signal=sig)
            return {"success": True, "ats": "internshala", "verified": True}

    # 2. Applied badge / button state
    if await page.query_selector(
        ".already-applied, .applied-badge, [class*='already_applied'], "
        "span:has-text('Already Applied'), span:has-text('Application Submitted'), "
        "button:has-text('Applied')"
    ):
        logger.info("Confirmed via applied badge")
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

    return None  # Modal still open with no success signal → failed


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

    result = await _check_submission_result(page)
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
        result = await _check_submission_result(page)
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

async def apply_internshala(page, job, profile, resume, settings_obj) -> dict:
    context = page.context

    cookies = _load_cookies()
    if cookies:
        try:
            await context.add_cookies(cookies)
            logger.info("Loaded cookies", count=len(cookies))
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
    # More specific eligibility checks - look for actual eligibility banners/messages
    if any(x in html_check for x in (
        "you are not eligible for this internship",
        "you're not eligible",
        "you do not meet the eligibility criteria",
        "not_eligible_banner",
        "eligibility-criteria-not-met",
    )):
        return {"success": False, "error": "Not eligible for this internship"}
    # Check for eligibility banner element with specific message
    eligibility_banner = await page.query_selector(
        ".not-eligible, .ineligible, [class*='not-eligible'], [class*='ineligible']"
    )
    if eligibility_banner and await eligibility_banner.is_visible():
        banner_text = await eligibility_banner.inner_text()
        logger.warning("Eligibility banner found", text=banner_text[:200])
        return {"success": False, "error": f"Not eligible: {banner_text.strip()[:150]}"}
    if any(x in html_check for x in (
        "hiring closed", "no longer accepting", "internship closed", "applications closed"
    )):
        return {"success": False, "error": "Internship is no longer accepting applications"}

    # Find Apply button (poll up to 10 s)
    apply_btn = None
    
    # Debug: get page content for analysis
    page_html = await page.content()
    logger.info("Page content length for debug", length=len(page_html))
    
    # Check if already applied
    already_applied = await page.query_selector(
        "text=Already applied, text=Applied, .already-applied, [class*='already-applied']"
    )
    if already_applied:
        logger.info("User already applied to this internship")
        return {"success": True, "message": "Already applied to this internship"}
    
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
                if el and await el.is_visible() and len((await el.inner_text()).strip()) < 30:
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
    btn_text = (await apply_btn.inner_text()).strip().lower()
    is_disabled = await apply_btn.get_attribute("disabled")
    
    logger.info("Checking apply button state", text=btn_text[:100], has_disabled_attr=is_disabled is not None)
    
    # Check for "already applied" first (highest priority)
    if "already applied" in btn_text or "applied" in btn_text:
        logger.info("Already applied to this internship")
        return {"success": True, "already_applied": True, "ats": "internshala", "verified": True}
    
    # Check for "not eligible"
    if "not eligible" in btn_text:
        return {"success": False, "error": "Not eligible for this internship (location or criteria mismatch)"}
    
    # Check if button is disabled for other reasons
    if is_disabled is not None:
        logger.warning("Apply button is disabled", text=btn_text[:100])
        return {"success": False, "error": f"Apply button is disabled: {btn_text[:100]}"}

    # Try to scroll button into view and wait for it to be enabled
    try:
        await apply_btn.scroll_into_view_if_needed()
        await page.evaluate("function(el) { el.scrollIntoView({behavior: 'smooth', block: 'center'}); }", apply_btn)
        await asyncio.sleep(2)
        
        # Wait for button to be enabled (max 10 seconds)
        for wait_attempt in range(20):
            is_disabled = await apply_btn.get_attribute("disabled")
            is_enabled = await apply_btn.is_enabled()
            
            if is_enabled and not is_disabled:
                logger.info("Apply button is now enabled")
                break
            
            # If button has "apply" text and looks like the right button, try JS click anyway
            btn_text = (await apply_btn.inner_text()).lower()
            if "apply" in btn_text and len(btn_text) < 30:
                logger.info("Button has apply text but reports disabled - attempting JS click anyway")
                break
            
            logger.info("Apply button not ready, waiting...", is_enabled=is_enabled, is_disabled=is_disabled)
            await asyncio.sleep(0.5)
    except Exception as e:
        logger.warning("Could not wait for button enablement", error=str(e))

    href = await apply_btn.get_attribute("href") or ""
    logger.info("Apply button", href=href)

    if href and href not in ("#", "") and "javascript" not in href:
        full_url = href if href.startswith("http") else f"https://internshala.com{href}"
        logger.info("Navigating to apply URL", url=full_url)
        await page.goto(full_url, wait_until="networkidle", timeout=45000)
        await asyncio.sleep(2)
        await _dismiss_blocking_modals_only(page)
    else:
        logger.info("Clicking Apply (AJAX modal)")
        try:
            # First try regular click
            await apply_btn.click(timeout=5000)
        except Exception as e:
            logger.warning("Regular click failed, trying JS click", error=str(e))
            try:
                # Fallback to JavaScript click
                await page.evaluate("(btn) => btn.click()", apply_btn)
            except Exception as js_e:
                logger.warning("JS click also failed, trying force click", error=str(js_e))
                # Last resort: force click via evaluate
                await page.evaluate("(btn) => { btn.dispatchEvent(new Event('click', {bubbles: true})); }", apply_btn)
        
        modal_opened = False
        for _ in range(20):
            await asyncio.sleep(0.5)
            modal = await page.query_selector(
                "#application_form, .application-modal, form[id*='apply'], "
                ".modal.show form, .modal[style*='block'] form"
            )
            visible_tas = [ta for ta in await page.query_selector_all("textarea") if await ta.is_visible()]
            if modal or visible_tas:
                modal_opened = True
                logger.info("Application modal opened")
                break
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