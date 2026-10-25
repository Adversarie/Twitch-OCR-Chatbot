# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Stack
Electron / Node.js

## Users
A Twitch streamer broadcasting their gameplay.

## Product Purpose
To automate a chatbot that watches the streamer's game and interacts with the Twitch chat. Success means the bot provides entertaining, accurate, and witty commentary based on real-time game events without requiring manual streamer input.

## Positioning
It acts as an autonomous AI co-host. Instead of relying on game-specific APIs or memory hooks, it visually captures the screen and performs OCR to understand the game-state, then uses a local Ollama LLM to generate witty banter and report it directly to the Twitch chat.

## Operating Context
Running concurrently with a demanding video game and broadcasting software (OBS). The streamer is busy playing, so the tool must operate completely autonomously in the background.

## Capabilities and Constraints
- **Performance:** Must be extremely lightweight to avoid impacting game performance or stream frame rates.
- **Flexibility:** Must work with multiple languages and fonts to support various games.
- **Integration:** Needs to support transparency/chroma keying for OBS integration.
- **AI:** Relies on a locally running Ollama instance for generating the banter.
- **Vision:** Uses screen capture and OCR to infer game state.

## Product Principles
1. **Zero-Touch Operation:** The streamer shouldn't have to babysit the bot while playing.
2. **Performance First:** The game and stream framerates are sacred; the bot must be frugal with system resources.
3. **Local & Private:** By relying on local OCR and Ollama, it avoids expensive cloud API costs and latency.
4. **Entertaining:** The output should feel like a witty co-host, not a robotic log of events.
