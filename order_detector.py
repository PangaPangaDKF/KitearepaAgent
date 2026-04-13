"""
Order Detector — Ollama-based HTML parser for Binance P2P orders.
"""

import json
import re
import logging
from ollama import Client
from config import OLLAMA_MODEL, OLLAMA_HOST, PROMPTS_DIR

logger = logging.getLogger(__name__)

_SYSTEM_PROMPT = (PROMPTS_DIR / "extract_orders.txt").read_text(encoding="utf-8")


class OrderDetector:
    def __init__(self):
        self.client = Client(host=OLLAMA_HOST)
        self.model = OLLAMA_MODEL

    def extract_orders(self, html: str) -> list[dict]:
        html_truncated = html[:50000]
        user_prompt = (
            "Analyze this Binance P2P order page HTML.\n\n"
            f"HTML content:\n{html_truncated}\n\n"
            "Return JSON only."
        )
        try:
            response = self.client.chat(
                model=self.model,
                messages=[
                    {"role": "system", "content": _SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt},
                ],
            )
            raw = response.message.content
            logger.debug(f"Ollama raw: {raw[:300]}")
        except Exception as e:
            logger.error(f"Ollama request failed: {e}")
            return []

        match = re.search(r"\{[\s\S]*\}", raw)
        if not match:
            logger.warning("No JSON in Ollama response")
            return []

        try:
            data = json.loads(match.group())
        except json.JSONDecodeError as e:
            logger.error(f"JSON parse error: {e} — raw: {raw[:200]}")
            return []

        orders = data.get("orders", [])
        valid = [o for o in orders if self._validate(o)]
        if len(orders) - len(valid):
            logger.warning(f"Skipped {len(orders) - len(valid)} invalid orders")
        logger.info(f"Extracted {len(valid)} valid orders")
        return valid

    def _validate(self, order: dict) -> bool:
        required = ["order_id", "buyer_name", "usdt_amount", "ves_amount", "price_per_usdt", "status"]
        if not all(k in order for k in required):
            return False
        if len(str(order["order_id"])) != 20:
            return False
        if order["usdt_amount"] <= 0 or order["ves_amount"] <= 0:
            return False
        calculated = order["ves_amount"] / order["usdt_amount"]
        if abs(calculated - order["price_per_usdt"]) / calculated > 0.01:
            return False
        return True
