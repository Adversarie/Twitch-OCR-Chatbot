"""
license_manager.py - Lemon Squeezy Commercial Licensing Engine for Twitch OCR Chatbot
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

from config import Config

logger = logging.getLogger("LicenseManager")

API_BASE_URL = "https://api.lemonsqueezy.com/v1/licenses"
OFFLINE_GRACE_DAYS = 7           # Max days allowed without internet check
HEARTBEAT_INTERVAL_SECONDS = 43200  # Check every 12 hours
REQUEST_TIMEOUT_SECONDS = 10     # Strict socket timeout

# Cache directory in %LOCALAPPDATA%\TwitchOCRChatbot
APP_DATA_DIR = Path(os.environ.get("LOCALAPPDATA", Path.home())) / "TwitchOCRChatbot"
CACHE_FILE = APP_DATA_DIR / "license.dat"


def is_demo_key_allowed() -> bool:
    """Returns True only when running in explicit developer/test mode (DEV_MODE=1)."""
    return os.environ.get("DEV_MODE", "").lower() in ("1", "true", "yes")


# --- Windows DPAPI Encryption (Zero External Dependencies) ---
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
            return ctypes.string_at(out_blob.pbData, out_blob.cbData)
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
            return ctypes.string_at(out_blob.pbData, out_blob.cbData)
        finally:
            ctypes.windll.kernel32.LocalFree(out_blob.pbData)
else:
    def _dpapi_encrypt(data_bytes: bytes) -> bytes:
        return data_bytes

    def _dpapi_decrypt(cipher_bytes: bytes) -> bytes:
        return cipher_bytes


def _get_machine_fingerprint() -> str:
    """Derives a machine-unique identifier for HMAC signing."""
    components = []
    if sys.platform == "win32":
        try:
            import winreg
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Cryptography") as key:
                guid, _ = winreg.QueryValueEx(key, "MachineGuid")
                components.append(str(guid))
        except Exception:
            pass
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
    def __init__(self, expected_store_id: int = 0, expected_product_id: int = 0):
        self.expected_store_id = expected_store_id or Config.LEMON_SQUEEZY_STORE_ID
        self.expected_product_id = expected_product_id or Config.LEMON_SQUEEZY_PRODUCT_ID
        self.state: str = LicenseState.UNLICENSED
        self.cached_license: Optional[Dict[str, Any]] = None
        self._stop_heartbeat = threading.Event()
        self._heartbeat_thread: Optional[threading.Thread] = None

        APP_DATA_DIR.mkdir(parents=True, exist_ok=True)
        self._load_cache()

        # If no local cache exists, attempt activation from configured environment variable
        if not self.cached_license and Config.LEMON_SQUEEZY_LICENSE_KEY:
            try:
                self.activate(Config.LEMON_SQUEEZY_LICENSE_KEY)
            except Exception as e:
                logger.warning(f"Could not auto-activate license key from .env: {e}")

        # If a license key exists in cache, perform an immediate background heartbeat
        if self.cached_license and self.cached_license.get("license_key"):
            self.start_background_heartbeat()

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
            return 0, {"network_error": str(e)}

    # --- Activation ---

    def activate(self, license_key: str, instance_name: Optional[str] = None) -> Tuple[bool, str]:
        """
        Activates a license key for this workstation instance.
        Returns: (success: bool, message: str)
        """
        clean_key = license_key.strip()
        if not clean_key:
            return False, "License key cannot be empty."

        if not instance_name:
            instance_name = os.environ.get("COMPUTERNAME", "Twitch-Broadcaster-PC")

        # Developer demo key support (gated to DEV_MODE=1)
        if clean_key == "DEMO-KEY-123":
            if not is_demo_key_allowed():
                return False, "Invalid license key. Developer demo keys are disabled in production builds."
            now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()
            cache_data = {
                "license_key": "DEMO-KEY-123",
                "instance_id": "demo-instance-uuid",
                "instance_name": instance_name,
                "customer_email": "demo@streamer.tv",
                "customer_name": "Demo Streamer",
                "product_id": self.expected_product_id or 45100,
                "store_id": self.expected_store_id or 81234,
                "status": "active",
                "expires_at": "2099-01-01T00:00:00Z",
                "last_validated_at": now_iso,
                "last_observed_timestamp": int(time.time()),
            }
            self._save_cache(cache_data)
            self.cached_license = cache_data
            self.state = LicenseState.LICENSED_ONLINE
            return True, "Demo license activated successfully!"

        status_code, body = self._post_license_api("activate", {
            "license_key": clean_key,
            "instance_name": instance_name.strip()
        })

        if status_code == 0:
            return False, f"Network error during activation: {body.get('network_error')}"

        if not body.get("activated"):
            error_msg = body.get("error") or "License activation failed."
            return False, error_msg

        # Cross-verify product ID if configured
        meta = body.get("meta", {})
        if self.expected_product_id and meta.get("product_id") != self.expected_product_id:
            return False, "This license key is valid for a different product, not Twitch OCR Chatbot."

        now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()
        lic_obj = body.get("license_key", {})
        inst_obj = body.get("instance", {})

        cache_data = {
            "license_key": lic_obj.get("key") or clean_key,
            "instance_id": inst_obj.get("id"),
            "instance_name": inst_obj.get("name") or instance_name,
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
        self.start_background_heartbeat()
        return True, "License activated successfully!"

    # --- Deactivation ---

    def deactivate(self) -> Tuple[bool, str]:
        """
        Releases the instance slot on Lemon Squeezy to free up the 2-seat limit.
        Returns: (success: bool, message: str)
        """
        if not self.cached_license or not self.cached_license.get("license_key"):
            return True, "No active license to deactivate."

        license_key = self.cached_license["license_key"]
        instance_id = self.cached_license.get("instance_id")

        if instance_id and license_key != "DEMO-KEY-123":
            status_code, body = self._post_license_api("deactivate", {
                "license_key": license_key,
                "instance_id": instance_id
            })
            if status_code == 0:
                logger.warning(f"Could not reach Lemon Squeezy to deactivate instance: {body.get('network_error')}")

        self._clear_cache()
        self.state = LicenseState.UNLICENSED
        self.stop_background_heartbeat()
        return True, "License deactivated on this machine."

    # --- Heartbeat Validation ---

    def validate_heartbeat(self) -> str:
        """
        Performs non-blocking heartbeat validation:
        1. If offline, evaluates the 7-day grace period.
        2. If online, syncs with Lemon Squeezy and updates cache.
        """
        if not self.cached_license or not self.cached_license.get("license_key"):
            self.state = LicenseState.UNLICENSED
            return self.state

        license_key = self.cached_license["license_key"]
        instance_id = self.cached_license.get("instance_id")

        if license_key == "DEMO-KEY-123":
            if is_demo_key_allowed():
                self.state = LicenseState.LICENSED_ONLINE
            else:
                self._clear_cache()
                self.state = LicenseState.UNLICENSED
            return self.state

        current_time = int(time.time())
        last_observed = self.cached_license.get("last_observed_timestamp", 0)
        if current_time < (last_observed - 3600):
            logger.warning("System clock rollback detected! Suspending offline grace.")
            self.state = LicenseState.CLOCK_TAMPERED
            return self.state

        self.cached_license["last_observed_timestamp"] = max(last_observed, current_time)

        params = {"license_key": license_key}
        if instance_id:
            params["instance_id"] = instance_id

        status_code, body = self._post_license_api("validate", params)

        if status_code == 0:
            return self._evaluate_offline_grace()

        if status_code == 404:
            self.state = LicenseState.UNLICENSED
            self._clear_cache()
            return self.state

        if body.get("valid") is True:
            lic_obj = body.get("license_key", {})
            now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()
            
            self.cached_license["status"] = lic_obj.get("status", "active")
            self.cached_license["expires_at"] = lic_obj.get("expires_at")
            self.cached_license["last_validated_at"] = now_iso
            self._save_cache(self.cached_license)
            
            self.state = LicenseState.LICENSED_ONLINE
            return self.state

        error_msg = body.get("error", "")
        lic_status = body.get("license_key", {}).get("status", "")

        if lic_status == "disabled" or "disabled" in error_msg:
            self.state = LicenseState.DISABLED
        elif lic_status == "expired" or "expired" in error_msg:
            self.state = LicenseState.EXPIRED
        else:
            self.state = LicenseState.UNLICENSED

        logger.info(f"License revoked or expired: {error_msg} (Status: {lic_status})")
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
                logger.warning("Offline grace period has expired. Re-connection required.")
        except Exception as e:
            logger.error(f"Error parsing validation timestamp: {e}")
            self.state = LicenseState.UNLICENSED

        return self.state

    # --- Cache Management ---

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
            if self.cached_license.get("license_key") == "DEMO-KEY-123" and not is_demo_key_allowed():
                self._clear_cache()
                self.state = LicenseState.UNLICENSED
                return
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
                # Sleep in 1-second slices so thread stops immediately on shutdown
                for _ in range(HEARTBEAT_INTERVAL_SECONDS):
                    if self._stop_heartbeat.is_set():
                        return
                    time.sleep(1)

                try:
                    self.validate_heartbeat()
                except Exception as e:
                    logger.error(f"Unhandled error in heartbeat loop: {e}")

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

    def get_status_display(self) -> Dict[str, Any]:
        """Returns structured status dictionary for UI and OBS Dock."""
        is_auth = self.is_feature_authorized()
        key = self.cached_license.get("license_key") if self.cached_license else ""
        masked_key = f"{key[:4]}...{key[-4:]}" if key and len(key) >= 8 else key

        grace_days_left = 0.0
        if self.state == LicenseState.LICENSED_OFFLINE_GRACE and self.cached_license:
            last_val = self.cached_license.get("last_validated_at")
            if last_val:
                try:
                    dt = datetime.datetime.fromisoformat(last_val)
                    delta = datetime.datetime.now(datetime.timezone.utc) - dt
                    grace_days_left = max(0.0, OFFLINE_GRACE_DAYS - (delta.total_seconds() / 86400.0))
                except Exception:
                    pass

        return {
            "valid": is_auth,
            "state": self.state,
            "status": "active" if is_auth else ("trial" if self.state == LicenseState.UNLICENSED else "expired"),
            "plan": "Pro Subscriber" if is_auth else "Trial Mode",
            "key_masked": masked_key or None,
            "instance_id": self.cached_license.get("instance_id") if self.cached_license else None,
            "customer_email": self.cached_license.get("customer_email") if self.cached_license else None,
            "expires_at": self.cached_license.get("expires_at") if self.cached_license else None,
            "grace_days_left": round(grace_days_left, 1),
            "checkout_url": Config.LEMON_SQUEEZY_CHECKOUT_URL
        }
