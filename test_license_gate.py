"""
test_license_gate.py - Automated test suite for Lemon Squeezy licensing gate,
%LOCALAPPDATA% persistence, and 1-Click Twitch Device Code OAuth routes.
Run with: python test_license_gate.py
"""

import asyncio
import os
from unittest.mock import MagicMock, patch
from config import Config, APP_DATA_DIR
from web import (
    state,
    get_license_status,
    activate_license,
    deactivate_license,
    handle_event,
    overlay_subscribers,
    start_twitch_auth,
    poll_twitch_auth_status,
    disconnect_twitch_auth,
)


async def run_licensing_tests():
    # Ensure production mode by default (DEV_MODE unset)
    os.environ.pop("DEV_MODE", None)

    print("[TEST] 1. Initial unauthenticated status...")
    await deactivate_license()
    status = await get_license_status()
    assert status["valid"] is False
    assert status["status"] == "trial"
    print("  -> Passed. Unauthenticated state is Trial Mode.")

    print("[TEST] 2. Commercial event gating (Unlicensed)...")
    q = asyncio.Queue()
    overlay_subscribers.add(q)
    state.is_scanning = True
    state.engine.cooldowns.clear()

    mock_bot = MagicMock()
    mock_bot.send_chat_message = MagicMock()
    state.bot = mock_bot

    await handle_event("poe2_death", "Crucible Boss", source="OCR")
    event_payload = q.get_nowait()
    assert event_payload["licensed"] is False
    assert event_payload["reaction"].startswith("[TRIAL]")
    assert mock_bot.send_chat_message.call_count == 0
    print("  -> Passed. Live Twitch chat blocked and overlay tagged [TRIAL].")

    print("[TEST] 3. Production DEMO-KEY-123 rejection (DEV_MODE unset)...")
    mock_req_prod = MagicMock()
    mock_req_prod.json = MagicMock(return_value=asyncio.Future())
    mock_req_prod.json.return_value.set_result({"license_key": "DEMO-KEY-123"})

    prod_resp = await activate_license(mock_req_prod)
    assert prod_resp["valid"] is False
    assert "disabled in production builds" in prod_resp["message"]
    print("  -> Passed. Production build rejects DEMO-KEY-123 bypass.")

    print("[TEST] 4. Dev-mode DEMO-KEY-123 activation (DEV_MODE=1)...")
    os.environ["DEV_MODE"] = "1"
    mock_req = MagicMock()
    mock_req.json = MagicMock(return_value=asyncio.Future())
    mock_req.json.return_value.set_result({"license_key": "DEMO-KEY-123"})

    act_resp = await activate_license(mock_req)
    assert act_resp["valid"] is True
    assert act_resp["status"] == "active"
    assert act_resp["key_masked"] == "DEMO...-123"
    print("  -> Passed. Key validated and activated under DEV_MODE=1.")

    print("[TEST] 5. Commercial event gating (Licensed)...")
    state.engine.cooldowns.clear()
    fut = asyncio.Future()
    fut.set_result(None)
    mock_bot.send_chat_message = MagicMock(return_value=fut)
    Config.TWITCH_CHANNEL = "demo_streamer"

    await handle_event("poe2_death", "Crucible Boss", source="OCR")
    event_payload_licensed = q.get_nowait()
    assert event_payload_licensed["licensed"] is True
    assert not event_payload_licensed["reaction"].startswith("[TRIAL]")
    assert mock_bot.send_chat_message.call_count == 1
    print("  -> Passed. Live Twitch chat transmitted.")

    print("[TEST] 6. %LOCALAPPDATA% mutable storage paths...")
    assert Config.ENV_FILE.parent == APP_DATA_DIR
    assert Config.ZONES_FILE.parent == APP_DATA_DIR
    assert Config.LOG_FILE.parent == APP_DATA_DIR
    assert APP_DATA_DIR.exists()
    print(f"  -> Passed. AppData storage verified at {APP_DATA_DIR}.")

    print("[TEST] 7. 1-Click Twitch Device Code OAuth flow...")
    with patch.object(state.twitch_auth, "_post_form") as mock_post_form, \
         patch.object(state.twitch_auth, "_validate_token") as mock_validate, \
         patch("web.webbrowser.open") as mock_browser:
        # Step A: Start Device Code flow; first _post_form is /oauth2/device,
        # second is /oauth2/token (pending), third is /oauth2/token (approved)
        mock_post_form.side_effect = [
            (
                200,
                {
                    "device_code": "dev_code_abc123",
                    "user_code": "ABCD-EFGH",
                    "verification_uri": "https://www.twitch.tv/activate",
                    "expires_in": 1800,
                    "interval": 0,
                },
            ),
            (400, {"message": "authorization_pending"}),
            (
                200,
                {
                    "access_token": "mock_access_token_xyz",
                    "refresh_token": "mock_refresh_token_xyz",
                },
            ),
        ]
        mock_validate.return_value = (200, {"login": "exile_streamer"})

        start_resp = await start_twitch_auth()
        assert start_resp["status"] == "pending"
        assert start_resp["user_code"] == "ABCD-EFGH"
        assert "device-code=ABCD-EFGH" in start_resp["verification_uri"]
        assert mock_browser.called

        # Wait for the background _poll_task to finish its two poll cycles (interval=0)
        if state.twitch_auth._poll_task:
            await asyncio.wait_for(state.twitch_auth._poll_task, timeout=5.0)

        poll_success = await poll_twitch_auth_status()
        assert poll_success["status"] == "connected"
        assert poll_success["channel"] == "exile_streamer"
        assert Config.TWITCH_OAUTH_TOKEN == "oauth:mock_access_token_xyz"
        assert Config.TWITCH_CHANNEL == "exile_streamer"

        # Step D: Disconnect
        disc_resp = await disconnect_twitch_auth()
        assert disc_resp["status"] == "disconnected"
        assert Config.TWITCH_OAUTH_TOKEN == ""
    print("  -> Passed. 1-Click Twitch Device Code OAuth lifecycle verified.")

    print("[TEST] 8. License deactivation...")
    deact_resp = await deactivate_license()
    assert deact_resp["valid"] is False
    assert deact_resp["status"] == "trial"
    os.environ.pop("DEV_MODE", None)
    print("  -> Passed. Device unlinked and returned to Trial Mode.")

    overlay_subscribers.discard(q)
    print("\n[SUCCESS] All 8 licensing, AppData, and 1-Click Twitch OAuth test cases passed cleanly!")


if __name__ == "__main__":
    asyncio.run(run_licensing_tests())

