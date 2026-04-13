from pathlib import Path
from vault import SecureVault

BASE_DIR = Path(__file__).parent

_vault = SecureVault()
_creds = _vault.load_credentials()
if _creds is None:
    raise SystemExit("Vault not initialized. Run: python vault.py --init")

exchange_EMAIL    = _creds["exchange"]["email"]
exchange_PASSWORD = _creds["exchange"]["password"]
TOTP_SECRET      = _creds["exchange"]["totp_secret"]

TELEGRAM_BOT_TOKEN = _creds["telegram"]["bot_token"]
TELEGRAM_CHAT_ID   = _creds["telegram"]["chat_id"]

BANK_URL  = _creds["banco"]["url"]
BANK_USER = _creds["banco"]["usuario"]
BANK_PASS = _creds["banco"]["password"]

SESSION_DIR  = BASE_DIR / "session"
STATE_FILE   = BASE_DIR / "data" / "known_orders.json"
LOG_FILE     = BASE_DIR / "logs" / "orders.log"
PROMPTS_DIR  = BASE_DIR / "prompts"

ORDERS_URL       = "https://p2p.exchange.com/es-LA/fiatOrder?tab=1&page=1"
MYADS_URL        = "https://c2c.exchange.com/es-LA/myads?type=normal&code=default"

OLLAMA_MODEL     = "llama3.2:3b"
OLLAMA_HOST      = "http://localhost:11434"

POLL_MIN_SECONDS = 60
POLL_MAX_SECONDS = 90
