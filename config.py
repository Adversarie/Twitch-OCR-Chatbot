import os
from dotenv import load_dotenv

# Load environment variables from .env file (override system envs)
load_dotenv(override=True)

class Config:
    TWITCH_CLIENT_ID = os.getenv("TWITCH_CLIENT_ID")
    TWITCH_CLIENT_SECRET = os.getenv("TWITCH_CLIENT_SECRET")
    _raw_token = os.getenv("TWITCH_OAUTH_TOKEN")
    TWITCH_OAUTH_TOKEN = f"oauth:{_raw_token}" if _raw_token and not _raw_token.startswith("oauth:") else _raw_token
    TWITCH_CHANNEL = os.getenv("TWITCH_CHANNEL")
    TWITCH_REDIRECT_URI = os.getenv("TWITCH_REDIRECT_URI", "http://localhost")
    
    TESSERACT_CMD = os.getenv("TESSERACT_CMD", r"C:\Program Files\Tesseract-OCR\tesseract.exe")
    TARGET_GAME = os.getenv("TARGET_GAME", "poe1")
    SCAN_INTERVAL = float(os.getenv("SCAN_INTERVAL", "1.0"))
    EVENT_COOLDOWN = float(os.getenv("EVENT_COOLDOWN", "30.0"))
    
    # Log File Paths
    POE_LOG_PATH = os.getenv("POE_LOG_PATH", "")
    WOW_COMBAT_LOG_PATH = os.getenv("WOW_COMBAT_LOG_PATH", "")
    WOW_CHAT_LOG_PATH = os.getenv("WOW_CHAT_LOG_PATH", "")
    
    USE_OLLAMA = os.getenv("USE_OLLAMA", "False").lower() in ("true", "1", "yes")
    OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3:8b")
    OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434/api/generate")

    @classmethod
    def validate(cls):
        missing = []
        if not cls.TWITCH_CLIENT_ID: missing.append("TWITCH_CLIENT_ID")
        if not cls.TWITCH_OAUTH_TOKEN: missing.append("TWITCH_OAUTH_TOKEN")
        if not cls.TWITCH_CHANNEL: missing.append("TWITCH_CHANNEL")
        
        if missing:
            raise ValueError(f"Missing required environment variables: {', '.join(missing)}")
