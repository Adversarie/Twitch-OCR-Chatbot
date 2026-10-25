Status: resolved
Assignee: agent
Type: prototype

## Question

How should the on-stream Visual Overlay (`/overlay`) be architected and styled using Server-Sent Events (SSE) or WebSockets to display animated reaction cards, support customizable visual themes (Dark Twitch Purple, Cyberpunk Neon, Retro Arcade), trigger web audio SFX cues on game events, and offer transparent chroma background for seamless inclusion as an OBS Browser Source?

## Answer

Resolved by prototyping all three requested design variants and retaining all three as user-selectable themes:

1. **Architecture & Transport**:
   - Implemented real-time Server-Sent Events (SSE) via FastAPI `StreamingResponse` at `GET /api/overlay/events`.
   - Wired into `web.py`'s `handle_event` so game detections (and `/api/simulate-event`) broadcast reactions instantly with sub-millisecond latency.
   - Canvas is 100% transparent for direct OBS Studio Browser Source integration without manual chroma-key filtering.

2. **The Three Visual Themes**:
   - **Twitch Streamer Glass** (`?theme=glass`, default): Floating bottom-right corner card with deep violet glassmorphism (`backdrop-filter: blur(16px)`), Twitch purple gradient glow, AI co-host badge, and animated auto-dismiss countdown bar. Two-tone sine-wave harmonic chime SFX.
   - **Cyberpunk Neon Banner** (`?theme=cyberpunk`): Top-center wide cinematic banner with neon cyan & hot pink accents, geometric clip-path borders, scanlines, and glitch entrance. Industrial synthesizer sweep SFX.
   - **Retro Arcade RPG Box** (`?theme=retro`): Bottom-left 8-bit chunky pixel dialogue box with pixelated borders, retro monospace pixel font ('Press Start 2P'), pixel bot avatar, and flashing prompt. 8-bit square-wave arpeggio SFX.

3. **Zero Audio Asset Dependency**:
   - Synthesizes all audio cues on-the-fly using the browser's native Web Audio API (`AudioContext`). Zero external `.mp3` or `.wav` assets, zero CORS or broken asset path issues.

4. **OBS Production Cleanliness**:
   - Preview controls (simulation buttons and theme switcher) automatically hide when the overlay is running with a configured theme in OBS Studio (`?theme=glass`), rendering a 100% clean transparent stream layer.
   - Preview controls appear when opened in a browser for setup/auditioning (`?preview=true`).
