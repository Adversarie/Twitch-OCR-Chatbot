import random
import requests
import logging
import time
from config import Config

logger = logging.getLogger(__name__)

# Over 500 rich, categorized, game-specific curated reactions.
# Guarantees zero GPU/CPU load during demanding gaming sessions.
PREWRITTEN_REACTIONS = {
    # --- Path of Exile 1 (150 lines) ---
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
        "Sirus stormed again? NotLikeThis",
        "Ground degen claims another victim! KEKW",
        "Corrupted blood immunity flask missing? MonkaS",
        "10% exp down the drain! BibleThump",
        "Donated exp to the map boss! LUL",
        "Cast on Death + Portal would have saved that portal!",
        "Death by porcupines? Classic PoE death!",
        "Did you read the map mods before opening? Clueless",
        "No spell suppression? In this economy? KEKW",
        "Died to after-death explosion again! LUL",
        "Offscreen projectile sniper! PogChamp",
        "Check resistances in town, exile! Kappa",
        "Map boss said sit down! KEKW",
        "Back to Lioneye's Watch with you!",
        "That was totally desync, right chat? Copium",
        "That rare mob had 5 Archnemesis modifiers! MonkaS",
        "Hit by the slam! Dodge next time! LUL",
        "Exp bar went backwards! BibleThump",
        "Instant transmission to the hideout! KEKW",
        "Death recap when, GGG? NotLikeThis",
        "Should have rolled a Juggernaut! Kappa",
        "Maven witnessed that embarrassing rip! KEKW",
        "Detonate Dead got you! Classic rip!",
        "Just a flesh wound! Resurrect in town!",
        "F for the fallen exile!",
        "Did you forget your defensive flasks were empty? KEKW",
        "The ground was lava! Avoid the red circles! LUL",
        "Corrupted Blood 20 stacks! Bleed out in 0.2 seconds! MonkaS",
        "Map had 100% extra damage as cold! Chilled to death!",
        "Should have stayed in the hideout! Safe and cozy! Kappa",
        "You died so fast your loot filter didn't even render!",
        "Rip bozo! The Twilight Strand welcomes its champion! KEKW",
        "Resurrection sickness in your soul! BibleThump",
        "That boss hit like a freight train with no brakes!",
        "Zero energy shield, zero life, 100% floor! LUL"
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
        "Another passive point for the tree! PogChamp",
        "Are we specing into more jewel sockets? POG",
        "Ding! Don't forget your ascendancy points!",
        "Exp bar reset to zero! Freedom from death penalty! LUL",
        "Gratz! Time to play recklessly with 0% exp!",
        "Level up sound is pure dopamine! PogChamp",
        "The grind never stops! Level up achieved!",
        "One passive closer to build completion!",
        "Ding! 100 grind is on! Let's go!",
        "Congratulations on surviving long enough to level!",
        "Nice ding! More mana, more life, more DPS!",
        "Gratz! Now spend 20 minutes staring at the passive tree KEKW",
        "Huge level! Map sustain paying off!",
        "Ding! Level achieved without dying to reflect!",
        "Level up! The build is finally coming together! Copium",
        "Gamer moment! Gratz on the level ding!",
        "Skill point ready! Don't forget to allocate it!",
        "Gratz on the level! Keep the zoom-zoom going!",
        "More HP pool to survive one-shots! PogChamp",
        "Ding ding ding! Big gratz exile!",
        "Another level closer to godly status!",
        "Exp bar full! Huge relief MonkaS",
        "Ding! POGGERS in the chat!",
        "Level up energy! Let's map faster!"
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
        "MIRROR TIER RNG! Clip that right now!",
        "The Krangled gods have blessed this stream! PogChamp",
        "Chris Wilson personally pressed the drop button! KEKW",
        "Wait, is that a Divine or a Mirror?! HUGE DROP!",
        "Divine Orb sound is sweet, but Mirror is GODLIKE!",
        "Bank account in PoE just exploded! PogChamp",
        "Streamer client confirmed! Totally rigged! KEKW",
        "Don't pick it up until you take a screenshot!",
        "Loot filter sound scared me! POGGERS",
        "You just financed an entire mirror-tier build!",
        "That sound! The drop chime of legends!",
        "Holy RNGesus! Gratz on the insane loot drop!",
        "I was here for the historical drop! PogChamp",
        "Rich exile! Time to fund the chat's builds! Kappa",
        "Is this real life or fantasy?! HUGE DROP!",
        "Unbelievable drop luck! Buy a lottery ticket!",
        "GG! You won Path of Exile today!",
        "No way that just dropped! Check inventory!",
        "The loot filter beam reached the heavens! POG",
        "Pure dopamine drop! Clip it and ship it!",
        "Streamer priority loot table active! LUL",
        "Best drop of the league! Hands down!",
        "Chat, we are witnessing greatness! PogChamp",
        "Insane drop! Absolutely unethical loot!"
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
        "Pinnacle boss erased! Pure DPS check passed!",
        "That boss got completely melted! PogChamp",
        "Ez clap! Boss had zero chance!",
        "Phase skipped! Unethical single target DPS! KEKW",
        "Maven memory game passed without dying! PogChamp",
        "Exarch balls dodged like Neo! PogChamp",
        "Boss down! Show us the loot!",
        "Loot check: 2 alchemy orbs and a scroll of wisdom? LUL",
        "Uber boss down! Absolute gigachad!",
        "Clean execution! Great boss mechanics!",
        "Boss deleted from Wraeclast! GG!",
        "POG kill! That was down to the wire MonkaS",
        "No portals left, but the boss is dead! Clutch!",
        "The arena is clear! Gratz exile!",
        "Boss wiped off the map! Easy loot!",
        "Did you drop anything good? Fragment check!",
        "Pinnacle content conquered! Let's go!",
        "That boss slam was close, but you survived!",
        "Masterclass in boss dodging! PogChamp",
        "Wraeclast boss conquered! Next target please!",
        "DPS was monstrous! Boss stood no chance!",
        "Clean takedown! Clip the final hit!",
        "Boss down! Time to farm the next invitation!",
        "The Maven stands corrected! Boss destroyed!",
        "Flawless execution! GG exile!"
    ],

    # --- Path of Exile 2 (205 lines) ---
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
        "Stamina bar depleted? MonkaS",
        "PoE 2 soulslike mechanics claiming exiles left and right!",
        "Boss reset to 100% health! True pain BibleThump",
        "Welcome to the grim dark reality of Path of Exile 2!",
        "No portal hopping to cheese this boss! KEKW",
        "That boss combo was filthy! LUL",
        "Forgot you can't instant logout in PoE 2? Rolled!",
        "Heavy armor didn't save you from that crush! KEKW",
        "Dodge roll i-frames weren't enough! MonkaS",
        "Check your spirit reservations, exile!",
        "Ouch! That stagger bar hit 100% and you were toast!",
        "PoE 2 combat pacing: slow, methodical, deadly!",
        "Waypoint run of shame begins now! LUL",
        "Did that boss just parry you? KEKW",
        "PoE 2 graphics: 10/10. Survival skills: 2/10 Kappa",
        "That mob wind-up was huge and you still stood there! LUL",
        "Flask charges don't refill on portal in PoE 2! Pain!",
        "Staggered into the ground! Brutal!",
        "That boss wind-up was a whole cutscene! KEKW",
        "Died with full mana and zero stamina! Classic!",
        "Wraeclast 2.0 does not forgive mistakes!",
        "Should have weapon swapped to shield! Clueless",
        "The ground texture in PoE 2 is gorgeous from down there!",
        "PoE 2 boss: 1. Streamer: 0. Go next!",
        "Soulslike death screen when? KEKW",
        "Dodge roll into another attack? Pro gamer move! LUL",
        "The checkpoint is calling your name, exile!",
        "Stamina management is hard, don't worry chat understands!",
        "PoE 2 death penalties hit different! BibleThump",
        "F in the chat for the fallen PoE 2 exile!",
        "That boss sweep had a hitbox the size of Texas! KEKW",
        "Rolling backwards off a cliff? Classic!",
        "Flask charges don't refill at the well, exile! MonkaS",
        "Caught mid-cast with no cast speed! Pain!",
        "Heavy armor penalties caught up with you! KEKW",
        "Boss executed a 5-hit martial combo on your skull!",
        "Dodge roll into a poison puddle! 200 IQ play! LUL",
        "Staggered, stunned, flattened, resurrected!",
        "That boss had zero chill! NotLikeThis",
        "PoE 2 campaign claims another streamer soul!",
        "Stamina empty, sprint failed, crushed by a club! KEKW",
        "Back to the camp to talk to the hooded figure! Kappa",
        "That boss looked right at the camera before crushing you!",
        "The dodge roll i-frames were a lie! Copium"
    ],
    "poe2_boss_kill": [
        "First try! (100% real, no copium) KEKW",
        "Wow, PoE 2 boss actually defeated! Huge!",
        "POG boss down! Those mechanics were intense!",
        "Those dodge rolls were actually clean! PogChamp",
        "PoE 2 boss mechanics are wild. Well played!",
        "Loot check? Show us the gold!",
        "Gigachad boss killer!",
        "Stagger break was timed perfectly! PogChamp",
        "PoE 2 combat mastery on display! Let's go!",
        "Clean dodge rolls! That looked cinematic!",
        "Boss felled! Wraeclast is a little safer!",
        "Those combo weapon swaps during the boss fight were nuts!",
        "Boss down without dying! PoE 2 gamer verified!",
        "Show the loot drop! Gold and uncut gems!",
        "The stagger mechanic carried that fight! PogChamp",
        "Flawless roll execution! GG streamer!",
        "That boss looked like an Elden Ring boss! Huge kill!",
        "Pinnacle gameplay! PoE 2 boss down!",
        "Cleanest boss fight of the stream! PogChamp",
        "The mechanics in PoE 2 are top tier, well fought!",
        "Boss down! Grab the gold and check the skill gems!",
        "Weapon mastery paid off in that fight! GG!",
        "No health resets today! Ez clap!",
        "That stagger bar burst was pure satisfaction! POG",
        "Masterclass in PoE 2 tactical combat!",
        "Huge victory! Time to explore the next chapter!",
        "Boss eliminated! Clip that final combo!",
        "Uncut gem dropped? Show the skills!",
        "PoE 2 boss down! Great patience and dodging!",
        "Pinnacle boss erased! Cinematic takedown!",
        "That phase transition was wild! GG streamer!",
        "Loot goblin activated! Vacuum that boss drop!",
        "Ez clap for the streamer! On to the next act!",
        "Wraeclast boss conquered! Next challenger please!",
        "That boss didn't stand a chance against that combo!"
    ],
    "poe2_gold_drop": [
        "Are we playing Diablo now? Gold? KEKW",
        "Oooh shiny gold coins!",
        "Wealthy exile! Spend it wisely!",
        "Gold drop? PogChamp",
        "Time to gamble some items in town!",
        "Gold coins everywhere! Loot goblin mode!",
        "Filling the treasury one gold coin at a time!",
        "Gold sound is surprisingly addictive!",
        "Gamble that gold with the town vendors! LUL",
        "Rich exile alert! Gold bags secured!",
        "Don't spend it all on town respecs! Kappa",
        "Gold hoard growing! POG",
        "PoE 2 economy is all about that gold!",
        "Pick up every single coin! Respect the grind!",
        "Gold rush in Wraeclast! Let's go!",
        "Heavy gold pouch! Don't let the bandits get it!",
        "Gold stacks piling up! Money printer go brrr!",
        "Every single coin counts toward the next gamble!",
        "Gold drop chime is music to my ears! PogChamp",
        "Pockets getting heavy! Visit the merchant soon!"
    ],
    "poe2_level_up": [
        "Ding! PoE 2 level up!",
        "One step closer to the PoE 2 endgame!",
        "Gratz on the PoE 2 level! POG",
        "New skills unlocked! Let's see them!",
        "Ding! Time to check the dual-spec passive tree!",
        "Skill points for both weapon sets! PogChamp",
        "PoE 2 ding! Level up sound hits deep!",
        "More attribute points to equip heavier armor!",
        "Gratz! Dual-spec passive tree is so cool!",
        "Ding! Keep pushing through the campaign!",
        "Level up! More spirit unlocked for aura reservation!",
        "PoE 2 progression feels so good! Gratz!",
        "One level stronger! Time to test the new combo skills!",
        "Ding ding! Ascendancy progress looking clean!",
        "Gratz on the PoE 2 level! Keep up the momentum!",
        "Level ding! Higher spirit pool unlocked!",
        "New gear tier requirements unlocked! Check inventory!",
        "Campaign progression flying by! Gratz exile!",
        "Stats up, spirit up, survivability up! PogChamp",
        "Ding! That level up flash is so clean in PoE 2!"
    ],
    "poe2_disconnect": [
        "Disconnected! Classic GGG server quality KEKW",
        "Server boss defeated you! LUL",
        "Unexpected disconnection... RIP mapping!",
        "Chris Wilson pulled the plug! BibleThump",
        "Log out macro worked too well? Kappa",
        "Go next! Server status check time!",
        "Did the realm just crash? MonkaS",
        "Unexpected disconnection occurred! Classic PoE launch!",
        "Server said: That's enough gaming for today! KEKW",
        "Hope you didn't lose an instance! Clueless",
        "Rollback incoming? MonkaS",
        "Realm restart in 5... 4... KEKW",
        "Disconnected from server! Time for a water break!",
        "The true final boss of PoE 2: Connection Lost!",
        "Queue position: 42,000! Enjoy the wait! KEKW",
        "GGG hamster took a coffee break! LUL",
        "Login screen music intensifies! BibleThump",
        "Authentication timeout! Server said sit down!",
        "Instance crashed! Hope no mirrors were on the ground!",
        "Connection reset by peer! Classic launch experience!"
    ],
    "poe2_inventory_full": [
        "Inventory full... pick up more scrolls! KEKW",
        "Portal to town when? LUL",
        "Hoarder mentality exposed! NotLikeThis",
        "Time to play Tetris in your inventory...",
        "Drop the trash items! Kappa",
        "No room for more loot! Inventory management mini-game!",
        "Leave the white items on the ground, exile! KEKW",
        "Inventory grid completely clogged! Portal time!",
        "Classic ARPG hoarder problem! LUL",
        "Identify and drop! Keep the inventory clean!",
        "Full bags! Time to visit the town vendor!",
        "Can't pick that up: Inventory full voice line spammed!",
        "Drop the iron ring from act 1! You don't need it! KEKW",
        "Overburdened exile! Walk of shame to town!",
        "Inventory grid 100% occupied! Sell the junk!",
        "Your bags are crying for mercy! Portal out!"
    ],
    "poe2_out_of_mana": [
        "Out of mana again? KEKW",
        "Need more spirit! Get some mana regen LUL",
        "Gotta love the out of mana sound spammed... NotLikeThis",
        "Zdps because no spirit? Kappa",
        "Buy some mana flasks already!",
        "Clicking empty skills with 0 mana! Classic!",
        "No mana, no skills, just awkward auto attacks! LUL",
        "Mana flask empty! Running for your life MonkaS",
        "Spirit reserved 99% of your mana pool? KEKW",
        "Out of mana sound effect on repeat! NotLikeThis",
        "Unreserve an aura! You have zero mana to cast!",
        "Clicking aggressively with an empty blue orb! LUL",
        "Mana burned! Waiting for natural regen in combat! MonkaS",
        "Auto attacking a boss because 0 mana! Gigachad! KEKW",
        "Flask charges dry, mana empty, panic rolling!",
        "Get a clarity aura or mana leech gem ASAP!"
    ],

    # --- World of Warcraft (160 lines) ---
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
        "Release and run back! The corpse run walk of shame!",
        "Did anyone soulstone the healer? MonkaS",
        "Standing in the swirlies! Classic wipe!",
        "Tank lost aggro? Where is taunt? KEKW",
        "Battle rez burned already? NotLikeThis",
        "Check your combat log! What killed you?!",
        "Repair bill stonks going to the moon! LUL",
        "Healer was out of mana! Watch your healer's bar!",
        "Wipe count: +1! We go again!",
        "Release spirit... Running simulator 2026!",
        "That trash pack hit harder than the raid boss! KEKW",
        "Did you forget defensive cooldowns existed? LUL",
        "Durability in the red! Repair bot dropped?",
        "Don't stand in front of the dragon cleave! Classic mistake!",
        "Wipe it up, reset the pull! Go next!",
        "F in the chat for the repair gold!",
        "That mechanic was completely avoidable! KEKW",
        "Corpse run time! Enjoy the scenic graveyard view!",
        "Who body-pulled through stealth? Clueless",
        "Wiped at 1% boss health? Absolute heartbreak! BibleThump",
        "Mass resurrection incoming! Hold on!",
        "Durability check: Armor is broken! Kappa",
        "Release and run! Don't be that guy waiting for rez!",
        "Stood in the frontal cone! Classic raid wipe! KEKW",
        "Ghost wolf / wisp run time! Scenic tour of the dungeon!",
        "Did you pop a health pot or just accept your fate? LUL",
        "Healers OOM, tanks dead, DPS scattering like roaches!",
        "That mechanic had a 5-second cast time! Dodge it! MonkaS",
        "Durability 0%! Repair bot costs are through the roof!",
        "Who agro'd the patrol?! Confess in chat! KEKW",
        "Wipe #14 on this boss! Progression raiding at its finest!",
        "Resurrection sickness in spirit! Running back now!",
        "Don't release! Wait for the mass rez... Nevermind! LUL"
    ],
    "wow_achievement": [
        "Gratz on the achievement!",
        "Achievement unlocked! Achievement hunter PogChamp",
        "POG achievement! What a grind!",
        "Show off! KEKW",
        "Points went up! Huge gamer moment!",
        "I was here for the achievement! POG",
        "Achievement points stonks rising! PogChamp",
        "Feat of Strength unlocked! Absolute legend!",
        "That achievement grind was insane! Well done!",
        "Ding! Achievement toast on stream! You love to see it!",
        "Title unlocked? Equip it right now!",
        "Gamer score increased! Achievement unlocked!",
        "Big gratz! Another milestone down in Azeroth!",
        "POGGERS achievement moment! Clip that toast!",
        "Dedicated grind paid off! Gratz on the achievement!",
        "Lore master progress? Huge milestone! POG",
        "Raid achievement completed! Clean execution!",
        "Rare mount achievement unlocked?! Show it off!",
        "Gamer street cred just increased significantly!",
        "Achievement points total looking massive!",
        "Glory of the Raider progress! GG team!",
        "Completed without looking at a guide? Impressive! Kappa",
        "Gold border toast on stream! Clip that moment!",
        "Another achievement checked off the bucket list!",
        "Ding! Achievement points +10! We love to see it!"
    ],
    "wow_level_up": [
        "Ding! Gratz on the level!",
        "Level up! Time to go spend gold on gear KEKW",
        "The WoW grind continues! PogChamp",
        "Only many more levels to go... Kappa",
        "DING! Gratz! What zone next?",
        "Level up! POGGERS",
        "Ding! New talent tree point available!",
        "Azeroth hero grows stronger! Level up!",
        "Gratz! One level closer to max-level mythic dungeons!",
        "The ding sound effect in WoW is timeless! PogChamp",
        "Level achieved! Mount speed upgrade soon?",
        "Another ding in the books! Keep the questing going!",
        "Gratz on the level! Don't forget your class trainer!",
        "Ding! Level up hype in chat!",
        "More stats, higher ilvl, let's keep grinding!",
        "Gamer milestone! One ding closer to raiding!",
        "Time to queue up for the next dungeon tier!",
        "Level ding! Don't forget to spec into your core talent!",
        "Quest log turning green! Move to the next hub!",
        "Level cap speedrun in progress! PogChamp",
        "Ding! That golden level-up pillar of light never gets old!",
        "More stamina, more spell power, more DPS!",
        "Big level ding! Stretch your legs and hydrate!",
        "Another level conquered! Azeroth won't save itself!",
        "Level up! Keep the dungeon queue rolling!"
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
        "Mythic upgrade dropped! That ilvl jump!",
        "Roll 100 on that item! Huge win!",
        "Best-in-Slot item secured! Huge DPS increase incoming!",
        "Purple epic glow! The loot gods have spoken!",
        "Main hand upgrade? PogChamp",
        "Trinket dropped! Check the tier list!",
        "Raid loot luck is real! Gratz on the epic drop!",
        "Warforged / Titanforged tier luck! PogChamp",
        "Can you trade that if you don't need it? Kappa",
        "Gold border item! Absolute gigachad drop!",
        "Vault loot paying dividends! You love to see it!",
        "Drop rates blessed by the developers themselves!",
        "Loot master drama avoided! Straight into bags!",
        "Equip that right now! Let's see the ilvl increase!",
        "The purple glow of pure satisfaction! PogChamp",
        "Huge drop! DPS meter about to explode!",
        "Congratulations on the godly upgrade!",
        "Loot gods smiled on the stream today! GG!"
    ],
    "poe1_rare_drop": [
        "Tink! That loot filter sound is pure ecstasy!",
        "Valuable drop! Don't leave it on the ground!",
        "Tier 1 drop identified! Huge currency value!",
        "Loot beam active! Grab it before portal closes!",
        "Unethical drops today! Streamer RNG strikes again!",
        "The loot filter warned us! POG drop!",
        "Divine tier loot! Your net worth just went up!",
        "Check rolls on that item before you sell it!",
        "God roll potential! ID it right now on stream!",
        "Tink sound woke chat right up! PogChamp",
        "Loot filter beam reached the sky! Amazing drop!",
        "Exile luck is real! Big currency drop!",
        "Don't accidentally leave it in the map! MonkaS",
        "Cha-ching! The mapping profits are rolling in!",
        "Pure dopamine audio cue! Grab the loot!"
    ],
    "poe2_rare_drop": [
        "Uncut gem dropped! Time to craft new abilities!",
        "Golden item beam in PoE 2! Check the rolls!",
        "High tier loot identified! Pick it up!",
        "PoE 2 rare drop! The graphics make it look so juicy!",
        "Uncut skill gem! What skill are we leveling?",
        "Valuable currency drop! Gold and artifacts!",
        "Loot drop confirmed! Check item requirements!",
        "PoE 2 itemization paying off! Big upgrade!",
        "Trophy drop! Show the item stats to chat!",
        "Rare weapon dropped! Does it match your build?",
        "Loot beam looking gorgeous in Wraeclast 2.0!",
        "Big drop! Town vendor won't see this one!",
        "Socket it! Craft it! Vaal or no balls? Kappa",
        "PoE 2 loot luck turning around! Gratz exile!",
        "Unethical drop! Clip the item tooltip!"
    ],
    "generic_event": [
        "PogChamp in the chat!",
        "Gamer moment observed!",
        "Clip it and ship it!",
        "Unbelievable gameplay on display!",
        "Did you see that?! Pog",
        "Certified streamer moment KEKW",
        "The algorithm approves of this play!",
        "Highlight reel footage right there!",
        "Clean gaming! You love to see it!",
        "Absolute cinema on stream today!",
        "10/10 execution! GG!",
        "Chat, are we witnessing peak performance?",
        "Pro gaming maneuvers! PogChamp",
        "What a play! Clip it!",
        "Standing ovation from Twitch chat! POGGERS"
    ]
}


class ReactionEngine:
    def __init__(self):
        self.ai_provider = getattr(Config, "AI_PROVIDER", "curated")
        self.cooldowns = {}
        self.cooldown_duration = getattr(Config, "EVENT_COOLDOWN", 30.0)

    def get_reaction(self, event_id: str, ocr_context: str = "") -> str:
        """
        Get a reaction for the given event. Evaluates cooldown first.
        If Cloud LLM (Groq / OpenAI) or Ollama is configured, queries dynamic AI.
        Always falls back gracefully to curated 500+ deck with zero delay.
        """
        current_time = time.time()
        if event_id in self.cooldowns:
            if current_time - self.cooldowns[event_id] < self.cooldown_duration:
                return None
                
        # Register cooldown
        self.cooldowns[event_id] = current_time

        # If Cloud LLM or Ollama is configured, attempt dynamic reaction
        provider = getattr(Config, "AI_PROVIDER", "curated").lower()

        if provider in ("groq", "openai", "cloud"):
            llm_response = self._generate_cloud_llm_reaction(event_id, ocr_context)
            if llm_response:
                return llm_response

        elif provider == "ollama" or getattr(Config, "USE_OLLAMA", False):
            llm_response = self._generate_ollama_reaction(event_id, ocr_context)
            if llm_response:
                return llm_response

        # Default & resilient fallback: Instant curated reaction deck (0% CPU/GPU overhead)
        return self._get_prewritten_reaction(event_id, ocr_context)

    def _get_prewritten_reaction(self, event_id: str, ocr_context: str = "") -> str:
        reactions = PREWRITTEN_REACTIONS.get(event_id)
        if not reactions:
            # Fallback to generic reaction if unknown event
            return f"Event observed: {event_id.replace('_', ' ').title()}!"
            
        choice = random.choice(reactions)
        # Context interpolation if available
        if ocr_context and "{context}" in choice:
            choice = choice.replace("{context}", ocr_context.strip())
        return choice

    def _build_prompt(self, event_id: str, ocr_context: str) -> str:
        personality = getattr(Config, "BOT_PERSONALITY", "snarky and sarcastic")
        return (
            f"You are a Twitch chat bot with a {personality} personality watching a streamer play a video game. "
            f"The in-game event detected is '{event_id}'. "
            f"Context: '{ocr_context}'. "
            f"Write a single short, natural Twitch chat reaction (1-8 words) in your {personality} style. "
            f"Include appropriate Twitch emote names (e.g. KEKW, PogChamp, LUL, MonkaS). "
            f"Never use quotation marks or prefixes. Output only the reaction text."
        )

    def _generate_cloud_llm_reaction(self, event_id: str, ocr_context: str) -> str:
        """Queries Groq or OpenAI compatible endpoints with a tight 2.5s timeout."""
        provider = getattr(Config, "AI_PROVIDER", "groq").lower()

        if provider == "groq" or getattr(Config, "GROQ_API_KEY", ""):
            api_key = getattr(Config, "GROQ_API_KEY", "")
            base_url = "https://api.groq.com/openai/v1/chat/completions"
            model = getattr(Config, "GROQ_MODEL", "llama-3.1-8b-instant")
        else:
            api_key = getattr(Config, "OPENAI_API_KEY", "")
            base_url = f"{getattr(Config, 'OPENAI_BASE_URL', 'https://api.openai.com/v1').rstrip('/')}/chat/completions"
            model = getattr(Config, "OPENAI_MODEL", "gpt-4o-mini")

        if not api_key:
            return None

        prompt = self._build_prompt(event_id, ocr_context)
        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": "You are a witty Twitch chat live streamer companion."},
                {"role": "user", "content": prompt}
            ],
            "max_tokens": 30,
            "temperature": 0.85
        }
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

        try:
            resp = requests.post(base_url, json=payload, headers=headers, timeout=2.5)
            if resp.status_code == 200:
                data = resp.json()
                content = data["choices"][0]["message"]["content"].strip().strip('"').strip("'")
                if content:
                    return content
            else:
                logger.warning(f"Cloud LLM API error {resp.status_code}: {resp.text[:120]}")
        except Exception as e:
            logger.debug(f"Cloud LLM request failed: {e}")

        return None

    def _generate_ollama_reaction(self, event_id: str, ocr_context: str) -> str:
        """Queries local Ollama with a tight timeout."""
        ollama_url = getattr(Config, "OLLAMA_URL", "http://localhost:11434/api/generate")
        ollama_model = getattr(Config, "OLLAMA_MODEL", "llama3:8b")
        prompt = self._build_prompt(event_id, ocr_context)

        payload = {
            "model": ollama_model,
            "prompt": prompt,
            "stream": False
        }

        try:
            response = requests.post(ollama_url, json=payload, timeout=2.0)
            if response.status_code == 200:
                data = response.json()
                resp = data.get("response", "").strip().strip('"').strip("'")
                if resp:
                    return resp
        except Exception as e:
            logger.debug(f"Ollama request skipped: {e}")

        return None
