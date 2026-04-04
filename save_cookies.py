#!/usr/bin/env python3
"""Save Internshala cookies after manual login."""

import asyncio
from playwright.async_api import async_playwright
import json
from pathlib import Path

async def main():
    print("="*60)
    print("INSTRUCTIONS:")
    print("1. A browser will open - go to internshala.com and login")
    print("2. After login, wait 5 seconds")
    print("3. Press Enter in this terminal to save cookies")
    print("="*60)
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        
        await page.goto("https://internshala.com/login/user")
        
        # Wait for user to login
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