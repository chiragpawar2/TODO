# Live voice checks

- `node tests/live/turn_sequence.mjs docs/index.html`: offline; list/message changes are kept when a model ends the turn after a tool call and speaks in a second turn (Gemini 3.8 Live) and when it speaks in the same turn (3.1).
- `node tests/live/live_models_check.mjs <key> gemini-3.8-live gemini-3.1-flash-live-preview`: live; connects, sends a Marathi list request, prints the tool call, the message order and the time to first audio.
