#!/usr/bin/env python3
"""Quick debug script to see what's happening on Internshala job page."""

import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124.0.0.0 Safari/537.36",
            viewport={"width": 1366, "height": 768},
        )
        page = await context.new_page()
        
        import json
        from pathlib import Path
        cookie_file = Path(__file__).parent.parent / "storage" / "internshala_cookies.json"
        
        # Load cookies from database (like the real bot does)
        cookies = None
        try:
            from app.services.cookie_service import cookie_service
            # Try to get cookies from DB for the test user
            cookies = await cookie_service.get_cookies('364c6ba3-8669-4f9a-bd50-577322459d4d', 'internshala')
            if cookies:
                print(f"Loaded {len(cookies)} cookies from database")
        except Exception as e:
            print(f"Could not load cookies from DB: {e}")
        
        # Fall back to file if no DB cookies
        if not cookies:
            try:
                if cookie_file.exists():
                    cookies = json.loads(cookie_file.read_text())
                    print(f"Loaded {len(cookies)} cookies from file")
            except Exception as e:
                print(f"Could not load cookies from file: {e}")
        
        if cookies:
            try:
                await context.add_cookies(cookies)
                print(f"Applied {len(cookies)} cookies to context")
            except Exception as e:
                print(f"Error adding cookies: {e}")
        
        # Go to internshala home first to check login
        await page.goto("https://internshala.com/", wait_until="networkidle", timeout=30000)
        await asyncio.sleep(2)
        
        # Check login status - try multiple methods
        login_text = await page.query_selector("text=Logout, text=Sign Out")
        print(f"Logout button found: {login_text is not None}")
        
        # Check for profile elements
        profile_img = await page.query_selector("#header-profile-img, .profile-header, .user-profile")
        print(f"Profile element found: {profile_img is not None}")
        
        # Check URL
        print(f"Current URL: {page.url}")
        
        # If we're on the student dashboard, we ARE logged in
        is_logged_in = "/student/" in page.url
        print(f"Logged in (via URL): {is_logged_in}")
        
        # Go to job page
        job_url = "https://internshala.com/internship/detail/artificial-intelligence-ai-internship-in-jaipur-at-lawdocs1774980778"
        print(f"Loading: {job_url}")
        await page.goto(job_url, wait_until="networkidle", timeout=45000)
        await asyncio.sleep(3)
        
        # Get the apply button
        print("\n=== Looking for apply button ===")
        apply_btn = None
        
        # Try various selectors
        selectors = [
            "#easy_apply_button", "#apply_button", "button:has-text('Easy Apply')",
            "a:has-text('Apply Now')", "button:has-text('Apply Now')",
            "a.button_apply_big", ".apply-now-btn",
        ]
        
        for sel in selectors:
            el = await page.query_selector(sel)
            if el:
                is_visible = await el.is_visible()
                btn_text = (await el.inner_text() or "").strip()
                print(f"Found: {sel}")
                print(f"  Text: '{btn_text}'")
                print(f"  Visible: {is_visible}")
                print(f"  Disabled: {await el.get_attribute('disabled')}")
                
                # Get full HTML
                html = await el.evaluate("el => el.outerHTML")
                print(f"  HTML: {html[:300]}")
                apply_btn = el
                break
        
        if apply_btn:
            # First dismiss any blocking modals
            print("\n=== Dismissing blocking modals ===")
            await page.evaluate("""
                () => {
                    // Remove modal backdrops first
                    document.querySelectorAll('.modal-backdrop.show').forEach(function(el) {
                        el.remove();
                    });
                    
                    // Handle generic aria-modal dialogs
                    document.querySelectorAll('[role="dialog"][aria-modal="true"]').forEach(function(dialog) {
                        var closeBtn = dialog.querySelector('[aria-label="Close"], .close, .modal-close, button[class*="close"]');
                        if (closeBtn) {
                            closeBtn.click();
                        } else {
                            dialog.remove();
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
            await asyncio.sleep(1)
            
            # Try clicking and see what happens
            print("\n=== Clicking apply button ===")
            await apply_btn.click()
            await asyncio.sleep(3)
            
            # Check URL after click
            print(f"URL after click: {page.url}")
            
            # Check if modal opened
            modal = await page.query_selector("#application_form, .application-modal, form[id*='apply'], .modal.show")
            print(f"Modal found: {modal is not None}")
            
            # Check for form fields
            textareas = await page.query_selector_all("textarea")
            print(f"Textareas on page: {len(textareas)}")
            
            inputs = await page.query_selector_all("input")
            print(f"Inputs on page: {len(inputs)}")
            
            # Check for any error messages
            errors = await page.query_selector_all(".error, .alert, [class*='error'], [class*='alert']")
            for err in errors:
                if await err.is_visible():
                    print(f"Error: {await err.inner_text()[:100]}")
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())