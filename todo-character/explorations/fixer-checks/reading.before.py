"""Read a sentence, choose a face.

Two separate questions, and they have different answers in the text:

    WHICH expression?   from what the sentence is ABOUT
    WHICH of its three levels?   from how it is WRITTEN

That split matters. "I'm annoyed" and "I AM SO ANNOYED!!!" pick the same
expression and different levels, and the level signal is carried almost
entirely by things that are not words - capitals, repeated letters, stacked
exclamation marks, intensifiers. Treating them as one problem is why most
chatbot avatars have three faces and use one of them.

This is deliberately rule-based and local. It runs well under a millisecond
on a Pi with no model loaded, and it is inspectable: when he pulls the wrong
face you can see exactly which word did it, which you cannot do with a
classifier. `read()` is the seam if that trade ever stops being worth it.

HOW IT READS (round 2)

The first version matched keywords as bare substrings and let the first
family with a hit win. Both were wrong in ways a household hits daily:
"studied" contains "died", "whatever" contains "hate", "Delhi" and "nahi"
contain "hi", and "I'm really tired" was surprise because "really" sat in an
earlier family. So now:

  * the text is TOKENISED and keywords are matched on whole words (or on a
    word's START, for stems marked `*` and for Devanagari, whose endings
    inflect: खुश / खुशी, थक / थकलो);
  * every family is SCORED and the strongest wins, so "sorry to hear your
    father died" is grief, not an apology;
  * a negator just before a keyword flips or drops it ("not happy" is sad,
    "don't worry" is reassurance, "no emergency" is not dread);
  * held letters, missing apostrophes, a few common typos and emoji are
    normalised before any of that, because that is how people actually type.
"""

from __future__ import annotations

import re

from . import expressions
from . import fallback

# ---------------------------------------------------------------------------
# WHICH expression - topic words
#
# Order is now only the TIE-BREAK (narrow before broad, as before): the
# strongest total score wins. A keyword ending in `*` matches any word that
# starts with it ("annoy*" - annoyed, annoying). Devanagari keywords always
# match on the word start, because Hindi and Marathi inflect at the end.
# Multi-word phrases match whole token runs.
# ---------------------------------------------------------------------------

_FAMILIES: list[tuple[str, tuple[str, ...]]] = [
    ("apologetic", ("sorry", "sory", "apolog*", "my fault", "my bad", "forgive me",
                    "i messed up", "i was wrong", "didn't mean", "i broke", "oops",
                    "maaf", "maafi", "माफ", "क्षमा", "galti", "chuk", "चूक")),
    ("crying", ("crying", "cry", "cried", "cries", "in tears", "heartbroken",
                "devastated", "passed away", "died", "dies", "funeral", "grief",
                "rona", "ro raha", "ro rahi", "रो~v", "रडू", "रड~v", "radu")),
    ("love", ("i love you", "love you", "i miss you", "miss you", "adore",
              "my love", "sweetheart", "darling", "pyaar", "pyar", "प्यार",
              "प्रेम", "prem")),
    ("tender", ("thank you", "thanks", "thank u", "grateful", "appreciate*",
                "kind of you", "take care", "sleep well", "proud of you",
                "touched", "emotional", "dhanyavaad", "dhanyavad", "dhanyawad",
                "shukriya", "aabhar", "धन्यवाद", "शुक्रिया", "आभार")),
    ("delight", ("yay", "hooray", "amazing", "wonderful", "fantastic",
                 "brilliant", "excellent", "congrat*", "we did it", "perfect",
                 "awesome", "great news", "the best", "best ever", "best day", "excited", "so excited",
                 "new job", "got the job", "job offer", "promotion", "promoted",
                 "passed", "got selected", "we won", "won the", "first prize",
                 "joy", "tears of joy", "zabardast", "jabardast", "ज़बरदस्त", "जबरदस्त", "wah", "waah",
                 "वाह", "chhan", "छान", "kya baat hai", "क्या बात है",
                 "shabash", "शाबाश", "bhari")),
    ("happy", ("happy", "happi*", "glad", "pleased", "cheerful", "good mood",
               "feeling good", "nice one", "lovely", "that's good", "well done",
               "all good", "sounds good", "went well", "went really well", "good job", "good", "great", "nice",
               "not bad", "beautiful", "better", "cute", "sweet", "bye", "see you",
               "khush", "khushi", "खुश", "आनंद", "anand", "majja", "maja",
               "मज्जा", "mast", "मस्त", "acche ho", "achhe ho", "अच्छे हो",
               "gunacha", "गुणाचा")),
    ("content", ("calm", "peaceful", "relaxed", "relax", "cosy", "comfortable",
                 "at ease", "no rush", "take your time", "phew", "thank god",
                 "thankfully", "relieved", "relief", "it's fine", "all fine",
                 "everything is fine", "forgiven", "makes sense", "sab theek", "theek hai",
                 "सब ठीक", "ठीक है")),
    ("grin", ("haha*", "hehe*", "lol", "lmao", "funny", "hilarious", "joke",
              "laugh*", "cracking up", "rofl")),
    ("mischief", ("secret", "don't tell", "sneaky", "prank", "naughty",
                  "between us", "mischief")),
    ("wink", ("just kidding", "kidding", "jk", "wink")),
    ("angry", ("angry", "angery", "mad at", "mad", "furious", "annoy*", "irritat*",
               "fed up", "hate", "hated", "stupid", "ridiculous", "useless",
               "rubbish", "terrible", "worst", "shut up", "unfair", "livid",
               "why would you", "why did you", "how could you",
               "gussa", "गुस्सा", "राग आला", "raag aala", "bakwas", "बकवास", "chid", "चिड~v")),
    ("stern", ("stop it", "stop", "unacceptable", "no means no", "i told you",
               "last warning", "don't do", "enough is enough")),
    ("sad", ("sad", "sadly", "unhappy", "lonely", "depress*", "miserable", "hurt",
             "upset", "disappoint*", "displeased", "feel low", "down today",
             "bad", "failed", "ugly", "ignores me", "ignored", "left out",
             "moved away", "you forgot", "cancelled", "i miss", "miss him",
             "miss her", "miss them", "miss everyone", "miss those", "miss kar",
             "you're useless", "you are useless", "i hate you",
             "stupid robot", "useless robot",
             "dukh", "दुख", "दुःख", "dukhi", "udaas", "उदास", "एकटं", "akela",
             "अकेला", "bura lag", "bura laga", "बुरा")),
    ("fret", ("stressed", "stress", "tension", "pareshan", "परेशान", "uncomfortable",
              "not working", "stopped working", "broken", "accidentally",
              "by mistake", "deadline", "battery died", "phone died", "laptop died",
              "charger died", "car died", "bulb died", "light chali", "power cut")),
    ("worried", ("worried", "worry", "worr*", "anxious", "nervous", "scared",
                 "scary", "afraid", "concern*", "what if", "hope not", "oh no",
                 "sick", "hospital", "can't find", "can't be happening",
                 "getting late", "running late", "hurry", "shaking",
                 "chinta", "चिंता", "dar lag", "darr", "डर", "भीती", "bhiti",
                 "ghabra*", "घाबर")),
    ("dread", ("terrified", "terrifying", "panic", "emergency", "accident",
               "danger*", "urgent")),
    ("alarmed", ("fire", "smoke", "gas leak", "smell gas", "bleeding", "fell",
                 "fallen", "help!", "dog bit", "bitten")),
    ("startled", ("ahh", "aah", "boo", "made me jump", "so loud", "too loud",
                  "bang", "jumped")),
    ("surprised", ("no way", "what!", "whoa", "wow", "omg", "oh my god", "can't believe",
                   "unbelievable", "shocked", "sach mein")),
    ("oh", ("oh", "ohh", "i see", "ah i see", "oh i see")),
    ("confusion", ("confus*", "don't understand", "don't know", "makes no sense",
                   "what do you mean", "huh", "i'm lost", "unclear",
                   "samjha nahi", "samajla nahi", "समझ नहीं", "समजलं नाही",
                   "ऐकू आलं नाही")),
    ("suspicious", ("suspicious", "are you sure", "i doubt", "doubt it",
                    "really though", "prove it", "hmm", "sus", "don't trust",
                    "scam")),
    ("skeptical", ("maybe", "not sure", "i guess", "supposedly", "allegedly",
                   "if you say so", "yeah right")),
    ("thinking", ("think*", "rethink*", "worst-case", "worst case", "wondering", "consider", "figure out", "work out",
                  "how do i", "why does", "explain")),
    ("curious", ("what is", "what's", "who is", "where is", "when is",
                 "how is", "tell me about", "curious", "interesting")),
    ("searching", ("search", "find", "look up", "google", "where did i",
                   "locate", "check the")),
    ("listening", ("listen", "are you there", "hello", "hey", "hi", "namaste",
                   "good morning", "can you hear", "namaskar")),
    ("waking", ("i just woke up", "just woke up", "i woke up", "waking up")),
    ("squint", ("squint", "can't see", "can't read", "too bright", "small print")),
    ("peek", ("peekaboo", "peek-a-boo", "peek", "i see you", "guess who")),
    ("drowsy", ("tired", "sleepy", "exhausted", "worn out", "long day",
                "need a nap", "fell asleep", "lazy",
                "थक", "neend", "नींद", "zop", "झोप")),
    ("yawn", ("yawn", "yawns", "yawning")),
    ("asleep", ("good night", "going to bed", "sleep now", "shut down",
                "goodnight")),
    ("bored", ("bored", "boring", "nothing to do", "same old", "whatever",
               "meh", "ugh", "never mind", "are we there yet")),
    ("proud", ("proud", "proud of myself", "i did it", "i finished", "i won",
               "managed to", "nailed it", "look what i", "got a star")),
    ("shy", ("embarrass*", "shy", "blush*", "awkward", "don't look")),
    ("focused", ("focus", "concentrate", "careful", "precise", "exactly",
                 "step by step")),
]

# ---------------------------------------------------------------------------
# Round 3: broad feeling vocabulary. Whole FAMILIES of words - synonyms,
# inflections (via `*` stems, which now only accept real English endings),
# Hinglish spellings and Devanagari - rather than the single words a test
# happened to use. Devanagari single words take a suffix class: ~n (noun /
# adjective endings: खुशी, उदासी), ~v (verb endings: रोना, थकलो) or both
# (the default).
# ---------------------------------------------------------------------------
_MORE: dict[str, tuple[str, ...]] = {
    "delight": ("thrill*", "excite*", "excitement", "ecstatic", "overjoyed", "elated",
                "stoked", "pumped", "psyched", "delighted", "delightful", "delicious",
                "tasty", "yummy", "yum", "scrumptious", "mouthwatering", "superb",
                "incredible", "outstanding", "phenomenal", "spectacular", "marvellous",
                "marvelous", "terrific", "splendid", "magnificent", "fabulous", "woohoo",
                "yippee", "hurray", "hurrah", "jackpot", "good news", "best news",
                "got in", "got admission", "got engaged", "getting married", "epic",
                "mind blowing", "mindblowing", "so good", "too good", "love it", "loved it",
                "loving it", "love this", "loved this",
                "maza aa gaya", "maza aaya", "mazaa aaya", "maza", "mazaa", "majaa",
                "majja aali", "maja aali", "jhakaas", "jhakas", "zakaas", "zakas",
                "kamaal", "kamal hai", "badhiya", "badiya", "shandaar", "shaandaar",
                "dhamaal", "dhamal", "lai bhari", "ekdum bhari",
                "मजा", "मजा आया", "मजा आ गया", "कमाल", "बढिया", "शानदार", "धमाल",
                "झकास", "लय भारी", "स्वादिष्ट", "रोमांचक", "रोमांचित", "उत्साहित", "उत्सुक"),
    "happy": ("birthday", "party", "holiday", "vacation", "picnic", "festival",
              "diwali", "holi", "eid", "christmas", "celebrate*", "celebration",
              "pleasant", "pleasantly", "enjoy*", "fun", "had fun", "joyful", "smiling",
              "feel good", "feeling great", "feeling better", "good day", "lovely day",
              "sunny", "beautiful day", "lovely weather", "cheer*",
              "sundar", "sunder", "accha laga", "acha laga", "achha laga", "accha lag",
              "acha lag", "achha lag", "achha lagta", "accha lagta", "bara vatla",
              "bara vatle", "bara vatta", "chhan vatla", "chan vatla", "khushi hui",
              "aanand", "masta", "sukhi", "prasann",
              "सुंदर", "अच्छा लगा", "अच्छा लग", "अच्छा लगता", "अच्छा लग रहा",
              "बरं वाटलं", "बरं वाटलं", "छान वाटलं", "खुशी~n", "प्रसन्न", "सुखी", "आनंदी"),
    "content": ("relaxing", "chill", "chilled", "peace", "what a relief", "thank goodness",
                "not too bad", "not that bad", "not so bad", "not half bad",
                "could be worse", "fair enough", "no worries", "no problem",
                "piece of cake", "be fine", "be okay", "be ok", "be alright", "all set",
                "sukoon", "aaram", "shanti", "shaant", "bara jhala", "bara zala",
                "accha hua", "achha hua", "acha hua",
                "सुकून", "आराम", "शांति", "शांत", "बरं झालं", "अच्छा हुआ", "चैन"),
    "angry": ("frustrat*", "exasperat*", "aggravat*", "infuriat*", "enraged",
              "outraged", "pissed", "pissed off", "fuming", "seething", "sick of",
              "tired of", "had enough", "so done", "nonsense", "sick and tired",
              "last straw", "drives me crazy", "driving me crazy", "drives me nuts",
              "lost my temper", "bakwaas", "bekar", "bekaar", "faltu", "dimag kharab",
              "dimaag kharab", "tang aa gaya", "tang aa gayi", "vaitag", "dokyat jato",
              "gussa aa raha", "chidchid",
              "बेकार", "फालतू", "राग", "वैताग", "तंग आ गया", "तंग आ गई", "चिडचिड",
              "दिमाग खराब", "डोक्यात जातो"),
    "sad": ("is moving", "are moving", "moved to", "moving to", "moving away",
            "shifting to", "leaving us", "going away", "homesick", "lonesome", "all alone", "miss home", "gloomy", "glum",
            "sorrow*", "mourn*", "grieving", "hopeless", "helpless", "worthless",
            "disheartened", "dejected", "crushed", "heart broke", "broke my heart",
            "feel like crying", "feeling down", "feeling low", "let down", "let me down",
            "bad day", "rough day", "hard day", "tough day", "nobody remembered",
            "no one remembered", "forgot my birthday", "nobody cares", "no one cares",
            "kharab", "mood off", "mood kharab", "dil toot", "dil tut", "udas",
            "akeli", "dukhi", "vait", "vaait", "vait vatla", "vait vatle",
            "rona aa raha", "bura lagta",
            "खराब", "दिल टूट", "बुरा लगा", "बुरा लग", "बुरा लगता", "वाईट", "वाईट वाटलं",
            "दुखी", "दुःखी", "अकेली", "एकटा", "एकटी", "एकटं"),
    "worried": ("jitter*", "tense", "edgy", "uneasy", "restless", "on edge", "apprehensive",
                "unwell", "fever", "high fever", "throwing up", "vomit*", "headache",
                "stomach ache", "in pain", "not feeling well", "don't feel well",
                "not well", "feel sick", "feeling sick", "under the weather", "icu",
                "admitted", "surgery", "missing", "cold feet", "butterflies",
                "can't sleep", "losing sleep", "fikar", "fikr", "ghabrahat", "kalji",
                "dar lag raha", "dar lagta",
                "फिक्र", "घबराहट", "घबरा~v", "काळजी", "डर लग", "बीमार", "तबियत"),
    "fret": ("frazzled", "overwhelmed", "swamped", "hectic", "mad rush",
             "so much to do", "running out", "lost my", "lost the", "lost our",
             "missed the", "missed my", "stuck", "stuck in", "problem", "dikkat",
             "gadbad", "lafda",
             "दिक्कत", "गडबड", "समस्या", "टेंशन"),
    "dread": ("horrified", "horrifying", "petrified", "scared to death", "freaking out",
              "freaked out", "panick*", "ambulance", "heart attack", "can't breathe",
              "not breathing", "collapsed", "unconscious", "fainted"),
    "stern": ("disgust*", "gross", "yuck", "eww", "ew", "revolting", "nasty", "vile",
              "how dare", "that's enough", "don't you dare", "behave yourself"),
    "shy": ("so embarrassing", "sharam", "sharm", "laaj", "laj vatte", "शर्म", "लाज"),
    "apologetic": ("guilty", "guilt", "ashamed", "regret*", "remorse*", "my apologies",
                   "feel bad about", "chuk zali", "chuk jhali", "galti ho gayi",
                   "maaf karna", "kshama", "चूक झाली", "गलती"),
    "tender": ("thankful", "blessed", "means a lot", "so kind", "sweet of you", "aww",
               "aw", "touching", "heartwarming", "aabhari", "आभारी"),
    "surprised": ("astonish*", "stunned", "out of nowhere", "speechless"),
    "drowsy": ("dead tired", "knackered", "drained", "burnt out", "burned out",
               "wiped out", "groggy", "drowsy", "thak gaya", "thak gayi", "thak gaye",
               "thaka", "thaki", "thake", "thakaa", "thakla", "thakle", "thakli", "thaklo",
               "thakaan", "thakan", "thakawat", "thakavat", "thakke"),
    "bored": ("dull", "tedious", "monotonous", "bore ho", "bor ho", "kantala",
              "kantalo", "kantaala", "kantaalo", "kantalla", "कंटाळा", "कंटाळ", "बोर"),
    "grin": ("lmfao", "cracked me up", "in splits", "rolling on the floor",
             "can't stop laughing", "you're killing me", "died laughing", "dying laughing",
             "dying of laughter", "dead laughing"),
    "love": ("fell in love", "falling in love", "in love", "head over heels",
             "crush on", "अभिमान"),
    "proud": ("killing it", "smashed it", "aced it", "aced the", "crushed it",
              "topped the", "came first", "bang on", "abhimaan", "garv", "गर्व"),
    "suspicious": ("jealous*", "envious", "envy"),
}
_MORE["love"] = tuple(k for k in _MORE["love"] if k != "अभिमान")
_MORE["proud"] += ("अभिमान",)
_FAMILIES = [(fam, keys + _MORE.get(fam, ())) for fam, keys in _FAMILIES]

# Idioms carry no feeling, or a different one, from the keyword inside them.
# They are indexed first and matched as longer runs, so they always win
# against the single word they contain ("died laughing", "bus stop").
_IDIOMS: dict[str, tuple[str, ...]] = {
    "delight": ("to die for", "dying to", "can't wait", "cannot wait", "over the moon",
                "on cloud nine", "on top of the world", "on fire", "blown away",
                "made my day", "dream come true"),
}

# How much one hit is worth. Default 1.0. Weak words are hedges or very
# common ("good", "think", "hmm"): they should decide a line only when
# nothing stronger is there. Strong words are the ones a person would never
# say lightly, and they also lift the LEVEL (see _STRONG).
_WEIGHT: dict[str, float] = {
    "good": 0.6, "great": 0.8, "nice": 0.8, "better": 0.7, "bye": 0.7,
    "see you": 0.6, "mad": 0.9, "don't know": 0.8, "joy": 0.9, "think": 0.6, "hmm": 0.6, "maybe": 0.8, "bad": 0.6,
    "cancelled": 0.8, "stop": 0.8, "help!": 1.4, "fell": 1.2, "oh": 0.5, "battery died": 2.0,
    "phone died": 2.0, "laptop died": 2.0, "charger died": 2.0, "car died": 2.0,
    "bulb died": 2.0, "worst-case": 1.5, "worst case": 1.5,
    "sweet": 0.9, "cute": 0.9, "find": 0.9, "lazy": 0.8,
    "died": 1.6, "passed away": 1.6, "funeral": 1.5, "heartbroken": 1.6,
    "devastated": 1.6, "terrified": 1.5, "emergency": 1.5, "furious": 1.4,
    "fire": 1.4, "gas leak": 1.6, "smell gas": 1.6, "bleeding": 1.5,
    "i love you": 1.3, "oh no": 1.2, "can't find": 1.2, "not bad": 1.1,
    "you're useless": 3.0, "you are useless": 3.0, "i hate you": 3.0,
    "stupid robot": 3.0, "useless robot": 3.0, "why would you": 1.2,
    "why did you": 1.2, "how could you": 1.2, "thank god": 1.3,
    "fun": 0.8, "birthday": 0.5, "party": 0.5, "holiday": 0.5, "vacation": 0.5,
    "picnic": 0.5, "festival": 0.5, "diwali": 0.5, "holi": 0.5, "eid": 0.5,
    "christmas": 0.5, "celebrate*": 0.8, "celebration": 0.7, "is moving": 0.8,
    "are moving": 0.8, "moved to": 0.8, "moving to": 0.8, "shifting to": 0.8, "sunny": 0.7, "problem": 0.6, "missing": 1.1, "stuck": 0.8,
    "kharab": 0.9, "chill": 0.7, "peace": 0.7, "aw": 0.8, "tense": 0.8,
    "icu": 1.4, "ambulance": 1.5, "fever": 1.1, "maza": 1.0, "dull": 0.8,
    "admitted": 1.0, "be fine": 1.2, "be okay": 1.2, "be ok": 1.2, "be alright": 1.2,
    "nobody remembered": 1.4, "no one remembered": 1.4, "forgot my birthday": 1.4,
    "not too bad": 1.3, "not that bad": 1.3, "not so bad": 1.3, "not half bad": 1.3,
    "don't feel well": 1.4, "not feeling well": 1.4, "not well": 1.2,
}
for _fam in _IDIOMS.values():
    for _k in _fam:
        _WEIGHT.setdefault(_k, 1.5)
for _k in ("died laughing", "dying laughing", "dying of laughter", "dead laughing",
           "fell in love", "falling in love", "killing it", "smashed it", "crushed it",
           "aced it", "can't stop laughing", "sick and tired", "scared to death"):
    _WEIGHT.setdefault(_k, 1.8)

# Words a person never says lightly. They push the level up by one step.
_STRONG = {"furious", "livid", "terrified", "terrifying", "heartbroken",
           "devastated", "hate", "emergency", "ecstatic", "thrilled", "panic",
           "overjoyed", "thrill*", "elated", "horrified", "petrified", "enraged",
           "infuriat*", "fuming", "scared to death", "heart attack", "ambulance",
           "unbelievable", "hated", "fire", "bleeding", "gas leak", "smell gas"}

# What a negated keyword turns into. None means "drop it": "not surprised"
# is not a face, it is the absence of one.
_NEG_FLIP = {
    "happy": "sad", "delight": "sad", "love": "sad",
    "sad": "content", "crying": "content", "angry": "content",
    "worried": "content", "fret": "content", "dread": "content",
    "alarmed": "content", "content": "worried",
}
_NEGATORS = {"not", "no", "never", "don't", "didn't", "isn't", "wasn't",
             "aren't", "won't", "doesn't", "nobody", "nothing", "none",
             "nahi", "nahin", "naahi", "नहीं", "नाही", "nako", "नको",
             "mat", "मत", "wouldn't", "can't", "couldn't", "shouldn't", "haven't",
             "hasn't", "hadn't", "ain't", "weren't", "hardly", "barely", "neither",
             "nor", "without", "nhi", "nai", "नाहीं"}
# Verbs that carry a negation across to the clause they introduce:
# "I wouldn't SAY I'm happy", "I don't THINK she's angry".
_SCOPE_VERBS = {"say", "think", "feel", "believe", "call", "guess", "reckon",
                "mean", "expect", "sure", "suppose", "seem", "seems", "look", "looks"}
_HEDGE_VERBS = {"say", "call", "sure", "guess", "reckon", "suppose"}
_COMPARE = {"this", "so", "more", "as", "ever", "such", "that"}
# "irritate mat KAR" forbids the action; it does not deny the feeling.
_KAR = {"kar", "karo", "kariye", "kijiye", "karna", "कर", "करो", "करिए", "कीजिए", "करना"}
# Hindi and Marathi put the negator AFTER the word: "khush nahi", "tension
# mat lo". These are the ones that may look forward.
_POST_NEG = {"nahi", "nahin", "naahi", "नहीं", "नाही", "nako", "नको",
             "mat", "मत"}
_BREAK = {",", ".", ";", "!", "?", "but", "lekin", "पण", "लेकिन", "-"}
_OTHERS_FUTURE = {"she'll", "he'll", "they'll", "will", "would", "might"}
_CONTRAST = {"but", "lekin", "पण", "लेकिन", "though", "however"}

# Emoji are words in chat. They outrank adjacent words: "great 😡" is angry.
_EMOJI = {
    "😂": "grin", "🤣": "grin", "😆": "grin", "😹": "grin",
    "😭": "crying", "😢": "sad", "😞": "sad", "😔": "sad", "☹": "sad",
    "🙁": "sad", "💔": "sad",
    "❤": "love", "♥": "love", "💕": "love", "💖": "love", "😍": "love",
    "🥰": "love", "😘": "love",
    "😡": "angry", "🤬": "angry", "😠": "angry",
    "🙏": "tender", "🥹": "tender",
    "😊": "happy", "☺": "happy", "🙂": "happy", "😄": "happy", "😁": "happy",
    "😀": "happy", "😃": "happy",
    "🎉": "delight", "🥳": "delight", "🤩": "delight",
    "😱": "alarmed", "😨": "dread", "😰": "worried", "😟": "worried",
    "😮": "surprised", "😲": "surprised", "😯": "oh",
    "😴": "asleep", "🥱": "yawn", "😪": "drowsy",
    "🤔": "thinking", "😉": "wink", "😏": "mischief", "😳": "shy",
    "🙄": "skeptical", "😒": "bored", "👍": "content", "😌": "content",
    # round 3: the common rest of the keyboard, as families
    "😤": "angry", "👿": "angry", "😾": "angry", "🖕": "angry",
    "💀": "grin", "😹": "grin", "😝": "mischief", "😜": "mischief", "😛": "mischief",
    "🤪": "mischief", "🤫": "mischief", "😈": "mischief",
    "😬": "fret", "😩": "fret", "😫": "fret", "😖": "fret", "😣": "fret", "🤦": "fret",
    "😓": "worried", "😥": "sad", "😿": "sad", "🥀": "sad", "😕": "confusion",
    "🤷": "confusion", "❓": "confusion",
    "😋": "delight", "🤤": "delight", "🔥": "delight", "💯": "delight", "🙌": "delight",
    "🎊": "delight", "🎂": "delight", "🏆": "proud", "💪": "proud", "👏": "proud",
    "😎": "proud", "✨": "happy", "😇": "content", "👌": "content", "🌞": "happy",
    "😺": "happy", "😸": "happy", "😅": "shy", "🙈": "shy", "😶": "shy",
    "🥺": "tender", "🤗": "tender", "🥲": "tender", "💐": "tender", "💗": "love",
    "💓": "love", "💘": "love", "💞": "love", "😻": "love", "😚": "love", "😗": "love",
    "🤯": "surprised", "😧": "surprised", "😦": "surprised", "😵": "dizzy",
    "🤢": "stern", "🤮": "stern", "🤨": "suspicious", "🧐": "suspicious",
    "😐": "bored", "😑": "bored", "🥶": "worried", "🤒": "worried", "🤕": "worried",
    "😷": "worried", "🚨": "alarmed", "💤": "asleep", "😮‍💨": "content",
}
_EMOJI_RE = re.compile("|".join(map(re.escape, sorted(_EMOJI, key=len, reverse=True))))
_MILD_EMOJI = {"👍", "🙂", "👌", "✨"}
_POSITIVE = {"happy", "delight", "proud", "love", "tender", "grin", "content"}
_NEGATIVE = {"sad", "crying", "angry", "fret", "worried", "dread", "alarmed", "stern"}

# Spelling as people actually type it. Only unambiguous ones.
_TYPO = {
    "thnks": "thanks", "thnx": "thanks", "thx": "thanks", "tnx": "thanks",
    "ty": "thanks", "tq": "thanks", "thanku": "thanks", "thnk": "thanks",
    "dont": "don't", "didnt": "didn't", "doesnt": "doesn't", "isnt": "isn't",
    "wasnt": "wasn't", "cant": "can't", "cannot": "can't", "wont": "won't", "im": "i'm",
    "ive": "i've", "whats": "what's", "thats": "that's", "youre": "you're",
    "u": "you", "ur": "your", "realy": "really", "pls": "please",
    "plz": "please", "sry": "sorry", "srry": "sorry", "angery": "angry",
    "worryed": "worried", "hapy": "happy", "nahin": "nahi",
    "thankyou": "thanks", "tysm": "thanks", "thnku": "thanks", "thanq": "thanks",
    "couldnt": "couldn't", "wouldnt": "wouldn't", "shouldnt": "shouldn't",
    "havent": "haven't", "hasnt": "hasn't", "arent": "aren't", "werent": "weren't",
    "ain't": "ain't", "itll": "it'll", "shes": "she's", "hes": "he's",
}

# Insults and compliments AIMED AT homebot. The face is homebot's own, so a
# child saying "you're stupid" should see him hurt, not glaring back.
_TO_BOT_INSULT = re.compile(
    r"\b(you'?re|you are|u r|ur)\s+(so |such an? |very |really |the |a |an |too )*"
    r"(useless|stupid|dumb|an idiot|idiot|rubbish|bad|worst|annoying|hopeless|"
    r"pathetic|mean|boring)\b"
    r"|\b(stupid|useless|dumb) (robot|bot|homebot)\b|\bi hate you\b"
    r"|\bshut up,? (homebot|robot|bot)\b|\b(homebot|robot|bot),? shut up\b"
    r"|\byou (never|don't|dont|do not|didn't|never ever) (listen|understand|care|help)"
    r"|\byou always (ignore|forget|mess)")
_TO_BOT_PRAISE = re.compile(
    r"\b(you'?re|you are|u r)\s+(so |such an? |very |really |the |a |an |too )*"
    r"(cute|sweet|smart|best|amazing|awesome|thoughtful|kind|lifesaver|"
    r"good|great|funny|lovely)\b"
    r"|\bi (really )?(like|love|enjoy) (talking|chatting|speaking) (to|with) you\b"
    r"|\bi (really )?like you\b|\byou'?re my (favourite|favorite|best)"
    r"|\b(good|clever|smart) (bot|robot|boy|homebot)\b")
# "oh great, another bill". Cheap and narrow on purpose: a praise word AND a
# repeat word AND a household-annoyance noun. Anything looser misfires on
# genuine joy, which is worse than missing the joke.
_SARC_PRAISE = {"great", "wonderful", "perfect", "lovely", "fantastic",
                "brilliant", "awesome", "best", "nice"}
_SARC_AGAIN = re.compile(r"\b(again|another|phir se|fir se|parat)\b")
# A praise word next to an event nobody enjoys is irony even without
# "again": "fantastic, a parking ticket", "great, the train is late".
_SARC_EVENT = re.compile(r"\b(ticket|fine|challan|late|power cut|load ?shedding|"
                         r"traffic|delay\w*|queue|jam|puncture\w*|flat tyre|"
                         r"breakdown|broke down|stuck|cancell?ed|overtime|"
                         r"leak\w*|no water|no electricity|no power)\b")
_SARC_NOUN = re.compile(r"\b(bill|rain\w*|traffic|down|broken|late|power cut|"
                        r"queue|jam|leak\w*|light|wifi|internet)\b")
# Sarcasm set phrases: praise words used to mean the opposite.
_SARC_SET = re.compile(
    r"\b(wow|oh),? (so|very|really|super) (helpful|useful|smart|clever)\b"
    r"|\bkya baat hai\b.*\b(phir|fir) se\b"
    r"|\bjust (great|perfect|wonderful|brilliant|fantastic|lovely|what i needed)\b"
    r"|\bthanks? (a lot |so much )?for nothing\b|\blove that for me\b"
    r"|\bbecause that (always|ever) works\b|\bcause that always works\b"
    r"|\boh (joy|goody|great|wonderful|perfect|brilliant)\b.*\b(again|another|more|now)\b"
    r"|\bwhat a (surprise|shock)\b(?!!)|\byeah,? (sure|right)\b|\bas if\b"
    r"|\bcouldn'?t be (better|happier)\b.*\b(not|traffic|again|late|broken)\b"
    r"|\b(great|perfect|wonderful|fantastic|brilliant|nice),? (just )?(great|perfect|wonderful)\b")
_LAUGH = re.compile(r"\b(ha(ha)+h?|he(he)+|lol|lmao|rofl)\b")

# A question with no other signal is curiosity, not a statement.
_QUESTION = "curious"
_DEFAULT = "attentive"
_NEUTRAL = {"attentive", "listening", "rest", "answering"}

_TOKEN = re.compile(r"[a-z0-9'ऀ-ॣ०-ॿ‌‍]+|[!?.,;\-]")
_NUKTA = "\u093c"
_HELD_OH = re.compile(r"o+h{3,}|o{3,}h+")
_RUN3 = re.compile(r"([a-z])\1{2,}")
_DEVA = re.compile(r"[ऀ-ॿ]")


# Phrases that CONTAIN a keyword but carry no feeling. Matching them first
# consumes the words, so "update the emergency contact" is a chore, not dread.
_NO_FEELING = ("emergency contact", "emergency number", "take out the rubbish",
               "rubbish bin", "take care of the", "take care of it",
               "explain later", "i'll explain", "fire extinguisher",
               "fire brigade number", "best before", "do not disturb",
               # round 3: places, chores and set phrases that contain a feeling word
               "bus stop", "full stop", "pit stop", "next stop", "last stop", "stop by",
               "non stop", "nonstop", "stop at", "fire up", "light the fire", "low fire",
               "medium fire", "high fire", "slow fire", "far cry", "killing time",
               "kill time", "dead end", "fire alarm test", "sick leave",
               "crying shame", "break a leg", "mad about", "scared straight",
               "give up smoking", "worst comes to worst")
# Suffixes a `*` stem may take. A stem is a word's root, not any prefix:
# "think*" is thinks / thinking, never "thinkpad".
_EN_SUFFIX = {"", "s", "es", "ed", "d", "ing", "er", "ers", "est", "ly", "y", "ies",
              "ied", "ying", "yingly", "ily", "iness", "ness", "ment", "ments", "ful",
              "ation", "ations", "ion", "ions", "ive", "ingly", "edly", "able", "ance",
              "ous", "ously", "e", "ise", "ize", "ised", "ized", "ising", "izing",
              "ulation", "ulations", "ulate", "ulated", "ter", "isome", "etic",
              "etically", "edness", "ia", "ingness", "ish", "ishly", "ity"}
_FREE_STEMS = {"haha", "hehe"}       # laughter repeats; any tail is fine
_DEVA_N = {"", "ी", "ा", "े", "ें", "ों", "ो", "ीं", "ियां", "ियों", "पन", "पणा", "ीचा",
           "ीची", "ीचे", "ाचा", "ाची", "ाचे", "ात", "ीत", "ाने", "ीने", "ाला", "ीला",
           "ित", "ता", "ाई", "ान", "ावट", "ं"}
_DEVA_V = {"", "ना", "ने", "नी", "ता", "ती", "ते", "तो", "त", "तात", "तोय", "तेय",
           "ला", "ले", "ली", "लो", "लं", "लीस", "लात", "णे", "णार", "णं", "ून", "ायला",
           "ायचं", "ायचे", "ू", "ूं", "ेगा", "ेगी", "ेंगे", "ोगे", "ई", "ए", "या",
           "ये", "यी", "कर", "के", "ाया", "वला", "वले", "ते हैं", "तोय", "लेला", "लेली",
           "चिड", "ायी", "ाये"}
_DEVA_NV = _DEVA_N | _DEVA_V
# People - for words whose sense depends on WHO: "I fell" vs "prices fell",
# "she's sick" vs "the movie was sick".
_PERSON = {"i", "i'm", "i've", "i'd", "me", "we", "we're", "he", "she", "they", "he's",
           "she's", "they're", "mom", "mum", "mummy", "mother", "dad", "papa", "father",
           "aai", "baba", "ajoba", "aaji", "ajji", "aji", "grandpa", "grandma", "granny",
           "nani", "nana", "dadi", "dada", "baby", "son", "daughter", "kid", "kids",
           "child", "wife", "husband", "brother", "sister", "friend", "uncle", "aunty",
           "aunt", "someone", "somebody", "everyone", "kaka", "kaku", "mama", "mami",
           "bhai", "didi", "tai", "dog", "cat", "puppy", "he'd", "she'd", "you", "you're",
           "him", "her", "my"}
_DEVICE = {"battery", "phone", "laptop", "charger", "car", "bulb", "inverter", "ups",
           "scooter", "bike", "mobile", "tv", "fridge", "remote", "torch", "router",
           "wifi", "engine", "geyser", "fan", "ac", "mixer", "printer", "tablet",
           "ipad", "computer", "pc", "watch", "earphones", "headphones", "speaker",
           "it", "signal", "connection", "server", "app"}
_EXAM = {"exam", "exams", "test", "tests", "interview", "driving", "course", "board",
         "boards", "paper", "papers", "class", "grade", "level", "round", "semester",
         "audition", "assessment", "certification", "neet", "jee", "upsc", "cet",
         "ssc", "hsc", "viva", "practical", "practicals", "quiz", "entrance", "with",
         "everything", "all", "both", "it", "first", "second", "final", "finals"}
_COPULA = {"was", "is", "so", "that's", "it's", "looks", "sounds", "pretty", "totally",
           "super", "really", "absolutely", "be", "are", "were"}
_STOP_OK = {"please", "pls", "just", "now", "you", "will", "ok", "okay", "homebot",
            "bas", "said", "to", "must", "should", "gotta", "can", "could", "!", ",",
            "and", "oh", "hey", "seriously", "never", "ever", "won't", "don't", "do",
            "stop", "i", "kindly"}
_MARATHI = {"aahe", "ahe", "ekdum", "lai", "khup", "zala", "jhala", "hota", "hoti",
            "re", "ch", "kay", "kiti", "ahes", "aahes", "vatla", "vatle", "आहे", "एकदम",
            "लय", "लई", "खूप", "झाला", "होता", "होती", "रे", "काय", "किती", "भाऊ", "bhau",
            "mast", "मस्त", "chhan", "छान", "zhala", "zali", "jhali"}
_ANAND_CTX = {"hua", "huaa", "aala", "ala", "aya", "aaya", "mila", "zala", "jhala",
              "vatla", "vatle", "aa", "hai", "aahe", "ahe", "आला", "हुआ", "झाला", "मिला",
              "वाटला", "वाटले", "आया", "है", "आहे", "आ", "मिळाला", "milala"}


def _build_index():
    exact: dict[tuple[str, ...], tuple[str, str, float]] = {}
    stems: dict[str, tuple[str, str, float]] = {}
    deva: dict[str, tuple[tuple[str, str, float], frozenset]] = {}
    longest = 1
    for fam, keys in list(_IDIOMS.items()) + _FAMILIES:
        for k in keys:
            k = k.replace(_NUKTA, "")
            cls = None
            if "~" in k:
                k, cls = k.split("~")
            w = _WEIGHT.get(k, _WEIGHT.get(k.rstrip("*"), 1.0))
            if k.endswith("*"):
                stems.setdefault(k[:-1], (fam, k, w))
                continue
            toks = tuple(_TOKEN.findall(k))
            if len(toks) == 1 and _DEVA.search(k):
                # Devanagari inflects at the end - but only with real endings,
                # so रो is रोना / रोया and never रोटी or रोज़.
                sufs = {"n": _DEVA_N, "v": _DEVA_V}.get(cls, _DEVA_NV)
                if k.endswith("ा"):      # गुस्सा -> गुस्से, बुरा -> बुरी
                    deva.setdefault(k[:-1], ((fam, k, w), frozenset({"ा", "े", "ी", "ों", "ें"})))
                deva.setdefault(k, ((fam, k, w), frozenset(sufs)))
            exact.setdefault(toks, (fam, k, w))
            longest = max(longest, len(toks))
    for k in _NO_FEELING:
        toks = tuple(_TOKEN.findall(k))
        exact[toks] = (None, k, 0.0)
        longest = max(longest, len(toks))
    stem_lens = sorted({len(s) for s in stems}, reverse=True)
    deva_lens = sorted({len(s) for s in deva}, reverse=True)
    return exact, stems, stem_lens, longest, deva, deva_lens


_EXACT, _STEMS, _STEM_LENS, _LONGEST, _DEVA_STEMS, _DEVA_LENS = _build_index()

# Inflection and typo fallback for single English feeling words. Families
# whose words are ordinary verbs/nouns (fire, stop, find) are left out.
_NO_INFLECT_FAM = {"alarmed", "startled", "stern", "searching", "listening", "curious",
                   "focused", "oh", "waking", "squint", "peek", "asleep", "thinking"}
_NO_INFLECT = {"good", "great", "nice", "sweet", "cute", "find", "stop", "fell", "fire",
               "mad", "bad", "mast", "maja", "prem", "anand", "lazy", "bye", "dull",
               "fun", "chill", "peace", "sunny", "stuck", "tense", "missing", "aw",
               "joy", "yum", "epic", "gross", "nasty", "envy", "guilt", "vait",
               "passed", "promotion", "boo", "bang", "wow", "meh", "ugh", "sus", "hurt",
               "cry", "upset", "funny", "joke"}
_SINGLE = {k[0]: v for k, v in _EXACT.items()
           if len(k) == 1 and v[0] and v[0] not in _NO_INFLECT_FAM and k[0].isascii()
           and k[0].isalpha() and len(k[0]) >= 4 and k[0] not in _NO_INFLECT}
_TYPO_BLOCK = {"please", "sacred", "united", "casual", "causal", "heated", "though",
               "through", "thought", "scarce", "lovers", "wonder", "trying", "hoping",
               "loving", "living", "angles", "shopping", "dying", "hating", "pleasure",
               "unite", "carried", "married", "worried"}
_DELETES: dict[str, str] = {}
for _w in _SINGLE:
    if len(_w) >= 6:
        for _i in range(len(_w)):
            _DELETES.setdefault(_w[:_i] + _w[_i + 1:], _w)


def _inflected(w: str):
    """'happier' -> happy, 'frustratingly' etc. come from stems; this covers
    plain words: worries, hated, angrier, saddest, lonelier."""
    cands = []
    if w.endswith("ies"):
        cands.append(w[:-3] + "y")
    if w.endswith("ier") or w.endswith("ied"):
        cands.append(w[:-3] + "y")
    if w.endswith("iest"):
        cands.append(w[:-4] + "y")
    for suf in ("s", "es", "ed", "d", "er", "est", "ing"):
        if w.endswith(suf) and len(w) - len(suf) >= 3:
            b = w[:-len(suf)]
            cands.append(b)
            if len(b) >= 2 and b[-1] == b[-2]:
                cands.append(b[:-1])          # sadder -> sad
            cands.append(b + "e")             # loving -> love
    for c in cands:
        if c in _SINGLE:
            return _SINGLE[c]
    return None


def _typo(w: str):
    """One slip of the finger on a long feeling word: a missing letter
    (amazng), an extra one (scarred), or two swapped (exhuasted)."""
    if len(w) < 6 or w in _TYPO_BLOCK or not w.isalpha() or not w.isascii():
        return None
    if w in _DELETES:                     # missing letter
        return _SINGLE[_DELETES[w]]
    for i in range(len(w)):               # extra letter
        d = w[:i] + w[i + 1:]
        if d in _SINGLE and len(d) >= 6:
            return _SINGLE[d]
    for i in range(len(w) - 1):           # swapped pair
        t = w[:i] + w[i + 1] + w[i] + w[i + 2:]
        if t in _SINGLE:
            return _SINGLE[t]
    return None
_FAM_ORDER = {fam: i for i, (fam, _) in enumerate(_FAMILIES)}


def _clean(text: str) -> tuple[str, list[str]]:
    """Lowercase, straighten apostrophes, lift emoji out. Returns the text and
    the emoji families found, in order."""
    t = text.replace("’", "'").replace("‘", "'").replace("️", "").replace(_NUKTA, "")
    emo = [(_EMOJI[m], m) for m in _EMOJI_RE.findall(t)] if not t.isascii() else []
    return t.lower(), emo


def _tokens(low: str) -> list[list[str]]:
    """Token lists to try. Held letters are ambiguous - "yaaaay" wants one
    'a' and "sorrry" wants two 'r's - so when there are any, both
    collapsings are read and the better one is kept."""
    raw = _TOKEN.findall(low)
    if not _RUN3.search(low):
        return [[_TYPO.get(w, w) for w in raw]]
    one = [_TYPO.get(x, x) for x in (_RUN3.sub(r"\1", w) for w in raw)]
    two = [_TYPO.get(x, x) for x in (_RUN3.sub(r"\1\1", w) for w in raw)]
    return [one, two]


def _hits(toks: list[str]):
    """Every keyword hit: (family, keyword, weight, start index, length)."""
    out = []
    i, n = 0, len(toks)
    while i < n:
        found = None
        for L in range(min(_LONGEST, n - i), 0, -1):
            e = _EXACT.get(tuple(toks[i:i + L]))
            if e:
                found = (e, L)
                break
        if found is None:
            w = toks[i]
            if w.isascii():
                for sl in _STEM_LENS:
                    if sl <= len(w) and w[:sl] in _STEMS and (
                            w[sl:] in _EN_SUFFIX or w[:sl] in _FREE_STEMS):
                        found = (_STEMS[w[:sl]], 1)
                        break
                if found is None and len(w) >= 4 and w.isalpha():
                    e = _inflected(w) or _typo(w)
                    if e:
                        found = (e, 1)
            elif _DEVA.search(w):
                for sl in _DEVA_LENS:
                    if sl < len(w) and w[:sl] in _DEVA_STEMS:
                        e, sufs = _DEVA_STEMS[w[:sl]]
                        rest = w[sl:]
                        if rest in sufs:
                            found = (e, 1)
                            break
        if found:
            (fam, k, wt), L = found
            if fam is not None:
                out.append((fam, k, wt, i, L))
            i += L
        else:
            i += 1
    return out


def _negated(toks: list[str], i: int, L: int) -> int:
    """0 = not negated, 1 = negated, 2 = hedged ("I wouldn't SAY I'm happy")."""
    reach, scope = 3, False
    j = i - 1
    while j >= 0 and j >= i - reach:
        t = toks[j]
        if t in _BREAK:
            break
        if t in _SCOPE_VERBS and not scope:
            scope = t
            reach += 3            # the negation reaches across the verb
        if t in _NEGATORS:
            between = toks[j + 1:i]
            kw = toks[i]
            # "never been THIS happy", "never felt better": a superlative,
            # not a denial.
            if t in ("never", "not") and (any(b in _COMPARE for b in between)
                                          or kw.endswith("er") or kw.endswith("est")
                                          or kw in ("better", "best")):
                if t == "never":
                    return 0
            if scope in _HEDGE_VERBS:
                return 2
            return 1
        j -= 1
    for j in range(i + L, min(len(toks), i + L + 2)):
        t = toks[j]
        if t in _BREAK:
            break
        if t in _POST_NEG:
            if t in ("mat", "मत", "nako", "नको") and j + 1 < len(toks) and toks[j + 1] in _KAR:
                return 0
            return 1
    return 0


# Keys whose own negator is the meaning - nothing before them flips them.
_NEG_PHRASE = {"don't feel well", "don't understand", "don't know", "no worries",
               "no problem", "no rush", "no way", "no means no", "nothing to do",
               "no one remembered", "nobody remembered", "nobody cares", "no one cares"}


def _context(fam, k, toks, i, L):
    """Words whose feeling depends on the words around them. Returns the
    family to count (possibly a different one), or None to ignore the hit."""
    prev = toks[i - 1] if i else ""
    nxt = toks[i + L] if i + L < len(toks) else ""
    before = toks[max(0, i - 4):i]
    after = toks[i + L:i + L + 4]
    if k in ("died", "dies", "dying", "died."):
        if any(t in _DEVICE for t in before):
            return "fret"                         # the battery died
    elif k == "passed":
        if nxt and nxt not in _BREAK and not (set(after) & _EXAM):
            return None                           # passed the salt
    elif k == "stop":
        if i and prev not in _STOP_OK and prev not in _BREAK:
            return None                           # the bus stop, a stop sign
    elif k == "fire":
        if nxt in ("up", "extinguisher", "brigade", "place", "wood", "pit", "drill"):
            return None
        if prev in ("on", "the", "low", "medium", "high", "slow", "camp", "open") and not \
                any(t in ("house", "kitchen", "building", "smoke", "help") for t in toks):
            return None
    elif k == "fell":
        if not any(t in _PERSON for t in before) and nxt not in ("down", "off", "over", "from"):
            return None                           # prices fell, Diwali fell on
    elif k == "sick":
        if any(t in _PERSON for t in before) or prev in ("feel", "feeling", "felt", "got", "getting"):
            return "worried"
        if prev in _COPULA or prev in ("so", "that's"):
            return "delight"                       # the movie was sick
    elif k == "on fire":
        who = {"i'm", "you're", "he's", "she's", "we're", "they're", "you", "i", "he",
               "she", "team", "they", "we", "you", "are", "were"}
        return "delight" if any(t in who for t in before) else "alarmed"
    elif k in ("bang",):
        if nxt == "on":
            return "proud"
    elif k in ("anand", "आनंद"):
        if not (nxt in _ANAND_CTX or prev in _UP or prev in ("bada", "बड़ा", "बडा", "khup", "खूप")):
            return None                           # Anand, the name
    elif k in ("bhari", "भारी"):
        if not any(t in _MARATHI for t in toks):
            return None                           # Hindi "heavy"
    elif k == "maza" or k == "मजा":
        if prev in ("ka", "ki", "को", "का"):
            return fam
    return fam


def _score(toks: list[str], low: str, emo: list[str], names=frozenset()):
    scores: dict[str, float] = {}
    why: dict[str, tuple[float, str]] = {}

    def add(fam, amount, k):
        scores[fam] = scores.get(fam, 0.0) + amount
        if amount > why.get(fam, (0.0, ""))[0]:
            why[fam] = (amount, k)

    contrast_at = max((i for i, t in enumerate(toks) if t in _CONTRAST), default=-1)
    hits = _hits(toks)
    praise_words = []
    for fam, k, wt, i, L in hits:
        if i in names:
            continue            # "is Joy coming", "call Sukhi aunty"
        fam = _context(fam, k, toks, i, L)
        if fam is None:
            continue
        if i > contrast_at >= 0:
            wt *= 1.25          # "...but I'm scared" - the turn is the point
        if i >= 2 and toks[i - 1] == "be" and toks[i - 2] in _OTHERS_FUTURE:
            wt *= 0.6           # "she'll be angry" is her feeling, and not yet
        neg = 0 if (k.startswith(("not ", "can't ", "cannot ")) or k in _NEG_PHRASE) \
            else _negated(toks, i, L)
        if neg == 2:
            # A hedge denies the strength, not the topic: "I wouldn't say I'm
            # happy" is unconvinced, not miserable.
            add("skeptical" if fam in _POSITIVE else "content" if fam in _NEGATIVE
                else fam, wt * 0.7, "hedged " + k)
            continue
        if neg and fam in ("angry", "stern", "sad", "crying") and i >= 2 \
                and toks[i - 1] == "be" and "please" in toks[max(0, i - 5):i]:
            add("worried", wt * 0.9, "please don't be " + k)   # a plea
            continue
        if neg:
            flip = _NEG_FLIP.get(fam)
            if flip:
                add(flip, wt * 0.7, "not " + k)
            continue
        add(fam, wt, k)
        if k in _SARC_PRAISE or k == "oh great":
            praise_words.append(k)
    # Emoji are a strong signal on their own, a supporting one next to clear
    # words: "terrible news 🙂" is still terrible news.
    worded = bool(scores)
    for e_fam, ch in emo:
        if e_fam == "crying" and (set(scores) & (_POSITIVE - {"content"})):
            add("delight", 1.6, "emoji (happy tears)")    # "I got the job 😭😭"
            continue
        w = 2.0 if not worded else 1.0
        if ch in _MILD_EMOJI:
            w *= 0.5
        add(e_fam, w, "emoji")

    if _TO_BOT_INSULT.search(low):
        add("sad", 3.0, "said to me")
    elif _TO_BOT_PRAISE.search(low):
        add("happy", 2.5, "said to me")
    if "?!" in low or "!?" in low:
        add("angry", 1.2, "?!")

    # Crying from laughing, or from joy, is not grief.
    if "crying" in scores and why["crying"][1] in ("crying", "cry", "cried", "in tears"):
        if _LAUGH.search(low) or "laugh" in low:
            add("grin", scores.pop("crying") + 0.5, why.pop("crying")[1] + " (laughing)")
        elif "happy" in scores or "delight" in scores:
            add("delight", scores.pop("crying"), why.pop("crying")[1] + " (happy tears)")

    # Sarcasm: praise + "again"/"another" + a thing nobody is pleased about,
    # or one of the set sarcastic phrases.
    if _SARC_SET.search(low) or (praise_words and _SARC_AGAIN.search(low)
                                 and _SARC_NOUN.search(low)) or (
            praise_words and _SARC_EVENT.search(low)
            and not set(scores) - {"delight", "happy", "content", "skeptical"}):
        for f in ("delight", "happy"):
            scores.pop(f, None); why.pop(f, None)
        for f in ("tender", "love"):
            scores.pop(f, None); why.pop(f, None)
        add("skeptical", 2.5, (praise_words[0] if praise_words else "set phrase") + " (sarcastic)")
    return scores, why


def _shout_words(text: str) -> list[str]:
    return re.findall(r"\b[A-Z]{2,}\b", text)


# Short capitals that are SPELT that way in this house: loan EMIs, OTPs,
# Ajoba's BP, UPI, FDs. None of them is shouting.
_ACRONYMS = {"I", "OK", "TV", "AM", "PM", "EMI", "OTP", "BP", "UPI", "FD",
             "ID", "PIN", "ATM", "GST", "PAN", "KYC", "SMS", "PDF", "USB",
             "WIFI", "CSMT", "AC", "GPS", "DND", "RD", "PF", "IT", "HR", "UK",
             "US", "USA", "ICU", "OPD", "MRI", "ECG", "CT", "LPG", "CNG", "IPL",
             "SBI", "HDFC", "ICICI", "NEFT", "IMPS", "IFSC", "QR", "OS", "PC"}


def _caps_lock(text: str) -> bool:
    """A whole sentence in capitals, several words long: caps lock or a
    habit, not a raised voice - unless what it says is itself emotional."""
    letters = [c for c in text if c.isalpha() and c.isascii()]
    return (len(letters) >= 6 and all(c.isupper() for c in letters)
            and len(text.split()) >= 3)


def _shouting(text: str) -> bool:
    """A capitalised WORD, not a capitalised acronym."""
    return any(w not in _ACRONYMS for w in _shout_words(text))


_UP = {"very", "really", "extremely", "incredibly", "absolutely", "totally",
       "completely", "utterly", "super", "insanely", "deeply", "massively",
       "terribly", "awfully", "ever", "seriously", "bahut", "bohot", "bahot",
       "khup", "खूप", "बहुत", "ekdum", "एकदम", "itna", "itni", "kitna"}
_UP2 = {("such", "a"), ("so", "much")}
_SO_STOP = {"that", "i", "we", "you", "he", "she", "they", "it", "the", "a",
            "an", "now", "far", "what", "then", "there", "this", "if", "is",
            "today", "yes", "no", "on", "ok", "okay", "maybe", "let's", "do",
            "are", "was", "will", "can", "my", "your", "his", "her", "our"}
_DOWN2 = {("a", "bit"): 2, ("a", "little"): 2, ("kind", "of"): 2,
          ("sort", "of"): 2, ("a", "touch"): 2, ("mostly", "ok"): 2,
          ("not", "really"): 1, ("no", "big"): 2}
_DOWN1 = {"slightly": 2, "kinda": 2, "somewhat": 2, "mildly": 2, "fairly": 1,
          "thoda": 2, "thodi": 2, "थोड़ा": 2, "थोडा": 2, "jara": 1, "थोडं": 2}
_FLAT_EXEMPT_START = {"i'm", "i", "you're", "you", "yes", "ur", "im"}


def _elongated_words(raw_tokens: list[str]) -> int:
    """soooo / yaaay / nooo - a held letter is a held feeling. Counted per
    word, so "sooooo happyyy" holds twice. hmmm and www are spelt, not held."""
    n = 0
    for w in raw_tokens:
        if _RUN3.search(w) and not re.fullmatch(r"h?m+|w+|z+|ha(ha)*h?|\.+", w):
            n += 1
    return n


def _level_score(text: str, low: str, toks: list[str], emo: list[str],
                 matched: str | None, why: str | None) -> int:
    score = 0
    bangs = low.count("!")
    if bangs >= 2:
        score += 2
    elif bangs == 1:
        score += 1
    if low.count("?") >= 2:
        score += 1

    emotional = matched is not None and matched not in _NEUTRAL \
        and matched not in (_QUESTION, "searching", "thinking")
    if _caps_lock(text):
        if emotional:
            score += 2
    elif _shouting(text):
        score += 2

    raw = _TOKEN.findall(low)
    score += min(2, _elongated_words(raw))
    up = 0
    for i, t in enumerate(toks):
        nxt = toks[i + 1] if i + 1 < len(toks) else None
        if t in _UP:
            up = 1
        elif t == "so" and nxt and nxt not in _SO_STOP and nxt not in _BREAK:
            up = 1
        elif nxt and (t, nxt) in _UP2:
            up = 1
    score += up
    down = 0
    for i, t in enumerate(toks):
        nxt = toks[i + 1] if i + 1 < len(toks) else None
        if nxt and (t, nxt) in _DOWN2 and not (i and toks[i - 1] == "in"):
            down = max(down, _DOWN2[(t, nxt)])
        elif t in _DOWN1:
            down = max(down, _DOWN1[t])
    score -= down
    if why and (why in _STRONG or why.split(" (")[0] in _STRONG):
        score += 1
    elif why and why.startswith("not ") and why[4:] in _STRONG:
        score -= 1      # "I don't hate it" is an understatement, not a feeling
    if len(emo) >= 2:
        score += 1
    for i, t in enumerate(toks):
        if emotional and why != "!" and t == "never" and any(
                x in ("this", "so", "such", "more", "happier", "better", "best")
                or (x.endswith(("ier", "est")) and len(x) > 5) for x in toks[i + 1:i + 4]):
            score += 1          # "never been this happy" is the strongest form
            break

    # A very short, flat, unpunctuated line is an understatement by default -
    # "sorry" and "thanks" really are quieter than "I am so sorry!!!". But
    # not a question ("total?"), not a laugh ("hahaha"), not an emoji, and not
    # a statement about someone ("i'm annoyed", "you're cute") - those are
    # short because they are plain, not because they are quiet.
    words = low.split()
    if (score == 0 and len(words) <= 2 and not bangs and "?" not in low
            and not _LAUGH.search(low) and not (emo and not set(_EMOJI_RE.findall(
                text.replace("️", ""))) <= _MILD_EMOJI)
            and not (words and words[0] in _FLAT_EXEMPT_START and len(words) == 2)):
        score -= 1
    return score


def level_of(text: str) -> str:
    """One of expressions.LOW / MID / INTENSE."""
    return _read(text)[1]


# ---------------------------------------------------------------------------

_ORIG_TOKEN = re.compile(r"[A-Za-z0-9'ऀ-ॣ०-ॿ‌‍]+|[!?.,;\-]")
_TITLES = {"mr", "mrs", "ms", "miss", "dr", "shri", "smt", "sri", "named",
           "called", "meet", "aunty", "uncle", "ji"}
# Kinship words that follow a name: "Prem bhaiya", "Sukhi aunty".
_KIN = {"bhaiya", "bhaia", "bhai", "didi", "di", "aunty", "auntie", "uncle", "ji",
        "kaka", "kaki", "mama", "mami", "mausi", "masi", "tai", "dada", "dadi",
        "nana", "nani", "chacha", "chachi", "sir", "madam", "maam", "ajoba", "aaji",
        "bua", "bhabhi", "jiju", "anna", "akka", "didi's", "aunty's", "uncle's"}
# A capitalised word after these is still the feeling: "Happy Diwali".
_OCCASION = {"diwali", "birthday", "holi", "eid", "christmas", "new", "anniversary",
             "dussehra", "navratri", "pongal", "onam", "easter", "independence",
             "teachers", "mothers", "fathers", "friendship", "journey", "landing",
             "married", "returns", "weekend", "sunday", "monday", "friday", "ganesh",
             "thanksgiving", "halloween", "valentine's", "valentines", "lohri", "ugadi",
             "gudi", "baisakhi", "rakhi", "raksha", "janmashtami", "durga", "wedding",
             "retirement", "holidays", "holiday", "hanukkah", "makar", "sankranti"}


def _name_positions(text: str, n: int) -> frozenset:
    """Token positions that are people or places, not feelings: a capitalised
    word mid-sentence, after a title, or followed by another capitalised word
    ("Happy Valley", "Prem bhaiya", "is Joy coming")."""
    if text.isupper() or not any(c.isupper() for c in text):
        return frozenset()
    t = text.replace("’", "'").replace("‘", "'").replace("️", "").replace(_NUKTA, "")
    raw = _ORIG_TOKEN.findall(t)
    if len(raw) != n:
        return frozenset()
    words = [w for w in raw if w[0].isalpha()]
    if len(words) > 2 and sum(w[0].isupper() for w in words) > 0.6 * len(words):
        return frozenset()       # Title Case Everything: no signal
    out = set()
    for i, w in enumerate(raw):
        if not (w[0].isupper() and w[0].isascii()) or w.isupper():
            continue
        prev = raw[i - 1] if i else "."
        nxt = raw[i + 1] if i + 1 < n else ""
        start = prev in (".", "!", "?") or (prev == "," and i == 1) \
            or (i >= 2 and raw[i - 2] in (".", "!", "?") and prev in (",", "-"))
        after_title = prev.lower() in _TITLES
        surname = (nxt[:1].isupper() and nxt[:1].isascii() and not nxt.isupper()
                   and nxt.lower() not in _OCCASION)
        kin = nxt.lower() in _KIN
        if after_title or surname or kin or not start:
            out.add(i)
    return frozenset(out)


# "!" with no feeling word: these cues decide what kind of news it is.
_BANG_LOSS = re.compile(r"\b(stole|stolen|robbed|lost|missing|broke|broken|crashed|"
                        r"ruined|spilt|spilled|popped|burnt|burned|flooded|gone)\b")
_BANG_RUSH = re.compile(r"\b(in|within) (\d+|a few|few|two|three|four|five|ten|"
                        r"fifteen|twenty|thirty) (minutes?|mins?|hours?|hrs?|seconds?|secs?)\b"
                        r"|\b(deadline|due today|due tomorrow|late|hurry|running late|"
                        r"last date|last day|leaving now|about to leave)\b")
_BANG_MED = re.compile(r"\b(hospital|doctor|fever|ambulance|injur\w*|bleed\w*|blood|"
                       r"accident|fracture\w*|stitches|bitten|allerg\w*|emergency)\b")

# Set False to read with rules only everywhere. The UI passes model=False
# per call instead and asks the model on a worker (see app._submit).
USE_MODEL = True


def _model_pick(text: str, model: bool = True):
    if not (model and USE_MODEL):
        return None
    # A synchronous caller (tests, tools) may wait for the one-off load; the
    # UI never gets here (USE_MODEL is off there) so the face never waits.
    fallback.start(wait=True)
    r = fallback.classify(text)
    if r is None:
        return None
    expr, conf, label = r
    return expr, f"model:{label} {conf:.2f}"


def _choose(text: str, low: str, emo: list[str], model: bool = True):
    if _HELD_OH.fullmatch(low.strip(" !.")):
        # A held "ohhh" is the penny dropping, not the short "oh!" flinch.
        return "surprised", "ohhh", ["oh"]
    best = None
    for toks in _tokens(low):
        scores, why = _score(toks, low, emo, _name_positions(text, len(toks)))
        if scores:
            fam = max(scores, key=lambda f: (scores[f], -_FAM_ORDER.get(f, 99)))
            cand = (scores[fam], fam, why[fam][1], toks)
        else:
            cand = (0.0, None, None, toks)
        if best is None or cand[0] > best[0]:
            best = cand
    sc, fam, why, toks = best
    if fam is not None and sc <= 0.55 and "?" in low:
        # A topic word ("Diwali", "party") in a question is still a question.
        return _QUESTION, "?", toks
    if fam is not None:
        return fam, why, toks

    # No word decided it. Read the punctuation and the shape of the line
    # before giving up on a neutral face - "Kaka got a new job in Dubai!" and
    # "!!!" are not the same as "add milk to the list".
    words = [t for t in toks if t not in _BREAK]
    stripped = low.strip(" !?.")
    if words and all(w == "no" for w in words) and (len(words) >= 2 or _RUN3.search(low)
                                                     or "!" in low):
        return "worried", "no no", toks
    if stripped in ("really", "seriously", "sach", "sachchi", "kya", "क्या", "सच",
                    "what") and ("?" in low or "!" in low):
        return "surprised", stripped, toks
    if stripped in ("काय", "kay", "huh", "what") and "?" in low:
        return "confusion", stripped, toks
    if "?" in text:
        if "??" in low:
            if _shouting(text):
                return "angry", "???", toks
            return "confusion", "??", toks
        return _QUESTION, "?", toks
    if "!" in text:
        # "!" raises a level; it never picks a feeling on its own. "I lost my
        # wallet!" and "Your mom called!" are news, so: a surprise.
        # An exclaimed YES is the exception - that is a word, and it is joy.
        if words and set(words) <= {"yes", "yess", "yay", "haan", "ho", "hoy", "again",
                                    "more", "yeah", "yup", "ok", "okay"}:
            return "delight", "yes!", toks
        # Bad news shouted is still bad news: a loss, a deadline, a doctor.
        if _BANG_MED.search(low):
            return "worried", "! (medical)", toks
        if _BANG_RUSH.search(low):
            return "worried", "! (deadline)", toks
        if _BANG_LOSS.search(low):
            return "fret", "! (loss)", toks
        m = _model_pick(text, model)
        if m and m[0] != "surprised":
            return m[0], m[1], toks
        # Nothing bad in it: a short exclaimed line is excitement - a child's
        # "a tree!", "look, a puppy!!".
        if words and len(words) <= 7:
            return "delight", "!", toks
        return "surprised", "!", toks
    m = _model_pick(text, model)
    if m:
        return m[0], m[1], toks
    return _DEFAULT, None, toks



def _read(text: str, model: bool = True):
    low, emo = _clean(text)
    name, why, toks = _choose(text, low, emo, model)
    # A shouted question with an emotional word is anger, not curiosity:
    # "WHY IS THE GEYSER NOT WORKING???".
    score = _level_score(text, low, toks, emo, name, why)
    if score >= 2:
        level = expressions.INTENSE
    elif score <= -1:
        level = expressions.LOW
    else:
        level = expressions.MID
    return name, level, why


def expression_of(text: str) -> tuple[str, str | None]:
    """Returns (expression, the phrase that chose it)."""
    name, _, why = _read(text)
    return name, why


def read(text: str, model: bool = True) -> tuple[str, str, float, str | None]:
    """Read a sentence.

    Returns (expression, level, intensity, the phrase that decided it).
    The intensity is already resolved through that expression's own three
    levels, because a 35% "startled" is a useful flinch and a 35% "asleep"
    is nothing at all.

    Rules first. Only a line the rules find no cue in is passed to the
    optional on-device model (fallback.py); model=False skips it, which is
    what the UI thread uses so it never waits on inference.
    """
    name, level, why = _read(text, model)
    return name, level, expressions.level_amount(name, level), why


# ---------------------------------------------------------------------------
# Paragraphs: one face per sentence, played in order
# ---------------------------------------------------------------------------

_SENT = re.compile(r"(?<=[.!?।॥])\s+")
# A turn inside one sentence is a second beat: "I passed, but barely".
_TURN = re.compile(r"(?<=\w),?\s+(?=(?:but|lekin|par|पर|पण|लेकिन)\s)", re.I)


def read_beats(text: str, model: bool = True) -> list[tuple[str, str, float, str | None, float]]:
    """Read a paragraph as the beats a listener's face goes through.

    "I got the job! But it's in Bangalore and I'll miss everyone." is two
    faces in a row, and a single read() can only ever show one of them.
    Returns [(expression, level, intensity, why, hold_seconds), ...]; a
    single sentence gives exactly what read() gives, with one beat.
    Consecutive sentences that read the same are merged into one beat, at
    the stronger of the two, so a calm paragraph does not twitch.
    """
    parts = []
    for p in _SENT.split(text.strip()):
        if not re.search(r"\w", p):
            continue
        bits = _TURN.split(p)
        if len(bits) > 1 and all(len(b.split()) >= 3 for b in bits):
            parts += bits
        else:
            parts.append(p)
    if len(parts) <= 1:
        r = read(text, model)
        return [r + (1.0,)]
    beats: list[list] = []
    for p in parts:
        name, level, amount, why = read(p, model)
        # A beat is held long enough to be seen, longer for a longer sentence.
        hold = max(0.9, min(2.2, 0.6 + 0.07 * len(p.split())))
        if beats and beats[-1][0] == name:
            b = beats[-1]
            if amount > b[2]:
                b[1], b[2], b[3] = level, amount, why
            b[4] = min(2.6, b[4] + hold * 0.5)
            continue
        beats.append([name, level, amount, why, hold])
    # A flat sentence between two that feel the same is part of that feeling:
    # "My dog is missing. We looked everywhere. I'm so scared." is one worry.
    i = 1
    while i < len(beats) - 1:
        if beats[i][0] == _DEFAULT and beats[i - 1][0] == beats[i + 1][0]:
            a, b = beats[i - 1], beats[i + 1]
            if b[2] > a[2]:
                a[1], a[2], a[3] = b[1], b[2], b[3]
            a[4] = min(2.6, a[4] + beats[i][4] * 0.5 + b[4] * 0.5)
            del beats[i:i + 2]
            continue
        i += 1
    # A flat sentence in the MIDDLE carries the feeling before it: the
    # listener's face does not drop to neutral for "We looked everywhere."
    i = 1
    while i < len(beats) - 1:
        if beats[i][0] == _DEFAULT and beats[i][3] is None and beats[i - 1][0] not in _NEUTRAL:
            beats[i - 1][4] = min(2.6, beats[i - 1][4] + beats[i][4] * 0.5)
            del beats[i]
            if beats[i - 1][0] == beats[i][0]:
                a, b = beats[i - 1], beats[i]
                if b[2] > a[2]:
                    a[1], a[2], a[3] = b[1], b[2], b[3]
                a[4] = min(2.6, a[4] + b[4] * 0.5)
                del beats[i]
            continue
        i += 1
    return [tuple(b) for b in beats]
