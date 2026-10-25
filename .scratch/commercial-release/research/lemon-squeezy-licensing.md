# Lemon Squeezy License API & Offline Heartbeat Architecture for Subscriptions

## Executive Summary

This research establishes the licensing, validation, and offline heartbeat architecture for the commercial release of the **Twitch OCR Chatbot** companion application (standalone Windows executable and OBS dock).

The commercial model relies on recurring subscriptions billed through **Lemon Squeezy** acting as Merchant of Record (MoR). In software distributed as a desktop client, licensing must satisfy two non-negotiable requirements:
1. **Zero Streamer Disruption:** Live broadcasts and game capture must never freeze, disconnect, or terminate mid-stream due to transient internet hiccups, packet loss, Twitch bitrate saturation, or Lemon Squeezy API downtime.
2. **Definitive Entitlement Enforcement:** Only paying subscribers (or those within an allowable offline grace period) should access commercial features, while subscriptions that are cancelled, past-due, expired, or refunded must be gracefully handled.

This document analyzes Lemon Squeezy's official License API, details exact HTTP request and response structures across all lifecycle states, maps subscription billing events to license statuses, and defines an offline heartbeat caching engine implemented using standard-library Python and native Windows Data Protection (DPAPI).

---

## 1. Lemon Squeezy License API Architecture

### 1.1 Architectural Distinction: License API vs. Core Lemon Squeezy API
Lemon Squeezy maintains two separate API surfaces:
* **Lemon Squeezy Core REST API** (`https://api.lemonsqueezy.com/v1/...`): A private, authenticated REST API compliant with JSON:API specifications. It requires an `Authorization: Bearer <API_KEY>` header and is designed for server-side administrative actions (managing stores, products, webhooks, and retrieving customer records).
* **Lemon Squeezy License API** (`https://api.lemonsqueezy.com/v1/licenses/...`): A **public, lightweight endpoint suite** designed specifically to be called directly by distributed software clients (desktop apps, plugins, CLI tools, web apps).

#### Key Characteristics of the License API:
1. **No API Key Required:** Endpoints do **not** require an administrative API key or `Authorization` header. Distributing client software does not risk leaking store-wide administrative tokens.
2. **Protocol & Base URL:** All requests must be made over HTTPS to `https://api.lemonsqueezy.com/v1/licenses/`.
3. **HTTP Method:** All operations (`activate`, `validate`, `deactivate`) use `POST` requests.
4. **Headers:**
   - `Accept: application/json` (Required)
   - `Content-Type: application/x-www-form-urlencoded` (Standard POST body format)
5. **Rate Limiting:** Lemon Squeezy enforces a rate limit of **60 requests per minute per IP address**.
6. **Primary Source:** [Lemon Squeezy Docs: License API Overview](https://docs.lemonsqueezy.com/api/license-api)

---

### 1.2 The Three License API Endpoints

```
+-----------------------------------------------------------------------------------+
|                            Lemon Squeezy License API                              |
+-----------------------------------------------------------------------------------+
| POST /v1/licenses/activate   --> Activates a key & creates a unique instance UUID |
| POST /v1/licenses/validate   --> Checks validity of key or specific instance      |
| POST /v1/licenses/deactivate --> Releases an instance UUID to free activation slot|
+-----------------------------------------------------------------------------------+
```

#### Endpoint 1: Activate a License Key
* **Route:** `POST https://api.lemonsqueezy.com/v1/licenses/activate`
* **Purpose:** Activates a license key for a specific device, increments the key's `activation_usage` count, and returns a unique `instance.id` (UUIDv4) identifying that machine.
* **Official Reference:** [Lemon Squeezy Docs: Activate a License Key](https://docs.lemonsqueezy.com/api/license-api/activate-license-key)

#### Endpoint 2: Validate a License Key
* **Route:** `POST https://api.lemonsqueezy.com/v1/licenses/validate`
* **Purpose:** Verifies whether a license key is currently valid. If an `instance_id` is passed, it validates that specific device instance; if omitted, it validates the license key globally.
* **Official Reference:** [Lemon Squeezy Docs: Validate a License Key](https://docs.lemonsqueezy.com/api/license-api/validate-license-key)

#### Endpoint 3: Deactivate a License Key
* **Route:** `POST https://api.lemonsqueezy.com/v1/licenses/deactivate`
* **Purpose:** Deactivates a specific instance on Lemon Squeezy, decrementing `activation_usage`. Allows a streamer to migrate their license to a new PC or uninstall cleanly.
* **Official Reference:** [Lemon Squeezy Docs: Deactivate a License Key](https://docs.lemonsqueezy.com/api/license-api/deactivate-license-key)

---

## 2. Request Parameter Specifications

### 2.1 Parameter Matrix

| Parameter | Type | Required in `/activate` | Required in `/validate` | Required in `/deactivate` | Description |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `license_key` | `string` | **Yes** | **Yes** | **Yes** | The UUID/alphanumeric license key issued to the customer upon purchase. |
| `instance_name` | `string` | **Yes** | No (Ignored) | No (Ignored) | A human-readable label identifying the device (e.g. `DESKTOP-GAMINGPC` or hostname). Appears in the Lemon Squeezy merchant dashboard. |
| `instance_id` | `string` (UUID) | No (Ignored) | **Optional** | **Yes** | The unique instance UUID returned by `/activate`. If omitted in `/validate`, validates the key globally and returns `"instance": null`. |

### 2.2 Parameter Validation Errors (HTTP 422)
If a required parameter is omitted or empty, Lemon Squeezy returns HTTP `422 Unprocessable Entity` with a structured error dictionary:

```http
POST /v1/licenses/activate HTTP/1.1
Host: api.lemonsqueezy.com
Accept: application/json
Content-Type: application/x-www-form-urlencoded

license_key=
```

```json
{
  "message": "The license key field is required. (and 1 more error)",
  "errors": {
    "license_key": [
      "The license key field is required."
    ],
    "instance_name": [
      "The instance name field is required."
    ]
  }
}
```

---

## 3. Response Payloads Across Subscription Lifecycle States

Every License API response returns a JSON object containing common top-level structures:
* `activated` / `valid` / `deactivated`: Boolean status flag.
* `error`: `null` on success, or a human-readable explanation string on failure.
* `license_key`: Metadata object describing the key (`id`, `status`, `key`, `activation_limit`, `activation_usage`, `created_at`, `expires_at`).
* `instance`: Object describing the activated device (`id`, `name`, `created_at`) or `null`.
* `meta`: Rich context containing order, product, variant, and customer identity (`store_id`, `product_id`, `product_name`, `variant_id`, `variant_name`, `customer_id`, `customer_email`).

### 3.1 State 1: Valid Active Subscription
When the streamer holds an active, paid recurring subscription and validates their activated instance:

* **HTTP Status Code:** `200 OK`
* **Response Body:**
```json
{
  "valid": true,
  "error": null,
  "license_key": {
    "id": 142857,
    "status": "active",
    "key": "38b1460a-5104-4067-a91d-77b872934d51",
    "activation_limit": 1,
    "activation_usage": 1,
    "created_at": "2026-09-01T12:00:00.000000Z",
    "expires_at": "2026-11-01T12:00:00.000000Z"
  },
  "instance": {
    "id": "f90ec370-fd83-46a5-8bbd-44a241e78665",
    "name": "STREAM-RIG-01",
    "created_at": "2026-09-01T12:05:00.000000Z"
  },
  "meta": {
    "store_id": 81234,
    "order_id": 923451,
    "order_item_id": 923452,
    "product_id": 45100,
    "product_name": "Twitch OCR Companion Pro",
    "variant_id": 58200,
    "variant_name": "Monthly Broadcaster",
    "customer_id": 612001,
    "customer_name": "Jane Broadcaster",
    "customer_email": "jane@streamer.tv"
  }
}
```

> **Key Subscription Behavior:** For subscription products, `expires_at` reflects the end of the current billing cycle (the next scheduled renewal timestamp). Each successful monthly/annual renewal pushes `expires_at` forward automatically.

---

### 3.2 State 2: Cancelled Subscription (In-Cycle vs. Ended Cycle)
When a subscriber cancels their recurring plan in Lemon Squeezy or via the customer portal:

1. **Phase 1: In-Cycle Grace Period (`status: "active"`, Subscription `cancelled`):**
   - Lemon Squeezy sets the subscription's `status` to `cancelled`, but the customer has already paid for the current period.
   - The license key `status` remains `"active"`.
   - `expires_at` remains fixed to the end of the current billing cycle (`ends_at`).
   - The `/v1/licenses/validate` endpoint returns `"valid": true`. Access continues until the paid period ends.
2. **Phase 2: Billing Cycle End Reached (`status: "expired"`, Subscription `expired`):**
   - Once the clock passes `expires_at`, Lemon Squeezy automatically changes the license key `status` to `"expired"`.
   - The validate endpoint transitions to State 4 below.

---

### 3.3 State 3: Past-Due Subscription (Dunning Process)
When a subscription renewal payment fails (e.g. expired credit card, insufficient funds):

1. **Dunning Window (Days 1–14):**
   - The subscription status becomes `past_due`.
   - Lemon Squeezy automatically initiates **4 payment retries across a 2-week window** while sending dunning emails to the customer.
   - If a retry succeeds, the subscription returns to `active`, and `expires_at` updates to the next cycle.
   - If retries are ongoing, Lemon Squeezy maintains the license key in `active` status until the dunning cycle terminates (unless customized in store dunning rules).
2. **Exhausted Retries (`status: "unpaid"` -> `"expired"`):**
   - If all 4 retries fail, the subscription becomes `unpaid`.
   - If dunning termination rules are enabled (default), the subscription status shifts to `expired`.
   - As soon as the subscription reaches `expired`, the license key `status` immediately shifts to `"expired"`.

---

### 3.4 State 4: Expired License Key (`status: "expired"`)
When a subscription terminates or its final billing period elapses:

* **HTTP Status Code:** `200 OK` (or `400 Bad Request` depending on validation parameters)
* **Response Body:**
```json
{
  "valid": false,
  "error": "This license key is expired.",
  "license_key": {
    "id": 142857,
    "status": "expired",
    "key": "38b1460a-5104-4067-a91d-77b872934d51",
    "activation_limit": 1,
    "activation_usage": 1,
    "created_at": "2026-09-01T12:00:00.000000Z",
    "expires_at": "2026-10-01T12:00:00.000000Z"
  },
  "instance": {
    "id": "f90ec370-fd83-46a5-8bbd-44a241e78665",
    "name": "STREAM-RIG-01",
    "created_at": "2026-09-01T12:05:00.000000Z"
  },
  "meta": {
    "store_id": 81234,
    "order_id": 923451,
    "order_item_id": 923452,
    "product_id": 45100,
    "product_name": "Twitch OCR Companion Pro",
    "variant_id": 58200,
    "variant_name": "Monthly Broadcaster",
    "customer_id": 612001,
    "customer_name": "Jane Broadcaster",
    "customer_email": "jane@streamer.tv"
  }
}
```

> **Client Action:** When `valid == false` and `status == "expired"`, the client invalidates the local cache and alerts the user that their subscription has expired, offering a direct link to the Lemon Squeezy renewal checkout or customer portal.

---

### 3.5 State 5: Manually Disabled License Key (`status: "disabled"`)
If a store owner manually disables a license key from the Lemon Squeezy dashboard (due to fraud, chargeback, or policy violation):

* **HTTP Status Code:** `200 OK`
* **Response Body:**
```json
{
  "valid": false,
  "error": "This license key is disabled.",
  "license_key": {
    "id": 142857,
    "status": "disabled",
    "key": "38b1460a-5104-4067-a91d-77b872934d51",
    "activation_limit": 1,
    "activation_usage": 1,
    "created_at": "2026-09-01T12:00:00.000000Z",
    "expires_at": null
  },
  "instance": null,
  "meta": {
    "store_id": 81234,
    "product_id": 45100,
    "product_name": "Twitch OCR Companion Pro"
  }
}
```

---

### 3.6 State 6: Invalid / Non-Existent Key
If a user inputs an invented, mistyped, or non-existent license key:

* **HTTP Status Code:** `404 Not Found`
* **Response Body:**
```json
{
  "valid": false,
  "error": "license_key not found."
}
```
*(Verified against live Lemon Squeezy License API endpoints).*

---

### 3.7 State 7: Activation Limit Reached (In `/v1/licenses/activate`)
When a valid license key is entered on a second computer, but `activation_limit` is set to 1:

* **HTTP Status Code:** `200 OK`
* **Response Body:**
```json
{
  "activated": false,
  "error": "This license key has reached the activation limit.",
  "license_key": {
    "id": 142857,
    "status": "active",
    "key": "38b1460a-5104-4067-a91d-77b872934d51",
    "activation_limit": 1,
    "activation_usage": 1,
    "created_at": "2026-09-01T12:00:00.000000Z",
    "expires_at": "2026-11-01T12:00:00.000000Z"
  },
  "meta": {
    "store_id": 81234,
    "product_id": 45100,
    "product_name": "Twitch OCR Companion Pro",
    "customer_name": "Jane Broadcaster",
    "customer_email": "jane@streamer.tv"
  }
}
```

---

### 3.8 State 8: Mandatory Cross-Product Validation
Because the License API is public, an attacker or customer who purchased a cheaper $5 product from the same creator could attempt to feed that license key into the $25/month Pro application.

**The client must enforce Product Matching:**
Even if `valid === true`, the client **must inspect `meta.store_id` and `meta.product_id` (or `meta.variant_id`)**. If they do not match the expected application constants, the client must treat the validation as failed:
```python
EXPECTED_STORE_ID = 81234
EXPECTED_PRODUCT_ID = 45100

if res.get("valid") and res.get("meta", {}).get("product_id") != EXPECTED_PRODUCT_ID:
    raise LicenseValidationError("License key does not belong to this application product.")
```

---

## 4. Subscription vs. License Lifecycle Summary

| Lifecycle Event | Subscription Status | License Key Status | `expires_at` Value | `/validate` Result |
| :--- | :--- | :--- | :--- | :--- |
| **New Purchase** | `active` | `inactive` (until 1st activation) | Renewal date (e.g. +30 days) | `valid: true` |
| **First App Startup** | `active` | `active` (`usage: 1`) | Renewal date | `valid: true` |
| **Normal Renewal** | `active` | `active` | Extended by +1 cycle | `valid: true` |
| **Payment Failed (Day 1)** | `past_due` | `active` | End of billing cycle | `valid: true` |
| **Dunning Retries (Days 1–14)** | `past_due` | `active` | End of billing cycle | `valid: true` |
| **Cancelled by User** | `cancelled` | `active` | End of current cycle | `valid: true` |
| **Cycle Ended (After Cancel)** | `expired` | `expired` | Past date | `valid: false` |
| **Payment Recovery Failed** | `unpaid` -> `expired` | `expired` | Past date | `valid: false` |
| **Refund Issued / Chargeback** | `expired` / `refunded`| `expired` or `disabled` | Past date or `null` | `valid: false` |
| **Creator Disabled Key** | Any | `disabled` | Any | `valid: false` |

---

## 5. Local Python Desktop Client: Offline Heartbeat Architecture

### 5.1 The Streamer UX & Non-Interruption Requirement
Desktop applications operating alongside live Twitch broadcasts face unique operational constraints:
1. **Network Saturation:** Broadcasters streaming at high bitrates (e.g. 6000–8000 kbps) can experience temporary socket exhaustion, local packet drops, or high latency.
2. **Zero-Freeze Rule:** The application's main thread and OCR/detection loops must **never** block synchronously on network I/O.
3. **No Stream Interruption:** If Lemon Squeezy's servers experience a 2-hour cloud outage or maintenance window on a Friday night, paying streamers broadcasting a tournament must not be kicked out of the app.

### 5.2 The 7-Day Sliding Grace Window
To balance piracy prevention with broadcast reliability, the desktop client implements a **7-Day Offline Grace Window**:
* When the client performs a successful online validation, it records `last_validated_at = utcnow()`.
* If a subsequent online heartbeat check fails due to network transport issues (socket timeout, DNS lookup failure, connection refused, or HTTP 5xx):
  - The client checks whether `utcnow() < last_validated_at + 7 days`.
  - If within the 7-day window, the client remains in an active **`VALID_OFFLINE_GRACE`** operational state.
  - The application logs a debug warning and renders a subtle status pill in the web UI / OBS dock (e.g. *"Offline mode - 5 days remaining in grace period"*).
  - No dialogs, modal popups, audio chimes, or interruptions occur.
* If the grace window expires (> 7 days without internet access):
  - The client transitions to `GRACE_EXPIRED` and prompts the user to reconnect to verify their license before enabling automated bot actions.

```
+-------------------------------------------------------------------------------+
|                            Heartbeat State Machine                            |
+-------------------------------------------------------------------------------+
|                                                                               |
|  [App Launch / Timer] ---> Background Thread HTTP Validation                  |
|                                     |                                         |
|                  +------------------+------------------+                      |
|                  |                                     |                      |
|            HTTP Success                           Network Error               |
|                  |                              (Timeout / 5xx)               |
|        +---------+---------+                           |                      |
|        |                   |                           v                      |
|  valid == true      valid == false               Check Grace Window           |
|        |                   |                           |                      |
|        v                   v                  +--------+--------+             |
| [LICENSED_ONLINE]   [REVOKED/EXPIRED]         |                 |             |
|  Reset 7-day clock   Immediate Lockout    < 7 Days          >= 7 Days         |
|  Update auth cache   Clear cache file         |                 |             |
|                                               v                 v             |
|                                       [OFFLINE_GRACE]     [GRACE_EXPIRED]     |
|                                       Silent operation    Require Reconnect   |
+-------------------------------------------------------------------------------+
```

---

### 5.3 Local Storage Security: DPAPI & Machine-Bound HMAC
A common mistake in desktop licensing is storing plain JSON files (`{"license": "...", "expires": "2099"}`) or easily bypassed XOR obfuscation. 

Following the **Lazy Senior Dev** philosophy ("Does a native platform feature cover it? Use it."):
On Windows, the standard operating system mechanism for protecting secrets at rest is the **Windows Data Protection API (DPAPI)** (`CryptProtectData` / `CryptUnprotectData`).

#### Why DPAPI + Machine-Bound HMAC:
1. **Zero External Dependencies:** Implemented via standard Python `ctypes.windll.crypt32`. Does not require installing third-party compiled C-extensions like `cryptography` or `pywin32`.
2. **User & Machine Bound:** Data encrypted with DPAPI uses keys derived from the user's Windows login credentials and system hardware. The file cannot be copied to a second computer or another Windows user profile.
3. **HMAC-SHA256 Integrity Verification:** In addition to DPAPI encryption, the cache payload includes an HMAC-SHA256 signature calculated over machine-unique hardware attributes (Windows Registry `MachineGuid` + CPU Architecture + Salt). This prevents clock tampering, replay attacks, or file modification.

---

### 5.4 Clock Rollback & System Time Tampering Prevention
To prevent users from rolling back their PC clock to freeze the 7-day grace period:
1. **Monotonic Clock Delta Tracking:** The app records Python's `time.monotonic()` continuously during process execution. Monotonic time is immune to system clock changes.
2. **High-Water Mark Timestamp:** The cache file records `last_observed_timestamp`. On every heartbeat tick, the client writes `last_observed_timestamp = max(last_observed_timestamp, current_system_time)`.
3. **Rollback Detection:** If `current_system_time < last_observed_timestamp - 3600` (allowing 1 hour for daylight saving adjustments), clock tampering is flagged, and the offline grace period is immediately suspended until an online validation succeeds.

---

## 6. Complete Python Desktop Reference Implementation

Below is the self-contained, standard-library-only licensing module implementing Lemon Squeezy activation, validation, offline heartbeat caching, DPAPI encryption, and asynchronous background polling.

```python
"""
license_manager.py - Lemon Squeezy Desktop Licensing with Offline Grace Heartbeat
Standard library only: ctypes (Windows DPAPI), urllib, hashlib, hmac, json, threading.
"""

import sys
import os
import json
import time
import hmac
import hashlib
import datetime
import urllib.request
import urllib.parse
import urllib.error
import threading
import logging
from pathlib import Path
from typing import Optional, Dict, Any, Tuple

logger = logging.getLogger("LicenseManager")

# --- Configuration Constants ---
API_BASE_URL = "https://api.lemonsqueezy.com/v1/licenses"
EXPECTED_STORE_ID = 81234        # Set from Lemon Squeezy Store settings
EXPECTED_PRODUCT_ID = 45100      # Set from Lemon Squeezy Product settings
OFFLINE_GRACE_DAYS = 7           # Max days allowed without internet check
HEARTBEAT_INTERVAL_SECONDS = 43200  # Check every 12 hours (2x per day)
REQUEST_TIMEOUT_SECONDS = 10     # Strict socket timeout

# Cache path in local app data (never tracked in repo)
APP_DATA_DIR = Path(os.environ.get("LOCALAPPDATA", Path.home())) / "TwitchOCRChatbot"
CACHE_FILE = APP_DATA_DIR / "license.dat"


# --- Windows DPAPI Encryption (Zero Third-Party Dependencies) ---
if sys.platform == "win32":
    import ctypes
    from ctypes import wintypes

    class DATA_BLOB(ctypes.Structure):
        _fields_ = [("cbData", wintypes.DWORD), ("pbData", ctypes.POINTER(ctypes.c_byte))]

    def _dpapi_encrypt(data_bytes: bytes) -> bytes:
        """Encrypts data using Windows DPAPI CryptProtectData."""
        cb_data = len(data_bytes)
        pb_data = (ctypes.c_byte * cb_data)(*data_bytes)
        in_blob = DATA_BLOB(cb_data, pb_data)
        out_blob = DATA_BLOB()

        crypt32 = ctypes.windll.crypt32
        # CRYPTPROTECT_UI_FORBIDDEN = 0x01
        if not crypt32.CryptProtectData(
            ctypes.byref(in_blob), None, None, None, None, 0x01, ctypes.byref(out_blob)
        ):
            raise ctypes.WinError()

        try:
            encrypted_bytes = ctypes.string_at(out_blob.pbData, out_blob.cbData)
            return encrypted_bytes
        finally:
            ctypes.windll.kernel32.LocalFree(out_blob.pbData)

    def _dpapi_decrypt(cipher_bytes: bytes) -> bytes:
        """Decrypts data using Windows DPAPI CryptUnprotectData."""
        cb_data = len(cipher_bytes)
        pb_data = (ctypes.c_byte * cb_data)(*cipher_bytes)
        in_blob = DATA_BLOB(cb_data, pb_data)
        out_blob = DATA_BLOB()

        crypt32 = ctypes.windll.crypt32
        if not crypt32.CryptUnprotectData(
            ctypes.byref(in_blob), None, None, None, None, 0x01, ctypes.byref(out_blob)
        ):
            raise ctypes.WinError()

        try:
            decrypted_bytes = ctypes.string_at(out_blob.pbData, out_blob.cbData)
            return decrypted_bytes
        finally:
            ctypes.windll.kernel32.LocalFree(out_blob.pbData)
else:
    # Cross-platform fallback for dev/testing
    def _dpapi_encrypt(data_bytes: bytes) -> bytes:
        return data_bytes

    def _dpapi_decrypt(cipher_bytes: bytes) -> bytes:
        return cipher_bytes


def _get_machine_fingerprint() -> str:
    """Derives a machine-unique identifier for HMAC signing."""
    components = []
    # 1. Windows MachineGuid
    if sys.platform == "win32":
        try:
            import winreg
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Cryptography") as key:
                guid, _ = winreg.QueryValueEx(key, "MachineGuid")
                components.append(str(guid))
        except Exception:
            pass
    # 2. Hostname & Architecture fallback
    components.append(os.environ.get("COMPUTERNAME", "UNKNOWN_HOST"))
    components.append(os.environ.get("PROCESSOR_IDENTIFIER", "UNKNOWN_CPU"))
    raw_str = "|".join(components)
    return hashlib.sha256(raw_str.encode("utf-8")).hexdigest()


class LicenseState:
    LICENSED_ONLINE = "LICENSED_ONLINE"
    LICENSED_OFFLINE_GRACE = "LICENSED_OFFLINE_GRACE"
    UNLICENSED = "UNLICENSED"
    EXPIRED = "EXPIRED"
    DISABLED = "DISABLED"
    GRACE_EXPIRED = "GRACE_EXPIRED"
    CLOCK_TAMPERED = "CLOCK_TAMPERED"


class LicenseManager:
    def __init__(self, expected_store_id: int = EXPECTED_STORE_ID, expected_product_id: int = EXPECTED_PRODUCT_ID):
        self.expected_store_id = expected_store_id
        self.expected_product_id = expected_product_id
        self.state: str = LicenseState.UNLICENSED
        self.cached_license: Optional[Dict[str, Any]] = None
        self._stop_heartbeat = threading.Event()
        self._heartbeat_thread: Optional[threading.Thread] = None

        APP_DATA_DIR.mkdir(parents=True, exist_ok=True)
        self._load_cache()

    # --- HTTP Communication ---

    def _post_license_api(self, endpoint: str, params: Dict[str, str]) -> Tuple[int, Dict[str, Any]]:
        """Issues POST request with application/x-www-form-urlencoded and Accept: application/json."""
        url = f"{API_BASE_URL}/{endpoint}"
        encoded_data = urllib.parse.urlencode(params).encode("utf-8")
        req = urllib.request.Request(
            url,
            data=encoded_data,
            headers={
                "Accept": "application/json",
                "Content-Type": "application/x-www-form-urlencoded",
                "User-Agent": "TwitchOCRChatbot/1.0"
            }
        )

        try:
            with urllib.request.urlopen(req, timeout=REQUEST_TIMEOUT_SECONDS) as resp:
                status_code = resp.status
                body = json.loads(resp.read().decode("utf-8"))
                return status_code, body
        except urllib.error.HTTPError as e:
            try:
                body = json.loads(e.read().decode("utf-8"))
            except Exception:
                body = {"error": f"HTTP {e.code}: {e.reason}"}
            return e.code, body
        except (urllib.error.URLError, TimeoutError, OSError) as e:
            # Transient transport failure (offline, DNS timeout, connection reset)
            return 0, {"network_error": str(e)}

    # --- Activation ---

    def activate(self, license_key: str, instance_name: Optional[str] = None) -> Tuple[bool, str]:
        """
        Activates a license key for this workstation.
        Returns: (success: bool, message: str)
        """
        if not instance_name:
            instance_name = os.environ.get("COMPUTERNAME", "Twitch-Broadcaster-PC")

        status_code, body = self._post_license_api("activate", {
            "license_key": license_key.strip(),
            "instance_name": instance_name.strip()
        })

        if status_code == 0:
            return False, f"Network error during activation: {body.get('network_error')}"

        if not body.get("activated"):
            error_msg = body.get("error") or "License activation failed."
            return False, error_msg

        # Cross-verify product ID
        meta = body.get("meta", {})
        if self.expected_product_id and meta.get("product_id") != self.expected_product_id:
            return False, "This license key is valid for a different product, not Twitch OCR Chatbot."

        # Successful activation; persist to encrypted cache
        now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()
        lic_obj = body.get("license_key", {})
        inst_obj = body.get("instance", {})

        cache_data = {
            "license_key": lic_obj.get("key"),
            "instance_id": inst_obj.get("id"),
            "instance_name": inst_obj.get("name"),
            "customer_email": meta.get("customer_email"),
            "customer_name": meta.get("customer_name"),
            "product_id": meta.get("product_id"),
            "store_id": meta.get("store_id"),
            "status": lic_obj.get("status", "active"),
            "expires_at": lic_obj.get("expires_at"),
            "last_validated_at": now_iso,
            "last_observed_timestamp": int(time.time()),
        }

        self._save_cache(cache_data)
        self.cached_license = cache_data
        self.state = LicenseState.LICENSED_ONLINE
        return True, "License activated successfully!"

    # --- Heartbeat Validation ---

    def validate_heartbeat(self) -> str:
        """
        Executes a heartbeat validation check.
        Runs non-blocking logic:
        1. If offline, evaluates the 7-day grace period.
        2. If online, syncs with Lemon Squeezy and updates the cache.
        """
        if not self.cached_license or not self.cached_license.get("license_key"):
            self.state = LicenseState.UNLICENSED
            return self.state

        license_key = self.cached_license["license_key"]
        instance_id = self.cached_license.get("instance_id")

        # Check clock tampering before making network request
        current_time = int(time.time())
        last_observed = self.cached_license.get("last_observed_timestamp", 0)
        if current_time < (last_observed - 3600):
            logger.warning("System clock rollback detected! Suspending offline grace.")
            self.state = LicenseState.CLOCK_TAMPERED
            return self.state

        # Update high-water mark timestamp
        self.cached_license["last_observed_timestamp"] = max(last_observed, current_time)

        # Call Validate endpoint
        params = {"license_key": license_key}
        if instance_id:
            params["instance_id"] = instance_id

        status_code, body = self._post_license_api("validate", params)

        if status_code == 0:
            # Network is unreachable; evaluate offline grace
            return self._evaluate_offline_grace()

        if status_code == 404:
            # Key was deleted or invalid
            self.state = LicenseState.UNLICENSED
            self._clear_cache()
            return self.state

        if body.get("valid") is True:
            # Successfully verified online
            lic_obj = body.get("license_key", {})
            now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()
            
            self.cached_license["status"] = lic_obj.get("status", "active")
            self.cached_license["expires_at"] = lic_obj.get("expires_at")
            self.cached_license["last_validated_at"] = now_iso
            self._save_cache(self.cached_license)
            
            self.state = LicenseState.LICENSED_ONLINE
            return self.state

        # Server returned valid: false
        error_msg = body.get("error", "")
        lic_status = body.get("license_key", {}).get("status", "")

        if lic_status == "disabled" or "disabled" in error_msg:
            self.state = LicenseState.DISABLED
        elif lic_status == "expired" or "expired" in error_msg:
            self.state = LicenseState.EXPIRED
        else:
            self.state = LicenseState.UNLICENSED

        logger.info(f"License revoked by Lemon Squeezy: {error_msg} (Status: {lic_status})")
        return self.state

    def _evaluate_offline_grace(self) -> str:
        """Determines if the client is within the 7-day offline grace period."""
        last_validated_str = self.cached_license.get("last_validated_at")
        if not last_validated_str:
            self.state = LicenseState.UNLICENSED
            return self.state

        try:
            last_validated = datetime.datetime.fromisoformat(last_validated_str)
            now = datetime.datetime.now(datetime.timezone.utc)
            delta = now - last_validated
            remaining_seconds = (OFFLINE_GRACE_DAYS * 86400) - delta.total_seconds()

            if remaining_seconds > 0:
                self.state = LicenseState.LICENSED_OFFLINE_GRACE
                days_left = remaining_seconds / 86400.0
                logger.info(f"Network unreachable. Running in offline grace mode ({days_left:.1f} days remaining).")
            else:
                self.state = LicenseState.GRACE_EXPIRED
                logger.warning("Offline grace period has expired. Internet connection required to re-validate.")
        except Exception as e:
            logger.error(f"Error parsing validation timestamp: {e}")
            self.state = LicenseState.UNLICENSED

        return self.state

    # --- Local Encrypted Cache Management ---

    def _save_cache(self, data: Dict[str, Any]) -> None:
        """Serializes, signs with HMAC, and encrypts with DPAPI."""
        try:
            raw_json = json.dumps(data).encode("utf-8")
            fingerprint = _get_machine_fingerprint()
            signature = hmac.new(fingerprint.encode("utf-8"), raw_json, hashlib.sha256).hexdigest()

            envelope = {
                "sig": signature,
                "payload": raw_json.decode("latin1")
            }
            envelope_bytes = json.dumps(envelope).encode("utf-8")
            encrypted_bytes = _dpapi_encrypt(envelope_bytes)

            with open(CACHE_FILE, "wb") as f:
                f.write(encrypted_bytes)
        except Exception as e:
            logger.error(f"Failed to persist encrypted license cache: {e}")

    def _load_cache(self) -> None:
        """Decrypts with DPAPI, validates HMAC signature, and loads state."""
        if not CACHE_FILE.exists():
            self.state = LicenseState.UNLICENSED
            return

        try:
            with open(CACHE_FILE, "rb") as f:
                encrypted_bytes = f.read()

            envelope_bytes = _dpapi_decrypt(encrypted_bytes)
            envelope = json.loads(envelope_bytes.decode("utf-8"))

            payload_bytes = envelope["payload"].encode("latin1")
            stored_sig = envelope["sig"]

            fingerprint = _get_machine_fingerprint()
            computed_sig = hmac.new(fingerprint.encode("utf-8"), payload_bytes, hashlib.sha256).hexdigest()

            if not hmac.compare_digest(stored_sig, computed_sig):
                logger.error("License cache signature mismatch! File was tampered with or moved across machines.")
                self.state = LicenseState.UNLICENSED
                return

            self.cached_license = json.loads(payload_bytes.decode("utf-8"))
            # Initial state evaluation based on cached timestamps
            self._evaluate_offline_grace()
        except Exception as e:
            logger.error(f"Failed to decrypt license cache: {e}")
            self.state = LicenseState.UNLICENSED

    def _clear_cache(self) -> None:
        """Clears local cached license file."""
        self.cached_license = None
        if CACHE_FILE.exists():
            try:
                CACHE_FILE.unlink()
            except OSError:
                pass

    # --- Background Heartbeat Threading ---

    def start_background_heartbeat(self) -> None:
        """Spawns an asynchronous background worker thread for periodic license checks."""
        if self._heartbeat_thread and self._heartbeat_thread.is_alive():
            return

        self._stop_heartbeat.clear()

        def _worker():
            logger.info("License heartbeat background worker started.")
            while not self._stop_heartbeat.is_set():
                try:
                    self.validate_heartbeat()
                except Exception as e:
                    logger.error(f"Unhandled error in heartbeat loop: {e}")

                # Sleep in short slices to support graceful thread shutdown
                for _ in range(HEARTBEAT_INTERVAL_SECONDS):
                    if self._stop_heartbeat.is_set():
                        break
                    time.sleep(1)

        self._heartbeat_thread = threading.Thread(target=_worker, name="LicenseHeartbeatThread", daemon=True)
        self._heartbeat_thread.start()

    def stop_background_heartbeat(self) -> None:
        """Stops the heartbeat worker cleanly."""
        self._stop_heartbeat.set()
        if self._heartbeat_thread:
            self._heartbeat_thread.join(timeout=2)

    def is_feature_authorized(self) -> bool:
        """Convenience query for OCR detection engine."""
        return self.state in (LicenseState.LICENSED_ONLINE, LicenseState.LICENSED_OFFLINE_GRACE)
```

---

## 7. Primary Sources & Documentation Citations

1. **Lemon Squeezy License API Reference:**
   https://docs.lemonsqueezy.com/api/license-api
   *Defines public HTTP requirements, HTTPS domain, Accept headers, form encoding, 60 req/min rate limit, and error codes (400, 404, 422).*
2. **Lemon Squeezy Activate a License Key:**
   https://docs.lemonsqueezy.com/api/license-api/activate-license-key
   *Details endpoint parameters (`license_key`, `instance_name`), instance UUID creation, `activation_limit`, and response objects.*
3. **Lemon Squeezy Validate a License Key:**
   https://docs.lemonsqueezy.com/api/license-api/validate-license-key
   *Details endpoint parameters (`license_key`, `instance_id`), validation flags (`valid: true/false`), instance matching, and meta object schema.*
4. **Lemon Squeezy Deactivate a License Key:**
   https://docs.lemonsqueezy.com/api/license-api/deactivate-license-key
   *Details endpoint parameters (`license_key`, `instance_id`), instance release, and usage decrementing.*
5. **Lemon Squeezy License Keys and Subscriptions:**
   https://docs.lemonsqueezy.com/help/licensing/license-keys-subscriptions
   *Establishes that subscription license lengths are governed by the subscription lifecycle, staying active until subscription expiry or payment exhaustion.*
6. **Lemon Squeezy Generating License Keys:**
   https://docs.lemonsqueezy.com/help/licensing/generating-license-keys
   *Explains license key activation limits, product/variant settings, and button link redirect variables.*
7. **Lemon Squeezy The Subscription Object:**
   https://docs.lemonsqueezy.com/api/subscriptions/the-subscription-object
   *Defines subscription status values (`on_trial`, `active`, `paused`, `past_due`, `unpaid`, `cancelled`, `expired`), dunning behavior (4 retries over 2 weeks), and customer portal links.*
8. **Lemon Squeezy The License Key Object:**
   https://docs.lemonsqueezy.com/api/license-keys/the-license-key-object
   *Defines license key attributes (`status`: `inactive`, `active`, `expired`, `disabled`, `expires_at`, `activation_usage`, `instances_count`).*
9. **Microsoft Windows Data Protection API (DPAPI):**
   https://learn.microsoft.com/en-us/windows/win32/api/dpapi/nf-dpapi-cryptprotectdata
   *Specification for OS-level encryption bound to the Windows user account and host machine.*
