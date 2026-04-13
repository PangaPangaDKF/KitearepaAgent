"""
exchange P2P Monitor Agent
Uso: source venv/bin/activate && python main.py
Requiere Chrome: /opt/google/chrome/chrome --remote-debugging-port=9222 --user-data-dir=$HOME/.config/chrome-bot &
"""

import asyncio
import logging
from datetime import datetime
from playwright.async_api import async_playwright
from playwright_stealth import stealth_async

from monitor import get_new_orders, get_status_changes, poll_delay, _order_state
from notify import send_telegram
from bank import open_bank
from config import LOG_FILE, MYADS_URL, ORDERS_URL

LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)

AUTO_OPEN_BANK_ON_PAID = True


def _fmt_new_order(order: dict) -> str:
    return (
        f"<b>🔔 NUEVA ORDEN DE VENTA</b>\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"📋 <b>Orden:</b> <code>{order['order_id']}</code>\n"
        f"👤 <b>Comprador:</b> {order['buyer_name']}\n"
        f"💰 <b>Monto:</b> {order['usdt_amount']} USDT → {order['ves_amount']:,.0f} Bs\n"
        f"📊 <b>Precio:</b> {order['price_per_usdt']:,.2f} Bs/USDT\n"
        f"⏰ <b>Tiempo:</b> {order.get('time_remaining', '—')}\n"
        f"📌 <b>Estado:</b> {order['status']}\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"🔗 <a href='{ORDERS_URL}'>Ver en exchange</a>"
    )


def _fmt_status_change(order: dict) -> str:
    old = order.get("old_status", "?")
    new = order["status"]
    paid = "\n\n⚠️ <b>VERIFICA EL PAGO EN EL BANCO</b>" if "pagado" in new.lower() else ""
    return (
        f"<b>⚡ CAMBIO DE ESTADO</b>\n"
        f"📋 Orden: <code>{order['order_id']}</code>\n"
        f"📌 {old} → <b>{new}</b>{paid}"
    )


class P2PMonitor:
    def __init__(self):
        self.is_monitoring = False
        self.force_check_requested = False
        self.last_check: str = "Nunca"
        self.total_detected: int = 0
        self.page = None
        self.context = None
        self._page_lock = asyncio.Lock()

    async def check_active_ad(self) -> bool:
        if not self.page:
            return False
        try:
            async with self._page_lock:
                await self.page.goto(MYADS_URL, wait_until="domcontentloaded", timeout=20000)
                await asyncio.sleep(2)
                content = (await self.page.content()).lower()
            return "en línea" in content or "online" in content or "en linea" in content
        except Exception as e:
            logger.error(f"check_active_ad error: {e}")
            return False

    def get_status(self) -> dict:
        return {
            "mode": "MONITOREANDO" if self.is_monitoring else "EN ESPERA",
            "tracking": len(_order_state),
            "last_check": self.last_check,
            "total_detected": self.total_detected,
        }

    def get_known_orders(self) -> list[dict]:
        return [
            {"id": oid, "usdt": data.get("usdt_amount", "?"), "status": data.get("last_status", "?")}
            for oid, data in list(_order_state.items())[-10:]
        ]

    async def do_check(self):
        async with self._page_lock:
            new_orders = await get_new_orders(self.page)
            for order in new_orders:
                self.total_detected += 1
                logger.info(f"New order: {order['order_id']}")
                await send_telegram(_fmt_new_order(order))

            changes = await get_status_changes(self.page)
            for order in changes:
                logger.info(f"Status change: {order['order_id']} → {order['status']}")
                await send_telegram(_fmt_status_change(order))
                if AUTO_OPEN_BANK_ON_PAID and "pagado" in order["status"].lower():
                    logger.info("Buyer marked paid — opening bank")
                    await open_bank(self.context)

        self.last_check = datetime.now().strftime("%H:%M:%S")


async def main():
    print("=" * 50)
    print("  exchange P2P Monitor Agent — Starting")
    print("=" * 50)

    monitor = P2PMonitor()
    from telegram_commands import TelegramController
    controller = TelegramController(monitor)

    async with async_playwright() as p:
        try:
            browser = await p.chromium.connect_over_cdp("http://localhost:9222")
            logger.info("Connected to Chrome via CDP")
        except Exception as e:
            raise SystemExit(
                f"No se pudo conectar a Chrome: {e}\n"
                "Ejecuta primero:\n"
                "  /opt/google/chrome/chrome --remote-debugging-port=9222 --user-data-dir=$HOME/.config/chrome-bot &"
            )

        monitor.context = browser.contexts[0]
        monitor.page = (
            monitor.context.pages[0] if monitor.context.pages
            else await monitor.context.new_page()
        )
        await stealth_async(monitor.page)
        logger.info(f"Page: {monitor.page.url}")

        async with controller.app:
            await controller.app.start()
            await controller.app.updater.start_polling(drop_pending_updates=True)
            await send_telegram(
                "<b>🤖 Agente P2P en línea</b>\n"
                "Estado: EN ESPERA\n"
                "Envía /iniciar para comenzar monitoreo."
            )
            logger.info("Waiting for /iniciar command via Telegram.")

            wait = 0.0
            try:
                while True:
                    await asyncio.sleep(10)

                    if monitor.force_check_requested:
                        monitor.force_check_requested = False
                        logger.info("Force check via Telegram")
                        try:
                            await monitor.do_check()
                        except Exception as e:
                            logger.error(f"Force check error: {e}")
                        continue

                    if not monitor.is_monitoring:
                        continue

                    wait -= 10
                    if wait > 0:
                        continue

                    logger.info("--- Checking orders ---")
                    try:
                        await monitor.do_check()
                    except Exception as e:
                        logger.error(f"Monitor error: {e}", exc_info=True)
                        await send_telegram(f"<b>⚠️ Error</b>\n<code>{e}</code>")

                    wait = poll_delay()
                    logger.info(f"Next check in {wait:.0f}s")

            except KeyboardInterrupt:
                logger.info("Stopped by user.")
                await send_telegram("<b>🛑 Agente detenido</b>")
            finally:
                await controller.app.updater.stop()
                await controller.app.stop()
                await browser.close()


if __name__ == "__main__":
    asyncio.run(main())
