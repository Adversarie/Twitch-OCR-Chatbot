import asyncio
import os
import re
import logging

logger = logging.getLogger(__name__)

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

    async def watch(self):
        """Asynchronous generator yielding (event_id, context) tuples."""
        files_to_watch = []
        
        def add_watcher(path, log_type):
            if path and os.path.exists(path):
                f = open(path, 'r', encoding='utf-8', errors='replace')
                f.seek(0, 2)
                files_to_watch.append({'file': f, 'type': log_type})
                logger.info(f"Tailing {log_type} Log: {path}")

        add_watcher(self.config.POE_LOG_PATH, 'poe')
        add_watcher(self.config.WOW_COMBAT_LOG_PATH, 'wow_combat')
        add_watcher(self.config.WOW_CHAT_LOG_PATH, 'wow_chat')

        if not files_to_watch:
            logger.warning("No log files configured or found. LogWatcher is idle.")
            return

        try:
            while True:
                for watcher in files_to_watch:
                    # Offload blocking file I/O to a thread
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
        if log_type == 'poe':
            match = self.poe_base_pattern.match(line)
            if not match: return None
            msg = match.group(1)
            
            if self.poe_death.search(msg):
                return ("poe2_death", "Player died") # mapped to our existing ollama prompt key
            
            lvl_match = self.poe_level.search(msg)
            if lvl_match:
                return ("poe2_level_up", f"Level {lvl_match.group(1)}")
                
            area_match = self.poe_area.search(msg)
            if area_match:
                return ("poe_area_change", area_match.group(1))
                
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
                return ("wow_loot", f"{loot_match.group(1)} looted {loot_match.group(2)}")
                
        return None
