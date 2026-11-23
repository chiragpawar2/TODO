"""The conversation loop: build the prompt, let the engine use tools, return a reply.

This file knows nothing about Gemini, Claude or Ollama. It speaks the neutral
message format from engines/base.py, so swapping provider changes nothing here.

Cost and speed notes:
  * The system prompt holds only unchanging things (household rules, member
    list). Volatile text - the clock, who is speaking, current tasks - goes in
    the user turn, so the Claude engine's prompt cache is never invalidated.
  * Only the last `history_turns` exchanges are resent.
  * Replies are kept to a sentence or two, which is both cheaper and better
    when the answer is going to be spoken aloud.
"""

from __future__ import annotations

import json
from datetime import datetime
from typing import Any

from .config import Config
from .engines import Engine, make_engine
from .store import Store
from .tools import TOOLS, dispatch

MAX_TOOL_ROUNDS = 6  # a runaway tool loop wastes quota and time


class Brain:
    def __init__(self, config: Config, store: Store, engine: Engine | None = None):
        self.config = config
        self.store = store
        self.engine = engine or make_engine(config)
        self.history: list[dict[str, Any]] = []

    # --- prompt construction ----------------------------------------------

    def system_prompt(self) -> str:
        """The stable half. Keep byte-identical between calls so it stays cacheable."""
        cfg = self.config
        members = "\n".join(
            f"  - {p.name} ({p.role}){': ' + p.notes if p.notes else ''}" for p in cfg.people
        ) or "  (nobody registered yet - ask who lives here)"

        return f"""You are the home assistant for {cfg.household_name}. You live on a small
device in the {cfg.room} and everyone in the house talks to you out loud.

Household members:
{members}

Languages: you may be spoken to in {", ".join(cfg.languages)}. Always reply in the
same language the person used.

How to behave:
- You are speaking aloud, not writing. Keep replies to one or two short sentences.
- Never use markdown, bullet points, asterisks or emoji - they sound wrong when read out.
- When someone mentions work they must do, add it as a task without being asked twice.
- Before answering any question about tasks, chores or the shopping list, call a tool
  to look it up. Never guess at household state.
- When a person tells you something worth knowing next week - a preference, an
  allergy, a birthday, a schedule - save it with the remember tool.
- After you call a tool, reply to the person in words. Never answer with only a tool call.
- If several people are involved, say who each thing belongs to.
- If you are unsure who is talking to you, ask.
- If you cannot do something, say so plainly in one sentence.

You are part of the family's daily life. Be warm, brief and practical."""

    def _context_preamble(self, speaker: str | None) -> str:
        """Volatile context. Lives in the user turn so it never breaks the cache."""
        now = datetime.now()
        parts = [
            f"[Current time: {now.strftime('%A %d %B %Y, %I:%M %p')}]",
            f"[Today's date for any due date you set: {now.strftime('%Y-%m-%d')}]",
            f"[Speaking to you now: {speaker or 'unknown person'}]",
        ]
        briefing = self.store.briefing()
        if briefing:
            parts.append(f"[Current household state:\n{briefing}\n]")
        return "\n".join(parts)

    # --- the conversation --------------------------------------------------

    def ask(self, text: str, speaker: str | None = None, verbose: bool = False) -> str:
        """Handle one thing a person said. Runs any tools requested, returns the reply."""
        self.store.log_message("user", text, speaker=speaker)

        turns = self._trimmed_history()
        turns.append(
            {"role": "user", "text": f"{self._context_preamble(speaker)}\n\n{text}"}
        )

        reply = ""
        for _ in range(MAX_TOOL_ROUNDS):
            result = self.engine.complete(self.system_prompt(), turns, TOOLS)

            if result.refused:
                reply = "Sorry, I can't help with that one."
                break

            turns.append(
                {
                    "role": "assistant",
                    "text": result.text,
                    "tool_calls": result.tool_calls,
                }
            )

            if not result.tool_calls:
                reply = result.text
                break

            for call in result.tool_calls:
                output = dispatch(self.store, call.name, call.args, speaker=speaker)
                if verbose:
                    print(f"  [tool] {call.name}({json.dumps(call.args)}) -> {output[:160]}")
                turns.append(
                    {"role": "tool", "id": call.id, "name": call.name, "content": output}
                )
        else:
            reply = "I got stuck working that out. Can you say it again more simply?"

        if not reply:
            # Some smaller models stop after a tool call without saying anything.
            reply = "Done."

        self.store.log_message("assistant", reply, speaker=speaker)
        self.history = turns
        return reply

    def _trimmed_history(self) -> list[dict[str, Any]]:
        """Keep recent turns only - fewer resent tokens means less quota used."""
        keep = self.config.brain.history_turns * 2
        trimmed = list(self.history[-keep:]) if keep else []
        # A conversation may not begin with an assistant turn or a stray tool
        # result, so drop leading fragments until it starts on a user turn.
        while trimmed and trimmed[0]["role"] != "user":
            trimmed.pop(0)
        return trimmed
