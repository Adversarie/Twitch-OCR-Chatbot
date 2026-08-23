Status: resolved
Labels: wayfinder:map

## Destination

A hybrid event detection system that combines visual OCR with native game log tailing (PoE `Client.txt` and WoW `/combatlog`) to extract high-fidelity context for chat reactions.

## Notes

- Domain: Game Log Parsing, File Tailing, Hybrid Event Dispatching.
- Preferences: Rely on native logs over addons. Fallback to OCR only when logs lack the event.
- Skills: `research`, `domain-modeling`.

## Decisions so far

- [01-poe-logs](file:///c:/Users/matt1/Downloads/Twitch%20OCR%20Chatbot/.scratch/log-integration/issues/01-poe-logs.md): PoE natively logs deaths, level ups, and areas, but NOT drops or boss kills. Regex captured in research.
- [02-wow-logs](file:///c:/Users/matt1/Downloads/Twitch%20OCR%20Chatbot/.scratch/log-integration/issues/02-wow-logs.md): WoW logs everything cleanly via combat/chat logs, but the chat log buffers. Regex captured in research.
- [03-log-watcher](file:///c:/Users/matt1/Downloads/Twitch%20OCR%20Chatbot/.scratch/log-integration/issues/03-log-watcher.md): Implemented async file-tailing module parsing PoE and WoW regexes.
- [04-hybrid-integration](file:///c:/Users/matt1/Downloads/Twitch%20OCR%20Chatbot/.scratch/log-integration/issues/04-hybrid-integration.md): Resolved. Rely on existing `ReactionEngine` cooldowns to naturally de-duplicate identical events fired by both Log and OCR scanners.
- [05-app-integration](file:///c:/Users/matt1/Downloads/Twitch%20OCR%20Chatbot/.scratch/log-integration/issues/05-app-integration.md): Added `LogWatcher` async loop to `main.py` and exposed the three log file paths in `gui.py` settings.
- [06-ollama-context](file:///c:/Users/matt1/Downloads/Twitch%20OCR%20Chatbot/.scratch/log-integration/issues/06-ollama-context.md): Updated Ollama prompt to explicitly roast item names, achievements, or boss names if they exist in the context string.

## Not yet specified

*(Empty)*

## Out of scope

- Building custom WoW Lua addons.
- Reading game memory directly.
