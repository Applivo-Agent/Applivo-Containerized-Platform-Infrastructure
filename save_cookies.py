#!/usr/bin/env python3
"""Save Internshala cookies after manual login."""

import asyncio
from playwright.async_api import async_playwright
import json
from pathlib import Path
import os


def _configured_account_email() -> str:
    for key in ("INTERNShALA_EMAIL", "USER_EMAIL"):
        value = os.environ.get(key, "").strip()
        if value and value.lower() not in {"your_email@example.com", "[your_email@example.com]"}:
            return value
    return ""

async def main():
    print("="*60)
    print("INSTRUCTIONS:")
    print("1. A browser will open - go to internshala.com and login")
    print("2. After login, wait 5 seconds")
    print("3. Press Enter in this terminal to save cookies")
    print("="*60)
    
    async with async_playwright() as p:
        # Use a proxy only if explicitly configured in the environment.
        proxy_server = os.environ.get("BROWSER_PROXY_SERVER")
        proxy_user = os.environ.get("BROWSER_PROXY_USER")
        proxy_pass = os.environ.get("BROWSER_PROXY_PASS")
        proxy_config = None
        if proxy_server:
            proxy_config = {"server": proxy_server}
            if proxy_user:
                proxy_config["username"] = proxy_user
            if proxy_pass:
                proxy_config["password"] = proxy_pass

        # Respect headless configuration from environment (default: True)
        headless_env = os.environ.get("BROWSER_HEADLESS")
        headless = True
        if headless_env is not None:
            headless = headless_env.lower() in ("1", "true", "yes")

        browser = await p.chromium.launch(
            headless=headless,
            proxy=proxy_config
        )
        page = await browser.new_page()

        await page.goto("https://internshala.com/login/user")

        # If credentials are provided, attempt an automated login (useful on headless VPS)
        email = _configured_account_email()
        password = os.environ.get("INTERNShALA_PASSWORD")
        if email and password:
            try:
                # Try common selectors for email + password fields and submit
                if await page.query_selector('input[name="email"]'):
                    await page.fill('input[name="email"]', email)
                elif await page.query_selector('input[type="email"]'):
                    await page.fill('input[type="email"]', email)
                elif await page.query_selector('#email'):
                    await page.fill('#email', email)

                if await page.query_selector('input[name="password"]'):
                    await page.fill('input[name="password"]', password)
                elif await page.query_selector('input[type="password"]'):
                    await page.fill('input[type="password"]', password)
                elif await page.query_selector('#password'):
                    await page.fill('#password', password)

                # Try several ways to submit the form
                if await page.query_selector('button[type="submit"]'):
                    await page.click('button[type="submit"]')
                elif await page.query_selector('button:has-text("Login")'):
                    await page.click('button:has-text("Login")')
                elif await page.query_selector('button:has-text("Sign in")'):
                    await page.click('button:has-text("Sign in")')
                else:
                    # fallback: press Enter in password field
                    await page.keyboard.press('Enter')

                # wait for navigation or account indicator
                await page.wait_for_timeout(5000)
            except Exception:
                print("Automated login attempt failed — falling back to manual login flow.")

        # If not using automated login, wait for user to confirm manual login
        if not (email and password):
            print("Manual login mode: open the browser window and login.")
            input("\nPress Enter after you've logged in...")

        await asyncio.sleep(5)  # Extra wait for session to stabilize
        
        # Save cookies
        cookies = await page.context.cookies()
        
        # Fix cookie domains
        for c in cookies:
            if c.get("sameSite") not in ("Strict", "Lax", "None"):
                c["sameSite"] = "Lax"
            if "domain" in c and not c["domain"].startswith("."):
                c["domain"] = "." + c["domain"].lstrip(".")
        
        # Save to file
        storage_path = Path(__file__).parent / "storage"
        storage_path.mkdir(exist_ok=True)
        cookie_file = storage_path / "internshala_cookies.json"
        cookie_file.write_text(json.dumps(cookies, indent=2))
        
        print(f"\nSaved {len(cookies)} cookies to: {cookie_file}")
        print("\nYou can now use the apply bot!")
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())