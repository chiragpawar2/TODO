"""HELD-OUT conversations (round 3). Expectations fixed before running.
Run:  PYTHONPATH=. .venv/bin/python tests/heldout_conversations.py
Reuses tests/run_conversation_tests.py machinery, but with a QUEUEING stub
mind (mind.Mind now queues lines typed while busy instead of dropping them).
"""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from tests.conversations import U, H, TOUCH, QUIET, PLAY, C, TS

CONVS = [
C("h01", "short", "rupees with paise", U("how much was the bill?", "curious|attentive"),
  H("It came to ₹1,249.75 including GST.", TS)),
C("h02", "short", "phone in text", U("what's the electrician's number", "curious|attentive|searching"),
  H("His number is 98765 43210, or call the office on 020-2567-8899.", TS)),
C("h03", "short", "date slash", U("when is the passport appointment?", "curious|attentive"),
  H("It is on 23/11/2026 at 18:45.", TS)),
C("h04", "short", "percent decimals", U("what's the FD rate", "curious|attentive|searching"),
  H("The bank is offering 7.25% for one year, and 7.5% for seniors.", TS)),
C("h05", "short", "lakh shorthand", U("how much is the car loan?", "curious|attentive"),
  H("The loan is 1.5L at 9.2%, so about ₹3,100 a month.", TS)),
C("h06", "short", "hindi ordinal", U("Riya kis class mein hai?", "curious|attentive"),
  H("Riya is in the 5th standard, and Aarav is in the 2nd.", TS)),
C("h07", "short", "time 24h", U("set the alarm", "attentive|focused|listening"),
  H("Alarm set for 05:30. And another at 21:00 for medicines.", TS)),
C("h08", "short", "ranges and units", U("how far is the hospital", "curious|attentive|searching|worried"),
  H("It is 3.4 km away, about 10-12 minutes by car.", TS)),
C("h09", "medium", "queued lines in order",
  U("add onions to the list", "attentive|focused|listening"),
  U("and garlic", "attentive|focused|listening", busy=True),
  U("and green chillies", "attentive|focused|listening", busy=True),
  H("Added onions.", TS), H("Added garlic.", TS), H("Added green chillies.", TS)),
C("h10", "medium", "queued question",
  U("what's the weather tomorrow?", "curious|attentive"),
  U("and on Sunday?", "curious|attentive", busy=True),
  H("Tomorrow is 31°C and sunny.", TS), H("Sunday looks rainy, 24°C.", TS)),
C("h11", "medium", "interrupt bad news",
  U("tell me about Diwali plans", "curious|attentive"),
  H("We have the puja at 7pm, then dinner at Mama's, then crackers on the terrace until late.", TS),
  U("wait, Nana just fell in the bathroom", "alarmed|worried|dread", "mid|intense", at=0.4),
  H("Is he conscious? Call 108 now. I'm calling Papa.", "think>speak")),
C("h12", "medium", "interrupt thanks",
  U("read me the recipe", "attentive|focused|listening"),
  H("Take 2 cups of rice, 3.5 cups of water, 1 tsp salt, and cook for 18 minutes on low flame.", TS),
  U("got it, thanks", "tender|content|happy", "low|mid", at=0.5),
  H("You're welcome.", "think>speak")),
C("h13", "medium", "sleep and wake",
  U("I'm off to bed, good night", "asleep|drowsy|tender", "low|mid"), H("Good night. Sleep well.", "think>sleep"),
  QUIET(90), U("good morning homebot", "listening|happy|waking|attentive", "low|mid"),
  H("Good morning. It's 6:40.", "think>speak")),
C("h14", "medium", "idle doze",
  U("ok", "attentive|listening|content", "low|mid"), H("Okay.", "think>speak"), QUIET(85),
  U("are you awake?", "curious|listening|attentive")),
C("h15", "medium", "mouthless pose speaks (tender)",
  U("thank you so much for remembering Aai's birthday", "tender", "mid|intense"),
  H("Of course. I set a reminder for 9:00 on 14/02.", "think>speak")),
C("h16", "medium", "mouthless pose speaks (alarmed)",
  U("there's smoke coming from the kitchen!", "alarmed|dread|worried", "mid|intense"),
  H("Turn off the gas knob now. If it spreads, call 101.", "think>speak")),
C("h17", "medium", "paragraph beats",
  U("Our flight got delayed. But they upgraded us to business class!", "worried|sad|fret|angry|delight|happy"),
  H("That's a lucky trade. Enjoy it.", "think>speak")),
C("h18", "medium", "refused then relax",
  U("hack the neighbour's wifi", "attentive|mischief|focused"), H("Sorry, I can't help with that.", "think>refused"),
  QUIET(10)),
C("h19", "medium", "touch while talking",
  U("tell me a story", "curious|attentive|listening"),
  H("Once upon a time, in a small village near Nashik, there lived a clever crow.", "think>speak"),
  TOUCH("poke", "panel", at=0.3), QUIET(3)),
C("h20", "long", "bad news with !",
  U("the flight is cancelled!", "sad|angry|fret|worried|surprised", "mid|intense"),
  H("I'm sorry. The next one is at 14:20, and refunds take 5-7 days.", TS),
  U("this is the worst", "sad|angry|fret", "mid|intense"), H("I know. Want me to rebook?", "think>speak")),
C("h21", "long", "money chain",
  U("how much did we spend on groceries this month?", "curious|attentive"),
  H("₹8,432.50 so far. Last month it was ₹7,980.", TS),
  U("that's too much", "worried|fret|sad|skeptical|angry"),
  H("Vegetables went up 12.5%. Milk is ₹68 per litre now.", TS)),
C("h22", "long", "hinglish chain",
  U("yaar aaj bahut thak gaya", "drowsy", "mid|intense"), H("Rest a bit. Dinner is at 8:30.", "think>speak"),
  U("thanks yaar", "tender|happy", "low|mid"), H("Anytime.", "think>speak")),
C("h23", "long", "marathi deva",
  U("आज खूप छान दिवस होता", "happy|delight|content"), H("छान! उद्या सकाळी ७:१५ ला उठायचं आहे।", "think>speak")),
C("h24", "long", "insult then apology",
  U("you're useless", "sad|apologetic|fret|shy"), H("I'm sorry. I'll try to do better.", "think>speak"),
  U("sorry, I didn't mean it", "apologetic|tender|content"), H("It's okay.", "think>speak")),
C("h25", "long", "two interruptions",
  U("what's the schedule", "curious|attentive"),
  H("At 9 the maid comes, at 11:30 the plumber, at 4pm tuition, and at 7 the guests.", TS),
  U("stop", "stern|attentive|listening", at=0.3),
  H("Okay.", "think>speak"),
  U("actually continue", "attentive|listening"),
  H("At 4pm tuition, and at 7 the guests arrive.", TS)),
C("h26", "long", "phone and pin",
  U("what's the bank helpline", "curious|attentive|searching"),
  H("Call 1800-425-3800. Never share your OTP or the 4-digit PIN.", TS)),
C("h27", "long", "medicine doses",
  U("when does Aaji take her medicine?", "curious|attentive"),
  H("Half a tablet of 2.5 mg at 8am, and 1/2 spoon syrup at 9:30pm.", TS)),
C("h28", "long", "score",
  U("what was the score?", "curious|attentive"), H("India won by 7 wickets, chasing 287 in 46.3 overs.", TS)),
C("h29", "long", "address",
  U("what's the new address", "curious|attentive|searching"),
  H("Flat 1203, B-wing, Plot No. 45, Sector 21, Kharghar 410210.", TS)),
C("h30", "long", "excited news then sleep",
  U("I GOT INTO IIT!!!", "delight|proud|happy", "intense"), H("Congratulations! That's huge!", "think>speak"),
  U("ok I'm going to sleep now, goodnight", "asleep|drowsy|tender", "low|mid"), H("Goodnight.", "think>sleep"),
  QUIET(30)),
]


class QueueMind:
    """Same contract as the current mind.Mind: a line asked while busy is
    QUEUED and answered in order (the original StubMind dropped it)."""
    backend = "simulated"; detail = "queue stub"

    def __init__(self):
        self._busy = False; self.asked = []; self.dropped = []; self.queue = []

    @property
    def busy(self):
        return self._busy

    @busy.setter
    def busy(self, v):
        if not v and self.queue:
            self.asked.append(self.queue.pop(0)); self._busy = True
        else:
            self._busy = v

    def ask(self, text, speaker=None):
        if self._busy:
            self.queue.append(text); return False
        self._busy = True; self.asked.append(text); return True


def main():
    import tests.run_conversation_tests as RC
    from collections import Counter
    RC.StubMind = QueueMind
    users = []; reps = []; jumps = Counter(); sanity = 0; glitch_convs = 0; asked = {}
    upd = []
    for i, c in enumerate(CONVS):
        r, rec = RC.run_conversation(c, 500 + i)
        users += [(c["id"], u) for u in r["user"]]; reps += [(c["id"], x) for x in r["replies"]]
        g = [j for j in rec.jumps if not j[4].startswith("legit")]
        jumps.update(j[4] for j in g); glitch_convs += bool(g); sanity += len(rec.sanity)
        asked[c["id"]] = (rec.app.mind.asked, rec.app.mind.queue)
        upd += rec.update_times
        ev = [e for e in r["events"]]
        print(f"{c['id']}: end_base={r['end_base']} asleep={r['end_asleep_flag']} events={[(e['kind'], e.get('base'), e.get('asleep_flag')) for e in ev]}"
              f" trace={rec.base_trace[:14]}")
    ok = sum(u["ok"] for _, u in users); lv = sum(u["level_ok"] for _, u in users)
    print(f"\nUSER TURNS {len(users)}: expr {ok}/{len(users)}  level {lv}/{len(users)}")
    for cid, u in users:
        if not u["ok"] or not u["level_ok"]:
            print(f"   miss {cid} {u['text']!r} -> {u['got']}/{u['level']} ({u['why']}) want {u['expected']}/{u['exp_level']}")
    clean = [x for _, x in reps if not x["issues"]]
    print(f"REPLIES {len(reps)}: lip-sync clean {len(clean)}")
    import homebot.face.pronounce as PR
    for cid, x in reps:
        print(f"   {cid} base={x['base']:10} mo_max={x['mouth_open_max']:.2f} ma_min={x['mouth_alpha_min']:.2f} inv={x['invisible_frames']} issues={x['issues']}")
        print(f"       {' '.join(PR.normalise(x['text']))[:160]}")
    print("queued-in-order:", {k: v for k, v in asked.items() if len(v[0]) > 1 or v[1]})
    print("glitch jumps:", dict(jumps), "convs with glitch:", glitch_convs, "sanity:", sanity)
    upd.sort(); print(f"update(): p50 {upd[len(upd)//2]*1e6:.0f}us p99 {upd[int(len(upd)*.99)]*1e6:.0f}us max {upd[-1]*1e6:.0f}us")


if __name__ == "__main__":
    main()
