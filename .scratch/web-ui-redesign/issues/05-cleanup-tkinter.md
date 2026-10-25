Type: task
Status: resolved
Blocked by: 02, 03, 04

## Question

How do we clean up the old Tkinter code (`gui.py`) and update launch scripts (like `run_gui.bat`) to launch the new web UI?

## Answer

Deleted `gui.py`. Renamed `run_gui.bat` to `run_web.bat` and updated it to launch `web.py` with python and automatically open the default browser to `http://127.0.0.1:8000`.
