# Twitch OCR Chatbot

A live stream companion that detects in-game events via visual screen capture and log tailing, generating real-time personality roasts delivered across broadcast chat channels.

## Language

**Game Event**:
An in-game occurrence observed by the system (such as a player death, level up, or boss kill) that can trigger commentary.
_Avoid_: Trigger, alert, notification, flag

**Detection Source**:
The origin mechanism that observed a Game Event, specifically visual screen capture or native file logs.
_Avoid_: Sensor, watcher type, scanner type

**Capture Zone**:
A defined rectangular region on the screen monitored by visual OCR for specific text keywords.
_Avoid_: Box, ROI, screen area, crop box

**Reaction**:
A short, platform-agnostic text quip generated in response to a detected Game Event.
_Avoid_: Message, response payload, embed, notification

**Cooldown**:
The suppression window following an event during which subsequent occurrences of the same Game Event ID are ignored.
_Avoid_: Throttle, debounce, rate limit

**Broadcast Channel**:
An external chat platform (Twitch chat or Discord webhook) receiving published Reactions.
_Avoid_: Output sink, delivery adapter, stream

**Fallback Reaction**:
A static, pre-written quip selected when the primary dynamic reaction generator (Ollama) is unavailable or times out.
_Avoid_: Default message, backup roast, error message

**Synthetic Event**:
An artificially injected Game Event triggered via developer tools or GUI controls to test reactions and broadcast channels without gameplay.
_Avoid_: Mock event, dummy event, fake trigger

**Bot Personality**:
The stylistic tone (such as sarcastic, hype, or deadpan) that guides the LLM prompt when generating dynamic Reactions.
_Avoid_: Persona config, system prompt, mood mode

**Template Matching**:
Full-screen computer vision comparison against reference asset images to detect visual Game Events without manual bounding box calibration.
_Avoid_: Bounding box search, crop scanning, OCR zone

**Active Game Detection**:
An automatic identification of the running foreground game window to load the corresponding event rules and log tailers without manual switching.
_Avoid_: Manual game switcher, dropdown selector

**OBS Dock**:
The embedded control panel docked directly inside OBS Studio for zero-tab management.
_Avoid_: Web dashboard, control window, admin panel

**Visual Overlay**:
An on-stream OBS Browser Source widget that renders dynamic visual reactions and sound effects during gameplay.
_Avoid_: Stream popup, alert box, notification widget

**Subscription License**:
The recurring commercial authorization token verifying an active subscriber account with heartbeat validation.
_Avoid_: Serial number, product key, purchase code

**Instance Identifier**:
The unique client-generated UUID registered with the Merchant of Record during activation to track per-seat device limits.
_Avoid_: Machine ID, hardware hash, device token

**Offline Grace Period**:
The time-bounded sliding window (7 days) during which an activated client remains fully operational without successfully contacting the licensing server.
_Avoid_: Free trial, offline mode, disconnected bypass

**Merchant of Record**:
The external commercial platform (Lemon Squeezy) assuming legal responsibility for payment processing, subscription management, invoicing, and global tax compliance.
_Avoid_: Payment gateway, payment processor, billing vendor

**One-Click Auth**:
The seamless OAuth connection workflow allowing streamers to authorize their Twitch channel without creating developer applications.
_Avoid_: Manual token copy, dev credentials, API key setup

