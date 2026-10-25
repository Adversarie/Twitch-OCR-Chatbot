Status: resolved
Type: research

## Question

How does Lemon Squeezy's License API (`/v1/licenses/validate` and `/v1/licenses/activate`) work for recurring subscriptions, what payload parameters and response fields indicate active vs past-due vs cancelled subscriptions, and how should a local Python desktop client implement offline heartbeat caching (e.g. 7-day grace period) so a streamer's live broadcast is never interrupted if their internet flickers or Lemon Squeezy is unreachable?

## Answer

Resolved via primary-source Lemon Squeezy documentation investigation and endpoint verification ([full research report](file:///c:/Users/matt1/Downloads/Twitch%20OCR%20Chatbot/.scratch/commercial-release/research/lemon-squeezy-licensing.md)):

1. **Exact Endpoints & Public Access**:
   - `POST https://api.lemonsqueezy.com/v1/licenses/activate`: Creates an instance UUID and increments `activation_usage`.
   - `POST https://api.lemonsqueezy.com/v1/licenses/validate`: Checks validity of key or specific instance (`instance_id` optional).
   - `POST https://api.lemonsqueezy.com/v1/licenses/deactivate`: Releases an instance UUID (`instance_id` required).
   - Public suite: No administrative API key required. Headers: `Accept: application/json` and `Content-Type: application/x-www-form-urlencoded`. Rate limit: 60 req/min.

2. **Required POST Parameters**:
   - `/activate`: `license_key` (required), `instance_name` (required, e.g. PC hostname).
   - `/validate`: `license_key` (required), `instance_id` (optional; if passed, validates instance).
   - `/deactivate`: `license_key` (required), `instance_id` (required).
   - Missing fields return `422 Unprocessable Entity`; non-existent keys return `404 Not Found`.

3. **Subscription Lifecycle vs. License Status**:
   - **Active:** `valid: true`, `license_key.status: "active"`, with `expires_at` representing the end of the current billing cycle / next renewal.
   - **Cancelled:** During the billing cycle, subscription is `cancelled` but license remains `status: "active"` until `expires_at`. Once cycle ends, status shifts to `expired` and validate returns `valid: false`.
   - **Past-Due (Dunning):** Enters 4-retry 2-week dunning window. Remains active during dunning; if unpaid, subscription transitions to `unpaid` -> `expired`, and license key status automatically flips to `expired`.
   - **Expired / Invalid:** Returns `valid: false`. Key not found returns HTTP 404 (`error: "license_key not found."`). Expired keys return `valid: false`, `error: "This license key is expired."`, `status: "expired"`. Disabled keys return `status: "disabled"`.
   - **Product Guard:** Client must verify `meta.store_id` and `meta.product_id` to prevent cross-product license reuse.

4. **Offline Heartbeat Caching & Streamer Non-Interruption**:
   - **7-Day Sliding Grace Window:** Heartbeat runs every 12 hours in a non-blocking background thread. If network/DNS fails, client operates in `LICENSED_OFFLINE_GRACE` mode up to 7 days from `last_validated_at`.
   - **Local Storage Security:** Encrypted at rest via native Windows DPAPI (`CryptProtectData` via `ctypes`) bound to user account and machine, plus HMAC-SHA256 signature using machine-unique GUID (`MachineGuid`) to prevent file copying or JSON tampering.
   - **Anti-Clock Tampering:** Monotonic delta tracking and high-water mark timestamp comparison detect clock rollbacks.
   - **Zero Broadcast Disruption:** OCR detection engine simply queries `is_feature_authorized()`; network failures produce subtle UI indicators rather than blocking dialogues or stream crashes.
