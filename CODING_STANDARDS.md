# Twitch OCR Chatbot Coding Standards & Architecture Invariants

This document defines the strict engineering standards, terminology constraints, security invariants, and code quality expectations for the Twitch OCR Chatbot application.

## 1. Canonical Domain Language

All code identifiers, comments, user interface copy, and documentation must use the canonical domain terms defined in [CONTEXT.md](CONTEXT.md). Avoid prohibited synonyms:

- **Game Event**: An in-game occurrence (e.g., player death, level up) observed by the system.
  - _Avoid_: Trigger, alert, notification, flag.
- **Detection Source**: Origin mechanism (visual screen capture or native file logs).
  - _Avoid_: Sensor, watcher type, scanner type.
- **Capture Zone**: Rectangular screen region monitored by visual OCR for text keywords.
  - _Avoid_: Box, ROI, screen area, crop box.
- **Template Matching**: Full-screen computer vision comparison against reference asset images.
  - _Avoid_: Bounding box search, crop scanning, OCR zone.
- **Active Game Detection**: Automatic identification of the running foreground game window.
  - _Avoid_: Manual game switcher, dropdown selector.
- **Reaction**: Short text quip generated in response to a Game Event.
  - _Avoid_: Message, response payload, embed, notification.
- **Fallback Reaction**: Pre-written static quip used when dynamic generation times out.
  - _Avoid_: Default message, backup roast, error message.
- **Cooldown**: Suppression window ignoring repeated triggers of the same event.
  - _Avoid_: Throttle, debounce, rate limit.
- **Broadcast Channel**: Destination chat service (Twitch chat or Discord webhook).
  - _Avoid_: Output sink, delivery adapter, stream.
- **Bot Personality**: Stylistic tone guiding the LLM roast generation.
  - _Avoid_: Persona config, system prompt, mood mode.
- **Synthetic Event**: Artificially injected Game Event for developer testing without gameplay.
  - _Avoid_: Mock event, dummy event, fake trigger.
- **OBS Dock**: Embedded control panel docked inside OBS Studio.
  - _Avoid_: Web dashboard, control window, admin panel.
- **Visual Overlay**: OBS Browser Source widget rendering visual reactions and sound effects.
  - _Avoid_: Stream popup, alert box, notification widget.
- **Subscription License**: Recurring commercial authorization token verified with Lemon Squeezy.
  - _Avoid_: Serial number, product key, purchase code.
- **Instance Identifier**: Client-generated UUID registered to enforce per-seat device limits.
  - _Avoid_: Machine ID, hardware hash, device token.
- **Offline Grace Period**: 7-day sliding window allowing offline operation.
  - _Avoid_: Free trial, offline mode, disconnected bypass.
- **Merchant of Record**: **Lemon Squeezy**, assuming legal and tax responsibility.
  - _Avoid_: Payment gateway, payment processor, billing vendor.
- **One-Click Auth**: Streamer OAuth workflow via Twitch Device Code Flow.
  - _Avoid_: Manual token copy, dev credentials, API key setup.

## 2. File Encoding & BOM Prohibition

- All Python source files (`.py`), configuration files (`.env*`, `.json`), Inno Setup scripts (`.iss`), PyInstaller specs (`.spec`), and batch scripts (`.bat`) must be encoded in **UTF-8 without BOM**.
- Files must never start with `0xEF, 0xBB, 0xBF`.
- Python file operations must explicitly specify `encoding="utf-8"`:
  ```python
  with open(path, "w", encoding="utf-8", newline="\n") as f:
      f.write(content)
  ```

## 3. Security & Licensing Invariants

- **Production Gate**: `DEMO-KEY-123` must strictly require `DEV_MODE=1` in the local environment and must never validate in production release binaries.
- **Credential & State Persistence**:
  - Mutable state (`.env`, `zones.json`, `bot.log`, cached tokens) must reside under `%LOCALAPPDATA%\TwitchOCRChatbot`, never in the Program Files installation directory.
  - License tokens and session caches must be protected using Windows DPAPI (`win32crypt.CryptProtectData`).
- **Heartbeat & Grace Period**: License validation calls Lemon Squeezy's Public License API. The 7-day sliding Offline Grace Period must be strictly enforced.
- **OAuth Safety**: Twitch Device Code Flow credentials and refresh tokens must be securely stored and automatically refreshed without leaking into logs.

## 4. Engineering Rigor & Error Handling

- **No Silent Exception Swallowing**: Bare `except:` or `except Exception: pass` blocks without logging are strictly prohibited.
- **Structured Logging**: All errors and system events must route through Python's standard `logging` module into `bot.log`.
- **No Workarounds**: Never implement monkeypatches around screen grabbers, OCR processes, or threading models. Fix bugs at their architectural origin.
