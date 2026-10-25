Status: resolved
Type: task
Labels: wayfinder:task
Blocked by: 01

## Question

Implement a zero-server TypeScript `LicenseClient` in Picture Perfect (`src/lib/license.ts`) that calls Lemon Squeezy's public License API directly, manages per-device instance UUIDs, and securely caches the 7-day offline grace state using Electron `safeStorage` (with a signed hash fallback for web preview), removing the requirement for any running backend server or database.

## Answer

Implemented zero-server commercial licensing engine in Picture Perfect:

1. **Client Engine ([license.ts](file:///c:/Users/matt1/Downloads/pictureperfect/src/lib/license.ts))**:
   - Created `LicenseClient` class querying Lemon Squeezy's public License API directly (`/v1/licenses/activate`, `/v1/licenses/validate`, `/v1/licenses/deactivate`).
   - Cross-product verification: Compares `meta.product_id` against `VITE_LEMON_SQUEEZY_PRODUCT_ID` and `meta.store_id` against `VITE_LEMON_SQUEEZY_STORE_ID`.
   - Per-device instance identifier: Manages workstation instance UUIDs and names.
   - Sliding 7-day offline grace window (`OFFLINE_GRACE_DAYS = 7`) with clock rollback tampering detection.
   - Background 12-hour heartbeat via `unref()`-friendly timer.
   - Developer demo key (`DEMO-KEY-123`) offline bypass.
   - Maintained full backwards-compatibility wrappers for `validateSubscriptionEntitlement()`, `startStripeSubscriptionCheckout()`, `openStripeCustomerPortal()`, and `validateWooCommerceLicense()`.

2. **Electron SafeStorage & External Browser IPC ([main.cjs](file:///c:/Users/matt1/Downloads/pictureperfect/main.cjs#L6-L44))**:
   - Added `license:isSafeStorageAvailable`, `license:encrypt`, and `license:decrypt` IPC handlers leveraging Electron's native `safeStorage` (Windows DPAPI / macOS Keychain).
   - Added Web Crypto HMAC-SHA256 signature fallback (`pictureperfect_license_vault_web`) with machine/browser fingerprinting for headless and web preview environments.
   - Added `open-external` IPC handler calling `shell.openExternal(url)` to open checkout links in the user's default desktop browser instead of the Electron window.

3. **Verification**:
   - `npm run lint` (`tsc --noEmit`): Passed with 0 errors.
   - [test_license_client.ts](file:///c:/Users/matt1/Downloads/pictureperfect/test_license_client.ts): Verified 6 test cases (unlicensed state, DEMO-KEY-123 activation, encrypted/HMAC vault persistence, rehydration from cache, compatibility wrappers, and seat deactivation). All passed with exit code 0.
   - `npm run build`: Production Vite build completed successfully in 17.68s.
