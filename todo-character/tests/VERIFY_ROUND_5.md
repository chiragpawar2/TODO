# Verify round 5: homebot face (blind-2 set)

All numbers come from runs made in this round (2026-11-23). No file under `homebot/` was edited. Re-running the old suites regenerated their own result files (`expression_results.json`, `heldout_results.json`, `blind_results.json`), because each runner writes its file on every run. No case file was changed.

New files:
- `tests/blind2_cases.py`: 204 single lines and 35 paragraphs. Expectations were fixed before the first run and not changed afterwards.
- `tests/run_blind2.py`: runs the set twice, once with rules only (`read(model=False)`) and once with the full reader (`read()`, rules plus the GoEmotions fallback). It also reports overlap with earlier sources.
- `tests/blind2_conversations.py`: 20 conversations with QueueMind, a short-reply timing check, and two interruption tests.

## 1. Fixer claims re-run

| Suite | Fixer claim | This round | Verdict |
|---|---|---|---|
| expression `--no-anim` | 131/131 | 131/131 expr, 131/131 level, multi 25/25 | confirmed (fitted) |
| conversations | – | **289/298 expr**, 298/298 level, lip-sync 284/290 clean | round 4 was 288, so +1 |
| held-out | – | 118/120 expr; paragraphs 22/28 exact | fitted |
| old blind | 157/159 | **157/159** (98.7%); paragraphs 16/30 exact, 22/30 with merges | number confirmed, but **contaminated** |
| held-out conversations | – | 42/44 expr, lip-sync 39/43 | ok |
| blind conversations (round 4) | – | 30/32 expr, 31/32 lip-sync clean, 0 glitches | unchanged misses (z17, z21) |
| blind_inbox | – | A, B and C all (0,0,0); 0 stale replies after an interrupt | the round-4 queue bug is **fixed** |

The old blind set went from 118/159 to 157/159. Its phrases were quoted to the fixer, so that number now only measures fitting.

## 2. BLIND-2 accuracy (the honest number)

**Overlap check.** 73 of 239 cases share a 4-word run with an earlier test file or `.md`, or contain a multi-word string from `lexicon.py`.
- Most of these are generic runs such as "i m so proud".
- Some are real lexicon hits despite my effort to avoid them: "on pins and needles", "blood is boiling", "running on fumes", "the last straw", "in a pickle", "got rejected", "dil bhar aaya".
- One line, x066 "pet mein chuhe daud rahe hain", is an accidental paraphrase of old b092.

The CLEAN subset excludes all 73. That makes it the stricter number, because the excluded lines are the ones the lexicon already covers.

| | rules only | **full read()** |
|---|---|---|
| Single lines, all 204 | 146/204 = 71.6% | **155/204 = 76.0%** |
| **Single lines, CLEAN (150)** | 96/150 = 64.0% | **105/150 = 70.0%** |
| Emotional lines only (158) | 66.5% | 72.2% |
| Level | 202/204 | 202/204 (uninformative: 193/204 lines got "mid", only 3 got "intense") |
| Misses that are silence (`why=None`) | 39/58 | 28/49 |
| Paragraphs, exact | 11/35 (31%) | **13/35 (37%)** |
| Paragraphs, merges allowed | 12/35 | 15/35 (43%) |
| Paragraphs, beats right by position | 51/78 (65%) | 58/78 (74%) |
| Paragraphs, CLEAN exact | 4/16 | 5/16 |

About 4 of the paragraph "fails" are splits inside the same feeling family: y04 delight then proud, y07 sad then crying, y19 worried then dread, y31. A family-level check would score paragraphs about 10 points higher.

**Over-trigger on neutral, command and name lines: 5/46 = 10.9%.**
- On the 28 neutral lines alone it is 4/28 (14%):
  - "hospital canteen opens at seven" -> worried
  - "funeral home is next to the post office" -> crying
  - "the crying baby emoji is in the second row" -> crying
  - "the broken chair is in the store room" -> fret
- Names: "Aanandi needs a lift" -> happy, because the lexicon matches "aanand" inside the name.
- Commands: 8/8 neutral. Names: 9/10.
- The lexicon grew about 4x, but over-trigger stayed contained. Commands, "the cat is sleeping", "killed the lights" and "we are out of sugar" were all fine.

**Against the previous honest numbers (55% -> 72.5% -> 81.2%):** blind-2 CLEAN is **70.0%** with the model and 64.0% with rules only. The comparable "all lines" figure is 76.0%. **There is no real gain on fresh text in this round.** The 874 Hindi/Marathi entries, about 1090 idioms and 419 events moved the contaminated set from 74% to 98.7%, while fresh text sits around 70 to 76%.

**Expression by category (full read()):**

| Category | Right | Category | Right |
|---|---|---|---|
| command | 8/8 | names | 9/10 |
| negation | 11/12 | plain | 22/24 |
| devanagari | 8/9 | emoji | 7/8 |
| to_bot | 7/8 | context | 8/10 |
| hinglish | 11/14 | idiom | 11/15 |
| typo | 6/8 | kids | 7/10 |
| grand | 4/6 | marathi | **4/8** |
| event | **5/12** | parents | **2/8** |
| sarcasm | **1/6** | | |

**Typical misses:**
- **Silence (no cue found):**
  - Events: "debt free", "driving licence", "gold star", "first paying customer", "laying people off", "towed", "landlord wants us out", "slipped in the bathroom", "kept us up all night", "hip is acting up", "nobody visits me".
  - Idioms: "ruffled my feathers", "sleep for a week", "million bucks", "heart is in my mouth".
  - Typos: frustared, exaused.
  - Marathi: dokyala tap, kantaalun, "tula kiti vela sangitla".
  - Devanagari: मन भारी.
- **Wrong trigger:**
  - Sarcasm, 5/6 wrong: "oh joy", "yay, more homework", "bahut badhiya, phir se", "terrific … again" -> delight, and "awesome, the wifi died" -> fret.
  - "maza mood kharab aahe" -> delight. The Marathi "maza" (= my) is read as the Hindi "maza" (= fun).
  - "couldn't be more pleased" -> sad, read as "not pleased".
  - "so bored I could cry" -> crying.
  - "tummy feels funny" -> grin.
  - "scary movie night" -> worried.
  - "I'd hate to miss your recital" -> angry.
  - "biopsy came back benign" -> worried.
  - "I missed you today, robot" -> sad (model).
- **Paragraphs:**
  - "!" plus no cue -> delight even on bad news: y17 "The puppy chewed my new shoes!"
  - "My son can't stop smiling" -> sad (negation).
  - "I have to move … the kids will hate it" -> angry.
  - Unknown first sentences fall to attentive (y03, y06, y13, y22).

**Timing:**
- `read(model=False)`: mean 72.7 us, p99 227 us, max 492 us. That is about 3x round 4's 25 us, but still fine.
- `read()` with the model: mean 32 ms, p50 162 us, p99 135 ms, max 358 ms. It must stay off the UI thread, which is what the app does.

## 3. Conversations (blind2_conversations.py)

- **User turns: 19/25 expr, 25/25 level.** 0 glitch jumps, 0 sanity violations.
- **Lip-sync: 25/25 replies clean.** Queued pairs were answered in order (w09, w10, w14, w18, w19).
- update(): p50 29 us, p99 88 us.
- **Misses:**
  - "I'm going to bed now" and "good night robot" -> **asleep**. The face falls asleep at the user's own announcement, before homebot has replied.
  - "the school bus left without Riya again" -> attentive.
  - "there's someone knocking at 2 am" -> attentive.
  - "oh joy, the in-laws…" -> delight.
  - "maybe later" -> skeptical.
- **Short replies, seconds per word:**
  - Okay. 0.72
  - Yes. 0.50
  - Hmm. 0.32
  - "Good night. Sleep well." 0.53
  - Anytime. 0.70
  - "Okay, stopped." 0.74
  - "Thank you!" 0.42
  - "I'm here." 0.32
  - All are within the 0.15-0.9 band.
- **Interruption:**
  - Two replies were queued when the user interrupted. **0 stale replies were played**, and the answer to the new line was spoken.
  - **New bug:** a reply to the OLD question that reaches the inbox *after* the interrupt is still spoken ("The second one is at six forty…" played after "no, tell me about buses"). Clearing `_speech` does not cover replies that are still in flight.

## 4. The four flagged shifts

| Line | Now | Verdict |
|---|---|---|
| "Kahi harkat nahi" (a homebot reply meaning "no problem") | content | **Accept.** A calm reassurance is right. |
| "बहुत अच्छा दादी" (a homebot reply praising Dadi) | happy | **Accept.** |
| "Rahul got fired" | sad | **Accept with a bug.** Job loss as sad is right. But "Rahul got fired up about the match" and "got fired from the cannon at the circus" also give sad. Exclude "fired up" and "fired from a/the cannon/gun". |
| "recovered" | content | **Mostly accept.** Health recovery is right, and "recovered the deleted photos" being content is harmless. But "she recovered from covid but is still weak" gives content, because the "but" clause is ignored within `read()`. |

## 5. Regressions

- No accuracy regressions on any existing suite. Conversations went 288 -> 289, and inbox case C is now fixed.
- `read(model=False)` mean went from 25 us to 73 us (about 3x), from the bigger lexicon. Not a problem in practice.
- `update()` max in the full conversation suite is 11 ms, and 13.6 ms in the held-out conversations; round 4 was about 0.5 ms. This is probably model or GC noise in the test process, but it is worth a look.
- **New errors caused by the lexicon:**
  - "maza" (Marathi "my") -> delight.
  - "Aanandi" -> happy.
  - "funeral" / "crying" / "broken" / "hospital" used as plain nouns now fire on neutral lines.

## 6. Remaining gaps, ranked (one-line fixes)

1. **Sarcasm, 1/6.** Praise word, then a comma, then a bad-event clause ("more homework", "died", "phir se", "again", "curdled") -> skeptical. Generalise the pattern instead of listing phrases.
2. **A stale reply arrives after the interrupt.** Tag each reply with a turn id from `_submit`, and drop any `_on_reply` whose id is older than the current turn.
3. **Parents, events and grandparents fall silent (11/26).** No word list will close this. Let the model also handle "event-shaped" English lines (all English lines with no cue already reach it) and lower THRESHOLD to about 0.35. Its lift was only 9 lines here.
4. **The face falls asleep on "going to bed" / "good night".** Map these to drowsy or tender, and let sleep follow homebot's own good-night reply.
5. **Nouns firing on neutral lines.** Do not score "funeral", "hospital", "broken" or "crying" when they are noun modifiers in a locative or descriptive frame ("X is next to / in / on"). Add "aanand-" names to the names list.
6. **Marathi "maza" / "majha" (= my).** When a Marathi marker (aahe, mala, khup) is present, treat "maza" as a possessive, not as fun.
7. **"couldn't be more X"** -> intensify X, do not negate it. **"could cry" / "feels funny" / "I'd hate to miss"** need small context rules.
8. **Level.** 95% of lines are "mid". Only caps lock and "!!!" ever reach "intense"; "terrified" and "petrified" should reach it on their own.
9. **Paragraph "!" with no cue -> delight.** Inherit the next beat's feeling instead, or stay neutral.

## 7. Verdict

**More lexicon rounds are not worth it.**
- Round 5 added about 3400 entries.
- The contaminated set went from 74% to 98.7%.
- Fresh text stayed flat: 70% CLEAN and 76% overall, against 72.5% and 74% in round 4, and below the 81.2% quoted before.
- Each round fits whatever set it is shown.
- Over-trigger is still acceptable at 11%, but it is starting to grow (funeral, crying, broken, hospital, Aanandi, maza).

**Worth one more round, as targeted rule fixes:** items 1, 2, 4, 5 and 6 above. These are bugs, not vocabulary.

**For the open-ended vocabulary** (events, idioms, Marathi): the remaining lever is the model path. That means a better or multilingual classifier, or a lower threshold, tested on a fresh blind set **written after** the change. Do not tune it on this one.
