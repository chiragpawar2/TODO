# Verify round 3: homebot face

All numbers below come from runs made in this round (2026-11-23). No file under homebot/ was edited.
New files: `tests/heldout_cases.py`, `tests/run_heldout.py`, `tests/heldout_conversations.py` (it holds the conversations, the runner and the `QueueMind` stub), and `tests/heldout_results.json`.

## 1. Fixer claims

| Claim | Result in this round | Verdict |
|---|---|---|
| expression suite 131/131 expr and level | 131/131, 131/131; multi per-sentence 56/56 | confirmed, but the suite is fitted (see section 2) |
| conversations 289/298 expr, 298/298 level | 289/298, 298/298 | confirmed |
| lip-sync 272/290 | 272/290 (16 seconds_per_word, 2 number_read_as_year) | confirmed |
| glitch jumps 80 -> 2 | 2 (talk_swap_mid_speech 1, idle_layer_swap 1), in 2/100 conversations | confirmed |

**FIXER NOTE edits in `run_conversation_tests.py`.** I diffed it against the original in `scratchpad/base/`. The edits are honest bug fixes:
- The fraction, Indian-grouping and year branches used to append an issue without ever looking at the output. They now inspect `got`.
- The danda is no longer counted as a silent word.

They narrow the year check to "output equals the year reading exactly", which is reasonable. They did not loosen anything else. The checker is still **too weak**, though. The held-out conversations below produce clearly wrong speech that it never flags: decimals inside percentages, phone numbers, dates, and "1.5L".

**StubMind.** The runner's StubMind still drops lines that arrive while the mind is busy. `mind.Mind` now queues them. I wrote `QueueMind` in `tests/heldout_conversations.py`, which queues and pops in order, and ran the original 100 conversations through it:
- 0 lines dropped (the old metric said 3).
- 297 lines asked.
- 1 line still queued at the end: c062 "did you add the tomatoes?". That is a script artefact, because c062 has fewer homebot replies than queued lines.

The "3 dropped" figure in the original runner is therefore stale.

## 2. HELD-OUT accuracy (the real number)

`tests/run_heldout.py`: 120 new single sentences plus 28 new paragraphs. The expectations were written before any run.

- **Expression: 66/120 (55%)**, against 100% on the fitted suite.
- **Level: 117/120 (98%).** This number is inflated: read() says "mid" almost always, and most cases accept mid. The two misses where intense was expected are p12 (terrified, gave mid) and p26 (overjoyed + "!", gave mid).
- **Beats:** 19/28 paragraphs exact and in order (68%); 18/28 with every level right; 47/60 beats right by position.

Expression results by category:

| Category | Right |
|---|---|
| plain | 26/30 |
| negation | 6/10 |
| Hinglish / Marathi (Latin script) | 3/10 |
| Devanagari | 5/10 |
| emoji | 4/8 |
| typos | 2/6 |
| sarcasm | 1/5 |
| substring traps | 3/12 |
| context traps | 1/8 |
| commands | 8/8 |
| aimed at homebot | 5/8 |
| over-trigger probes | 2/5 |

What the failures show:
- **Out-of-vocabulary feeling words fall to attentive.** Examples: thrilled, delicious, pleasant, frustrated, "don't feel well", kharab, maza, sundar, bakwaas (double a), "bara vatla", kantalo, "अच्छा लग".
- **Negation:** "I wouldn't say I'm happy" gives happy. "I can't say I'm excited" gives delight. "never been this happy" gives **sad**, because "never" flips a superlative. "bas kar, irritate mat kar" gives content: "mat" is read as negation of the feeling when it actually negates the command.
- **Context traps:**
  - "nearly died laughing" -> crying
  - "on fire today" -> alarmed
  - "fell in love" -> alarmed
  - "movie was sick" -> worried
  - "dying to see", "to die for", "killing it" -> attentive
- **Substring and word-sense traps:**
  - Thakur -> drowsy (`thak*`)
  - "bus stop" -> stern
  - "passed the salt" -> delight
  - "fire up the oven" -> alarmed
  - "bhari" (heavy, in Hindi) -> delight
  - "battery dies" -> crying
  - thinkpad -> thinking
  - "bang on time" -> startled
  - "far cry" -> crying
- **Devanagari prefix matching is a real false-positive source.** These come from direct probes:

  | Word | Prefix matched | Read as |
  |---|---|---|
  | रोटी, रोज़, रोहित, रोमांचक | रो | crying |
  | चिड़िया | चिड | angry |
  | झोपड़ी | झोप | drowsy |
  | डरबन | डर | worried |
  | प्रेमचंद | प्रेम | love |
  | मस्तक | मस्त | happy |
  | माफ़िया | माफ | apologetic |
  | बुराड़ी | बुरा | sad |
  | आनंद (a name) | आनंद | happy |

- **Emoji:**
  - Unknown emoji are ignored: 😤, 💀, 😬, 🤦, 😋.
  - The emoji weight (2.0) outranks clear words: "I got the job!! 😭😭" -> crying/intense, "terrible news 🙂" -> happy, "great 😭" -> crying, "I am happy 😢" -> sad.
  - The happy-tears rule only fires on the word "crying", never on 😭.
- **"!" alone gives delight on bad news:**
  - "Grandpa is in the ICU!", "I lost my wallet!", "I lost my job!" and "Your mom called!" (a neutral line) all -> delight.
  - "my exam is tomorrow!" -> delight.
  - Paragraph mm17 "...guests arrive in ten minutes!" -> delight.
- **Sarcasm:** only the "praise + again + household noun" form is caught. "great, just great. The milk went off." -> happy. "thanks a lot for nothing" -> tender. "love that for me, stuck in traffic" and "because that always works" -> attentive.
- **Typos are only caught from a fixed list:** exhuasted, thankyou, amazng, scarred.
- **Lines aimed at homebot:** "you never listen to me" and "I like talking to you" -> attentive. "shut up homebot" -> angry; homebot glares back instead of looking hurt.
- **Beat failures:**
  - A neutral middle sentence hides the feeling: mm08 "My cat is missing..." gives one attentive beat; mm18 "Nobody remembered my birthday" gives attentive.
  - Unknown words: mm14 sunny, mm15 "she'll be fine", mm22 "दूर रहूँगा".
  - Strong beats are lost: mm06 "broke my laptop" (2nd beat attentive), mm21 "doesn't sound right".
  - Sentence splitting only happens on punctuation followed by a space. A "but" inside one sentence does not split.

## 3. New conversations

`tests/heldout_conversations.py` holds 30 conversations: 44 user turns and 43 replies.

**Behaviour that works:**
- User turns: 43/44 expressions right, 41/44 levels right. The level misses are "and garlic" low, "stop" low and "actually continue" low, all minor.
- The read-face hold is visible, roughly 0.7 s before "thinking" takes over.
- Mouthless poses (tender, alarmed, attentive, drowsy) still show a mouth while speaking: `mouth_alpha_min` 0.33, 0 voiced-but-mouthless frames.
- Interruptions h11, h12 and h25 fade with 0 glitch jumps.
- Queued lines h09 and h10 were answered in order in the simulation.
- Refused/apologetic relaxes to rest after about 9 s (h18).
- Sleep and wake work: h13 ("good night" -> asleep -> 90 s quiet -> waking -> listening), h14 (dozes at 75 s, wakes on input), h30 ends asleep.
- 0 sanity violations, 0 glitch jumps.
- update(): p50 29 us, p99 97 us, max 638 us.

**Lip-sync.** The checker calls 34/43 replies clean, which is far too generous. By my reading, these are wrong:

| Reply text | Spoken as | Problem |
|---|---|---|
| `7.25%`, `7.5%`, `9.2%`, `12.5%` | "seven twenty five percent", "seven five percent" | the decimal point is lost before %. **Severe: it changes the number** |
| `98765 43210` | "ninety eight thousand seven hundred sixty five forty three thousand…" | a phone number with a space is read as two numbers |
| `410210` (PIN code) | four hundred ten thousand two hundred ten | should be read digit by digit |
| `23/11/2026` | "twenty three slash eleven slash two thousand twenty six" | date |
| `14/02` | "fourteen by two" | date |
| `1.5L` (loan) | "one point five **litres**" | should be lakh in a money sentence |
| `21:00` | "twenty one oh clock" | 24-hour time |
| `1 tsp` | "one teaspoons" | plural after one |
| `1203` (flat number) | "twelve oh three" | the checker flags this; borderline |
| `७:१५` in a Marathi sentence | "seven fifteen" | English digits inside Marathi; the checker flags it as silent, which is arguably a false flag |

These were right: `₹1,249.75`, `₹8,432.50`, `18:45`, `05:30`, 5th/2nd, `3.4 km`, `10-12`, `2.5 mg`, `1/2`, `46.3`, `1800-425-3800`, `8am`/`9:30pm`.

## 4. New problems and regressions

1. **Queued replies talk over each other (real Mind). High impact.** With the real `Mind` and `OfflineMind`, I submitted 3 lines back to back. All 3 replies' speak() calls fired within 2 ms. Each call hushes the previous one (`_fading` length 1, then 2), so only the last reply is heard.
   - The queue fixed the drop, but now it silently swallows the speech.
   - `_on_reply` also runs on the brain thread and mutates the Animator, which is a race.
   - The scripted runner cannot see this, because it plays replies one after another.
   - Fix: in `_on_reply`, if `anim.speaking`, add the reply to a speech queue that update/_idle_check drains, and marshal it onto the UI thread.
2. **The ~1.5–2 ms update() spikes are the Python garbage collector, not face code.**
   - With gc enabled, 5 of 43,145 frames were over 400 us, and one of them coincided with a gc start.
   - With `gc.disable()`, the same 40 conversations gave p99 76 us, max 277 us, and 0 frames over 500 us.
   - `_begin` costs 16 us, or 37 us with intensity, so it is not the cause.
   - Fix: `gc.freeze()` after startup and/or `gc.collect()` in idle frames.
3. **The read face lingers into the reply.** 31/290 replies start on the read face (original suite: answering 259 of 290). The reply arrives inside `reaction_until` (up to 3.5 s for paragraphs), so speech starts on the read face and "answering" is applied mid-speech. This looks acceptable, but it is the user's call (section 6).
4. **Over-triggering.** "!" gives delight on bad news, and emoji at weight 2.0 outrank clear words. Examples are in section 2.
5. **Devanagari prefix false positives.** Examples are in section 2.
6. **OfflineMind uses substring greetings.** "and chillies" contains "hi", so it got the "Hello…" greeting reply. This is in `mind.py`.
7. **read() timing on held-out text:** mean 20.5 us, max 131 us. No problem.

## 5. New gaps ranked by impact, with one-line fixes

1. **Queued replies cut each other off.** Add a speech queue in app/animator and drain it when the current utterance finishes.
2. **Decimal percentages lose the point** (7.25% -> "seven twenty five"). In pronounce, handle `\d+\.\d+%` before the % rule.
3. **"!" means delight on bad news.** Only apply the "!" fallback when no negative cue is present (lost, ICU, cancelled, hospital), or fall back to surprised instead.
4. **Devanagari prefix matching.** Require a minimum stem length of 3 or more letters plus an explicit inflection whitelist (खुश→खुशी, थक→थकलो). Drop the bare रो, चिड, डर, झोप prefixes in favour of exact forms (रो रहा, रडू).
5. **Emoji outrank words.** Lower the emoji weight to about 1.2 when an explicit feeling word is present. Treat 😭 next to joy words as happy tears. Add 😤 💀 😬 🤦 😋.
6. **Out-of-vocabulary feeling words.** Add a broad lexicon: thrilled, delicious, pleasant, frustrated, unwell, kharab, maza, sundar, bakwaas, bara, kantala, अच्छा लग. Better still, consider a small sentiment fallback for lines that would otherwise be neutral.
7. **Idioms and context.** Add the phrases "died laughing", "on fire", "fell in love", "to die for", "dying to", "killing it", "was sick" (as praise), "passed the", "bus stop", "fire up", "far cry", "bang on". Add Thakur and Anand to a names list.
8. **Phone numbers, PIN codes and dates.** Read 10-digit, `5+5` and 6-digit tokens digit by digit. Read dd/mm(/yyyy) as a date. Read hh:00 in 24-hour form as "twenty-one hundred". Read "1.5L" as lakh when ₹/loan/price appears nearby.
9. **Negation.** "wouldn't/can't say" should hedge the feeling (skeptical/neutral). A "never ... this X" superlative should not flip. "mat" should negate only the following verb, not the feeling.
10. **Sarcasm.** Add the forms "just great", "thanks a lot for nothing", "love that for me", "because that always works".
11. **Beats.** A neutral beat between two emotional ones should keep the paragraph's feeling. Also split sentences on "but"/"पर".
12. **"shut up homebot" -> hurt, not angry.** Add it to the `_TO_BOT_INSULT` patterns. Add "you never listen" (hurt) and "I like talking to you" (pleased).
13. **The checker misses most of the lip-sync errors above.** Add reference expansions for %, phone numbers, PIN codes and dates.

## 6. Needs the user's decision

- Should the read face be held into the start of the reply (current behaviour, 31/290 replies), or should the reply always start on "answering"?
- For a 24-hour time such as 21:00, say "nine pm" or "twenty-one hundred"? And should Marathi/Hindi replies read digits in Marathi/Hindi or in English?
- "!" with no other cue: delight, surprised, or neutral?
- Is a lexicon-only reader acceptable at 55% held-out accuracy, or should a small local sentiment model be the fallback for neutral results?
- Should queued replies all be spoken, or should only the latest be spoken, with the earlier ones shown as captions?
