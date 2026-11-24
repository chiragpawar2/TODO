"""BLIND cases for homebot.face.reading (verification round 4).

Expectations were written BEFORE read() was run on any of them and were
never adjusted afterwards. None of these lines are taken or paraphrased from
VERIFY_ROUND_3.md, heldout_cases.py, expression_cases.py or conversations.py
(tests/run_blind.py checks exact/near-duplicate overlap and prints it).

Perspective: mirror the user's feeling; for lines aimed at homebot, homebot's
own reaction (hurt / shy / pleased).
"""

L, M, I = "low", "mid", "intense"
N = ["attentive", "listening", "rest", "answering"]
REQ = N + ["focused", "searching", "curious", "thinking"]
HAPPY = ["happy", "delight", "content", "grin"]
JOY = ["delight", "happy", "proud", "grin"]
SADF = ["sad", "crying"]
WORRY = ["worried", "fret", "dread"]
ANGRY = ["angry", "stern"]
HURT = ["sad", "apologetic", "fret", "shy"]
PLEASED = ["shy", "happy", "love", "proud", "tender", "delight", "content"]
SURP = ["surprised", "startled", "oh", "delight"]
TIRED = ["drowsy", "yawn", "sad", "bored"]
FEAR = ["dread", "worried", "alarmed", "fret"]
THANK = ["tender", "happy", "content", "love"]

_n = [0]


def S(cat, text, accept, level):
    _n[0] += 1
    return {"id": f"b{_n[0]:03d}", "category": cat, "text": text, "expected": list(accept),
            "expected_level": level.split("|")}


def B(accept, level):
    return {"accept": list(accept), "level": level.split("|")}


def MULTI(id, text, beats):
    return {"id": id, "category": "multi", "text": text, "expected": beats}


CASES = [
    # ---------------- plain: emotions x strengths ----------------
    S("plain", "the cake turned out nice", HAPPY, "low|mid"),
    S("plain", "I'm really glad you came over", HAPPY, "mid"),
    S("plain", "BEST DAY OF MY LIFE!!!", JOY, I),
    S("plain", "a bit gloomy today", SADF + ["bored"], "low"),
    S("plain", "I feel miserable", SADF, "mid"),
    S("plain", "I can't stop sobbing", ["crying", "sad"], "mid|intense"),
    S("plain", "that's a little irritating", ANGRY + ["skeptical"], "low"),
    S("plain", "I'm livid with the plumber", ANGRY, "mid|intense"),
    S("plain", "I AM SO FURIOUS RIGHT NOW", ANGRY, I),
    S("plain", "slightly nervous about the interview", WORRY, "low"),
    S("plain", "I'm anxious about Papa's surgery", WORRY, "mid"),
    S("plain", "I'm absolutely petrified", FEAR, "intense"),
    S("plain", "oh, that's unexpected", SURP, "low|mid"),
    S("plain", "no way, really?", SURP + ["skeptical"], "mid"),
    S("plain", "I'm a bit sleepy", TIRED, "low"),
    S("plain", "I'm worn out after the wedding", TIRED, "mid"),
    S("plain", "I adore my grandchildren", ["love", "tender", "happy"], "mid"),
    S("plain", "I'm a little bored", ["bored"], "low"),
    S("plain", "this is so dull", ["bored"], "mid"),
    S("plain", "I'm proud of my daughter", ["proud", "happy", "delight"], "mid"),
    S("plain", "I'm confused about the form", ["confusion", "thinking", "curious"], "mid"),
    S("plain", "I'm so embarrassed", ["shy", "apologetic", "fret"], "mid"),
    S("plain", "I'm sorry I forgot", ["apologetic"], "mid"),
    S("plain", "ugh, disgusting", ANGRY + ["skeptical", "squint"], "mid"),
    # ---------------- family speech ----------------
    S("family", "Dadi's knee is hurting again", WORRY + SADF, "mid"),
    S("family", "Mummy, I scored full marks in maths!", JOY, "mid|intense"),
    S("family", "Grandpa can't find his spectacles", REQ + WORRY + ["confusion"], "low|mid"),
    S("family", "the baby finally slept", ["content", "happy", "tender"] + N, "low|mid"),
    S("family", "my son didn't call on my birthday", SADF + ["fret"], "mid"),
    S("family", "Papa is coming home from the hospital today", HAPPY + ["tender"], "mid"),
    S("family", "Aai made puran poli, it was heavenly", HAPPY, "mid"),
    S("family", "the kids are fighting again", ANGRY + WORRY + ["bored"], "mid"),
    S("family", "Nani's flight got delayed", WORRY + SADF + N, "low|mid"),
    S("family", "my granddaughter took her first steps", JOY + ["tender", "love"], "mid|intense"),
    # ---------------- negation ----------------
    S("negation", "I'm not upset anymore", HAPPY + N + ["content"], "low|mid"),
    S("negation", "not bad at all", HAPPY + N, "low|mid"),
    S("negation", "I don't hate it", HAPPY + N + ["content"], "low|mid"),
    S("negation", "nobody is happy with this", SADF + ANGRY, "mid"),
    S("negation", "I'm hardly excited", SADF + N + ["bored"], "low|mid"),
    S("negation", "no need to panic", N + ["content", "tender"], "low|mid"),
    S("negation", "it isn't funny", ANGRY + ["skeptical", "sad"], "mid"),
    S("negation", "I never feel lonely with you around", PLEASED, "mid"),
    S("negation", "mujhe bilkul accha nahi lag raha", SADF, "mid"),
    S("negation", "mala nahi aavadla", SADF + ["skeptical"], "mid"),
    S("negation", "मैं दुखी नहीं हूँ", HAPPY + N + ["content"], "low|mid"),
    S("negation", "without any worry now", ["content", "happy"] + N, "low|mid"),
    # ---------------- Hinglish / romanised ----------------
    S("hinglish", "aaj bahut khushi hui", HAPPY, "mid"),
    S("hinglish", "khooshi ke maare naach rahi hoon", JOY, "mid|intense"),
    S("hinglish", "ekdum jhakaas movie", JOY, "mid"),
    S("hinglish", "bindaas raho yaar", HAPPY + ["content", "grin"], "low|mid"),
    S("hinglish", "yeh phone bekaar hai", ANGRY + SADF + ["skeptical"], "mid"),
    S("hinglish", "mera dimag kharab mat kar", ANGRY, "mid"),
    S("hinglish", "bahut tension ho raha hai", WORRY, "mid"),
    S("hinglish", "mujhe neend aa rahi hai", TIRED, "mid"),
    S("hinglish", "dar lag raha hai", FEAR, "mid"),
    S("hinglish", "bahut gussa aa raha hai", ANGRY, "mid"),
    S("hinglish", "mann udaas hai", SADF, "mid"),
    S("hinglish", "kya baat hai! zabardast", JOY, "mid"),
    S("hinglish", "pagal ho gaya hai kya", ANGRY + ["skeptical", "surprised"], "mid"),
    S("hinglish", "thak gayi hoon", TIRED, "mid"),
    S("marathi", "lay bhari zhala", JOY, "mid"),
    S("marathi", "mast ahe he", HAPPY, "mid"),
    S("marathi", "khup kantala aala", ["bored"] + TIRED, "mid"),
    S("marathi", "mala bhiti vatte", FEAR, "mid"),
    S("marathi", "khup raag aalay", ANGRY, "mid"),
    S("marathi", "mala vait vatla", SADF, "mid"),
    S("marathi", "zop yetey", TIRED, "mid"),
    S("marathi", "ekdum jhakas re", JOY, "mid"),
    # ---------------- Devanagari ----------------
    S("devanagari", "मुझे बहुत खुशी है", HAPPY, "mid"),
    S("devanagari", "मला खूप आनंद झाला", HAPPY, "mid"),
    S("devanagari", "मैं बहुत थका हुआ हूँ", TIRED, "mid"),
    S("devanagari", "मला भीती वाटते", FEAR, "mid"),
    S("devanagari", "मुझे गुस्सा आ रहा है", ANGRY, "mid"),
    S("devanagari", "रोहन आज रोटी लाया", N + REQ, "low|mid"),
    S("devanagari", "बहुत उदास लग रहा है", SADF, "mid"),
    S("devanagari", "दिल टूट गया", SADF, "mid|intense"),
    S("devanagari", "पेट में चूहे दौड़ रहे हैं", ["drowsy", "fret", "curious", "happy", "grin"] + N, "low|mid"),
    S("devanagari", "डरबन का मैच कब है?", REQ, "low|mid"),
    S("devanagari", "मस्तक पर तिलक लगाओ", REQ, "low|mid"),
    S("devanagari", "धन्यवाद बेटा", THANK, "low|mid"),
    # ---------------- English idioms ----------------
    S("idiom", "I'm over the moon", JOY, "mid|intense"),
    S("idiom", "I've been down in the dumps all week", SADF, "mid"),
    S("idiom", "she's on cloud nine", JOY, "mid"),
    S("idiom", "I'm fed up to here with this", ANGRY + ["bored"], "mid|intense"),
    S("idiom", "I'm at my wits' end", WORRY + ANGRY, "mid|intense"),
    S("idiom", "my heart sank", SADF + WORRY, "mid"),
    S("idiom", "I'm shaking like a leaf", FEAR, "mid|intense"),
    S("idiom", "I'm dead tired", TIRED, "mid|intense"),
    S("idiom", "that made my day", HAPPY + ["tender"], "mid"),
    S("idiom", "I'm walking on air", JOY, "mid"),
    S("idiom", "it gets on my nerves", ANGRY, "mid"),
    S("idiom", "pet mein chuhe kood rahe hain", N + ["fret", "curious", "grin", "happy"], "low|mid"),
    S("idiom", "dil toot gaya yaar", SADF, "mid|intense"),
    S("idiom", "dil garden garden ho gaya", JOY, "mid"),
    S("idiom", "naak mein dum kar diya", ANGRY + ["bored"], "mid"),
    # ---------------- emoji ----------------
    S("emoji", "🥳🥳", JOY, "mid|intense"),
    S("emoji", "result aaya 😩", SADF + TIRED + WORRY, "mid"),
    S("emoji", "ok 🙄", ["skeptical", "bored", "angry"], "low|mid"),
    S("emoji", "Dadu's back home ❤️🙏", THANK + HAPPY, "mid"),
    S("emoji", "😱 the gas was on all night", FEAR + ["startled"], "mid|intense"),
    S("emoji", "😴😴", ["drowsy", "asleep", "yawn"], "mid"),
    S("emoji", "lol 😂😂", HAPPY, "mid|intense"),
    S("emoji", "miss you nana 🥺", SADF + ["tender", "love"], "mid"),
    S("emoji", "🤬🤬🤬", ANGRY, I),
    S("emoji", "passed my driving test 🥲", HAPPY + ["tender", "proud"], "mid"),
    # ---------------- typos ----------------
    S("typo", "im so hapyy", HAPPY, "mid"),
    S("typo", "feeling realy sad", SADF, "mid"),
    S("typo", "im scaredd", FEAR, "mid"),
    S("typo", "soooo tird", TIRED, "mid|intense"),
    S("typo", "thnks a lot", THANK, "low|mid"),
    S("typo", "im angy", ANGRY, "mid"),
    S("typo", "exciteddd", JOY, "mid|intense"),
    # ---------------- sarcasm ----------------
    S("sarcasm", "oh wonderful, the power's gone again", ANGRY + ["skeptical", "bored", "sad"], "mid"),
    S("sarcasm", "yeah, because I have all the time in the world", ANGRY + ["skeptical", "bored"], "mid"),
    S("sarcasm", "fantastic, another parking ticket", ANGRY + ["skeptical", "sad"], "mid"),
    S("sarcasm", "wow, so helpful, thanks", ["skeptical", "angry", "stern", "sad"], "mid"),
    S("sarcasm", "kya baat hai, phir se late", ANGRY + ["skeptical"], "mid"),
    # ---------------- context / word-sense traps ----------------
    S("context", "the shoes are a steal", HAPPY + N, "low|mid"),
    S("context", "I'm dying of laughter", HAPPY, "mid|intense"),
    S("context", "the traffic is killing me", ANGRY + TIRED + ["fret"], "mid"),
    S("context", "that paneer was criminally good", HAPPY, "mid"),
    S("context", "the exam was a breeze", HAPPY + ["proud", "content"], "mid"),
    S("context", "I could kill for a cup of chai", HAPPY + N + TIRED + ["curious"], "low|mid"),
    S("context", "she's crazy talented", JOY + ["surprised"], "mid"),
    S("context", "my phone died", ANGRY + N + ["sad", "fret"], "low|mid"),
    S("context", "the plant is dying", SADF + WORRY, "mid"),
    S("context", "I'm sick of this weather", ANGRY + ["bored", "sad"], "mid"),
    # ---------------- names / places that look like keywords ----------------
    S("names", "call Sukhi aunty", REQ, "low|mid"),
    S("names", "Anand Vihar station kitna door hai", REQ, "low|mid"),
    S("names", "is Joy coming for dinner?", REQ, "low|mid"),
    S("names", "Khushi's tuition is at 5", REQ, "low|mid"),
    S("names", "book a cab to Happy Valley", REQ, "low|mid"),
    S("names", "Mr. Sadhu sent a parcel", REQ, "low|mid"),
    S("names", "play Kishore Kumar songs", REQ, "low|mid"),
    S("names", "Prem bhaiya called", REQ, "low|mid"),
    S("names", "send it to Mrs. Gussain", REQ, "low|mid"),
    S("names", "Patience is at the door", REQ, "low|mid"),
    # ---------------- household commands ----------------
    S("command", "switch off the geyser", REQ, "low|mid"),
    S("command", "remind me to pay the society maintenance", REQ, "low|mid"),
    S("command", "what's for dinner tonight", REQ, "low|mid"),
    S("command", "lights band karo", REQ, "low|mid"),
    S("command", "doodh ka order daal do", REQ, "low|mid"),
    S("command", "kill the lights in the hall", REQ, "low|mid"),
    S("command", "set a timer for the pressure cooker, three whistles", REQ, "low|mid"),
    S("command", "पंखा चालू करो", REQ, "low|mid"),
    # ---------------- children's excited one-liners ----------------
    S("kids", "a tree!", SURP + JOY + ["curious"], "mid"),
    S("kids", "look, a puppy!!", SURP + JOY + ["curious", "love"], "mid|intense"),
    S("kids", "a rainbow!!!", SURP + JOY, "mid|intense"),
    S("kids", "I lost my tooth!", SURP + JOY + ["proud"], "mid|intense"),
    S("kids", "mama, a butterfly!", SURP + JOY + ["curious"], "mid"),
    S("kids", "it's snowing!", SURP + JOY, "mid|intense"),
    S("kids", "I don't want to go to school", SADF + ANGRY + ["fret", "bored"], "mid"),
    S("kids", "my balloon popped", SADF + ["startled", "surprised"], "mid"),
    # ---------------- aimed at homebot ----------------
    S("to_bot", "homebot you're my best friend", PLEASED, "mid"),
    S("to_bot", "you're so cute", PLEASED, "mid"),
    S("to_bot", "you're dumb", HURT, "mid"),
    S("to_bot", "I'm proud of you homebot", PLEASED, "mid"),
    S("to_bot", "go away, you're annoying", HURT, "mid"),
    S("to_bot", "you got it wrong again", HURT, "mid"),
]

MULTI_CASES = [
    MULTI("mb01", "I got the promotion! But we have to move to Bangalore.",
          [B(JOY, "mid|intense"), B(SADF + WORRY, "mid")]),
    MULTI("mb02", "The dog ran off this morning. We found him by the temple. I'm so relieved.",
          [B(WORRY + SADF, "mid"), B(N + HAPPY + REQ, "low|mid"), B(HAPPY + ["content"], "mid")]),
    MULTI("mb03", "Ajji fell in the garden. She's okay now, thank god.",
          [B(FEAR + SADF, "mid"), B(HAPPY + ["content", "tender"], "low|mid")]),
    MULTI("mb04", "I failed the driving test. I'm so embarrassed.",
          [B(SADF, "mid"), B(["shy", "apologetic", "fret", "sad"], "mid")]),
    MULTI("mb05", "Wow, the house looks amazing! Who did all this?",
          [B(JOY + SURP, "mid|intense"), B(SURP + ["curious"] + N, "mid")]),
    MULTI("mb06", "I'm exhausted. The baby was up all night. But she smiled at me this morning.",
          [B(TIRED, "mid"), B(TIRED + N + SADF, "low|mid"), B(HAPPY + ["tender", "love"], "mid")]),
    MULTI("mb07", "Stop shouting! I can hear you fine.",
          [B(ANGRY, "mid|intense"), B(ANGRY + N, "low|mid")]),
    MULTI("mb08", "Sorry I'm late. The train was cancelled.",
          [B(["apologetic"], "mid"), B(ANGRY + SADF + N, "low|mid")]),
    MULTI("mb09", "Our flight is tomorrow. I'm nervous, I've never flown before.",
          [B(N + REQ, "low|mid"), B(WORRY, "mid"), B(WORRY + N, "low|mid")]),
    MULTI("mb10", "Thank you for the gift. I love it!",
          [B(THANK, "mid"), B(["love"] + JOY, "mid|intense")]),
    MULTI("mb11", "My best friend is moving abroad. I'll miss her terribly.",
          [B(SADF + N, "low|mid"), B(SADF, "mid|intense")]),
    MULTI("mb12", "The results are out! I came first in the district!",
          [B(SURP + JOY, "mid|intense"), B(JOY, "mid|intense")]),
    MULTI("mb13", "I was so scared during the storm. Now it's calm and sunny.",
          [B(FEAR, "mid"), B(HAPPY + ["content"] + N, "low|mid")]),
    MULTI("mb14", "The neighbour's music is too loud. It's midnight. I'm furious.",
          [B(ANGRY, "mid"), B(N + ANGRY, "low|mid"), B(ANGRY, "mid|intense")]),
    MULTI("mb15", "Aaj result aaya. Main pass ho gaya! Bahut khush hoon.",
          [B(N + SURP, "low|mid"), B(JOY, "mid|intense"), B(HAPPY, "mid")]),
    MULTI("mb16", "आज बहुत थकान है। लेकिन काम पूरा हो गया।",
          [B(TIRED, "mid"), B(HAPPY + ["content", "proud"] + N, "low|mid")]),
    MULTI("mb17", "Mala khup bhiti vatli. Pan aata bara vatat ahe.",
          [B(FEAR, "mid"), B(HAPPY + ["content"], "low|mid")]),
    MULTI("mb18", "My grandfather passed away last night. He was ninety two. He had a good life.",
          [B(SADF, "mid|intense"), B(SADF + N, "low|mid"), B(["tender", "sad", "content"] + N, "low|mid")]),
    MULTI("mb19", "I burnt the dal. Everyone is hungry. What do I do now?",
          [B(["apologetic", "fret", "sad"] + WORRY, "mid"), B(WORRY + N, "low|mid"), B(WORRY + ["confusion", "thinking"], "mid")]),
    MULTI("mb20", "Haha that was hilarious. Tell me another one!",
          [B(HAPPY, "mid|intense"), B(HAPPY + REQ, "mid")]),
    MULTI("mb21", "I'm bored. There's nothing on TV.",
          [B(["bored"], "mid"), B(["bored"] + N + ["sad"], "low|mid")]),
    MULTI("mb22", "The doctor says it's not serious. What a relief!",
          [B(N + ["content", "happy"], "low|mid"), B(HAPPY + ["content"], "mid|intense")]),
    MULTI("mb23", "Someone stole my cycle! I just bought it last week.",
          [B(ANGRY + SADF + ["startled"], "mid|intense"), B(SADF + ANGRY + N, "low|mid")]),
    MULTI("mb24", "Happy anniversary, Aai and Baba! Love you both so much.",
          [B(JOY, "mid|intense"), B(["love", "tender"] + HAPPY, "mid|intense")]),
    MULTI("mb25", "I can't find my passport. The flight is in three hours!",
          [B(WORRY, "mid"), B(FEAR, "mid|intense")]),
    MULTI("mb26", "We won the match! Then it started pouring and we all got soaked.",
          [B(JOY, "mid|intense"), B(N + HAPPY + SADF + SURP, "low|mid")]),
    MULTI("mb27", "Please don't be angry. I broke your favourite cup.",
          [B(["apologetic", "fret", "worried"], "mid"), B(["apologetic"], "mid")]),
    MULTI("mb28", "He proposed! I said yes! I'm still shaking.",
          [B(JOY + SURP, "mid|intense"), B(JOY, "mid|intense"), B(JOY + SURP + FEAR, "mid|intense")]),
    MULTI("mb29", "Ugh, Monday again. At least there's cake in the office.",
          [B(["bored"] + ANGRY + TIRED, "mid"), B(HAPPY + ["content"], "low|mid")]),
    MULTI("mb30", "Nana is not well. The ambulance is on its way. Please pray for him.",
          [B(WORRY + SADF, "mid"), B(FEAR, "mid|intense"), B(WORRY + SADF + ["tender"], "mid")]),
]
