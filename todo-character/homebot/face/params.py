"""The parametric face.

Every expression this character can make is a point in one float space. Nothing
is a sprite, nothing is a pre-rendered frame. That is deliberate and it is how
Anki built Cozmo and Vector: their face is ~43 interpolated floats, and because
every pose is a point in the same space, the animation system can tween between
any two poses it is ever asked for - including poses nobody designed.

A flipbook of PNGs cannot do that. It can only play the transitions someone drew.
That difference is most of why a procedural face reads as alive.

Our space is 43 floats: 7 global, 15 per eye, 6 mouth - the same order
of magnitude as Vector's, and for the same reason.
"""

from __future__ import annotations

from dataclasses import dataclass, fields, replace


def _lerp(a: float, b: float, t: float) -> float:
    return a + (b - a) * t


@dataclass
class EyeParams:
    """One eye. Units are fractions of the nominal eye box unless stated."""

    w: float = 1.0          # width scale
    h: float = 1.0          # height scale
    radius: float = 0.42    # corner rounding, 0 = square, 0.5 = fully round
    x: float = 0.0          # centre offset, fraction of eye width
    y: float = 0.0
    angle: float = 0.0      # whole-eye rotation, degrees

    # Lids. The SIGN of the angle is what separates anger from sadness - in
    # both, the upper lid drops; only the direction of the slope differs.
    upper_lid: float = 0.0  # 0 open, 1 fully closed from above
    upper_angle: float = 0.0
    upper_bend: float = 0.0   # lid edge curvature; + bulges into the eye
    lower_lid: float = 0.0
    lower_angle: float = 0.0
    lower_bend: float = 0.0

    pupil_x: float = 0.0    # gaze within the eye, -1..1
    pupil_y: float = 0.0
    pupil_scale: float = 1.0
    pupil_alpha: float = 1.0

    def blend(self, other: "EyeParams", t: float) -> "EyeParams":
        return EyeParams(**{
            f.name: _lerp(getattr(self, f.name), getattr(other, f.name), t)
            for f in fields(self)
        })


@dataclass
class FaceParams:
    left: EyeParams = None
    right: EyeParams = None

    # Global
    glow: float = 1.0        # brightness multiplier
    tilt: float = 0.0        # whole-face rotation, degrees
    shift_x: float = 0.0     # whole-face translation, px
    shift_y: float = 0.0
    scale: float = 1.0
    aberration: float = 1.6  # chromatic fringe, px

    # Mouth
    mouth_w: float = 1.0
    mouth_curve: float = 0.18   # -1 full frown .. +1 full smile
    mouth_y: float = 0.0
    mouth_thick: float = 1.0
    mouth_alpha: float = 1.0
    mouth_open: float = 0.0     # 0 a stroke, 1 an open O
    mouth_x: float = 0.0

    # A tear is the one thing on this face that is a PROP, not a deformation.
    # No arrangement of lids and curves says "crying"; a discrete falling shape
    # does. 0 none, 1 fully formed. Drawn under the left eye only - a single
    # tear reads as grief, two read as a cartoon gag.
    tear: float = 0.0           # 0..1 size/opacity
    tear_fall: float = 0.0      # 0 at the lid, 1 at the bottom of its travel

    def __post_init__(self):
        if self.left is None:
            self.left = EyeParams()
        if self.right is None:
            self.right = EyeParams()

    def blend(self, other: "FaceParams", t: float) -> "FaceParams":
        out = {}
        for f in fields(self):
            if f.name in ("left", "right"):
                continue
            out[f.name] = _lerp(getattr(self, f.name), getattr(other, f.name), t)
        return FaceParams(
            left=self.left.blend(other.left, t),
            right=self.right.blend(other.right, t),
            **out,
        )

    def copy(self) -> "FaceParams":
        return replace(self, left=replace(self.left), right=replace(self.right))


# Which fields move together. The animator advances these groups on slightly
# different clocks so the face arrives in a chain rather than all at once -
# "start the main mass first; a connected flexible appendage follows later."
EYE_SHAPE = ("w", "h", "radius", "x", "y", "angle", "upper_lid", "upper_angle",
             "upper_bend", "lower_lid", "lower_angle", "lower_bend")
EYE_PUPIL = ("pupil_x", "pupil_y", "pupil_scale", "pupil_alpha")
FACE_MOUTH = ("mouth_w", "mouth_curve", "mouth_y", "mouth_thick",
              "mouth_alpha", "mouth_open", "mouth_x", "tear", "tear_fall")
FACE_GLOBAL = ("glow", "tilt", "shift_x", "shift_y", "scale", "aberration")


def blend_channels(a: "FaceParams", b: "FaceParams",
                   t_shape: float, t_pupil: float,
                   t_mouth: float, t_global: float) -> "FaceParams":
    """Blend with a different clock per channel group."""
    def eye(ea, eb):
        out = {}
        for k in EYE_SHAPE:
            out[k] = _lerp(getattr(ea, k), getattr(eb, k), t_shape)
        for k in EYE_PUPIL:
            out[k] = _lerp(getattr(ea, k), getattr(eb, k), t_pupil)
        return EyeParams(**out)

    kw = {}
    for k in FACE_MOUTH:
        kw[k] = _lerp(getattr(a, k), getattr(b, k), t_mouth)
    for k in FACE_GLOBAL:
        kw[k] = _lerp(getattr(a, k), getattr(b, k), t_global)
    return FaceParams(left=eye(a.left, b.left), right=eye(a.right, b.right), **kw)


def sanitise(p: "FaceParams") -> "FaceParams":
    """Overshoot deliberately pushes values past their target. Clamp the few
    that break the renderer if they land outside their real range."""
    for e in (p.left, p.right):
        e.w = max(0.04, e.w)
        e.h = max(0.02, e.h)
        e.radius = max(0.0, min(0.5, e.radius))
        e.upper_lid = max(0.0, min(1.0, e.upper_lid))
        e.lower_lid = max(0.0, min(1.0, e.lower_lid))
        e.pupil_alpha = max(0.0, min(1.0, e.pupil_alpha))
        e.pupil_scale = max(0.0, e.pupil_scale)
        e.pupil_x = max(-1.0, min(1.0, e.pupil_x))
        e.pupil_y = max(-1.0, min(1.0, e.pupil_y))
    p.glow = max(0.0, p.glow)
    p.mouth_open = max(0.0, min(1.2, p.mouth_open))
    p.mouth_alpha = max(0.0, min(1.0, p.mouth_alpha))
    # The mouth arc is drawn for -1..1; past that it folds into a different
    # shape rather than a bigger smile.
    p.mouth_curve = max(-1.0, min(1.0, p.mouth_curve))
    p.mouth_w = max(0.05, p.mouth_w)
    p.aberration = max(0.0, p.aberration)
    p.tear = max(0.0, min(1.0, p.tear))
    p.tear_fall = max(0.0, min(1.0, p.tear_fall))
    return p
