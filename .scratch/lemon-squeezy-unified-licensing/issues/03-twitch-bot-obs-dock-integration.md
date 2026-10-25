Status: resolved
Type: prototype
Labels: wayfinder:prototype
Blocked by: 02

## Question

Wire the Python `LicenseManager` into `web.py` to replace the mock `.env` licensing endpoints (`/api/license/status`, `/api/license/activate`, `/api/license/deactivate`), gate commercial OCR scanning so unauthenticated sessions are restricted to setup/preview mode, and update the OBS Dock modal in `static/index.html` with real-time activation feedback, masked key display, and 1-click external browser checkout launch.

## Answer

Integrated [license_manager.py](file:///c:/Users/matt1/Downloads/Twitch%20OCR%20Chatbot/license_manager.py) into [web.py](file:///c:/Users/matt1/Downloads/Twitch%20OCR%20Chatbot/web.py) and [static/index.html](file:///c:/Users/matt1/Downloads/Twitch%20OCR%20Chatbot/static/index.html) with zero external runtime dependencies:

1. **State & Endpoints ([web.py](file:///c:/Users/matt1/Downloads/Twitch%20OCR%20Chatbot/web.py))**:
   - Initialized `state.license_manager = LicenseManager()`.
   - Updated `GET /api/license/status` to return structured display data (`valid`, `state`, `status`, `plan`, `key_masked`, `instance_id`, `grace_days_left`, `checkout_url`).
   - Replaced `POST /api/license/activate` with async non-blocking execution via `asyncio.to_thread` calling `state.license_manager.activate(key, instance_name)` and syncing to `.env` on success.
   - Added `POST /api/license/deactivate` to unbind machine instances on Lemon Squeezy and free up 1 of the 2 workstation seats.
   - Added background heartbeat shutdown to `lifespan` handler.

2. **Commercial Gating ([web.py](file:///c:/Users/matt1/Downloads/Twitch%20OCR%20Chatbot/web.py#L51-L93))**:
   - In `handle_event()`, `state.license_manager.is_feature_authorized()` is checked.
   - When unlicensed (Trial Mode): visual reactions are broadcast to the OBS overlay tagged with `[TRIAL]`, allowing broadcasters to calibrate OBS visual scenes, but live Twitch chat messages (`state.bot.send_chat_message`) and Discord webhooks are blocked.
   - When licensed: live Twitch chat and Discord broadcasts are dispatched immediately.

3. **OBS Dock UI ([static/index.html](file:///c:/Users/matt1/Downloads/Twitch%20OCR%20Chatbot/static/index.html))**:
   - Added compact dock 💎 shortcut button for 300px-wide OBS docks.
   - Enhanced `#license-modal` with real-time validation status, masked key display, device seat indicator (`Seat 1 of 2`), inline error/success messaging, and 1-click external checkout launch (`window.open(checkoutUrl, '_blank')`).
   - Added `Unlink Device` deactivation button with user confirmation to release seats cleanly.

4. **Automated Verification**:
   - Created [test_license_gate.py](file:///c:/Users/matt1/Downloads/Twitch%20OCR%20Chatbot/test_license_gate.py) verifying all 5 gate transitions (unauthenticated trial mode, OCR event trial tagging + chat suppression, key activation, licensed live chat delivery, and deactivation). All tests pass with exit code 0.
