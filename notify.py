"""
Telegram Notifications
"""

from telegram import Bot
from telegram.error import TelegramError
from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID


async def send_telegram(message: str):
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("[notify] ERROR: Telegram credentials missing in vault")
        return
    try:
        bot = Bot(token=TELEGRAM_BOT_TOKEN)
        await bot.send_message(
            chat_id=TELEGRAM_CHAT_ID,
            text=message,
            parse_mode="HTML"
        )
        print("[notify] Telegram message sent.")
    except TelegramError as e:
        print(f"[notify] Failed: {e}")


def format_order_message(order: dict) -> str:
    return (
        f"<b>Nueva orden P2P — SELL</b>\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"💰 <b>Monto:</b> {order.get('usdt_amount', '?')} USDT\n"
        f"📌 <b>Estado:</b> {order.get('status', '?')}\n"
    )
