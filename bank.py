"""
Bank Portal Opener — opens session, stops for manual action.
"""

import asyncio
import random
from playwright.async_api import BrowserContext
from playwright_stealth import stealth_async
from config import BANK_URL, BANK_USER, BANK_PASS


async def open_bank(context: BrowserContext):
    if not BANK_URL or not BANK_USER or not BANK_PASS:
        print("[bank] Bank credentials not set in vault — skipping.")
        return None

    print(f"[bank] Opening bank portal: {BANK_URL}")
    page = await context.new_page()
    await stealth_async(page)

    try:
        await page.goto(BANK_URL, timeout=30000)
        await asyncio.sleep(random.uniform(1.5, 3.0))

        for selector in ['input[name="usuario"]', 'input[name="username"]', 'input[type="text"]']:
            try:
                await page.wait_for_selector(selector, timeout=5000)
                await page.fill(selector, BANK_USER)
                break
            except Exception:
                continue

        await asyncio.sleep(random.uniform(0.8, 1.5))

        for selector in ['input[name="password"]', 'input[name="clave"]', 'input[type="password"]']:
            try:
                await page.wait_for_selector(selector, timeout=5000)
                await page.fill(selector, BANK_PASS)
                break
            except Exception:
                continue

        await asyncio.sleep(random.uniform(0.5, 1.2))

        for selector in ['button[type="submit"]', 'input[type="submit"]', 'button[id*="ingresar"]']:
            try:
                await page.click(selector, timeout=5000)
                break
            except Exception:
                continue

        await asyncio.sleep(random.uniform(2.0, 3.5))
        print(f"[bank] Portal opened. URL: {page.url}")
        print("[bank] Agent stopped — complete verification manually.")

    except Exception as e:
        print(f"[bank] Error: {e}")

    return page
