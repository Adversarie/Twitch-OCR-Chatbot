Status: resolved
Assignee: agent
Type: prototype
Blocked by: 03

## Question

How should the existing Tailwind Web UI be adapted into an integrated OBS Dock view, featuring a compact responsive layout suitable for narrow OBS panels, a 1-click "Copy Overlay URL" button, subscription license status indicator, and an interactive step-by-step modal guiding streamers on how to add the custom browser dock into OBS Studio?

## Answer

Resolved by implementing a fully responsive OBS-ready layout in `static/index.html` and backing endpoints in `web.py`:

1. **Responsive OBS Dock Shell**:
   - Re-architected layout from rigid desktop sidebar to flex-responsive grid: on narrow widths (300px–450px OBS docks), the sidebar collapses into a sleek top header with compact tab navigation pills, scanner status indicator, and full-width card layout.

2. **OBS Live Stream Suite Controls**:
   - Added dedicated OBS Browser Source Overlay panel in the Overview tab.
   - Live theme dropdown allowing streamers to switch between Twitch Glass, Cyberpunk Neon, and Retro Arcade RPG Box on the fly.
   - One-click **"Copy Overlay URL"** button that copies `http://127.0.0.1:8000/overlay?theme=<theme>` to clipboard with instant visual confirmation.
   - One-click **"Test Preview"** button opening `http://127.0.0.1:8000/overlay?preview=true` for browser auditioning.

3. **OBS Dock Setup Guide Modal**:
   - Interactive modal providing a 3-step guide for OBS Studio:
     1. Open OBS Studio -> Menu: **Docks** -> **Custom Browser Docks...**
     2. Set Dock Name: `Twitch OCR Bot`, URL: `http://127.0.0.1:8000`.
     3. Click **Apply** and drag dock into OBS Studio workspace!
   - Includes quick-copy button for the dock URL.

4. **Subscription License Badge & Modal**:
   - Sidebar/footer badge displaying current license plan (`💎 Pro Subscriber` or `⚡ Free Trial Mode`).
   - Modal interface allowing streamers to enter their Lemon Squeezy license key, validated and persisted via `/api/license/activate` and `/api/license/status`.

5. **Twitch Channel Status Badge**:
   - Displays real-time broadcaster status (`@<channel>`) via `/api/twitch/status`.
