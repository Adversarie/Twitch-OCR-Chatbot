## Destination

A zero-calibration detection architecture that eliminates manual bounding boxes by relying on native logs for lifecycle events (deaths, level ups), full-screen OpenCV template matching for unlogged visual events (loot drops, disconnects, out of mana), and automatic active game window detection.

## Notes

- Domain: Twitch OCR Chatbot event detection and automation
- Lazy Senior Dev: Shortest working diff, zero new external pip dependencies (use standard library `ctypes` for Windows foreground window detection, use already-installed `opencv-python` for template matching).
- Zero-Box UX: Streamer never has to calibrate or drag bounding boxes again.
- Out of scope: Audio loopback capture (WASAPI).
- Execution is in-scope for this map.

## Decisions so far

- [01-active-game-detection](file:///C:/Users/matt1/Downloads/Twitch%20OCR%20Chatbot/.scratch/zero-calibration-detection/issues/01-active-game-detection.md): Implemented zero-dependency `GameDetector` using Win32 API to auto-detect and switch between PoE 1, PoE 2, and WoW.
- [02-log-first-event-routing](file:///C:/Users/matt1/Downloads/Twitch%20OCR%20Chatbot/.scratch/zero-calibration-detection/issues/02-log-first-event-routing.md): Auto-discovered native log paths and routed all deaths and level ups exclusively to logs, stripping redundant OCR zones.
- [03-template-matching-engine](file:///C:/Users/matt1/Downloads/Twitch%20OCR%20Chatbot/.scratch/zero-calibration-detection/issues/03-template-matching-engine.md): Implemented `TemplateScanner` with OpenCV `matchTemplate` running in ~5-15ms across full screen, integrated into `OCRScanner`.
- [04-reference-template-assets](file:///C:/Users/matt1/Downloads/Twitch%20OCR%20Chatbot/.scratch/zero-calibration-detection/issues/04-reference-template-assets.md): Packaged reference visual assets in `templates/` and added web endpoints for template previewing.
- [05-web-ui-retirement-of-zone-drawing](file:///C:/Users/matt1/Downloads/Twitch%20OCR%20Chatbot/.scratch/zero-calibration-detection/issues/05-web-ui-retirement-of-zone-drawing.md): Retired manual zone drawing canvas from Web UI, replaced with Visual Templates manager, Overview Event Simulator, and live active game indicator.

## Not yet specified

- Multi-scale template matching optimization if 4K downscaling causes false negatives
- Custom user-uploaded template asset manager in Web UI

## Out of scope

- [Audio Cue Detection](link): Audio loopback capture via WASAPI is out of scope to avoid audio driver dependencies and false positives from background stream music or Discord calls.
