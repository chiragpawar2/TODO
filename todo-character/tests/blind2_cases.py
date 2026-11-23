"""BLIND-2 cases for homebot.face.reading (verification round 5).

Written and expectations FIXED before read() was run on any of them; never
adjusted afterwards. Deliberately avoids phrases in tests/*.py, tests/*.md
and homebot/face/lexicon.py (tests/run_blind2.py checks and reports overlap).

Perspective: mirror the user's feeling; for lines aimed at homebot, homebot's
own reaction (hurt / shy / pleased).  "neutral" category = lines a big
lexicon might over-trigger on; they must stay in N (or a question face).
"""

L, M, I = "low", "mid", "intense"
N = ["attentive", "listening", "rest", "answering"]
Q = N + ["curious", "thinking", "focused", "searching"]
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
SKEP = ["skeptical", "stern", "bored", "sad"]
CALM = ["content", "happy", "tender"]
DISGUST = ["angry", "stern", "skeptical"]

_n = [0]


def S(cat, text, accept, level="mid"):
    _n[0] += 1
    return {"id": f"x{_n[0]:03d}", "category": cat, "text": text, "expected": list(accept),
            "expected_level": level.split("|")}


def B(accept, level="low|mid|intense"):
    return {"accept": list(accept), "level": level.split("|")}


def MULTI(id, text, beats):
    return {"id": id, "category": "multi", "text": text, "expected": beats}


LM, MI, ANY = "low|mid", "mid|intense", "low|mid|intense"

CASES = [
    # ---------------- plain: emotions x 3 strengths ----------------
    S("plain", "the soup is decent", HAPPY + ["content"], LM),
    S("plain", "I'm delighted with how the paint looks", HAPPY, M),
    S("plain", "THIS IS THE GREATEST THING EVER!!!", JOY, I),
    S("plain", "feeling a touch low this evening", SADF + ["bored"], L),
    S("plain", "I feel so lonely these days", SADF, M),
    S("plain", "I'm completely heartbroken and can't eat", SADF, MI),
    S("plain", "mildly annoyed with the cable guy", ANGRY + ["skeptical"], L),
    S("plain", "I'm really fed up with the landlord", ANGRY + ["bored"], M),
    S("plain", "I'M SO ENRAGED I COULD SCREAM", ANGRY, I),
    S("plain", "a little uneasy about the drive", WORRY, L),
    S("plain", "I'm stressed about the loan papers", WORRY, M),
    S("plain", "I'm terrified, the house is shaking", FEAR + ["startled"], I),
    S("plain", "huh, didn't expect that", SURP + ["confusion"], LM),
    S("plain", "I'm stunned", SURP, M),
    S("plain", "kind of drowsy after lunch", TIRED, L),
    S("plain", "I'm exhausted from the night shift", TIRED, M),
    S("plain", "I'm so bored I could cry", ["bored", "sad"], M),
    S("plain", "that smell is disgusting", DISGUST + ["sad"], M),
    S("plain", "I'm so embarrassed", ["shy", "apologetic"], M),
    S("plain", "I'm grateful for everything you did", THANK, M),
    S("plain", "I feel calm and peaceful", CALM, LM),
    S("plain", "I'm so proud of myself", ["proud", "happy", "delight"], M),
    S("plain", "that was hilarious", ["grin", "happy", "delight"], M),
    S("plain", "I'm a little confused by the form", ["confusion", "thinking", "curious"], LM),

    # ---------------- kids ----------------
    S("kids", "Mumma, Tanmay pinched me", HURT + ANGRY + ["sad"], M),
    S("kids", "I don't like broccoli, yuck", DISGUST + ["sad", "skeptical"], M),
    S("kids", "my sandcastle got washed away", SADF + ["fret"], M),
    S("kids", "I can tie my own shoelaces now!", JOY, MI),
    S("kids", "there's a lizard on the wall, eek", FEAR + ["startled"], MI),
    S("kids", "nobody wants to play with me at recess", SADF, M),
    S("kids", "I got a gold star today", JOY, M),
    S("kids", "my tummy feels funny", WORRY + SADF, M),
    S("kids", "can we go to the zoo, pleeease", ["happy", "delight", "curious", "hopeful"] + N, M),
    S("kids", "I'm scared of the dark", FEAR, M),

    # ---------------- parents ----------------
    S("parents", "the kids finally slept, phew", CALM + ["drowsy"], LM),
    S("parents", "the school called again about Aryan's behaviour", WORRY + ANGRY + ["sad"], M),
    S("parents", "my daughter cleared her board exams with distinction", JOY, M),
    S("parents", "the electricity bill is double this month", WORRY + ANGRY + ["surprised"], M),
    S("parents", "I barely had time to breathe today", TIRED + WORRY, M),
    S("parents", "the baby kept us up all night", TIRED, M),
    S("parents", "my husband forgot our anniversary", SADF + ANGRY, M),
    S("parents", "we're finally debt free", JOY + CALM, M),

    # ---------------- grandparents ----------------
    S("grand", "my hip is acting up again", SADF + WORRY, M),
    S("grand", "nobody visits me anymore", SADF, M),
    S("grand", "my great-grandson was born this morning", JOY, M),
    S("grand", "I keep forgetting where I kept my spectacles", WORRY + ["sad", "confusion", "bored"], M),
    S("grand", "the grandkids made me a card, so sweet", THANK + ["happy"], M),
    S("grand", "my old friend Shanta passed last night", SADF, M),

    # ---------------- negation ----------------
    S("negation", "I'm not thrilled about it", SADF + SKEP, LM),
    S("negation", "not exactly a fun evening", SADF + SKEP + ["bored"], LM),
    S("negation", "I'm not worried at all", CALM + N, LM),
    S("negation", "it's not that I'm angry, just tired", TIRED + SADF, LM),
    S("negation", "never been this happy", JOY, MI),
    S("negation", "I couldn't be more pleased", JOY, MI),
    S("negation", "don't be sad, it's fine", ["tender", "content"] + N + SADF, LM),
    S("negation", "no one remembered my name", SADF, M),
    S("negation", "I can't sleep at all", WORRY + TIRED, M),
    S("negation", "it doesn't hurt anymore", CALM + N, LM),
    S("negation", "I'm not feeling well", SADF + WORRY, M),
    S("negation", "nothing is going right", SADF + WORRY, M),

    # ---------------- hinglish (romanised Hindi) ----------------
    S("hinglish", "dil bhar aaya", SADF + ["tender"], M),
    S("hinglish", "bahut tension ho gaya hai yaar", WORRY, M),
    S("hinglish", "aaj mann bahut udaas hai", SADF, M),
    S("hinglish", "itna gussa aa raha hai na", ANGRY, MI),
    S("hinglish", "maine paper top kar diya", JOY, M),
    S("hinglish", "pet mein chuhe daud rahe hain", ["hungry", "bored", "content"] + N, ANY),
    S("hinglish", "sar dard se phat raha hai", SADF + WORRY, MI),
    S("hinglish", "mujhe darr lag raha hai", FEAR, M),
    S("hinglish", "ekdum mast feel ho raha hai", HAPPY, M),
    S("hinglish", "yeh toh kamaal ho gaya", JOY + SURP, M),
    S("hinglish", "dimaag kharab mat karo", ANGRY, M),
    S("hinglish", "bas thak gayi hoon", TIRED, M),
    S("hinglish", "kuch samajh nahi aa raha", ["confusion", "thinking", "worried"], M),
    S("hinglish", "doodh ubal gaya, chhodo", N + ["bored"], LM),

    # ---------------- marathi (romanised) ----------------
    S("marathi", "mala khup aanand jhala", JOY, M),
    S("marathi", "maza mood kharab aahe", SADF + ANGRY, M),
    S("marathi", "dokyala tap hotoy", SADF + WORRY + ANGRY, M),
    S("marathi", "bhiti vatte mala", FEAR, M),
    S("marathi", "ekdum zakaas", JOY, M),
    S("marathi", "kantaalun gelo", ["bored", "drowsy", "sad"], M),
    S("marathi", "tula kiti vela sangitla", ANGRY, M),
    S("marathi", "aai, bhook lagli", ["hungry"] + N, ANY),

    # ---------------- devanagari ----------------
    S("devanagari", "मन बहुत भारी है", SADF, M),
    S("devanagari", "मुझे बहुत गर्व है", ["proud", "happy"], M),
    S("devanagari", "बहुत डर लग रहा है", FEAR, M),
    S("devanagari", "मला खूप राग आला", ANGRY, M),
    S("devanagari", "आज मी खूप खुश आहे", HAPPY, M),
    S("devanagari", "थकान से बुरा हाल है", TIRED, M),
    S("devanagari", "वाह, क्या खुशखबरी है", JOY + SURP, M),
    S("devanagari", "बत्ती बंद कर दो", N, ANY),
    S("devanagari", "मला काळजी वाटते", WORRY, M),

    # ---------------- English idioms (not in IDIOMS) ----------------
    S("idiom", "I'm on pins and needles waiting for the result", WORRY, M),
    S("idiom", "she's got butterflies before the recital", WORRY, M),
    S("idiom", "I'm at the end of my rope", WORRY + ANGRY + SADF + TIRED, M),
    S("idiom", "that really ruffled my feathers", ANGRY, M),
    S("idiom", "I'm as happy as a dog with two tails", JOY, M),
    S("idiom", "my blood is boiling", ANGRY, MI),
    S("idiom", "I could sleep for a week", TIRED, M),
    S("idiom", "it scared the living daylights out of me", FEAR + ["startled"], MI),
    S("idiom", "I'm tickled to death", JOY, M),
    S("idiom", "feeling like a million bucks", JOY, M),
    S("idiom", "I'm running on fumes", TIRED, M),
    S("idiom", "my heart is in my mouth", FEAR, M),
    S("idiom", "this is the last straw", ANGRY, MI),
    S("idiom", "I'm bent out of shape over it", ANGRY + WORRY, M),
    S("idiom", "I'm in a pickle", WORRY, M),

    # ---------------- life events (not in EVENTS) ----------------
    S("event", "our offer on the flat got accepted", JOY, M),
    S("event", "the biopsy came back benign", CALM + JOY, M),
    S("event", "my visa got rejected", SADF + ["fret"], M),
    S("event", "the car was towed from outside the bank", ANGRY + WORRY + SADF, M),
    S("event", "the landlord wants us out by Friday", WORRY + ANGRY, M),
    S("event", "my sister is getting divorced", SADF + WORRY, M),
    S("event", "I finally got my driving licence", JOY, M),
    S("event", "the factory is laying people off", WORRY + SADF, M),
    S("event", "Nani slipped in the bathroom", WORRY + FEAR, M),
    S("event", "we won the society cricket final", JOY, M),
    S("event", "my startup got its first paying customer", JOY, M),
    S("event", "the vet says Bruno needs surgery", WORRY + SADF, M),

    # ---------------- typos (not pre-generated) ----------------
    S("typo", "im so exctied for tomorow", JOY, M),
    S("typo", "feeling realy lonley", SADF, M),
    S("typo", "im so frustared", ANGRY, M),
    S("typo", "this is so embarassing", ["shy", "apologetic"], M),
    S("typo", "i am terrifed", FEAR, MI),
    S("typo", "so gratefull for you", THANK, M),
    S("typo", "im exaused", TIRED, M),
    S("typo", "im so greatful and hapy", THANK + HAPPY, M),

    # ---------------- sarcasm (not in SARCASM) ----------------
    S("sarcasm", "oh joy, the in-laws are staying a month", SKEP + ANGRY + SADF, ANY),
    S("sarcasm", "awesome, the wifi died during my call", SKEP + ANGRY + SADF, ANY),
    S("sarcasm", "love that for me, a flat tyre at midnight", SKEP + ANGRY + SADF, ANY),
    S("sarcasm", "yay, more homework", SKEP + ["bored", "sad"], ANY),
    S("sarcasm", "bahut badhiya, phir se light chali gayi", SKEP + ANGRY + SADF, ANY),
    S("sarcasm", "terrific, the milk curdled again", SKEP + ANGRY + SADF, ANY),

    # ---------------- emoji ----------------
    S("emoji", "😭😭", SADF, MI),
    S("emoji", "results are out 🎉🎉", JOY, M),
    S("emoji", "😡", ANGRY, M),
    S("emoji", "ok 🙂", HAPPY + N, LM),
    S("emoji", "Monday again 😩", TIRED + SADF + ["bored"], M),
    S("emoji", "🥺 please don't go", SADF + WORRY + ["tender"], M),
    S("emoji", "💀💀 that video", ["grin", "happy", "delight"], M),
    S("emoji", "😴", TIRED + ["asleep"], ANY),

    # ---------------- context traps ----------------
    S("context", "the movie was sad but I loved it", HAPPY + ["love", "tender", "content"], M),
    S("context", "I cried laughing at the wedding video", ["grin", "happy", "delight"], M),
    S("context", "scary movie night with the kids tonight", HAPPY + N + ["curious"], ANY),
    S("context", "killer deal on the washing machine", HAPPY + N, ANY),
    S("context", "the dog died in the book I'm reading", SADF + N, ANY),
    S("context", "I'm dying to see the new baby", JOY + ["hopeful"], M),
    S("context", "that drummer was sick", JOY, M),
    S("context", "the exam was a nightmare", SADF + WORRY + ANGRY, M),
    S("context", "I'm happy for her but I'll miss her", SADF + ["tender", "content", "happy"], M),
    S("context", "I'd hate to miss your recital", ["tender", "happy", "content"] + SADF + N, ANY),

    # ---------------- household commands (stay neutral) ----------------
    S("command", "set a timer for the dal, twenty minutes", Q, ANY),
    S("command", "remind me to pay the society maintenance", Q, ANY),
    S("command", "turn the geyser on at six", Q, ANY),
    S("command", "play some old Kishore Kumar songs", Q, ANY),
    S("command", "add atta and haldi to the list", Q, ANY),
    S("command", "call the gas agency", Q, ANY),
    S("command", "switch off the bedroom fan", Q, ANY),
    S("command", "what time does the chemist close", Q, ANY),

    # ---------------- names / places that look like feelings ----------------
    S("names", "is Anand uncle coming for lunch", Q, ANY),
    S("names", "message Khushi that I'm late", Q, ANY),
    S("names", "Santosh will drop the parcel", Q, ANY),
    S("names", "book a cab to Shanti Nagar", Q, ANY),
    S("names", "Hope Street is closed today", Q, ANY),
    S("names", "tell Gloria the meeting moved", Q, ANY),
    S("names", "Sukhmani is staying over", Q, ANY),
    S("names", "drive to Paradise circle", Q, ANY),
    S("names", "Mr. Bliss from the bank called", Q, ANY),
    S("names", "Aanandi needs a lift to class", Q, ANY),

    # ---------------- said to homebot ----------------
    S("to_bot", "you're a sweetheart, homebot", PLEASED, M),
    S("to_bot", "you never listen to me", HURT + ["sad"], M),
    S("to_bot", "homebot, you're hopeless", HURT, M),
    S("to_bot", "good job on the reminder", PLEASED, M),
    S("to_bot", "I missed you today, robot", PLEASED + ["tender"], M),
    S("to_bot", "shut up, homebot", HURT + ANGRY, MI),
    S("to_bot", "you look adorable when you blink", PLEASED, M),
    S("to_bot", "you messed up my alarm", HURT, M),

    # ---------------- NEUTRAL over-trigger checks ----------------
    S("neutral", "the bus stop is near the temple", Q, ANY),
    S("neutral", "I need to iron my shirt", Q, ANY),
    S("neutral", "the pressure cooker whistled twice", Q, ANY),
    S("neutral", "keep the blue bag near the door", Q, ANY),
    S("neutral", "the doctor's clinic is on the second floor", Q, ANY),
    S("neutral", "we are out of sugar", Q + ["sad"], ANY),
    S("neutral", "Grandpa is reading the paper", Q, ANY),
    S("neutral", "the train leaves platform four at nine", Q, ANY),
    S("neutral", "my cousin works at a bank in Pune", Q, ANY),
    S("neutral", "the hospital canteen opens at seven", Q, ANY),
    S("neutral", "school reopens on the fifteenth", Q, ANY),
    S("neutral", "put the cold drinks in the fridge", Q, ANY),
    S("neutral", "the fire extinguisher is under the sink", Q, ANY),
    S("neutral", "the cat is sleeping on the sofa", Q + CALM, ANY),
    S("neutral", "a heavy box arrived for you", Q, ANY),
    S("neutral", "the match starts at eight", Q, ANY),
    S("neutral", "dad is cutting the grass", Q, ANY),
    S("neutral", "aaj sabzi mein aloo hai", Q, ANY),
    S("neutral", "kal market band hai", Q, ANY),
    S("neutral", "udya shala aahe", Q, ANY),
    S("neutral", "the kids are at tuition", Q, ANY),
    S("neutral", "the funeral home is next to the post office", Q, ANY),
    S("neutral", "I watched a documentary about war", Q, ANY),
    S("neutral", "the crying baby emoji is in the second row", Q, ANY),
    S("neutral", "the battery is at fifty percent", Q, ANY),
    S("neutral", "we killed the lights and went to bed", Q + TIRED, ANY),
    S("neutral", "the broken chair is in the store room", Q, ANY),
    S("neutral", "the gift shop sells candles", Q, ANY),
]

MULTI_CASES = [
    MULTI("y01", "I got the promotion! But I have to move to Hyderabad. The kids will hate it.",
          [B(JOY), B(SADF + WORRY)]),
    MULTI("y02", "The flight got cancelled. We waited six hours. Finally we got seats on the next one, thank god.",
          [B(SADF + ANGRY + WORRY), B(CALM + JOY + THANK)]),
    MULTI("y03", "Pinky ran away from home this morning. We found her at the station. She is safe now.",
          [B(FEAR + WORRY), B(CALM + JOY + THANK)]),
    MULTI("y04", "I was so nervous before the speech. Then everyone clapped! I'm so proud.",
          [B(WORRY), B(JOY)]),
    MULTI("y05", "Dadi fell asleep in her chair. She looked so peaceful. I covered her with a shawl.",
          [B(CALM + TIRED + ["tender"] + N)]),
    MULTI("y06", "The neighbour cut our mango tree without asking. I am furious. Papa is going to talk to him.",
          [B(ANGRY + SADF), B(ANGRY + N)]),
    MULTI("y07", "We lost the match. The boys were crying. But the coach said he was proud of them.",
          [B(SADF), B(["proud", "tender", "content", "happy"])]),
    MULTI("y08", "Your Nana called. He sounded weak. The doctor wants to see him tomorrow.",
          [B(N + WORRY), B(WORRY + SADF)]),
    MULTI("y09", "I burnt the rotis again. Everyone laughed. Honestly, it was funny.",
          [B(SADF + ["apologetic", "shy", "fret"]), B(["grin", "happy", "delight"])]),
    MULTI("y10", "mujhe naukri mil gayi! Lekin salary kam hai. Chalo, shuruaat toh hai.",
          [B(JOY), B(SADF + SKEP + WORRY), B(CALM + HAPPY)]),
    MULTI("y11", "aaj office mein boss ne daanta. Ghar aake bachchon ko dekha toh sab theek lag raha hai.",
          [B(SADF + ANGRY + HURT), B(CALM + HAPPY + ["tender"])]),
    MULTI("y12", "Aaji la hospital madhe admit kela. Ata ti bari aahe.",
          [B(WORRY + SADF), B(CALM + HAPPY)]),
    MULTI("y13", "मेरा फोन खो गया। बहुत गुस्सा आ रहा है। फिर भाई ने ढूंढ दिया।",
          [B(SADF + WORRY + ["fret"]), B(ANGRY), B(CALM + HAPPY + THANK)]),
    MULTI("y14", "The power went out during the exam prep. I panicked. Then I found the candles and kept going.",
          [B(N + WORRY + ANGRY + SADF), B(FEAR + WORRY), B(CALM + ["proud", "focused"] + N)]),
    MULTI("y15", "Grandma made my favourite kheer. I ate three bowls. Now I can't move.",
          [B(HAPPY + THANK + ["love"]), B(TIRED + ["grin"] + HAPPY + N)]),
    MULTI("y16", "My best friend is moving abroad. I'm happy for him. I'll really miss our evening walks.",
          [B(SADF + N), B(HAPPY), B(SADF)]),
    MULTI("y17", "The puppy chewed my new shoes! I wanted to shout. Then he looked at me with those eyes.",
          [B(ANGRY + SURP + SADF), B(ANGRY), B(["tender", "love", "happy", "content", "grin"])]),
    MULTI("y18", "Results came today. I failed maths. Papa didn't shout, he just hugged me.",
          [B(N + WORRY), B(SADF), B(["tender", "love", "content"] + SADF)]),
    MULTI("y19", "I can't find Mummy's ring anywhere. I've checked every drawer. I'm panicking now.",
          [B(WORRY + FEAR)]),
    MULTI("y20", "The baby said her first word today. It was 'dada'. Her father nearly cried.",
          [B(JOY), B(["tender", "love"] + JOY + SADF)]),
    MULTI("y21", "Ugh, the traffic was horrible. But the biryani at the end was worth it.",
          [B(ANGRY + SADF + TIRED + ["bored"]), B(HAPPY)]),
    MULTI("y22", "I shouted at my son today. He went quiet. I feel terrible about it.",
          [B(ANGRY + ["apologetic"] + SADF), B(SADF + ["apologetic"] + N)]),
    MULTI("y23", "Someone left a basket of fruit at our door. No note. It must be Mrs. Iyer, she's so kind.",
          [B(SURP + HAPPY + N + ["curious"]), B(THANK + HAPPY)]),
    MULTI("y24", "The water tank overflowed again. The whole terrace is flooded. I'm sick of this.",
          [B(ANGRY + WORRY + SADF + N), B(ANGRY + TIRED)]),
    MULTI("y25", "I won the lottery! Wait, no, I misread the number. Never mind.",
          [B(JOY + SURP), B(SADF + SKEP + ["bored", "shy"] + N)]),
    MULTI("y26", "My knee surgery went fine. The physio is painful though. I'm grateful to be walking.",
          [B(CALM + HAPPY), B(SADF + WORRY), B(THANK)]),
    MULTI("y27", "Amma's birthday is tomorrow. I forgot to buy a gift. Oh no.",
          [B(N + HAPPY), B(WORRY + ["apologetic"])]),
    MULTI("y28", "We adopted a kitten! She's tiny and grey. My son can't stop smiling.",
          [B(JOY), B(HAPPY + ["tender", "love"])]),
    MULTI("y29", "The pandit didn't show up for the puja. We were all waiting. Finally Mama-ji did it himself and it was lovely.",
          [B(ANGRY + WORRY + SADF + SKEP), B(HAPPY + CALM + ["tender"])]),
    MULTI("y30", "I'm so tired. The baby has a fever. I don't know what to do.",
          [B(TIRED), B(WORRY + SADF)]),
    MULTI("y31", "My painting got selected for the exhibition! I can't believe it. I've been working on it for a year.",
          [B(JOY + SURP), B(JOY + SURP + ["proud"] + N)]),
    MULTI("y32", "The neighbours are fighting again. I can hear plates breaking. I'm scared for the children.",
          [B(N + WORRY + SADF + ANGRY), B(FEAR + WORRY)]),
    MULTI("y33", "Dada's eyesight is getting worse. He still reads his paper every morning. He's stubborn, and I love him.",
          [B(WORRY + SADF), B(N + ["tender", "love", "content", "grin"]), B(["love", "tender", "happy"])]),
    MULTI("y34", "I thought the parcel was lost. It turned up today! Inside was a letter from my brother.",
          [B(WORRY + SADF), B(JOY + SURP), B(N + ["tender", "happy", "love"])]),
    MULTI("y35", "मी आज खूप थकले. पण मुलांनी जेवण बनवलं. खूप छान वाटलं.",
          [B(TIRED), B(N + HAPPY + ["tender", "proud", "surprised"]), B(HAPPY + THANK)]),
]
