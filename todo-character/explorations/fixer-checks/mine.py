# My own probe lines (NOT from the blind/heldout sets): families around each gap.
import sys, time
from homebot.face import reading as R
L = [
 # hindi/marathi
 ("mujhe aaj kuch accha nahi lag raha", "sad"), ("mala he bilkul nahi aavadla", "sad"), ("mala khup aavadla", "happy"),
 ("usko dekh ke khup raag aalay", "angry"), ("kitna gussa aata hai yaar", "angry"), ("khooshi se pagal ho gayi main", "delight"),
 ("bindaas reh yaar, sab theek hoga", "content"), ("tu pagal hai kya", "angry"), ("dil baag baag ho gaya", "delight"),
 ("isne toh naak me dam kar rakha hai", "angry"), ("bahut udaas hoon aaj", "sad"), ("mujhe tumhari bahot yaad aati hai", "sad"),
 ("khup kantala aala", "bored"), ("neend aa rahi hai", "drowsy"), ("darr lag raha hai mujhe", "worried"),
 ("shukar hai sab thik ho gaya", "content"), ("bahut bura laga mujhe", "sad"), ("बहुत गुस्सा आ रहा है", "angry"),
 ("मला नाही आवडलं", "sad"), ("मुझे अच्छा नहीं लग रहा", "sad"), ("खूप राग आलाय", "angry"), ("दिल बाग बाग हो गया", "delight"),
 ("doodh le aana", None), ("kal subah jaldi uthana", None), ("light band kar do", None), ("mala chaha de", None),
 # english idioms
 ("I've been down in the dumps all week", "sad"), ("she's walking on air since the wedding", "delight"),
 ("that noise really gets on my nerves", "angry"), ("this commute is killing me", "fret"), ("my back is killing me", "worried"),
 ("the exam was a breeze", "content"), ("my tulsi plant is dying", "sad"), ("I'm at my wits end with this printer", "fret"),
 ("he's been driving me up the wall", "angry"), ("I'm on pins and needles", "worried"), ("we were in stitches", "grin"),
 ("I could hit the sack right now", "asleep"), ("my heart sank when I saw it", "sad"),
 # negation
 ("it isn't funny", "angry"), ("that's not okay", "sad"), ("this is not fair", "angry"), ("I'm not proud of it", "sad"),
 # sarcasm
 ("yeah, because I have all the time in the world", "skeptical"), ("oh sure, that'll work", "skeptical"),
 ("like that's ever going to happen", "skeptical"), ("great, another flat tyre", "skeptical"), ("just what I needed today", "skeptical"),
 # events
 ("the baby took her first steps today", "delight"), ("Dadi is coming home from the hospital tomorrow", "content"),
 ("my fever is gone", "content"), ("nobody came to my party", "sad"), ("the twins are fighting again", "fret"),
 ("my ice cream fell on the floor", "sad"), ("I don't want to go to school", "sad"), ("I lost my tooth!", "delight"),
 ("I can whistle now!", "delight"), ("my son never calls me", "sad"), ("my balloon flew away", "sad"),
 # typos
 ("im so hapyy", "happy"), ("so tird today", "drowsy"), ("im angy", "angry"), ("feeling sadd", "sad"), ("im scard", "worried"),
 ("so excted", "delight"),
 # to bot
 ("you got it wrong again", "apologetic"), ("that's not what I asked", "apologetic"), ("you never get it right", "apologetic"),
 # commands stay neutral
 ("set an alarm for six", None), ("turn on the fan", None), ("what's the weather like", None), ("call mom", None),
 ("add eggs to the list", None), ("is it okay to call now?", None), ("play some music", None),
]
ok = 0
for t, want in L:
    e, lv, a, why = R.read(t, model=False)
    good = (e in ("attentive", "curious", "listening", "searching", "thinking")) if want is None else e == want
    ok += good
    if not good or "-v" in sys.argv:
        print("XX" if not good else "OK", repr(t), "->", e, lv, why, "want", want)
print(f"{ok}/{len(L)}")
ts = []
for t, _ in L * 5:
    t0 = time.perf_counter(); R.read(t, model=False); ts.append(time.perf_counter() - t0)
print("read() mean %.1f us max %.1f us" % (1e6 * sum(ts) / len(ts), 1e6 * max(ts)))
