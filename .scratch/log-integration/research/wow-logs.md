# World of Warcraft Log Parsing

World of Warcraft outputs logging to two separate files (which can be toggled in-game via `/combatlog` and `/chatlog`). The files are located in the `_retail_/Logs/` (or `_classic_/Logs/`) directory.

## 1. Combat Log (`WoWCombatLog.txt`)
The Combat Log captures detailed, structured gameplay data (damage, healing, auras, deaths) in a comma-separated format. It's the best place to reliably parse **Player Deaths**. (Note: Advanced Combat Logging should be enabled in System > Network settings for precise data).

### Player Deaths (`UNIT_DIED`)
Death events have the `UNIT_DIED` event type. The format of the line is:
`TIMESTAMP  EVENT_TYPE,SourceGUID,SourceName,SourceFlags,SourceRaidFlags,DestGUID,DestName,DestFlags,DestRaidFlags`

**Raw Example Line:**
`4/15 20:31:25.123  UNIT_DIED,0000000000000000,nil,0x80000000,0x80000000,Player-970-00000123,Leeroy,0x511,0x0`

**Regex for Parsing Player Deaths:**
To distinguish player deaths from NPC/pet deaths, we look for `Player-` in the `DestGUID`.

```regex
^(\d{1,2}\/\d{1,2}\s\d{2}:\d{2}:\d{2}\.\d{3})\s+UNIT_DIED,.*?,.*?,.*?,.*?,(Player-[^,]+),([^,]+),
```
*   **Group 1:** Timestamp
*   **Group 2:** Target GUID (e.g., `Player-970-00000123`)
*   **Group 3:** Target Name (e.g., `Leeroy`)

---

## 2. Chat Log (`WoWChatLog.txt`)
The Chat Log is a plain-text capture of what appears in the user's chat box, prepended with a timestamp. It is the best place to parse **Achievements, Level Ups, and Epic Loot Drops**. 

**Important Note:** The Chat Log formatting is highly dependent on game localization/language, and link codes (like `|H...|h`) are injected for items and achievements.

### Achievement Unlocks
Achievements are broadcasted in chat with clickable link formatting.
**Regex:**
```regex
^(\d{1,2}\/\d{1,2}\s\d{2}:\d{2}:\d{2}\.\d{3})\s+(.*?)\s+has earned the achievement\s+\|Hachievement:\d+:.*?\|h\[(.*?)\]\|h
```
*(Note: System messages might omit the player name and just say `[Achievement Name] earned.`, but player broadcasts look like above. A generic fallback capturing the `|Hachievement:` block is recommended.)*

### Level Ups
Level up broadcasts are localized plain-text messages.
**Regex (English):**
```regex
^(\d{1,2}\/\d{1,2}\s\d{2}:\d{2}:\d{2}\.\d{3})\s+(.*?)\s+has reached level\s+(\d+)!
```

### Epic Loot Drops
Loot is logged similarly in the chat file. The game wraps the item in a clickable `|Hitem:...|h` string. To specifically find *Epic* loot, one could theoretically parse the item ID from the string, but standard regex captures any loot matching this pattern.

**Regex (Self / "You receive"):**
```regex
^(\d{1,2}\/\d{1,2}\s\d{2}:\d{2}:\d{2}\.\d{3})\s+You receive loot:\s+\|Hitem:\d+:.*?\|h\[(.*?)\]\|h
```

**Regex (Other Players):**
```regex
^(\d{1,2}\/\d{1,2}\s\d{2}:\d{2}:\d{2}\.\d{3})\s+(.*?)\s+receives loot:\s+\|Hitem:\d+:.*?\|h\[(.*?)\]\|h
```

### Important Parser Considerations
1.  **Buffering:** While `WoWCombatLog.txt` streams relatively quickly, `WoWChatLog.txt` is known to buffer and sometimes only flushes when the user logs out or reloads their UI. If tailing for real-time Twitch alerts, be aware of this limitation.
2.  **Pipes and Brackets:** The `|H...|h` links contain internal IDs. The regex groups above are designed to capture the human-readable text inside the `[...]` brackets. 
