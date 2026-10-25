---
type: wayfinder:task
status: closed
assignee: agent
blocked_by:
  - 03-template-matching-engine
---

## Question

What reference template assets should be packaged for unlogged visual events (PoE disconnect popup, PoE 2 gold/loot drops, out of mana/inventory alerts, and WoW achievements), and where in the project repository should they be stored and indexed?

## Resolution

Organized and packaged standard reference visual templates in `templates/<game_id>/<event_id>.png`:
- `templates/poe2/poe2_disconnect.png`: Modal frame header for disconnect errors.
- `templates/poe2/poe2_out_of_mana.png`: Floating warning cue for out of mana / spirit depletion.
- `templates/poe2/poe2_inventory_full.png`: Alert cue for full inventory bag.
- `templates/poe2/poe2_boss_kill.png`: Victory / Defeated emblem banner.
- `templates/poe1/poe1_exalted_mirror_drop.png`: Mirror of Kalandra high-value ground drop label.
- `templates/wow/wow_achievement.png`: Golden achievement crest banner.
- Created `scripts/generate_templates.py` generator tool.
- Mounted `/templates` static route and added `GET /api/templates` in `web.py` to serve asset metadata and visual previews to the Web UI.
