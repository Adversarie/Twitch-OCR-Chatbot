Status: resolved
Type: prototype
Labels: wayfinder:prototype
Blocked by: 04

## Question

Refactor Picture Perfect's React UI (`src/App.tsx`) to decommission the custom Express backend server (`server.js`), launch the Lemon Squeezy hosted checkout directly in the user's default browser, and provide an activation and status modal showing the active subscription tier, instance status, and offline grace indicator.

## Answer

Completed the UI refactor and decommissioned the custom Express backend server in Picture Perfect:

1. **Decommissioned Backend Server ([server.js](file:///c:/Users/matt1/Downloads/pictureperfect/server.js))**:
   - Deleted the 285-line custom Express server (`server.js`) that previously handled Stripe webhooks, database entitlements, and custom portal redirects.
   - Removed `"server": "node server.js"` from `package.json`. The entire app runs zero-server using client-direct Lemon Squeezy public License API calls.

2. **React UI & Modal Refactor ([App.tsx](file:///c:/Users/matt1/Downloads/pictureperfect/src/App.tsx))**:
   - Replaced old Stripe checkout logic with direct calls to `licenseClient`.
   - **Active Pro Mode**:
     - Upgraded the PRO badge in the sidebar to be interactive and display offline grace remaining (e.g. `PRO (6.8d)`).
     - Clicking the badge opens the License Management view displaying subscription tier, validation status, masked license key, and device seat allocation (`1 of 2 seats`).
     - Added 1-click **"Manage Orders on Lemon Squeezy ↗"** button opening the customer self-service order portal.
     - Added **"Unlink This Workstation Seat"** button with confirmation prompt calling `licenseClient.deactivate()`.
   - **Trial / Upgrade Mode**:
     - Interactive feature checklist.
     - License key activation input supporting both real UUID keys and offline `DEMO-KEY-123` bypass.
     - **"Buy License on Lemon Squeezy ↗"** button that invokes `licenseClient.startCheckout()`, opening the checkout page in the user's default desktop browser via Electron `shell.openExternal`.

3. **Automated Verification**:
   - `npm run lint` (`tsc --noEmit`): Passed with 0 errors.
   - `npm run build`: Production Vite bundle compiled in 5.51s with code 0.
   - [test_license_client.ts](file:///c:/Users/matt1/Downloads/pictureperfect/test_license_client.ts): 6/6 test cases passing cleanly.
