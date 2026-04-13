"""
Monitor — polls Binance P2P orders page, tracks new orders and status changes.
"""

import asyncio
import json
import logging
import random
from playwright.async_api import Page
from playwright_stealth import stealth_async
from order_detector import OrderDetector
from config import ORDERS_URL, STATE_FILE, POLL_MIN_SECONDS, POLL_MAX_SECONDS

logger = logging.getLogger(__name__)
detector = OrderDetector()


def _load_state() -> dict:
    try:
        return json.loads(STATE_FILE.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def _save_state(state: dict):
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    STATE_FILE.write_text(json.dumps(state, indent=2, ensure_ascii=False), encoding="utf-8")


_order_state: dict = _load_state()


async def _get_page_html(page: Page) -> str:
    await page.goto(ORDERS_URL, wait_until="domcontentloaded", timeout=30000)
    await asyncio.sleep(random.uniform(2.0, 3.5))
    return await page.content()


async def get_new_orders(page: Page) -> list[dict]:
    await stealth_async(page)
    try:
        html = await _get_page_html(page)
    except Exception as e:
        logger.error(f"Failed to load orders page: {e}")
        return []

    orders = detector.extract_orders(html)
    new_orders = []
    for order in orders:
        oid = str(order["order_id"])
        if oid not in _order_state:
            _order_state[oid] = {**order, "last_status": order["status"]}
            _save_state(_order_state)
            new_orders.append(order)
            logger.info(f"NEW order: {oid} | {order['usdt_amount']} USDT | {order['status']}")

    if not new_orders:
        logger.info(f"No new orders. Tracking {len(_order_state)} total.")
    return new_orders


async def get_status_changes(page: Page) -> list[dict]:
    await stealth_async(page)
    try:
        html = await _get_page_html(page)
    except Exception as e:
        logger.error(f"Failed to load orders page for status check: {e}")
        return []

    orders = detector.extract_orders(html)
    changes = []
    for order in orders:
        oid = str(order["order_id"])
        if oid in _order_state:
            old_status = _order_state[oid].get("last_status", "")
            new_status = order["status"]
            if old_status != new_status:
                logger.info(f"Status change {oid}: {old_status!r} → {new_status!r}")
                changes.append({**order, "old_status": old_status})
                _order_state[oid]["last_status"] = new_status
                _save_state(_order_state)
    return changes


def poll_delay() -> float:
    return random.uniform(POLL_MIN_SECONDS, POLL_MAX_SECONDS)
