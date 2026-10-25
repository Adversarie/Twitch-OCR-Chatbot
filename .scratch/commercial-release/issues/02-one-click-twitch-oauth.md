Status: resolved
Type: research

## Question

How should 1-click Twitch OAuth authentication be implemented for a local desktop and OBS application so streamers can authorize their channel in a single browser click without creating a Twitch Developer application, managing developer credentials, or manually copying token strings into `.env`? Specifically, what is the best mechanism between a local HTTP loopback receiver (`http://127.0.0.1:8000/api/auth/twitch/callback`), Twitch Device Code Flow (`twitch.tv/activate`), and token persistence/refresh?

## Answer

Resolved via primary-source Twitch Developer documentation investigation ([full research report](file:///c:/Users/matt1/Downloads/Twitch%20OCR%20Chatbot/.scratch/commercial-release/research/one-click-twitch-oauth.md)):

1. **Architecture: Device Code Grant Flow (RFC 8628) with Public Client Type**:
   - Twitch does **not** support PKCE (RFC 7636) for code exchange, making standard code flows impossible without leaking a `client_secret` in client binaries.
   - Twitch Implicit Grant does **not** issue refresh tokens (tokens expire in ~4 hours, requiring repeated logins).
   - Twitch officially recommends **Public Client Type** with Device Code Flow for open platforms (Windows): zero client secrets are required or stored, while rolling refresh tokens are granted.

2. **Zero-Code Streamer Experience (True 1-Click)**:
   - When the streamer clicks "Connect Twitch", the app initiates Device Code Flow and opens the pre-filled verification URI:
     `https://www.twitch.tv/activate?public=true&device-code=<USER_CODE>`
   - The user code is automatically populated by Twitch; the streamer simply clicks **"Authorize"** once in their browser.
   - The app's background polling loop receives the `access_token` and `refresh_token`. Zero inbound ports, zero firewall warnings, and zero redirect URI mismatch errors.

3. **Required Scopes**:
   - `chat:read`, `chat:edit` (for existing IRC `twitchio` bot).
   - `user:read:chat`, `user:write:chat` (for forward-compatible Helix REST / EventSub).

4. **Zero Re-Login & Token Persistence**:
   - Auto-discovers broadcaster name via `GET https://id.twitch.tv/oauth2/validate` (streamer never types channel name).
   - Silent rolling token refresh runs on 4-hour expiry or HTTP 401 via `POST /oauth2/token` with `grant_type=refresh_token`, `client_id`, and `refresh_token`. Refresh tokens remain valid for a rolling 30-day window.
   - Tokens persist in `%APPDATA%\TwitchOCRChatbot\auth.json` (or `.env` during dev).
