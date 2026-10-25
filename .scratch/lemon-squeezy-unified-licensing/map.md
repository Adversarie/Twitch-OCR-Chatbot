Status: resolved
Labels: wayfinder:map

## Destination

A unified, zero-server commercial licensing engine powered by Lemon Squeezy (as Merchant of Record) deployed across both Twitch OCR Chatbot and Picture Perfect, providing direct-to-client public License API activation/validation, 2-device seat enforcement, 7-day offline grace protection via platform-native DPAPI / safeStorage encryption, and hosted browser checkout.

## Notes

- Scope: Unified licensing architecture across both Twitch OCR Chatbot (Python/FastAPI) and Picture Perfect (React/Electron).
- Architecture: Client-direct Lemon Squeezy public License API (`/v1/licenses/activate`, `/v1/licenses/validate`, `/v1/licenses/deactivate`). Zero 24/7 backend servers or databases required.
- Security & Offline Policy: 7-day sliding offline grace window secured via native OS encryption (Windows DPAPI via `ctypes` in Python, Electron `safeStorage` in Picture Perfect).
- Commercial Terms: Recurring subscriptions, 2 device activations per seat, hosted browser checkout.
- Skills: `domain-modeling`, `prototype`, `research`.

## Decisions so far

<!-- the index: one line per closed ticket, enough to judge relevance, then zoom the link for the detail the ticket holds -->

- [01-lemon-squeezy-store-product-spec](file:///c:/Users/matt1/Downloads/Twitch%20OCR%20Chatbot/.scratch/lemon-squeezy-unified-licensing/issues/01-lemon-squeezy-store-product-spec.md): Defined 2-seat subscription product structure, client environment variables (STORE_ID, PRODUCT_ID, CHECKOUT_URL), and mandatory cross-product validation guards.
- [02-python-client-license-engine](file:///c:/Users/matt1/Downloads/Twitch%20OCR%20Chatbot/.scratch/lemon-squeezy-unified-licensing/issues/02-python-client-license-engine.md): Implemented standard-library LicenseManager module with Windows DPAPI encryption, machine-bound HMAC integrity, background 12-hour heartbeats, and 7-day offline grace caching.
- [03-twitch-bot-obs-dock-integration](file:///c:/Users/matt1/Downloads/Twitch%20OCR%20Chatbot/.scratch/lemon-squeezy-unified-licensing/issues/03-twitch-bot-obs-dock-integration.md): Wired LicenseManager into FastAPI routes, gated commercial Twitch chat broadcasts behind active subscriptions with OBS overlay trial previews, and updated the OBS Dock modal with masked key status and 1-click Lemon Squeezy checkout.
- [04-pictureperfect-electron-license-engine](file:///c:/Users/matt1/Downloads/Twitch%20OCR%20Chatbot/.scratch/lemon-squeezy-unified-licensing/issues/04-pictureperfect-electron-license-engine.md): Implemented zero-server TypeScript LicenseClient with direct Lemon Squeezy public License API activation, Electron safeStorage DPAPI encryption, HMAC-SHA256 web fallback, and 7-day offline grace tracking.
- [05-pictureperfect-ui-and-checkout-migration](file:///c:/Users/matt1/Downloads/Twitch%20OCR%20Chatbot/.scratch/lemon-squeezy-unified-licensing/issues/05-pictureperfect-ui-and-checkout-migration.md): Decommissioned Express server.js, refactored Picture Perfect React UI with direct browser checkout launch, dynamic PRO badge with offline grace countdown, and device seat unlinking.

## Not yet specified

<!-- see "Fog of war": in-scope fog you can't ticket yet; graduates as the frontier advances -->

- In-app remote instance deactivation: Handling activation limit errors (`activation_limit_reached`) by querying or unbinding older instances directly within the client UI.
- Desktop auto-updater integration: Version checking and update distribution using Lemon Squeezy product file attachments.
- Affiliate tracking: Passing streamer/photographer affiliate tags (`?aff=...`) through to the hosted checkout redirect.

## Out of scope

<!-- see "Out of scope": work ruled beyond the destination; closed, never graduates -->

- Custom licensing proxy server / PostgreSQL database: Ruled out because Lemon Squeezy's public License API eliminates server hosting costs and handles instance counters natively.
- Custom tax registration management: Ruled out because Lemon Squeezy acts as the Merchant of Record and remits all global sales tax and VAT automatically.
- Stripe Billing & Invoicing: Decommissioned and replaced entirely by Lemon Squeezy.
