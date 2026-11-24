"""Conversation-level tests for homebot's face.

    PYTHONPATH=. .venv/bin/python tests/run_conversation_tests.py

Drives the REAL FaceApp (homebot/face/app.py) headless: its _submit, _wake,
_on_state, _on_reply and _idle_check run unmodified. Only two things are
swapped, from outside, on the instance / module attribute:
  * the clock: `time` in homebot.face.app and homebot.face.animator is
    replaced with a fake whose monotonic() advances 1/50 s per frame (the app
    ticks at 50 fps);
  * the mind: FaceApp.mind is a stub with the same busy/ask contract as
    mind.Mind (ask() is dropped while busy; busy clears when the reply is
    delivered). The brain-state stream is SIMULATED from each conversation's
    expected states, because there is no API key; OfflineMind is run
    separately to show what an offline family actually sees.
Nothing under homebot/ is edited. Raw results go to the scratchpad dir given
by $CONV_OUT (default: alongside nothing - printed only).
"""

from __future__ import annotations

import json
import math
import os
import random
import re
import statistics as st
import sys
import time as _realtime
from collections import Counter, defaultdict
from dataclasses import fields

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame  # noqa: E402

from homebot.face import animator as AN  # noqa: E402
from homebot.face import app as APP  # noqa: E402
from homebot.face import expressions as E  # noqa: E402
from homebot.face import pronounce as PR  # noqa: E402
from homebot.face import reading as R  # noqa: E402
from homebot.face import visemes as V  # noqa: E402
from homebot.face.mind import Mind, OfflineMind  # noqa: E402
from tests.conversations import CONVERSATIONS  # noqa: E402

FPS = 50
DT = 1.0 / FPS
STATE_NAME = {"think": "thinking", "tool": "tool", "success": "success",
              "speak": "speaking", "refused": "refused", "stuck": "stuck",
              "unknown": "unknown_speaker", "sleep": "sleep"}
# How long each Brain state is held before the next arrives (realistic gaps
# for a Gemini round-trip / a tool call). States emitted right before the
# reply (speaking/refused/stuck/sleep) get no hold, as in mind.Mind._work.
STATE_GAP = {"thinking": 0.9, "tool": 0.7, "success": 0.35,
             "unknown_speaker": 0.5}
MOUTHLESS = ("tender", "alarmed", "peek", "attentive", "drowsy", "suspicious")
BETWEEN_TURNS = 2.0     # pause after a reply finishes before the next event


# ---------------------------------------------------------------------------
# fake clock
# ---------------------------------------------------------------------------

class FakeTime:
    def __init__(self, t0=1000.0):
        self.now = t0

    def monotonic(self):
        return self.now

    def time(self):
        return self.now

    def sleep(self, s):
        self.now += s

    def perf_counter(self):
        return _realtime.perf_counter()


class StubMind:
    """Same contract as mind.Mind: ask() is ignored while busy."""
    backend = "simulated"
    detail = "conversation script"

    def __init__(self):
        self.busy = False
        self.asked = []
        self.dropped = []

    def ask(self, text, speaker=None):
        if self.busy:
            self.dropped.append(text)
            return
        self.busy = True
        self.asked.append(text)


_APP = None


def fresh_app(seed):
    """A FaceApp with a fake clock, a stub mind and a seeded RNG."""
    global _APP
    clock = FakeTime()
    APP.time = clock
    AN.time = clock
    random.seed(seed)
    if _APP is None:
        _APP = APP.FaceApp(size=(640, 400))
    app = _APP
    app.anim = AN.Animator(app.renderer)
    app.mind = StubMind()
    app.last_activity = clock.now
    app.asleep = False
    app._reply_at = 0.0
    app.typed = ""
    return app, clock


# ---------------------------------------------------------------------------
# per-frame recorder
# ---------------------------------------------------------------------------

def _flat(p):
    d = {}
    for f in fields(p):
        if f.name in ("left", "right"):
            for g in fields(getattr(p, f.name)):
                d[f"{f.name[0]}.{g.name}"] = getattr(getattr(p, f.name), g.name)
        else:
            d[f.name] = getattr(p, f.name)
    return d


# per-frame thresholds (50 fps). Justification in CONVERSATION_GAPS.md:
# a 0.42 s default beat moving a channel by its largest library range peaks
# well under these; only sub-0.2 s beats, blinks, saccades and viseme cuts
# legitimately exceed them, and those are attributed separately below.
JUMP = {"glow": 0.10, "shift_x": 3.0, "shift_y": 3.0, "tilt": 3.0,
        "scale": 0.05, "mouth_open": 0.45, "mouth_alpha": 0.35,
        "mouth_curve": 0.35, "l.h": 0.30, "r.h": 0.30,
        "l.upper_lid": 0.35, "r.upper_lid": 0.35,
        "l.pupil_x": 0.35, "r.pupil_x": 0.35, "l.pupil_y": 0.35, "r.pupil_y": 0.35,
        "l.pupil_alpha": 0.45, "r.pupil_alpha": 0.45}
LEGIT = {"fast_beat", "blink", "saccade", "speech", "speech_accent"}


class Recorder:
    def __init__(self, app, clock, cid):
        self.app, self.clock, self.cid = app, clock, cid
        self.prev = None
        self.prev_base = app.anim.base
        self.prev_overlay = app.anim.overlay_name
        self.prev_utt = None
        self.prev_gaze_t0 = app.anim._gaze_t0
        self.update_times = []
        self.frames = 0
        self.sanity = []
        self.jumps = []           # (cid, t, channel, delta, cause)
        self.bases = Counter()
        self.speech_frames = 0
        self.invisible_speech = 0   # utt active, viseme open, mouth_alpha<0.02
        self.utt_replaced = []
        self.base_trace = []      # (t, base) on change
        self.prev_cur = None
        self.prev_look = None

    def step(self, seconds):
        n = max(1, int(round(seconds / DT)))
        for _ in range(n):
            self.frame()

    def frame(self):
        app, a, clk = self.app, self.app.anim, self.clock
        clk.now += DT
        app._idle_check()
        utt_before = a._utt
        t0 = _realtime.perf_counter()
        p = a.update()
        self.update_times.append(_realtime.perf_counter() - t0)
        self.frames += 1
        now = clk.now
        d = _flat(p)

        # sanity
        bad = [k for k, v in d.items() if not math.isfinite(v)]
        for e in ("l", "r"):
            if d[f"{e}.w"] <= 0 or d[f"{e}.h"] <= 0:
                bad.append(f"{e}.w/h<=0")
            for k in ("upper_lid", "lower_lid"):
                if not 0.0 <= d[f"{e}.{k}"] <= 1.0:
                    bad.append(f"{e}.{k}")
            for k in ("pupil_x", "pupil_y"):
                if not -1.0 <= d[f"{e}.{k}"] <= 1.0:
                    bad.append(f"{e}.{k}")
        if not 0.0 <= d["mouth_open"] <= 1.2:
            bad.append("mouth_open")
        if d["glow"] < 0:
            bad.append("glow")
        if bad:
            self.sanity.append((self.cid, round(now, 2), bad))

        # speech visibility
        if utt_before is not None:
            stt = now - a._utt_t0 if a._utt is not None else None
            if a._utt is not None:
                self.speech_frames += 1
                vo, _ = a._utt.mouth(stt)
                if vo > 0.05 and p.mouth_alpha < 0.02:
                    self.invisible_speech += 1

        # cause attribution for jumps. `cur` is the pose layer alone (beat +
        # overlap); the residual final-minus-pose is idle life + speech.
        cur = _flat(a.current)
        swap = (a.base != self.prev_base) or (a.overlay_name != self.prev_overlay)
        replaced = (a._utt is not None and self.prev_utt is not None
                    and a._utt is not self.prev_utt)
        b = a._beat
        in_beat = (now - a._t0) < b.dur * 1.25
        soft = set()
        if a._blinking:
            soft.add("blink")
        if now - a._gaze_t0 < 0.1:
            soft.add("saccade")
        if a._look_at is not None or self.prev_look is not None and a._look_at is None:
            soft.add("look_at")
        if a._utt is not None:
            soft.add("speech")
        if self.prev is not None:
            for k, thr in JUMP.items():
                dv = d[k] - self.prev[k]
                if abs(dv) <= thr:
                    continue
                dpose = cur[k] - self.prev_cur[k]
                resid = dv - dpose
                if replaced and k.startswith("mouth"):
                    cause = "utterance_replaced"
                elif swap and abs(resid) > thr and not (soft & {"blink", "saccade", "look_at"}):
                    cause = ("talk_swap_mid_speech" if a._utt is not None and a.base != self.prev_base
                             else "idle_layer_swap")
                elif in_beat and abs(dpose) > thr * 0.5:
                    cause = "legit:snap_beat" if b.hold_snap >= 0.5 else "legit:transition"
                elif soft:
                    cause = "legit:" + "+".join(sorted(soft))
                elif in_beat:
                    cause = "legit:transition"
                else:
                    cause = "unexplained"
                self.jumps.append((self.cid, round(now, 2), k, round(dv, 3), cause,
                                   self.prev_base, a.base, round(resid, 3)))
        self.prev_cur = cur
        self.prev_look = a._look_at
        if a.base != self.prev_base:
            self.base_trace.append((round(now, 2), a.base))
        self.bases[a.base] += 1
        if a.overlay_name:
            self.bases[a.overlay_name] += 0   # register name
            self.bases["overlay:" + a.overlay_name] += 1
        self.prev = d
        self.prev_base = a.base
        self.prev_overlay = a.overlay_name
        self.prev_utt = a._utt


# ---------------------------------------------------------------------------
# lip-sync checks on one reply
# ---------------------------------------------------------------------------

_ONES = "zero one two three four five six seven eight nine".split()
_UNITS_RAW = {"mg", "ml", "gb", "mbps", "tsp", "km", "kg", "cm"}


def _ref_int(n):
    return PR.number_words(n)


def reference_expansion(tok):
    """An independent idea of what a person would SAY for a numeric token.
    Returns None if the token has no digits. Indian lakh grouping and
    fractions are read the Indian-English way."""
    t = tok.strip(".,!?;:()\"'")
    if not re.search(r"\d", t):
        return None
    out = []
    if t[:1] in "₹":
        # FIXER NOTE (round 5): money with two decimals is read the way it is
        # spoken - "ninety nine rupees ninety nine paise" - per the user's
        # decision; "point nine nine" on a price is the misreading.
        m = re.fullmatch(r"₹(\d[\d,]*)\.(\d{2})", t)
        if m:
            p = int(m.group(2))
            return _ref_int(int(m.group(1).replace(",", ""))) + ["rupees"] + (
                _ref_int(p) + ["paise"] if p else [])
        out.append("rupees")
        t = t[1:]
    # FIXER NOTE (round 3): the reference now knows 24-hour times, dates,
    # decimal percentages and PIN codes, which it used to wave through or
    # read wrongly itself (see VERIFY_ROUND_3 section 3). Expectations in
    # conversations.py are untouched; this is the checker's own reading.
    m = re.fullmatch(r"(\d{1,2}):(\d{2})", t)
    if m and 13 <= int(m.group(1)) <= 23:
        h, mi = int(m.group(1)) - 12, int(m.group(2))
        return out + _ref_int(h) + ([] if mi == 0 else
                                    (["oh"] + _ref_int(mi) if mi < 10 else _ref_int(mi))) + ["pee", "em"]
    if m:
        h, mi = int(m.group(1)), int(m.group(2))
        return out + _ref_int(h) + (["oh", "clock"] if mi == 0 else
                                   (["oh"] + _ref_int(mi) if mi < 10 else _ref_int(mi)))
    m = re.fullmatch(r"(\d{1,2})/(\d{1,2})(/\d{2,4})?", t)
    if m and 1 <= int(m.group(2)) <= 12 and 1 <= int(m.group(1)) <= 31 and (
            m.group(3) or int(m.group(1)) >= int(m.group(2)) > 0 and int(m.group(1)) > 1
            or m.group(2).startswith("0")):
        return ["DATE", t, _MONTHS[int(m.group(2)) - 1]]
    m = re.fullmatch(r"(\d+)/(\d+)", t)
    if m:
        return ["FRACTION", t]          # "half", "three quarters", "seven eighths"
    m = re.fullmatch(r"\d{1,2},\d{2},\d{3}", t)
    if m:
        return ["LAKH", t]              # ₹1,25,000 is "one lakh twenty five thousand"
    m = re.fullmatch(r"(\d[\d,]*)\.(\d+)", t)
    if m:
        return out + _ref_int(int(m.group(1).replace(",", ""))) + ["point"] + \
            [_ONES[int(c)] for c in m.group(2)]
    m = re.fullmatch(r"(\d[\d,]*)(?:\.(\d+))?%", t)
    if m:
        return out + _ref_int(int(m.group(1).replace(",", ""))) + (
            ["point"] + [_ONES[int(c)] for c in m.group(2)] if m.group(2) else []) + ["percent"]
    m = re.fullmatch(r"(\d+)(st|nd|rd|th)", t)
    if m:
        return None   # trust ordinals; not under test here
    m = re.fullmatch(r"\d[\d,]*", t)
    if m:
        n = int(t.replace(",", ""))
        if len(t) == 4 and 1100 <= n <= 2099:
            return ["YEAR_OR_NUMBER", t]   # ambiguous; checked by context below
        if len(t) == 6 and "," not in t and not out and t[0] != "0":
            return ["PIN", t]              # a bare six-digit number is a PIN code
        return out + _ref_int(n)
    return ["OTHER", t]


_NUMBER_WORDS = {"zero", "one", "two", "three", "four", "five", "six", "seven", "eight",
                 "nine", "ten", "eleven", "twelve", "thirteen", "fourteen", "fifteen",
                 "sixteen", "seventeen", "eighteen", "nineteen", "twenty", "thirty",
                 "forty", "fifty", "sixty", "seventy", "eighty", "ninety", "hundred",
                 "thousand", "lakh", "crore"}
_MONTHS = ["january", "february", "march", "april", "may", "june", "july",
           "august", "september", "october", "november", "december"]
_MONEY = re.compile(r"[₹$]|\b(rs\.?|inr|rupees?|loan|lakhs?|salary|price|cost|emi|"
                    r"budget|fees?|paid|pay|income|ctc|amount|deposit|balance)\b", re.I)


def _contains(seq, sub):
    n = len(sub)
    return any(seq[i:i + n] == sub for i in range(len(seq) - n + 1))


def whole_text_number_issues(text):
    """FIXER NOTE (round 3): readings that depend on the words AROUND a
    number - a phone number split by a space, "1.5L" next to a loan, "1 tsp" -
    cannot be judged one token at a time, so they are checked on the whole
    sentence here."""
    issues = []
    got = [w.lower() for w in PR.normalise(text) if w not in ".,!?;:"]
    for m in re.finditer(r"(?<![\d,.])(\+?\d{2,5})((?: \d{3,5}){1,3})(?![\d,]|\.\d)", text):
        digits = re.sub(r"\D", "", m.group(0))
        if len(digits) >= 10 and not _contains(got, [_ONES[int(c)] for c in digits]):
            issues.append(("phone_not_digit_by_digit", m.group(0), got))
    if _MONEY.search(text):
        for m in re.finditer(r"\b\d+(?:\.\d+)?L\b", text):
            if "lakh" not in got or "litres" in got:
                issues.append(("lakh_read_as_litres", m.group(0), got))
    for m in re.finditer(r"\b1 (tsp|tbsp|kg|km|cm|mg|ml|hr|min)\b", text):
        unit = PR._UNITS[m.group(1)][-1]
        if _contains(got, ["one", unit]) and unit.endswith("s"):
            issues.append(("plural_after_one", m.group(0), got))
    return issues


def lipsync_check(tr, text):
    issues = whole_text_number_issues(text)
    if tr.skipped:
        issues.append(("skipped", tr.skipped))
    digit_words = [w for w in tr.words if re.search(r"\d", w)]
    if digit_words:
        issues.append(("digits_unexpanded", digit_words))
    # FIXER NOTE (round 5): the checker used to look only at the track's
    # words, so a code like "Q3", a split ordinal ("one st"), a roman numeral
    # after a name or "Dr." read as a full stop all passed as clean. Now any
    # token with a digit (or a letter+digit mix) left in the normalised
    # output is flagged, and so are those split / dropped forms.
    said = PR.normalise(text)
    left = [w for w in said if re.search(r"\d", w)]
    if left and not digit_words:
        issues.append(("digits_unexpanded", left))
    low_said = [w.lower() for w in said]
    for i, w in enumerate(low_said[1:], 1):
        if w in ("st", "nd", "rd", "th") and low_said[i - 1] in _NUMBER_WORDS:
            issues.append(("ordinal_suffix_split", low_said[i - 1] + " " + w))
        if w == "." and low_said[i - 1] in ("doctor", "mister", "missus"):
            issues.append(("abbreviation_ends_sentence", said[i - 1]))
    roman = [w for w in said if re.fullmatch(r"(II|III|IV|VI|VII|VIII|IX|XI|XII|XIV|XV|XVI)", w)]
    if roman:
        issues.append(("roman_unexpanded", roman))
    if re.search(r"(?<![\w.,%)])-\d", text) and "minus" not in low_said:
        issues.append(("minus_dropped", text))
    raw_units = [w for w in tr.words if w.lower() in _UNITS_RAW]
    if raw_units:
        issues.append(("unit_unexpanded", raw_units))
    # semantic number check against an independent reading
    for tok in text.split():
        ref = reference_expansion(tok)
        if ref is None:
            continue
        got = PR.normalise(tok)
        got = [w for w in got if w not in ".,!?;:"]
        # FIXER NOTE: these three branches used to append the issue
        # unconditionally, without ever looking at `got`, so a correct reading
        # was still counted as a failure. They now check the actual output
        # against what the label says is wrong.
        if ref[0] == "FRACTION":
            if "slash" in got or any(re.search(r"\d", w) for w in got):
                issues.append(("fraction_read_as_slash", tok, got))
        elif ref[0] == "LAKH":
            if "lakh" not in got:
                issues.append(("indian_grouping_read_western", tok, got))
        elif ref[0] == "YEAR_OR_NUMBER":
            ctx = text.lower()
            n = int(ref[1])
            hi, lo = divmod(n, 100)
            as_year = _ref_int(hi) + (["hundred"] if lo == 0 else
                                      ["oh"] + _ref_int(lo) if lo < 10 else _ref_int(lo))
            if (not re.search(r"(in|since|built in|from)\s+" + re.escape(ref[1]), ctx)
                    and [w.lower() for w in got] == as_year):
                issues.append(("number_read_as_year", tok, got))
        elif ref[0] == "DATE":
            if ref[2] not in got or "slash" in got or "by" in got:
                issues.append(("date_misread", tok, got))
        elif ref[0] == "PIN":
            if [w.lower() for w in got] != [_ONES[int(c)] for c in ref[1]]:
                issues.append(("pin_not_digit_by_digit", tok, got))
        elif ref[0] == "OTHER":
            if got == [tok.strip(".,!?;:")] or any(re.search(r"\d", w) for w in got):
                issues.append(("numeric_token_unhandled", tok, got))
        elif [w.lower() for w in got] != ref:
            issues.append(("number_misread", tok, got, ref))
    if tr.words:
        spw = tr.duration / len(tr.words)
        if not 0.15 <= spw <= 0.9:
            issues.append(("seconds_per_word", round(spw, 3)))
    for c in tr.cues:
        if c.shape not in V.SHAPES:
            issues.append(("bad_shape", c.shape))
    for a, b in zip(tr.cues, tr.cues[1:]):
        if b.t0 < a.t0 - 1e-9 or a.t1 < a.t0:
            issues.append(("cue_order", a.t0, b.t0))
            break
    # Devanagari words must each make at least one non-rest shape
    for w in text.split():
        # FIXER NOTE: the danda (U+0964/5) is punctuation, not a word; it used
        # to be counted as a "silent Devanagari word" on its own.
        core = re.sub(r"[^ऀ-ॿ]|[\u0964\u0965]", "", w)
        if core and not [s for s in V.word_shapes(core) if s not in "X"]:
            issues.append(("devanagari_silent", w))
    return issues


# ---------------------------------------------------------------------------
# run one conversation
# ---------------------------------------------------------------------------

def region_point(anim, name):
    for r in anim.regions:
        if r.name == name:
            return r.cx, r.cy
    return anim.r.w * 0.5, anim.r.h * 0.95   # panel: bottom centre


def do_touch(app, rec, kind, region):
    a = app.anim
    x, y = region_point(a, region)
    out = []
    if kind == "poke":
        app._wake(gesture=True); out.append(a.touch_down(x, y)); rec.step(0.1); a.touch_up(x, y)
    elif kind == "hold":
        app._wake(gesture=True); out.append(a.touch_down(x, y)); rec.step(1.2); a.touch_up(x, y)
    elif kind == "stroke":
        app._wake(gesture=True); out.append(a.touch_down(a.r.w * 0.2, y))
        for i in range(12):
            a.touch_move(a.r.w * (0.2 + 0.05 * i), y); rec.step(0.04)
        a.touch_up(a.r.w * 0.8, y)
    elif kind == "poke5":
        for _ in range(5):
            app._wake(gesture=True); out.append(a.touch_down(x, y)); rec.step(0.08)
            a.touch_up(x, y); rec.step(0.17)
    rec.step(0.3)
    return out


def run_conversation(conv, idx):
    app, clock = fresh_app(1000 + idx)
    rec = Recorder(app, clock, conv["id"])
    rec.step(1.0)
    turns = conv["turns"]
    results = {"id": conv["id"], "length": conv["length"], "user": [], "replies": [],
               "events": [], "dropped": []}
    utt_end = None    # clock time the current homebot utterance finishes
    i = 0
    while i < len(turns):
        t = turns[i]
        nxt = turns[i + 1] if i + 1 < len(turns) else None
        k = t["kind"]
        if k == "user":
            was_asleep = app.asleep
            base_asleep = app.anim.base == "asleep"
            speaking_before = app.anim.speaking
            app._wake()                       # first key press
            rec.step(0.3)                     # typing tail
            tr0 = _realtime.perf_counter()
            name, level, amt, why = R.read(t["text"])
            read_t = _realtime.perf_counter() - tr0
            app._submit(t["text"])
            got_base = app.anim.base
            rec.step(DT)                      # brain thread emits "thinking" ~1 frame later
            results["user"].append({
                "text": t["text"], "got": name, "level": level, "why": why,
                "expected": sorted(t["expected"]), "exp_level": sorted(t["level"]),
                "ok": name in t["expected"], "level_ok": level in t["level"],
                "interrupt": t["at"] is not None, "busy": t["busy"],
                "speaking_before": speaking_before,
                "speaking_after": app.anim.speaking,
                "woke_from_flag": was_asleep, "woke_from_base_asleep": base_asleep,
                "base_after_submit": got_base, "read_s": read_t})
            if app.mind.dropped and app.mind.dropped[-1] == t["text"]:
                results["dropped"].append(t["text"])
            # if the next homebot turn is not for this line, still idle a bit
            if not nxt or nxt["kind"] != "homebot":
                if not (nxt and nxt.get("busy")):
                    rec.step(0.8)
                    # unscripted: no reply is spoken, but the brain is not
                    # left 'busy' forever (that would fake drops)
                    app.mind.busy = False
        elif k == "homebot":
            for s in t["states"]:
                sname = STATE_NAME[s]
                app._on_state(sname)
                rec.step(STATE_GAP.get(sname, 0.0) or DT)
            style = E.talk(app.anim.base)
            base_at_speech = app.anim.base
            v0 = _realtime.perf_counter()
            tr = V.VisemeTrack(t["text"], style.rate, style.crisp)
            vt = _realtime.perf_counter() - v0
            replaced = app.anim.speaking
            app._on_reply(t["text"])
            app.mind.busy = False
            utt = app.anim._utt
            dur = utt.duration
            issues = lipsync_check(utt, t["text"])
            # step through the utterance (or only part of it, if interrupted)
            frac = nxt.get("at") if nxt else None
            span = dur * frac if frac is not None else dur + 0.5
            mo_max, ma_min, ma_max, inv = 0.0, 9.0, 0.0, 0
            n = max(1, int(round(span / DT)))
            for _ in range(n):
                before_inv = rec.invisible_speech
                rec.frame()
                p = app.anim.current
                if app.anim._utt is utt:
                    pp = rec.prev
                    mo_max = max(mo_max, pp["mouth_open"])
                    ma_min = min(ma_min, pp["mouth_alpha"])
                    ma_max = max(ma_max, pp["mouth_alpha"])
                inv += rec.invisible_speech - before_inv
            if frac is None:
                rec.step(BETWEEN_TURNS)
            results["replies"].append({
                "text": t["text"], "states": t["states"], "base": base_at_speech,
                "duration": dur, "words": len(utt.words), "issues": issues,
                "mouth_open_max": mo_max, "mouth_alpha_min": ma_min,
                "mouth_alpha_max": ma_max, "invisible_frames": inv,
                "replaced_previous": replaced, "viseme_s": vt,
                "base_after_hold": app.anim.base, "interrupted_at": frac})
        elif k == "touch":
            speaking = app.anim.speaking
            utt = app.anim._utt
            reacts = do_touch(app, rec, t["touch"], t["region"])
            results["events"].append({"kind": "touch", "touch": t["touch"],
                                      "region": t["region"], "reacts": reacts,
                                      "during_speech": speaking,
                                      "speech_survived": speaking and app.anim._utt is utt,
                                      "base_after": app.anim.base})
            if t["at"] is not None and nxt and nxt.get("at") is not None:
                pass
            elif speaking:
                rec.step(3.0)
        elif k == "quiet":
            rec.step(t["seconds"])
            results["events"].append({"kind": "quiet", "seconds": t["seconds"],
                                      "asleep_flag": app.asleep, "base": app.anim.base})
        elif k == "play":
            app._wake()
            app._submit("!" + t["name"])
            d = sum(h for _, h, _ in E.sequence(t["name"]))
            nxt_user = nxt and nxt["kind"] == "user"
            rec.step(d * 0.5 if nxt_user else d + 0.5)
            results["events"].append({"kind": "play", "name": t["name"],
                                      "playing_when_next": app.anim.playing,
                                      "base": app.anim.base})
        i += 1
    rec.step(12.0)
    results["end_base"] = app.anim.base
    results["end_asleep_flag"] = app.asleep
    return results, rec


# ---------------------------------------------------------------------------
# targeted experiments (c, e, f, g)
# ---------------------------------------------------------------------------

SENT = "Your reminder is at 7:30, Aaji's tablet, 500 mg, after dinner."


def mouth_pixels(app, p):
    """Lit pixels in the mouth band of a rendered frame, minus the same frame
    with the mouth removed - i.e. what the viewer actually sees of the mouth."""
    surf = app.renderer.render(p).copy()     # render() reuses one surface
    q = p.copy(); q.mouth_alpha = 0.0
    surf0 = app.renderer.render(q).copy()
    r = app.renderer
    y0, y1 = int(r.mouth_y - r.h * 0.12), int(r.mouth_y + r.h * 0.25)
    x0, x1 = int(r.w * 0.25), int(r.w * 0.75)
    a = pygame.surfarray.pixels3d(surf)[x0:x1, y0:y1].astype("int32")
    b = pygame.surfarray.pixels3d(surf0)[x0:x1, y0:y1].astype("int32")
    return int(((abs(a - b).sum(axis=2)) > 60).sum())


def exp_mouthless():
    out = {}
    for pose in MOUTHLESS + ("answering", "rest", "sad"):
        for path in ("set", "read_intensity"):
            app, clock = fresh_app(7)
            rec = Recorder(app, clock, "mouthless")
            if path == "set":
                app.anim.set(pose)
            else:
                app.anim.set(pose, intensity=E.level_amount(pose, E.MID))
            rec.step(1.5)
            base_px = mouth_pixels(app, app.anim.update())
            dur = app.anim.speak(SENT)
            mo, ma, px = 0.0, 1.0, 0
            vis_frames, frames, open_frames = 0, 0, 0
            k = 0
            while app.anim.speaking:
                rec.frame()
                pp = rec.prev
                frames += 1
                st_ = clock.now - app.anim._utt_t0 if app.anim._utt else None
                vo = app.anim._utt.mouth(st_)[0] if app.anim._utt else 0
                if vo > 0.3:
                    open_frames += 1
                mo = max(mo, pp["mouth_open"]); ma = min(ma, pp["mouth_alpha"])
                if k % 5 == 0:
                    pp_ = app.anim.update(); clock.now += 0  # same time, render it
                    m = mouth_pixels(app, pp_)
                    px = max(px, m)
                    if m > base_px + 20:
                        vis_frames += 1
                k += 1
            out[f"{pose}/{path}"] = {"duration": round(dur, 2), "mouth_open_max": round(mo, 3),
                                     "mouth_alpha_min": round(ma, 3), "rest_mouth_px": base_px,
                                     "speech_mouth_px_max": px,
                                     "sampled_frames_mouth_visibly_moving": vis_frames,
                                     "sampled_frames": (k + 4) // 5,
                                     "head_bob_px_max": None}
    return out


def exp_mood_change():
    """speak() docstring: 'if the mood changes mid-sentence, the same words
    finish being spoken differently'. Answering -> sad at 40%, as when a user
    types 'I feel sad' while he talks."""
    res = {}
    for new_mood, user_line in (("sad", "I feel sad"), ("tender", "thank you"),
                                ("angry", "this is so stupid")):
        app, clock = fresh_app(11)
        rec = Recorder(app, clock, "mood")
        app.anim.set("answering"); rec.step(1.0)
        text = ("Tomorrow in Pune it will be thirty one degrees with a forty percent "
                "chance of rain in the evening so carry an umbrella after five")
        dur = app.anim.speak(text)
        before, after, jumps = [], [], []
        sw = dur * 0.4
        n_before = int(sw / DT)
        for _ in range(n_before):
            rec.frame(); before.append(rec.prev)
        prev = rec.prev
        name, level, amt, _ = R.read(user_line)
        app._submit(user_line)
        rec.frame()
        first = rec.prev
        sw_jump = {k: round(first[k] - prev[k], 3) for k in ("mouth_open", "shift_y", "glow",
                                                             "mouth_alpha", "mouth_w")}
        gone_at = None
        while app.anim.speaking:
            rec.frame(); after.append(rec.prev)
            if gone_at is None and rec.prev["mouth_alpha"] < 0.02:
                gone_at = round(len(after) * DT, 2)
        res[new_mood] = {
            "mouth_invisible_after_s": gone_at,
            "speech_left_when_mouth_vanished_s": (round(len(after) * DT - gone_at, 2)
                                                  if gone_at is not None else None),
            "read_as": name, "still_speaking_after_submit": bool(after),
            "duration_unchanged": True,
            "mouth_open_peak_before": round(max(f["mouth_open"] for f in before), 3),
            "mouth_open_peak_after": round(max([f["mouth_open"] for f in after] or [0]), 3),
            "mouth_alpha_after_min": round(min([f["mouth_alpha"] for f in after] or [1]), 3),
            "shift_y_min_before": round(min(f["shift_y"] for f in before), 2),
            "shift_y_max_after": round(max([f["shift_y"] for f in after] or [0]), 2),
            "first_frame_delta": sw_jump,
            "jumps_over_threshold": [j for j in rec.jumps if not j[4].startswith("legit")][:6]}
    return res


def exp_interrupt_reply():
    """A new reply arriving while the previous one is still being said."""
    app, clock = fresh_app(13)
    rec = Recorder(app, clock, "replace")
    app._on_state("speaking"); rec.step(0.4)
    app._on_reply("Tomorrow in Pune it will be warm and sunny with a light breeze all day long.")
    old = app.anim._utt
    # find a frame where the mouth is wide open, around 40%
    rec.step(old.duration * 0.4)
    while old.mouth(clock.now - app.anim._utt_t0)[0] < 0.5:
        rec.frame()
    before = rec.prev["mouth_open"]
    app._submit("wait, I meant Mumbai")
    sub_speaking = app.anim.speaking
    rec.frame()
    app._on_state("thinking"); rec.step(0.9)
    still = app.anim._utt is old
    mo_before_reply = rec.prev["mouth_open"]
    app._on_reply("Mumbai: thirty three degrees, humid.")
    rec.frame()
    return {"mouth_open_when_user_typed": round(before, 3),
            "speech_continued_after_user_turn": sub_speaking,
            "old_utterance_still_running_after_thinking": still,
            "mouth_open_just_before_new_reply": round(mo_before_reply, 3),
            "mouth_open_first_frame_of_new_reply": round(rec.prev["mouth_open"], 3),
            "no_hush_called": True,
            "jumps": [j for j in rec.jumps if not j[4].startswith("legit")][:8]}


def exp_sequences():
    res = {}
    # 1. new user turn stops a sequence
    app, clock = fresh_app(17); rec = Recorder(app, clock, "seq")
    app._submit("!slow_burn"); rec.step(1.5)
    app._submit("what's the time?")
    rec.step(4.0)
    res["user_turn_stops_sequence"] = {"playing": app.anim.playing, "base": app.anim.base}
    # 2. brain state arriving during a sequence (e.g. '!' typed while mind busy)
    app, clock = fresh_app(17); rec = Recorder(app, clock, "seq")
    app._submit("!nod_off"); rec.step(0.5)
    app._on_state("thinking"); rec.step(0.3)
    b1 = app.anim.base
    rec.step(1.2)
    app._on_state("speaking"); app._on_reply("Here is your answer.")
    rec.step(4.0)
    res["brain_state_during_sequence"] = {"base_right_after_thinking": b1,
                                          "base_after_reply": app.anim.base,
                                          "trace": rec.base_trace,
                                          "still_playing": app.anim.playing}
    # 3. touch during nod_off: wake, then does the sequence put it back to sleep?
    app, clock = fresh_app(17); rec = Recorder(app, clock, "seq")
    app._submit("!nod_off"); rec.step(4.2)
    b = app.anim.base
    app._wake(gesture=True)
    r = app.anim.touch_down(*region_point(app.anim, "forehead"))
    rec.step(0.1); app.anim.touch_up(0, 0)
    rec.step(6.0)
    res["touch_during_nod_off"] = {"base_when_touched": b, "reaction": r,
                                   "base_6s_later": app.anim.base,
                                   "app_asleep_flag": app.asleep,
                                   "trace": rec.base_trace}
    return res


def exp_sleep_wake():
    res = {}
    # A: plain idle from rest
    app, clock = fresh_app(19); rec = Recorder(app, clock, "sleep")
    t_start = clock.now
    slept_at = None
    for _ in range(int(90 / DT)):
        rec.frame()
        if app.asleep and slept_at is None:
            slept_at = clock.now - t_start
            overlay = app.anim.overlay_name
    rec_beat = app.anim._beat
    res["idle_to_sleep"] = {"asleep_after_s": round(slept_at, 2), "overlay_at_sleep": overlay,
                            "final_base": app.anim.base,
                            "asleep_beat_dur_used": rec_beat.dur,
                            "asleep_duration_requested": 1.8,
                            "trace": rec.base_trace[-4:],
                            "blinks_while_asleep": None}
    # breathing while asleep: glow range
    gl = []
    for _ in range(int(10 / DT)):
        rec.frame(); gl.append(rec.prev["glow"])
    res["idle_to_sleep"]["asleep_glow_range"] = (round(min(gl), 3), round(max(gl), 3))
    # wake by keypress, user types slowly, base during typing
    app._wake(); rec.step(0.1)
    after_key = (app.anim.base, app.anim.overlay_name)
    rec.step(3.0)
    during_typing = app.anim.base
    app._submit("what time is it?"); rec.step(DT)
    res["wake_by_key"] = {"base_overlay_after_key": after_key,
                          "base_while_typing_3s": during_typing,
                          "base_after_submit": app.anim.base,
                          "jumps": [j for j in rec.jumps if not j[4].startswith("legit")][-6:]}
    # B: wake by touch, then nobody types: what does the face do for 60s?
    app, clock = fresh_app(23); rec = Recorder(app, clock, "sleep")
    rec.step(80)
    app._wake(gesture=True)
    r = app.anim.touch_down(*region_point(app.anim, "panel"))
    rec.step(0.1); app.anim.touch_up(0, 0)
    marks = {}
    for s in (1, 5, 20, 60):
        while clock.now < (rec.clock.now if False else 0):
            pass
    t0 = clock.now
    for target in (1, 5, 20, 60, 80):
        rec.step(target - (clock.now - t0))
        marks[f"{target}s"] = (app.anim.base, app.asleep)
    res["wake_by_touch_then_silence"] = {"reaction": r, "marks": marks}
    # C: "Goodnight" through the brain's sleep state (OfflineMind BYE path)
    app, clock = fresh_app(29); rec = Recorder(app, clock, "sleep")
    app._submit("good night homebot")
    rec.step(DT)
    app._on_state("thinking"); rec.step(0.9)
    app._on_state("sleep"); rec.step(DT)
    app._on_reply("Goodnight."); app.mind.busy = False
    style = E.talk(app.anim.base)
    rec.step(3)
    marks = {"after_reply": (app.anim.base, app.asleep, style.open_max)}
    yawned_at = None
    t0 = clock.now
    for _ in range(int(100 / DT)):
        rec.frame()
        if app.anim.overlay_name == "yawn" and yawned_at is None:
            yawned_at = round(clock.now - t0 + 3, 1)
    marks["yawn_overlay_on_already_sleeping_face_at_s"] = yawned_at
    app._wake(); rec.step(0.1)
    marks["key_after_brain_sleep"] = (app.anim.base, app.anim.overlay_name)
    res["brain_sleep_state"] = marks
    # D: long thinking keeps it awake?  mind.busy refreshes last_activity
    app, clock = fresh_app(31); rec = Recorder(app, clock, "sleep")
    app._submit("plan a trip to Kerala"); rec.step(DT)
    app._on_state("thinking"); rec.step(100)
    res["long_brain_call"] = {"asleep": app.asleep, "base": app.anim.base}
    return res


def exp_non_answer_holds():
    """After a reply in a state other than answering/delight, does the face
    ever relax back to rest?"""
    res = {}
    for chain in (["thinking", "speaking"], ["thinking", "refused"], ["thinking", "stuck"],
                  ["thinking", "tool"], ["thinking", "unknown_speaker"], ["thinking", "success"]):
        app, clock = fresh_app(37); rec = Recorder(app, clock, "hold")
        app._submit("what is the weather?"); rec.step(DT)
        for s in chain:
            app._on_state(s); rec.step(0.5)
        speak_face = app.anim.base
        app._on_reply("I cannot look that up yet."); app.mind.busy = False
        rec.step(10)
        b10 = app.anim.base
        rec.step(50)
        res[">".join(chain)] = {"spoke_in": speak_face, "base_10s": b10, "base_60s": app.anim.base}
    return res


def exp_touch_during_speech():
    res = {}
    for region in ("mouth", "cheek_left", "forehead"):
        app, clock = fresh_app(41); rec = Recorder(app, clock, "touch")
        app._on_state("speaking"); rec.step(0.4)
        app._on_reply("At eight there is cricket and at nine thirty a Marathi movie on Zee.")
        utt = app.anim._utt
        rec.step(1.0)
        app._wake(gesture=True)
        r = app.anim.touch_down(*region_point(app.anim, region))
        mo = []
        for _ in range(int(0.9 / DT)):
            rec.frame(); mo.append(rec.prev["mouth_open"])
        app.anim.touch_up(0, 0)
        res[region] = {"reaction": r, "speech_continued": app.anim._utt is utt,
                       "mouth_open_min_during_flash": round(min(mo), 3),
                       "mouth_open_max_during_flash": round(max(mo), 3),
                       "talk_style_used": app.anim.base}
    # five pokes during speech
    app, clock = fresh_app(43); rec = Recorder(app, clock, "touch")
    app._on_state("speaking"); rec.step(0.4)
    app._on_reply("At eight there is cricket and at nine thirty a Marathi movie on Zee.")
    utt = app.anim._utt
    reacts = []
    for _ in range(5):
        app._wake(gesture=True)
        reacts.append(app.anim.touch_down(*region_point(app.anim, "mouth"))); rec.step(0.1)
        app.anim.touch_up(0, 0); rec.step(0.15)
    res["poke5_during_speech"] = {"reacts": reacts, "speech_continued": app.anim._utt is utt}
    return res


def exp_real_thread_latency():
    """With the REAL mind.Mind (offline, real threads, real clock): does the
    read() face ever reach a frame before the brain's 'thinking' replaces it?"""
    fresh_app(0)
    APP.time = _realtime
    AN.time = _realtime
    app = _APP
    app.anim = AN.Animator(app.renderer)
    seen = Counter()
    lat = []
    texts = ["I'm so happy today!", "I am scared", "thank you", "you are useless",
             "Mama passed away this morning"]
    for i in range(60):
        app.mind = Mind(app._on_state, app._on_reply)
        t0 = _realtime.perf_counter()
        app._submit(texts[i % len(texts)])
        # what the next draw() would see, at the earliest possible moment
        seen[app.anim.base] += 1
        while app.mind.busy:
            _realtime.sleep(0.0005)
        lat.append(_realtime.perf_counter() - t0)
    expected = Counter(R.read(t)[0] for t in texts for _ in range(12))
    return {"base_seen_immediately_after_submit": dict(seen),
            "read_faces_requested": dict(expected),
            "offline_round_trip_ms_median": round(st.median(lat) * 1000, 2)}


def exp_offline_pass(convs):
    """What an offline family sees: OfflineMind's real states and replies."""
    om = OfflineMind()
    random.seed(5)
    faces, replies = Counter(), Counter()
    examples = []
    for c in convs:
        for t in c["turns"]:
            if t["kind"] != "user":
                continue
            states = []
            reply = om.ask(t["text"], on_state=states.append)
            face = E.BRAIN_STATES.get(states[-1], "rest")
            faces[face] += 1
            replies[reply] += 1
            if len(examples) < 6 and states[-1] in ("tool", "sleep"):
                examples.append((t["text"], states, reply, face))
    return {"speaking_face": dict(faces), "distinct_replies": len(replies),
            "top_replies": replies.most_common(4), "examples": examples}


# ---------------------------------------------------------------------------

def main():
    out_dir = os.environ.get("CONV_OUT")
    print("real-thread latency ...", flush=True)
    real = exp_real_thread_latency()

    all_res, recs = [], []
    t0 = _realtime.perf_counter()
    for i, c in enumerate(CONVERSATIONS):
        r, rec = run_conversation(c, i)
        all_res.append(r); recs.append(rec)
    sim_s = _realtime.perf_counter() - t0

    # ---- a. accuracy
    print("\n=== a. expression / level accuracy (user turns) ===")
    by = defaultdict(lambda: [0, 0, 0])
    for r in all_res:
        for u in r["user"]:
            b = by[r["length"]]; b[0] += 1; b[1] += u["ok"]; b[2] += u["level_ok"]
            a = by["ALL"]; a[0] += 1; a[1] += u["ok"]; a[2] += u["level_ok"]
    for k in ("short", "medium", "long", "ALL"):
        n, ok, lv = by[k]
        print(f"  {k:6} turns={n:3}  expr={ok}/{n} ({ok/n:.0%})  level={lv}/{n} ({lv/n:.0%})")
    miss = [(r["id"], u) for r in all_res for u in r["user"] if not u["ok"]]
    why_c = Counter(u["why"] or ("<?>" if u["got"] == "curious" else "<default>") for _, u in miss)
    got_c = Counter(u["got"] for _, u in miss)
    print("  misses by chosen expression:", got_c.most_common())
    print("  misses by deciding phrase:", why_c.most_common(25))
    lvl_conf = Counter(("/".join(u["exp_level"]), u["level"]) for r in all_res for u in r["user"]
                       if not u["level_ok"])
    print("  level confusions (expected -> got):", lvl_conf.most_common())
    deva = [u for r in all_res for u in r["user"] if re.search(r"[ऀ-ॿ]", u["text"])]
    print(f"  Devanagari user turns: {len(deva)}, correct {sum(u['ok'] for u in deva)}, "
          f"chosen {Counter(u['got'] for u in deva)}")

    # ---- b. lip sync
    print("\n=== b. lip sync ===")
    reps = [x for r in all_res for x in r["replies"]]
    clean = [x for x in reps if not x["issues"]]
    print(f"  replies={len(reps)}  clean={len(clean)} ({len(clean)/len(reps):.0%})")
    ic = Counter(i[0] for x in reps for i in x["issues"])
    print("  issue counts:", ic.most_common())
    for kind in ic:
        ex = [(x["text"][:70], [i for i in x["issues"] if i[0] == kind][0]) for x in reps
              if any(i[0] == kind for i in x["issues"])][:3]
        for e in ex:
            print(f"    [{kind}] {e[0]!r} -> {e[1][1:]}")
    spw = [x["duration"] / max(1, x["words"]) for x in reps]
    print(f"  seconds/word: min {min(spw):.3f} median {st.median(spw):.3f} max {max(spw):.3f}")
    dv = [x for x in reps if re.search(r"[ऀ-ॿ]", x["text"])]
    print(f"  Devanagari replies: {len(dv)}, with issues: {sum(1 for x in dv if x['issues'])}")
    probes = {}
    for s in ["७:३० वाजता", "₹१,२५० झाले", "₹1,250.50", "₹2.5 lakh", "10am", "7:30pm",
              "Rs.500", "2-3 days", "98201-23456", "45°C", "₹1,00,000", "call 1906", "5 km"]:
        tr = V.VisemeTrack(s)
        probes[s] = {"normalise": PR.normalise(s) if not re.search(r"[ऀ-ॿ]", s) else "(deva)",
                     "skipped": tr.skipped, "words": tr.words}
    print("  extra probes:")
    for k, v in probes.items():
        print(f"    {k!r}: {v}")

    # ---- c. speech on the current expression
    print("\n=== c. speech on top of the expression ===")
    base_c = Counter(x["base"] for x in reps)
    print("  face at reply start:", base_c.most_common())
    zero_open = [x for x in reps if x["mouth_open_max"] < 0.15]
    print(f"  replies whose mouth never opened >0.15: {len(zero_open)}",
          [(x["text"][:30], x["base"]) for x in zero_open][:5])
    inv_r = [x for x in reps if x["invisible_frames"] > 0]
    print(f"  replies with invisible-mouth speech frames: {len(inv_r)}; "
          f"frames total {sum(x['invisible_frames'] for x in reps)}")
    for x in inv_r[:6]:
        print(f"    {x['text'][:50]!r} base={x['base']} invisible={x['invisible_frames']} "
              f"alpha_min={x['mouth_alpha_min']:.2f}")
    total_speech = sum(r.speech_frames for r in recs)
    total_inv = sum(r.invisible_speech for r in recs)
    print(f"  all speech frames {total_speech}, mouthless-while-voicing {total_inv}")
    ml = exp_mouthless()
    print("  mouthless pose experiment:")
    for k, v in ml.items():
        print(f"    {k:28} {v}")

    # ---- d. frame sanity
    print("\n=== d. frame sanity ===")
    frames = sum(r.frames for r in recs)
    sanity = [s for r in recs for s in r.sanity]
    print(f"  frames={frames}  sanity violations={len(sanity)}", sanity[:5])
    jumps = [j for r in recs for j in r.jumps]
    jc = Counter((j[4] if not j[4].startswith("legit") else "legit") for j in jumps)
    print("  jumps over threshold by cause:", jc.most_common())
    jch = Counter((j[4], j[2]) for j in jumps if not j[4].startswith("legit"))
    print("  glitch jumps by (cause, channel):", jch.most_common(20))
    for cause in [c for c in jc if c != "legit"]:
        ex = [j for j in jumps if j[4] == cause]
        ex.sort(key=lambda j: -abs(j[3]))
        for j in ex[:3]:
            print(f"    [{cause}] {j[0]} t={j[1]} {j[2]} d={j[3]} resid={j[7]} {j[5]}->{j[6]}")
    legit = [j for j in jumps if j[4].startswith("legit")]
    lc = Counter((j[4], j[2]) for j in legit)
    print("  legit jumps by (cause, channel):", lc.most_common(12))
    per_conv = Counter(j[0] for j in jumps if not j[4].startswith("legit"))
    print(f"  conversations with >=1 glitch jump: {len(per_conv)}/100")
    inv = [(r.cid, r.invisible_speech) for r in recs if r.invisible_speech]
    print("  conversations with voiced-but-mouthless frames:", inv)

    # ---- e/f. transitions & interruptions
    print("\n=== e/f. transitions & interruptions ===")
    ints = [(r["id"], u) for r in all_res for u in r["user"] if u["interrupt"]]
    for cid, u in ints:
        print(f"  {cid} user-interrupt {u['text']!r}: speaking_before={u['speaking_before']} "
              f"after={u['speaking_after']} base={u['base_after_submit']}")
    rep_rep = [x for x in reps if x["replaced_previous"]]
    print(f"  replies that cut off a still-running reply: {len(rep_rep)}")
    touches = [(r["id"], e) for r in all_res for e in r["events"] if e["kind"] == "touch"]
    print(f"  touches={len(touches)}, during speech={sum(1 for _, e in touches if e['during_speech'])}, "
          f"speech survived={sum(1 for _, e in touches if e['speech_survived'])}")
    print("  touch reactions:", Counter(x for _, e in touches for x in e["reacts"]).most_common())
    drops = [(r["id"], d) for r in all_res for d in r["dropped"]]
    print(f"  user turns silently dropped by mind.busy: {len(drops)}", drops)
    mood = exp_mood_change(); print("  mood change mid-utterance:")
    for k, v in mood.items():
        print(f"    {k}: {v}")
    rr = exp_interrupt_reply(); print("  reply replaced mid-speech:", rr)
    sq = exp_sequences(); print("  sequences:")
    for k, v in sq.items():
        print(f"    {k}: {v}")
    td = exp_touch_during_speech(); print("  touch during speech:")
    for k, v in td.items():
        print(f"    {k}: {v}")
    nh = exp_non_answer_holds(); print("  face after reply, by final brain state:")
    for k, v in nh.items():
        print(f"    {k}: {v}")
    print("  real Mind threading:", real)

    # ---- g. sleep / wake
    print("\n=== g. idle / sleep / wake ===")
    sw = exp_sleep_wake()
    for k, v in sw.items():
        print(f"  {k}: {v}")
    quiets = [(r["id"], e) for r in all_res for e in r["events"] if e["kind"] == "quiet"]
    for cid, e in quiets:
        if e["seconds"] >= 75:
            print(f"  {cid} quiet {e['seconds']}s -> asleep_flag={e['asleep_flag']} base={e['base']}")
    wakes = [(r["id"], u) for r in all_res for u in r["user"]
             if u["woke_from_flag"] or u["woke_from_base_asleep"]]
    for cid, u in wakes:
        print(f"  {cid} next input {u['text']!r}: flag_asleep={u['woke_from_flag']} "
              f"base_was_asleep={u['woke_from_base_asleep']} -> {u['base_after_submit']}")
    ends = Counter(r["end_base"] for r in all_res)
    print("  face 12s after each conversation ends:", ends.most_common())

    # ---- h. variety
    print("\n=== h. variety ===")
    rep_runs, pairs = 0, 0
    for r in all_res:
        g = [u["got"] for u in r["user"]]
        for a, b in zip(g, g[1:]):
            pairs += 1; rep_runs += a == b
    print(f"  consecutive user turns with the same read() face: {rep_runs}/{pairs} "
          f"({rep_runs/max(1,pairs):.0%})")
    longest = max(((r["id"], max((len(list(gp)) for _, gp in __import__('itertools').groupby(
        [u['got'] for u in r['user']])), default=0)) for r in all_res), key=lambda x: x[1])
    print("  longest same-face run:", longest)
    read_used = Counter(u["got"] for r in all_res for u in r["user"])
    print("  read() faces used:", read_used.most_common())
    shown = set()
    for rec in recs:
        for k in rec.bases:
            shown.add(k.replace("overlay:", ""))
    never = [n for n in E.names() if n not in shown]
    never_read = [n for n in E.names() if n not in read_used]
    print(f"  shown at all (base or overlay) across 100 conversations: {len(shown & set(E.names()))}/43")
    print("  never shown:", never)
    print(f"  never chosen by read(): {len(never_read)}", never_read)
    frame_share = Counter()
    for rec in recs:
        for k, v in rec.bases.items():
            if not k.startswith("overlay:"):
                frame_share[k] += v
    tot = sum(frame_share.values())
    print("  share of all frames by base:", [(k, f"{v/tot:.1%}") for k, v in frame_share.most_common(8)])

    # ---- i. performance
    print("\n=== i. performance ===")
    ut = [t for r in recs for t in r.update_times]
    ut_sorted = sorted(ut)
    print(f"  update(): n={len(ut)} mean {st.mean(ut)*1e6:.1f} us  p99 {ut_sorted[int(len(ut)*0.99)]*1e6:.1f} us"
          f"  max {ut_sorted[-1]*1e6:.1f} us")
    rt = [u["read_s"] for r in all_res for u in r["user"]]
    vt = [x["viseme_s"] for x in reps]
    print(f"  read(): mean {st.mean(rt)*1e6:.1f} us max {max(rt)*1e6:.1f} us")
    print(f"  VisemeTrack: mean {st.mean(vt)*1e3:.3f} ms max {max(vt)*1e3:.3f} ms")
    t0 = _realtime.perf_counter()
    p = _APP.anim.update()
    for _ in range(200):
        _APP.renderer.render(p)
    print(f"  renderer.render() (640x400, laptop): {(_realtime.perf_counter()-t0)/200*1e3:.2f} ms")
    print(f"  whole simulation wall time {sim_s:.1f}s for {frames} frames")

    off = exp_offline_pass(CONVERSATIONS)
    print("\n=== offline pass (OfflineMind, real) ===")
    print(" ", off)

    if out_dir:
        os.makedirs(out_dir, exist_ok=True)
        with open(os.path.join(out_dir, "conversation_results.json"), "w") as f:
            json.dump({"convs": all_res, "mouthless": ml, "mood": mood, "replace": rr,
                       "sequences": sq, "touch": td, "holds": nh, "sleep": sw,
                       "real": real, "offline": off,
                       "jumps": [j for j in jumps if not j[4].startswith("legit")]},
                      f, ensure_ascii=False, indent=1, default=str)


if __name__ == "__main__":
    main()
