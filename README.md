# Twitch OCR Chatbot

Real-time AI & Curated OBS Co-Host for **Path of Exile 1**, **Path of Exile 2**, and **World of Warcraft** streamers on Windows.

## Features

- **Zero-Calibration Game Log Tailing**: Automatically watches `Client.txt` (PoE 1 & 2) and `WOWCombatLog.txt` (WoW) to detect Boss Kills, Player Deaths, Level Ups, and Achievements with zero OCR setup.
- **Sub-10ms OpenCV Template Scanner**: High-speed multi-scale visual template matching (`template_scanner.py`) for rare currency drops (Mirror of Kalandra, Divine Orb, Exalted Orb) and on-screen death/victory banners.
- **1-Click Twitch Device Code OAuth**: Connect your Twitch broadcaster account in one browser click (`POST /api/twitch/auth/start`) with automatic broadcaster login discovery and rolling OAuth token refresh.
- **Zero-GPU Curated Deck or BYOK LLM**: Run with 0% GPU/VRAM overhead using Curated Streamer Reaction Decks, or connect Groq, OpenAI, or local Ollama LLMs.
- **OBS Browser Source Overlay & Dock**: Includes 3 animated 1080p overlay themes (*Twitch Glass*, *Cyberpunk Neon*, *Retro RPG*) and a real-time FastAPI WebSocket Control Center (`http://127.0.0.1:8000`).
- **Commercial Licensing**: Powered by Lemon Squeezy's public License API with Windows DPAPI (`CryptProtectData`) local encryption (`%LOCALAPPDATA%\TwitchOCRChatbot`) and a 7-day offline grace period across 2 device seats (Gaming PC + Streaming PC).

## Download & Installation

Download the latest standalone Windows installer (`TwitchOCRBot-Setup-v1.0.0.exe`) from the [**GitHub Releases**](https://github.com/Adversarie/Twitch-OCR-Chatbot/releases) page.

## Development & Packaging

```powershell
# Run the web control center & bot in development
.\run_web.bat

# Run the automated test suite
python test_license_gate.py

# Build standalone Windows installer (PyInstaller + Inno Setup 7)
.\scripts\build_windows_exe.bat
```
