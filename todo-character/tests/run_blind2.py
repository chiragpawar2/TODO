"""Run the BLIND-2 set (tests/blind2_cases.py), round 5.

    PYTHONPATH=. .venv/bin/python tests/run_blind2.py [--rules]

Reports expression / level / beats (exact, merges allowed, positional), per
category, the over-trigger rate on neutral lines, read(model=False) and
read() timing, and overlap of the cases with earlier phrase sources
(tests/*.py, tests/*.md, homebot/face/lexicon.py).
"""
from __future__ import annotations

import glob, os, re, sys, time
from collections import Counter, defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from homebot.face import reading as R
from tests.blind2_cases import CASES, MULTI_CASES, Q
from tests.run_heldout import align

NEUTRALISH = set(Q)


def _norm(s):
    return " ".join(re.findall(r"\w+", s.lower()))


def overlap_report():
    """4-word runs shared with any earlier test file / md, and any multi-word
    lexicon.py string literal (alternatives split on |) contained in a case."""
    corpus = []
    for p in glob.glob(os.path.join(ROOT, "tests", "*.py")) + glob.glob(os.path.join(ROOT, "tests", "*.md")):
        if "blind2" in p or "VERIFY_ROUND_5" in p:
            continue
        corpus.append(_norm(open(p, encoding="utf-8").read()))
    big = " " + " ".join(corpus) + " "
    lex_src = open(os.path.join(ROOT, "homebot", "face", "lexicon.py"), encoding="utf-8").read()
    lex = set()
    for lit in re.findall(r'"([^"\n]+)"', lex_src):
        if "\\" in lit or "{" in lit:
            continue
        for alt in lit.split("|") if " " in lit else [lit]:
            a = _norm(alt)
            if len(a.split()) >= 2:
                lex.add(a)
    hits = {}
    for c in CASES + MULTI_CASES:
        w = _norm(c["text"]).split()
        t = " " + " ".join(w) + " "
        tg = [" ".join(w[i:i + 4]) for i in range(len(w) - 3)]
        shared = [g for g in tg if f" {g} " in big]
        lx = [p for p in lex if f" {p} " in t]
        if shared or lx:
            hits[c["id"]] = (c["text"], shared[:3], lx[:4])
    return hits


def run(model):
    by = defaultdict(lambda: [0, 0, 0])
    fails, out = [], []
    for c in CASES:
        name, level, amt, why = R.read(c["text"], model=model)
        ok = name in c["expected"]; lok = level in c["expected_level"]
        for k in (c["category"], "ALL") + (("EMOTIONAL",) if c["category"] not in ("neutral", "command", "names") else ()):
            b = by[k]; b[0] += 1; b[1] += ok; b[2] += lok
        out.append({**c, "got": name, "level": level, "why": why, "ok": ok})
        if not ok or not lok:
            fails.append((c, name, level, why, ok))
    return by, fails, out


def main():
    model = "--rules" not in sys.argv
    ov = overlap_report()
    print(f"OVERLAP: {len(ov)} cases share a 4-word run with old tests/md or contain a lexicon phrase")
    for k, v in ov.items():
        print("   ", k, v)
    for label, m in (("RULES ONLY  read(model=False)", False), ("FULL  read() (rules + model fallback)", True)):
        if m and not model:
            continue
        by, fails, out = run(m)
        print(f"\n===== {label}")
        n, e, l = by["ALL"]
        print(f"SINGLE n={n}: expression {e}/{n} ({e/n:.1%})  level {l}/{n} ({l/n:.1%})")
        cl = [o for o in out if o["id"] not in ov]
        print(f"  CLEAN (no overlap) n={len(cl)}: expression {sum(o['ok'] for o in cl)}/{len(cl)} "
              f"({sum(o['ok'] for o in cl)/len(cl):.1%})")
        ne, ee, le = by["EMOTIONAL"]
        print(f"  emotional-only n={ne}: {ee}/{ne} ({ee/ne:.1%})")
        for k, (n_, e_, l_) in sorted(by.items()):
            if k not in ("ALL", "EMOTIONAL"):
                print(f"  {k:11} n={n_:2} expr {e_:2}/{n_:<2}  level {l_:2}/{n_}")
        neu = [o for o in out if o["category"] in ("neutral", "command", "names")]
        trig = [o for o in neu if o["got"] not in NEUTRALISH]
        print(f"  OVER-TRIGGER on neutral/command/name lines: {len(trig)}/{len(neu)} ({len(trig)/len(neu):.1%})")
        nn = [o for o in out if o["category"] == "neutral"]
        print(f"    'neutral' category alone: {sum(o['got'] not in NEUTRALISH for o in nn)}/{len(nn)}")
        print("  level distribution:", dict(Counter(o["level"] for o in out)))
        sil = [f for f in fails if not f[4] and f[3] is None]
        print(f"  misses: {sum(not f[4] for f in fails)} (silence why=None: {len(sil)})")
        for c, name, level, why, ok in fails:
            print(f"  {'E' if not ok else 'l'} {c['id']} [{c['category']}] {c['text']!r} -> {name}/{level} ({why!r})"
                  f"  want {c['expected'][:4]} / {c['expected_level']}")
        st = le2 = lv = bt = bok = 0
        print(f"\n  MULTI {len(MULTI_CASES)} paragraphs")
        cst = cn = 0
        for mc in MULTI_CASES:
            got = R.read_beats(mc["text"], model=m)
            s, l2, ln = align(got, mc["expected"])
            st += s; lv += l2; le2 += ln; bt += len(mc["expected"])
            bok += sum(1 for g, x in zip(got, mc["expected"]) if g[0] in x["accept"])
            if mc["id"] not in ov:
                cn += 1; cst += s
            mark = "OK " if s else ("~  " if ln else "XX ")
            print(f"   {mark}{mc['id']} got={[(g[0], g[3]) for g in got]}  want={[x['accept'][:3] for x in mc['expected']]}")
        k = len(MULTI_CASES)
        print(f"  beats exact {st}/{k} ({st/k:.0%}); merges allowed {le2}/{k} ({le2/k:.0%}); exact+levels {lv}/{k}; "
              f"positional {bok}/{bt} ({bok/bt:.0%}); clean exact {cst}/{cn}")
    texts = [c["text"] for c in CASES] + [mc["text"] for mc in MULTI_CASES]
    for label, m, reps in (("read(model=False)", False, 50), ("read()", True, 3)):
        if m and not model:
            continue
        ts = []
        for _ in range(reps):
            for t in texts:
                a = time.perf_counter(); R.read(t, model=m); ts.append(time.perf_counter() - a)
        ts.sort()
        print(f"{label}: mean {sum(ts)/len(ts)*1e6:.1f} us  p50 {ts[len(ts)//2]*1e6:.1f} us  "
              f"p99 {ts[int(len(ts)*.99)]*1e6:.1f} us  max {ts[-1]*1e6:.1f} us")


if __name__ == "__main__":
    main()
