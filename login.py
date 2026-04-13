"""
Login — conecta a Chrome existente via CDP (reutiliza sesión activa).
Antes de correr el bot: google-chrome --remote-debugging-port=9222 &
"""

import asyncio
from playwright.async_api import BrowserContext
from playwright_stealth import stealth_async


async def get_authenticated_context(playwright):
    print("[login] Connecting to existing Chrome via CDP...")
    try:
        browser = await playwright.chromium.connect_over_cdp("http://localhost:9222")
    except Exception as e:
        raise SystemExit(
            f"[login] Cannot connect to Chrome: {e}\n"
            "Run first: google-chrome --remote-debugging-port=9222 &\n"
            "Then log into Binance manually and re-run the bot."
        )

    context = browser.contexts[0]
    page = context.pages[0] if context.pages else await context.new_page()
    await stealth_async(page)

    print(f"[login] Connected. Current page: {page.url}")
    return browser, context, page
