# homebot's face

A blue CRT character, drawn procedurally. No image assets — every frame is
computed from 43 floats.

```bash
python -m homebot.face                 # window, for evaluating on a laptop
python -m homebot.face --fullscreen    # the Pi
python -m homebot.face --cheap         # drop aberration and bezel if the Pi struggles
```

## Talking to it

| | |
|---|---|
| **Type** + Enter | always works, nothing to install |
| **Hold F2** | push-to-talk; see *Voice* below |
| **Click / touch the face** | see *Touch* below |
| `/name` | hold one expression (`/delight`, `/glitch`, …). `/` alone lists them |
| **F1** | step through all 30 expressions |
| **TAB** | fps, current state, brain backend |

## Touch

| where | reaction |
|---|---|
| left eye | squints that eye |
| right eye | winks |
| mouth | surprised |
| forehead | confusion |
| cheeks | shy |
| anywhere else | curious, and the eyes look at your finger |
| stroke across | love |
| 4 fast pokes | annoyed |
| 5 fast pokes | dizzy |
| long press | shy |
| poke while asleep | startled, then waking |

The eyes also track the mouse pointer when it is over the panel.

## How it is built

Four files, each one layer:

- **`params.py`** — the float space. 7 global, 15 per eye, 6 mouth.
- **`expressions.py`** — 30 named points in that space, plus each one's **beat**
  (how it arrives), **idle** (how it lives once held) and **talk** (how it speaks).
- **`speech.py`** — turns text into one impulse signal: rhythm, stress, pauses.
- **`animator.py`** — beat → overlap → idle → speech → touch.
- **`renderer.py`** — shapes → bloom → chromatic aberration → scanlines.

### Every expression has its own acting, not one shared curve

> "Identical endpoints can feel heavy, light, cautious, explosive, smooth,
> mechanical, comic, or alive depending on their in-betweens... do not make
> every acceleration mathematically even."

So each expression owns a `Beat(dur, anticipate, overshoot, hold_snap)`.
`startled` arrives in 100 ms with **no** anticipation — a shock has no time to
prepare — and overshoots to 1.37 before settling. `angry` pulls back to −0.17
first, then strikes. `sad` takes 800 ms and never bounces at all; anything
that springs there reads as fake.

Channels are also staggered — eye shape leads, pupils at +5%, mouth at +13%,
glow and tilt at +19% — so the face arrives as a chain of cause and response
rather than all at once.

Each expression also owns an `Idle`: `angry` almost never blinks (that is what
makes a stare a stare), `thinking` looks around twice as often, `asleep`
breathes slow and deep.

### Lip sync

Real visemes, on the Rhubarb / Hanna-Barbera shape set — six basic shapes plus
Rhubarb's three extended ones:

| | mouth | sounds |
|---|---|---|
| **X** | rest, lips relaxed | pauses |
| **A** | closed, slight pressure | P B M |
| **B** | slightly open, teeth together | most consonants, and EE |
| **C** | open | EH (men), AE (bat) |
| **D** | wide open | AA (father) |
| **E** | slightly rounded | AO (off), ER (bird) |
| **F** | puckered | UW (you), OW (show), W |
| **G** | teeth on lower lip | F V |
| **H** | open, tongue up | long L |

There is no audio, so this is the standard text-only chain: **grapheme to
phoneme, then phoneme to viseme**. The G2P is rule-based rather than
dictionary-based, which is wrong on English's irregular spellings (it says
"though" with an OW) and exactly right on **Devanagari, which is phonetic** —
so Marathi and Hindi lip sync are actually the more accurate of the two.

Two details carry it:

- **The mouth closes between words**, and closes harder at punctuation. A
  mouth that never returns to X is the commonest tell of fake lip sync.
- **Cues are cosine-blended over ~70 ms**, not cut. Rhubarb's own example for
  "Hi" is `X D C B X` and notes the C is inserted only "as an in-between...
  for a smoother animation from D to B" — our blend passes through that
  intermediate opening on its own, so the in-between comes for free.

Teeth and tongue are deliberately not drawn. At 320×240 behind a scanline mask
they are below the panel's resolution, and faking them costs legibility.

Devanagari also gets **schwa deletion** — the word-final inherent vowel is
dropped, so नमस्कार is *namaskaar*, not *namaskaara*.

### The viseme says what, the expression says how big

> "Dialogue and facial action require a thought change, not mouth-shape
> substitution. Face, head, spine, weight, and appendages should share the
> same impulse."

So the viseme track sets the mouth *shape*, and the expression's `Talk` style
scales it and spends the same impulse across the rest of the face: head rise,
tilt sway across the phrase, glow pulse, eyes tightening on loud syllables,
pupil and lid kick on stressed ones.

`delight` opens 1.43× and bounces; `apologetic` opens 0.50× and its head
**sinks** instead of rising; `angry` clips each syllable short; `asleep` only
mumbles. Same words, same shapes, different performance.

Type `>some words` in the window to make him speak them in whatever expression
is currently held.

### Why parametric and not a sprite sheet

Every expression is a point in one continuous space, so the animator can tween
between any two of them — including pairs nobody designed. A flipbook can only
play transitions someone drew. This is the approach Anki used for Cozmo and
Vector (~43 interpolated floats) and it is most of why those faces read as
alive rather than as a UI.

### The idle layer is not optional

Blinks, micro-saccades, breathing glow and drift are applied on top of *any*
expression, including mid-transition. A face that holds perfectly still between
states reads as a screensaver. Timings are from the research:

- blink every 2.8–6.5 s (humans: 14–17/min at rest); 120 ms to close, 90 ms to open
- re-gaze every 1.2–3.4 s, each saccade under 80 ms and then dead still
- macro transitions 420 ms

The saccade is deliberately *not* eased. Easing it makes the eye look like it
is swimming.

### Two rules every expression obeys

1. **Redundant encoding.** Eye silhouette, pupil direction and mouth all change
   in every state. Kalegina et al. (HRI 2018) found that stripping the mouth
   and pupils makes a robot face read as "soulless" and get assigned to
   surveillance; a 305-participant study found full faces recognised at 64.4%
   vs 51.3% for eyes-only. No study places Indian viewers on the eyes-vs-mouth
   axis, so we encode the feeling twice.
2. **No two states share a physical solution.** `angry` and `sad` have nearly
   identical lid coverage and differ only in the *sign* of `upper_angle` —
   which is how the distinction actually works on a face.

## The nine states are real code

`expressions.BRAIN_STATES` maps to actual branches in `homebot/brain.py`:
`engine.complete()` → thinking, `dispatch(tool)` → searching, `result.refused`
→ apologetic, `MAX_TOOL_ROUNDS` → confusion, and so on.

`mind.py` wires this up **without editing brain.py**: it wraps the engine
object and swaps `homebot.brain.dispatch` for an announcing version. Both are
reversible.

With no working API key, `OfflineMind` takes over so the character stays fully
interactive — and says plainly that it has no brain rather than pretending.

## Voice

Recording works out of the box (`sounddevice`, `numpy`). Turning it into text
needs one of:

1. `pip install faster-whisper` — local, no network, no per-request cost,
   handles Hindi and Marathi. **The right answer for the Pi.**
2. Any OpenAI-compatible `/audio/transcriptions` endpoint, using the key in
   `.env`.

With neither, it records and tells you it cannot hear yet.

Push-to-talk is the right first build because it removes every false-trigger
question while the character is being judged. On the Pi this becomes wake-word
or VAD driven — there is no keyboard in a living room.

## On the Pi

`pygame-ce` renders through SDL2, which uses KMSDRM to draw straight to the
framebuffer with no desktop, and reports touches as `FINGER*` events. The same
file runs on a Mac trackpad and a Pi touchscreen.

`fbcp-ili9341`, which most older Pi display guides point at, has been dead
since Feb 2024 (DispmanX, no Pi 5) — do not build on it.

Prefer an OLED panel: this character is glow-on-black and true black is most of
the effect. Burn-in on a static face is a months-to-years risk, which the idle
drift already mitigates.


## Studied from the reference expression sheet

Eight poses were added after studying a reference sheet of robot-face
expressions. Nothing in the existing character changed - no geometry, no
palette, no timing. What the sheet taught was four devices this face was not
using:

| Device | Where it came from | Where it is used here |
|---|---|---|
| The mouth may vanish entirely | its suspicious face has no mouth at all | `suspicious` (`mouth_alpha = 0`) |
| The mouth is a solid, not a line | its laugh is a wide filled slab, its gasp a tall filled dome - the same hole read two ways by proportion | `grin`, `oh`, `dread` |
| The eye may stop being an eye | anger is two straight bars, worry two chevrons - pure silhouette, no socket | `stern`, `fret`, `content` |
| Grief needs a prop | no lid arrangement says crying | `crying` (`tear`, `tear_fall`) |

The tear is the only new drawn element in the whole face, and the only float
with its own clock: it wells up over ~2 s, hangs, then falls and fades on a
4.6 s cycle. A tear frozen at one size is a sticker, not a tear.

Rule 2 at the top of `expressions.py` still holds - every one of the eight is
a silhouette no existing pose already used. `stern` is colder than `angry`
(bars, not an angled lid over a round eye); `fret` is the silhouette version
of `worried`; `content` is a held pose where `blink` is a 90 ms shutter;
`oh` is `surprised` with the eyes taken out of it.

38 expressions.


## Studied from the Jibo-family reference

A second reference sheet, and it works a different way. That family has **no
mouth at all** - not as one pose, as the whole design - and carries everything
on two devices:

| Device | Where it is used |
|---|---|
| **The half-disc.** One flat edge, one curved. Not a crescent (curved both edges) and not a bar (flat both). `lower_bend = 0` is what makes the lid edge flat. | `tender`, `alarmed`, `peek`, `drowsy` |
| **Tilt is the sentence.** With the mouth gone, the ANGLE of the pair does the work the mouth used to do. | `tender` vs `alarmed` |

`tender` and `alarmed` are the same two shapes with the tilt reversed, and
nothing else differs. That pair is the clearest demonstration in the whole
library that silhouette alone does not carry feeling - orientation does.

43 expressions.

## Lip sync: pronunciation

`pronounce.py` turns text into phonemes; `visemes.py` turns phonemes into
mouth shapes. The split matters because only the second half is solved.

Normalisation runs first and is **exact** - there is no ambiguity about how
"7:30" or "25" is read aloud:

    "I have 25 books"      -> I have twenty five books
    "call me at 7:30"      -> call me at seven thirty
    "Rs 1,250"             -> rupees one thousand two hundred fifty
    "the answer is 3.5"    -> the answer is three point five
    "50% off"              -> fifty percent off
    "in 1947"              -> in nineteen forty seven

Before this stage existed, numbers produced **no mouth movement at all** - the
face silently skipped whole words while the voice said them.

Then `lookup()` tries a lexicon of ~240 irregular high-frequency words, and
letter rules handle the rest. The right answer here is CMUdict (134k words,
the standard for this job); it is not installed, so the lexicon is hand-built
and covers where nearly all the error lives - English's irregular spellings
are concentrated in its commonest words. **`lookup()` is the seam: drop
CMUdict in and every word becomes exact without touching anything else.**

## Emotion fallback (optional)

`reading.read()` is rules first. Only when the rules find no cue (the line
would fall to a neutral face) is a small on-device model asked
(`fallback.py`): SamLowe/roberta-base-go_emotions-onnx, int8, ~122 MB,
28 emotion labels mapped to our expressions; below confidence 0.45 the face
stays neutral. English only: Devanagari and romanised Hindi/Marathi lines
are not sent to it (it misreads them; the rules handle those).

```bash
.venv/bin/pip install onnxruntime tokenizers huggingface_hub
.venv/bin/python -c "from huggingface_hub import hf_hub_download as d
[d('SamLowe/roberta-base-go_emotions-onnx', f, local_dir='todo-character/models/go-emotions')
 for f in ('onnx/config.json','onnx/tokenizer.json','onnx/model_quantized.onnx')]"
```

It loads once in a background thread at startup; the UI thread reads with
rules only and asks the model on a worker, applying its answer when it
arrives (~65 ms on a laptop, est. 0.3-0.5 s on a Pi 4). Override the path
with `HOMEBOT_EMOTION_MODEL=/path/to/onnx-dir`. If anything is missing, the
face silently runs on rules alone.
