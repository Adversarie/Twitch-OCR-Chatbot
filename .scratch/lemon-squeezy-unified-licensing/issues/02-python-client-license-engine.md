Status: resolved
Type: task
Labels: wayfinder:task
Blocked by: 01

## Question

Implement a zero-dependency Python `LicenseManager` module for Twitch OCR Chatbot that connects directly to Lemon Squeezy's public License API (`/v1/licenses/activate`, `/v1/licenses/validate`, `/v1/licenses/deactivate`), manages the unique instance UUID, performs background heartbeat validation every 12 hours, and persists a tamper-resistant 7-day offline grace cache using Windows DPAPI (`CryptProtectData` via `ctypes`) and machine GUID HMAC.

## Answer

Implemented the zero-dependency [`license_manager.py`](file:///c:/Users/matt1/Downloads/Twitch%20OCR%20Chatbot/license_manager.py) module using standard library modules (`ctypes`, `urllib.request`, `json`, `hashlib`, `hmac`, `threading`):

1. **Windows DPAPI Encryption (`_dpapi_encrypt` & `_dpapi_decrypt`)**:
   - Uses native `ctypes.windll.crypt32.CryptProtectData` and `CryptUnprotectData` to encrypt the local cache using OS user-account credentials without external C dependencies like `cryptography`.
2. **Machine-Bound HMAC Integrity**:
   - Signs the cache payload with an HMAC-SHA256 digest keyed against Windows `MachineGuid`, CPU identifier, and hostname to prevent moving license files across machines or editing timestamps.
3. **Public License API Client**:
   - Calls `POST https://api.lemonsqueezy.com/v1/licenses/activate` with `license_key` and `instance_name`.
   - Calls `POST https://api.lemonsqueezy.com/v1/licenses/validate` with `instance_id`.
   - Calls `POST https://api.lemonsqueezy.com/v1/licenses/deactivate` to unbind machine instances cleanly.
4. **Offline Heartbeat Engine**:
   - Runs on a non-blocking background daemon thread (`validate_heartbeat()`) every 12 hours.
   - If network or DNS fails, operates seamlessly in `LICENSED_OFFLINE_GRACE` mode for up to 7 days from `last_validated_at`.
   - Detects system clock rollbacks via high-water mark timestamp comparisons.
5. **Configuration Integration**:
   - Updated [`config.py`](file:///c:/Users/matt1/Downloads/Twitch%20OCR%20Chatbot/config.py) to read `LEMON_SQUEEZY_STORE_ID`, `LEMON_SQUEEZY_PRODUCT_ID`, `LEMON_SQUEEZY_CHECKOUT_URL`, and `LEMON_SQUEEZY_LICENSE_KEY`.
6. **Verification**:
   - Tested DPAPI round-trip encryption, machine fingerprinting, invalid key rejection, and local demo activation/deactivation cycles. All passed.

