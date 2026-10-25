## Destination

A redesigned local web UI (FastAPI + HTML/JS/Tailwind) that replaces `gui.py`, featuring a browser-based visual zone editor, while integrating the existing Python backend (`main.py`) as background tasks.

## Notes

- Domain: Twitch OCR Chatbot frontend
- Keep it simple: Plain HTML + Vanilla JS + CDN Tailwind. No build step.
- Single process: FastAPI runs the web server and the bot/OCR loops as background tasks.
- SSE for real-time bot log streaming.
- Execution is in-scope for this map.

## Decisions so far

- [01-fastapi-scaffold](file:///C:/Users/matt1/Downloads/Twitch%20OCR%20Chatbot/.scratch/web-ui-redesign/issues/01-fastapi-scaffold.md): Created `web.py` to serve FastAPI, mounting static files, and running bot tasks asynchronously.
- [02-dashboard-and-logs](file:///C:/Users/matt1/Downloads/Twitch%20OCR%20Chatbot/.scratch/web-ui-redesign/issues/02-dashboard-and-logs.md): Built Dashboard HTML with Tailwind and integrated SSE log streaming and bot toggle controls.
- [03-settings-page](file:///C:/Users/matt1/Downloads/Twitch%20OCR%20Chatbot/.scratch/web-ui-redesign/issues/03-settings-page.md): Implemented `GET/POST /api/settings` logic, `Config.reload()`, and a dynamic Settings form.
- [04-zone-editor](file:///C:/Users/matt1/Downloads/Twitch%20OCR%20Chatbot/.scratch/web-ui-redesign/issues/04-zone-editor.md): Implemented `/api/screenshot` and an HTML5 Canvas-based visual zone editor in the web UI.
- [05-cleanup-tkinter](file:///C:/Users/matt1/Downloads/Twitch%20OCR%20Chatbot/.scratch/web-ui-redesign/issues/05-cleanup-tkinter.md): Deleted `gui.py` and updated batch script to `run_web.bat`.

## Not yet specified

## Out of scope
