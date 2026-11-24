"""Text -> viseme track, on the Rhubarb / Hanna-Barbera shape set.

The shapes are the six basic ones invented at Hanna-Barbera and used since by
Disney and Warner Bros, plus Rhubarb's three extended ones:

  A  closed, slight pressure between the lips     P B M
  B  slightly open, clenched teeth                most consonants, and EE
  C  open                                         EH (men), AE (bat)
  D  wide open                                    AA (father)
  E  slightly rounded, no wider open than C       AO (off), ER (bird)
  F  puckered lips                                UW (you), OW (show), W
  G  upper teeth on lower lip                     F V
  H  open as C but not as D, tongue up            long L
  X  idle, lips closed but relaxed                pauses

We have no audio, so this is the standard text-only chain: grapheme-to-phoneme,
then phoneme-to-viseme. The G2P is rule-based rather than dictionary-based,
which is wrong on English's irregular spellings (it will say "though" with an
OW) and exactly right on Devanagari, which is phonetic.

Two things make it read as speech rather than flapping:

  * The mouth CLOSES between words and at punctuation. A mouth that never
    returns to X is the commonest tell of fake lip sync.
  * Cues are blended over ~70ms rather than cut. Rhubarb's own example for
    "Hi" runs X, D, C, B, X and notes that C is inserted "as an in-between...
    for a smoother animation from D to B" - our cosine blend passes through
    that intermediate opening on its own, so we get the in-between for free.

Shape geometry is (open, width): a puckered F is narrow and moderately open, a
D is wide open and not very wide across. Teeth and tongue are deliberately not
modelled - at 320x240 behind a scanline mask they are below the resolution of
the panel, and faking them costs legibility.
"""

from __future__ import annotations

import math

from . import pronounce
import re
from dataclasses import dataclass

#: shape -> (mouth_open 0..1, mouth_width multiplier, is_vowel)
SHAPES: dict[str, tuple[float, float, bool]] = {
    "X": (0.00, 1.00, False),   # rest, relaxed
    "A": (0.00, 0.90, False),   # closed, pressed
    "B": (0.22, 1.06, False),   # slightly open, teeth together
    "C": (0.58, 0.92, True),    # open
    "D": (1.00, 0.84, True),    # wide open
    "E": (0.50, 0.66, True),    # rounded
    "F": (0.44, 0.42, True),    # puckered - narrow, so it must open MORE to
                                # read as a pucker rather than a flat line
    "G": (0.14, 0.84, False),   # teeth on lip
    "H": (0.70, 0.88, True),    # L, tongue up
}

# Base duration per shape, in seconds, at rate 1.0. Vowels carry length;
# stops are quick. Scaled by the speaker's rate.
_DUR = {"X": 0.09, "A": 0.07, "B": 0.075, "C": 0.125, "D": 0.145,
        "E": 0.125, "F": 0.13, "G": 0.085, "H": 0.115}

BLEND = 0.070          # cosine blend window between cues
WORD_GAP = 0.055       # the mouth returns toward rest between words
COMMA_PAUSE = 0.20
STOP_PAUSE = 0.34

# --- English ---------------------------------------------------------------

_DIGRAPHS = [
    ("igh", "D"), ("ough", "F"), ("augh", "C"),
    ("tch", "B"), ("sch", "B"),
    ("ch", "B"), ("sh", "B"), ("th", "B"), ("ph", "G"), ("gh", "B"),
    ("ck", "B"), ("ng", "B"), ("qu", "F"), ("wh", "F"),
    ("oo", "F"), ("ou", "F"), ("ow", "F"), ("oa", "E"), ("oi", "E"),
    ("oy", "E"), ("oe", "E"),
    ("ee", "B"), ("ea", "B"), ("ie", "B"), ("ei", "B"),
    ("ai", "D"), ("ay", "D"), ("au", "C"), ("aw", "C"),
    ("ar", "D"), ("er", "E"), ("ir", "E"), ("ur", "E"), ("or", "E"),
]
# 'h' makes no mouth shape of its own - it is breath, and the mouth is
# already forming the vowel after it. Giving it a shape is why "Hi" came out
# closed instead of wide open.
_SILENT = set("h")
_SINGLE = {
    "a": "C", "e": "C", "i": "B", "o": "E", "u": "B", "y": "B",
    "p": "A", "b": "A", "m": "A",
    "f": "G", "v": "G",
    "w": "F",
    "l": "H",
    "r": "E",
}


# --- English: phonemes, not letters -----------------------------------------
#
# ARPAbet phoneme -> viseme. This is the real mapping, and it is the half of
# the problem that is genuinely solved: given a phoneme, the mouth shape is
# not in doubt. All the remaining uncertainty lives upstream, in getting from
# spelling to phonemes.
#
# Diphthongs get TWO cues, because they are two mouth positions - that is what
# makes them diphthongs. Rhubarb's own worked example shows "Hi" as D then B,
# which is exactly AY spelt out as its two halves.

_PHON: dict[str, tuple[str, ...]] = {
    # closed, pressed
    "P": ("A",), "B": ("A",), "M": ("A",),
    # teeth on lip
    "F": ("G",), "V": ("G",),
    # tongue up
    "L": ("H",),
    # rounded / puckered
    "W": ("F",), "UW": ("F",), "UH": ("F",),
    "R": ("E",), "ER": ("E",), "AO": ("E",),
    # wide open
    "AA": ("D",), "AE": ("D",),
    # mid open
    "AH": ("C",), "EH": ("C",), "IH": ("B",), "IY": ("B",),
    # diphthongs: two positions, in order
    "AY": ("D", "B"), "AW": ("D", "F"), "EY": ("C", "B"),
    "OW": ("E", "F"), "OY": ("E", "B"),
    # everything else closes toward the teeth
    "T": ("B",), "D": ("B",), "N": ("B",), "S": ("B",), "Z": ("B",),
    "K": ("B",), "G": ("B",), "NG": ("B",), "Y": ("B",),
    "CH": ("B",), "JH": ("B",), "SH": ("B",), "ZH": ("B",),
    "TH": ("B",), "DH": ("B",),
    "HH": (),               # no shape of its own; the next vowel carries it
}


def _english(word: str) -> list[str]:
    out: list[str] = []
    for ph in pronounce.phonemes(word):
        out.extend(_PHON.get(ph, ("B",)))
    # A held shape is one cue, not two.
    return [s for j, s in enumerate(out) if j == 0 or s != out[j - 1]]


# --- Devanagari ------------------------------------------------------------
# Phonetic, so this mapping is genuinely accurate rather than a guess.

VIRAMA = "्"
_DEVA_VOWEL = {
    "अ": "C", "आ": "D", "इ": "B", "ई": "B",
    "उ": "F", "ऊ": "F", "ए": "C", "ऐ": "C",
    "ओ": "E", "औ": "F", "ऋ": "E",
}
_DEVA_MATRA = {
    "ा": "D", "ि": "B", "ी": "B", "ु": "F",
    "ू": "F", "ृ": "E", "े": "C", "ै": "C",
    "ो": "E", "ौ": "F",
}
_DEVA_CONS = {
    "प": "A", "फ": "G", "ब": "A", "भ": "A", "म": "A",
    "व": "G", "ल": "H", "ळ": "H", "र": "E",
}


def _devanagari(word: str) -> list[str]:
    out: list[str] = []
    ch = list(word)
    for i, c in enumerate(ch):
        nxt = ch[i + 1] if i + 1 < len(ch) else ""
        if c in _DEVA_VOWEL:
            out.append(_DEVA_VOWEL[c])
        elif c in _DEVA_MATRA:
            out.append(_DEVA_MATRA[c])
        elif c in ("ं", "ँ"):          # anusvara / candrabindu
            out.append("A")
        elif "क" <= c <= "ह" or "क़" <= c <= "य़":
            out.append(_DEVA_CONS.get(c, "B"))
            # inherent short 'a', unless a virama kills it or a matra replaces it
            if nxt != VIRAMA and nxt not in _DEVA_MATRA:
                out.append("C")
    if len(out) > 2 and out[-1] == "C":
        out.pop()
    return [s for j, s in enumerate(out) if j == 0 or s != out[j - 1]]


def word_shapes(word: str) -> list[str]:
    if any("ऀ" <= c <= "ॿ" for c in word):
        return _devanagari(word)
    return _english(word)


@dataclass
class Cue:
    t0: float
    t1: float
    shape: str
    stress: float = 0.5


class VisemeTrack:
    """A timed list of mouth cues, the same shape of data Rhubarb emits."""

    def __init__(self, text: str, rate: float = 5.2, crisp: float = 0.5):
        self.text = text
        self.cues: list[Cue] = []
        self.words: list[str] = []
        self.skipped: list[str] = []
        self._build(text, rate, crisp)

    def _build(self, text: str, rate: float, crisp: float) -> None:
        # rate is syllables/sec in the old rhythm model; visemes run several
        # times faster than syllables, so scale relative to a 5.2 baseline.
        speed = max(0.45, min(2.2, rate / 5.2))
        hold = (1.0 - 0.28 * max(0.0, min(1.0, crisp))) / speed

        # The lead-in and the closing tail are fixed costs. On a one-word
        # reply ("Okay.") they used to be most of the utterance - over a
        # second for one word - so both scale with length (set below, once
        # the words are known). The cue list starts with the lead-in X.
        t = 0.0

        def push(shape: str, d: float) -> None:
            nonlocal t
            if self.cues and self.cues[-1].shape == shape:
                self.cues[-1].t1 += d      # a held shape is one cue, not two
            else:
                self.cues.append(Cue(t, t + d, shape))
            t += d

        # Say the text the way a voice would say it BEFORE looking for mouth
        # shapes. Without this, "I have 25 books" produced no mouth at all for
        # the 25 - a whole word the face silently skipped while the voice said
        # it, which a viewer notices far faster than a slightly wrong vowel.
        # Devanagari is already phonetic, so it passes through untouched.
        # Devanagari digits are numbers like any other ("७:३०" is half past
        # seven), and a danda glued to a Latin word ("500 mg।") is just a full
        # stop - left on, it drags "mg" into the Devanagari reader, which
        # cannot say it, so the word went silent.
        text = text.translate(pronounce._DEVA_DIGITS)
        text = re.sub(r"(?<=[^\u0900-\u097f\s])[\u0964\u0965]", ".", text)
        raw = [tok for tok in re.split(r"(\s+)", text) if tok.strip()]
        tokens: list[str] = []
        run: list[str] = []

        def flush() -> None:
            # Latin runs are normalised together, not word by word, because a
            # number's reading depends on its neighbours: "call 1930" is
            # dialled digit by digit, "in 1930" is a year.
            if run:
                spoken = pronounce.normalise(" ".join(run))
                tokens.extend(spoken if spoken else run)
                run.clear()

        for tok in raw:
            if any("\u0900" <= c <= "\u097f" for c in tok):
                flush()
                tokens.append(tok)
            else:
                run.append(tok)
        flush()

        nwords = sum(1 for tok in tokens if re.sub(r"[^\wऀ-ॿ]", "", tok))
        short = max(0.0, min(1.0, (nwords - 1) / 3.0))   # 0 for one word, 1 from four
        lead = 0.05 + 0.05 * short
        self.cues.append(Cue(0.0, lead, "X"))
        t = lead
        last = len(tokens) - 1
        for n, tok in enumerate(tokens):
            letters = re.sub(r"[^\wऀ-ॿ]", "", tok)
            shapes = word_shapes(letters) if letters else []
            if not shapes:
                # Every token must produce something. A token we cannot read
                # becomes an audible beat, never a silently dropped word.
                shapes = ["C"] if letters else []
                if letters:
                    self.skipped.append(tok)
            if letters:
                self.words.append(letters)
            for s in shapes:
                push(s, _DUR[s] * hold)

            tail = tok[-1:]
            if tail in ",;:":
                gap = COMMA_PAUSE
            elif tail in ".!?।":
                gap = STOP_PAUSE
            else:
                gap = WORD_GAP
            if n == last:
                # The final full stop is silence the tail already covers.
                gap = min(gap, WORD_GAP + (STOP_PAUSE - WORD_GAP) * short * 0.5)
            # The mouth closes between words. This is most of what separates
            # speech from flapping.
            push("X", gap)

        push("X", 0.10 + 0.08 * short)   # push() already advanced t past it
        self.duration = t
        self._mark_stress()

    def _mark_stress(self) -> None:
        """The first vowel of each word carries the beat."""
        want = True
        for c in self.cues:
            if c.shape == "X":
                want = True
                continue
            if want and SHAPES[c.shape][2]:
                c.stress = 1.0
                want = False

    # -- per-frame ---------------------------------------------------------

    def _at(self, t: float) -> tuple[Cue, Cue, float]:
        """The cue at t, the next one, and how far into the blend we are."""
        lo, hi = 0, len(self.cues) - 1
        while lo < hi:
            mid = (lo + hi) // 2
            if self.cues[mid].t1 <= t:
                lo = mid + 1
            else:
                hi = mid
        cur = self.cues[lo]
        nxt = self.cues[min(lo + 1, len(self.cues) - 1)]
        # Blend out of this cue into the next over the last BLEND seconds.
        span = min(BLEND, (cur.t1 - cur.t0) * 0.9)
        k = 0.0
        if span > 0 and t > cur.t1 - span:
            k = (t - (cur.t1 - span)) / span
            k = 0.5 - 0.5 * math.cos(math.pi * max(0.0, min(1.0, k)))
        return cur, nxt, k

    def mouth(self, t: float) -> tuple[float, float]:
        """(open, width) at time t, cosine-blended between cues."""
        if t < 0 or t > self.duration:
            return 0.0, 1.0
        cur, nxt, k = self._at(t)
        o0, w0, _ = SHAPES[cur.shape]
        o1, w1, _ = SHAPES[nxt.shape]
        return o0 + (o1 - o0) * k, w0 + (w1 - w0) * k

    def energy(self, t: float) -> float:
        """How hard he is speaking: the whole-face impulse, from jaw opening."""
        o, _ = self.mouth(t)
        return max(0.0, min(1.0, o / 0.95))

    def accent(self, t: float) -> float:
        """A decaying spike at each stressed vowel onset."""
        out = 0.0
        for c in self.cues:
            if c.stress < 0.9:
                continue
            x = t - c.t0
            if 0 <= x < 0.26:
                out = max(out, (1.0 - x / 0.26) ** 2)
        return out

    def breath(self, t: float) -> float:
        if self.duration <= 0:
            return 0.0
        return math.sin(math.pi * max(0.0, min(1.0, t / self.duration)) * 2.0)

    def done(self, t: float) -> bool:
        return t > self.duration

    def debug(self) -> str:
        return " ".join(c.shape for c in self.cues)
