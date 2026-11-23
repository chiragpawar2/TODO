"""Tweening, the idle life layer, touch reactions, and speech.

Five things stack every frame, in this order:

  1. BEAT      - the pose arrives on a curve that belongs to THAT expression:
                 its own duration, anticipation and overshoot.
  2. OVERLAP   - eye shape leads, pupils follow, mouth after them, glow and
                 tilt last. The face arrives as a chain of cause and response.
  3. IDLE      - blinks, saccades, breathing and drift, at a rate that also
                 belongs to that expression. A hold is a performance, not a
                 frozen drawing.
  4. SPEECH    - one impulse signal spent across the whole face, not a mouth
                 animation. See speech.py.
  5. REACTION  - a touch pushes a short-lived expression in front, then hands
                 control back.

Why 1 and 2 exist at all: the earlier version ran every transition on one
shared smoothstep, which is precisely what the motion study forbids -
"do not make every acceleration mathematically even. A living action has
designed changes of rate." Startled and asleep cannot share an easing curve
and still both be true.

Timings for layer 3:
  * blink interval 2.8-6.5s   - humans blink 14-17/min at rest
  * blink close 120ms, open 90ms  - closing is faster than opening
  * re-gaze every 1.2-3.4s, each saccade under 80ms and then dead still
"""

from __future__ import annotations

import math
import random
import time
from dataclasses import dataclass, fields

from . import expressions
from .params import FaceParams, blend_channels, sanitise
from .visemes import VisemeTrack

BLINK_MIN, BLINK_MAX = 2.8, 6.5
BLINK_CLOSE, BLINK_OPEN = 0.12, 0.09
GAZE_MIN, GAZE_MAX = 1.2, 3.4
MACRO = 0.42

# Channel lag as a fraction of the transition. Small numbers: this is a face,
# not a tail - too much and it reads as broken rather than alive.
LAG_SHAPE, LAG_PUPIL, LAG_MOUTH, LAG_GLOBAL = 0.0, 0.05, 0.13, 0.19

# The breathing and talking SETTINGS follow the pose over time instead of
# swapping on the frame the pose changes. Swapping them made the glow jump
# by up to a quarter of its brightness in one frame (rest -> asleep), and the
# head bob jump when the mood changed mid-sentence.
IDLE_TAU, TALK_TAU = 0.45, 0.25
# Speech is never cut in one frame: an interrupted or replaced utterance
# fades out over this long, and a mouthless pose grows its mouth this fast
# while it talks (and lets it go a little slower once it stops).
SPEECH_FADE = 0.15
MOUTH_SHOW_TAU, MOUTH_HIDE_TAU = 0.05, 0.18
_IDLE_FIELDS = [f.name for f in fields(expressions.Idle)]
_TALK_FIELDS = [f.name for f in fields(expressions.Talk)]


def _ease(dt: float, tau: float) -> float:
    return 1.0 - math.exp(-dt / tau) if tau > 0 else 1.0


def _smoothstep(t: float) -> float:
    t = max(0.0, min(1.0, t))
    return t * t * (3.0 - 2.0 * t)


def _act_curve(u: float, antic: float, over: float, snap: float) -> float:
    """Progress 0..1 reshaped into an acted move.

    Returns values BELOW 0 during anticipation and ABOVE 1 during overshoot;
    the blend extrapolates, which is exactly what we want - the face really
    does pull back before it strikes.
    """
    u = max(0.0, min(1.0, u))
    if snap > 0.001:
        # Snap compresses the whole move into the front of its window, so a
        # hard hold arrives and then simply sits there.
        u = min(1.0, u / max(1e-6, 1.0 - 0.92 * snap))
    a_end = 0.24 if antic > 0.001 else 0.0
    if u < a_end:
        return -antic * _smoothstep(u / a_end)
    if over > 0.001:
        peak = a_end + (1.0 - a_end) * 0.66
        if u < peak:
            s = _smoothstep((u - a_end) / (peak - a_end))
            return -antic + (1.0 + over + antic) * s
        s = _smoothstep((u - peak) / (1.0 - peak))
        return (1.0 + over) + (1.0 - (1.0 + over)) * s
    s = _smoothstep((u - a_end) / max(1e-6, 1.0 - a_end))
    return -antic + (1.0 + antic) * s


@dataclass
class Region:
    name: str
    cx: float
    cy: float
    rx: float
    ry: float

    def hit(self, x: float, y: float) -> bool:
        if self.rx <= 0 or self.ry <= 0:
            return False
        return ((x - self.cx) / self.rx) ** 2 + ((y - self.cy) / self.ry) ** 2 <= 1.0


class Animator:
    def __init__(self, renderer):
        self.r = renderer
        self.current = expressions.get("rest")
        self._from = self.current.copy()
        self._to = self.current.copy()
        self._beat = expressions.beat("rest")
        self._t0 = time.monotonic()

        self.base = "rest"
        self.base_since = time.monotonic()
        self._base_dur: float | None = None
        self._mix: str | None = None
        self._mix_amount = 0.0
        self._intensity = 1.0
        self._seq: list[tuple[str, float, float]] = []   # (name, hold, intensity)
        self._seq_next = 0.0
        self._lean = 0.0
        self._strain = 0.0
        self._fatigue = 0.0
        self._overlay: str | None = None
        self._overlay_until = 0.0

        now = time.monotonic()
        self._next_blink = now + random.uniform(BLINK_MIN, BLINK_MAX)
        self._blink_start = 0.0
        self._blinking = False
        self._next_gaze = now + random.uniform(GAZE_MIN, GAZE_MAX)
        self._gaze = (0.0, 0.0)
        self._gaze_from = (0.0, 0.0)
        self._gaze_t0 = now

        self._look_at: tuple[float, float] | None = None
        self._look_until = 0.0

        self._utt: VisemeTrack | None = None
        self._utt_t0 = 0.0
        # Utterances on their way out: (track, start, fade_start).
        self._fading: list[tuple[VisemeTrack, float, float]] = []
        self._mouth_show = 0.0

        # The reaction to what the user just said is protected until this
        # time; brain states that arrive sooner wait in pending_state (the app
        # applies them). It lives here because it is about what the FACE is
        # showing, and a fresh face starts with nothing held.
        self.reaction_until = 0.0
        self.pending_state: str | None = None

        self._last_now = now
        self._idle_s = {k: getattr(expressions.idle("rest"), k) for k in _IDLE_FIELDS}
        self._talk_s = {k: getattr(expressions.talk("rest"), k) for k in _TALK_FIELDS}
        self._breath_phase = 0.0
        self._sleep_w = 0.0

        self._pokes: list[float] = []
        self._press_at: tuple[float, float] | None = None
        self._press_t0 = 0.0
        self._drag = 0.0
        self.last_touch = ""

        self.regions = self._build_regions()

    # -- regions -----------------------------------------------------------

    def _build_regions(self) -> list[Region]:
        r = self.r
        return [
            Region("left_eye", r.w * 0.5 - r.eye_gap, r.cy, r.eye_hw * 1.25, r.eye_hh * 1.25),
            Region("right_eye", r.w * 0.5 + r.eye_gap, r.cy, r.eye_hw * 1.25, r.eye_hh * 1.25),
            Region("mouth", r.w * 0.5, r.mouth_y, r.mouth_hw * 1.9, r.h * 0.085),
            Region("forehead", r.w * 0.5, r.h * 0.10, r.w * 0.5, r.h * 0.13),
            Region("cheek_left", r.w * 0.14, r.h * 0.62, r.w * 0.16, r.h * 0.2),
            Region("cheek_right", r.w * 0.86, r.h * 0.62, r.w * 0.16, r.h * 0.2),
        ]

    def region_at(self, x: float, y: float) -> str:
        for reg in self.regions:
            if reg.hit(x, y):
                return reg.name
        return "panel"

    def clear_pokes(self) -> None:
        self._pokes.clear()

    @property
    def overlay_name(self) -> str | None:
        return self._overlay

    # -- expression control ------------------------------------------------

    def set(self, name: str, duration: float | None = None,
            mix: str | None = None, amount: float = 1.0,
            intensity: float = 1.0) -> None:
        """Hold an expression - or a point BETWEEN two of them.

        This is where the range actually comes from. 43 named poses is a
        vocabulary; holding a blend of two is grammar, and the parametric face
        was built for exactly this. "70% tired, 30% pleased" is not a pose
        anybody designed and it reads perfectly, because every pose is a point
        in one continuous space and so is everything between them.

        mix/amount  hold a blend: set("bored", mix="happy", amount=0.3)
        intensity   how far toward the pose to travel at all. 0.4 is a hint
                    of it, 1.4 overshoots past it into caricature. The same
                    pose at three intensities is three different readings -
                    mildly annoyed and furious are not different shapes.
        """
        if name != self.base:
            self.base_since = time.monotonic()
        self.base = name
        self._base_dur = duration
        self._mix = mix
        self._mix_amount = max(0.0, min(1.0, amount)) if mix else 0.0
        self._intensity = max(0.0, min(1.6, intensity))
        if self._overlay is None:
            self._begin(name, duration)

    def play(self, name: str) -> float:
        """Run a sequence. Returns how long it takes.

        A pose shows a state; a sequence shows a THOUGHT, because a thought is
        a change and a change needs two states to be a change between.
        """
        return self.play_steps(expressions.sequence(name))

    def play_steps(self, steps: list[tuple[str, float, float]]) -> float:
        """Run any list of (expression, hold, intensity) beats - a named
        sequence, or the beats reading.read_beats() found in a paragraph."""
        steps = list(steps)
        if not steps:
            return 0.0
        self._seq = steps[1:]
        first, hold, amt = steps[0]
        self._seq_next = time.monotonic() + hold
        self.set(first, intensity=amt)
        return sum(h for _, h, _ in steps)

    def stop_sequence(self) -> None:
        self._seq = []

    @property
    def playing(self) -> bool:
        return bool(self._seq)

    # -- modifiers: adjectives, not words ----------------------------------
    #
    # These compose with ANY of the 43 poses instead of being poses of their
    # own, so they multiply the range rather than adding to it. They also put
    # the five dials no expression ever touched to work.

    def lean(self, amount: float) -> None:
        """Posture. + leans in toward you, - pulls back. Uses `scale`, which
        no expression moves: the face is the only body this character has, so
        getting closer IS leaning forward."""
        self._lean = max(-1.0, min(1.0, amount))

    def strain(self, amount: float) -> None:
        """Eyes converging inward - effort, focus, or being cross-eyed with
        frustration. Uses eye.x, which nothing else moves."""
        self._strain = max(-1.0, min(1.0, amount))

    def fatigue(self, amount: float) -> None:
        """Drops both lids and dims, on top of whatever is already showing.
        Tired-and-happy and tired-and-cross are different faces, and neither
        is a pose anybody has to design."""
        self._fatigue = max(0.0, min(1.0, amount))

    def flash(self, name: str, hold: float = 1.1, duration: float | None = None) -> None:
        self._overlay = name
        self._overlay_until = time.monotonic() + hold
        self._begin(name, duration)

    def look_at(self, x: float, y: float, hold: float = 1.6) -> None:
        nx = (x - self.r.w * 0.5) / (self.r.w * 0.5)
        ny = (y - self.r.cy) / (self.r.h * 0.5)
        self._look_at = (max(-1.0, min(1.0, nx)), max(-1.0, min(1.0, ny)))
        self._look_until = time.monotonic() + hold

    def _begin(self, name: str, duration: float | None = None) -> None:
        self._from = self.current.copy()
        target = expressions.get(name)
        if self._mix and self._mix_amount > 0.001:
            target = target.blend(expressions.get(self._mix), self._mix_amount)
        if abs(self._intensity - 1.0) > 0.001:
            # Scale the whole pose relative to REST, not to zero - the amount
            # of an expression is how far it has travelled from neutral.
            full = target
            target = expressions.get("rest").blend(target, self._intensity)
            # ...but a mouthless pose must stay mouthless, and hidden pupils
            # must stay hidden. These two are STRUCTURAL, not matters of
            # degree: fading them back in grows a ghost mouth inside a face
            # whose whole design is that it has none. There is no "slightly
            # has a mouth".
            if full.mouth_alpha < 0.02:
                target.mouth_alpha = 0.0
            for src, dst in ((full.left, target.left), (full.right, target.right)):
                if src.pupil_alpha < 0.02:
                    dst.pupil_alpha = 0.0
            if self._intensity > 1.0:
                # Past 100% a pose is caricature, and a few channels break
                # rather than exaggerate: stern's slit closes to a hairline,
                # dread's pupils shrink to pinpricks, a smile bends past the
                # arc the renderer was drawn for. Hold those at the point
                # where they still read as MORE of the pose.
                for src, dst in ((full.left, target.left), (full.right, target.right)):
                    dst.h = max(dst.h, min(src.h, 0.12))
                    dst.pupil_scale = max(dst.pupil_scale, min(src.pupil_scale, 0.38))
                    dst.pupil_x = max(-0.9, min(0.9, dst.pupil_x))
                target.mouth_curve = max(-1.0, min(1.0, target.mouth_curve))
                target.mouth_open = min(1.2, target.mouth_open)
                target.tear = min(1.0, target.tear)
        self._to = target
        b = expressions.beat(name)
        if duration is not None:
            b = expressions.Beat(max(0.02, duration), b.anticipate, b.overshoot, b.hold_snap)
        self._beat = b
        self._t0 = time.monotonic()

    # -- speech ------------------------------------------------------------

    def speak(self, text: str) -> float:
        """Say something. Returns how long it will take.

        The rhythm is fixed here from the expression in force at the start, but
        the DELIVERY is read fresh every frame - so if the mood changes
        mid-sentence, the same words finish being spoken differently.
        """
        style = expressions.talk(self.base)
        # A new utterance never cuts the old one off in a frame: the old one
        # fades while the new one starts (it opens on a closed mouth anyway).
        self.hush()
        self._utt = VisemeTrack(text, style.rate, style.crisp)
        self._utt_t0 = time.monotonic()
        return self._utt.duration

    def hush(self, fade: float = SPEECH_FADE) -> None:
        """Stop talking - over `fade` seconds, so the mouth closes rather than
        vanishing. Used when the user starts talking over him."""
        if self._utt is not None and fade > 0:
            self._fading.append((self._utt, self._utt_t0, time.monotonic()))
        self._utt = None
        if fade <= 0:
            self._fading.clear()

    @property
    def speaking(self) -> bool:
        return self._utt is not None

    # -- touch -------------------------------------------------------------

    def touch_down(self, x: float, y: float) -> str:
        now = time.monotonic()
        region = self.region_at(x, y)
        self._press_at = (x, y)
        self._press_t0 = now
        self._drag = 0.0
        self.last_touch = region

        if self.base == "asleep":
            self._pokes.clear()
            self.flash("startled", hold=0.7)
            self.set("waking")
            return "wake"

        self._pokes = [t for t in self._pokes if now - t < 2.4]
        self._pokes.append(now)

        if len(self._pokes) >= 5:
            self._pokes.clear()
            self.flash("dizzy", hold=1.6)
            return "dizzy"
        if len(self._pokes) == 4:
            self.flash("angry", hold=1.0)
            return "annoyed"

        reaction = {
            "left_eye": "squint", "right_eye": "wink", "mouth": "surprised",
            "forehead": "confusion", "cheek_left": "shy",
            "cheek_right": "shy", "panel": "curious",
        }[region]
        self.flash(reaction, hold=0.9)
        self.look_at(x, y, hold=1.8)
        return reaction

    def touch_move(self, x: float, y: float) -> None:
        if self._press_at is None:
            return
        dx, dy = x - self._press_at[0], y - self._press_at[1]
        self._drag += math.hypot(dx, dy)
        self._press_at = (x, y)
        self.look_at(x, y, hold=0.9)
        if self._drag > self.r.w * 0.22:
            self.flash("love", hold=1.4)
            self._drag = 0.0

    def touch_up(self, x: float, y: float) -> None:
        if self._press_at is not None:
            held = time.monotonic() - self._press_t0
            if held > 0.9 and self._drag < 20:
                self.flash("shy", hold=1.3)
        self._press_at = None
        self._drag = 0.0

    # -- the frame ---------------------------------------------------------

    def update(self) -> FaceParams:
        now = time.monotonic()

        dt = max(0.0, min(0.1, now - self._last_now))
        self._last_now = now

        if self._overlay and now >= self._overlay_until:
            self._overlay = None
            # The duration asked for while the overlay was up is honoured
            # now, instead of being silently dropped.
            self._begin(self.base, self._base_dur)

        if self._seq and now >= self._seq_next:
            name, hold, amt = self._seq.pop(0)
            self._seq_next = now + hold
            self.set(name, intensity=amt)

        # 1 + 2: the beat, staggered across channels.
        b = self._beat
        e = now - self._t0
        def chan(lag: float) -> float:
            return _act_curve((e - b.dur * lag) / b.dur,
                              b.anticipate, b.overshoot, b.hold_snap)
        self.current = blend_channels(
            self._from, self._to,
            chan(LAG_SHAPE), chan(LAG_PUPIL), chan(LAG_MOUTH), chan(LAG_GLOBAL))
        p = self.current.copy()

        # The breathing/blinking settings drift toward the new pose's own.
        k = _ease(dt, IDLE_TAU)
        tgt = expressions.idle(self.base)
        for f in _IDLE_FIELDS:
            self._idle_s[f] += (getattr(tgt, f) - self._idle_s[f]) * k
        idle = expressions.Idle(**self._idle_s)
        # Phase is integrated, not now*rate: with a monotonic clock in the
        # thousands, changing the rate by a hair would jump the phase.
        self._breath_phase += dt * idle.breath_rate
        self._sleep_w += ((1.0 if self.base == "asleep" else 0.0) - self._sleep_w) * k
        breath = math.sin(self._breath_phase)

        # 3: idle life.
        if (not self._blinking and now >= self._next_blink
                and self.base != "asleep" and idle.blink_rate > 0.01):
            self._blinking = True
            self._blink_start = now
        if self._blinking:
            el = now - self._blink_start
            if el >= BLINK_CLOSE + BLINK_OPEN:
                self._blinking = False
                gap = random.uniform(BLINK_MIN, BLINK_MAX) / max(0.05, idle.blink_rate)
                self._next_blink = now + gap
            else:
                amt = (el / BLINK_CLOSE) if el < BLINK_CLOSE else \
                      (1.0 - (el - BLINK_CLOSE) / BLINK_OPEN)
                amt = max(0.0, min(1.0, amt))
                for eye in (p.left, p.right):
                    eye.upper_lid = max(eye.upper_lid, amt * 0.97)
                    eye.pupil_alpha *= (1.0 - amt * 0.9)

        if self._look_at and now < self._look_until:
            gx, gy = self._look_at
        else:
            self._look_at = None
            if now >= self._next_gaze:
                self._gaze_from = self._gaze
                m = idle.gaze_mag
                self._gaze = (random.uniform(-m, m), random.uniform(-m * 0.6, m * 0.6))
                self._gaze_t0 = now
                rate = max(0.05, idle.gaze_rate)
                self._next_gaze = now + random.uniform(GAZE_MIN, GAZE_MAX) / rate
            # Under 80ms, then dead still. Easing it makes the eye swim.
            st = min(1.0, (now - self._gaze_t0) / 0.07)
            gx = self._gaze_from[0] + (self._gaze[0] - self._gaze_from[0]) * st
            gy = self._gaze_from[1] + (self._gaze[1] - self._gaze_from[1]) * st

        if self.base != "asleep":
            for eye in (p.left, p.right):
                eye.pupil_x += gx
                eye.pupil_y += gy

        p.glow *= 1.0 + idle.breath_depth * breath
        sw = self._sleep_w
        p.shift_y += 2.2 * sw * breath
        p.shift_x += (1.0 - sw) * 1.3 * idle.drift * math.sin(now * 0.37)
        p.shift_y += (1.0 - sw) * 1.0 * idle.drift * math.sin(now * 0.29 + 1.2)

        # A tear is the only part of this face with its own clock. It wells up,
        # hangs, falls, and is gone - then the next one starts. A tear frozen
        # at one size is a sticker; the cycle is what makes it a tear.
        if p.tear > 0.01:
            TEAR_CYCLE = 4.6
            u = (now % TEAR_CYCLE) / TEAR_CYCLE
            if u < 0.42:                      # welling up at the lid
                p.tear *= u / 0.42
                p.tear_fall = 0.0
            elif u < 0.56:                    # hanging, full size
                p.tear_fall = 0.0
            else:                             # falling, accelerating
                f = (u - 0.56) / 0.44
                p.tear_fall = f * f
                p.tear *= max(0.0, 1.0 - f * 0.55)

        # 3b: modifiers. These are adjectives - they compose with whatever
        # pose is showing instead of replacing it.
        if self._lean:
            p.scale *= 1.0 + 0.09 * self._lean
            p.shift_y += -3.0 * self._lean
            p.glow *= 1.0 + 0.07 * self._lean
        if self._strain:
            p.left.x += 0.18 * self._strain
            p.right.x -= 0.18 * self._strain
            p.left.pupil_x += 0.30 * self._strain
            p.right.pupil_x -= 0.30 * self._strain
        if self._fatigue:
            f = self._fatigue
            for eye in (p.left, p.right):
                eye.upper_lid = max(eye.upper_lid, 0.52 * f)
                eye.lower_angle += 3.0 * f      # the lower lid sags unevenly
                eye.pupil_y += 0.12 * f
            p.glow *= 1.0 - 0.30 * f
            p.shift_y += 2.0 * f

        # 4: speech, spent across the whole face. The delivery settings follow
        # the mood over a quarter second rather than snapping to it.
        kt = _ease(dt, TALK_TAU)
        ttgt = expressions.talk(self.base)
        for f in _TALK_FIELDS:
            self._talk_s[f] += (getattr(ttgt, f) - self._talk_s[f]) * kt
        t = expressions.Talk(**self._talk_s)

        voices: list[tuple[VisemeTrack, float, float]] = []
        if self._utt is not None:
            st = now - self._utt_t0
            if self._utt.done(st):
                self._utt = None
            else:
                voices.append((self._utt, st, 1.0))
        keep = []
        for trk, t0, fs in self._fading:
            g = 1.0 - (now - fs) / SPEECH_FADE
            if g > 0.0 and not trk.done(now - t0):
                keep.append((trk, t0, fs))
                voices.append((trk, now - t0, g))
        self._fading = keep

        # A mouthless pose that speaks grows a mouth for as long as it speaks.
        # The pose itself is untouched - at rest it is still mouthless - but
        # a voice with no mouth moving is the one thing a viewer will not
        # accept.
        show = 1.0 if voices else 0.0
        tau = MOUTH_SHOW_TAU if show > self._mouth_show else MOUTH_HIDE_TAU
        self._mouth_show += (show - self._mouth_show) * _ease(dt, tau)
        if self._mouth_show > 0.002:
            p.mouth_alpha = max(p.mouth_alpha, self._mouth_show)

        scale = t.open_max / 0.60
        for trk, st, g in voices:
            v_open, v_width = trk.mouth(st)
            amp = trk.energy(st) * g
            acc = trk.accent(st) * g
            sway = trk.breath(st) * g

            # The viseme says WHAT shape; the expression says how big and
            # how wide that shape gets made. Both, not one or the other -
            # apologetic and delight say the same word with the same
            # mouth shapes, at very different sizes.
            p.mouth_open = max(p.mouth_open, min(1.1, v_open * scale) * g)
            p.mouth_w *= 1.0 + (v_width * (1.0 + (t.width - 1.0) * amp) - 1.0) * g
            # The head rises with the voice (or sinks, if the expression
            # talks downward) and the tilt sways across the phrase.
            p.shift_y -= t.bob * (0.65 * amp + 0.35 * acc)
            p.tilt += t.sway * sway
            p.glow *= 1.0 + t.glow_pulse * amp
            for eye in (p.left, p.right):
                eye.h *= 1.0 - t.squint * amp
                eye.pupil_y += 0.07 * t.accent * acc
                eye.upper_lid = max(eye.upper_lid, 0.10 * t.accent * acc)

        return sanitise(p)
