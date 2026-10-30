import os
import sys
import shutil
from pathlib import Path
from dotenv import load_dotenv

def _get_bundle_dir() -> Path:
    base = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return Path(base)

# Persist mutable user settings, zones, and logs in %LOCALAPPDATA%\TwitchOCRChatbot
APP_DATA_DIR = Path(os.environ.get("LOCALAPPDATA", Path.home())) / "TwitchOCRChatbot"
APP_DATA_DIR.mkdir(parents=True, exist_ok=True)

ENV_FILE = APP_DATA_DIR / ".env"
ZONES_FILE = APP_DATA_DIR / "zones.json"
LOG_FILE = APP_DATA_DIR / "bot.log"

# Seed .env into %LOCALAPPDATA%\TwitchOCRChatbot on first run if not present
if not ENV_FILE.exists():
    local_env = Path(".env")
    example_env = _get_bundle_dir() / ".env.example"
    if local_env.exists():
        shutil.copyfile(local_env, ENV_FILE)
    elif example_env.exists():
        shutil.copyfile(example_env, ENV_FILE)
    else:
        ENV_FILE.write_text("", encoding="utf-8")

# Seed zones.json into %LOCALAPPDATA%\TwitchOCRChatbot on first run if not present
if not ZONES_FILE.exists():
    bundled_zones = _get_bundle_dir() / "zones.json"
    local_zones = Path("zones.json")
    if bundled_zones.exists():
        shutil.copyfile(bundled_zones, ZONES_FILE)
    elif local_zones.exists():
        shutil.copyfile(local_zones, ZONES_FILE)
    else:
        ZONES_FILE.write_text("{}", encoding="utf-8")

# Load environment variables from %LOCALAPPDATA%\TwitchOCRChatbot\.env (override system envs)
load_dotenv(dotenv_path=str(ENV_FILE), override=True)

# Public Client ID registered in Twitch Developer Console (Client Type: Public, Device Code Grant Flow)
DEFAULT_PUBLIC_TWITCH_CLIENT_ID = "0ladxfm8g5y0apc3i5nz4pjm9qo2fh"
DEFAULT_LEMON_SQUEEZY_STORE_ID = 504193
DEFAULT_LEMON_SQUEEZY_PRODUCT_ID = 1472500
DEFAULT_LEMON_SQUEEZY_CHECKOUT_URL = "https://pictureperfect.lemonsqueezy.com/checkout"


class Config:
    APP_DATA_DIR = APP_DATA_DIR
    ENV_FILE = ENV_FILE
    ZONES_FILE = ZONES_FILE
    LOG_FILE = LOG_FILE

    @classmethod
    def validate(cls):
        missing = []
        if not cls.TWITCH_CLIENT_ID:
            missing.append("TWITCH_CLIENT_ID")
        if not cls.TWITCH_OAUTH_TOKEN:
            missing.append("TWITCH_OAUTH_TOKEN")
        if not cls.TWITCH_CHANNEL:
            missing.append("TWITCH_CHANNEL")

        if missing:
            raise ValueError(f"Missing required environment variables: {', '.join(missing)}")

    @classmethod
    def reload(cls):
        load_dotenv(dotenv_path=str(cls.ENV_FILE), override=True)
        cls.TWITCH_CLIENT_ID = os.getenv("TWITCH_CLIENT_ID") or DEFAULT_PUBLIC_TWITCH_CLIENT_ID
        cls.TWITCH_CLIENT_SECRET = os.getenv("TWITCH_CLIENT_SECRET", "")
        _raw_token = os.getenv("TWITCH_OAUTH_TOKEN", "")
        cls.TWITCH_OAUTH_TOKEN = f"oauth:{_raw_token}" if _raw_token and not _raw_token.startswith("oauth:") else _raw_token
        cls.TWITCH_REFRESH_TOKEN = os.getenv("TWITCH_REFRESH_TOKEN", "")
        cls.TWITCH_CHANNEL = os.getenv("TWITCH_CHANNEL", "")
        cls.TWITCH_REDIRECT_URI = os.getenv("TWITCH_REDIRECT_URI", "http://localhost")

        cls.TESSERACT_CMD = os.getenv("TESSERACT_CMD", r"C:\Program Files\Tesseract-OCR\tesseract.exe")
        cls.TARGET_GAME = os.getenv("TARGET_GAME", "poe2")
        cls.SCAN_INTERVAL = float(os.getenv("SCAN_INTERVAL") or "1.0")
        cls.EVENT_COOLDOWN = float(os.getenv("EVENT_COOLDOWN") or "30.0")

        cls.POE_LOG_PATH = os.getenv("POE_LOG_PATH", "")
        cls.POE2_LOG_PATH = os.getenv("POE2_LOG_PATH", "")
        cls.WOW_COMBAT_LOG_PATH = os.getenv("WOW_COMBAT_LOG_PATH", "")
        cls.WOW_CHAT_LOG_PATH = os.getenv("WOW_CHAT_LOG_PATH", "")

        cls.DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL", "")
        cls.BOT_PERSONALITY = os.getenv("BOT_PERSONALITY", "snarky and sarcastic")

        cls.USE_OLLAMA = os.getenv("USE_OLLAMA", "False").lower() in ("true", "1", "yes")
        cls.OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3:8b")
        cls.OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434/api/generate")

        cls.AI_PROVIDER = os.getenv("AI_PROVIDER", "curated").lower()
        cls.GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
        cls.GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")
        cls.OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
        cls.OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        cls.OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")

        cls.LEMON_SQUEEZY_STORE_ID = int(os.getenv("LEMON_SQUEEZY_STORE_ID") or DEFAULT_LEMON_SQUEEZY_STORE_ID)
        cls.LEMON_SQUEEZY_PRODUCT_ID = int(os.getenv("LEMON_SQUEEZY_PRODUCT_ID") or DEFAULT_LEMON_SQUEEZY_PRODUCT_ID)
        cls.LEMON_SQUEEZY_CHECKOUT_URL = os.getenv("LEMON_SQUEEZY_CHECKOUT_URL") or DEFAULT_LEMON_SQUEEZY_CHECKOUT_URL
        cls.LEMON_SQUEEZY_LICENSE_KEY = os.getenv("LEMON_SQUEEZY_LICENSE_KEY", "")


Config.reload()





