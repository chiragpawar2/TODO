# homebot face: where `reading.read()` gets it wrong

Every number here comes from `PYTHONPATH=. .venv/bin/python tests/run_expression_tests.py`
(raw data in `tests/expression_results.json`). I wrote the expectations in
`tests/expression_cases.py` as a human reader before running anything, and did not change them after.
Use `--no-anim` to skip the Animator level checks. Those checks took 39 min of wall
time but only 4.6 s of CPU, because `time.sleep(0.02)` was throttled in a background process.

## 1. Headline numbers

| | result |
|---|---|
| Labelled cases | **156**: 131 single, 25 multi-emotion paragraphs (56 beats) |
| Single cases, expression correct | **68/131 (52%)** |
| Single cases, level correct | **123/131 (94%)** |
| Both correct | 64/131 |
| Multi-emotion, `read()` on the whole paragraph | **23/56 beats (41%)**. Never more than 1 beat per paragraph. 2/25 paragraphs got no beat at all |
| Multi-emotion, `read()` on each sentence | **40/56 beats (71%)**. All beats captured in 12/25 paragraphs. Level right on 39/40 of the captured beats |
| Expressions reachable from text | **29/43**. 14 can never be reached |
| Substring probes (26 extra household sentences, 1 control) | **25/25 false positives** |
| Shadow probes (an earlier family's keyword co-occurs with the real emotion) | 10/20 right |
| Level probes (pairs differing only by a misread substring) | **9/10 pairs got different levels** |
| Speed | 12.3 µs per call on average (31,200 calls). 43 µs for the longest input (258 chars) |
| Structural rules (mouthless stays mouthless, hidden pupils stay hidden) | **0 violations** across 43 poses × 3 levels × 12 settled frames |

By category (expression / level): plain 23/26, 25/26 · strength 12/12, 11/12 · single_word 7/9, 9/9 ·
command 7/8, 7/8 · edge 5/7, 7/7 · substring **4/22**, 22/22 · hinglish **4/12**, 12/12 ·
devanagari **0/6**, 6/6 · emoji **2/6**, 3/6 · typo 2/6, 5/6 · negation **0/7**, 6/7 ·
sarcasm **0/4**, 4/4 · to_bot 2/6, 6/6.

The default face `attentive` was the output for 43/131 single cases (33%).

## 2. Failures by root cause (63 single-case expression failures, one primary cause each)

### A. Substring and word-sense false positives: 21 cases (+25/25 probes). Severity: HIGH
Keywords are matched as bare substrings, so a keyword fires inside other words and in other senses.
The wrong face lands on neutral household speech, and often it is a *strong* wrong face (dread, crying, angry).
- In-word matches (15): `"The Diwali fireworks were beautiful"` → dread ('fire'); `"I'm unhappy with the new maid"` → **happy** ('happy');
  `"Whatever you think is fine"` → angry ('hate'); `"I'm reading about the crusades"` → sad; `"The census officer came today"` → suspicious ('sus');
  `"I bought a lollipop for Riya"` → grin ('lol'); `"I'm displeased with the result"` → happy; `"I'm so uncomfortable in this heat"` → content;
  `"abhi nahi, baad mein"` → listening ('hi ', inside the Hindi words abhi/nahi).
- Wrong sense (6): `"My phone battery died"` → crying; `"Good enough, let's go"` → stern; `"He was crying with laughter"` → crying;
  `"Do not forget to buy onions"` → stern; `"That's the worst-case scenario, let's plan for it"` → angry.
- Probes (all 25 non-control probes were false positives): `"I studied all night for the exam"` → crying ('died');
  `"My father retired last year"` → drowsy; `"Can you help me with my homework"` → **dread** ('help me');
  `"Rahul got fired from his job"` → dread; `"Please take out the rubbish"` → angry; `"Mehndi function is tomorrow at 5"` / `"Mehta uncle is coming over"` → bored ('meh');
  `"Bring the prasad from the temple"` → sad; `"They said the bus is late"` → listening ('hey'); `"Do we have enough rice for tonight"` → stern;
  `"Take care of the electricity bill"` → tender; `"Happy Thanksgiving to the cousins in the US"` → tender (the 'thanks' family comes before happy).
  Indian names and words are hit especially often: Mehta, Sadashiv, prasad, Delhi, abhi/nahi/bhi/kabhi/yahi.

### B. No Hindi/Marathi: 12 cases (14 including the two 'hi ' substring hits in A). Severity: HIGH for this household
Every romanised Hindi/Marathi emotion and every Devanagari input falls back to `attentive`:
`"bahut khush hoon aaj"` → attentive/mid; `"mujhe bahut gussa aa raha hai"` → attentive; `"mi khup thaklo aahe"` → attentive;
`"मी खूप खुश आहे"` → attentive/mid; `"मुझे दुख है"` → attentive; `"धन्यवाद"` → attentive/low.
The only Hinglish inputs that pass are the ones that contain English keywords (`"yaar I'm so tired"` → drowsy, `"thank you beta"` → tender).

### C. No negation: 7/7 negation cases (plus `"Thankfully nobody was hurt"` → sad inside m10). Severity: HIGH
`"I'm not happy with the service"` → **happy**; `"I'm not sad anymore"` → sad; `"Don't worry, everything is fine"` → worried;
`"There's no emergency, relax"` → **dread**; `"I'm not angry, just tired"` → angry; `"I don't hate it"` → angry; `"not bad at all"` → attentive.
Reassurance ("don't worry", "no emergency") makes the face show the exact fear being dismissed.

### D. Missing English vocabulary: 7 cases (and 14 of the 16 beats lost per-sentence). Severity: MEDIUM-HIGH
`"I'm mad at my brother"` → attentive; `"The kids are so sweet"` → attentive; `"you're so cute"` → attentive; `"good job homebot"` → attentive;
`"ugh"` → attentive; `"nooo"` → attentive; `"Ahh! Something just fell off the shelf!"` → attentive/intense.
Also missing: "cry" (only "crying" is listed, so `"the ending made me cry"` → attentive), "proud" (`"I'm proud of myself"` → attentive,
because the proud family contains no "proud" keyword), "stressed", "tension", "scam", "phew", "thank god", "failed", "hospital".

### E. Emoji ignored: 4/6 expression, 3/6 level. Severity: MEDIUM (chat and WhatsApp-style input)
`"😂😂"` → attentive/low; `"😭"` → attentive/low; `"❤️"` → attentive/low; `"great 😡"` → attentive/low (the emoji should override "great").

### F. Typos and elongation not normalised: 4/6. Severity: MEDIUM
`"yaaaay!!!"` → attentive/intense; `"sorrry"` → attentive; `"thnks"` → attentive; `"angery"` → attentive.
Probes: `"dont tell mom"`, `"i dont understand"`, `"whats the time"` → attentive (the keywords require the apostrophe); `"thx"`, `"ty"`, `"thank u"` → attentive.

### G. Sarcasm read literally: 4/4. Severity: MEDIUM
`"wonderful, it's raining again"` → delight; `"Perfect. The wifi is down again."` → delight;
`"oh great, another electricity bill"` → attentive ("great" alone is not a keyword); `"Yeah right, like the plumber will come today"` → attentive.

### H. First match decides, not the stronger emotion: 10/20 shadow probes wrong. Severity: HIGH
"really" and "seriously" are both *surprised* keywords and level intensifiers. Surprised sits above 13 later families,
so intensifying any of those emotions turns the face into surprise:
`"I'm really tired"` → surprised; `"I'm really bored"` → surprised; `"I really don't understand this form"` → surprised;
`"I'm really embarrassed"` → surprised; `"seriously, I'm exhausted"` → surprised; `"I really think we should go"` → surprised.
Order also beats salience: `"Sorry to hear your father died"` → apologetic; `"Take care, I'm terrified for you"` → tender;
`"I'm so happy I'm crying"` → crying; `"I think I'm going to cry"` → thinking.

### I. Question mark overrides tone: 2 cases. Severity: LOW-MEDIUM
`"why would you do that?!"` → curious/mid; `"WHY IS THE GEYSER NOT WORKING???"` → curious/intense.

### J. Perspective: insults to homebot are mirrored as anger: 2 cases. Severity: MEDIUM (children will say this)
`"you're useless"` → angry/low; `"I hate you"` → angry/mid. A family robot should look hurt or apologetic, not glare.

### K. One expression per input: multi-emotion paragraphs. Severity: HIGH (stated requirement)
- Whole paragraph: 23/56 beats (41%). 33 beats are lost by design. Which beat survives depends on family order, not on text order or salience.
  The first beat survived in 17 of 23 paragraphs and a later beat in 6 (m04 joke→grief kept crying; m08 surprise→thanks kept tender).
- `"I got the job offer! But it's in Bangalore and I'll miss everyone."` → attentive/intense (both beats lost; "miss everyone" is not "miss you").
- `"I love you beta. But you need to stop playing games all night."` → love (the stern beat is lost; "stop" without "it" is not a keyword).
- Splitting on `.!?` and calling `read()` per sentence recovers 17 more beats: **40/56 (71%)**.
  Of the 16 beats still missed, 14 are missing vocabulary, 1 is negation ("nobody was hurt" → sad), and 1 is the question default ("is this a scam?" → curious).
  Splitting is cheap and almost all of the remaining loss is vocabulary.
  Caveat: the alignment is greedy and in order, and lenient. A beat can match a neighbouring sentence, so treat 71% as an upper bound.

### L. Level misjudged: 8/131 single cases, 9/10 level probes. Severity: MEDIUM
- The ≤2-word "flat line" rule: `"i'm annoyed"` → angry/**low** (expected mid). "i'm" makes it two words.
- Caps lock is read as shouting: `"ADD MILK TO THE LIST"` → attentive/**intense**. Indian acronyms count as shouting too:
  `"pay the EMI today"` → intense vs `"pay the loan today"` → mid; same for OTP.
- Elongation counts only once: `"sooooo happyyy"` → happy/mid (expected intense). "so " needs a trailing space, so "sooooo" does not count as an intensifier.
- One "!" on an emergency stays mid: `"Emergency! There's a gas leak in the kitchen"` → dread/mid.
- Emoji-only input → low: `"😂😂"`, `"😭"`, `"great 😡"`.
- Intensifiers and diminishers are matched as substrings: `"going to the supermarket!"` → intense vs `"going to the shop!"` → mid ('super');
  `"every day is the same!"` / `"I never said that!"` → intense ('ever'); `"so that we can leave early!"` → intense;
  `"I'd rather stay home today"` → low; `"just a reminder, the gas man comes at 4"` → low; `"hmmm ok"` → mid vs `"hmm ok"` → low.
- Word choice carries no strength: `"I'm furious"` and `"i'm annoyed"` score the same; only punctuation and caps raise the level.

## 3. Unreachable expressions and shadowed keywords

**Unreachable from `read()` (14/43), verified by running `expression_of` on every keyword plus both fallbacks:**
rest, answering, startled, wink, dizzy, squint, yawn, waking, glitch, oh, fret, alarmed, peek, blink.
- Still reachable through other paths: rest (BRAIN_STATES, SEQUENCES), answering (BRAIN_STATES), and startled, squint, yawn, waking, oh, fret, peek (SEQUENCES only).
  Touch and the app also flash wink, dizzy, startled and squint.
- No route from text at all: **wink, dizzy, glitch, alarmed, blink**.
  wink and dizzy are reachable by touch. alarmed and glitch are reachable only through the `/name` command and the F1 demo cycle (I grepped homebot/ to check). blink is the idle blink's pose.
- Text routes that are needed: startled/alarmed for "Ahh!" and "oh no!"; oh for "oh!"; fret for stressed/tension (very common Indian English);
  yawn for "yawn" (it currently goes to drowsy).

**Keywords that can never win (4 of 226; the bare keyword already loses to an earlier family):**
- `sad: 'unhappy'` always loses to happy, via 'happy'. The inversion is total: unhappy → happy face.
- `suspicious: 'really though'` always loses to surprised, via 'really'.
- `asleep: 'good night'` always loses to tender, via 'good night'. This is the only keyword listed in two families; "goodnight" (one word) still reaches asleep.
- `bored: 'whatever'` always loses to angry, via 'hate'.

**Effectively shadowed:** every family after surprised (13 of 28) is overridden whenever "really" or "seriously" appears.
The proud family has no "proud" keyword; "proud of you" lives in tender.

## 4. Level integrity (real Animator)

Method: for each of the 43 poses × 3 levels I built a fresh `Animator(FaceRenderer((400,250)))` and called `a.set(name, intensity=level_amount)`.
I then ran `update()` until at least 1.25 × the beat duration and at least 40 frames had passed, with 0.02 s sleeps, and kept 12 settled frames.

Idle noise: I compared levels on the noise-free target `a._to`, not on `update()` output. I used the settled frames for two things only:
the structural checks (on the real, sanitised output) and a param-space idle-noise floor (`settled_dev`, the mean distance of settled frames from `_to`).

Distance metrics:
- **Param distance**: L2 over all 43 floats. Angles are divided by 20°, tilt by 10°, shifts by 10 px and aberration by 5 px; everything else is in native units.
- **Pixel distance**: % of pixels that change by more than 24 levels when rendered. The per-pose noise floor is the same pose with one mean-size saccade (gaze_mag/2), breath crest and drift crest applied.

Threshold: a level step is **indistinguishable** if it is below the idle noise on either metric, and **marginal** if it is under 2× noise.
The reasoning: a step smaller than the face's own idle motion cannot be read as a deliberate change.

- **Structural rules hold.** Mouthless poses (suspicious, tender, alarmed, peek, attentive, drowsy) never grew a mouth.
  Hidden-pupil poses (12, including the one-eye cases wink R and peek R) never showed a pupil. 0 violations; LEVELS are monotonic for every entry.
- **Identical levels:** `rest` is byte-identical at all three levels (0.0% pixels, L2 0.000), because `rest.blend(rest, k)` is always rest. The LEVELS comment says "a breath apart"; it is not even that. `blink` (1, 1, 1) is identical by design.
- **Indistinguishable:** `answering` low→mid and mid→intense change 0.8% of pixels against a 1.6% idle floor. `asleep` mid→intense has L2 0.151 against a settled noise of 0.242 (1.5% px).
  `glitch` mid→intense has L2 0.394 against noise 0.406.
- **Marginal (under 2× idle on one metric):** `attentive` (the most common output, 43/131 cases) has L2 0.158/0.113 against noise 0.090, so its level choice is mostly invisible.
  `listening` has L2 0.138/0.134 against 0.105. Others: curious (px 1.19–1.25×), love (1.41–1.64×), dizzy (1.35–1.53×), worried (1.39–1.54×), thinking (1.7×), confusion (1.8×).
- **Intense produces out-of-range or collapsing values** (on the unsanitised target):
  - `stern` intense eye h = **0.053**: the slit almost vanishes (sanitise floor 0.02).
  - `dread` intense pupil_scale **0.29**: pinprick pupils.
  - `oh`/`dread`/`startled`/`yawn` intense mouth_open 1.44/1.40/1.35/1.30 are clamped to 1.2, so the mouth stops scaling between mid and intense.
  - `searching` intense pupil_x 1.10 is clamped to 1.0: the pupils are pinned at the edge and idle saccades clip there.
  - `delight`/`happy`/`love` intense mouth_curve 1.28/1.01/1.06 exceeds the documented −1..1 range and is not clamped (the renderer draws a deeper arc).
  - `crying` intense tear 1.22 → clamped to 1.0.
  - `wink` intense upper_lid 1.13 → clamped to 1.0 (harmless).
  - radius > 0.5 for several poses (clamped, harmless).
- **Design notes:** 17 expressions use `_DEFAULT_LEVELS` (0.45, 0.85, 1.30), including tender, which text reaches often.
  "mid" is 0.85–0.95 for most poses, so the normal level (96/131 single cases came out mid) never shows the pose exactly as designed.

## 5. Gaps to fill later, ranked by impact

1. **Word-boundary matching** (`\b` regex with an allow-list of stems such as `apolog`, `irritat`, `confus`, `embarrass`). Fixes the 15 in-word false positives, the 25 probe hits, the Hindi "hi " hits and the unhappy/displeased/uncomfortable inversions.
2. **Negation scope**: if not/no/never/don't/nahi/nako occurs within ~3 tokens before a keyword, neutralise or flip it (not happy → sad/angry; don't worry → content). 7/7 cases plus m10.
3. **Hindi/Marathi lexicon in both scripts** (khush/खुश, dukh/दुख, gussa/गुस्सा, thak/थक, bhiti/भीती, dhanyavad/धन्यवाद, zabardast, tension, pareshan). 12 failing cases. This household's actual language.
4. **Score all families and pick the strongest, instead of first match**, and remove "really"/"seriously" from surprised (keep them as intensifiers only). Fixes the "really tired → surprised" class and "sorry … died".
5. **Per-sentence reading with beats handed to the Animator** as a timed SEQUENCES-style list. Already measured at 41% → 71% beats with no other change.
6. **Fill the English vocabulary holes** (mad, cry, sweet, cute, good job, proud, stressed, scam, phew, thank god, ugh, nooo, oh no). Most of the remaining per-sentence loss.
7. **Fix the level scorer**:
   - word-boundary `_UP`/`_DOWN` (super, ever, so, rather, just a);
   - treat an all-caps whole sentence as caps lock and add an acronym list (EMI, OTP, UPI, ATM, GST);
   - count elongation per word;
   - add lexical strength (furious > annoyed);
   - skip the ≤2-word low rule when an emotion keyword matched.
8. **Emoji map** (😂 grin, 😭 crying, ❤️ love, 😡 angry, 🙏 tender, 👍 content), with the emoji taking precedence over adjacent words. 4 expression and 3 level failures.
9. **Normalise before matching**: collapse 3+ repeated letters (yaaaay → yay), accept apostrophe-less forms (dont, whats, im), and a small typo table (thnks, thx, angery). 4 cases plus probes.
10. **Insults aimed at homebot** ("you're …", "I hate you") should route to sad/apologetic, not mirrored angry. 2 cases.
11. **Make the unreachable faces reachable where meaningful**: startled/alarmed for "ahh!"/"oh no!"; oh for "oh!"; fret for stressed/tension; wink for "just kidding"/";)"; yawn for "yawn".
    De-duplicate "good night" (tender vs asleep).
12. **Level-integrity fixes**:
    - give `answering`, `attentive` and `listening` wider LEVELS triples (their level steps are within idle noise);
    - give `rest` a non-rest scaling target or drop its levels;
    - widen asleep's mid→intense step;
    - cap stern intense h around 0.10 and dread pupil_scale around 0.35;
    - clamp mouth_curve to ±1, or let mouth_open scale past 1.2 so intense ≠ mid.
13. **"?!" / "why would you" tone**: route to angry/confusion instead of curious. 2 cases.
14. **Sarcasm heuristics** (a positive word plus "again"/"another"/a complaint noun → skeptical/bored). 4 cases. Hardest to do well, so it ranks last.

## 6. What works well

- **Explicit English emotion sentences**: plain 23/26 and strength triples 12/12 on expression. Level 11/12 on the triples; the only miss is the 2-word rule on `"i'm annoyed"`.
  Examples: `"i'm a bit annoyed"` → angry/low (0.40), `"I AM SO ANNOYED!!!"` → angry/intense (1.40), `"i'm kind of worried about the exam"` → worried/low.
- **Household commands stay neutral** (7/8): `"add milk to the list"` → attentive; `"find my phone"` → searching; `"what's on the calendar today?"` → curious.
- **Edge inputs are safe** (no crashes): `""`, `"   "`, `"12345"` → attentive/low; `"!!!"` → attentive/intense.
- **Level accuracy overall is 94%**, and the rendered poses honour the structural rules at every level (0 violations).
- **Fast**: 12 µs per call on average, 43 µs on a 258-character paragraph.
- **The `why` field made every failure above diagnosable in one line**, so keep it in whatever replaces this.
