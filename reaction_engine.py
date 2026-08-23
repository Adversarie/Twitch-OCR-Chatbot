import random
import requests
import logging
from config import Config

logger = logging.getLogger(__name__)

# Predefined reactions mapping an event ID to a list of possible chat messages
PREWRITTEN_REACTIONS = {
    "poe1_death": [
        "RIP bozo KEKW",
        "F in the chat",
        "Back to the Twilight Strand!",
        "-10% EXP LUL",
        "Was it the lag? Clueless",
        "Should have stacked more chaos res...",
        "Log out macro failed? KEKW",
        "Cast on Death + Portal setup when?",
        "Chris Wilson sends his regards. BibleThump",
        "Offscreened by a white mob KEKW",
        "Was that physical reflect? MonkaS",
        "Losing 10% EXP at this level hurts my soul",
        "Still sane, exile? KEKW",
        "Zdps build? NotLikeThis",
        "HC viable? I think not Kappa",
        "One-shot mechanics are balanced, I swear Copium",
        "Floor POV is looking great today!",
        "Go next! Twilight Strand speedrun!",
        "Did you forget to cap your resistances? LUL",
        "That's a rip! Clip it!",
    ],
    "poe1_level_up": [
        "Ding! Gratz on the level!",
        "Level up! POG",
        "One step closer to 100! PogChamp",
        "Skill point acquired! Time to misplace it KEKW",
        "Only 200 more maps for the next level... Gratz!",
        "POG level up! Let's go!",
        "More life, more damage, still gonna die KEKW",
        "Nice! Don't lose that 10% exp now MonkaS",
        "DING! The grind pays off!",
        "Unethical levelling speed, nerf incoming Kappa",
    ],
    "poe1_exalted_mirror_drop": [
        "MIRROR??? WHAT?! PogChamp",
        "POGGERS MIRROR OF KALANDRA! OMG",
        "RNG carried! Unbelievable!",
        "Streamer loot luck is actually real NotLikeThis",
        "UNETHICAL DROP! BAN THEM KEKW",
        "Check the clip! That is a mirror!",
        "Time to retire! You've beaten the game!",
        "I was here! POGGERS",
        "Can I get a loan? Kappa",
        "Absolute gigachad drop! Gratz!",
    ],
    "poe1_boss_kill": [
        "Boss down! Easy game!",
        "POG boss dead!",
        "Clean kill! (Well, mostly) KEKW",
        "Loot was absolute trash though LUL",
        "First try, no sweat! Copium",
        "Eater of Worlds? More like Eater of Dirt KEKW",
        "Maven down! You love to see it!",
        "Huge fight! Gratz!",
    ],
    "poe2_death": [
        "RIP! PoE 2 is absolutely unforgiving...",
        "Dodge roll on cooldown? KEKW",
        "Back to the waypoint, exile!",
        "KEKW You died again. Welcome to PoE 2!",
        "No log out macro in PoE 2? Rolled! LUL",
        "Oof, boss hp reset. Pain.",
        "Get rolled! Literally KEKW",
        "Should have rolled earlier MonkaS",
        "PoE 2 boss fights don't mess around!",
        "Did you run out of spirit? Clueless",
        "Floor inspection team leader!",
        "Those graphics look great from the ground! Kappa",
        "Ranger/Witch dodge roll failed!",
    ],
    "poe2_boss_kill": [
        "First try! (100% real, no copium) KEKW",
        "Wow, PoE 2 boss actually defeated! Huge!",
        "POG boss down! Those mechanics were intense!",
        "Those dodge rolls were actually clean! PogChamp",
        "PoE 2 boss mechanics are wild. Well played!",
        "Loot check? Show us the gold!",
        "Gigachad boss killer!",
    ],
    "poe2_gold_drop": [
        "Are we playing Diablo now? Gold? KEKW",
        "Oooh shiny gold coins!",
        "Wealthy exile! Spend it wisely!",
        "Gold drop? PogChamp",
        "Time to gamble some items in town!",
    ],
    "poe2_level_up": [
        "Ding! PoE 2 level up!",
        "One step closer to the PoE 2 endgame!",
        "Gratz on the PoE 2 level! POG",
        "New skills unlocked! Let's see them!",
    ],
    "poe2_disconnect": [
        "Disconnected! Classic GGG server quality KEKW",
        "Server boss defeated you! LUL",
        "Unexpected disconnection... RIP mapping!",
        "Chris Wilson pulled the plug! BibleThump",
        "Log out macro worked too well? Kappa",
        "Go next! Server status check time!",
    ],
    "poe2_inventory_full": [
        "Inventory full... pick up more scrolls! KEKW",
        "Portal to town when? LUL",
        "Hoarder mentality exposed! NotLikeThis",
        "Time to play Tetris in your inventory...",
        "Drop the trash items! Kappa",
    ],
    "poe2_out_of_mana": [
        "Out of mana again? KEKW",
        "Need more spirit! Get some mana regen LUL",
        "Gotta love the out of mana sound spammed... NotLikeThis",
        "Zdps because no spirit? Kappa",
        "Buy some mana flasks already!",
    ],
    "wow_death": [
        "Wipe! Back to the entrance we go...",
        "Release spirit... running simulator active! LUL",
        "Did the hunter or pet pull again? LUL",
        "Stand in the fire, get the pyre KEKW",
        "Tank? Healer? Anyone? NotLikeThis",
        "Soulstone when? MonkaS",
        "Your repair bill is absolutely crying right now.",
        "Healer's fault obviously Kappa",
        "Who pulled that extra pack? Clueless",
        "Floor pov! DPS looks great down here KEKW",
        "Rez pls! BibleThump",
        "Oof, durability down by 10%.",
    ],
    "wow_achievement": [
        "Gratz on the achievement!",
        "Achievement unlocked! Achievement hunter PogChamp",
        "POG achievement! What a grind!",
        "Show off! KEKW",
        "Points went up! Huge gamer moment!",
        "I was here for the achievement! POG",
    ],
    "wow_level_up": [
        "Ding! Gratz on the level!",
        "Level up! Time to go spend gold on gear KEKW",
        "The WoW grind continues! PogChamp",
        "Only many more levels to go... Kappa",
        "DING! Gratz! What zone next?",
        "Level up! POGGERS",
    ],
    "wow_loot_drop": [
        "EPIC LOOT! PogChamp",
        "Need or greed? Ninja loot incoming! LUL",
        "Gratz on the drop! Is it BiS?",
        "BiS item acquired! HUGE!",
        "Wow, RNG blessed you today!",
        "Can I roll need on that? Kappa",
        "Unethical loot drops. Report streamer luck! KEKW",
        "Purple pixels! Pog",
    ]
}

import time

class ReactionEngine:
    def __init__(self):
        self.use_ollama = Config.USE_OLLAMA
        self.ollama_url = Config.OLLAMA_URL
        self.ollama_model = Config.OLLAMA_MODEL
        self.cooldowns = {}
        self.cooldown_duration = Config.EVENT_COOLDOWN

    def get_reaction(self, event_id: str, ocr_context: str = "") -> str:
        """
        Get a reaction for the given event. Evaluates cooldown first.
        Uses Ollama if enabled, otherwise falls back to prewritten lists.
        Returns None if the event is on cooldown.
        """
        current_time = time.time()
        if event_id in self.cooldowns:
            if current_time - self.cooldowns[event_id] < self.cooldown_duration:
                return None
                
        # Register cooldown
        self.cooldowns[event_id] = current_time

        if self.use_ollama:
            llm_response = self._generate_ollama_reaction(event_id, ocr_context)
            if llm_response:
                return llm_response
            else:
                logger.warning("Ollama failed, falling back to prewritten reactions.")
        
        # Fallback to pre-written lists
        return self._get_prewritten_reaction(event_id)

    def _get_prewritten_reaction(self, event_id: str) -> str:
        reactions = PREWRITTEN_REACTIONS.get(event_id)
        if reactions:
            return random.choice(reactions)
        return ""

    def _generate_ollama_reaction(self, event_id: str, ocr_context: str) -> str:
        prompt = (
            f"You are a Twitch chat bot watching a streamer play a game. "
            f"The streamer just triggered the event '{event_id}'. "
            f"The exact game context is: '{ocr_context}'. "
            f"Write a short, funny, natural Twitch chat reaction (1-10 words). "
            f"If the context contains an item name, achievement, or boss name, make sure to mention or roast it! Don't use quotes."
        )

        payload = {
            "model": self.ollama_model,
            "prompt": prompt,
            "stream": False
        }

        try:
            response = requests.post(self.ollama_url, json=payload, timeout=5)
            response.raise_for_status()
            data = response.json()
            return data.get("response", "").strip()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error communicating with Ollama: {e}")
            return None
