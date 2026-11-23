# Verify round 4: homebot face (blind set)

Every number here comes from a run made in this round (2026-11-23). No file under `homebot/` was edited, and no existing case file was changed.

New files:
- `tests/blind_cases.py`: 159 single lines and 30 paragraphs. Expectations were fixed before any run.
- `tests/run_blind.py`: the runner. It also checks for overlap with earlier phrase sources.
- `tests/blind_results.json`: the raw results.
- `tests/blind_conversations.py`: 25 conversations, run through the QueueMind machinery.
- `tests/blind_inbox.py`: threaded inbox and speech-queue tests.

## 1. Fixer claims re-run

| Suite | Fixer / round 3 | This round | Verdict |
|---|---|---|---|
| expression suite | 131/131 | 131/131 expr+level; 0/25 substring FPs; 20/20 shadow | confirmed (fitted) |
| held-out (round 3) | 117/120 | **117/120 expr, 119/120 level**; paragraphs 17/28 exact, 46/60 positional | confirmed, but **contaminated** |
| conversations | 289/298 | **288/298 expr**, 298/298 level; lip-sync 272/290; 2 glitch jumps in 2/100 conversations | **-1 regression** (section 5) |
| held-out conversations | - | user turns 41/44 expr, 41/44 level; replies 34/43 checker-clean; 0 glitches | unchanged |

## 2. BLIND accuracy (the honest number)

`run_blind.py` matches earlier phrase sources (heldout, expression, conversations, and quotes in VERIFY_ROUND_3) for exact or contained runs of 3 or more words.
- It found **10 single lines and 1 paragraph** I had written that collide, for example "not bad at all", "I don't hate it" and "you're so cute".
- The kids' line "a tree!" was suggested in the brief, but it is also in `conversations.py` c084. The check missed it because it is only 2 words.
- The clean number below excludes all of these.

| | Result |
|---|---|
| **Expression, clean subset** | **108/149 = 72.5%** |
| Expression, all 159 | 118/159 = 74.2% |
| Expression, emotional lines only | 86/123 = 70% |
| Expression, neutral / command lines | 17/21 |
| Level | 156/159 (98.1%). This is uninformative: 143/159 lines got "mid". Lines expecting only low or intense: 8/9 |
| Paragraphs, beats exact and in order | **13/30 (43%)**; 15/30 allowing merges; 13/29 on the clean subset |
| Paragraphs, beats right by position | 48/69 (70%) |
| `read()` timing | mean 25.4 us, max 90.2 us |

**Against the previous blind baseline:**
- Round 3 blind was 66/120 (55%). This round is **72.5%**, so about +17 points of real improvement.
- The same reader scores 98% on the held-out set it was fixed against. A **~25-point gap** is the fitting.
- Paragraph exact accuracy went **down**: 68% on round 3 held-out versus 43% here.

**Expression by category:**

| Category | Right | Category | Right |
|---|---|---|---|
| plain | 23/24 | devanagari | 12/12 |
| emoji | 10/10 | command | 8/8 |
| marathi | 7/8 | hinglish | 11/14 |
| negation | 9/12 | to_bot | 5/6 |
| kids | 5/8 | context | 6/10 |
| names | 6/10 | typo | 4/7 |
| idiom | 8/15 | family | **3/10** |
| sarcasm | **1/5** | | |

**What the 41 misses are.** 30/41 are silence: `why=None`, so the line falls to attentive. 11/41 are a wrong trigger.

- **Silence (no cue found):**
  - Unlisted words: "can't stop sobbing", "knee is hurting", "heavenly", "first steps", "fighting again".
  - Idioms:
    - down in the dumps
    - wits' end
    - heart sank
    - walking on air
    - gets on my nerves
    - dil garden garden
    - naak mein dum
    - a breeze
    - crazy talented
    - killing me
    - plant is dying
  - Regional words: khooshi, bindaas, pagal, "khup raag", "accha nahi lag raha", "nahi aavadla".
  - Typos: hapyy, tird, angy.
  - Others: "it isn't funny", "I don't want to go to school", "my balloon popped", "you got it wrong again".
- **Wrong trigger:**
  - Names: "call Sukhi aunty" -> happy, "is Joy coming" -> delight, "Happy Valley" -> happy, "Prem bhaiya" -> love.
  - Sarcasm:
    - "fantastic, another parking ticket" -> delight
    - "wow, so helpful, thanks" -> tender
    - "kya baat hai, phir se late" -> delight
  - "Papa is coming home from the hospital" -> worried.
  - "I lost my tooth!" -> fret.
  - "my son didn't call on my birthday" -> skeptical ("hedged birthday").
  - "scored full marks!" -> surprised ("!").
- **Paragraph failures:**
  - "!" now gives surprised on bad news: "Someone stole my cycle!" and "flight is in three hours!".
  - Neutral or unknown middle sentences: mb02, mb06, mb19.
  - "Pan aata bara vatat ahe" -> attentive.
  - "He proposed! I said yes! I'm still shaking." -> surprised, worried.
  - "Please don't be angry" -> content, because the negation is read as reassurance.
  - "The neighbour's music is too loud" -> startled.

## 3. Conversations and the threaded inbox

**`blind_conversations.py`** (25 conversations, QueueMind):
- User turns: 30/32 expr, 32/32 level. The misses are "shubh ratri homebot" -> attentive, and "how do I make chai for 4" -> thinking.
- Queued lines were asked in order: z13 had 3 lines, 0 were left in the queue.
- 0 glitch jumps, 0 sanity violations.
- update(): p50 29 us, p99 43 us, max 547 us.
- "you're absolutely useless today" -> angry: homebot glares back again. I accepted this as a pass, but it is the hurt-versus-glare question from round 3.

**`blind_inbox.py`:**
- **A. Real background thread, 3 replies about 2 ms apart, fake UI clock.**
  - All 3 were spoken in full and in order.
  - Gaps between them were 0.03 s and 0.022 s, with 0 overlapping starts and 0 cut short.
  - **0 Animator calls off the UI thread.** I wrapped speak, hush, set, flash, play, play_steps and stop_sequence to check this.
- **B. Real `mind.Mind` (offline backend), real clock, 3 lines submitted back to back.** 3 replies, in order, gaps 0.039 s and 0.046 s, 0 overlap, 0 off-thread calls. The round-3 talk-over bug is **fixed**.
- **C. Interruption while 2 replies are queued.**
  - `_submit` hushes the current reply but does **not clear `_speech`**.
  - The next stale reply starts **0.02 s after the user interrupts**, and both queued replies are then spoken over the user's new line.
  - **New high-impact bug.**

## 4. Lip-sync on new number formats

I ran `pronounce.normalise` directly on 46 formats. **21 right, 4 partial, 21 wrong.**

**Right:**
- 3rd Dec
- 21st March
- 2,50,000 -> "two lakh fifty thousand"
- ₹99.99
- 100+
- ₹5k
- 10 lakh
- ₹1.2 crore
- 12/12/2025
- 10K
- 1.5kg
- 100ml
- 2-3 days
- #5
- 9 a.m.
- B-12
- "₹ 500"
- Devanagari text with digits: "३ बजे" and "सुबह 7:30 बजे" (the digits are read in English)
- "+91 98220 12345" when nothing follows it

**Severe: these change the meaning.**

| Input | Spoken as | Problem |
|---|---|---|
| `-4°C` | "4°C" | the minus is dropped |
| `-4 degrees` | "four degrees" | the minus is dropped |
| `₹99.99/month` | "rupees ninety nine **ninety nine** slash month" | the decimal is lost |
| `call +91 98220 12345, now` (a phone number followed by a comma) | "plus ninety one ninety eight thousand two hundred twenty twelve thousand…" | phone joining fails. Real replies hit this, for example z24 |

**Wrong:**
- `Q3`, `Q4 FY25`: left as is
- `5'10"`, `6ft`: left as is; "5 ft 10 in" becomes "five ft ten in"
- `x2`, `2x`, `3x faster`, `24x7`: left as is
- `1st/2nd` -> "one st slash two nd"
- `3/4th` -> "three slash four th"
- Roman numerals in names (George V, Louis XIV, Henry VIII, Chapter IV): left as letters
- `₹2,500/-` -> "rupees 2,500/"; `500/-` -> "500/"
- `4.5★`, `1990s`, `'90s`: left as is
- `Dr.` and `No.`: become "doctor ." and "No .", which inserts a sentence stop

**Partial:**
- `50km/h` -> "fifty km slash h"
- `10:00-13:30` -> "ten oh clock one thirty pee em": the "to" is dropped
- `50%-60%`: the "to" is dropped

**The checker is still blind to many of these.** In the conversations it reported 24/32 replies clean, but z09 ("one st slash two nd"), z10 (roman numerals) and z24 (the phone number, "Dr.", and the time range) are among the "clean" ones.

## 5. Regressions

- **Conversations: 289 -> 288.** The "!" fallback changed from delight to **surprised**. That broke excited kids' lines (c078 "T-rex!!", c084 "a truck!") and c098 "bus is coming in 2 minutes!!", which got surprised where worried was expected.
- It also misreads blind bad news ending in "!" as surprised: "stole my cycle!" and "flight is in three hours!".
- Surprised is better than delight on bad news. It is still wrong for clear joy or clear alarm.
- No timing regressions: read() mean 25 us; update() p99 41-43 us.

## 6. Remaining gaps, ranked by impact (one-line fixes)

1. **A stale queue resumes over the user's interruption.** In `app._submit`, `self._speech.clear()` (and drain the inbox's replies) when the user speaks.
2. **Numbers that change meaning.**
   - Keep a leading `-` before a digit as "minus".
   - Handle `\d+\.\d+/` before splitting on the slash.
   - Let phone joining tolerate trailing punctuation (`[,.;]`).
3. **Silence on unseen feeling language: 30/41 blind misses, 73%.** When `read()` finds no cue (`why is None`), fall back to a small local sentiment model (see the verdict).
4. **Names read as feelings: 4/10.** Do not score a capitalised token mid-sentence, or one after call/to/is/with, and keep a household names list (Sukhi, Joy, Prem, Happy Valley).
5. **Sarcasm: 1/5.** A praise word followed by a negative-event noun (ticket, late, power, again) should become skeptical. Add "so helpful" and "kya baat hai … phir se".
6. **"!" fallback.** Use surprised only when there is no other cue. When there is a loss, theft or deadline cue, prefer worried. Let delight win for a bare noun exclamation from a child ("a truck!").
7. **Paragraph beats: 43% exact.** Carry the previous beat through neutral middle sentences. Treat "please don't be X" as a plea, not as reassurance.
8. **Unexpanded tokens:**
   - Qn becomes "Q three".
   - xN or Nx becomes "times N" / "N times"; 24x7 becomes "twenty four seven".
   - Ordinals joined by a slash.
   - Roman numerals after a capitalised name.
   - ft/in, and `/-`.
   - Decades ("1990s").
   - "Dr." and "No." should not end a sentence.
9. **The lip-sync checker should flag any letter+digit token that is left in the output, and ordinal suffixes split off from their number.**
10. Small items: "shubh ratri" should be read as good night, and "you're useless" should get hurt rather than angry.

## 7. Verdict

**The rule-based reader is not good enough on unseen text alone, but it should stay as the first stage.**

Evidence:
- **Blind accuracy is 72.5%**, against 98% on the set it was tuned on. Each fix round adds about 17 points on new text, while the fitted sets sit near 100%. That is the signature of a lexicon chasing its test sets.
- **73% of the remaining misses are silence, not wrong rules.** The line has a feeling, the reader found no listed word, and it gave attentive. English and Hindi idioms, regional words and typos are open-ended, so adding to the list will not converge.
- **What the rules do well is not something a model does well.** They score 100% on Devanagari, emoji and commands, 23/24 on plain lines, at 25 us, and they are inspectable. A sentiment model would also add new errors on names and commands.
- The wrong-trigger errors (names, sarcasm, "!") are **rule bugs** that rules can fix.

**Recommendation:**
- Keep `read()` and add a **small local multilingual sentiment or emotion model as a fallback, used only when `why is None`**.
- Map it to valence, then to a family at "mid".
- Gate adoption on this blind set: the fallback must lift the 30 silence misses without breaking the 17/21 neutral lines.

I did **not** test a model in this round, so the size of that lift is a projection, not a measurement.

## 8. Needs the user's decision

- Should queued replies be dropped when the user interrupts? I recommend yes.
- "!" with no cue: surprised (current), delight, or neutral?
- Is a fallback sentiment model acceptable on the Pi, given its RAM and startup cost?
