"""BLIND conversations (round 4). Expectations fixed before running.

    PYTHONPATH=. .venv/bin/python tests/blind_conversations.py

Reuses tests/run_conversation_tests.py through tests/heldout_conversations.py
(its QueueMind stub queues lines asked while busy, like mind.Mind).
"""
from __future__ import annotations
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from tests.conversations import U, H, TOUCH, QUIET, PLAY, C, TS

CONVS = [
C("z01", "short", "ordinal date", U("when is Chintu's annual day?", "curious|attentive"),
  H("It is on 3rd Dec, at 4:30 in the school hall.", TS)),
C("z02", "short", "quarter", U("how did the shop do this quarter", "curious|attentive|searching"),
  H("Sales in Q3 were up 12% over Q2.", TS)),
C("z03", "short", "indian grouping", U("what's the fixed deposit worth now", "curious|attentive|searching"),
  H("It is worth 2,50,000 rupees today.", TS)),
C("z04", "short", "rupee decimal", U("how much is the Netflix plan", "curious|attentive|searching"),
  H("The basic plan is ₹99.99 a month.", TS)),
C("z05", "short", "speed unit", U("how fast was the bus going?", "curious|attentive"),
  H("It was doing 50km/h near the school.", TS)),
C("z06", "short", "feet inches", U("how tall is Rohan now", "curious|attentive"),
  H("He is 5'10\" now, taller than his father.", TS)),
C("z07", "short", "negative temp", U("how cold is it in Gulmarg", "curious|attentive|searching"),
  H("It is -4°C there tonight, with snow.", TS)),
C("z08", "short", "multiplier", U("how many tablets for Aaji", "curious|attentive"),
  H("Paracetamol x2 after lunch, and the chemist is open 24x7.", TS)),
C("z09", "short", "plus count", U("how many people came to the wedding", "curious|attentive"),
  H("There were 100+ guests, and 1st/2nd cousins from Nagpur.", TS)),
C("z10", "short", "roman numerals", U("who is on the stamp", "curious|attentive|searching"),
  H("It shows King George V, and the next one shows Pope John Paul II.", TS)),
C("z11", "short", "k and lakh", U("what's the budget", "curious|attentive|searching"),
  H("Spend ₹5k on decorations, and keep 10 lakh for the hall.", TS)),
C("z12", "short", "devanagari digits", U("दवाई कब लेनी है?", "curious|attentive"),
  H("दवाई 2 बजे और रात 9 बजे लेनी है।", TS)),
C("z13", "medium", "three queued questions",
  U("is the milkman coming today", "curious|attentive"),
  U("and the newspaper", "curious|attentive|listening", "low|mid", busy=True),
  U("and the maid?", "curious|attentive|listening", "low|mid", busy=True),
  H("Yes, the milkman comes at 6.", TS), H("The paper is on leave today.", TS), H("The maid comes at 10.", TS)),
C("z14", "medium", "grief then thanks",
  U("my dog Bruno died this morning", "crying|sad", "mid|intense"),
  H("I'm so sorry. Bruno was lucky to have you.", "think>speak"),
  U("thank you, that helps", "tender|content|happy", "low|mid"),
  H("I'm here whenever you want to talk.", "think>speak")),
C("z15", "medium", "kid excited interrupt",
  U("tell me a story", "attentive|focused|listening|curious"),
  H("Once upon a time there was a little elephant who lived near a big blue river, and every morning she", TS),
  U("look, a puppy!!", "surprised|delight|startled|oh|curious|love", "mid|intense", at=0.4),
  H("Oh! Is it a brown one?", "think>speak")),
C("z16", "medium", "angry then sorry",
  U("why didn't you remind me about the gas bill?!", "angry|stern", "mid|intense"),
  H("I'm sorry, I didn't have it saved. Shall I add it for the 5th of every month?", "think>refused>speak"),
  U("ok fine, do that", "attentive|content|listening|focused", "low|mid"),
  H("Done.", TS)),
C("z17", "medium", "sleep goodnight marathi",
  U("shubh ratri homebot", "asleep|drowsy|tender|happy", "low|mid"),
  H("Shubh ratri.", "think>sleep"), QUIET(60),
  U("uth ja", "waking|listening|attentive", "low|mid"), H("Good morning!", "think>speak")),
C("z18", "medium", "scared at night",
  U("I heard a noise downstairs, I'm scared", "worried|dread|alarmed|fret", "mid|intense"),
  H("Stay in your room. I've turned on the porch lights and I'm calling Papa.", "think>speak")),
C("z19", "medium", "hinglish happy",
  U("aaj toh maza aa gaya yaar", "happy|delight|grin|content", "mid"),
  H("Sounds like a great day!", "think>speak")),
C("z20", "medium", "touch during speech",
  U("what's the weather", "curious|attentive|searching"),
  H("It is 28°C and humid, with a 70% chance of rain after 3pm.", TS),
  TOUCH("poke", "panel", at=0.5)),
C("z21", "long", "recipe numbers",
  U("how do I make chai for 4", "curious|attentive|focused"),
  H("Boil 2½ cups of water with 1 tsp of tea and 4-5 cardamoms for 3-4 min, then add 1½ cups of milk.", TS)),
C("z22", "long", "insult then apology",
  U("you're absolutely useless today", "sad|apologetic|fret|shy|angry|stern", "mid|intense"),
  H("I'm sorry. What can I do better?", "think>speak"),
  U("sorry, I'm just tired", "apologetic|drowsy|sad", "low|mid"),
  H("That's okay. Rest a bit.", "think>speak")),
C("z23", "long", "idle doze then poke",
  U("nothing, just sitting", "attentive|bored|listening|content|rest", "low|mid"),
  H("Okay.", "think>speak"), QUIET(80), TOUCH("poke", "panel")),
C("z24", "long", "phone and time",
  U("what's the doctor's number", "curious|attentive|searching"),
  H("Dr. Kulkarni is on +91 98220 12345, available 10:00-13:30 on weekdays.", TS)),
C("z25", "long", "news paragraph",
  U("I passed my CA exam! I can't believe it. Mummy is crying with joy.", "delight|proud|happy|surprised", "mid|intense"),
  H("Congratulations! That's fantastic news!", "think>speak")),
]


def main():
    import tests.heldout_conversations as HC
    HC.CONVS = CONVS
    HC.main()


if __name__ == "__main__":
    main()
