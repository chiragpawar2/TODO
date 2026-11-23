"""Run the hand-labelled expression cases plus structural checks.

    PYTHONPATH=. .venv/bin/python tests/run_expression_tests.py [--no-anim]

Writes tests/expression_results.json (raw data) and prints a summary.
This file only READS homebot/; it never patches it.
"""

from __future__ import annotations

import json
import math
import os
import re
import sys
import time
from collections import Counter, defaultdict
from dataclasses import fields

from homebot.face import expressions as E
from homebot.face import reading as R
from homebot.face.params import EyeParams, FaceParams, sanitise
from tests.expression_cases import (CASES, SUBSTRING_PROBES, SUBSTRING_CONTROL,
                                    SHADOW_PROBES, LEVEL_PROBES, LEVEL_CONTROL)

OUT = os.path.join(os.path.dirname(__file__), "expression_results.json")


# ---------------------------------------------------------------------------
# 1. single cases
# ---------------------------------------------------------------------------

def run_single():
    rows = []
    for c in CASES:
        if c["category"] == "multi":
            continue
        name, level, amt, why = R.read(c["text"])
        rows.append({
            "id": c["id"], "category": c["category"], "text": c["text"],
            "got": name, "level": level, "intensity": amt, "why": why,
            "expected": c["expected"], "expected_level": c["expected_level"],
            "expr_ok": name in c["expected"],
            "level_ok": level in c["expected_level"],
            "note": c["note"],
        })
    return rows


# ---------------------------------------------------------------------------
# 2. multi-emotion paragraphs
# ---------------------------------------------------------------------------

def split_sentences(text: str) -> list[str]:
    parts = re.findall(r"[^.!?]+[.!?]*", text)
    return [p.strip() for p in parts if p.strip()]


def run_multi():
    rows = []
    for c in CASES:
        if c["category"] != "multi":
            continue
        beats = c["expected"]
        whole = R.read(c["text"])
        whole_hit = [i for i, b in enumerate(beats) if whole[0] in b["accept"]]
        sents = split_sentences(c["text"])
        per = [R.read(s) for s in sents]
        # ordered greedy alignment of expected beats onto sentence readings
        captured, level_ok, j = [], [], 0
        for b in beats:
            hit = None
            for k in range(j, len(per)):
                if per[k][0] in b["accept"]:
                    hit = k
                    break
            if hit is not None:
                captured.append(True)
                level_ok.append(per[hit][1] in b["level"])
                j = hit + 1
            else:
                captured.append(False)
        rows.append({
            "id": c["id"], "text": c["text"], "note": c["note"],
            "beats": [b["accept"] for b in beats],
            "whole": list(whole), "whole_captured": 1 if whole_hit else 0,
            "whole_matched_beat": whole_hit[0] if whole_hit else None,
            "sentences": sents, "per_sentence": [list(p) for p in per],
            "per_captured": sum(captured), "n_beats": len(beats),
            "per_level_ok": sum(level_ok), "per_level_n": len(level_ok),
        })
    return rows


# ---------------------------------------------------------------------------
# 3. structural: coverage + shadowing
# ---------------------------------------------------------------------------

def coverage_and_shadowing():
    families = [n for n, _ in R._FAMILIES]
    reachable = set()
    shadowed = []
    for fam, keys in R._FAMILIES:
        for k in keys:
            got, why = R.expression_of(k)
            if got == fam:
                reachable.add(fam)
            else:
                # the bare keyword already loses: every text containing it
                # also contains `why`, from an earlier family -> never wins
                shadowed.append({"family": fam, "keyword": k,
                                 "always_loses_to": got, "via": why})
    # the two fallbacks
    if R.expression_of("is it?")[0] == R._QUESTION:
        reachable.add(R._QUESTION)
    if R.expression_of("xyz")[0] == R._DEFAULT:
        reachable.add(R._DEFAULT)
    unreachable = [n for n in E.names() if n not in reachable]
    dup_fam = [n for n, c in Counter(families).items() if c > 1]
    # keywords appearing in two families
    owners = defaultdict(list)
    for fam, keys in R._FAMILIES:
        for k in keys:
            owners[k].append(fam)
    dup_kw = {k: v for k, v in owners.items() if len(v) > 1}
    # where else can unreachable ones be shown? (other code paths)
    other_paths = {}
    seq_names = {s for steps in E.SEQUENCES.values() for s, _, _ in steps}
    for n in unreachable:
        paths = []
        if n in E.BRAIN_STATES.values():
            paths.append("BRAIN_STATES")
        if n in seq_names:
            paths.append("SEQUENCES")
        other_paths[n] = paths
    return {"reachable": sorted(reachable), "unreachable": unreachable,
            "other_paths": other_paths, "shadowed": shadowed,
            "dup_keywords": dup_kw, "dup_families": dup_fam,
            "n_keywords": sum(len(k) for _, k in R._FAMILIES)}


APOSTROPHE_PROBES = ["dont tell mom", "i dont understand", "whats the time",
                     "thank u", "thx", "ty", "im sad", "im so tired"]


def run_probes():
    sub = []
    for text, must_not, note in SUBSTRING_PROBES:
        r = R.read(text)
        sub.append({"text": text, "must_not": must_not, "got": r[0], "why": r[3],
                    "false_positive": r[0] == must_not and text not in SUBSTRING_CONTROL,
                    "control": text in SUBSTRING_CONTROL, "note": note})
    sh = []
    for text, exp, note in SHADOW_PROBES:
        r = R.read(text)
        sh.append({"text": text, "expected": exp, "got": r[0], "why": r[3],
                   "ok": r[0] in exp, "note": note})
    lv = []
    for a, b, note in LEVEL_PROBES:
        ra, rb = R.read(a), R.read(b)
        lv.append({"a": a, "b": b, "level_a": ra[1], "level_b": rb[1],
                   "differs": ra[1] != rb[1], "control": a in LEVEL_CONTROL, "note": note})
    ap = [{"text": t, "read": list(R.read(t))} for t in APOSTROPHE_PROBES]
    return {"substring": sub, "shadow": sh, "level": lv, "apostrophe": ap}


# ---------------------------------------------------------------------------
# 4. level integrity with the real Animator
# ---------------------------------------------------------------------------

EYE_SCALE = {"angle": 20.0, "upper_angle": 20.0, "lower_angle": 20.0}
GLOBAL_SCALE = {"tilt": 10.0, "shift_x": 10.0, "shift_y": 10.0,
                "aberration": 5.0}


def vec(p: FaceParams) -> dict:
    out = {}
    for side, e in (("L", p.left), ("R", p.right)):
        for f in fields(EyeParams):
            out[f"{side}.{f.name}"] = getattr(e, f.name) / EYE_SCALE.get(f.name, 1.0)
    for f in fields(FaceParams):
        if f.name in ("left", "right"):
            continue
        out[f.name] = getattr(p, f.name) / GLOBAL_SCALE.get(f.name, 1.0)
    return out


def pdist(a: FaceParams, b: FaceParams):
    va, vb = vec(a), vec(b)
    d = {k: abs(va[k] - vb[k]) for k in va}
    top = max(d, key=d.get)
    return math.sqrt(sum(x * x for x in d.values())), d[top], top


def broken(p: FaceParams) -> list[str]:
    """Values that are outside the range the renderer/doc says is real, on the
    UNSANITISED target, plus visual-collapse conditions."""
    bad = []
    for side, e in (("L", p.left), ("R", p.right)):
        if e.h < 0.06:
            bad.append(f"{side}.h={e.h:.3f} (eye near-gone; sanitise floor 0.02)")
        if e.w < 0.06:
            bad.append(f"{side}.w={e.w:.3f}")
        if not (0.0 <= e.upper_lid <= 1.0):
            bad.append(f"{side}.upper_lid={e.upper_lid:.3f}")
        if not (0.0 <= e.lower_lid <= 1.0):
            bad.append(f"{side}.lower_lid={e.lower_lid:.3f}")
        if e.upper_lid + e.lower_lid >= 0.95:
            bad.append(f"{side}.lids sum {e.upper_lid + e.lower_lid:.2f} (eye shut)")
        if not (0.0 <= e.radius <= 0.5):
            bad.append(f"{side}.radius={e.radius:.3f}")
        if not (-1.0 <= e.pupil_x <= 1.0) or not (-1.0 <= e.pupil_y <= 1.0):
            bad.append(f"{side}.pupil=({e.pupil_x:.2f},{e.pupil_y:.2f}) clamps")
        if e.pupil_alpha > 0.02 and e.pupil_scale < 0.3:
            bad.append(f"{side}.pupil_scale={e.pupil_scale:.2f} (pinprick)")
        if not (0.0 <= e.pupil_alpha <= 1.0):
            bad.append(f"{side}.pupil_alpha={e.pupil_alpha:.2f}")
    if abs(p.mouth_curve) > 1.0:
        bad.append(f"mouth_curve={p.mouth_curve:.2f} (doc range -1..1, not clamped)")
    if p.mouth_open > 1.2:
        bad.append(f"mouth_open={p.mouth_open:.2f} (clamped to 1.2)")
    if not (0.0 <= p.mouth_alpha <= 1.0):
        bad.append(f"mouth_alpha={p.mouth_alpha:.2f}")
    if p.tear > 1.0:
        bad.append(f"tear={p.tear:.2f} (clamped to 1.0)")
    if p.glow < 0.15:
        bad.append(f"glow={p.glow:.2f} (nearly dark)")
    return bad


def run_levels(do_render=True):
    os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
    import pygame
    pygame.init()
    pygame.display.set_mode((8, 8))
    from homebot.face.renderer import FaceRenderer
    from homebot.face.animator import Animator
    import numpy as np

    rend = FaceRenderer((400, 250))
    names = E.names()
    out = {}
    rest = E.get("rest")

    def img(p):
        s = rend.render(sanitise(p.copy()))
        return pygame.surfarray.array3d(s).astype(np.int16)

    def pixdiff(a, b):
        d = np.abs(a - b).max(axis=2)
        return float((d > 24).mean() * 100.0)   # % of pixels visibly changed

    for name in names:
        base = E.get(name)
        lv = E.levels(name)
        entry = {"levels": lv, "targets": {}, "settled_dev": {}, "structural": [],
                 "broken": {}}
        mouthless = base.mouth_alpha < 0.02
        hidden = [s for s, e in (("L", base.left), ("R", base.right)) if e.pupil_alpha < 0.02]
        for lname, amt in zip(("low", "mid", "intense"), lv):
            a = Animator(rend)
            a.set(name, intensity=amt)
            tgt = a._to.copy()
            dur = a._beat.dur
            t_end = time.monotonic() + dur * 1.25 + 0.06
            n = 0
            while time.monotonic() < t_end or n < 40:
                a.update()
                n += 1
                time.sleep(0.02)
            settled = []
            for _ in range(12):
                settled.append(a.update())
                time.sleep(0.02)
            # structural checks on every settled rendered-parameter frame
            for fr in settled:
                if mouthless and fr.mouth_alpha >= 0.02:
                    entry["structural"].append(f"{lname}: ghost mouth alpha={fr.mouth_alpha:.2f}")
                    break
            for s in hidden:
                for fr in settled:
                    e = fr.left if s == "L" else fr.right
                    if e.pupil_alpha >= 0.02:
                        entry["structural"].append(f"{lname}: {s} pupil reappears alpha={e.pupil_alpha:.2f}")
                        break
            # how far the settled frames are from the target (idle noise)
            devs = [pdist(fr, tgt)[0] for fr in settled]
            entry["settled_dev"][lname] = round(sum(devs) / len(devs), 3)
            entry["targets"][lname] = tgt
            entry["broken"][lname] = broken(tgt)

        t = entry["targets"]
        pairs = {}
        for x, y in (("low", "mid"), ("mid", "intense"), ("low", "intense")):
            l2, mx, top = pdist(t[x], t[y])
            pairs[f"{x}-{y}"] = {"l2": round(l2, 3), "max": round(mx, 3), "top": top}
        entry["pairs"] = pairs
        entry["rest_dist_mid"] = round(pdist(rest, t["mid"])[0], 3)
        entry["rest_dist_pose"] = round(pdist(rest, base)[0], 3)

        if do_render:
            im = {k: img(v) for k, v in t.items()}
            # idle noise floor for this pose: one mean-size saccade + breath
            # crest + drift crest applied to the mid target
            idl = E.idle(name)
            nz = t["mid"].copy()
            for e in (nz.left, nz.right):
                e.pupil_x += idl.gaze_mag * 0.5
            nz.glow *= 1.0 + idl.breath_depth * 0.7
            nz.shift_x += 1.3 * idl.drift * 0.7
            entry["noise_px"] = round(pixdiff(im["mid"], img(nz)), 2)
            entry["px"] = {f"{x}-{y}": round(pixdiff(im[x], im[y]), 2)
                           for x, y in (("low", "mid"), ("mid", "intense"), ("low", "intense"))}
        entry["targets"] = None  # not JSON-serialisable; drop
        entry["mouthless"] = mouthless
        entry["hidden_pupils"] = hidden
        out[name] = entry
    # LEVELS table sanity
    table = []
    for n in E.LEVELS:
        if n not in E.EXPRESSIONS:
            table.append(f"LEVELS key {n} is not an expression")
        lo, mi, hi = E.LEVELS[n]
        if not (lo <= mi <= hi):
            table.append(f"{n} levels not monotonic {E.LEVELS[n]}")
    default_users = [n for n in names if n not in E.LEVELS]
    return out, table, default_users


# ---------------------------------------------------------------------------

def speed(reps=200):
    texts = [c["text"] for c in CASES]
    t0 = time.perf_counter()
    for _ in range(reps):
        for t in texts:
            R.read(t)
    dt = time.perf_counter() - t0
    n = reps * len(texts)
    long = max(texts, key=len)
    t1 = time.perf_counter()
    for _ in range(5000):
        R.read(long)
    dl = (time.perf_counter() - t1) / 5000
    return {"calls": n, "total_s": dt, "us_per_call": dt / n * 1e6,
            "longest_chars": len(long), "us_longest": dl * 1e6}


def main():
    do_anim = "--no-anim" not in sys.argv
    single = run_single()
    multi = run_multi()
    struct = coverage_and_shadowing()
    probes = run_probes()
    sp = speed()
    res = {"single": single, "multi": multi, "structure": struct,
           "probes": probes, "speed": sp}

    ns = len(single)
    eok = sum(r["expr_ok"] for r in single)
    lok = sum(r["level_ok"] for r in single)
    both = sum(r["expr_ok"] and r["level_ok"] for r in single)
    print(f"SINGLE: {ns} cases  expression {eok}/{ns} ({eok/ns:.0%})  "
          f"level {lok}/{ns} ({lok/ns:.0%})  both {both}/{ns}")
    bycat = defaultdict(lambda: [0, 0, 0])
    for r in single:
        b = bycat[r["category"]]
        b[0] += 1; b[1] += r["expr_ok"]; b[2] += r["level_ok"]
    for k, (n, e, l) in bycat.items():
        print(f"  {k:12s} n={n:2d} expr {e}/{n}  level {l}/{n}")
    print("\nSINGLE FAILURES (expression):")
    for r in single:
        if not r["expr_ok"]:
            print(f"  {r['id']} {r['text'][:60]!r} -> {r['got']}/{r['level']} "
                  f"(why={r['why']!r}) expected {r['expected']}")
    print("\nSINGLE FAILURES (level only):")
    for r in single:
        if r["expr_ok"] and not r["level_ok"]:
            print(f"  {r['id']} {r['text'][:60]!r} -> {r['got']}/{r['level']} expected level {r['expected_level']}")

    nb = sum(m["n_beats"] for m in multi)
    wc = sum(m["whole_captured"] for m in multi)
    pc = sum(m["per_captured"] for m in multi)
    plo = sum(m["per_level_ok"] for m in multi)
    pln = sum(m["per_level_n"] for m in multi)
    full_per = sum(m["per_captured"] == m["n_beats"] for m in multi)
    first = sum(m["whole_matched_beat"] == 0 for m in multi)
    print(f"\nMULTI: {len(multi)} paragraphs, {nb} beats")
    print(f"  whole-paragraph read(): {wc}/{nb} beats ({wc/nb:.0%}); "
          f"paragraphs with any beat {wc}/{len(multi)}; matched beat was the FIRST beat in {first}")
    print(f"  per-sentence read():   {pc}/{nb} beats ({pc/nb:.0%}); all beats in {full_per}/{len(multi)}; "
          f"level right on {plo}/{pln} captured beats")
    for m in multi:
        print(f"  {m['id']} whole={m['whole'][0]}/{m['whole'][1]}({m['whole'][3]!r}) "
              f"per={[p[0] for p in m['per_sentence']]} {m['per_captured']}/{m['n_beats']}")

    print(f"\nCOVERAGE: reachable {len(struct['reachable'])}/{len(E.names())}; "
          f"unreachable: {struct['unreachable']}")
    print("  other paths:", struct["other_paths"])
    print(f"SHADOWED keywords ({len(struct['shadowed'])} of {struct['n_keywords']}):")
    for s in struct["shadowed"]:
        print(f"  {s['family']}:{s['keyword']!r} always loses to {s['always_loses_to']} via {s['via']!r}")
    print("  keywords in two families:", struct["dup_keywords"])
    sub = [x for x in probes["substring"] if not x["control"]]
    fp = sum(x["false_positive"] for x in sub)
    print(f"\nSUBSTRING PROBES: {fp}/{len(sub)} false positives")
    for x in probes["substring"]:
        print(f"  {'FP ' if x['false_positive'] else 'ok '}{x['text']!r} -> {x['got']} (why={x['why']!r})")
    sh = probes["shadow"]
    print(f"SHADOW PROBES: {sum(x['ok'] for x in sh)}/{len(sh)} right")
    for x in sh:
        print(f"  {'ok ' if x['ok'] else 'BAD'} {x['text']!r} -> {x['got']} (why={x['why']!r}) expected {x['expected']}")
    lvp = [x for x in probes["level"] if not x["control"]]
    print(f"LEVEL PROBES: {sum(x['differs'] for x in lvp)}/{len(lvp)} pairs misjudged")
    for x in probes["level"]:
        print(f"  {'DIFF' if x['differs'] else 'same'} {x['a']!r}={x['level_a']}  {x['b']!r}={x['level_b']}{'  (control)' if x['control'] else ''}")
    print("APOSTROPHE PROBES:")
    for x in probes["apostrophe"]:
        print(f"  {x['text']!r} -> {x['read']}")
    print(f"\nSPEED: {sp['us_per_call']:.1f} us/call over {sp['calls']} calls; "
          f"longest input ({sp['longest_chars']} chars) {sp['us_longest']:.1f} us")

    if do_anim:
        lv, table, default_users = run_levels()
        res["levels"] = lv
        res["levels_table"] = table
        res["default_level_users"] = default_users
        print("\nLEVEL INTEGRITY")
        print("  table problems:", table or "none")
        print("  using _DEFAULT_LEVELS:", default_users)
        for n, e in lv.items():
            st = "; ".join(e["structural"]) or "-"
            br = {k: v for k, v in e["broken"].items() if v}
            print(f"  {n:11s} lv={e['levels']} restdist(pose)={e['rest_dist_pose']:.2f} "
                  f"L2 lo-mid={e['pairs']['low-mid']['l2']:.3f} mid-hi={e['pairs']['mid-intense']['l2']:.3f} "
                  f"px lo-mid={e['px']['low-mid']:.1f}% mid-hi={e['px']['mid-intense']:.1f}% "
                  f"noise={e['noise_px']:.1f}% settled_dev={e['settled_dev']['mid']:.3f} "
                  f"struct={st} broken={br}")
    with open(OUT, "w") as f:
        json.dump(res, f, indent=1, ensure_ascii=False, default=str)
    print("\nwrote", OUT)


if __name__ == "__main__":
    main()
