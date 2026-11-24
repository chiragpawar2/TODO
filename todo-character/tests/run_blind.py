"""Run the BLIND set (tests/blind_cases.py) against reading.read / read_beats.

    PYTHONPATH=. .venv/bin/python tests/run_blind.py
"""
from __future__ import annotations

import json, os, re, sys, time
from collections import defaultdict

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from homebot.face import reading as R
from tests.blind_cases import CASES, MULTI_CASES
from tests.run_heldout import align

HERE = os.path.dirname(os.path.abspath(__file__))


def _norm(s):
    return " ".join(re.findall(r"\w+", s.lower()))


def overlap_report():
    """Exact or contained matches against every earlier phrase source."""
    seen = set()
    from tests import heldout_cases, expression_cases, conversations
    for c in heldout_cases.CASES + heldout_cases.MULTI_CASES:
        seen.add(_norm(c["text"]))
    for c in getattr(expression_cases, "CASES", []) + getattr(expression_cases, "MULTI_CASES", []):
        if isinstance(c, dict) and "text" in c:
            seen.add(_norm(c["text"]))
    for cv in conversations.CONVERSATIONS:
        for t in cv["turns"]:
            if "text" in t:
                seen.add(_norm(t["text"]))
    md = open(os.path.join(HERE, "VERIFY_ROUND_3.md"), encoding="utf-8").read()
    for q in re.findall(r'"([^"\n]{3,})"', md):
        seen.add(_norm(q))
    seen.discard("")
    hits = []
    for c in CASES + MULTI_CASES:
        t = _norm(c["text"])
        for s in seen:
            if len(s.split()) >= 3 and (s == t or s in t or (len(t.split()) >= 3 and t in s)):
                hits.append((c["id"], c["text"], s))
    return hits


def main():
    ov = overlap_report()
    print(f"OVERLAP with earlier phrase sources (>=3 words, exact/contained): {len(ov)}")
    for h in ov:
        print("   ", h)
    by = defaultdict(lambda: [0, 0, 0])
    fails, out = [], []
    for c in CASES:
        name, level, amt, why = R.read(c["text"])
        ok = name in c["expected"]; lok = level in c["expected_level"]
        for k in (c["category"], "ALL"):
            b = by[k]; b[0] += 1; b[1] += ok; b[2] += lok
        out.append({**c, "got": name, "level": level, "why": why, "ok": ok, "level_ok": lok})
        if not ok or not lok:
            fails.append((c["id"], c["category"], c["text"], name, level, why, c["expected"], c["expected_level"], ok))
    bad = {h[0] for h in ov}
    for o in out:
        if o["id"] not in bad:
            b = by["CLEAN"]; b[0] += 1; b[1] += o["ok"]; b[2] += o["level_ok"]
    n, e, l = by["CLEAN"]
    print(f"\nBLIND SINGLE, CLEAN (overlapping cases removed): n={n} expression {e}/{n} ({e/n:.1%})  level {l}/{n} ({l/n:.1%})")
    by.pop("CLEAN")
    n, e, l = by["ALL"]
    print(f"BLIND SINGLE: n={n} expression {e}/{n} ({e/n:.1%})  level {l}/{n} ({l/n:.1%})")
    for k, (n_, e_, l_) in sorted(by.items()):
        if k != "ALL":
            print(f"  {k:11} n={n_:2} expr {e_:2}/{n_:<2}  level {l_:2}/{n_}")
    from collections import Counter
    print("level distribution got:", dict(Counter(o["level"] for o in out if "level" in o)))
    print("\nFAILURES (E = expression wrong, l = level only):")
    for f in fails:
        print(f"  {'E' if not f[8] else 'l'} {f[0]} [{f[1]}] {f[2]!r} -> {f[3]}/{f[4]} ({f[5]!r})  want {f[6][:4]} / {f[7]}")

    st = le = lv = 0; bt = bok = 0
    print(f"\nBLIND MULTI: {len(MULTI_CASES)} paragraphs")
    for m in MULTI_CASES:
        got = R.read_beats(m["text"])
        s, l2, ln = align(got, m["expected"])
        st += s; lv += l2; le += ln
        bt += len(m["expected"])
        bok += sum(1 for g, e in zip(got, m["expected"]) if g[0] in e["accept"])
        mark = "OK " if s else ("~  " if ln else "XX ")
        print(f"  {mark}{m['id']} got={[(g[0], g[1]) for g in got]}  want={[e['accept'][:3] for e in m['expected']]}")
        out.append({**m, "got": [list(g[:4]) for g in got], "strict": s, "lenient": ln, "levels": l2})
    cm = [o for o in out if o.get("category") == "multi" and o["id"] not in bad]
    print(f"  CLEAN paragraphs: exact {sum(o['strict'] for o in cm)}/{len(cm)}")
    k = len(MULTI_CASES)
    print(f"  beats exact-in-order {st}/{k} ({st/k:.0%}); allowing merges {le}/{k}; "
          f"exact+all levels {lv}/{k}; positional beats {bok}/{bt} ({bok/bt:.0%})")

    texts = [c["text"] for c in CASES] + [m["text"] for m in MULTI_CASES]
    t0 = time.perf_counter(); worst = 0.0
    for _ in range(50):
        for t in texts:
            a = time.perf_counter(); R.read(t); worst = max(worst, time.perf_counter() - a)
    tot = time.perf_counter() - t0
    print(f"\nread(): mean {tot/(50*len(texts))*1e6:.1f} us  max {worst*1e6:.1f} us")
    json.dump(out, open(os.path.join(HERE, "blind_results.json"), "w"), ensure_ascii=False, indent=1, default=str)


if __name__ == "__main__":
    main()
