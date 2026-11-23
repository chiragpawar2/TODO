"""Wires the face to homebot's Brain, without touching Brain.

The nine expressions are not decoration - each one is a real branch in
homebot/brain.py. To drive them we need to know when the engine is thinking and
when a tool is running, and `Brain.ask()` does not report that.

Rather than edit brain.py, we instrument it from outside:
  * the engine object is wrapped, so `complete()` announces itself
  * `homebot.brain.dispatch` is swapped for a wrapper that announces tool calls

Both are reversible and brain.py stays exactly as it is.

If there is no working API key, `OfflineMind` takes over so the character is
still fully interactive. It says so plainly rather than pretending.
"""

from __future__ import annotations

import random
import re
import threading
from typing import Callable

StateFn = Callable[[str], None]


class OfflineMind:
    """Keyword replies, used when no engine is configured. Honest about it."""

    GREET = ("hi", "hello", "hey", "namaste", "namaskar", "हाय")
    THANKS = ("thanks", "thank", "dhanyavad", "धन्यवाद")
    JOKE = ("joke", "funny", "laugh")
    BYE = ("bye", "goodnight", "good night", "sleep")

    def ask(self, text: str, speaker=None, on_state: StateFn = lambda s: None) -> str:
        t = text.lower().strip()
        on_state("thinking")
        # Whole words: "and chillies" contains "hi", "Delhi" too.
        words = set(re.findall(r"[\w']+", t))
        has = lambda keys: any((k in t) if " " in k else (k in words) for k in keys)
        if has(self.GREET):
            on_state("success")
            return "Hello. I am running without a brain key right now, so I can only make faces."
        if has(self.THANKS):
            on_state("success")
            return "Any time."
        if has(self.JOKE):
            on_state("success")
            return "I would tell you one, but my sense of humour is in the API key."
        if has(self.BYE):
            on_state("sleep")
            return "Goodnight."
        if "?" in t:
            on_state("tool")
            return "I cannot look that up yet. Set GEMINI_API_KEY in .env and I will."
        on_state("speaking")
        return random.choice([
            "Noted, though I am only pretending to remember it.",
            "I hear you. No brain attached yet.",
            "Right. Give me an API key and I will mean that.",
        ])


class Mind:
    """Runs the brain off the UI thread and reports what it is doing."""

    def __init__(self, on_state: StateFn, on_reply: Callable[[str], None]):
        self.on_state = on_state
        self.on_reply = on_reply
        self.busy = False
        self._queue: list[tuple[str, str | None]] = []
        self._lock = threading.Lock()
        self.backend = "offline"
        self.detail = ""
        self._brain = None
        self._store = None
        self._offline = OfflineMind()
        self._connect()

    def _connect(self) -> None:
        try:
            from ..config import load_config
            from ..store import Store
            from ..brain import Brain
            from .. import brain as brain_mod

            cfg = load_config()
            self._store = Store(cfg.resolved_db_path)
            brain = Brain(cfg, self._store)

            engine = brain.engine
            emit = lambda s: self.on_state(s)

            class _Watched:
                def complete(self, system, turns, tools):
                    emit("thinking")
                    return engine.complete(system, turns, tools)

            brain.engine = _Watched()

            if not getattr(brain_mod, "_face_patched", False):
                original = brain_mod.dispatch

                def watched_dispatch(store, name, args, speaker=None):
                    emit("tool")
                    out = original(store, name, args, speaker=speaker)
                    emit("success")
                    return out

                brain_mod.dispatch = watched_dispatch
                brain_mod._face_patched = True

            self._brain = brain
            self.backend = cfg.brain.engine
            self.detail = cfg.brain.model or "default model"
        except Exception as exc:  # no key, bad config, missing dep - all fine
            self.backend = "offline"
            self.detail = f"{type(exc).__name__}: {exc}"[:110]

    def ask(self, text: str, speaker: str | None = None) -> bool:
        """Hand a line to the brain. Returns False if it had to wait its turn.

        A line typed while the brain is still working used to be dropped
        without a word - "and tomatoes" simply never happened. Now it is
        queued and answered, in order, once the current one is done."""
        with self._lock:
            if self.busy:
                self._queue.append((text, speaker))
                return False
            self.busy = True
        threading.Thread(target=self._run, args=(text, speaker), daemon=True).start()
        return True

    @property
    def queued(self) -> int:
        return len(self._queue)

    def _run(self, text: str, speaker: str | None) -> None:
        while True:
            self._work(text, speaker)
            with self._lock:
                if not self._queue:
                    self.busy = False
                    return
                text, speaker = self._queue.pop(0)

    def _work(self, text: str, speaker: str | None) -> None:
        try:
            if self._brain is None:
                reply = self._offline.ask(text, speaker, self.on_state)
            else:
                self.on_state("thinking")
                reply = self._brain.ask(text, speaker=speaker)
                low = reply.lower()
                if low.startswith("sorry, i can't help"):
                    self.on_state("refused")
                elif low.startswith("i got stuck"):
                    self.on_state("stuck")
                else:
                    self.on_state("speaking")
            self.on_reply(reply)
        except Exception as exc:
            self.on_state("refused")
            self.on_reply(f"Something broke: {type(exc).__name__}: {exc}")
