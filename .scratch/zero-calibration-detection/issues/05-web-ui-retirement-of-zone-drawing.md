---
type: wayfinder:task
status: closed
assignee: agent
blocked_by:
  - 01-active-game-detection
  - 02-log-first-event-routing
  - 03-template-matching-engine
  - 04-reference-template-assets
---

## Question

How should the Web UI be updated to remove the tedious manual zone drawing canvas and replace it with active game status indicators, active visual template previews, and test simulation controls?

## Resolution

1. **Retired Zone Drawing Canvas:** Removed the manual bounding-box drawing `<canvas>`, drag-to-draw mouse event listeners, screenshot capture button, and legacy zone coordinate persistence.
2. **Added Visual Templates Tab:** Replaced "OCR Zones" with "Visual Templates" in the sidebar navigation. Loads dynamic cards from `/api/templates` showing the game title, image preview, event ID, matching threshold, and quick "Test" button.
3. **Added Event Simulator Panel:** Added an interactive event tester directly onto the Overview dashboard tab (`#sim-event`, `#sim-context`, and "Fire Event" button), allowing instantaneous testing of any event across PoE 1, PoE 2, and WoW via `POST /api/simulate-event`.
4. **Active Game Status Display:** Wired the sidebar's `#active-game-badge` to real-time polling of `/api/bot/status` to display the foreground detected game (PoE 1, PoE 2, or WoW).
5. **Standardized Webhook Dispatch:** Replaced external uninstalled `requests` calls with standard library `urllib.request` in `web.py` and `main.py`.
