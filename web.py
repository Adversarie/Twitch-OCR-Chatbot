import sys
import os

# Ensure valid stdout/stderr streams in windowless / frozen Windows environments
if sys.stdout is None:
    sys.stdout = open(os.devnull, "w", encoding="utf-8")
if sys.stderr is None:
    sys.stderr = open(os.devnull, "w", encoding="utf-8")

import asyncio
import json
import logging
import urllib.request
import urllib.parse
import urllib.error
import webbrowser
from typing import Optional, Dict, Any, Tuple
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse, StreamingResponse, Response
from contextlib import asynccontextmanager
from dotenv import dotenv_values, set_key
from io import BytesIO
import mss
import uvicorn


def get_resource_path(relative_path: str) -> str:
    """Get absolute path to resource, supports both dev and PyInstaller frozen runtime."""
    base_path = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)


from config import Config
from reaction_engine import ReactionEngine
from ocr_scanner import OCRScanner
from log_watcher import LogWatcher
from main import TwitchOCRBot
from game_detector import GameDetector
from license_manager import LicenseManager, LicenseState

logger = logging.getLogger(__name__)

TWITCH_SCOPES = "chat:read chat:edit"


class TwitchDeviceAuthManager:
    """Manages 1-Click Twitch Device Code Grant Flow (Public Client) and rolling token refresh."""

    def __init__(self):
        self.state: str = "authorized" if (Config.TWITCH_OAUTH_TOKEN and Config.TWITCH_CHANNEL) else "idle"
        self.user_code: Optional[str] = None
        self.verification_uri: Optional[str] = None
        self.message: Optional[str] = None
        self.interval: int = 5
        self._poll_task: Optional[asyncio.Task] = None

    def _post_form(self, url: str, params: Dict[str, str]) -> Tuple[int, Dict[str, Any]]:
        encoded = urllib.parse.urlencode(params).encode("utf-8")
        req = urllib.request.Request(
            url,
            data=encoded,
            headers={
                "Accept": "application/json",
                "Content-Type": "application/x-www-form-urlencoded",
                "User-Agent": "TwitchOCRChatbot/1.0",
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=10) as resp:
                return resp.status, json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            try:
                body = json.loads(e.read().decode("utf-8"))
            except Exception:
                body = {"message": f"HTTP {e.code}: {e.reason}"}
            return e.code, body
        except Exception as e:
            return 0, {"message": str(e)}

    def _validate_token(self, raw_access_token: str) -> Tuple[int, Dict[str, Any]]:
        clean = raw_access_token.replace("oauth:", "").strip()
        req = urllib.request.Request(
            "https://id.twitch.tv/oauth2/validate",
            headers={
                "Authorization": f"OAuth {clean}",
                "Accept": "application/json",
                "User-Agent": "TwitchOCRChatbot/1.0",
            },
            method="GET",
        )
        try:
            with urllib.request.urlopen(req, timeout=10) as resp:
                return resp.status, json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            try:
                body = json.loads(e.read().decode("utf-8"))
            except Exception:
                body = {"message": f"HTTP {e.code}"}
            return e.code, body
        except Exception as e:
            return 0, {"message": str(e)}

    def save_credentials(self, access_token: str, refresh_token: str, channel: str) -> None:
        env_path = str(Config.ENV_FILE)
        clean_access = access_token.replace("oauth:", "").strip()
        set_key(env_path, "TWITCH_OAUTH_TOKEN", f"oauth:{clean_access}")
        set_key(env_path, "TWITCH_REFRESH_TOKEN", refresh_token or "")
        set_key(env_path, "TWITCH_CHANNEL", channel.lower().strip())
        Config.reload()

    async def start_device_flow(self, open_browser: bool = True) -> Dict[str, Any]:
        if self._poll_task and not self._poll_task.done():
            self._poll_task.cancel()

        client_id = (Config.TWITCH_CLIENT_ID or "").strip()
        if not client_id:
            self.state = "error"
            self.message = "Twitch Client ID is not configured."
            return self.get_status()

        status_code, body = await asyncio.to_thread(
            self._post_form,
            "https://id.twitch.tv/oauth2/device",
            {"client_id": client_id, "scopes": TWITCH_SCOPES},
        )

        if status_code != 200 or "device_code" not in body:
            self.state = "error"
            err_msg = body.get("message") or "Could not start Twitch Device Code flow."
            self.message = f"Twitch Auth Error: {err_msg}"
            return self.get_status()

        device_code = body["device_code"]
        self.user_code = body.get("user_code")
        raw_uri = body.get("verification_uri") or "https://www.twitch.tv/activate"
        if self.user_code and "device-code=" not in raw_uri:
            sep = "&" if "?" in raw_uri else "?"
            self.verification_uri = f"{raw_uri}{sep}public=true&device-code={self.user_code}"
        else:
            self.verification_uri = raw_uri
        interval = int(body["interval"]) if "interval" in body and body["interval"] is not None else 5
        self.interval = interval

        self.state = "waiting_for_user"
        self.message = "Click 'Authorize' in the Twitch browser tab to connect your channel."

        if open_browser and self.verification_uri:
            try:
                webbrowser.open(self.verification_uri)
            except Exception as e:
                logger.warning(f"Could not auto-open browser for Twitch auth: {e}")

        self._poll_task = asyncio.create_task(self._poll_for_token(client_id, device_code, interval))
        return self.get_status()

    async def _poll_for_token(self, client_id: str, device_code: str, interval: int) -> None:
        max_attempts = 60  # ~5 minutes
        for _ in range(max_attempts):
            await asyncio.sleep(interval)
            status_code, body = await asyncio.to_thread(
                self._post_form,
                "https://id.twitch.tv/oauth2/token",
                {
                    "client_id": client_id,
                    "scopes": TWITCH_SCOPES,
                    "device_code": device_code,
                    "grant_type": "urn:ietf:params:oauth:grant-type:device_code",
                },
            )

            if status_code == 200 and "access_token" in body:
                access_token = body["access_token"]
                refresh_token = body.get("refresh_token", "")
                val_code, val_body = await asyncio.to_thread(self._validate_token, access_token)
                channel = val_body.get("login") if val_code == 200 else (Config.TWITCH_CHANNEL or "broadcaster")

                self.save_credentials(access_token, refresh_token, channel)
                self.state = "authorized"
                self.user_code = None
                self.verification_uri = None
                self.message = f"Connected as @{channel}!"
                logger.info(f"1-Click Twitch OAuth completed for channel @{channel}")
                return

            err_msg = (body.get("message") or "").lower()
            if "authorization_pending" in err_msg or "slow_down" in err_msg:
                if "slow_down" in err_msg:
                    interval += 2
                continue

            self.state = "error"
            self.message = body.get("message") or "Twitch authorization failed or expired."
            return

        self.state = "error"
        self.message = "Twitch authorization timed out. Click Connect Twitch to try again."

    async def refresh_if_needed(self) -> bool:
        if not Config.TWITCH_OAUTH_TOKEN:
            return False

        val_code, val_body = await asyncio.to_thread(self._validate_token, Config.TWITCH_OAUTH_TOKEN)
        if val_code == 200 and val_body.get("expires_in", 3600) > 1800:
            if val_body.get("login") and not Config.TWITCH_CHANNEL:
                self.save_credentials(
                    Config.TWITCH_OAUTH_TOKEN, Config.TWITCH_REFRESH_TOKEN, val_body["login"]
                )
            self.state = "authorized"
            return True

        if not Config.TWITCH_REFRESH_TOKEN:
            return val_code == 200

        status_code, body = await asyncio.to_thread(
            self._post_form,
            "https://id.twitch.tv/oauth2/token",
            {
                "grant_type": "refresh_token",
                "refresh_token": Config.TWITCH_REFRESH_TOKEN,
                "client_id": Config.TWITCH_CLIENT_ID,
            },
        )
        if status_code == 200 and "access_token" in body:
            access_token = body["access_token"]
            refresh_token = body.get("refresh_token", Config.TWITCH_REFRESH_TOKEN)
            val_code2, val_body2 = await asyncio.to_thread(self._validate_token, access_token)
            channel = val_body2.get("login") if val_code2 == 200 else Config.TWITCH_CHANNEL
            self.save_credentials(access_token, refresh_token, channel)
            self.state = "authorized"
            logger.info("Successfully refreshed Twitch OAuth token via Public Client refresh token.")
            return True

        return False

    async def disconnect(self) -> Dict[str, Any]:
        if self._poll_task and not self._poll_task.done():
            self._poll_task.cancel()
        env_path = str(Config.ENV_FILE)
        set_key(env_path, "TWITCH_OAUTH_TOKEN", "")
        set_key(env_path, "TWITCH_REFRESH_TOKEN", "")
        set_key(env_path, "TWITCH_CHANNEL", "")
        Config.reload()
        self.state = "idle"
        self.user_code = None
        self.verification_uri = None
        self.message = "Disconnected from Twitch."
        return self.get_status()

    def get_status(self) -> Dict[str, Any]:
        connected = bool(Config.TWITCH_OAUTH_TOKEN and Config.TWITCH_CHANNEL)
        if connected and self.state == "idle":
            self.state = "authorized"
        status_map = {
            "authorized": "connected",
            "waiting_for_user": "pending",
            "error": "error",
            "idle": "disconnected",
        }
        return {
            "status": status_map.get(self.state, "disconnected"),
            "state": self.state,
            "connected": connected,
            "has_token": bool(Config.TWITCH_OAUTH_TOKEN),
            "channel": Config.TWITCH_CHANNEL or None,
            "user_code": self.user_code,
            "verification_uri": self.verification_uri,
            "interval": self.interval,
            "message": self.message,
        }


# Global State
class AppState:
    def __init__(self):
        self.detector = GameDetector(Config.TARGET_GAME)
        self.engine = ReactionEngine()
        self.scanner = OCRScanner()
        self.log_watcher = LogWatcher(Config)
        self.license_manager = LicenseManager()
        self.twitch_auth = TwitchDeviceAuthManager()
        self.bot = None
        self.is_running = False
        self.is_scanning = True
        self.tasks = []


state = AppState()
overlay_subscribers = set()


async def handle_event(event_id, text_context, source="OCR"):
    if not state.is_scanning:
        return

    logger.info(f"[{source}] Event Detected: {event_id} - Context: {text_context.strip()}")
    reaction_msg = state.engine.get_reaction(event_id, text_context)
    if reaction_msg:
        is_licensed = state.license_manager.is_feature_authorized()

        # Broadcast to OBS Visual Overlay subscribers
        # In trial/unauthenticated mode, tag overlay reactions with [TRIAL]
        display_reaction = reaction_msg if is_licensed else f"[TRIAL] {reaction_msg}"
        overlay_payload = {
            "event_id": event_id,
            "reaction": display_reaction,
            "context": text_context.strip(),
            "source": source,
            "licensed": is_licensed,
        }
        for q in list(overlay_subscribers):
            try:
                q.put_nowait(overlay_payload)
            except Exception:
                pass

        # Gate commercial Twitch chat and Discord broadcasts to licensed sessions
        if not is_licensed:
            logger.info(
                f"[{source}] Active subscription required for Twitch chat/Discord broadcast. Event previewed in OBS overlay only."
            )
            return

        if state.bot and Config.TWITCH_CHANNEL:
            try:
                await state.bot.send_chat_message(Config.TWITCH_CHANNEL, reaction_msg)
            except Exception as e:
                logger.error(f"Failed to send Twitch chat reaction: {e}")

        # Broadcast to Discord Webhook if configured
        if Config.DISCORD_WEBHOOK_URL:
            def _send_discord():
                req = urllib.request.Request(
                    Config.DISCORD_WEBHOOK_URL,
                    data=json.dumps({"content": reaction_msg}).encode("utf-8"),
                    headers={"Content-Type": "application/json", "User-Agent": "TwitchBot"},
                )
                with urllib.request.urlopen(req, timeout=5) as _:
                    pass

            try:
                await asyncio.to_thread(_send_discord)
                logger.info("Sent reaction to Discord Webhook")
            except Exception as e:
                logger.error(f"Failed to send to Discord Webhook: {e}")


async def scan_loop():
    logger.info("Started OCR Scanning Loop")
    while state.is_running:
        if state.is_scanning:
            active_game = state.detector.detect()
            if active_game != state.scanner.target_game:
                state.scanner.target_game = active_game
            state.scanner.reload_zones()
            detected_events = state.scanner.scan()

            for event_id, text_context in detected_events:
                await handle_event(event_id, text_context, "OCR")

        await asyncio.sleep(Config.SCAN_INTERVAL)


async def log_watch_loop():
    logger.info("Started Native Game Log Tailing Loop")
    async for event_id, text_context in state.log_watcher.watch():
        if not state.is_running:
            break
        await handle_event(event_id, text_context, "LOG")


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        await state.twitch_auth.refresh_if_needed()
        Config.validate()
    except ValueError as e:
        logger.info(f"Twitch configuration incomplete: {e}. Bot will run in setup/overlay mode.")
    except Exception as e:
        logger.debug(f"Startup Twitch check note: {e}")
    os.makedirs(static_dir, exist_ok=True)
    yield
    state.license_manager.stop_background_heartbeat()
    await stop_bot()


app = FastAPI(lifespan=lifespan)
static_dir = get_resource_path("static")
templates_dir = get_resource_path("templates")
os.makedirs(static_dir, exist_ok=True)
os.makedirs(templates_dir, exist_ok=True)
app.mount("/static", StaticFiles(directory=static_dir), name="static")
app.mount("/templates", StaticFiles(directory=templates_dir), name="templates")


@app.get("/", response_class=HTMLResponse)
async def read_root():
    return FileResponse(os.path.join(static_dir, "index.html"))


@app.post("/api/bot/start")
async def start_bot():
    if state.is_running:
        return {"status": "already running"}
    state.is_running = True

    tasks = [
        asyncio.create_task(scan_loop()),
        asyncio.create_task(log_watch_loop()),
    ]

    if Config.TWITCH_OAUTH_TOKEN and Config.TWITCH_CHANNEL:
        try:
            state.bot = TwitchOCRBot(state.engine)
            tasks.append(asyncio.create_task(state.bot.start()))
            logger.info("Twitch chat bot task started")
        except Exception as e:
            logger.error(f"Failed to start Twitch bot: {e}")
    else:
        logger.info("Bot started in Visual Overlay mode (Twitch chat unconfigured)")

    state.tasks = tasks
    logger.info("Bot started via API")
    return {"status": "started"}


@app.post("/api/bot/stop")
async def stop_bot():
    if not state.is_running:
        return {"status": "not running"}
    state.is_running = False

    if state.bot:
        try:
            await state.bot.close()
        except Exception as e:
            logger.debug(f"Error closing Twitch bot: {e}")
        state.bot = None

    for task in state.tasks:
        task.cancel()
    state.tasks = []

    logger.info("Bot stopped via API")
    return {"status": "stopped"}


@app.get("/api/bot/status")
async def bot_status():
    return {
        "is_running": state.is_running,
        "is_scanning": state.is_scanning,
        "twitch_connected": bool(Config.TWITCH_OAUTH_TOKEN and Config.TWITCH_CHANNEL),
        "active_game": state.detector.detect(),
        "manual_override": state.detector.manual_override or "auto",
        "foreground_window": state.detector.get_foreground_title(),
    }


@app.get("/api/active-game")
async def get_active_game():
    return {
        "active_game": state.detector.detect(),
        "manual_override": state.detector.manual_override or "auto",
        "foreground_window": state.detector.get_foreground_title(),
    }


@app.post("/api/active-game")
async def set_active_game(request: Request):
    data = await request.json()
    game = data.get("game", "auto")
    state.detector.set_game(game)
    active = state.detector.detect()
    state.scanner.target_game = active
    state.scanner.reload_zones()
    Config.TARGET_GAME = active
    try:
        if game and game.lower() != "auto":
            set_key(str(Config.ENV_FILE), "TARGET_GAME", active)
    except Exception:
        pass
    return {
        "status": "ok",
        "active_game": active,
        "manual_override": state.detector.manual_override or "auto",
    }


@app.get("/api/templates")
async def get_templates():
    state.scanner.template_scanner.reload_templates()
    result = {}
    for game, evs in state.scanner.template_scanner.templates.items():
        result[game] = [
            {"event_id": event_id, "image_url": f"/templates/{game}/{event_id}.png"}
            for event_id in evs.keys()
        ]
    return result


@app.post("/api/simulate-event")
async def simulate_event(request: Request):
    data = await request.json()
    event_id = data.get("event_id", "poe2_death")
    text_context = data.get("text_context", "Simulated test event")
    await handle_event(event_id, text_context, source="SIMULATION")
    return {"status": "ok", "event_id": event_id}


@app.get("/overlay")
async def get_overlay():
    return FileResponse(os.path.join(static_dir, "overlay.html"))


@app.get("/api/overlay/events")
async def overlay_events(request: Request):
    """Streams live reaction events to the OBS Browser Source overlay via SSE."""
    queue = asyncio.Queue()
    overlay_subscribers.add(queue)

    async def event_generator():
        try:
            while True:
                if await request.is_disconnected():
                    break
                try:
                    data = await asyncio.wait_for(queue.get(), timeout=15.0)
                    yield f"data: {json.dumps(data)}\n\n"
                except asyncio.TimeoutError:
                    yield ": keepalive\n\n"
        finally:
            overlay_subscribers.discard(queue)

    return StreamingResponse(event_generator(), media_type="text/event-stream")


@app.get("/api/license/status")
async def get_license_status():
    return state.license_manager.get_status_display()


@app.post("/api/license/activate")
async def activate_license(request: Request):
    data = await request.json()
    key = data.get("license_key", "").strip()
    instance_name = data.get("instance_name")
    if not key:
        return {"status": "error", "valid": False, "message": "License key cannot be empty."}

    success, message = await asyncio.to_thread(state.license_manager.activate, key, instance_name)
    if success:
        try:
            set_key(str(Config.ENV_FILE), "LEMON_SQUEEZY_LICENSE_KEY", key)
        except Exception:
            pass
        return {"status": "ok", "valid": True, "message": message, **state.license_manager.get_status_display()}
    return {"status": "error", "valid": False, "message": message, **state.license_manager.get_status_display()}


@app.post("/api/license/deactivate")
async def deactivate_license():
    success, message = await asyncio.to_thread(state.license_manager.deactivate)
    try:
        set_key(str(Config.ENV_FILE), "LEMON_SQUEEZY_LICENSE_KEY", "")
    except Exception:
        pass
    return {"status": "ok" if success else "error", "message": message, **state.license_manager.get_status_display()}


@app.get("/api/twitch/status")
async def get_twitch_status():
    auth_status = state.twitch_auth.get_status()
    return {
        "connected": bool(Config.TWITCH_OAUTH_TOKEN and Config.TWITCH_CHANNEL),
        "channel": Config.TWITCH_CHANNEL or "Unconfigured",
        "bot_online": state.is_running and state.bot is not None,
        "auth_state": auth_status["state"],
        "user_code": auth_status["user_code"],
        "verification_uri": auth_status["verification_uri"],
        "message": auth_status["message"],
    }


@app.post("/api/twitch/auth/start")
async def start_twitch_auth(open_browser: bool = True):
    return await state.twitch_auth.start_device_flow(open_browser=open_browser)


@app.get("/api/twitch/auth/poll-status")
async def poll_twitch_auth_status():
    return state.twitch_auth.get_status()


@app.post("/api/twitch/auth/disconnect")
async def disconnect_twitch_auth():
    if state.bot:
        try:
            await state.bot.close()
        except Exception:
            pass
        state.bot = None
    return await state.twitch_auth.disconnect()


@app.get("/api/settings")
async def get_settings():
    return dotenv_values(str(Config.ENV_FILE))


@app.post("/api/settings")
async def save_settings(request: Request):
    data = await request.json()
    env_path = str(Config.ENV_FILE)
    for k, v in data.items():
        set_key(env_path, k, str(v))
    Config.reload()
    if "TARGET_GAME" in data and data["TARGET_GAME"]:
        state.detector.set_game(data["TARGET_GAME"])
        state.scanner.target_game = state.detector.detect()
        state.scanner.reload_zones()
    return {"status": "saved"}


@app.get("/api/screenshot")
async def get_screenshot():
    with mss.mss() as sct:
        monitor = sct.monitors[0]
        sct_img = sct.grab(monitor)

        from PIL import Image
        img = Image.frombytes("RGB", sct_img.size, sct_img.bgra, "raw", "BGRX")

        buf = BytesIO()
        img.save(buf, format="PNG")
        buf.seek(0)

        return Response(content=buf.read(), media_type="image/png")


@app.get("/api/zones")
async def get_zones():
    try:
        with open(str(Config.ZONES_FILE), "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        try:
            with open(get_resource_path("zones.json"), "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}


@app.post("/api/zones")
async def save_zones(request: Request):
    data = await request.json()
    with open(str(Config.ZONES_FILE), "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)
    return {"status": "saved"}


@app.get("/api/bot/logs")
async def bot_logs(request: Request):
    """Streams the %LOCALAPPDATA%\\TwitchOCRChatbot\\bot.log file using Server-Sent Events (SSE)."""
    async def log_generator():
        log_file = str(Config.LOG_FILE)
        if not os.path.exists(log_file):
            open(log_file, "a", encoding="utf-8").close()

        with open(log_file, "r", encoding="utf-8") as f:
            f.seek(0, 2)  # go to end
            while True:
                if await request.is_disconnected():
                    break
                line = f.readline()
                if not line:
                    await asyncio.sleep(0.5)
                    continue
                yield f"data: {line}\n\n"

    return StreamingResponse(log_generator(), media_type="text/event-stream")


if __name__ == "__main__":
    import threading
    import time

    def open_browser():
        time.sleep(1.2)
        try:
            webbrowser.open("http://127.0.0.1:8000")
        except Exception:
            pass

    threading.Thread(target=open_browser, daemon=True).start()
    uvicorn.run(app, host="127.0.0.1", port=8000, log_config=None)
