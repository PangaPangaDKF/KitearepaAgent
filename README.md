# KitearepaAgent

Autonomous P2P arbitrage agent for the VES/USDT market. Runs 24/7 on local hardware with zero manual intervention.

## What it does

The agent executes a full buy-sell cycle autonomously:

1. **Monitor** — Watches the P2P order book for incoming sell orders
2. **Sell** — Detects a new order, notifies operator via Telegram
3. **Verify** — Waits for buyer to mark payment as sent
4. **Release** — Operator confirms bank deposit, agent signals release
5. **Buy** — Agent identifies best buy opportunity at spread
6. **Pay** — Executes payment flow to close the buy side
7. **Cycle complete** — Returns to monitoring state

Each cycle generates profit from the bid-ask spread in the VES/USDT market.

## Stack

- Python 3.10+ / asyncio
- Playwright (browser automation, stealth mode)
- Ollama / llama3.2:3b (local LLM for order parsing)
- Telegram Bot API (operator control + alerts)
- AES-256 encrypted credential vault

## Telegram Commands

| Command | Action |
|---------|--------|
| `/iniciar` | Verify active listing and start monitoring |
| `/detener` | Pause monitoring |
| `/estado` | Show current agent status |
| `/check` | Force immediate order check |
| `/ordenes` | List tracked orders |

## Setup

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python vault.py --init
