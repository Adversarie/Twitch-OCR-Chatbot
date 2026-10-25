Status: resolved
Labels: wayfinder:map

## Destination

A sellable, subscription-gated live streaming companion packaged as an integrated OBS Studio Dock and on-stream Visual Overlay (`/overlay`) with customizable themes and audio alerts, seamless 1-click Twitch OAuth authentication, zero-load curated reaction decks out of the box (with optional BYOK cloud / local LLM), Lemon Squeezy subscription license validation with offline heartbeat caching, and a zero-config Windows executable release artifact.

## Notes

- Domain: Twitch OCR Chatbot, OBS Dock, Visual Overlay, Commercial Licensing, Standalone Windows Distribution.
- Lazy Senior Dev Principles: Zero C++ libobs plugins (use OBS Custom Browser Dock), zero cloud server hosting costs (client-side Lemon Squeezy license validation + 1-click loopback auth), shortest working diffs.
- Skills: `research`, `prototype`, `grilling`, `domain-modeling`.
- Standing preferences: Streamers must never touch Twitch Developer Console or command lines. Zero GPU impact during gameplay by defaulting to curated reaction decks.

## Decisions so far

<!-- the index: one line per closed ticket, enough to judge relevance, then zoom the link for the detail the ticket holds -->

- [01-lemon-squeezy-subscription-licensing](file:///c:/Users/matt1/Downloads/Twitch%20OCR%20Chatbot/.scratch/commercial-release/issues/01-lemon-squeezy-subscription-licensing.md): Adopted Lemon Squeezy public License API with background 12-hour heartbeat validation, 7-day offline grace window, and Windows DPAPI + HMAC-SHA256 encrypted local cache to prevent stream interruption during network flickers.
- [02-one-click-twitch-oauth](file:///c:/Users/matt1/Downloads/Twitch%20OCR%20Chatbot/.scratch/commercial-release/issues/02-one-click-twitch-oauth.md): Adopted Twitch Device Code Flow with Public Client Type and pre-filled activation URLs, enabling 1-click browser authorization, 30-day rolling refresh tokens, zero client secrets, and zero local port/firewall issues.
- [03-visual-overlay-engine](file:///c:/Users/matt1/Downloads/Twitch%20OCR%20Chatbot/.scratch/commercial-release/issues/03-visual-overlay-engine.md): Implemented real-time SSE on-stream overlay (`/overlay`) supporting three selectable themes (Twitch Glass, Cyberpunk Neon, Retro Arcade), synthesized Web Audio SFX, and transparent background for OBS Studio.
- [04-obs-dock-ui-adaptation](file:///c:/Users/matt1/Downloads/Twitch%20OCR%20Chatbot/.scratch/commercial-release/issues/04-obs-dock-ui-adaptation.md): Adapted Web UI to fit responsive narrow OBS docks with collapsible navigation, 1-click "Copy Overlay URL" with theme picker, interactive OBS setup modal, and subscription license badge/activation.
- [05-reaction-engine-curated-decks-and-byok](file:///c:/Users/matt1/Downloads/Twitch%20OCR%20Chatbot/.scratch/commercial-release/issues/05-reaction-engine-curated-decks-and-byok.md): Expanded reaction engine with 506 curated lines across 18 event categories (0% GPU load), context interpolation, and unified BYOK cloud LLM support (Groq/OpenAI) with instant fallback.
- [06-pyinstaller-windows-packaging](file:///c:/Users/matt1/Downloads/Twitch%20OCR%20Chatbot/.scratch/commercial-release/issues/06-pyinstaller-windows-packaging.md): Defined PyInstaller onedir distribution spec (`TwitchOCRBot.spec`), windowless execution (`console=False`), dynamic MEIPASS resource resolver, automated build script (`scripts/build_windows_exe.bat`), and Inno Setup installer (`installer.iss`) for zero-UAC installation.

## Not yet specified

- OBS WebSocket integration: Connecting to OBS WebSocket v5 to automatically pause scanning when stream is stopped and resume when stream goes live.
- Desktop auto-updater: Seamless in-app version check against GitHub releases or Lemon Squeezy product updates.
- Custom streamer audio SFX asset uploader in the OBS Dock.
- Multi-game custom visual template creator in the Web UI.

## Out of scope

- Native C++ `libobs` compiled plugin: Out of scope because OBS Custom Browser Docks and Browser Sources natively support our FastAPI HTML/JS interface without ABI fragility or C++ toolchains.
- Hosted central AI proxy: Out of scope to avoid recurring server/token hosting costs; zero-load curated decks + BYOK (Groq/OpenAI) or local Ollama cover it.
- macOS and Linux release packaging: Out of scope because PoE 1, PoE 2, and WoW streamer demographic is overwhelmingly on Windows.
