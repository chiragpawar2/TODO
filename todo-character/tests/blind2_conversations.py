"""BLIND-2 conversations (round 5). Expectations fixed before running.

    PYTHONPATH=. .venv/bin/python tests/blind2_conversations.py

Part 1: 20 conversations through tests/heldout_conversations.main (QueueMind).
Part 2: short-reply seconds-per-word.
Part 3: interruption with queued replies (stale replies must not play).
"""
from __future__ import annotations
import os, sys, threading
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from tests.conversations import U, H, TOUCH, QUIET, C, TS

CONVS = [
C("w01", "short", "kid wins race", U("I came first in the sack race!", "delight|happy|proud|grin", "mid|intense"),
  H("Wow, first place! Well done.", "think>speak")),
C("w02", "short", "okay", U("remind me about the plumber at 5", "attentive|listening|focused|curious"),
  H("Okay.", "think>speak")),
C("w03", "short", "good night", U("I'm going to bed now", "attentive|drowsy|listening|content|rest|yawn", "low|mid"),
  H("Good night. Sleep well.", "think>speak")),
C("w04", "short", "grandma worried", U("Ajoba hasn't called since morning, I'm worried", "worried|fret|dread"),
  H("Shall I call him for you?", "think>speak")),
C("w05", "short", "angry at bus", U("the school bus left without Riya again", "angry|stern|worried|sad|fret"),
  H("I'm sorry. Do you want me to call the transport desk?", "think>speak")),
C("w06", "short", "neutral fact", U("the pressure cooker whistled twice", "attentive|listening|curious"),
  H("Okay, I'll keep track.", "think>speak")),
C("w07", "short", "marathi happy", U("aaj khup maja aali", "happy|delight|grin|content"),
  H("Chhan!", "think>speak")),
C("w08", "short", "thanks", U("thank you homebot, you saved my day", "tender|happy|shy|content|love|proud"),
  H("Anytime.", "think>speak")),
C("w09", "medium", "queued two", U("is the pharmacy open", "curious|attentive|searching"),
  U("and the bakery", "curious|attentive|listening", "low|mid", busy=True),
  H("Yes, till ten tonight.", TS), H("The bakery closes at eight.", TS)),
C("w10", "medium", "sad then comfort", U("my best friend stopped talking to me", "sad|crying|fret"),
  H("That sounds really hard. Do you want to talk about it?", "think>speak"),
  U("maybe later", "attentive|sad|listening|bored", "low|mid"), H("Okay. I'm here.", "think>speak")),
C("w11", "medium", "devanagari", U("मुझे आज बहुत अकेलापन लग रहा है", "sad|crying"),
  H("मैं यहीं हूँ। बात करें?", "think>speak")),
C("w12", "medium", "numbers in reply", U("how much is the electricity bill", "curious|attentive|searching"),
  H("It is ₹2,340 for 312 units, due on 5th Jan.", TS)),
C("w13", "medium", "poke while talking", U("tell me a joke", "curious|attentive|grin|happy|mischief"),
  H("Why did the tomato blush? It saw the salad dressing.", "think>speak"), TOUCH("poke", "panel", at=0.4)),
C("w14", "medium", "interrupt", U("read me the news", "curious|attentive|searching"),
  H("The monsoon has reached Kerala early this year, and the weather office expects good rain.", TS),
  U("stop, stop", "attentive|listening|worried|startled|stern", "low|mid|intense", at=0.3),
  H("Okay, stopped.", "think>speak")),
C("w15", "medium", "sarcasm", U("oh joy, the in-laws are staying a month", "skeptical|stern|bored|sad|angry|worried"),
  H("That's a long visit. Want me to plan the meals?", "think>speak")),
C("w16", "long", "fear at night", U("there's someone knocking at 2 am", "worried|dread|alarmed|fret|startled", "mid|intense"),
  H("Don't open the door. I'm calling the watchman.", "think>speak")),
C("w17", "long", "name trap", U("is Anand uncle coming for lunch", "curious|attentive|searching"),
  H("Yes, at one.", TS)),
C("w18", "long", "insult then praise", U("you're hopeless, homebot", "sad|apologetic|fret|shy"),
  H("Sorry. I'll try harder.", "think>speak"),
  U("okay fine, you're actually pretty sweet", "shy|happy|love|tender|content|delight"),
  H("Thank you!", "think>speak")),
C("w19", "long", "idle then good night", U("nothing much", "attentive|bored|listening|content|rest", "low|mid"),
  H("Okay.", "think>speak"), QUIET(70), U("good night robot", "drowsy|tender|content|happy|attentive|yawn", "low|mid"),
  H("Good night. Sleep well.", "think>speak")),
C("w20", "long", "paragraph news", U("Dadi came home from hospital today. She's weak but smiling. We're all so relieved.",
  "content|happy|tender|delight", "mid|intense"),
  H("That's wonderful. Give her my love.", "think>speak")),
]


def short_spw():
    from homebot.face import visemes as V, pronounce as PR
    print("\nSHORT-REPLY TIMING (seconds per word, 0.15-0.9 is the checker's band)")
    fn = None
    for n in ("plan", "build", "timeline", "make_track", "track"):
        if hasattr(V, n):
            fn = getattr(V, n); break
    import tests.run_conversation_tests as RC
    app, clock = RC.fresh_app(11)
    for t in ["Okay.", "Yes.", "Hmm.", "Good night. Sleep well.", "Anytime.", "Chhan!", "Okay, stopped.",
              "No.", "Thank you!", "I'm here."]:
        d = app.anim.speak(t)
        utt = app.anim._utt
        w = len(utt.words) if utt is not None else max(1, len(t.split()))
        print(f"   {t!r:28} dur {d:.2f}s words {w} -> {d/max(1,w):.2f} s/word")
        app.anim.hush(); clock.now += 2.0; app.anim.update()


def interrupt_test():
    import tests.run_conversation_tests as RC
    from homebot.face import animator as AN, app as APP
    from tests.heldout_conversations import QueueMind
    print("\nINTERRUPT WITH QUEUED REPLIES")
    REP = ["The first train is at six ten from platform two.",
           "The second one is at six forty, it is usually late.",
           "And the fast local leaves at seven sharp."]
    app, clock = RC.fresh_app(13)
    APP.time = clock; AN.time = clock
    app.anim = AN.Animator(app.renderer); app.mind = QueueMind()
    rec = RC.Recorder(app, clock, "I")
    spoken = []
    orig = app.anim.speak
    def sp(text, *a, **k):
        spoken.append((text, clock.now)); return orig(text, *a, **k)
    app.anim.speak = sp
    th = threading.Thread(target=lambda: [app._on_reply(r) for r in REP]); th.start(); th.join()
    rec.step(1.2)
    t_int = clock.now
    queued = len(app._speech)
    app._wake(); app._submit("wait, which one is fastest")
    rec.step(0.3)
    # the brain answers the NEW line
    th = threading.Thread(target=lambda: app._on_reply("The seven o'clock fast local.")); th.start(); th.join()
    rec.step(15)
    after = [s for s in spoken if s[1] >= t_int]
    stale = [s for s in after if s[0] in REP]
    print(f"   queued at interrupt {queued}; spoken after interrupt: {[s[0][:30] for s in after]}")
    print(f"   STALE replies played after interrupt: {len(stale)}  (want 0); "
          f"new answer spoken: {any('fast local.' in s[0] for s in after)}; inbox left {app._inbox.qsize()}")
    # variant: stale reply arrives in the inbox AFTER the interrupt (brain was mid-answer)
    app2, clock2 = RC.fresh_app(14)
    APP.time = clock2; AN.time = clock2
    app2.anim = AN.Animator(app2.renderer); app2.mind = QueueMind()
    rec2 = RC.Recorder(app2, clock2, "I2"); sp2 = []
    o2 = app2.anim.speak
    app2.anim.speak = lambda text, *a, **k: (sp2.append((text, clock2.now)), o2(text, *a, **k))[1]
    app2._on_reply(REP[0]); rec2.step(1.0)
    t2 = clock2.now
    app2._wake(); app2._submit("no, tell me about buses")
    app2._on_reply(REP[1])           # late reply to the OLD question lands after the interrupt
    rec2.step(0.3); app2._on_reply("Bus 42 comes every ten minutes."); rec2.step(15)
    a2 = [s[0] for s in sp2 if s[1] >= t2]
    print(f"   late-arriving old reply variant: spoken after interrupt {[x[:30] for x in a2]} "
          f"-> stale played: {REP[1] in a2}")


def main():
    import tests.heldout_conversations as HC
    HC.CONVS = CONVS
    HC.main()
    short_spw()
    interrupt_test()


if __name__ == "__main__":
    main()
