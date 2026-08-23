# Path of Exile Client.txt Research

## Log File Location and Basics
- **PoE 1 & 2 Log Location:** Typically located at `[Install Directory]/logs/Client.txt` (e.g., `C:\Program Files (x86)\Steam\steamapps\common\Path of Exile\logs\Client.txt`). Both PoE 1 and PoE 2 use the same general file and structure.
- **Log Structure:** 
  `<Date> <Time> <Internal_ID> <Internal_Hex> [<Log_Level> <Logger> <PID>] : <Message>`
  *Example:* `2020/10/12 22:39:44 2316728953 ba9 [INFO Client 7124] : You have entered Desert Hideout.`

## Captured Events

### 1. Deaths
- **Logged?** Yes, but informally. 
- **Details:** The game client logs a message when the player is slain, often outputting `"You have been slain"` or `"Player died"`. However, it does **not** log damage recaps, the specific source of damage, or your character's level at the time of death. 

### 2. Level Ups
- **Logged?** Yes. 
- **Details:** The client logs when a player reaches a new level, usually with the phrase `"is now level X"`.

### 3. Boss Kills
- **Logged?** Not explicitly. There is no standard structured log for defeating a boss. Some boss encounters might trigger NPC dialogue or quest updates that appear in the log, but parsing this would be highly specific to individual encounters.

### 4. Drops
- **Logged?** **No.**
- **Details:** The `Client.txt` file does **not** explicitly log item drops, currency, or high-value loot. Tools that track player wealth typically rely on the official Path of Exile Stash Tab API, not the local text log.

### 5. Chat, Trade, and Areas
- **Logged?** Yes. Area transitions (e.g., `"You have entered..."`) and all chat/whisper messages are fully logged. This is how many trade companion apps function.

## Regex Parsing Patterns

**Full Line Capture Pattern (Extracts timestamp, PID, and message):**
```regex
^(?P<date>\d{4}/\d{2}/\d{2})\s+(?P<time>\d{2}:\d{2}:\d{2})\s+\d+\s+\w+\s+\[\w+\s+\w+\s+(?P<pid>\d+)\]\s+:\s+(?P<message>.*)$
```

**Specific Event Matching (Applied to the extracted `<message>` string):**
- **Death:** `(?i)you have been slain|player died`
- **Level Up:** `(?i)is now level (?P<level>\d+)`
- **Area Change:** `(?i)you have entered (?P<area>.*)\.`
```
