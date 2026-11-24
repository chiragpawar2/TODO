"""The expression library.

Two rules govern every pose here, both taken from the research:

1. REDUNDANT ENCODING. Eye silhouette, pupil direction and mouth all change
   together in every state. Kalegina et al. (HRI 2018) found that stripping the
   mouth and pupils from a robot face makes people call it "soulless" and guess
   it is for surveillance; a 305-participant study found full faces recognised
   at 64.4% against 51.3% for eyes-only. No study places Indian viewers on the
   eyes-vs-mouth axis either way, so we encode the feeling twice and stop
   worrying about which channel the viewer reads.

2. NO TWO STATES SHARE A PHYSICAL SOLUTION. If two feelings resolve to the same
   shape, one of them is not being acted. A fixed eye shape across every feeling
   reads as a mask, not a face.

Note `angry` and `sad` below: the lid coverage is nearly identical and only the
SIGN of upper_angle differs. That is not a shortcut, it is how the distinction
actually works on a face.
"""

from __future__ import annotations

from .params import EyeParams, FaceParams


def _face(both: dict | None = None, left: dict | None = None,
          right: dict | None = None, **globals_) -> FaceParams:
    both = both or {}
    return FaceParams(
        left=EyeParams(**{**both, **(left or {})}),
        right=EyeParams(**{**both, **(right or {})}),
        **globals_,
    )


EXPRESSIONS: dict[str, FaceParams] = {

    # ---- the nine states that map to Brain.ask() -------------------------

    "rest": _face(
        {"h": 1.0, "w": 1.0},
        glow=1.0, mouth_curve=0.20, mouth_w=1.0),

    "listening": _face(
        {"h": 1.16, "w": 1.06, "radius": 0.45},
        glow=1.22, mouth_curve=0.34, mouth_w=1.1),

    "thinking": _face(
        {"h": 0.88, "w": 1.0, "lower_lid": 0.20, "lower_bend": 0.1,
         "pupil_x": -0.52, "pupil_y": -0.55},
        glow=0.85, mouth_curve=0.03, mouth_w=0.8, mouth_x=-0.22, tilt=-2.5),

    # The flattest of the nine. Horizontal slots are unambiguous at any size,
    # which is why this state reads best on a small panel.
    "searching": _face(
        {"h": 0.42, "w": 1.18, "radius": 0.5, "pupil_x": 0.85, "pupil_scale": 0.9},
        glow=0.98, mouth_curve=0.0, mouth_w=0.4),

    "answering": _face(
        {"h": 1.02, "w": 1.0},
        glow=1.12, mouth_curve=0.48, mouth_w=1.18),

    "delight": _face(
        {"h": 1.22, "lower_lid": 0.46, "lower_bend": 0.46, "pupil_alpha": 0.0},
        glow=1.38, mouth_curve=0.92, mouth_w=1.3, mouth_thick=1.15),

    # The ONLY asymmetric state in the core nine. The disagreement between the
    # eyes is itself the signal, so nothing else may borrow it.
    "confusion": _face(
        left={"h": 1.22, "w": 1.05, "radius": 0.5, "pupil_x": 0.42},
        right={"h": 0.70, "w": 0.95, "pupil_x": 0.42, "upper_lid": 0.12},
        glow=1.0, tilt=6.0, mouth_curve=-0.16, mouth_x=0.2, mouth_w=0.75),

    # Must read sorry, not angry. The upper lid slopes DOWN outer-to-inner
    # (negative angle) and the pupils drop. Flip that sign and you get a glare.
    "apologetic": _face(
        {"h": 0.92, "upper_lid": 0.46, "upper_angle": -14.0, "pupil_y": 0.48},
        glow=0.70, mouth_curve=-0.30, mouth_y=0.03, mouth_w=0.82),

    "asleep": _face(
        {"h": 0.20, "w": 0.98, "radius": 0.5, "pupil_alpha": 0.0, "upper_bend": 0.3},
        glow=0.34, mouth_curve=0.06, mouth_w=0.42, mouth_thick=0.85),

    # ---- the wider emotional range ---------------------------------------

    "happy": _face(
        {"h": 1.08, "lower_lid": 0.40, "lower_bend": 0.40, "pupil_alpha": 0.0},
        glow=1.22, mouth_curve=0.78, mouth_w=1.2),

    "sad": _face(
        {"h": 0.95, "upper_lid": 0.32, "upper_angle": -11.0, "pupil_y": 0.36},
        glow=0.62, mouth_curve=-0.58, mouth_w=0.85, mouth_y=0.04),

    # Same lid coverage as "sad". Only the sign of upper_angle differs.
    "angry": _face(
        {"h": 0.82, "upper_lid": 0.40, "upper_angle": 19.0, "pupil_scale": 0.9},
        glow=1.16, mouth_curve=-0.38, mouth_w=0.78, aberration=3.0),

    "surprised": _face(
        {"h": 1.34, "w": 1.12, "radius": 0.5, "pupil_scale": 0.66},
        glow=1.30, mouth_open=0.85, mouth_w=1.00, mouth_curve=0.06),

    "startled": _face(
        {"h": 1.44, "w": 1.16, "radius": 0.5, "pupil_scale": 0.5},
        glow=1.42, shift_y=-5.0, mouth_open=1.0, mouth_w=0.96, aberration=3.5),

    "love": _face(
        {"h": 1.08, "pupil_scale": 1.12, "lower_lid": 0.12, "lower_bend": 0.12},
        glow=1.28, tilt=3.0, mouth_curve=0.82, mouth_w=1.1),

    "wink": _face(
        left={"h": 1.0},
        right={"h": 1.1, "upper_lid": 0.87, "upper_bend": -0.20, "pupil_alpha": 0.0},
        glow=1.18, mouth_curve=0.62, mouth_x=0.16, mouth_w=1.0),

    "skeptical": _face(
        left={"h": 1.05, "upper_lid": 0.14, "pupil_x": 0.34},
        right={"h": 0.86, "upper_lid": 0.50, "upper_angle": 11.0, "pupil_x": 0.34},
        glow=1.0, tilt=-2.0, mouth_curve=-0.12, mouth_x=0.2, mouth_w=0.7),

    "bored": _face(
        {"h": 0.95, "upper_lid": 0.44, "pupil_x": -0.52, "pupil_y": 0.22, "pupil_scale": 0.9},
        glow=0.68, mouth_curve=-0.08, mouth_w=0.66),

    "dizzy": _face(
        left={"h": 1.12, "pupil_x": 0.58, "pupil_y": -0.42, "pupil_scale": 0.8},
        right={"h": 1.12, "pupil_x": -0.55, "pupil_y": 0.45, "pupil_scale": 0.8},
        glow=1.1, tilt=8.0, mouth_curve=-0.1, mouth_open=0.4, mouth_w=0.6,
        aberration=4.0),

    "curious": _face(
        left={"h": 1.20, "pupil_y": -0.2},
        right={"h": 0.94, "pupil_y": -0.2},
        glow=1.1, tilt=-5.0, mouth_curve=0.26, mouth_w=0.78),

    "proud": _face(
        {"h": 0.86, "upper_lid": 0.18, "upper_angle": 6.0, "pupil_y": -0.16},
        glow=1.16, mouth_curve=0.52, mouth_w=1.05),

    "worried": _face(
        {"h": 0.98, "upper_lid": 0.22, "upper_angle": -17.0,
         "pupil_y": 0.2, "pupil_x": 0.2},
        glow=0.80, mouth_curve=-0.42, mouth_w=0.68, mouth_x=-0.1),

    "mischief": _face(
        {"h": 0.74, "upper_lid": 0.38, "upper_angle": 13.0, "pupil_x": 0.46},
        glow=1.14, mouth_curve=0.60, mouth_x=0.2, mouth_w=0.9),

    "shy": _face(
        {"h": 0.90, "upper_lid": 0.50, "upper_angle": -8.0,
         "pupil_x": -0.46, "pupil_y": 0.3},
        glow=0.86, tilt=-4.0, mouth_curve=0.30, mouth_w=0.58),

    "squint": _face(
        {"h": 0.46, "w": 0.95, "pupil_scale": 0.85},
        glow=1.05, mouth_curve=0.12, mouth_w=0.66),

    "focused": _face(
        {"h": 0.78, "w": 0.90, "pupil_scale": 0.78},
        glow=1.12, mouth_curve=0.06, mouth_w=0.58),

    "yawn": _face(
        {"h": 0.86, "upper_lid": 0.68, "upper_bend": 0.2, "pupil_y": 0.3},
        glow=0.58, mouth_open=1.0, mouth_w=0.72, mouth_y=0.04),

    "waking": _face(
        {"h": 0.74, "upper_lid": 0.70, "upper_bend": 0.25, "pupil_y": 0.12},
        glow=0.56, mouth_curve=0.10, mouth_w=0.5),

    "glitch": _face(
        left={"h": 0.58, "w": 1.22},
        right={"h": 1.22, "w": 0.86},
        glow=1.2, tilt=-3.0, aberration=6.0, mouth_curve=-0.05, mouth_w=0.9),

    # ---- studied from the reference expression sheet ----------------------
    #
    # That sheet solves faces with devices ours had not used. Four of them:
    #
    #   1. THE MOUTH IS ALLOWED TO VANISH. Its suspicious face has no mouth at
    #      all. Deleting a feature is a stronger statement than bending it.
    #   2. THE MOUTH IS A SOLID, NOT A LINE. Its laugh is a wide filled slab
    #      and its gasp a tall filled dome - the same hole read two ways by
    #      proportion alone.
    #   3. THE EYE MAY STOP BEING AN EYE. Anger is two straight bars; worry is
    #      two chevrons. No pupil, no socket - pure silhouette, which is what
    #      survives being small.
    #   4. GRIEF NEEDS A PROP. No lid arrangement says crying. A tear does.
    #
    # Rule 2 at the top of this file still binds: none of these repeats a
    # solution already in use above.

    # Device 2, wide. Open and FLAT - the width is the laugh; a tall opening
    # here would read as a shout instead.
    "grin": _face(
        {"h": 1.00, "lower_lid": 0.52, "lower_bend": 0.50, "pupil_alpha": 0.0},
        glow=1.34, mouth_open=0.74, mouth_w=1.52, mouth_curve=0.30,
        mouth_thick=1.1),

    # Device 2, tall. Same hole as "grin", a third of the width. Distinct from
    # "surprised", whose eyes blow open; here the eyes barely move, so the
    # mouth carries it alone.
    "oh": _face(
        {"h": 1.06, "w": 1.0, "pupil_scale": 0.86},
        glow=1.16, mouth_open=1.15, mouth_w=0.48, mouth_curve=-0.60,
        mouth_thick=1.15),

    # Device 3, dome. Dread, not shock: the eyes SHRINK and the pupils pull to
    # pinpricks while the mouth opens. Shock opens everything at once.
    "dread": _face(
        {"h": 0.80, "w": 0.94, "pupil_scale": 0.42, "pupil_y": 0.20},
        glow=0.92, mouth_open=1.15, mouth_w=0.60, mouth_curve=-0.50,
        mouth_y=0.02, mouth_thick=1.15, aberration=2.4),

    # Device 1. No mouth at all, and the eyes are near-shut slits aimed
    # sideways. "skeptical" is asymmetric and keeps its mouth; this is the
    # flat, symmetrical, wordless stare.
    "suspicious": _face(
        {"h": 0.34, "w": 1.14, "radius": 0.16, "pupil_x": 0.80,
         "pupil_scale": 1.45},
        glow=1.04, mouth_alpha=0.0, mouth_w=0.5, mouth_curve=0.0),

    # Device 3, bars. Anger as pure geometry: no roundness left to soften it.
    # The inner ends drop, which is the whole message. Our existing "angry"
    # keeps a round eye under an angled lid - a hotter, more reactive feeling.
    # This one is colder.
    "stern": _face(
        left={"h": 0.26, "w": 1.12, "radius": 0.10, "angle": 10.0,
              "pupil_alpha": 0.0},
        right={"h": 0.26, "w": 1.12, "radius": 0.10, "angle": -10.0,
               "pupil_alpha": 0.0},
        glow=1.10, mouth_curve=0.0, mouth_w=0.86, mouth_thick=1.15),

    # Device 3, chevrons. The lid bows UP through the middle (negative bend),
    # leaving a thin arc that peaks in the centre - the brow-pinch of worry
    # drawn as the eye itself. "worried" does this with lid ANGLE on a round
    # eye; this is the silhouette version, which survives a smaller panel.
    "fret": _face(
        left={"h": 0.98, "w": 1.08, "lower_lid": 0.50, "lower_bend": 0.48,
              "angle": -12.0, "pupil_alpha": 0.0},
        right={"h": 0.98, "w": 1.08, "lower_lid": 0.50, "lower_bend": 0.48,
               "angle": 12.0, "pupil_alpha": 0.0},
        glow=0.86, mouth_curve=-0.46, mouth_w=0.62, mouth_y=0.03),

    # Closed, arcing UP. Not "blink" (a shutter, gone in 90ms) and not
    # "delight" (which keeps the top of the eye). Eyes-shut contentment is a
    # held pose - the face of someone not looking because they do not need to.
    "content": _face(
        {"h": 1.06, "w": 1.06, "lower_lid": 0.56, "lower_bend": 0.54,
         "pupil_alpha": 0.0},
        glow=1.08, mouth_curve=0.64, mouth_w=0.92),

    # Device 4. "sad" plus the one thing sadness cannot be acted into.
    "crying": _face(
        {"h": 0.94, "upper_lid": 0.28, "upper_angle": -13.0, "pupil_y": 0.24,
         "pupil_scale": 0.88},
        glow=0.56, mouth_curve=-0.66, mouth_w=0.80, mouth_y=0.05,
        tear=1.0, tear_fall=0.0),

    # ---- studied from the Jibo-family reference ---------------------------
    #
    # A second reference sheet, and it works a different way from the first.
    # That family has NO MOUTH AT ALL - not as one pose, as the whole design -
    # and carries everything on two devices:
    #
    #   5. THE HALF-DISC. One flat edge, one curved. It is not a crescent
    #      (which is curved on both edges) and not a bar (flat on both). The
    #      flat edge is what makes it read as a lid rather than a shape.
    #   6. TILT IS THE SENTENCE. With the mouth gone, the ANGLE of the pair
    #      does the work the mouth used to do. Angled inward reads tender;
    #      angled outward reads alarmed; the same two shapes, opposite feeling.
    #
    # A flat lid edge means bend = 0. Every crescent we already own bends.

    # Half-discs angled inward, no mouth. The warmest pose in the set and the
    # only one that gets there without a smile.
    "tender": _face(
        left={"h": 1.10, "w": 1.08, "lower_lid": 0.44, "lower_bend": 0.0,
              "angle": -14.0, "pupil_alpha": 0.0},
        right={"h": 1.10, "w": 1.08, "lower_lid": 0.44, "lower_bend": 0.0,
               "angle": 14.0, "pupil_alpha": 0.0},
        glow=1.18, tilt=2.0, mouth_alpha=0.0),

    # The same two half-discs tilted the OTHER way. Nothing else changes and
    # the feeling inverts - which is the point of device 6.
    "alarmed": _face(
        left={"h": 1.10, "w": 1.08, "lower_lid": 0.44, "lower_bend": 0.0,
              "angle": 15.0, "pupil_alpha": 0.0},
        right={"h": 1.10, "w": 1.08, "lower_lid": 0.44, "lower_bend": 0.0,
               "angle": -15.0, "pupil_alpha": 0.0},
        glow=1.26, shift_y=-3.0, mouth_alpha=0.0, aberration=2.8),

    # One eye half-shut, one wide, head cocked, no mouth. The reference's most
    # characteristic pose. "confusion" is the two eyes DISAGREEING in size;
    # this is one eye lidded while both still look straight at you, which is
    # interest rather than puzzlement.
    "peek": _face(
        left={"h": 1.16, "w": 1.06, "radius": 0.5},
        right={"h": 1.16, "w": 1.06, "lower_lid": 0.50, "lower_bend": 0.0,
               "pupil_alpha": 0.0},
        glow=1.14, tilt=-7.0, mouth_alpha=0.0),

    # Mouthless and perfectly level: the resting attention of a device that is
    # listening and not yet saying anything. Pupils slightly small so it reads
    # as looking AT you rather than staring through you.
    "attentive": _face(
        {"h": 1.20, "w": 1.10, "radius": 0.5, "pupil_scale": 0.80},
        glow=1.10, mouth_alpha=0.0),

    # Flat lid dropped most of the way, heavy tilt. Distinct from "asleep"
    # (which is nearly shut and level) and from "bored" (which has a mouth and
    # looks away) - this one is still watching, just barely.
    "drowsy": _face(
        {"h": 1.12, "w": 1.04, "upper_lid": 0.50, "upper_bend": 0.0,
         "pupil_y": 0.42, "pupil_scale": 0.52},
        glow=0.66, tilt=5.0, mouth_alpha=0.0),

    # Used by the idle layer, never selected directly.
    "blink": _face(
        {"h": 1.0, "upper_lid": 0.97, "upper_bend": 0.12, "pupil_alpha": 0.0},
        glow=1.0, mouth_curve=0.20),
}


#: Which expression each state of Brain.ask() maps to. The nine are not a mood
#: board - they are real branches in homebot/brain.py.
BRAIN_STATES = {
    "idle": "rest",
    "heard": "listening",
    "thinking": "thinking",     # engine.complete() in flight
    "tool": "searching",        # dispatch(tool) running
    "speaking": "answering",    # reply being returned
    "success": "delight",       # tool succeeded
    "unknown_speaker": "confusion",
    "refused": "apologetic",    # result.refused
    "stuck": "confusion",       # MAX_TOOL_ROUNDS exhausted
    "sleep": "asleep",          # long idle
}


def get(name: str) -> FaceParams:
    return EXPRESSIONS.get(name, EXPRESSIONS["rest"]).copy()


def names() -> list[str]:
    return list(EXPRESSIONS)


# ---------------------------------------------------------------------------
# ACTING METADATA
#
# A pose is only half an expression. The Animator's Survival Kit is blunt about
# this: "identical endpoints can feel heavy, light, cautious, explosive, smooth,
# mechanical, comic, or alive depending on their in-betweens", and "do not make
# every acceleration mathematically even."
#
# So each expression also owns HOW it arrives, how it idles once it is there,
# and how it talks. One shared easing curve for all 30 states - which is what
# this had before - is the mistake that rule names.
# ---------------------------------------------------------------------------

from dataclasses import dataclass


@dataclass
class Beat:
    """How an expression arrives.

    dur        total transition time
    anticipate how far it pulls the OPPOSITE way first, as a fraction of the
               move. Preparation before an outward action.
    overshoot  how far past the target it travels before settling back.
    hold_snap  0 settles softly, 1 snaps to the target (hard hold)
    """
    dur: float = 0.42
    anticipate: float = 0.0
    overshoot: float = 0.0
    hold_snap: float = 0.0


@dataclass
class Idle:
    """The living changes inside a held pose.

    "A hold is a performance decision, not a frozen drawing... retain tiny
    living changes." An excited face must not breathe at the same rate as a
    sad one, or the hold is the same hold wearing a different mask.
    """
    breath_rate: float = 2.1
    breath_depth: float = 0.045
    drift: float = 1.0        # how much the whole face wanders
    gaze_mag: float = 0.22    # saccade size
    gaze_rate: float = 1.0    # >1 looks around more often
    blink_rate: float = 1.0   # >1 blinks more often


@dataclass
class Talk:
    """How this expression talks.

    Never a mouth bolted onto a frozen face: "Dialogue and facial action
    require a thought change, not mouth-shape substitution. Face, head, spine,
    weight and appendages should share the same impulse."

    So every field here drives something other than the mouth as well.
    """
    open_max: float = 0.62    # widest the mouth goes
    width: float = 1.0        # mouth width multiplier while speaking
    bob: float = 3.0          # head rise on each stressed syllable, px
    sway: float = 0.9         # slow tilt sway across a phrase, degrees
    glow_pulse: float = 0.10  # brightness lifts with the voice
    squint: float = 0.05      # eyes tighten slightly on loud syllables
    rate: float = 5.2         # syllables per second
    crisp: float = 0.5        # 0 drawls, 1 clips each syllable short
    accent: float = 0.5       # pupil / lid kick on a stressed syllable


_B = Beat
BEATS: dict[str, Beat] = {
    # A shock has no time to prepare - that is what makes it a shock. It gets
    # no anticipation and a large overshoot instead.
    "startled":   _B(0.10, 0.00, 0.38, 0.0),
    "surprised":  _B(0.14, 0.00, 0.26, 0.0),
    "glitch":     _B(0.06, 0.00, 0.30, 1.0),

    # An outward, energetic action loads first, then releases past the target.
    "delight":    _B(0.30, 0.14, 0.20),
    "happy":      _B(0.34, 0.10, 0.14),
    "love":       _B(0.44, 0.12, 0.16),
    "proud":      _B(0.40, 0.14, 0.10),
    "answering":  _B(0.34, 0.07, 0.10),
    "listening":  _B(0.26, 0.06, 0.12),

    # Aggression pulls back before it strikes. Short and hard.
    "angry":      _B(0.16, 0.18, 0.10, 0.6),
    "mischief":   _B(0.26, 0.12, 0.12),
    "dizzy":      _B(0.30, 0.00, 0.22),

    # Sinking has no bounce in it. Anything that springs here reads as fake.
    "apologetic": _B(0.70, 0.00, 0.00),
    "sad":        _B(0.80, 0.00, 0.00),
    "worried":    _B(0.55, 0.00, 0.03),
    "shy":        _B(0.50, 0.00, 0.04),
    "bored":      _B(0.75, 0.00, 0.00),
    "yawn":       _B(0.85, 0.08, 0.00),
    "asleep":     _B(1.70, 0.00, 0.00),
    "waking":     _B(1.10, 0.00, 0.05),

    # Thought takes time; the face arrives at it rather than cutting to it.
    "thinking":   _B(0.55, 0.05, 0.04),
    "confusion":  _B(0.46, 0.09, 0.12),
    "skeptical":  _B(0.40, 0.08, 0.08),
    "curious":    _B(0.36, 0.08, 0.14),
    "searching":  _B(0.28, 0.04, 0.08),
    "focused":    _B(0.30, 0.06, 0.05),
    "squint":     _B(0.22, 0.04, 0.06),
    "rest":       _B(0.46, 0.03, 0.05),
    "wink":       _B(0.16, 0.00, 0.14),
    # From the reference sheet.
    "grin":       _B(0.22, 0.16, 0.26),      # loads hard, bursts
    "oh":         _B(0.17, 0.00, 0.22),      # the mouth gets there first
    "dread":      _B(0.46, 0.00, 0.00, 0.7), # arrives and locks; no bounce
    "suspicious": _B(0.34, 0.06, 0.00, 0.9), # the slits SNAP shut and hold
    "stern":      _B(0.20, 0.12, 0.04, 0.8), # a decision, not an outburst
    "fret":       _B(0.52, 0.00, 0.04),
    "content":    _B(0.62, 0.05, 0.06),      # the slowest happy pose we own
    "crying":     _B(0.95, 0.00, 0.00),      # slower even than "sad"
    # From the Jibo-family reference. With no mouth, the arrival IS the
    # performance - there is nothing else on the face to carry it.
    "tender":     _B(0.66, 0.08, 0.10),
    "alarmed":    _B(0.12, 0.00, 0.34, 0.0),
    "peek":       _B(0.34, 0.10, 0.16),
    "attentive":  _B(0.30, 0.05, 0.08),
    "drowsy":     _B(0.90, 0.00, 0.00),
    "blink":      _B(0.09, 0.00, 0.00, 1.0),
}

_I = Idle
IDLES: dict[str, Idle] = {
    "rest":       _I(2.1, 0.045, 1.00, 0.30, 1.0, 1.0),
    "listening":  _I(2.9, 0.060, 0.70, 0.16, 1.5, 1.3),
    "thinking":   _I(1.5, 0.055, 1.30, 0.34, 2.1, 0.6),
    "searching":  _I(3.4, 0.040, 0.50, 0.40, 2.6, 0.5),
    "answering":  _I(2.6, 0.050, 0.90, 0.18, 1.2, 1.0),
    "delight":    _I(3.6, 0.085, 1.60, 0.14, 1.4, 1.4),
    "confusion":  _I(1.9, 0.055, 1.20, 0.26, 1.8, 1.1),
    "apologetic": _I(1.2, 0.030, 0.55, 0.10, 0.5, 0.7),
    "asleep":     _I(0.9, 0.300, 0.00, 0.00, 0.0, 0.0),
    "happy":      _I(3.1, 0.070, 1.40, 0.18, 1.3, 1.3),
    "sad":        _I(1.0, 0.028, 0.45, 0.09, 0.4, 0.6),
    # Anger stares. Rare blinks are most of what makes a stare a stare.
    "angry":      _I(3.3, 0.035, 0.75, 0.07, 0.4, 0.2),
    "surprised":  _I(3.0, 0.030, 0.40, 0.06, 0.5, 0.3),
    "startled":   _I(3.8, 0.030, 0.35, 0.05, 0.4, 0.2),
    "love":       _I(2.4, 0.080, 1.30, 0.12, 0.9, 1.2),
    "wink":       _I(2.6, 0.055, 1.00, 0.16, 1.0, 0.8),
    "skeptical":  _I(1.7, 0.040, 0.70, 0.14, 0.8, 0.5),
    "bored":      _I(1.1, 0.035, 0.80, 0.40, 2.2, 0.8),
    "dizzy":      _I(2.8, 0.090, 2.20, 0.30, 2.4, 1.2),
    "curious":    _I(2.5, 0.060, 1.20, 0.30, 1.9, 1.2),
    "proud":      _I(2.0, 0.050, 0.60, 0.12, 0.7, 0.8),
    "worried":    _I(2.3, 0.045, 1.10, 0.28, 1.9, 1.4),
    "mischief":   _I(2.7, 0.060, 1.10, 0.22, 1.5, 0.9),
    "shy":        _I(2.2, 0.040, 0.90, 0.20, 1.4, 1.3),
    "squint":     _I(2.1, 0.040, 0.70, 0.16, 1.0, 0.7),
    "focused":    _I(1.8, 0.035, 0.45, 0.08, 0.5, 0.5),
    "yawn":       _I(0.8, 0.120, 0.70, 0.10, 0.4, 0.4),
    "waking":     _I(0.9, 0.090, 0.80, 0.16, 0.7, 1.5),
    "glitch":     _I(6.0, 0.110, 2.60, 0.50, 3.2, 0.3),
    # From the reference sheet.
    "grin":       _I(3.8, 0.095, 1.70, 0.12, 1.3, 1.4),
    "oh":         _I(3.2, 0.035, 0.45, 0.07, 0.5, 0.3),
    # Dread does not look around. Watching one thing is the fear.
    "dread":      _I(1.3, 0.025, 0.30, 0.04, 0.2, 0.3),
    # The stare that holds longest of all - fewer blinks even than "angry".
    "suspicious": _I(3.6, 0.030, 0.40, 0.09, 0.6, 0.15),
    "stern":      _I(3.5, 0.030, 0.50, 0.05, 0.3, 0.18),
    "fret":       _I(2.4, 0.050, 1.20, 0.26, 2.0, 1.3),
    # Slow, deep, almost asleep - but awake and choosing to be here.
    "content":    _I(1.5, 0.110, 0.80, 0.00, 0.0, 0.25),
    "crying":     _I(0.9, 0.055, 0.60, 0.07, 0.3, 1.6),
    "tender":     _I(1.8, 0.090, 0.90, 0.08, 0.5, 0.9),
    "alarmed":    _I(3.9, 0.030, 0.35, 0.05, 0.4, 0.2),
    "peek":       _I(2.6, 0.065, 1.10, 0.22, 1.6, 1.0),
    "attentive":  _I(2.8, 0.050, 0.60, 0.14, 1.1, 1.1),
    "drowsy":     _I(1.0, 0.130, 0.70, 0.10, 0.5, 0.5),
    "blink":      _I(),
}

_T = Talk
TALKS: dict[str, Talk] = {
    #                open  width  bob  sway  glow  squint rate crisp accent
    "rest":       _T(0.60, 1.00, 3.0, 0.9, 0.10, 0.05, 5.2, 0.50, 0.50),
    "listening":  _T(0.40, 0.95, 2.0, 0.5, 0.08, 0.03, 4.6, 0.55, 0.35),
    "answering":  _T(0.68, 1.12, 3.4, 1.0, 0.12, 0.06, 5.0, 0.50, 0.55),
    # Delight talks over itself: fast, wide, bouncing.
    "delight":    _T(0.86, 1.22, 6.0, 1.6, 0.20, 0.10, 6.4, 0.34, 0.85),
    "happy":      _T(0.76, 1.15, 5.0, 1.4, 0.16, 0.09, 6.0, 0.38, 0.75),
    "love":       _T(0.66, 1.08, 3.6, 1.8, 0.15, 0.07, 4.4, 0.60, 0.50),
    "proud":      _T(0.62, 1.05, 2.6, 0.6, 0.13, 0.05, 4.4, 0.66, 0.60),
    # Sorry talks small and quiet, and the head sinks instead of rising.
    "apologetic": _T(0.30, 0.80, -1.6, 0.5, 0.04, 0.02, 3.8, 0.72, 0.18),
    "sad":        _T(0.26, 0.78, -1.8, 0.4, 0.03, 0.02, 3.4, 0.76, 0.14),
    "shy":        _T(0.28, 0.70, -1.2, 1.1, 0.05, 0.04, 4.0, 0.68, 0.20),
    "worried":    _T(0.44, 0.80, 2.2, 1.3, 0.07, 0.08, 5.6, 0.44, 0.55),
    # Anger clips every syllable off short. That is the whole character of it.
    "angry":      _T(0.72, 0.82, 4.4, 0.4, 0.17, 0.14, 6.2, 0.90, 0.95),
    "skeptical":  _T(0.40, 0.76, 1.6, 0.8, 0.06, 0.07, 4.2, 0.70, 0.45),
    "mischief":   _T(0.52, 0.92, 3.0, 1.5, 0.12, 0.09, 5.8, 0.62, 0.70),
    "thinking":   _T(0.34, 0.82, 1.4, 1.1, 0.06, 0.04, 3.6, 0.46, 0.30),
    "searching":  _T(0.26, 0.60, 1.0, 0.6, 0.05, 0.02, 4.0, 0.60, 0.25),
    "confusion":  _T(0.46, 0.80, 2.0, 1.9, 0.07, 0.05, 4.2, 0.48, 0.45),
    "curious":    _T(0.52, 0.86, 2.8, 1.7, 0.10, 0.05, 5.0, 0.52, 0.55),
    "surprised":  _T(0.70, 1.05, 4.0, 0.7, 0.16, 0.04, 5.4, 0.40, 0.80),
    "startled":   _T(0.76, 1.05, 5.2, 0.9, 0.18, 0.04, 5.8, 0.36, 0.90),
    "dizzy":      _T(0.56, 0.84, 3.0, 2.6, 0.10, 0.06, 4.0, 0.42, 0.40),
    "bored":      _T(0.30, 0.74, 0.8, 0.5, 0.03, 0.03, 3.2, 0.80, 0.15),
    "focused":    _T(0.44, 0.74, 1.4, 0.3, 0.09, 0.07, 4.8, 0.78, 0.50),
    "squint":     _T(0.40, 0.72, 1.6, 0.6, 0.08, 0.06, 5.0, 0.68, 0.45),
    "wink":       _T(0.58, 1.02, 3.2, 1.2, 0.12, 0.06, 5.4, 0.52, 0.60),
    # A mumble, not speech. It should read as talking in its sleep.
    "asleep":     _T(0.16, 0.50, 0.6, 0.3, 0.02, 0.00, 1.8, 0.20, 0.05),
    "yawn":       _T(0.90, 0.80, 1.0, 0.6, 0.04, 0.00, 1.4, 0.10, 0.05),
    "waking":     _T(0.30, 0.62, 1.0, 0.7, 0.04, 0.02, 3.0, 0.40, 0.15),
    "glitch":     _T(0.60, 0.95, 5.0, 3.0, 0.22, 0.10, 9.0, 0.95, 1.00),

    # From the reference sheet.
    # Laughing speech: the widest mouth we own, and the head rides it.
    "grin":       _T(0.95, 1.40, 7.0, 1.8, 0.22, 0.12, 6.6, 0.30, 0.90),
    "oh":         _T(0.80, 0.68, 3.4, 0.8, 0.14, 0.03, 4.6, 0.40, 0.70),
    # Dread speaks in a near-whisper. Narrow, fast, almost no head movement.
    "dread":      _T(0.46, 0.66, 1.0, 0.4, 0.05, 0.10, 6.0, 0.74, 0.30),
    # It has no mouth. Speaking has to grow one, so it opens grudgingly and
    # stays tight - and the pupils do most of the talking.
    "suspicious": _T(0.34, 0.60, 1.2, 0.5, 0.06, 0.09, 4.4, 0.82, 0.75),
    # Clipped to the edge of curt. Every syllable lands and stops.
    "stern":      _T(0.52, 0.76, 2.0, 0.2, 0.09, 0.12, 5.0, 0.95, 0.85),
    "fret":       _T(0.44, 0.78, 2.2, 1.4, 0.06, 0.05, 5.6, 0.48, 0.45),
    # Unhurried. Nothing in this voice is in a rush.
    "content":    _T(0.48, 0.92, 1.8, 1.0, 0.08, 0.02, 3.6, 0.26, 0.30),
    # The voice breaks: slowest rate we have, and the biggest sway.
    "crying":     _T(0.42, 0.74, -2.2, 2.0, 0.05, 0.08, 3.2, 0.34, 0.55),

    # These five have no mouth. Speaking has to GROW one, so they all open
    # narrow, and the glow and the tilt carry more of the voice than usual.
    "tender":     _T(0.40, 0.84, 1.6, 1.3, 0.10, 0.03, 3.8, 0.30, 0.35),
    "alarmed":    _T(0.70, 0.92, 4.6, 0.7, 0.16, 0.06, 6.2, 0.40, 0.85),
    "peek":       _T(0.46, 0.88, 2.6, 1.1, 0.11, 0.05, 5.2, 0.46, 0.65),
    "attentive":  _T(0.44, 0.90, 2.2, 0.7, 0.10, 0.04, 5.0, 0.50, 0.45),
    "drowsy":     _T(0.26, 0.66, 0.8, 0.9, 0.03, 0.01, 2.8, 0.24, 0.12),
}

_DEF_BEAT, _DEF_IDLE, _DEF_TALK = Beat(), Idle(), Talk()


def beat(name: str) -> Beat:
    return BEATS.get(name, _DEF_BEAT)


def idle(name: str) -> Idle:
    return IDLES.get(name, _DEF_IDLE)


def talk(name: str) -> Talk:
    return TALKS.get(name, _DEF_TALK)


# ---------------------------------------------------------------------------
# SEQUENCES
#
# A pose is a word. These are sentences.
#
# No single pose can show a THOUGHT, because a thought is a change - it has a
# before and an after, and the join between them is the whole content. A
# double-take is not a pose; it is surprise that arrives LATE, and the lateness
# is the joke. The skill file is explicit about this: "Dialogue and facial
# action require a thought change", and a change needs two states to be a
# change between.
#
# Each step is (expression, how long to hold it, intensity). Intensity is what
# makes a slow burn a burn: the same pose three times, further each time.
# ---------------------------------------------------------------------------

SEQUENCES: dict[str, list[tuple[str, float, float]]] = {

    # The classic. Look away, THEN realise. The beat of normality in the
    # middle is what sells it - take it out and it is just a flinch.
    "double_take": [
        ("rest", 0.35, 1.0),
        ("searching", 0.30, 1.0),
        ("startled", 0.55, 1.2),
        ("curious", 0.70, 1.0),
    ],

    # Anger that arrives in three stages rather than one. Each step is the
    # SAME pose further along - which is the whole point of intensity.
    "slow_burn": [
        ("rest", 0.40, 1.0),
        ("skeptical", 0.70, 0.8),
        ("angry", 0.80, 0.5),
        ("stern", 1.20, 1.0),
        ("angry", 0.90, 1.3),
    ],

    # Not getting it, then getting it. The pause before "delight" is the
    # thought happening; cut it short and he looks like he was pretending.
    "realisation": [
        ("confusion", 0.70, 1.0),
        ("thinking", 0.90, 1.0),
        ("surprised", 0.30, 1.1),
        ("delight", 1.10, 1.2),
    ],

    # Trying not to laugh and losing. Needs the failed suppression in the
    # middle or it is just a laugh.
    "lose_it": [
        ("content", 0.45, 1.0),
        ("squint", 0.25, 1.2),
        ("mischief", 0.30, 1.0),
        ("grin", 1.00, 1.3),
        ("happy", 0.70, 1.0),
    ],

    # Falling asleep is not one move. It is three failed attempts to stay up.
    "nod_off": [
        ("drowsy", 0.90, 1.0),
        ("waking", 0.35, 0.7),
        ("drowsy", 0.80, 1.2),
        ("yawn", 0.80, 1.0),
        ("asleep", 2.00, 1.0),
    ],

    # Hearing your name from across the room.
    "perk_up": [
        ("drowsy", 0.30, 1.0),
        ("attentive", 0.35, 1.2),
        ("listening", 0.90, 1.0),
    ],

    # Being wrong about something, in public.
    "caught_out": [
        ("proud", 0.50, 1.0),
        ("startled", 0.25, 1.0),
        ("shy", 0.60, 1.0),
        ("apologetic", 1.00, 1.0),
    ],

    # Warming to someone. The tilt reverses halfway, which is the moment the
    # judgement turns into affection.
    "warm_up": [
        ("skeptical", 0.60, 1.0),
        ("curious", 0.55, 1.0),
        ("peek", 0.60, 1.0),
        ("tender", 1.30, 1.0),
    ],

    # Second thoughts. Ends somewhere other than it started, which is what
    # separates doubt from worry.
    "second_thought": [
        ("delight", 0.45, 1.0),
        ("rest", 0.30, 1.0),
        ("fret", 0.70, 0.8),
        ("worried", 0.90, 1.0),
    ],

    # The spit-take without the spit.
    "disbelief": [
        ("attentive", 0.40, 1.0),
        ("oh", 0.35, 1.2),
        ("suspicious", 0.80, 1.0),
        ("skeptical", 0.90, 1.0),
    ],
}


def sequence(name: str) -> list[tuple[str, float, float]]:
    return list(SEQUENCES.get(name, []))


def sequence_names() -> list[str]:
    return list(SEQUENCES)


# ---------------------------------------------------------------------------
# LEVELS
#
# Every expression exists at three strengths: a little, a normal amount, and
# a lot. "Intense happy", "medium happy" and "a small pleasant smile" are the
# same pose travelled different distances from rest - not three poses.
#
# The numbers are per-expression because the default is wrong for several of
# them. A 35% "startled" is a flinch, which is useful. A 35% "asleep" is not
# "slightly asleep" - there is no such thing; it would just be awake. So
# asleep barely scales, and the poses that CAN go to caricature go further.
# ---------------------------------------------------------------------------

LOW, MID, INTENSE = "low", "mid", "intense"

_DEFAULT_LEVELS = (0.45, 0.85, 1.30)

LEVELS: dict[str, tuple[float, float, float]] = {
    # Things with no meaningful small version. Being asleep is not a dimmer
    # switch, and neither is a hard reboot.
    "asleep":     (0.80, 1.00, 1.25),
    "blink":      (1.00, 1.00, 1.00),
    # Measured: at (0.55, 1.00, 1.35) glitch mid->intense moved less than the
    # face's own idle motion, so the two levels could not be told apart.
    "glitch":     (0.45, 1.00, 1.60),

    # Shocks: the low end is a flinch, which is genuinely different and
    # genuinely useful, so these get a wide range.
    "startled":   (0.35, 0.90, 1.35),
    "surprised":  (0.35, 0.85, 1.30),
    "alarmed":    (0.38, 0.88, 1.30),
    "oh":         (0.40, 0.85, 1.25),

    # Joy travels furthest. A 45% delight is a private little smile and a
    # 150% one is a whole body laugh - both read, so use the whole range.
    "delight":    (0.42, 0.88, 1.50),
    "grin":       (0.40, 0.90, 1.45),
    "happy":      (0.40, 0.85, 1.40),
    "love":       (0.42, 0.85, 1.38),
    "content":    (0.50, 0.90, 1.25),

    # Sinking emotions bottom out early: past a point more is not sadder, it
    # is just a different pose. Keep the top end modest.
    "sad":        (0.40, 0.85, 1.20),
    "crying":     (0.45, 0.90, 1.22),
    "apologetic": (0.42, 0.85, 1.18),
    "worried":    (0.42, 0.85, 1.25),
    "fret":       (0.44, 0.86, 1.25),
    "dread":      (0.45, 0.88, 1.22),

    # Held stares. A low-intensity stare is just looking, so start higher.
    "suspicious": (0.52, 0.90, 1.22),
    "stern":      (0.50, 0.90, 1.28),
    "skeptical":  (0.48, 0.88, 1.28),
    "angry":      (0.40, 0.88, 1.40),

    # The resting pose is already neutral; scaling it toward neutral does
    # nothing at all (rest.blend(rest, k) is rest), so its levels cannot
    # differ. Kept only so the table is complete.
    "rest":       (0.75, 1.00, 1.15),
    # These three are the faces text lands on most often. Their old ranges
    # (0.60-1.20 and similar) moved them less than idle breathing and gaze
    # do, so the level read from the sentence was invisible. Widened until
    # each step clears the idle noise.
    "attentive":  (0.40, 1.00, 1.50),
    "listening":  (0.40, 1.00, 1.50),
    "answering":  (0.45, 1.00, 1.50),
    "thinking":   (0.55, 0.90, 1.25),
}


def levels(name: str) -> tuple[float, float, float]:
    return LEVELS.get(name, _DEFAULT_LEVELS)


def level_amount(name: str, level: str) -> float:
    """The intensity multiplier for one expression at one of the three levels."""
    lo, mid, hi = levels(name)
    return {LOW: lo, MID: mid, INTENSE: hi}.get(level, mid)
