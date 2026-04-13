"""
Telegram Command Controller — control del agente via Telegram.
Comandos: /iniciar /detener /estado /check /ordenes /ayuda
"""

import asyncio
import logging
from telegram import Update, BotCommand
from telegram.ext import Application, CommandHandler, ContextTypes
from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID, MYADS_URL

logger = logging.getLogger(__name__)


class TelegramController:
    def __init__(self, monitor):
        self.monitor = monitor
        self.app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
        self._register_handlers()

    def _register_handlers(self):
        self.app.add_handler(CommandHandler("iniciar", self.cmd_iniciar))
        self.app.add_handler(CommandHandler("detener", self.cmd_detener))
        self.app.add_handler(CommandHandler("estado",  self.cmd_estado))
        self.app.add_handler(CommandHandler("check",   self.cmd_check))
        self.app.add_handler(CommandHandler("ordenes", self.cmd_ordenes))
        self.app.add_handler(CommandHandler("ayuda",   self.cmd_ayuda))

    def _auth(self, update: Update) -> bool:
        return str(update.effective_chat.id) == str(TELEGRAM_CHAT_ID)

    async def cmd_iniciar(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not self._auth(update):
            return
        if self.monitor.is_monitoring:
            await update.message.reply_text("🔄 Ya estoy monitoreando.")
            return
        await update.message.reply_text("🔍 Verificando anuncio activo en Binance…")
        has_ad = await self.monitor.check_active_ad()
        if has_ad:
            self.monitor.is_monitoring = True
            await update.message.reply_text(
                "✅ <b>Monitoreo iniciado</b>\n"
                "📊 Checks cada 60–90 s\n"
                "Recibirás alertas automáticas.",
                parse_mode="HTML",
            )
        else:
            await update.message.reply_text(
                "❌ <b>No hay anuncio activo</b>\n\n"
                "1. Ve a Binance P2P → Mis anuncios\n"
                "2. Publica un anuncio de VENTA de USDT\n"
                "3. Asegúrate que esté <b>En línea</b>\n"
                "4. Envía /iniciar nuevamente.",
                parse_mode="HTML",
            )

    async def cmd_detener(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not self._auth(update):
            return
        self.monitor.is_monitoring = False
        await update.message.reply_text("🛑 <b>Monitoreo detenido.</b>", parse_mode="HTML")

    async def cmd_estado(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not self._auth(update):
            return
        s = self.monitor.get_status()
        await update.message.reply_text(
            f"📊 <b>ESTADO DEL AGENTE</b>\n"
            f"━━━━━━━━━━━━━━\n"
            f"🔄 Modo: <b>{s['mode']}</b>\n"
            f"📋 Órdenes en seguimiento: {s['tracking']}\n"
            f"🕐 Último check: {s['last_check']}\n"
            f"📈 Total detectadas: {s['total_detected']}\n"
            f"━━━━━━━━━━━━━━\n"
            f"<i>/iniciar /detener /check /ordenes</i>",
            parse_mode="HTML",
        )

    async def cmd_check(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not self._auth(update):
            return
        if not self.monitor.is_monitoring:
            await update.message.reply_text("⚠️ Primero inicia con /iniciar")
            return
        await update.message.reply_text("🔍 Ejecutando check manual…")
        self.monitor.force_check_requested = True

    async def cmd_ordenes(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not self._auth(update):
            return
        orders = self.monitor.get_known_orders()
        if not orders:
            await update.message.reply_text("📭 Sin órdenes registradas aún.")
            return
        lines = "\n".join(
            f"• <code>{o['id']}</code> | {o['usdt']} USDT | {o['status']}"
            for o in orders[-10:]
        )
        await update.message.reply_text(
            f"📋 <b>Últimas órdenes ({len(orders)} total):</b>\n{lines}",
            parse_mode="HTML",
        )

    async def cmd_ayuda(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not self._auth(update):
            return
        await update.message.reply_text(
            "🤖 <b>Comandos disponibles</b>\n"
            "━━━━━━━━━━━━━━\n"
            "/iniciar — verifica ad y comienza monitoreo\n"
            "/detener — pausa el monitoreo\n"
            "/estado  — muestra estado actual\n"
            "/check   — fuerza check inmediato\n"
            "/ordenes — lista órdenes conocidas\n"
            "/ayuda   — esta ayuda\n"
            "━━━━━━━━━━━━━━\n"
            "<i>Solo monitorea si hay anuncio activo en Binance.</i>",
            parse_mode="HTML",
        )
