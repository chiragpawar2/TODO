"""Run the held-out set (tests/heldout_cases.py) against reading.read / read_beats.

    PYTHONPATH=. .venv/bin/python tests/run_heldout.py
"""
from __future__ import annotations

import json, os, sys, time
from collections import defaultdict

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from homebot.face import reading as R
from tests.heldout_cases import CASES, MULTI_CASES


def align(got, exp):
    """Strict: same number of beats, each in order. Lenient: a got beat may
    cover several consecutive expected beats it is acceptable for (read_beats
    merges equal neighbours)."""
    strict = len(got) == len(exp) and all(g[0] in e["accept"] for g, e in zip(got, exp))
    lvl = strict and all(g[1] in e["level"] for g, e in zip(got, exp))
    j = 0
    ok = True
    for g in got:
        if j >= len(exp) or g[0] not in exp[j]["accept"]:
            ok = False; break
        j += 1
        while j < len(exp) and g[0] in exp[j]["accept"] and len(got) < len(exp):
            j += 1
    lenient = ok and j == len(exp)
    return strict, lvl, lenient


def main():
    by = defaultdict(lambda: [0, 0, 0])
    fails = []
    out = []
    for c in CASES:
        name, level, amt, why = R.read(c["text"])
        ok = name in c["expected"]; lok = level in c["expected_level"]
        b = by[c["category"]]; b[0] += 1; b[1] += ok; b[2] += lok
        a = by["ALL"]; a[0] += 1; a[1] += ok; a[2] += lok
        out.append({**c, "got": name, "level": level, "why": why, "ok": ok, "level_ok": lok})
        if not ok or not lok:
            fails.append((c["id"], c["text"], name, level, why, c["expected"], c["expected_level"], ok))
    n, e, l = by["ALL"]
    print(f"HELD-OUT SINGLE: n={n} expression {e}/{n} ({e/n:.0%})  level {l}/{n} ({l/n:.0%})")
    for k, (n_, e_, l_) in by.items():
        if k != "ALL":
            print(f"  {k:12} n={n_:2} expr {e_}/{n_}  level {l_}/{n_}")
    print("\nFAILURES (E = expression wrong, l = level only):")
    for f in fails:
        print(f"  {'E' if not f[7] else 'l'} {f[0]} {f[1]!r} -> {f[2]}/{f[3]} ({f[4]!r})  want {f[5][:5]} / {f[6]}")

    st = le = lv = 0; bt = bok = 0
    print(f"\nHELD-OUT MULTI: {len(MULTI_CASES)} paragraphs")
    for m in MULTI_CASES:
        got = R.read_beats(m["text"])
        s, l2, ln = align(got, m["expected"])
        st += s; lv += l2; le += ln
        bt += len(m["expected"])
        bok += sum(1 for g, e in zip(got, m["expected"]) if g[0] in e["accept"])
        mark = "OK " if s else ("~  " if ln else "XX ")
        print(f"  {mark}{m['id']} got={[(g[0], g[1]) for g in got]}  want={[e['accept'][:3] for e in m['expected']]}")
        out.append({**m, "got": [g[:4] for g in got], "strict": s, "lenient": ln, "levels": l2})
    k = len(MULTI_CASES)
    print(f"  paragraphs beats-exact-in-order {st}/{k} ({st/k:.0%}); allowing merges {le}/{k}; "
          f"with all levels right {lv}/{k}; positional beats right {bok}/{bt}")

    # timing on held-out text
    texts = [c["text"] for c in CASES] + [m["text"] for m in MULTI_CASES]
    t0 = time.perf_counter(); worst = 0
    for _ in range(50):
        for t in texts:
            a = time.perf_counter(); R.read(t); worst = max(worst, time.perf_counter() - a)
    tot = time.perf_counter() - t0
    print(f"\nread(): mean {tot/(50*len(texts))*1e6:.1f} us  max {worst*1e6:.1f} us")
    json.dump(out, open(os.path.join(os.path.dirname(__file__), "heldout_results.json"), "w"),
              ensure_ascii=False, indent=1, default=str)


if __name__ == "__main__":
    main()
