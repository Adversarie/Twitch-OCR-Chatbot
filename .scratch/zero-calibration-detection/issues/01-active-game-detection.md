---
type: wayfinder:task
status: closed
assignee: agent
---

## Question

How should the bot detect the running foreground game window without external pip dependencies or CPU overhead, and automatically switch active game profiles between Path of Exile 1, Path of Exile 2, and World of Warcraft?

## Resolution

Implemented `game_detector.py` using Windows native `ctypes.windll.user32` to query the foreground window title (`GetForegroundWindow` + `GetWindowTextW`) with zero external pip dependencies.
- Substring signatures map `"Path of Exile 2"` -> `poe2`, `"Path of Exile"` -> `poe1`, and `"World of Warcraft"` -> `wow`.
- Persists the active game state across alt-tab transitions so streaming tools (OBS, Discord, browser) don't interrupt active detection.
- Hooked into `main.py`'s scanning loop and `web.py`'s background runner, exposing `/api/bot/status` and `/api/active-game` with real-time UI badge updates in the sidebar.
