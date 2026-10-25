import ctypes
from ctypes import wintypes
import logging

logger = logging.getLogger(__name__)

class GameDetector:
    """
    Lightweight, zero-dependency active game detector.
    Monitors the Windows foreground window title using native user32 Win32 API.
    """
    def __init__(self, default_game: str = "poe1"):
        self.default_game = default_game
        self.current_game = default_game
        self.manual_override = None  # None = auto-detect, or 'poe1', 'poe2', 'wow'
        self._user32 = None
        try:
            self._user32 = ctypes.windll.user32
            self._user32.GetForegroundWindow.restype = wintypes.HWND
            self._user32.GetWindowTextLengthW.argtypes = [wintypes.HWND]
            self._user32.GetWindowTextW.argtypes = [wintypes.HWND, wintypes.LPWSTR, ctypes.c_int]
        except Exception as e:
            logger.debug(f"User32 initialization: {e}")

    def set_game(self, game: str):
        """Set explicit game override, or 'auto'/None to restore window tracking."""
        if not game or game.lower() in ("auto", "none"):
            self.manual_override = None
            logger.info("Game detector set to Auto-Detect mode")
        else:
            clean = game.lower().strip()
            self.manual_override = clean
            self.current_game = clean
            logger.info(f"Game detector manually locked to: {clean}")

    def get_foreground_title(self) -> str:
        """Returns the title of the current Windows foreground window."""
        if not self._user32:
            return ""
        try:
            hwnd = self._user32.GetForegroundWindow()
            if not hwnd:
                return ""
            length = self._user32.GetWindowTextLengthW(hwnd)
            if length <= 0:
                return ""
            buf = ctypes.create_unicode_buffer(length + 1)
            self._user32.GetWindowTextW(hwnd, buf, length + 1)
            return buf.value.strip()
        except Exception:
            return ""

    def detect(self) -> str:
        """
        Identifies the currently focused game ('poe1', 'poe2', 'wow').
        Falls back to the last detected game if streamer alt-tabs to OBS or browser.
        """
        if self.manual_override:
            return self.manual_override

        title = self.get_foreground_title()
        if title:
            title_lower = title.lower()
            # Check PoE 2 before PoE 1 to prevent substring shadowing
            if "path of exile 2" in title_lower:
                if self.current_game != "poe2":
                    logger.info("Auto-switched active game context to Path of Exile 2")
                    self.current_game = "poe2"
                return "poe2"
            elif "path of exile" in title_lower:
                if self.current_game != "poe1":
                    logger.info("Auto-switched active game context to Path of Exile 1")
                    self.current_game = "poe1"
                return "poe1"
            elif "world of warcraft" in title_lower:
                if self.current_game != "wow":
                    logger.info("Auto-switched active game context to World of Warcraft")
                    self.current_game = "wow"
                return "wow"

        return self.current_game
