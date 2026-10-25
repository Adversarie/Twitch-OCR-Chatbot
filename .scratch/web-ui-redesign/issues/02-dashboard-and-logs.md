Type: task
Status: resolved
Blocked by: 01

## Question

How do we build the Dashboard UI, implement the SSE endpoint for streaming `bot.log`, and hook up the Start/Stop bot controls?

## Answer

Added `/api/bot/logs` to `web.py` utilizing FastAPI's `StreamingResponse` for SSE. Wrote `index.html` using TailwindCSS to construct the layout, and added Javascript to manage tab state, fetch bot status, POST to `/api/bot/start` and `/api/bot/stop`, and read logs from the `EventSource` and append them to a scrollable `<div>`.
