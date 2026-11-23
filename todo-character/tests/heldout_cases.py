"""HELD-OUT cases for homebot.face.reading (verification round 3).

Written BEFORE running read() on any of them, as a careful human reader,
and never adjusted afterwards. None of these sentences appear in
expression_cases.py or conversations.py. Many deliberately use words that
are NOT in reading.py's lexicon, because the previous suite was partly
fitted to its own cases.

Perspective as in expression_cases.py: mirror the user's feeling; for lines
aimed at homebot, homebot's own reaction (hurt / shy / pleased).
"""

L, M, I = "low", "mid", "intense"
N = ["attentive", "listening", "rest", "answering"]          # neutral
REQ = N + ["focused", "searching", "curious", "thinking"]     # a chore / request


def S(id, cat, text, accept, level):
    return {"id": id, "category": cat, "text": text, "expected": list(accept),
            "expected_level": [level] if isinstance(level, str) else list(level)}


def B(accept, level):
    return {"accept": list(accept), "level": [level] if isinstance(level, str) else list(level)}


def MULTI(id, text, beats):
    return {"id": id, "category": "multi", "text": text, "expected": beats}


HAPPY = ["happy", "delight", "content", "grin"]
JOY = ["delight", "happy", "proud"]
SADF = ["sad", "crying"]
WORRY = ["worried", "fret", "dread"]
ANGRY = ["angry", "stern"]
HURT = ["sad", "apologetic", "fret", "shy"]
PLEASED = ["shy", "happy", "love", "proud", "tender", "delight"]

CASES = [
    # ------------- plain, all emotions x three strengths (new wording) -----
    S("p01", "plain", "the new curtains look kind of nice", HAPPY, [L, M]),
    S("p02", "plain", "I'm really happy with how the party went", HAPPY, [M, I]),
    S("p03", "plain", "I AM SO INCREDIBLY HAPPY RIGHT NOW!!!", JOY, I),
    S("p04", "plain", "I'm a bit down today", SADF, [L, M]),
    S("p05", "plain", "I feel really sad about Nani", SADF, [M, I]),
    S("p06", "plain", "I'm completely heartbroken, she's gone", ["crying", "sad"], I),
    S("p07", "plain", "I'm slightly annoyed with the plumber", ANGRY + ["bored"], [L, M]),
    S("p08", "plain", "The neighbour's dog barked all night and I'm angry", ANGRY, M),
    S("p09", "plain", "I AM ABSOLUTELY LIVID WITH THE BANK", ANGRY, I),
    S("p10", "plain", "a little worried about the exam tomorrow", WORRY, [L, M]),
    S("p11", "plain", "I'm really nervous about the interview", WORRY, [M, I]),
    S("p12", "plain", "I'm terrified, there's someone outside the door", ["dread", "alarmed", "worried"], I),
    S("p13", "plain", "kinda sleepy", ["drowsy", "yawn"], [L, M]),
    S("p14", "plain", "I am exhausted after the wedding", ["drowsy"], [M, I]),
    S("p15", "plain", "wow, I didn't expect that", ["surprised", "oh"], M),
    S("p16", "plain", "WHAT?! The flat got sold already?!", ["surprised", "startled", "alarmed", "angry"], I),
    S("p17", "plain", "I'm grateful you reminded me", ["tender"], M),
    S("p18", "plain", "I'm so bored, nothing on TV", ["bored"], [M, I]),
    S("p19", "plain", "I'm a little confused about the new remote", ["confusion"], [L, M]),
    S("p20", "plain", "I am so proud of myself, I ran 5 km today", ["proud", "delight", "happy"], [M, I]),
    S("p21", "plain", "I'm feeling peaceful after the puja", ["content", "happy"], [L, M]),
    S("p22", "plain", "I'm thrilled about the trip to Goa", JOY, [M, I]),
    S("p23", "plain", "ugh, I'm so lonely these days", SADF, [M, I]),
    S("p24", "plain", "I'm embarrassed, I sang in front of everyone", ["shy"], M),
    S("p25", "plain", "the soup is delicious", HAPPY, [L, M]),
    S("p26", "plain", "I'm overjoyed, the baby is here!", JOY, I),
    S("p27", "plain", "I feel miserable with this cold", SADF + ["drowsy"], M),
    S("p28", "plain", "I'm scared of the thunder", WORRY + ["startled"], M),
    S("p29", "plain", "I'm frustrated, the app keeps logging me out", ANGRY + ["fret"], M),
    S("p30", "plain", "it was a pleasant evening", HAPPY, [L, M]),

    # ------------- negation (new forms) -----------------------------------
    S("n01", "negation", "I wouldn't say I'm happy", ["sad", "skeptical", "bored"] + N, [L, M]),
    S("n02", "negation", "no I'm not angry", ["content"] + N, [L, M]),
    S("n03", "negation", "not too bad", ["content", "happy"], [L, M]),
    S("n04", "negation", "I'm not worried at all", ["content"] + N, [L, M]),
    S("n05", "negation", "it's not that I'm sad, just tired", ["drowsy"], [L, M]),
    S("n06", "negation", "I can't say I'm excited about it", ["sad", "bored", "skeptical"] + N, [L, M]),
    S("n07", "negation", "never been this happy", JOY, [M, I]),
    S("n08", "negation", "I'm not unhappy", ["content", "happy"] + N, [L, M]),
    S("n09", "negation", "no need to apologise", ["content", "tender"] + N, [L, M]),
    S("n10", "negation", "I don't feel well", ["sad", "worried", "drowsy"], M),

    # ------------- Hinglish / Marathi, both scripts, NEW words -------------
    S("h01", "hinglish", "aaj mood bahut kharab hai", SADF + ["angry"], M),
    S("h02", "hinglish", "yaar main bahut thak gaya hoon", ["drowsy"], [M, I]),
    S("h03", "hinglish", "bahut maza aaya kal", HAPPY, [M, I]),
    S("h04", "hinglish", "mujhe darr lag raha hai", WORRY, M),
    S("h05", "hinglish", "kitna sundar hai ye", HAPPY + ["love"], M),
    S("h06", "hinglish", "kya bakwaas hai yeh", ANGRY + ["skeptical"], M),
    S("h07", "hinglish", "mala khup bara vatla", HAPPY + ["tender"], M),
    S("h08", "hinglish", "mi khup kantalo aahe", ["bored", "drowsy"], M),
    S("h09", "hinglish", "bas kar yaar, irritate mat kar", ANGRY, M),
    S("h10", "hinglish", "Bhai, mubarak ho!", JOY, [M, I]),
    S("d01", "devanagari", "मुझे बहुत अच्छा लग रहा है", HAPPY, M),
    S("d02", "devanagari", "मैं बहुत परेशान हूँ", WORRY + SADF, [M, I]),
    S("d03", "devanagari", "आज मी खूप आनंदी आहे", HAPPY, [M, I]),
    S("d04", "devanagari", "मला भीती वाटते", WORRY, M),
    S("d05", "devanagari", "रोज़ सुबह दूध लाना", REQ, M),
    S("d06", "devanagari", "रोटी बना दो", REQ, M),
    S("d07", "devanagari", "चिड़िया खिड़की पर बैठी है", N + ["curious", "happy"], [L, M]),
    S("d08", "devanagari", "आनंद अंकल आ रहे हैं", N + ["happy", "listening"], [L, M]),
    S("d09", "devanagari", "मुझे बहुत गुस्सा आ रहा है", ANGRY, [M, I]),
    S("d10", "devanagari", "झोपडी के पास गाड़ी खड़ी है", N, [L, M]),

    # ------------- emoji combos -------------------------------------------
    S("e01", "emoji", "I got the job!! 😭😭", JOY + ["tender"], I),
    S("e02", "emoji", "worst day ever 😂", ["grin", "sad", "skeptical"], M),
    S("e03", "emoji", "😤😤", ANGRY + ["fret"], M),
    S("e04", "emoji", "dinner ready? 😋", HAPPY + ["curious"], [L, M]),
    S("e05", "emoji", "my phone fell in the toilet 🤦", ["fret", "sad", "worried", "alarmed"], M),
    S("e06", "emoji", "💀💀 that video", ["grin"], M),
    S("e07", "emoji", "thank you 🙏❤️", ["tender", "love"], M),
    S("e08", "emoji", "results tomorrow 😬", WORRY, M),

    # ------------- typos ---------------------------------------------------
    S("t01", "typo", "im so exhuasted", ["drowsy"], [M, I]),
    S("t02", "typo", "thankyou so much", ["tender"], [M, I]),
    S("t03", "typo", "im realy sad", SADF, M),
    S("t04", "typo", "that was amazng", JOY, M),
    S("t05", "typo", "im scarred of the dark", WORRY, M),
    S("t06", "typo", "sooo hapyyy", JOY, [M, I]),

    # ------------- sarcasm --------------------------------------------------
    S("s01", "sarcasm", "oh fantastic, the geyser is leaking again", ["skeptical", "angry", "bored", "fret"], M),
    S("s02", "sarcasm", "yeah, because that always works", ["skeptical", "bored"], M),
    S("s03", "sarcasm", "great, just great. The milk went off.", ["skeptical", "angry", "bored", "sad", "fret"], M),
    S("s04", "sarcasm", "wow, thanks a lot for nothing", ["skeptical", "angry", "sad"], M),
    S("s05", "sarcasm", "love that for me, stuck in traffic again", ["skeptical", "bored", "angry"], M),

    # ------------- substring / word traps on the NEW lexicon ---------------
    S("x01", "substring", "Thakur ji called about the rent", N, [L, M]),
    S("x02", "substring", "Anand uncle is coming at six", N + ["happy"], [L, M]),
    S("x03", "substring", "take the bus stop near the temple", REQ, M),
    S("x04", "substring", "he passed the salt", N, [L, M]),
    S("x05", "substring", "yes exactly, put it there", N + ["focused", "content"], [L, M]),
    S("x06", "substring", "fire up the oven to 180", REQ, M),
    S("x07", "substring", "the bag is very bhari, help me lift it", REQ + ["fret"], M),
    S("x08", "substring", "Dad doesn't smoke anymore", N + ["content", "happy"], [L, M]),
    S("x09", "substring", "the phone battery dies so fast", ["fret", "bored", "angry"] + N, [L, M]),
    S("x10", "substring", "this thinkpad is old", N + ["bored"], [L, M]),
    S("x11", "substring", "the train was bang on time", HAPPY + N, [L, M]),
    S("x12", "substring", "it's a far cry from the old house", N + ["thinking", "content"], [L, M]),

    # ------------- context traps --------------------------------------------
    S("c01", "context", "I'm dying to see the movie", JOY + ["curious"], [M, I]),
    S("c02", "context", "this cake is to die for", HAPPY + ["love"], [M, I]),
    S("c03", "context", "she's killing it at work", JOY, M),
    S("c04", "context", "the movie was sick", JOY + ["grin"], M),
    S("c05", "context", "I nearly died laughing", ["grin"], [M, I]),
    S("c06", "context", "you're on fire today", JOY + ["grin"], M),
    S("c07", "context", "I fell in love with this song", ["love", "happy", "delight"], M),
    S("c08", "context", "that's crazy good", JOY, M),

    # ------------- household commands ---------------------------------------
    S("k01", "command", "set an alarm for 6:15", REQ, M),
    S("k02", "command", "remind me to pay the electricity bill", REQ, M),
    S("k03", "command", "turn off the hall light", REQ, M),
    S("k04", "command", "add Parle-G and Surf Excel to the list", REQ, M),
    S("k05", "command", "what's on the calendar this Sunday?", REQ, M),
    S("k06", "command", "play some old Kishore Kumar songs", REQ, M),
    S("k07", "command", "note that the maid is off on Friday", REQ, M),
    S("k08", "command", "call the society office", REQ, M),

    # ------------- to homebot ------------------------------------------------
    S("b01", "to_bot", "you're an idiot", HURT, M),
    S("b02", "to_bot", "homebot you're so annoying", HURT, M),
    S("b03", "to_bot", "you're brilliant, homebot", PLEASED, M),
    S("b04", "to_bot", "good boy homebot", PLEASED, M),
    S("b05", "to_bot", "you never listen to me", HURT, M),
    S("b06", "to_bot", "you're the worst robot ever", HURT, [M, I]),
    S("b07", "to_bot", "I like talking to you", PLEASED, M),
    S("b08", "to_bot", "shut up homebot", HURT + ["stern"], M),

    # ------------- over-trigger probes ---------------------------------------
    S("o01", "overtrigger", "Grandpa is in the ICU!", WORRY + ["alarmed", "sad"], [M, I]),
    S("o02", "overtrigger", "the flight is cancelled!", ["sad", "angry", "fret", "worried", "surprised"], [M, I]),
    S("o03", "overtrigger", "I lost my wallet!", WORRY + ["sad", "alarmed"], [M, I]),
    S("o04", "overtrigger", "terrible news 🙂", SADF + WORRY + ["skeptical"], M),
    S("o05", "overtrigger", "I'm fine 🙂", ["content", "happy"] + N, [L, M]),
]

MULTI_CASES = [
    MULTI("mm01", "We bought a new car! The EMI is scary though.",
          [B(JOY, [M, I]), B(WORRY, M)]),
    MULTI("mm02", "Papa's surgery went well. I'm so relieved.",
          [B(HAPPY + ["tender"], M), B(["content", "happy"], [M, I])]),
    MULTI("mm03", "I failed my driving test. Can you book another slot?",
          [B(SADF, M), B(REQ, M)]),
    MULTI("mm04", "The power went out. I'm scared of the dark.",
          [B(N + ["fret", "worried", "surprised"], [L, M]), B(WORRY, M)]),
    MULTI("mm05", "Thanks for the reminder. I would have totally forgotten.",
          [B(["tender"], M), B(N + ["oh", "apologetic", "content", "tender"], [L, M])]),
    MULTI("mm06", "I'm so angry at Rohan! He broke my laptop.",
          [B(ANGRY, [M, I]), B(ANGRY + ["fret", "sad"], M)]),
    MULTI("mm07", "Haha you're funny. Now set a timer for the rice.",
          [B(["grin", "happy"], M), B(REQ, M)]),
    MULTI("mm08", "My cat is missing. I've looked everywhere. Please help me.",
          [B(WORRY + SADF, M), B(WORRY + ["searching", "sad", "fret"], M), B(WORRY + ["alarmed"], [M, I])]),
    MULTI("mm09", "Wow! Sneha topped her class. I'm so proud of her.",
          [B(["surprised", "delight"], [M, I]), B(JOY, [M, I]), B(["proud", "tender", "happy", "delight"], [M, I])]),
    MULTI("mm10", "I'm bored. What should we do today?",
          [B(["bored"], M), B(["curious", "thinking"] + N, M)]),
    MULTI("mm11", "Sorry I yelled at you. I was stressed about work.",
          [B(["apologetic"], M), B(WORRY, M)]),
    MULTI("mm12", "The wedding was beautiful. But I cried when she left.",
          [B(HAPPY + ["tender", "love"], M), B(SADF + ["tender"], M)]),
    MULTI("mm13", "I can't find my keys! Wait, found them. Phew.",
          [B(WORRY + ["searching"], M), B(N + ["oh", "content", "surprised"], [L, M]), B(["content"], [L, M])]),
    MULTI("mm14", "Ugh, Monday again. At least it's sunny.",
          [B(["bored", "sad", "skeptical"], M), B(HAPPY, [L, M])]),
    MULTI("mm15", "Dadi is in hospital. The doctor says she'll be fine.",
          [B(WORRY + ["sad"], M), B(["content", "happy"], [L, M])]),
    MULTI("mm16", "I love you homebot. Good night!",
          [B(["love", "tender"], M), B(["asleep", "drowsy", "happy", "tender"], [L, M])]),
    MULTI("mm17", "The cake burnt. The guests arrive in ten minutes!",
          [B(["sad", "fret", "worried", "alarmed"], M), B(WORRY + ["alarmed"], [M, I])]),
    MULTI("mm18", "Nobody remembered my birthday. Not even my brother.",
          [B(SADF, M), B(SADF, M)]),
    MULTI("mm19", "I'm exhausted. But we won the match!",
          [B(["drowsy"], M), B(JOY, [M, I])]),
    MULTI("mm20", "That's hilarious. Okay, I need to focus now.",
          [B(["grin"], M), B(["focused"] + N, M)]),
    MULTI("mm21", "Hmm, are you sure? That doesn't sound right.",
          [B(["suspicious", "skeptical"], M), B(["suspicious", "skeptical", "confusion"], M)]),
    MULTI("mm22", "मुझे नौकरी मिल गई! पर मैं घर से दूर रहूँगा।",
          [B(JOY, [M, I]), B(SADF, M)]),
    MULTI("mm23", "Aaj result aaya. Main pass ho gaya!",
          [B(N + ["curious", "worried"], [L, M]), B(JOY, [M, I])]),
    MULTI("mm24", "I hate this traffic. Anyway, how was your day?",
          [B(ANGRY + ["bored"], M), B(["curious"] + N, M)]),
    MULTI("mm25", "Whoa, the lights flickered. Is there a storm?",
          [B(["surprised", "startled", "oh"], M), B(["curious", "worried"], M)]),
    MULTI("mm26", "I'm nervous about the results. Fingers crossed. Wish me luck!",
          [B(WORRY, M), B(WORRY + N + ["content"], [L, M]), B(WORRY + HAPPY + ["tender"], M)]),
    MULTI("mm27", "OMG the baby walked! She took three steps!",
          [B(["surprised", "delight"], [M, I]), B(JOY, [M, I])]),
    MULTI("mm28", "I'm sad Ria moved away. I'll call her tonight.",
          [B(SADF, M), B(N + ["content", "happy"], [L, M])]),
]
