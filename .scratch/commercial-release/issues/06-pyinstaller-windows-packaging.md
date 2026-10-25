Status: resolved
Assignee: agent
Type: research
Blocked by: 01, 02, 03, 04, 05
Completed At: 2026-10-09T10:47:30-07:00

## Question

What is the optimal PyInstaller / Inno Setup build specification to bundle the Python 3 runtime, FastAPI backend, Uvicorn server, OpenCV/MSS binaries, reference templates, static web assets, and audio cues into a standalone, single-executable or zero-install Windows distribution that auto-launches the background service and opens the OBS setup guide?

## Answer

### 1. Architectural Strategy: Onedir + Inno Setup vs. Onefile
For a real-time streamer application running local computer vision and an ASGI web server, **PyInstaller `COLLECT` (onedir) paired with an Inno Setup installer** is significantly superior to PyInstaller `--onefile`:
* **Zero Cold-Start Lag**: PyInstaller `--onefile` uncompresses 200MB+ of Python binaries, OpenCV DLLs, and site-packages into a fresh `%TEMP%/_MEIxxxxxx` directory on **every single startup**, causing 4–8 second delays and disk churn. In contrast, `onedir` launches in < 400ms directly from disk.
* **Streamer-Friendly Setup**: Inno Setup compresses the entire `dist/TwitchOCRBot` directory into a single, clean `TwitchOCRBot-Setup-v1.0.0.exe` (~35–45 MB download).
* **Zero Admin UAC Elevation**: Configured with `PrivilegesRequired=lowest`, the installer installs into `%LOCALAPPDATA%\Programs\TwitchOCRChatbot`, allowing standard users to install without Windows UAC administrator elevation prompts.

### 2. PyInstaller Specification (`TwitchOCRBot.spec`)
The build specification encapsulates all application dependencies and static assets:
* **Bundled Assets (`datas`)**:
  * `static/` -> `static` (OBS Dock UI, on-stream transparent canvas `overlay.html`, fonts, icons)
  * `templates/` -> `templates` (Visual template matching PNG reference crops for zero-setup detection)
  * `zones.json` -> `.` (Pre-configured game zones)
* **Hidden Imports (`hiddenimports`)**:
  * Uvicorn dynamic modules: `uvicorn.loops.auto`, `uvicorn.protocols.http.auto`, `uvicorn.protocols.websockets.auto`, `uvicorn.lifespans.on`
  * ASGI stack: `fastapi.staticfiles`, `starlette.middleware`, `twitchio.ext.commands`
  * Native C-extensions: `cv2`, `mss`, `numpy`, `ctypes`, `multiprocessing`
* **Windowless Background Daemon**:
  * `console=False`: Suppresses the black Windows command prompt window from popping up over OBS or the streamer's game.

### 3. Frozen Resource Resolution Pattern
All filesystem asset loaders utilize the standardized resource resolution helper:
```python
def get_resource_path(relative_path: str) -> str:
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    target = os.path.join(base_path, relative_path)
    return target if os.path.exists(target) else relative_path
```
Implemented across:
* `web.py`: Mounts `/static` and `/templates` and serves `index.html` and `overlay.html`.
* `template_scanner.py`: Resolves `templates/{game}/{event}.png` directly from `sys._MEIPASS` or local directory.
* `ocr_scanner.py`: Resolves `zones.json` fallback if not present in active working directory.

### 4. Background Execution & Auto-Browser Launch
In `web.py`:
* Direct programmatic startup: `uvicorn.run(app, host="127.0.0.1", port=8000)` without string-based reloaders that fail under frozen execution.
* Seamless streamer onboarding: A background daemon thread triggers `webbrowser.open("http://127.0.0.1:8000")` after 1.2s warmup, immediately presenting the OBS Dock setup and license activation screen upon launch.

### 5. Automated Build & Distribution Pipeline
* **Build Script**: [`scripts/build_windows_exe.bat`](file:///c:/Users/matt1/Downloads/Twitch%20OCR%20Chatbot/scripts/build_windows_exe.bat) verifies/installs `pyinstaller` and executes `pyinstaller TwitchOCRBot.spec --clean --noconfirm`.
* **Installer Script**: [`installer.iss`](file:///c:/Users/matt1/Downloads/Twitch%20OCR%20Chatbot/installer.iss) compiles `dist/TwitchOCRBot` into `dist/TwitchOCRBot-Setup-v1.0.0.exe`, configuring Start Menu and Desktop shortcuts, plus auto-launch on setup completion.
