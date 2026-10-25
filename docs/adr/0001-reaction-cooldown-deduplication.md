# Cooldown-Based Event Deduplication

When both visual OCR and native log tailing observe the same physical in-game event (e.g. player death), they fire separate events into the application runner within seconds of each other. We decided to rely entirely on the ReactionEngine's 30-second cooldown per event ID to suppress duplicate reactions, rather than building an ingestion-layer event reconciler or message queue. This keeps the detection pipeline simple and stateless while satisfying the requirement that chat is not spammed.
