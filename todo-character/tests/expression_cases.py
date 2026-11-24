"""Hand-labelled test conditions for homebot.face.reading.read().

Expectations were written as a careful human reader BEFORE running read() on
any of them. They are NOT tuned to the code's output.

Single cases:
    expected        acceptable expressions (any one is a pass)
    expected_level  acceptable levels (list; more than one where a careful
                    reader genuinely could go either way)
Multi-emotion cases (category "multi"):
    expected        ordered list of beats, each {"accept": [...], "level": [...]}

Perspective: the face reacts to what the user said. For the user's own
feelings that means mirroring/empathising (user sad -> sad face). For
insults aimed at homebot it means homebot's own reaction (hurt/apologetic),
never glaring back at a family member.
"""

L, M, I = "low", "mid", "intense"

NEUTRAL = ["attentive", "listening", "rest", "answering"]


def S(id, category, text, expected, level, note):
    if isinstance(level, str):
        level = [level]
    return {"id": id, "category": category, "text": text,
            "expected": list(expected), "expected_level": list(level),
            "note": note}


def B(accept, level):
    if isinstance(level, str):
        level = [level]
    return {"accept": list(accept), "level": list(level)}


def MULTI(id, text, beats, note):
    return {"id": id, "category": "multi", "text": text,
            "expected": beats, "note": note}


CASES = [
    # ---------------- single words ----------------
    S("w01", "single_word", "sorry", ["apologetic"], [L, M], "bare apology"),
    S("w02", "single_word", "yay", ["delight", "happy", "grin"], [L, M], "small cheer"),
    S("w03", "single_word", "ugh", ["angry", "bored", "fret", "skeptical", "sad"], [L, M], "frustration grunt"),
    S("w04", "single_word", "hmm", ["thinking", "skeptical", "suspicious"], [L], "pondering / doubt"),
    S("w05", "single_word", "wow", ["surprised", "oh", "delight"], [L, M], "impressed surprise"),
    S("w06", "single_word", "ok", NEUTRAL + ["content"], [L], "plain acknowledgement"),
    S("w07", "single_word", "thanks", ["tender"], [L, M], "gratitude"),
    S("w08", "single_word", "lol", ["grin"], [L, M], "laugh"),
    S("w09", "single_word", "nooo", ["sad", "dread", "worried", "alarmed", "surprised", "fret"], [M, I], "elongated dismay"),

    # ---------------- plain emotions ----------------
    S("p01", "plain", "I'm feeling really happy today", ["happy", "delight", "content"], [M], "happy"),
    S("p02", "plain", "We won the match, this is amazing!", ["delight", "grin", "happy"], [M, I], "delight"),
    S("p03", "plain", "I love you homebot", ["love", "tender", "shy"], [M], "love"),
    S("p04", "plain", "Thank you for reminding me about the medicine", ["tender"], [M], "gratitude"),
    S("p05", "plain", "I'm feeling sad because my friend moved away", ["sad"], [M], "sad"),
    S("p06", "plain", "My grandmother passed away last night", ["crying", "sad"], [M], "grief"),
    S("p07", "plain", "The plumber didn't show up again, I'm furious", ["angry"], [M, I], "anger"),
    S("p08", "plain", "Stop it right now, that's your last warning", ["stern", "angry"], [M, I], "stern"),
    S("p09", "plain", "I'm worried about Aai's blood pressure", ["worried", "fret"], [M], "worry"),
    S("p10", "plain", "Emergency! There's a gas leak in the kitchen", ["dread", "alarmed", "startled"], [I], "emergency"),
    S("p11", "plain", "No way, the electricity bill is only 200 rupees", ["surprised", "oh", "delight"], [M], "surprise"),
    S("p12", "plain", "I don't understand how this washing machine works", ["confusion"], [M], "confusion"),
    S("p13", "plain", "Are you sure the shop is open on Sunday?", ["suspicious", "skeptical"], [M], "doubt question"),
    S("p14", "plain", "There's nothing to do this evening", ["bored"], [M], "boredom"),
    S("p15", "plain", "I'm exhausted after the long commute", ["drowsy"], [M], "tired"),
    S("p16", "plain", "I finished the whole marathon today", ["proud", "delight"], [M], "pride"),
    S("p17", "plain", "That's so embarrassing, everyone saw me fall", ["shy"], [M, I], "embarrassed"),
    S("p18", "plain", "Don't tell mom, but I ate the last laddoo", ["mischief", "grin"], [M], "mischief"),
    S("p19", "plain", "Haha that video was hilarious", ["grin"], [M], "laughing"),
    S("p20", "plain", "What is the capital of Australia?", ["curious", "thinking"], [M], "curious question"),
    S("p21", "plain", "Let me think about what to cook tonight", ["thinking"], [M], "thinking"),
    S("p22", "plain", "Sitting on the balcony with chai, feeling so relaxed", ["content"], [M], "content"),
    S("p23", "plain", "Ahh! Something just fell off the shelf!", ["startled", "alarmed", "surprised"], [I], "startle with no keyword"),
    S("p24", "plain", "I'm scared of the thunder", ["worried", "dread", "fret"], [M], "fear"),
    S("p25", "plain", "The kids are so sweet", ["happy", "tender", "love", "content"], [M], "affection without a listed keyword"),
    S("p26", "plain", "I'm mad at my brother", ["angry"], [M], "common anger word 'mad'"),

    # ---------------- same emotion, three strengths ----------------
    S("s01", "strength", "i'm a bit annoyed", ["angry"], [L], "annoyed low"),
    S("s02", "strength", "i'm annoyed", ["angry"], [M], "annoyed mid"),
    S("s03", "strength", "I AM SO ANNOYED!!!", ["angry"], [I], "annoyed intense"),
    S("s04", "strength", "i'm slightly happy with the result", ["happy", "content"], [L], "happy low"),
    S("s05", "strength", "i'm happy with the result", ["happy", "content"], [M], "happy mid"),
    S("s06", "strength", "I'M SO HAPPY WITH THE RESULT!!!", ["happy", "delight"], [I], "happy intense"),
    S("s07", "strength", "i'm a little sad today", ["sad"], [L], "sad low"),
    S("s08", "strength", "i'm sad today", ["sad"], [M], "sad mid"),
    S("s09", "strength", "i'm sooo sad today, really really sad!!", ["sad", "crying"], [I], "sad intense"),
    S("s10", "strength", "i'm kind of worried about the exam", ["worried", "fret"], [L], "worried low"),
    S("s11", "strength", "i'm worried about the exam", ["worried", "fret"], [M], "worried mid"),
    S("s12", "strength", "I'M REALLY WORRIED ABOUT THE EXAM!!", ["worried", "fret", "dread"], [I], "worried intense"),

    # ---------------- negation ----------------
    S("n01", "negation", "I'm not happy with the service", ["angry", "sad", "skeptical", "stern"], [M], "negated happy"),
    S("n02", "negation", "not bad at all", ["happy", "content"], [L, M], "double negative = positive"),
    S("n03", "negation", "I don't hate it", ["content", "skeptical", "happy"], [L], "grudging approval"),
    S("n04", "negation", "Don't worry, everything is fine", ["content", "happy", "tender"] + NEUTRAL, [L, M], "reassurance"),
    S("n05", "negation", "I'm not angry, just tired", ["drowsy"], [L, M], "denied anger, real state tired"),
    S("n06", "negation", "There's no emergency, relax", ["content"] + NEUTRAL, [L, M], "denied emergency"),
    S("n07", "negation", "I'm not sad anymore", ["content", "happy"], [M], "recovered"),

    # ---------------- sarcasm ----------------
    S("x01", "sarcasm", "oh great, another electricity bill", ["bored", "skeptical", "angry", "fret"], [M], "sarcastic great"),
    S("x02", "sarcasm", "wonderful, it's raining again", ["bored", "skeptical", "sad", "angry"], [M], "sarcastic wonderful"),
    S("x03", "sarcasm", "Perfect. The wifi is down again.", ["angry", "bored", "skeptical", "fret"], [M], "sarcastic perfect"),
    S("x04", "sarcasm", "Yeah right, like the plumber will come today", ["skeptical", "suspicious", "bored"], [M], "sarcastic disbelief"),

    # ---------------- household commands ----------------
    S("c01", "command", "add milk to the list", NEUTRAL + ["focused"], [L, M], "list command"),
    S("c02", "command", "remind me at 7:30 to take medicine", NEUTRAL + ["focused"], [L, M], "reminder"),
    S("c03", "command", "what's on the calendar today?", ["curious", "searching", "thinking"] + NEUTRAL, [L, M], "calendar query"),
    S("c04", "command", "turn off the lights", NEUTRAL, [L, M], "device command"),
    S("c05", "command", "set a timer for 10 minutes", NEUTRAL + ["focused"], [L, M], "timer"),
    S("c06", "command", "find my phone", ["searching"] + NEUTRAL, [L, M], "find"),
    S("c07", "command", "ADD MILK TO THE LIST", NEUTRAL + ["focused"], [L, M], "caps-lock command, not shouting emotion"),
    S("c08", "command", "Do not forget to buy onions", NEUTRAL + ["focused"], [L, M], "reminder phrased 'do not'"),

    # ---------------- Hinglish / romanised ----------------
    S("h01", "hinglish", "bahut khush hoon aaj", ["happy", "delight"], [M], "Hindi: very happy today"),
    S("h02", "hinglish", "mala bhook lagli", NEUTRAL, [L, M], "Marathi: I'm hungry (no emotion)"),
    S("h03", "hinglish", "yaar I'm so tired", ["drowsy"], [M], "Hinglish tired"),
    S("h04", "hinglish", "thank you beta", ["tender"], [L, M], "thanks to child"),
    S("h05", "hinglish", "mujhe bahut gussa aa raha hai", ["angry"], [M, I], "Hindi: I'm very angry"),
    S("h06", "hinglish", "bahut dukh hua sunke", ["sad"], [M], "Hindi: very sad to hear"),
    S("h07", "hinglish", "kya baat hai! zabardast", ["delight", "happy", "surprised"], [M, I], "Hindi: wow, fantastic"),
    S("h08", "hinglish", "arre yaar, phir se light chali gayi", ["bored", "angry", "sad", "fret"], [M], "power cut again, frustration"),
    S("h09", "hinglish", "mi khup thaklo aahe", ["drowsy"], [M], "Marathi: I'm very tired"),
    S("h10", "hinglish", "tension mat lo, sab theek hai", ["content", "tender", "happy"] + NEUTRAL, [L, M], "Hindi: don't worry, all fine"),
    S("h11", "hinglish", "abhi nahi, baad mein", ["attentive", "rest", "bored", "skeptical"], [L, M], "Hindi: not now, later"),
    S("h12", "hinglish", "aai ko bahut miss kar rahi hoon", ["sad", "love", "tender"], [M], "missing mother"),

    # ---------------- Devanagari ----------------
    S("d01", "devanagari", "मी खूप खुश आहे", ["happy", "delight"], [M, I], "Marathi: I'm very happy"),
    S("d02", "devanagari", "मुझे दुख है", ["sad"], [M], "Hindi: I'm sad"),
    S("d03", "devanagari", "धन्यवाद", ["tender"], [L, M], "thank you"),
    S("d04", "devanagari", "मुझे बहुत गुस्सा आ रहा है", ["angry"], [M, I], "Hindi: very angry"),
    S("d05", "devanagari", "मला भीती वाटते", ["worried", "dread", "fret"], [M], "Marathi: I'm afraid"),
    S("d06", "devanagari", "आज मैं बहुत थक गया हूँ", ["drowsy"], [M], "Hindi: very tired today"),

    # ---------------- emoji ----------------
    S("e01", "emoji", "😂😂", ["grin"], [M, I], "laughing emoji"),
    S("e02", "emoji", "❤️", ["love", "tender"], [L, M], "heart"),
    S("e03", "emoji", "great 😡", ["angry"], [M], "angry emoji overrides word"),
    S("e04", "emoji", "😭", ["crying", "sad"], [M], "crying emoji"),
    S("e05", "emoji", "👍", ["content", "happy"] + NEUTRAL, [L], "thumbs up"),
    S("e06", "emoji", "thanks 🙏", ["tender"], [L, M], "thanks with folded hands"),

    # ---------------- typos / elongation ----------------
    S("t01", "typo", "sooooo happyyy", ["happy", "delight"], [I], "double elongation"),
    S("t02", "typo", "thnks", ["tender"], [L, M], "typo thanks"),
    S("t03", "typo", "angery", ["angry"], [L, M], "typo angry"),
    S("t04", "typo", "im realy worryed", ["worried", "fret"], [M], "typos"),
    S("t05", "typo", "yaaaay!!!", ["delight", "happy", "grin"], [I], "elongated cheer"),
    S("t06", "typo", "sorrry", ["apologetic"], [L, M], "elongated sorry"),

    # ---------------- edge cases ----------------
    S("g01", "edge", "", NEUTRAL, [L], "empty"),
    S("g02", "edge", "   ", NEUTRAL, [L], "whitespace"),
    S("g03", "edge", "!!!", ["surprised", "startled", "alarmed", "oh"] + NEUTRAL, [M, I], "bangs only"),
    S("g04", "edge", ("so today I went to the market and bought vegetables and the auto "
                      "guy took the long route and then I met Sharma aunty and we talked "
                      "about her son and his job in Pune and then I came home and made dal "
                      "and now I'm just sitting here wondering if I locked the car"),
      ["thinking", "worried", "fret"] + NEUTRAL, [L, M], "long ramble ending in mild doubt"),
    S("g05", "edge", "12345", NEUTRAL, [L], "numbers only"),
    S("g06", "edge", "why would you do that?!", ["angry", "stern", "confusion", "surprised"], [M, I], "angry question"),
    S("g07", "edge", "WHY IS THE GEYSER NOT WORKING???", ["angry", "fret", "confusion"], [I], "shouted frustrated question"),

    # ---------------- substring false positives (from the real keyword list) ----------------
    S("f01", "substring", "I'm reading about the crusades", ["curious", "focused", "thinking"] + NEUTRAL, [M], "'sad' inside crusades"),
    S("f02", "substring", "The Diwali fireworks were beautiful", ["delight", "happy", "content"], [M], "'fire' inside fireworks"),
    S("f03", "substring", "Whatever you think is fine", ["content", "bored", "skeptical"] + NEUTRAL, [M], "'hate' inside whatever"),
    S("f04", "substring", "Grandpa wants to bestow his watch on Rohan", ["tender", "happy", "content"] + NEUTRAL, [M], "'best' inside bestow"),
    S("f05", "substring", "We need to rethink the budget", ["thinking", "focused"], [M], "'think' inside rethink (true positive control)"),
    S("f06", "substring", "My phone battery died", ["bored", "sad", "fret", "skeptical"] + NEUTRAL, [M], "'died' about a battery"),
    S("f07", "substring", "The truck hurtled past our gate", ["startled", "surprised", "alarmed", "worried"] + NEUTRAL, [M], "'hurt' inside hurtled"),
    S("f08", "substring", "I'm unhappy with the new maid", ["sad", "angry", "skeptical"], [M], "'happy' inside unhappy"),
    S("f09", "substring", "I'm so uncomfortable in this heat", ["fret", "sad", "angry", "drowsy", "worried"], [M], "'comfortable' inside uncomfortable"),
    S("f10", "substring", "They are coming for dinner at 8", NEUTRAL + ["happy", "content"], [M], "'hey' inside they"),
    S("f11", "substring", "Mom is at the secretary's office", NEUTRAL, [M], "'secret' inside secretary"),
    S("f12", "substring", "Good enough, let's go", ["content", "happy"] + NEUTRAL, [L, M], "'enough' in good enough"),
    S("f13", "substring", "The census officer came today", NEUTRAL, [M], "'sus' inside census"),
    S("f14", "substring", "I'm displeased with the result", ["angry", "sad", "skeptical"], [M], "'pleased' inside displeased"),
    S("f15", "substring", "I bought a lollipop for Riya", NEUTRAL + ["happy", "content"], [M], "'lol' inside lollipop"),
    S("f16", "substring", "I'll be in Delhi tomorrow", NEUTRAL, [M], "'hi ' at end of Delhi"),
    S("f17", "substring", "He was crying with laughter", ["grin"], [M], "'crying' meaning laughing"),
    S("f18", "substring", "I really think we should go", ["thinking"] + NEUTRAL, [M], "'really' is an intensifier, not surprise"),
    S("f19", "substring", "That's the worst-case scenario, let's plan for it", ["thinking", "focused", "worried"], [M], "'worst' in worst-case"),
    S("f20", "substring", "I accidentally deleted the photos", ["fret", "worried", "sad", "apologetic"], [M], "'accident' inside accidentally -> dread?"),
    S("f21", "substring", "The glass is perfectly clean now", ["content", "happy"] + NEUTRAL, [M], "'perfect' inside perfectly"),
    S("f22", "substring", "Abhi nahi bhi chalega", NEUTRAL + ["content"], [M], "'hi ' inside abhi/nahi/bhi (Hindi)"),

    # ---------------- user reacting to homebot ----------------
    S("r01", "to_bot", "you're useless", ["sad", "apologetic", "fret"], [L, M], "insult -> hurt, not glare"),
    S("r02", "to_bot", "good job homebot", ["proud", "happy", "delight", "shy"], [M], "praise"),
    S("r03", "to_bot", "you're so cute", ["shy", "happy", "love"], [M], "compliment"),
    S("r04", "to_bot", "homebot you're the best", ["proud", "shy", "happy", "delight", "love"], [M], "praise"),
    S("r05", "to_bot", "I hate you", ["sad", "apologetic", "fret"], [M], "insult -> hurt"),
    S("r06", "to_bot", "thank you homebot, you're a lifesaver", ["tender", "happy", "proud"], [M], "gratitude"),

    # ---------------- multi-emotion paragraphs ----------------
    MULTI("m01", "I got the job offer! But it's in Bangalore and I'll miss everyone.",
          [B(["delight", "happy"], [M, I]), B(["sad"], [M])], "good news then sadness"),
    MULTI("m02", "Sorry I forgot to pay the bill. Thanks for reminding me though.",
          [B(["apologetic"], [M]), B(["tender"], [M])], "apology then thanks"),
    MULTI("m03", "I was so worried about the test results. Thank god, everything is normal.",
          [B(["worried", "fret"], [M]), B(["content", "happy", "tender"], [M])], "worry then relief"),
    MULTI("m04", "Haha that joke was good. Anyway, my uncle passed away this morning.",
          [B(["grin"], [M]), B(["crying", "sad"], [M])], "joke then grief"),
    MULTI("m05", "I'm furious that the bank charged me twice. Can you check the statement?",
          [B(["angry"], [M, I]), B(["searching", "curious", "attentive", "thinking"], [M])], "anger then request"),
    MULTI("m06", "Happy birthday Aai! I'm sad I can't be there.",
          [B(["delight", "happy", "love"], [M, I]), B(["sad"], [M])], "celebration then sadness"),
    MULTI("m07", "The geyser is broken again. Ugh, I'm so fed up. Can you call the plumber?",
          [B(["fret", "angry", "bored", "sad"], [M]), B(["angry"], [M, I]), B(NEUTRAL + ["curious"], [M])],
          "frustration build then request"),
    MULTI("m08", "Wow, you remembered my birthday! I'm touched, thank you.",
          [B(["surprised", "delight", "oh"], [M, I]), B(["tender", "love"], [M])], "surprise then gratitude"),
    MULTI("m09", "I'm tired after work. But I'm happy to see the kids.",
          [B(["drowsy"], [M]), B(["happy", "content"], [M])], "tired then happy"),
    MULTI("m10", "There was an accident on the highway. Thankfully nobody was hurt. I'm still shaking.",
          [B(["dread", "alarmed", "worried"], [M]), B(["content", "tender", "happy"], [M]),
           B(["worried", "dread", "fret"], [M])], "fright, relief, residual fear"),
    MULTI("m11", "I'm bored. What should we do this weekend?",
          [B(["bored"], [L, M]), B(["curious", "thinking"], [M])], "bored then question"),
    MULTI("m12", "I failed my driving test. I'm so embarrassed. I'll try again next week.",
          [B(["sad"], [M]), B(["shy"], [M]), B(["focused", "proud", "content", "attentive"], [M])],
          "failure, embarrassment, resolve"),
    MULTI("m13", "Mom is in the hospital. I'm scared. Please remind me to call her at 6.",
          [B(["worried", "sad", "dread"], [M]), B(["worried", "dread", "fret"], [M]), B(NEUTRAL + ["focused"], [M])],
          "bad news, fear, command"),
    MULTI("m14", "I can't believe it, we won the lottery! Wait, is this a scam?",
          [B(["surprised", "delight"], [M, I]), B(["suspicious", "skeptical"], [M])], "joy then suspicion"),
    MULTI("m15", "I love you beta. But you need to stop playing games all night.",
          [B(["love", "tender"], [M]), B(["stern"], [M])], "affection then discipline"),
    MULTI("m16", "Sorry, I yelled at you earlier. I was just stressed about work.",
          [B(["apologetic"], [M]), B(["worried", "fret", "sad", "drowsy"], [M])], "apology then explanation"),
    MULTI("m17", "Great news, the visa got approved! Now I'm nervous about the flight.",
          [B(["delight", "happy"], [M, I]), B(["worried", "fret"], [M])], "good news then nerves"),
    MULTI("m18", "I don't understand this bill at all. Oh wait, I see it now, it includes the deposit. Makes sense!",
          [B(["confusion"], [M]), B(["surprised", "oh", "happy", "content", "thinking"], [M]),
           B(["content", "happy"], [M])], "confusion then realisation"),
    MULTI("m19", "That movie was hilarious. But the ending made me cry.",
          [B(["grin"], [M]), B(["sad", "crying"], [M])], "laugh then sad"),
    MULTI("m20", "Good morning homebot! I'm feeling lazy today, so no rush.",
          [B(["listening", "happy", "attentive"], [M]), B(["drowsy", "content", "bored"], [L, M])],
          "greeting then lazy"),
    MULTI("m21", "I'm so proud of you for finishing the project. Take a rest now, you must be exhausted.",
          [B(["tender", "proud", "love", "happy"], [M]), B(["tender", "content", "drowsy"], [M])],
          "pride in someone, then care"),
    MULTI("m22", "The neighbour's dog bit Riya. She's okay but I'm really angry at them.",
          [B(["alarmed", "dread", "worried", "sad", "startled"], [M]), B(["angry"], [M, I])],
          "fright then anger"),
    MULTI("m23", "Hmm, are you sure that's the right address? Okay, if you say so. Let's go.",
          [B(["suspicious", "skeptical", "thinking"], [M]), B(["skeptical"], [L, M]), B(NEUTRAL + ["content"], [L, M])],
          "doubt, grudging acceptance, move on"),
    MULTI("m24", "Diwali was wonderful this year! But Ajoba wasn't with us, and that hurt.",
          [B(["delight", "happy"], [M, I]), B(["sad", "crying"], [M])], "joy then loss"),
    MULTI("m25", "I'm worried I'll be late. Oh good, the traffic is clear. Phew!",
          [B(["worried", "fret"], [M]), B(["content", "happy", "delight"], [M])], "worry then relief"),
]


# ---------------------------------------------------------------------------
# Extra probes (not counted in the headline accuracy).
#
# SUBSTRING_PROBES: ordinary household sentences that contain one of the real
# keywords inside another word / another sense. `must_not` is the family a
# careful reader says this sentence must NOT trigger.
# ---------------------------------------------------------------------------

SUBSTRING_PROBES = [
    ("I studied all night for the exam", "crying", "'died' inside studied"),
    ("My father retired last year", "drowsy", "'tired' inside retired"),
    ("Mehndi function is tomorrow at 5", "bored", "'meh' inside mehndi"),
    ("Mehta uncle is coming over", "bored", "'meh' inside Mehta"),
    ("Bring the prasad from the temple", "sad", "'sad' inside prasad"),
    ("Sadashiv kaka called", "sad", "'sad' inside Sadashiv"),
    ("Can you help me with my homework", "dread", "'help me' as a request"),
    ("Help me find my keys", "dread", "'help me' as a request"),
    ("Update the emergency contact list", "dread", "'emergency' as a noun"),
    ("Rahul got fired from his job", "dread", "'fire' inside fired"),
    ("Buy firewood for the bonfire", "dread", "'fire' inside firewood"),
    ("Please take out the rubbish", "angry", "'rubbish' = trash (Indian English)"),
    ("Do we have enough rice for tonight", "stern", "'enough' as a quantity"),
    ("Turn on do not disturb mode", "stern", "'do not' in a feature name"),
    ("She is being pushy about the wedding", "shy", "'shy' inside pushy"),
    ("They said the bus is late", "listening", "'hey' inside they"),
    ("Is this plastic sustainable", "suspicious", "'sus' inside sustainable"),
    ("Jesus, that was loud", "suspicious", "'sus' inside Jesus"),
    ("The milk is best before Monday", "delight", "'best' in best-before"),
    ("Take care of the electricity bill", "tender", "'take care of' = handle"),
    ("Please research flights to Goa", "searching", "control: research -> searching is fine; must_not is a dummy"),
    ("Happy Thanksgiving to the cousins in the US", "tender", "'thanks' inside Thanksgiving"),
    ("I'll explain later, I'm driving", "thinking", "'explain' as deferral"),
    ("Yahi rakh do, kabhi bhi le lena", "listening", "'hi ' inside yahi/kabhi/bhi"),
    ("He spoke calmly but he was angry", "content", "'calm' inside calmly"),
    ("Abhi aata hoon", "listening", "'hi ' inside abhi"),
]
# the research probe's must_not is a deliberate control and is skipped in counts
SUBSTRING_CONTROL = {"Please research flights to Goa"}

# SHADOW_PROBES: an earlier family's keyword co-occurs with the real (later or
# stronger) emotion. `expected` is the acceptable set for the whole sentence.
SHADOW_PROBES = [
    ("I'm really tired", ["drowsy"], "'really' (surprised) beats tired"),
    ("I'm really bored", ["bored"], "'really' beats bored"),
    ("I really don't understand this form", ["confusion"], "'really' beats confusion"),
    ("I'm really embarrassed", ["shy"], "'really' beats shy"),
    ("seriously, I'm exhausted", ["drowsy"], "'seriously' beats exhausted"),
    ("Sorry to hear your father died", ["sad", "crying", "tender"], "condolence: apologetic beats grief"),
    ("I'm so happy I'm crying", ["delight", "happy"], "tears of joy -> crying"),
    ("Thanks, but I'm heartbroken", ["crying", "sad"], "thanks beats heartbroken"),
    ("Good night, I'm going to bed", ["asleep", "tender", "drowsy"], "acceptable either way - control"),
    ("Take care, I'm terrified for you", ["dread", "worried"], "thanks/care beats terror"),
    ("I'm proud of myself, I finished the report", ["proud"], "control: proud family"),
    ("I'm proud of myself", ["proud"], "no 'proud' keyword in proud family"),
    ("I'm so worried, what if it's an emergency", ["worried", "dread"], "control"),
    ("Thank you so much, I'm so happy", ["delight", "happy", "tender"], "control"),
    ("I'm happy but also really worried", ["worried", "happy", "fret"], "happy first, worry lost - judge: either"),
    ("I think I'm going to cry", ["sad", "crying"], "'think' is the hedge; sad lost"),
    ("I think my mother is sick, I'm scared", ["worried", "dread"], "'scared' wins (worried earlier than thinking)"),
    ("Sorry, I'm so tired today", ["drowsy", "apologetic"], "control: either acceptable"),
    ("Hey, I'm feeling sad", ["sad"], "control: greeting then sad"),
    ("Hello, the house is on fire!", ["dread", "alarmed", "startled"], "control"),
]

# LEVEL_PROBES: pairs that differ only by a substring that the level scorer
# misreads. A careful reader gives both the SAME level.
LEVEL_PROBES = [
    ("going to the supermarket!", "going to the shop!", "'super' inside supermarket"),
    ("every day is the same!", "each day is the same!", "'ever' inside every"),
    ("I never said that!", "I didn't say that!", "'ever' inside never"),
    ("so that we can leave early!", "then we can leave early!", "'so ' as conjunction"),
    ("pay the EMI today", "pay the loan today", "acronym counted as shouting"),
    ("send the OTP to Aai", "send the code to Aai", "acronym counted as shouting"),
    ("I'd rather stay home today", "I'd prefer to stay home today", "'rather' as preference"),
    ("just a reminder, the gas man comes at 4", "reminder, the gas man comes at 4", "'just a' as filler"),
    ("hmmm ok", "hmm ok", "elongated hmm"),
    ("the www site is down", "the web site is down", "'www' counted as elongation"),
    ("the kids are absolutely fine", "the kids are fine", "control: real intensifier - judge: may differ"),
]
LEVEL_CONTROL = {"the kids are absolutely fine"}
