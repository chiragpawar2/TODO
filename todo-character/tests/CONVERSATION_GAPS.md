# homebot face: conversation-level gaps (round 2)

Source: `tests/conversations.py` (100 hand-written conversations; expectations
fixed before any run) driven by `tests/run_conversation_tests.py` through the
real `FaceApp` (`_submit`, `_wake`, `_on_state`, `_on_reply`, `_idle_check` run
unmodified). Fake clock at 50 fps (the app's tick). Brain states are simulated
from each conversation's expected states (there is no API key), using
`mind.Mind`'s busy contract. `OfflineMind` and the real threaded `Mind` were
also run separately. Nothing under `homebot/` was edited. All numbers are from
the last run. Timings vary a little between runs; everything else is
deterministic (seeded).

## 1. Headline numbers

| | |
|---|---|
| Conversations | 100: 40 short (2 turns), 35 medium (3-8), 25 long (6-20 turns, plus touches, silences, sequences) |
| User turns / homebot replies | 298 / 290. Frames simulated: 219,340 (73 min) |
| Expression accuracy | **223/298 = 75%**. Short 32/40 (80%), medium 75/94 (80%), long 116/164 (71%) |
| Level accuracy | **276/298 = 93%**. Short 95%, medium 95%, long 91% |
| Lip-sync | **264/290 = 91%** pass the hard checks; 249/290 (86%) if the seconds-per-word warning counts. **26 of 111 replies that contain a digit fail (23%)** |
| Frame sanity | **0** NaN/inf/out-of-range values in 219,340 frames. **80 glitch jumps** in 38/100 conversations (73 breathing-layer swaps, 4 talk-style swaps, 3 cut-off utterances). 963 over-threshold jumps were classed as legitimate |
| Interruptions | User spoke over homebot 5 times: speech carried on 5/5 and was never hushed. 4 replies cut off a reply that was still playing. Touch during speech: speech carried on 3/3. Lines sent while the brain was busy: **3/3 silently dropped** |
| Mouthless speech | Renders **0 mouth pixels** in all 6 mouthless poses for the whole utterance |
| Read face on screen | **0 of 60** live submits through the real threaded `Mind` showed the `read()` face for even one frame |

How jumps were judged. A frame-to-frame change is flagged when it goes past a
per-channel threshold at 50 fps: glow 0.10, shift 3 px, tilt 3°, eye h 0.30,
lids 0.35, pupil xy 0.35, pupil alpha 0.45, mouth_open 0.45, mouth_alpha 0.35,
curve 0.35, scale 0.05. These limits sit above what a default 0.42 s beat
produces across the library's largest ranges, and below what a frame cut
produces. Each flagged jump is then split into its pose layer (`anim.current`)
and its residual (idle life plus speech). It counts as **legitimate** when:
- the pose layer moved inside an active beat (`transition`: 207; `snap_beat`: 18, the deliberate hold_snap poses suspicious, stern, dread and angry);
- or the residual is explained by a blink (2), a saccade or look_at (28), or a viseme change (`speech`: 708, mostly mouth_open, because a 70 ms cosine blend from X to D peaks near 0.49 per frame).

Note: look_at sets the gaze in one frame (pupil xy jumps up to 1.22). It is classed as a saccade here, but it is a teleport, not a 70 ms move.

It counts as a **glitch** when the residual jumps on the very frame the base,
overlay or utterance changes.

## 2. Failures by root cause

### A. Expression choice (75 misses)

**A1. Nothing matched, so the face fell back to `attentive`: 57 misses (76% of all misses). Severity HIGH.**
No word-free signal is used. `!!!`, capitals, "oh no", "yay"-less good news and
bad news all land on the mouthless neutral face.
- `"Kaka got a new job in Dubai!"` gave attentive. It should be delight or surprised.
- `"I smell gas in the kitchen!"` and `"bus is coming in 2 minutes!!"` gave attentive. They should be alarmed or dread. `"HELP! Ajoba fell in the bathroom!"` also gave attentive: "help me" matches but "help!" does not.
- `"she's very sick"`, `"Actually, Baba just called. His flight got cancelled."` and `"homebot I broke Aai's vase"` all gave attentive. They should be sad or worried.
- Hindi and Marathi have no keywords at all. `"मला खूप एकटं वाटतंय"` (I feel very lonely), `"तुम बहुत अच्छे हो"`, `"tu khup gunacha aahes"` and `"arre wah! chhan!"` all gave attentive. All 13 Devanagari turns were decided by `?` or the default, never by a word. The 10 that "passed" only did so because curious or attentive was in the expected set.
- Held letters are not normalised: `"I'm boooored"`, `"byeee"` and `"ohhh"` all gave attentive.

**A2. Substring false hits: 5 misses. Severity HIGH (the wrong emotion, not just a missing one).**
- `"I studied hard for the maths test"` gave **crying**, because "stu**died**" contains "died".
- `"whatever"` gave **angry**, because "w**hate**ver" contains "hate".
- `"Book the cheapest flight to Del**hi** next Friday"` and `"Kamwali bai aaj phir na**hi** aayi"` gave listening, because "hi " matches.
- A long Marathi turn ending in `"...chaha la"` gave **grin**, because "c**haha**" contains "haha".

**A3. Keyword with no context or negation (first family wins): 10 misses. Severity MEDIUM.**
- `"help me with fractions"` and `"help me step by step"` gave **dread**.
- `"I can't find Aarav anywhere!!"` gave searching. That is a panic, not a lookup.
- `"I'll really miss him"` and `"hmm, so not really worth it?"` gave surprised, from "really".
- `"no but I'm scared she'll be angry"` gave angry. The fear is the feeling here.
- `"no don't tell her"` gave mischief. `"ok you're forgiven"` gave apologetic. `"I think she's a big potato"` gave thinking. `"hmm not bad"` gave suspicious.

**A4. A bare `?` maps to curious even for angry or confused questions: 3 misses. Severity LOW-MED.**
`"why did you play the alarm at 4 am??"`, `"why not??"` and `"काय? मला ऐकू आलं नाही"` all gave curious.

### B. Level (22 misses)

- **B1. The short-flat-line rule also fires on questions and laughs: 14 misses.** `"total?"`, `"and savings?"`, `"sleepy?"`, `"किती वाजता?"`, `"hahaha"`, `"phew lol"`, `"yes please"`, `"you're cute"` and `"I'm scared"` all gave **low**. The rule only exempts `!`.
- **B2. Acronyms count as shouting: 5 misses.** BP, UPI, FD and ID push the score to intense. `"Can you check Ajoba's BP reading?"` and `"where is my school ID?"` both gave intense. Only I, OK, TV, AM and PM are exempt.
- **B3. Down-words matched as substrings: 2 misses.** `"I'll be back in a bit"` gave low. `"not really"` beats `"really"`.
- One judgement call: `"whatever"` gave mid; a person would read it as low.

### C. Lip-sync (26 replies fail; all of them contain digits)

- **C1. A number at the end of a sentence is never spoken: 13 replies. Severity HIGH.** `pronounce.normalise` stops stripping the full stop because `_DEC.match("5"+".0")` passes. So `"5."` stays a token, gets `skipped` and is mouthed as one "C" beat.
  - `"...platform 5."`
  - `"...divided by 4 is 990."`
  - `"His usual is around 130 over 85."`
  - `"391."`: the whole answer to Ajoba's maths test goes unsaid.
- **C2. Fractions are read as "slash": 10 tokens.** `1/2 tablet` becomes "one slash two". `3/4 cup` becomes "three slash four". The medicine-dose reply is affected.
- **C3. Units are not expanded: 6.** mg, ml and GB are mouthed letter by letter (`_ABBREV` has kg and km only).
- **C4. Indian forms.** `₹1,00,000` and `₹1,25,000` become "one hundred thousand" rather than lakh (2 replies). Helplines read as years: `call 1906` becomes "nineteen oh six". In our replies 1930 and 1906 were also caught by C1.
- **C5. Hyphenated and joined numerics are not handled: 3 replies, plus probes.** `98201-23456` is skipped. `5-star`, `2-3 days`, `10am`, `7:30pm` and `Rs.500` all come out with the digits still in.
- **C6. Wrong decimals (probes).** `₹1,250.50` becomes "rupees one two hundred fifty fifty": the thousand and the point are lost. `₹2.5 lakh` becomes "rupees two five lakh".
- **C7. Devanagari edge cases: 1 reply, plus probes.** In `"...500 mg।"` the danda glues onto "mg", so the token goes to the Devanagari G2P and is skipped. Devanagari digits `७:३०` and `₹१,२५०` are skipped.
- **Warning only.** Replies of 1-3 words run 0.9-1.24 s per word (`"Okay."` takes 1.15 s), because of the fixed 0.10 s lead, 0.34 s stop and 0.18 s tail. The median across all replies is 0.45 s per word.

All cue shapes were valid and cues were ordered in all 290 replies. 12 of the
13 Devanagari replies are clean.

## 3. Speech on mouthless poses

`renderer._draw_mouth` returns early when `mouth_alpha < 0.02`. `Animator.update`
raises `mouth_open` during speech but never touches `mouth_alpha`. The
comment in `TALKS` says "Speaking has to GROW one", but no code does that.

I set each pose, let it settle for 1.5 s, then spoke `"Your reminder is at
7:30, Aaji's tablet, 500 mg, after dinner."` I rendered every 5th frame and
diffed it against the same frame with the mouth removed:

| pose | internal mouth_open max | rendered mouth pixels during speech |
|---|---|---|
| tender | 0.67 | 0 (74 sampled frames) |
| alarmed | 1.10 | 0 |
| peek | 0.77 | 0 |
| attentive | 0.73 | 0 |
| drowsy | 0.43 | 0 |
| suspicious | 0.57 | 0 |
| control: answering | 1.10 | up to 12,382 (4,756 at rest); visibly moving in 36 of 58 frames |

Both paths give the same result: plain `set()` and the `read()` intensity path.
The head bob, glow pulse, squint and pupil accent keep running, so the face
nods and pulses with no mouth at all. In normal flow the reply starts in
`answering` (282 of 290 replies), so this shows up when the user talks over
homebot:
- **c090:** `"that's lovely, thank you"` arrives mid-reply. Tender gives 41 frames (0.8 s) of voiced, mouthless speech.
- **Experiment:** a thank-you at 40% of a reply. The mouth is gone 0.5 s later, with **4.6 s of speech left to play invisibly**.

`attentive` is also the default `read()` face for 38% of all user lines.

## 4. Transitions, interruptions, sleep and wake

**The `read()` face never reaches the screen.** Through the real threaded
`mind.Mind` (offline), 60 of 60 `_submit` calls returned with the base already
on answering or delight (median round trip 0.3 ms). With the real engine,
`_work` emits "thinking" on its first line. So the read face shows for at
most a frame or two. The simulation gave it 1 frame, which is generous.

Everything measured in section 2A is invisible in the live app, except when
the user speaks over homebot.

**Talking over homebot.**
- Speech carried on 5/5 and was never hushed. It kept going under the user's face, and then under `thinking` (talk open_max 0.34). Homebot keeps saying the stale answer while it "thinks".
- The new reply then cuts the old one in one frame: mouth_open goes **-1.10** (c089), -0.50 (c060) and -0.46 (c096).

**Mood change mid-utterance.** The `speak()` docstring is right: delivery
follows. Sad brought the peak open from 1.10 to 0.43 and flipped the bob
downward. But the style swaps instantly:
- First frame: mouth_open -0.29 and shift_y +2.4 px (sad), shift_y -1.9 px (angry).
- c089: mouth_open +0.57 in one frame at thinking to answering.

**Breathing layer swaps instantly** when the base changes. `glow *= 1 +
depth*sin(now*rate)` jumps to the new depth and phase at once: **73 glow jumps**
in conversations, up to 0.27 per frame (rest to asleep, depth 0.045 to 0.30).

**Brain states do not stop sequences.** With `!nod_off` playing, "thinking"
was overridden 0.4 s later by `waking`. The reply was then spoken while the
face yawned and fell asleep (trace: thinking, waking, drowsy, answering, yawn,
asleep).

**Non-answer replies are held forever.**
- After refused the face stays apologetic. After stuck or unknown it stays confusion. After tool it stays searching. All still held at 60 s, because `_idle_check` only relaxes answering, delight and speaking.
- 5 of 100 conversations ended in one of those faces.
- Offline: OfflineMind answers 71 of 298 lines (24%) from the "tool" state, so those replies are spoken in, and stuck on, `searching`.

**Messages dropped while busy.** `Mind.ask` returns early, but the face still
reacts. In c062 `"and tomatoes"` and `"and coriander"` were lost, and in c098
`"and my tiffin?"` was lost (3/3). No error or caption tells the user.

**Touch during speech** is handled. Speech carried on 3/3 and through 5 fast
pokes (surprised, surprised, surprised, annoyed, dizzy). Delivery keeps the
base talk style.

**A user line stops a sequence** (`stop_sequence` in `_submit`). Working.

**Idle, sleep and wake.**
- It dozes at 75.02 s: yawn flash, then asleep. The requested `duration=1.8` is dropped (1.70 used) because the overlay defers `_begin`. Trivial.
- Wake by key: waking plus a surprised flash, held while typing, then the read face. Good.
- **Wake by touch, then silence:** stuck in `waking` (half-lidded) at 1, 5, 20 and 60 s. It sleeps again at 80 s and never returns to rest.
- **"Goodnight" through the brain's sleep state:** the face goes to `asleep`, but `app.asleep` stays False.
  - A key 10 s later plays no wake. It cuts from asleep straight to curious, with a 0.195 glow jump.
  - 75 s later `_idle_check` flashes a yawn (mouth open 1.0) on the already-sleeping face.
- A long brain call keeps it awake, because `busy` refreshes `last_activity`. Correct.

**Variety.**
- 29% of consecutive user turns (58 of 198) get the same face. The longest run is 5 (c096).
- `read()` chose attentive 114 times (38%) and curious 63 times (21%).
- Faces never shown in 100 conversations: glitch, fret, content, alarmed, peek (and blink, which is internal).
- 16 of 43 are never chosen by `read()`.
- answering and rest take 82% of all frames.

**Performance** (laptop):
- `update()`: mean 27 µs, p99 46 µs, max 595 µs.
- `read()`: mean 36 µs, max 137 µs.
- VisemeTrack: mean 0.17 ms, max 0.74 ms.
- `render()`: 4.1 ms at 640x400. Render, not animation, is the Pi budget.

## 5. Gaps to fill, ranked by impact

1. **The read face is overwritten immediately.** Hold the `read()` pose for a minimum of about 0.6-0.8 s before brain states may replace it (a timestamp guard in `_on_state`, or queue the state).
2. **Mouthless poses speak invisibly.** In `update()`, while `_utt` is active, raise `mouth_alpha` toward 1 (or blend to the nearest mouthed sibling, e.g. tender to love, attentive to listening) and fade it back after.
3. **Sentence-final numbers are skipped.** In `normalise`, only keep the trailing "." as a decimal point when digits follow it; strip it otherwise.
4. **Messages are dropped while busy.** Queue lines in `Mind.ask` (or show "still thinking" and flash confusion) instead of returning silently.
5. **There is no fallback for unmatched lines.** Add a punctuation and affect fallback before `attentive`: `!` or caps lean to surprised or delight, emergency cues to alarmed, "oh no" or "no no" to sad.
6. **Substring matching gives false hits.** Match on word boundaries (`\bdied\b`, `\bhate\b`, `\bhi\b`) so studied, whatever, Delhi, nahi and chaha stop triggering.
7. **Talking over homebot leaves stale speech.** On a new user line, `hush()` (or fade it out over about 120 ms). In `speak()`, cross-fade from the old utterance instead of replacing it in one frame.
8. **Non-answer faces stick.** Extend `_idle_check`'s relax-to-rest to apologetic, confusion, searching and waking, with their own hold times.
9. **Breathing and talk style swap instantly.** Blend the Idle and Talk parameters over the beat duration instead of reading `idle(self.base)` and `talk(self.base)` raw each frame. That fixes the 73 glow jumps and the mid-speech style snaps.
10. **Two notions of "asleep".** Make the brain's "sleep" state go through the app's sleep path (`app.asleep = True`), so a later key plays the wake and no yawn fires on a sleeping face.
11. **Brain states don't stop sequences.** Call `stop_sequence()` in `_on_state` (or let a sequence be marked as interruptible).
12. **Hindi and Marathi have no keywords.** Add Devanagari and romanised families (एकटं, दुःख, आनंद, घाबर, wah, chhan, bakwas, dar lag).
13. **Level heuristics misfire.** Exempt questions and laughs from the short-flat-to-low rule; exempt known acronyms (BP, UPI, ID, FD, OTP, PIN) from shouting.
14. **Number formats.** Add fractions (half, three quarters), units (mg, ml, GB, tsp), Indian lakh and crore grouping, digit-by-digit reading for phone numbers and helplines, the `Xam`/`X:YYpm` forms, `Rs.N`, hyphen ranges, and decimals with a comma or currency sign.
15. **Devanagari tokenising.** Split the danda and Devanagari digits off before G2P, and map ०-९ to Marathi or Hindi number words.
16. **Unused faces.** Wire fret, content, alarmed and peek into `read()` families (e.g. "relieved"/"phew" to content, emergencies to alarmed) so 5 designed faces stop being dead weight.

## 6. What works well

- **Numerically robust.** 0 NaN or out-of-range values in 219,340 frames, including overshoot, touch storms, sequences and sleep. `sanitise()` holds.
- **Lip-sync on plain prose.** Times (`7:15`, `6:40`), `₹1,250`, percentages, decimals (`3.5`, `1.5`) and Devanagari sentences are correct. Every cue shape was valid, and the median pace is 0.45 s per word.
- **Speech goes on through touches and pokes,** and the mouth stays expressive. Sad speaks at 0.43 open against 1.10 for answering, with the bob reversed. "Delivery follows mood" is real.
- **Normal flow is smooth.** In the normal answering flow the face returns to rest (95 of 100 conversations end at rest).
- **Sleep and wake by keypress work.** Idle sleep fires at 75 s and the key wake looks right.
- **Cheap.** `update()` at 27 µs and `read()` at 36 µs are negligible next to a 20 ms frame.
