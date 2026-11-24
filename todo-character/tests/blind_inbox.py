"""Round 4: direct tests of FaceApp's threaded inbox + speech queue.

    PYTHONPATH=. .venv/bin/python tests/blind_inbox.py

A) 3 replies posted from a REAL background thread within a few ms (fake UI clock).
B) Same with the REAL mind.Mind on the real clock (3 lines submitted back to back).
C) The user interrupts while 2 replies are still queued.
Every Animator mutator is wrapped to record which thread called it.
"""
from __future__ import annotations
import os, sys, threading, time as _rt
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import tests.run_conversation_tests as RC
from homebot.face import animator as AN, app as APP
from homebot.face.mind import Mind

MUT = ("speak", "hush", "set", "flash", "play", "play_steps", "stop_sequence")
REPLIES = ["Yes, the milkman comes at six tomorrow.",
           "The newspaper is on leave on Monday.",
           "And the maid said she will come at ten."]


def instrument(app, ui):
    log = {"off_thread": [], "speaks": [], "hush_live": []}
    a = app.anim
    for m in MUT:
        orig = getattr(a, m)
        def w(*args, _o=orig, _m=m, **kw):
            if threading.current_thread() is not ui:
                log["off_thread"].append(_m)
            if _m == "speak":
                prev = a._utt
                log["speaks"].append({"text": args[0], "t": APP.time.monotonic(),
                                      "prev_live": prev is not None,
                                      "prev_text": prev.text if prev is not None and hasattr(prev, "text") else None})
            if _m == "hush" and a._utt is not None:
                log["hush_live"].append(APP.time.monotonic())
            r = _o(*args, **kw)
            if _m == "speak":
                log["speaks"][-1]["dur"] = r
            return r
        setattr(a, m, w)
    return log


def summarise(name, log):
    sp = log["speaks"]
    overlaps = 0; cut = 0
    for i in range(1, len(sp)):
        end_prev = sp[i - 1]["t"] + sp[i - 1]["dur"]
        if sp[i]["t"] < end_prev - 1e-6:
            overlaps += 1
    for i, s in enumerate(sp):
        end = s["t"] + s["dur"]
        if any(s["t"] < h < end - 1e-6 for h in log["hush_live"]):
            cut += 1
    print(f"[{name}] spoken in order: {[s['text'][:22] for s in sp]}")
    print(f"   gaps(s): {[round(sp[i]['t'] - (sp[i-1]['t'] + sp[i-1]['dur']), 3) for i in range(1, len(sp))]}")
    print(f"   overlapping starts: {overlaps}  utterances cut short: {cut}  "
          f"animator calls off UI thread: {len(log['off_thread'])} {sorted(set(log['off_thread']))}")
    return overlaps, cut, len(log["off_thread"])


def test_a():
    app, clock = RC.fresh_app(7)
    app.mind = RC.StubMind()
    rec = RC.Recorder(app, clock, "A")
    log = instrument(app, threading.current_thread())
    rec.step(0.5)
    def brain():
        app._on_state("speaking")
        for r in REPLIES:
            app._on_reply(r); _rt.sleep(0.002)
    th = threading.Thread(target=brain); th.start(); th.join()
    print(f"[A] inbox size after thread: {app._inbox.qsize()}  thread posted in ~{len(REPLIES)*2} ms")
    rec.step(20.0)
    return summarise("A fake clock, real thread", log)


def test_b():
    RC.fresh_app(8)
    APP.time = _rt; AN.time = _rt
    app = RC._APP
    app.anim = AN.Animator(app.renderer)
    app.mind = Mind(app._on_state, app._on_reply)
    log = instrument(app, threading.current_thread())
    print(f"[B] real Mind backend: {app.mind.backend}")
    for t in ["is the milkman coming", "and the newspaper", "and the maid"]:
        app._submit(t)
    t0 = _rt.monotonic()
    while _rt.monotonic() - t0 < 25:
        app._idle_check(); app.anim.update(); _rt.sleep(0.02)
        if len(log["speaks"]) >= 3 and not app.anim.speaking and not app._speech and not app.mind.busy:
            break
    print(f"   replies: {[s['text'][:30] for s in log['speaks']]}")
    r = summarise("B real Mind, real clock", log)
    return r


def test_c():
    app, clock = RC.fresh_app(9)
    APP.time = clock; AN.time = clock
    app.anim = AN.Animator(app.renderer); app.mind = RC.StubMind()
    rec = RC.Recorder(app, clock, "C")
    log = instrument(app, threading.current_thread())
    th = threading.Thread(target=lambda: [app._on_reply(r) for r in REPLIES]); th.start(); th.join()
    rec.step(1.0)
    first = log["speaks"][0]
    rec.step(first["dur"] * 0.4)
    t_int = clock.now
    app._wake(); app._submit("wait, stop talking")
    queued_at_interrupt = len(app._speech)
    rec.step(0.5)
    after = [s for s in log["speaks"] if s["t"] >= t_int]
    rec.step(15)
    after_all = [s for s in log["speaks"] if s["t"] >= t_int]
    # FIXER NOTE (round 5): guard the report for the fixed case, where no
    # stale reply resumes at all (after_all[0] used to raise IndexError).
    stale = [s for s in after_all if s["text"] in REPLIES]
    print(f"[C] stale queued replies spoken after the interrupt: {len(stale)}; "
          f"replies after interrupt (incl. the answer to the new line): {[s['text'][:25] for s in after_all]}; "
          f"off-thread animator calls: {len(log['off_thread'])}")
    if not after_all:
        return queued_at_interrupt, len(after), 0
    print(f"[C] interrupt at {first['dur']*0.4:.2f}s into reply 1; queued then: {queued_at_interrupt}; "
          f"speaking 0.5 s after interrupt: {[s['text'][:25] for s in after]}; "
          f"total resumed after interrupt: {len(after_all)} (first {after_all[0]['t']-t_int:.2f}s after the interrupt, base then={app.anim.base}); mind.asked={app.mind.asked}")
    return queued_at_interrupt, len(after), len(after_all)


if __name__ == "__main__":
    a = test_a(); c = test_c(); b = test_b()
    print("RESULT A (overlaps, cut, offthread):", a, " B:", b, " C (queued, resumed<0.5s, resumed total):", c)
