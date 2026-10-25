Type: task
Status: resolved
Blocked by: 

## Question

How do we scaffold the FastAPI app (`web.py`), serve the frontend (`index.html`), and integrate the asynchronous loops from `main.py` (`bot.start`, `scan_loop`, `log_watch_loop`) as background tasks?

## Answer

Created `web.py` which runs a FastAPI server. It mounts a `static/` directory to serve `index.html`. The `TwitchOCRBot`, `scan_loop`, and `log_watch_loop` are integrated by providing `/api/bot/start` and `/api/bot/stop` endpoints that manage them using `asyncio.create_task()` and `task.cancel()`.

