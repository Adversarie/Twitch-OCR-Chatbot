Type: task
Status: resolved
Blocked by: 01

## Question

How do we build the Settings UI tab, and implement the API endpoints to read from and write to `.env` (and reload configuration)?

## Answer

Added `/api/settings` GET and POST endpoints in `web.py` leveraging python-dotenv's `dotenv_values` and `set_key`. Implemented `Config.reload()` in `config.py` so the backend picks up the new values immediately. Built a dynamic HTML form in `index.html` that hides sensitive fields and submits JSON updates.
