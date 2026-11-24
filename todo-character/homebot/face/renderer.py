"""Draws a FaceParams as the blue CRT panel.

Everything is drawn from the parameters each frame. There are no image assets.

The CRT treatment is four passes, applied in this order because each depends on
the previous one:

  1. shapes    - superellipse eyes, lid masks, mouth, on a transparent layer
  2. bloom     - downscale, smoothscale back up, add. Phosphor glow.
  3. aberration- split R/G/B and offset them. The colour fringe on the benchmark.
  4. scanlines - a pre-rendered multiply mask. Built once, not per frame.

Passes 2-4 are the expensive ones and can each be switched off for a Pi that is
struggling; `Quality.cheap()` does that. The shapes pass alone still reads as
the same character, just without the glass.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

import pygame

from .params import FaceParams, EyeParams

# Palette, read off the benchmark panel.
GLOW = (212, 231, 252)
GLOW_HOT = (248, 252, 255)
PANEL = (8, 10, 14)
BEZEL = (27, 27, 29)
BEZEL_EDGE = (62, 62, 66)
CATCHLIGHT = (225, 240, 255)


@dataclass
class Quality:
    bloom: bool = True
    aberration: bool = True
    scanlines: bool = True
    bezel: bool = True
    bloom_div: int = 6          # higher = cheaper, softer

    @classmethod
    def cheap(cls) -> "Quality":
        return cls(bloom=True, aberration=False, scanlines=True,
                   bezel=False, bloom_div=8)


def _rounded_poly(cx: float, cy: float, hw: float, hh: float,
                  radius_frac: float, steps: int = 7) -> list[tuple[float, float]]:
    """A rounded rectangle as a point list. radius_frac 0.5 gives an ellipse."""
    r = max(0.0, min(0.5, radius_frac)) * 2.0 * min(hw, hh)
    r = min(r, hw, hh)
    if r <= 0.5:
        return [(cx - hw, cy - hh), (cx + hw, cy - hh),
                (cx + hw, cy + hh), (cx - hw, cy + hh)]
    pts: list[tuple[float, float]] = []
    corners = [
        (cx + hw - r, cy - hh + r, -90, 0),
        (cx + hw - r, cy + hh - r, 0, 90),
        (cx - hw + r, cy + hh - r, 90, 180),
        (cx - hw + r, cy - hh + r, 180, 270),
    ]
    for ox, oy, a0, a1 in corners:
        for i in range(steps + 1):
            a = math.radians(a0 + (a1 - a0) * i / steps)
            pts.append((ox + r * math.cos(a), oy + r * math.sin(a)))
    return pts


def _lid_poly(cx: float, cy: float, hw: float, hh: float, cover: float,
              angle_deg: float, bend: float, upper: bool) -> list[tuple[float, float]]:
    """The polygon a lid eats out of the eye.

    `cover` is how far across the eye it comes, `angle_deg` tilts the edge
    (its SIGN is what separates a sad lid from an angry one), and `bend` bows
    the edge into the eye, which is what turns a squashed eye into a crescent.
    """
    pad = hw * 0.6 + 6
    span = 2 * hh + 4
    edge = (cy - hh - 2) + cover * span if upper else (cy + hh + 2) - cover * span
    slope = math.tan(math.radians(max(-60.0, min(60.0, angle_deg))))
    bend = max(-cover, min(cover, bend))
    bow = bend * hh * 1.15 * (1.0 if upper else -1.0)

    pts = []
    n = 14
    for i in range(n + 1):
        t = i / n
        x = cx - hw - pad + t * (2 * hw + 2 * pad)
        y = edge + slope * (x - cx) + bow * math.sin(math.pi * t)
        pts.append((x, y))
    far = (cy - hh - span - 10) if upper else (cy + hh + span + 10)
    pts.append((cx + hw + pad, far))
    pts.append((cx - hw - pad, far))
    return pts


class FaceRenderer:
    def __init__(self, size: tuple[int, int] = (640, 400), quality: Quality | None = None):
        self.w, self.h = size
        self.q = quality or Quality()
        self._scanlines = self._build_scanlines()
        self._layer = pygame.Surface(size, pygame.SRCALPHA)
        self._out = pygame.Surface(size)

        # Geometry, all derived from panel size so it scales to any display.
        self.eye_hw = self.w * 0.142
        self.eye_hh = self.h * 0.175
        self.eye_gap = self.w * 0.188
        self.cy = self.h * 0.44
        self.mouth_y = self.h * 0.700
        self.mouth_hw = self.w * 0.112

    # -- passes ------------------------------------------------------------

    def _build_scanlines(self) -> pygame.Surface:
        s = pygame.Surface((self.w, self.h))
        s.fill((255, 255, 255))
        dark = (92, 92, 92)
        for y in range(0, self.h, 3):
            pygame.draw.line(s, dark, (0, y), (self.w, y))
            pygame.draw.line(s, (196, 196, 196), (0, y + 1), (self.w, y + 1))
        return s

    def _draw_eye(self, surf: pygame.Surface, e: EyeParams, cx: float, colour) -> None:
        hw = self.eye_hw * max(0.05, e.w)
        hh = self.eye_hh * max(0.03, e.h)
        ecx = cx + e.x * self.eye_hw
        ecy = self.cy + e.y * self.eye_hh

        # Rotation of the whole eye: cheapest correct way is to draw into a
        # local surface and rotate that, so the lids rotate with it.
        pad = int(max(hw, hh) * 1.8) + 14
        loc = pygame.Surface((pad * 2, pad * 2), pygame.SRCALPHA)
        lx, ly = pad, pad

        pygame.draw.polygon(loc, colour, _rounded_poly(lx, ly, hw, hh, e.radius))

        # The pupil is a HOLE, not a dark fill - so the panel shows through and
        # the bloom pass only ever sees emitting blue.
        if e.pupil_alpha > 0.01:
            pr_w = hw * 0.50 * e.pupil_scale
            pr_h = hh * 0.60 * e.pupil_scale
            px = lx + e.pupil_x * (hw - pr_w) * 0.92
            py = ly + e.pupil_y * (hh - pr_h) * 0.92
            pr_w = min(pr_w, hw * 0.96)
            pr_h = min(pr_h, hh * 0.96)
            if pr_w > 1 and pr_h > 1:
                pygame.draw.ellipse(
                    loc, (0, 0, 0, 0),
                    pygame.Rect(px - pr_w, py - pr_h, pr_w * 2, pr_h * 2))
                cr = max(2.0, pr_w * 0.26)
                a = int(235 * e.pupil_alpha)
                pygame.draw.circle(loc, (*CATCHLIGHT, a),
                                   (px + pr_w * 0.42, py - pr_h * 0.44), cr)

        if e.upper_lid > 0.005:
            pygame.draw.polygon(loc, (0, 0, 0, 0), _lid_poly(
                lx, ly, hw, hh, e.upper_lid, e.upper_angle, e.upper_bend, True))
        if e.lower_lid > 0.005:
            pygame.draw.polygon(loc, (0, 0, 0, 0), _lid_poly(
                lx, ly, hw, hh, e.lower_lid, e.lower_angle, e.lower_bend, False))

        if abs(e.angle) > 0.2:
            loc = pygame.transform.rotate(loc, -e.angle)
        r = loc.get_rect(center=(ecx, ecy))
        surf.blit(loc, r)

    def _draw_tear(self, surf: pygame.Surface, p: FaceParams, colour) -> None:
        """One tear, under the left eye.

        Taken straight from the reference sheet: on that face the only pose
        the lids cannot reach is grief, and it is solved with an object rather
        than a shape change. The same trick works here because the tear is a
        SOLID - it has no pupil hole - so it reads as a different material from
        the eye above it even at 320x240.
        """
        if p.tear < 0.01:
            return
        cx = self.w * 0.5 - self.eye_gap + self.eye_hw * 0.30
        top = self.cy + self.eye_hh * 0.82
        travel = self.h * 0.16 * p.tear_fall
        cy = top + travel

        r = self.eye_hw * 0.17 * p.tear
        if r < 1.2:
            return
        a = int(255 * min(1.0, p.tear * (1.25 - 0.45 * p.tear_fall)))
        col = (*colour, a)

        # A drop is a circle with a point pulled up out of it: rounder as it
        # falls, because surface tension wins once it is no longer hanging.
        point = r * (2.05 - 1.15 * p.tear_fall)
        pygame.draw.circle(surf, col, (int(cx), int(cy)), int(r))
        pygame.draw.polygon(surf, col, [
            (cx, cy - point),
            (cx - r * 0.82, cy + r * 0.12),
            (cx + r * 0.82, cy + r * 0.12),
        ])

    def _draw_mouth(self, surf: pygame.Surface, p: FaceParams, colour) -> None:
        """The mouth is one shape between two arcs, not a stroke OR an ellipse.

        The old version swapped a curved stroke for a round ellipse as soon as
        the mouth opened, which threw the expression away at exactly the moment
        the character started talking - an apologetic face and a delighted face
        opened into the identical circle. Here the upper arc always carries
        mouth_curve and the lower arc is pushed down by mouth_open, so a happy
        mouth opens happily and a sorry one opens sorry.
        """
        if p.mouth_alpha < 0.02:
            return
        col = (*colour, int(255 * max(0.0, min(1.0, p.mouth_alpha))))
        cx = self.w * 0.5 + p.mouth_x * self.mouth_hw
        cy = self.mouth_y + p.mouth_y * self.h
        hw = self.mouth_hw * max(0.08, p.mouth_w)
        thick = max(2.0, self.h * 0.0255 * p.mouth_thick)
        amp = p.mouth_curve * self.h * 0.098
        open_h = max(0.0, p.mouth_open) * self.h * 0.200

        n = 72
        upper, lower = [], []
        for i in range(n + 1):
            t = i / n
            x = cx - hw + t * 2 * hw
            u = (x - cx) / max(hw, 1e-6)
            k = max(0.0, 1.0 - u * u)   # float error here goes complex under **
            yu = cy + amp * k - amp * 0.5
            upper.append((x, yu))
            # sqrt(1-u^2) is a true ellipse. A power curve here comes to a
            # point in the middle and the open mouth reads as a fang.
            lower.append((x, yu + open_h * math.sqrt(k)))

        if open_h <= thick * 1.15:
            # Closed. This used to stamp 31 discs at int() coordinates along
            # the arc, which is exactly why the smile looked chewed: every
            # centre got truncated to a whole pixel, so the stroke stepped
            # instead of curving. Sweep a band along the arc normal and fill
            # it as one polygon - same round caps, one clean edge.
            top, bot = [], []
            for i, (x, y) in enumerate(upper):
                j0 = max(0, i - 1)
                j1 = min(len(upper) - 1, i + 1)
                dx = upper[j1][0] - upper[j0][0]
                dy = upper[j1][1] - upper[j0][1]
                ln = math.hypot(dx, dy) or 1.0
                nx, ny = -dy / ln, dx / ln     # unit normal to the arc
                top.append((x + nx * thick, y + ny * thick))
                bot.append((x - nx * thick, y - ny * thick))
            pygame.draw.polygon(surf, col, top + list(reversed(bot)))
            for x, y in (upper[0], upper[-1]):
                pygame.draw.circle(surf, col, (int(round(x)), int(round(y))),
                                   int(round(thick)))
            return

        pygame.draw.polygon(surf, col, upper + list(reversed(lower)))

    def _bloom(self, layer: pygame.Surface, out: pygame.Surface, strength: float) -> None:
        # Two glows, not one. The reference panel has a tight bright rim sitting
        # inside a wide soft haze - a single blur radius can only be one or the
        # other, which is why this read as a hard outline before.
        d = max(2, self.q.bloom_div)
        tight = pygame.transform.smoothscale(layer, (self.w // d, self.h // d))
        tight = pygame.transform.smoothscale(tight, (self.w, self.h))

        # The wide pass has to stay a HALO. Blurred far enough it stops being a
        # glow around the shape and just lifts the whole panel off black, which
        # is the one thing an OLED face must not do.
        wd = d * 2
        wide = pygame.transform.smoothscale(layer, (max(1, self.w // wd),
                                                    max(1, self.h // wd)))
        wide = pygame.transform.smoothscale(wide, (self.w, self.h))

        big = tight
        wide.fill((120, 120, 120, 255), None, pygame.BLEND_RGB_MULT)
        big.blit(wide, (0, 0), special_flags=pygame.BLEND_RGB_ADD)
        k = max(0.0, min(1.0, 0.30 * strength))
        big.fill((int(70 * k), int(140 * k), int(255 * k), 255),
                 None, pygame.BLEND_RGB_MULT)
        out.blit(big, (0, 0), special_flags=pygame.BLEND_RGB_ADD)

    def _aberrate(self, layer: pygame.Surface, out: pygame.Surface, px: float) -> None:
        o = int(round(px))
        if o < 1:
            out.blit(layer, (0, 0), special_flags=pygame.BLEND_RGB_ADD)
            return
        for mask, dx in (((255, 0, 0), -o), ((0, 255, 0), 0), ((0, 0, 255), o)):
            c = layer.copy()
            c.fill((*mask, 255), None, pygame.BLEND_RGB_MULT)
            out.blit(c, (dx, 0), special_flags=pygame.BLEND_RGB_ADD)

    # -- public ------------------------------------------------------------

    def render(self, p: FaceParams) -> pygame.Surface:
        layer = self._layer
        layer.fill((0, 0, 0, 0))

        g = max(0.0, min(1.6, p.glow))
        k = min(1.0, 0.55 + 0.45 * g)   # never clip B; hue must hold
        colour = tuple(int(c * k) for c in GLOW)

        half = self.eye_gap
        self._draw_eye(layer, p.left, self.w * 0.5 - half, colour)
        self._draw_eye(layer, p.right, self.w * 0.5 + half, colour)
        self._draw_mouth(layer, p, colour)
        self._draw_tear(layer, p, colour)

        if abs(p.tilt) > 0.2 or abs(p.scale - 1.0) > 0.01:
            layer = pygame.transform.rotozoom(layer, -p.tilt, max(0.3, p.scale))

        out = self._out
        out.fill(PANEL)
        pos = (int(p.shift_x) + (self.w - layer.get_width()) // 2,
               int(p.shift_y) + (self.h - layer.get_height()) // 2)

        shifted = pygame.Surface((self.w, self.h), pygame.SRCALPHA)
        shifted.blit(layer, pos)

        # Scanlines belong to the EMISSION, not to the finished picture. They
        # used to be a multiply over the final frame, which meant the eye blew
        # out to flat white first and the mask then knocked that white down to
        # a flat grey - so the colour of the face could not reach the screen at
        # all. Darkening the source instead keeps the troughs at the emitter's
        # own blue while the bloom lifts only the peaks toward white, which is
        # exactly the gradient the reference panel shows.
        if self.q.scanlines:
            shifted.blit(self._scanlines, (0, 0), special_flags=pygame.BLEND_RGB_MULT)

        if self.q.aberration and p.aberration >= 1.0:
            self._aberrate(shifted, out, p.aberration)
        else:
            out.blit(shifted, (0, 0))
        if self.q.bloom:
            self._bloom(shifted, out, g)
        return out

    def draw_bezel(self, target: pygame.Surface, rect: pygame.Rect) -> None:
        if not self.q.bezel:
            return
        o = rect.inflate(26, 26)
        pygame.draw.rect(target, BEZEL, o, border_radius=30)
        pygame.draw.rect(target, BEZEL_EDGE, o, width=2, border_radius=30)
