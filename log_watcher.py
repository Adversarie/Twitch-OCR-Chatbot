import asyncio
import os
import re
import logging

logger = logging.getLogger(__name__)

DEFAULT_LOG_CANDIDATES = {
    'poe1': [
        r"C:\Program Files (x86)\Steam\steamapps\common\Path of Exile\logs\Client.txt",
        r"C:\Program Files (x86)\Grinding Gear Games\Path of Exile\logs\Client.txt",
    ],
    'poe2': [
        r"C:\Program Files (x86)\Steam\steamapps\common\Path of Exile 2\logs\Client.txt",
        r"C:\Program Files (x86)\Grinding Gear Games\Path of Exile 2\logs\Client.txt",
    ],
    'wow_combat': [
        r"C:\Program Files (x86)\World of Warcraft\_retail_\Logs\WoWCombatLog.txt",
        r"C:\Program Files (x86)\World of Warcraft\_classic_\Logs\WoWCombatLog.txt",
    ],
    'wow_chat': [
        r"C:\Program Files (x86)\World of Warcraft\_retail_\Logs\WoWChatLog.txt",
        r"C:\Program Files (x86)\World of Warcraft\_classic_\Logs\WoWChatLog.txt",
    ]
}

class LogWatcher:
    def __init__(self, config):
        self.config = config
        
        # PoE Patterns
        self.poe_base_pattern = re.compile(r"^\d{4}/\d{2}/\d{2}\s+\d{2}:\d{2}:\d{2}\s+\d+\s+\w+\s+\[\w+\s+\w+\s+\d+\]\s+:\s+(.*)$")
        self.poe_death = re.compile(r"(?i)you have been slain|player died")
        self.poe_level = re.compile(r"(?i)is now level (\d+)")
        self.poe_area = re.compile(r"(?i)you have entered (.*?)\.")
        
        # WoW Patterns
        self.wow_death = re.compile(r"^\d{1,2}\/\d{1,2}\s\d{2}:\d{2}:\d{2}\.\d{3}\s+UNIT_DIED,.*?,.*?,.*?,.*?,(Player-[^,]+),([^,]+),")
        self.wow_achiev = re.compile(r"^\d{1,2}\/\d{1,2}\s\d{2}:\d{2}:\d{2}\.\d{3}\s+(.*?)\s+has earned the achievement\s+\|Hachievement:\d+:.*?\|h\[(.*?)\]\|h")
        self.wow_level = re.compile(r"^\d{1,2}\/\d{1,2}\s\d{2}:\d{2}:\d{2}\.\d{3}\s+(.*?)\s+has reached level\s+(\d+)!")
        self.wow_loot = re.compile(r"^\d{1,2}\/\d{1,2}\s\d{2}:\d{2}:\d{2}\.\d{3}\s+(You|.*?)\s+(?:receive|receives) loot:\s+\|Hitem:\d+:.*?\|h\[(.*?)\]\|h")

    def _resolve_path(self, configured_path: str, candidates_key: str) -> str:
        if configured_path and os.path.exists(configured_path):
            return configured_path
        for candidate in DEFAULT_LOG_CANDIDATES.get(candidates_key, []):
            if os.path.exists(candidate):
                logger.info(f"Auto-discovered default log path for {candidates_key}: {candidate}")
                return candidate
        return ""

    async def watch(self):
        """Asynchronous generator yielding (event_id, context) tuples."""
        files_to_watch = []
        
        def add_watcher(path, log_type):
            if path and os.path.exists(path):
                f = open(path, 'r', encoding='utf-8', errors='replace')
                f.seek(0, 2)
                files_to_watch.append({'file': f, 'type': log_type})
                logger.info(f"Tailing {log_type} Log: {path}")

        poe1_path = self._resolve_path(getattr(self.config, 'POE_LOG_PATH', ''), 'poe1')
        poe2_path = self._resolve_path(getattr(self.config, 'POE2_LOG_PATH', ''), 'poe2')
        wow_combat = self._resolve_path(getattr(self.config, 'WOW_COMBAT_LOG_PATH', ''), 'wow_combat')
        wow_chat = self._resolve_path(getattr(self.config, 'WOW_CHAT_LOG_PATH', ''), 'wow_chat')

        add_watcher(poe1_path, 'poe1')
        add_watcher(poe2_path, 'poe2')
        add_watcher(wow_combat, 'wow_combat')
        add_watcher(wow_chat, 'wow_chat')

        if not files_to_watch:
            logger.warning("No game log files found or configured. LogWatcher is idle.")
            return

        try:
            while True:
                for watcher in files_to_watch:
                    line = await asyncio.to_thread(watcher['file'].readline)
                    if not line:
                        continue
                        
                    event = self._parse_line(line.strip(), watcher['type'])
                    if event:
                        yield event
                        
                await asyncio.sleep(0.1)
        finally:
            for watcher in files_to_watch:
                watcher['file'].close()

    def _parse_line(self, line, log_type):
        if log_type in ('poe1', 'poe2'):
            match = self.poe_base_pattern.match(line)
            if not match: return None
            msg = match.group(1)
            
            prefix = "poe1" if log_type == 'poe1' else "poe2"
            
            if self.poe_death.search(msg):
                return (f"{prefix}_death", "Player died")
            
            lvl_match = self.poe_level.search(msg)
            if lvl_match:
                return (f"{prefix}_level_up", f"Level {lvl_match.group(1)}")
                
            area_match = self.poe_area.search(msg)
            if area_match:
                return (f"{prefix}_area_change", area_match.group(1))
                
        elif log_type == 'wow_combat':
            death_match = self.wow_death.match(line)
            if death_match:
                return ("wow_death", f"{death_match.group(2)} died")
                
        elif log_type == 'wow_chat':
            achiev_match = self.wow_achiev.match(line)
            if achiev_match:
                return ("wow_achievement", f"{achiev_match.group(1)} earned {achiev_match.group(2)}")
                
            lvl_match = self.wow_level.match(line)
            if lvl_match:
                return ("wow_level_up", f"{lvl_match.group(1)} reached level {lvl_match.group(2)}")
                
            loot_match = self.wow_loot.match(line)
            if loot_match:
                return ("wow_loot_drop", f"{loot_match.group(1)} looted {loot_match.group(2)}")
                
        return None
