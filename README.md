# KitearepaAgent

Autonomous P2P arbitrage agent for the VES/USDT market. Runs 24/7 on local hardware with zero manual intervention.

## Cycle

1. Monitor — watches P2P order book for sell orders
2. Sell — new order detected, operator notified via Telegram
3. Verify — waits for buyer payment confirmation
4. Release — operator confirms bank deposit
5. Buy — agent finds best buy at spread
6. Pay — closes buy side
7. Repeat

## Stack

- Python 3.10+ / asyncio
- Playwright + stealth (browser automation)
- Local LLM via Ollama (order parsing)
- Telegram Bot (operator control and alerts)
- AES-256 encrypted vault (credentials)

## Telegram Commands

| Command | Action |
|---------|--------|
| /iniciar | start monitoring |
| /detener | pause |
| /estado | status |
| /check | force check now |
| /ordenes | list tracked orders |

## Kite Chain Integration

On-chain settlement removes the manual release step — enabling fully trustless 24/7 operation.
