"""The live character.

Run it:  python -m homebot.face

Input, in order of how well it works today:
  * TYPE and press Enter        - always available, nothing to install
  * TOUCH or click the face     - poke the eyes, the mouth, the forehead, the
                                  cheeks; stroke it; poke it five times fast
  * HOLD SPACE to talk          - needs the optional voice deps, see voice.py

On a Raspberry Pi touchscreen, SDL delivers finger events as both FINGER* and
synthetic MOUSE* events. We read FINGER* when present and fall back to MOUSE*,
so the same file runs on a Mac with a trackpad and on the Pi with a finger.
"""

from __future__ import annotations

import sys
import collections
import gc
import queue
import threading
import time

import pygame

from . import expressions
from . import fallback
from . import reading
from .animator import Animator
from .mind import Mind
from .renderer import FaceRenderer, Quality
from .voice import Recorder, Transcriber

PANEL_W, PANEL_H = 640, 400
IDLE_SLEEP = 75.0     # seconds of nothing before it dozes off
REPLY_HOLD = 2.6
# The face read() picks from what you said is held at least this long before
# the brain's own states ("thinking", "answering") may replace it. Without
# it the reaction lasted one frame: the brain says "thinking" within a
# millisecond, so the face that understood you was never on screen.
READ_HOLD = 0.7
READ_HOLD_MAX = 3.5   # a long paragraph's beats may hold a little longer
# Faces that are about a moment, not a mood. Once nothing is happening they
# relax back to rest after this many seconds, instead of being held forever
# (a refused answer used to leave him apologising until the next input).
RELAX_AFTER = {"answering": REPLY_HOLD, "delight": REPLY_HOLD,
               "speaking": REPLY_HOLD, "apologetic": 6.0, "confusion": 6.0,
               "searching": 5.0, "waking": 4.0}


class FaceApp:
    def __init__(self, fullscreen: bool = False, cheap: bool = False,
                 size: tuple[int, int] = (PANEL_W, PANEL_H)):
        pygame.init()
        pygame.display.set_caption("homebot")
        flags = pygame.FULLSCREEN if fullscreen else pygame.RESIZABLE
        self.screen = pygame.display.set_mode(
            size if not fullscreen else (0, 0), flags)
        self.clock = pygame.time.Clock()

        self.renderer = FaceRenderer((PANEL_W, PANEL_H),
                                     Quality.cheap() if cheap else Quality())
        self.anim = Animator(self.renderer)
        self.mind = Mind(self._on_state, self._on_reply)
        self.rec = Recorder()
        self.stt = Transcriber()

        self.font = pygame.font.SysFont("menlo,dejavusansmono,monospace", 15)
        self.small = pygame.font.SysFont("menlo,dejavusansmono,monospace", 12)

        self.typed = ""
        self.caption = ""
        self.caption_until = 0.0
        self.debug = False
        self.running = True
        self.last_activity = time.monotonic()
        self.asleep = False
        self._reply_at = 0.0
        self._panel_rect = pygame.Rect(0, 0, PANEL_W, PANEL_H)
        # Brain callbacks arrive on the brain thread. They are put in this
        # inbox and applied by the UI loop, so only one thread ever touches
        # the Animator. Replies wait their turn in _speech: each is spoken in
        # full, in order, and none talks over the one before it.
        self._inbox: queue.SimpleQueue = queue.SimpleQueue()
        self._speech: collections.deque[str] = collections.deque()
        self._ui_thread = threading.current_thread()
        self._gc_at = 0.0
        # The optional emotion model loads in its own thread; the face never
        # waits for it (rules-only until it is ready, or for good if absent).
        fallback.start()

        # Everything built so far lives for the whole run: move it out of the
        # collector's sight, so a collection only walks what is new.
        gc.collect()
        gc.freeze()
        self.say(f"brain: {self.mind.backend}  |  {self.stt.hint()}"
                 "  -  type, hold F2 to talk, or poke my face", 7.0)

    # -- callbacks from the brain thread -----------------------------------

    def _on_state(self, state: str) -> None:
        if threading.current_thread() is not self._ui_thread:
            self._inbox.put(("state", state))
            return
        self._state_now(state)

    def _state_now(self, state: str) -> None:
        # While the read() face is still being
        # held, remember only the LATEST state; _idle_check applies it when
        # the hold runs out.
        if time.monotonic() < self.anim.reaction_until:
            self.anim.pending_state = state
            return
        self._apply_state(state)

    def _apply_state(self, state: str) -> None:
        self.anim.pending_state = None
        # A brain state is the truth about what he is doing right now, so it
        # ends any sequence that was playing - otherwise a "!nod_off" carries
        # on underneath and he yawns and falls asleep in the middle of an
        # answer.
        self.anim.stop_sequence()
        if state == "sleep":
            # Through the app's own sleep path, so app.asleep agrees with the
            # face: the next key plays the wake, and no yawn fires later on a
            # face that is already asleep.
            self._fall_asleep(yawn=False)
            return
        self.anim.set(expressions.BRAIN_STATES.get(state, "rest"))

    def _fall_asleep(self, yawn: bool = True) -> None:
        self.asleep = True
        self.anim.stop_sequence()
        if yawn:
            self.anim.flash("yawn", hold=1.6, duration=0.5)
        self.anim.set("asleep", duration=1.8)

    def _on_reply(self, text: str) -> None:
        if threading.current_thread() is not self._ui_thread:
            self._inbox.put(("reply", text))
            return
        self._reply_now(text)

    def _reply_now(self, text: str) -> None:
        # Still saying the last answer: this one waits its turn.
        if self.anim.speaking or self._speech:
            self._speech.append(text)
            return
        self._speak(text)

    def _drain(self) -> None:
        """UI thread: apply what the brain thread sent, then start the next
        queued reply once the current one has finished."""
        while True:
            try:
                kind, val = self._inbox.get_nowait()
            except queue.Empty:
                break
            if kind == "state":
                self._state_now(val)
            elif kind == "mood":
                self._apply_mood(*val)
            else:
                self._reply_now(val)
        if self._speech and not self.anim.speaking:
            self._speak(self._speech.popleft())

    def _drop_queued_replies(self) -> None:
        """UI thread: empty the inbox of replies, keep brain states."""
        keep = []
        while True:
            try:
                item = self._inbox.get_nowait()
            except queue.Empty:
                break
            if item[0] != "reply":
                keep.append(item)
        for item in keep:
            self._inbox.put(item)

    def _apply_mood(self, text: str, result) -> None:
        """UI thread: the model's reading of a line the rules had no cue
        for. Applied only if that line is still the one being reacted to."""
        if (result is None or text != getattr(self, "_read_text", None)
                or self.anim.speaking or time.monotonic() >= self.anim.reaction_until):
            return
        expr, conf, _label = result
        level = expressions.MID if conf >= 0.6 else expressions.LOW
        self.anim.set(expr, intensity=expressions.level_amount(expr, level))
        self.say(f"you: {text}   [{expr} / {level}]  (model {conf:.2f})", 3.0)

    def _speak(self, text: str) -> None:
        # Say it with the face, not just in the caption. speak() returns how
        # long the utterance runs, so the hold-then-rest timer waits for the
        # mouth to finish rather than cutting it off mid-sentence.
        spoken = self.anim.speak(text)
        self.say(text, max(7.0, spoken + 1.5))
        self._reply_at = time.monotonic() + spoken

    def say(self, text: str, hold: float = 4.0) -> None:
        self.caption = text
        self.caption_until = time.monotonic() + hold

    # -- input -------------------------------------------------------------

    def _panel_point(self, pos) -> tuple[float, float] | None:
        """Window coords -> panel coords, or None if outside the panel."""
        x, y = pos
        r = self._panel_rect
        if not r.collidepoint(x, y):
            return None
        return ((x - r.x) * PANEL_W / r.w, (y - r.y) * PANEL_H / r.h)

    def _wake(self, gesture: bool = False) -> None:
        """A touch wakes it too, but the ANIMATOR owns that story - it needs to
        still see base == "asleep" to play startled-then-waking. So for a
        gesture we only clear the flags here and let touch_down do the acting.
        Waking it up must never count as a poke, or being woken reads as being
        annoyed at you."""
        self.last_activity = time.monotonic()
        if self.asleep:
            self.asleep = False
            self.anim.clear_pokes()
            if not gesture:
                self.anim.set("waking")
                self.anim.flash("surprised", hold=0.5, duration=0.12)

    def handle(self, ev) -> None:
        if ev.type == pygame.QUIT:
            self.running = False
            return

        if ev.type == pygame.VIDEORESIZE:
            self.screen = pygame.display.set_mode(ev.size, pygame.RESIZABLE)
            return

        if ev.type == pygame.KEYDOWN:
            self._wake()
            if ev.key == pygame.K_ESCAPE:
                self.running = False
            elif ev.key == pygame.K_RETURN:
                text = self.typed.strip()
                self.typed = ""
                if text:
                    self._submit(text)
            elif ev.key == pygame.K_BACKSPACE:
                self.typed = self.typed[:-1]
            elif ev.key == pygame.K_TAB:
                self.debug = not self.debug
            elif ev.key == pygame.K_F1:
                self._cycle_demo()
            elif ev.key == pygame.K_F2:
                self._mic_down()
            elif ev.unicode and ev.unicode.isprintable():
                self.typed += ev.unicode
            return

        if ev.type == pygame.KEYUP and ev.key == pygame.K_F2:
            self._mic_up()
            return

        # Touch first, mouse as the fallback for the same gesture.
        if ev.type == pygame.FINGERDOWN:
            self._wake(gesture=True)
            p = self._panel_point((ev.x * self.screen.get_width(),
                                   ev.y * self.screen.get_height()))
            if p:
                self.say(f"*{self.anim.touch_down(*p)}*", 1.4)
        elif ev.type == pygame.FINGERMOTION:
            p = self._panel_point((ev.x * self.screen.get_width(),
                                   ev.y * self.screen.get_height()))
            if p:
                self.anim.touch_move(*p)
        elif ev.type == pygame.FINGERUP:
            p = self._panel_point((ev.x * self.screen.get_width(),
                                   ev.y * self.screen.get_height()))
            if p:
                self.anim.touch_up(*p)

        elif ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
            self._wake(gesture=True)
            p = self._panel_point(ev.pos)
            if p:
                self.say(f"*{self.anim.touch_down(*p)}*", 1.4)
        elif ev.type == pygame.MOUSEMOTION:
            p = self._panel_point(ev.pos)
            if p:
                if ev.buttons[0]:
                    self.anim.touch_move(*p)
                elif not self.asleep:
                    # Follow the cursor the way it will follow a face.
                    self.anim.look_at(*p, hold=0.35)
        elif ev.type == pygame.MOUSEBUTTONUP and ev.button == 1:
            p = self._panel_point(ev.pos)
            if p:
                self.anim.touch_up(*p)

    # -- voice -------------------------------------------------------------

    def _mic_down(self) -> None:
        if self.rec.recording:
            return
        if not self.rec.start():
            self.say(f"mic unavailable: {self.rec.error}", 5.0)
            self.anim.flash("apologetic", hold=1.2)
            return
        # Listening is a real state with a real face. Show it.
        self.anim.set("listening")
        self.say("listening... (release F2)", 30.0)

    def _mic_up(self) -> None:
        if not self.rec.recording:
            return
        wav = self.rec.stop()
        if not wav:
            self.anim.flash("confusion", hold=1.0)
            self.say("heard nothing", 2.0)
            self.anim.set("rest")
            return
        if not self.stt.ready:
            self.anim.flash("apologetic", hold=1.6)
            self.say(f"recorded {len(wav)//32000}s but {self.stt.hint()}", 7.0)
            self.anim.set("rest")
            return
        self.anim.set("thinking")
        self.say("transcribing...", 20.0)
        self.stt.transcribe(wav, self._on_transcript)

    def _on_transcript(self, text: str) -> None:
        text = (text or "").strip()
        if not text:
            self.anim.flash("confusion", hold=1.2)
            self.say("could not make that out", 3.0)
            self.anim.set("rest")
            return
        self._submit(text)

    def _submit(self, text: str) -> None:
        if text.startswith(">"):
            self.anim.speak(text[1:].strip() or "Testing, one two three.")
            self.say("speaking in: " + self.anim.base, 4.0)
            return
        if text.startswith("!"):
            # A sequence - a thought rather than a state.
            name = text[1:].strip()
            d = self.anim.play(name)
            if d:
                self.say(f"playing: {name}  ({d:.1f}s)", 2.5)
            else:
                self.say("sequences: " + ", ".join(expressions.sequence_names()), 9.0)
            return
        if text.startswith("+"):
            # Modifiers - adjectives that compose with whatever is showing.
            parts = text[1:].split()
            if len(parts) == 2 and parts[0] in ("lean", "strain", "fatigue"):
                try:
                    v = float(parts[1])
                except ValueError:
                    self.say("+lean/-1..1  +strain 0..1  +fatigue 0..1", 5.0); return
                getattr(self.anim, parts[0])(v)
                self.say(f"{parts[0]} = {v:+.2f}", 2.0)
            else:
                self.say("+lean -1..1   +strain 0..1   +fatigue 0..1", 6.0)
            return
        if text.startswith("/"):
            arg = text[1:].strip()
            # "/bored happy 0.3" holds a BLEND; "/angry *0.4" sets intensity.
            bits = arg.split()
            name = bits[0] if bits else ""
            mix, amount, intensity = None, 0.0, 1.0
            for b in bits[1:]:
                if b.startswith("*"):
                    try: intensity = float(b[1:])
                    except ValueError: pass
                elif b.replace(".", "", 1).isdigit():
                    amount = float(b)
                elif b in expressions.names():
                    mix = b
            if name in expressions.names():
                self.anim.stop_sequence()
                self.anim.set(name, mix=mix, amount=amount or 0.5, intensity=intensity)
                label = name
                if mix:
                    label += f" + {mix} {int((amount or 0.5)*100)}%"
                if intensity != 1.0:
                    label += f" @{intensity:.2f}"
                self.say("holding: " + label, 2.5)
            else:
                self.say("expressions: " + ", ".join(expressions.names()), 9.0)
            return
        # React to what was SAID, at the strength it was said with. He used to
        # go to a flat "listening" for everything, which made every sentence
        # look the same to him. A paragraph gets one face per sentence, in
        # order: "I got the job! But I'll miss everyone." is two reactions.
        # Rules only here - this is the UI thread. If they found nothing,
        # the optional model is asked on a worker and its answer arrives
        # through the inbox (see _apply_mood).
        beats = reading.read_beats(text, model=False)
        name, level, amount, why, _ = beats[0]
        # The user is talking: stop talking over them (a fade, not a cut),
        # and drop every reply still waiting its turn - they answered
        # what was said BEFORE this, and would otherwise resume over it.
        self._speech.clear()
        self._drop_queued_replies()
        if self.anim.speaking:
            self.anim.hush()
        self._read_text = text
        if len(beats) == 1 and why is None and fallback.available():
            fallback.ask_async(text, lambda r, t=text: self._inbox.put(("mood", (t, r))))
        self.anim.stop_sequence()
        if len(beats) > 1:
            self.anim.play_steps([(b[0], b[4], b[2]) for b in beats])
            shown = sum(b[4] for b in beats[:-1])
        else:
            self.anim.set(name, intensity=amount)
            shown = 0.0
        self.anim.reaction_until = time.monotonic() + min(READ_HOLD_MAX, shown + READ_HOLD)
        self.anim.pending_state = None
        tag = " > ".join(f"{b[0]} / {b[1]}" for b in beats)
        if why and len(beats) == 1:
            tag += f'  ("{why}")'
        busy = self.mind.busy
        self.say(f"you: {text}   [{tag}]" + ("   (after this one)" if busy else ""), 3.5)
        self.mind.ask(text)

    def _cycle_demo(self) -> None:
        self._demo = getattr(self, "_demo", -1) + 1
        all_names = expressions.names()
        name = all_names[self._demo % len(all_names)]
        self.anim.set(name)
        self.say(f"{name}  ({self._demo % len(all_names) + 1}/{len(all_names)})", 3.0)

    # -- frame -------------------------------------------------------------

    def _gc_tick(self, now: float) -> None:
        # The ~1-2 ms frame spikes were the cyclic garbage collector. Collect the
        # young generations on quiet frames, where a pause cannot be seen, so
        # the automatic collections rarely land in the middle of speech.
        if self.anim.speaking:
            return
        if now - self._gc_at > 1.0:
            self._gc_at = now
            gc.collect(1)

    def _idle_check(self) -> None:
        self._drain()
        now = time.monotonic()
        self._gc_tick(now)
        if self.anim.pending_state is not None and now >= self.anim.reaction_until:
            self._apply_state(self.anim.pending_state)
        if self.mind.busy:
            self.last_activity = now
            return
        quiet = now - self.last_activity
        base = self.anim.base
        if quiet > IDLE_SLEEP and not self.asleep:
            self._fall_asleep()
        elif (not self.asleep and base in RELAX_AFTER and not self.anim.speaking
              and not self.anim.playing and now >= self.anim.reaction_until):
            if base in ("answering", "delight", "speaking"):
                # only after a reply: these are what he says, not how he is
                ready = self._reply_at and now - self._reply_at > RELAX_AFTER[base]
            else:
                since = max(self._reply_at, self.anim.base_since)
                ready = (now - since > RELAX_AFTER[base]
                         and quiet > 1.5)   # not while you are still typing
            if ready:
                self._reply_at = 0.0
                self.anim.set("rest", duration=0.7)

    def draw(self) -> None:
        sw, sh = self.screen.get_size()
        self.screen.fill((9, 9, 10))

        margin = 34
        avail_w, avail_h = sw - margin * 2, sh - margin * 2 - 58
        scale = max(0.2, min(avail_w / PANEL_W, avail_h / PANEL_H))
        pw, ph = int(PANEL_W * scale), int(PANEL_H * scale)
        self._panel_rect = pygame.Rect((sw - pw) // 2, margin, pw, ph)

        self.renderer.draw_bezel(self.screen, self._panel_rect)
        panel = self.renderer.render(self.anim.update())
        self.screen.blit(pygame.transform.smoothscale(panel, (pw, ph)),
                         self._panel_rect.topleft)

        y = self._panel_rect.bottom + 22
        if self.caption and time.monotonic() < self.caption_until:
            self._text(self.caption[:110], 24, y, (196, 196, 200))
            y += 22
        prompt = "> " + self.typed + ("_" if int(time.time() * 2) % 2 else " ")
        self._text(prompt, 24, y, (255, 176, 70))

        if self.debug:
            a = self.anim
            lines = [
                f"fps {self.clock.get_fps():5.1f}   base {a.base:<11} overlay {a.overlay_name or '-'}",
                f"touch {a.last_touch or '-':<12} brain {self.mind.backend} ({self.mind.detail})",
                "F1 cycle  F2 talk  >speak  /pose [mix amt] [*int]  !sequence  +lean/strain/fatigue  TAB  ESC",
            ]
            for i, ln in enumerate(lines):
                self._text(ln, 24, 6 + i * 15, (110, 110, 118), small=True)

    def _text(self, s: str, x: int, y: int, colour, small: bool = False) -> None:
        f = self.small if small else self.font
        self.screen.blit(f.render(s, True, colour), (x, y))

    def run(self) -> None:
        while self.running:
            for ev in pygame.event.get():
                self.handle(ev)
            self._idle_check()
            self.draw()
            pygame.display.flip()
            self.clock.tick(50)
        pygame.quit()


def main(argv: list[str] | None = None) -> int:
    argv = argv if argv is not None else sys.argv[1:]
    FaceApp(fullscreen="--fullscreen" in argv, cheap="--cheap" in argv).run()
    return 0
