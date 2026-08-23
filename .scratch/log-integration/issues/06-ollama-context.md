Status: claimed (Agent)
Type: task

## Question

Now that `LogWatcher` returns rich context like `wow_loot: 'Player looted [Thunderfury]'` and `wow_achievement: 'Player earned [Realm First]'`, we need to actually inject this dynamic context into the Ollama prompt in `reaction_engine.py` so the bot can generate a hyper-specific, contextual roast. Update `reaction_engine.py` to use the `ocr_context` parameter natively in its Ollama system prompt.
