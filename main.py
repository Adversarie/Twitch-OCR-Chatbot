import asyncio
import logging
from twitchio.ext import commands
from config import Config
from reaction_engine import ReactionEngine
from ocr_scanner import OCRScanner
from log_watcher import LogWatcher

import sys
import os

# Ensure valid stdout/stderr streams in windowless / frozen Windows environments
if sys.stdout is None:
    sys.stdout = open(os.devnull, "w", encoding="utf-8")
if sys.stderr is None:
    sys.stderr = open(os.devnull, "w", encoding="utf-8")

from logging.handlers import RotatingFileHandler

# Set up logging to both console and a rotating log file
log_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Rotating File Handler (max 5MB, keep 3 backup logs) in %LOCALAPPDATA%\TwitchOCRChatbot\bot.log
file_handler = RotatingFileHandler(str(Config.LOG_FILE), maxBytes=5*1024*1024, backupCount=3, encoding='utf-8')
file_handler.setFormatter(log_formatter)
file_handler.setLevel(logging.INFO)

# Console Handler
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setFormatter(log_formatter)
console_handler.setLevel(logging.INFO)

# Configure Root Logger
root_logger = logging.getLogger()
root_logger.setLevel(logging.INFO)
root_logger.addHandler(file_handler)
root_logger.addHandler(console_handler)

logger = logging.getLogger(__name__)

class TwitchOCRBot(commands.Bot):
    def __init__(self, engine):
        # Initialize Twitch bot with modern OAuth
        token = (Config.TWITCH_OAUTH_TOKEN or "").strip()
        client_id = (Config.TWITCH_CLIENT_ID or "").strip()
        channel = (Config.TWITCH_CHANNEL or "").strip()
        super().__init__(
            token=token,
            client_id=client_id,
            prefix='!',
            initial_channels=[channel] if channel else []
        )
        
        self.engine = engine
        # Control flag
        self.is_scanning = True

    async def event_ready(self):
        logger.info(f'Logged in as | {self.nick}')
        logger.info(f'User id is | {self.user_id}')
        logger.info(f'Attempting to join channel: {Config.TWITCH_CHANNEL}')

    async def event_join(self, channel, user):
        if user.name.lower() == self.nick.lower():
            logger.info(f"Successfully joined channel: {channel.name}")

    async def event_message(self, message):
        # Prevent infinite loops: only ignore if the author is the bot AND the message is not a command.
        # This allows the streamer to run commands even if the bot is running on their own broadcaster account.
        if message.author and message.author.name.lower() == self.nick.lower():
            if not message.content.startswith('!'):
                return
        
        # Log incoming messages for diagnostics
        author_name = message.author.name if message.author else "Unknown"
        logger.info(f"Chat Message - {author_name}: {message.content}")
        
        # Handle commands
        await self.handle_commands(message)

    async def send_chat_message(self, channel_name, message):
        """Helper to send a message to a specific channel."""
        channel = self.get_channel(channel_name.lower())
        if channel:
            logger.info(f"Sending message: {message}")
            await channel.send(message)
        else:
            logger.error(f"Cannot send reaction: Bot has not successfully joined or retrieved channel '{channel_name}' yet.")

    @commands.command(name='bot_status')
    async def bot_status(self, ctx: commands.Context):
        """Returns the current status of the Twitch OCR Chatbot."""
        status = "Enabled" if self.is_scanning else "Disabled"
        response = (
            f"Twitch OCR Bot is active! "
            f"Scanning: {status} | "
            f"Game: {Config.TARGET_GAME} | "
            f"Ollama Mode: {'Enabled' if Config.USE_OLLAMA else 'Disabled (Hybrid Prewritten)'} | "
            f"Interval: {Config.SCAN_INTERVAL}s"
        )
        await ctx.send(response)

    @commands.command(name='test_reaction')
    async def test_reaction(self, ctx: commands.Context, event_id: str = None):
        """Simulates an OCR trigger for an event (Broadcaster/Mod only)."""
        if not (ctx.author.is_broadcaster or ctx.author.is_mod):
            return
            
        if not event_id:
            available = [
                "poe2_death", "poe2_level_up", "poe2_boss_kill", 
                "poe2_disconnect", "poe2_inventory_full", "poe2_out_of_mana"
            ]
            await ctx.send(f"Please specify an event ID. E.g., !test_reaction poe2_death. Available: {', '.join(available)}")
            return
            
        logger.info(f"Manually triggered test reaction for event: {event_id}")
        reaction_msg = self.engine.get_reaction(event_id, "DEBUG_TEST_CONTEXT")
        if reaction_msg:
            logger.info(f"Sending test reaction message: {reaction_msg}")
            await ctx.send(reaction_msg)
        else:
            await ctx.send(f"No reaction found/generated for event ID '{event_id}'.")

    @commands.command(name='toggle_ocr')
    async def toggle_ocr(self, ctx: commands.Context):
        """Allows the broadcaster to toggle the OCR scanning on or off."""
        if ctx.author.is_broadcaster:
            self.is_scanning = not self.is_scanning
            status = "enabled" if self.is_scanning else "disabled"
            await ctx.send(f"OCR scanning has been {status}.")

import json
import urllib.request
from game_detector import GameDetector

async def run_app():
    """Core Application Runner orchestrating the Scanner, Engine, and Twitch Bot."""
    engine = ReactionEngine()
    detector = GameDetector(Config.TARGET_GAME)
    scanner = OCRScanner(Config.TARGET_GAME)
    log_watcher = LogWatcher(Config)
    bot = TwitchOCRBot(engine)
    
    async def handle_event(event_id, text_context, source="OCR"):
        if not bot.is_scanning:
            return
            
        logger.info(f"[{source}] Event Detected: {event_id} - Context: {text_context.strip()}")
        reaction_msg = engine.get_reaction(event_id, text_context)
        if reaction_msg:
            await bot.send_chat_message(Config.TWITCH_CHANNEL, reaction_msg)
            
            # Broadcast to Discord Webhook if configured
            if Config.DISCORD_WEBHOOK_URL:
                def _send_discord():
                    req = urllib.request.Request(
                        Config.DISCORD_WEBHOOK_URL,
                        data=json.dumps({"content": reaction_msg}).encode("utf-8"),
                        headers={"Content-Type": "application/json", "User-Agent": "TwitchBot"}
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
        await bot.wait_for_ready()
        
        while True:
            if bot.is_scanning:
                active_game = detector.detect()
                if active_game != scanner.target_game:
                    scanner.target_game = active_game
                # Reload zones from disk dynamically so edits take effect immediately
                scanner.reload_zones()
                detected_events = scanner.scan()
                
                for event_id, text_context in detected_events:
                    await handle_event(event_id, text_context, "OCR")
                        
            await asyncio.sleep(Config.SCAN_INTERVAL)

    async def log_watch_loop():
        logger.info("Started Native Game Log Tailing Loop")
        await bot.wait_for_ready()
        
        async for event_id, text_context in log_watcher.watch():
            await handle_event(event_id, text_context, "LOG")

    # Run the Twitch bot connection, OCR loop, and Log loop concurrently
    await asyncio.gather(
        bot.start(),
        scan_loop(),
        log_watch_loop()
    )

if __name__ == "__main__":
    try:
        Config.validate()
        asyncio.run(run_app())
    except Exception as e:
        logger.error(f"Failed to start app: {e}")
