---
type: wayfinder:task
status: closed
assignee: agent
---

## Question

How should the event pipeline be restructured so native logs exclusively own all lifecycle events (deaths, level ups, area changes) across PoE and WoW, eliminating redundant OCR and OCR configuration for those events?

## Resolution

Restructured the event ingestion pipeline to establish Log-First Dominance:
- Upgraded `log_watcher.py` with automatic default path resolution for Path of Exile 1, Path of Exile 2, and World of Warcraft (auto-detecting default Steam and GGG installation directories).
- Implemented file-specific game prefixing so `Client.txt` lines map cleanly to `poe1_death`, `poe2_death`, `poe1_level_up`, `poe2_level_up`, and `wow_death` without cross-game collision.
- Added `POE2_LOG_PATH` to `config.py` and the Web UI configuration form.
- Cleaned out redundant death and level-up OCR capture zones from `zones.json`, reserving optical scanning strictly for unlogged visual events (boss kills, disconnect errors, full inventory, out of mana).
- Updated Web UI to clarify that lifecycle events are handled automatically from native logs with zero configuration.
