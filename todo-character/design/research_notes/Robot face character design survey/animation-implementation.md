# Animation & Technical Implementation of Expressive Robot Faces

## Anki Vector / Cozmo: how the procedural eye system was built, and its parameters

### Takeaway
Cozmo/Vector eyes are a **procedural** (not sprite-based) system: a flat vector of **43 floats** — 5 global face params + 19 params per eye — drives a rounded-rectangle eye body with eight independent corner radii plus two deformable lids. Emotion presets are small deltas on that vector. The best-documented reimplementation is `pycozmo`, whose parameter layout is reverse-engineered from the real animation files; Anki's own official SDK never exposed the procedural params, only a raw framebuffer and eye hue.

### Cited Findings

**Parameter vector (pycozmo `procedural_face.py`, reverse-engineered from Cozmo animation data)**
- The face is "a flat list of 43 floats," sectioned by source comments into `# face parameters`, `# left eye parameters`, `# right eye parameters`; face = indices 0–4, left eye = 5–23 (19 values), right eye = 24–42 — [pycozmo procedural_face.py](https://raw.githubusercontent.com/zayfod/pycozmo/master/pycozmo/procedural_face.py)
- Face params (index: name, default): `0 center_x 0.0`, `1 center_y 0.0`, `2 scale_x 1.0`, `3 scale_y 1.0`, `4 angle 0.0` — [same](https://raw.githubusercontent.com/zayfod/pycozmo/master/pycozmo/procedural_face.py)
- Per-eye params (offset within eye: name, default):
  `+0 center_x 0.0`, `+1 center_y 0.0`, `+2 scale_x 1.0`, `+3 scale_y 1.0`, `+4 angle 0.0`,
  `+5 lower_inner_radius_x 0.5`, `+6 lower_inner_radius_y 0.5`, `+7 lower_outer_radius_x 0.5`, `+8 lower_outer_radius_y 0.5`,
  `+9 upper_inner_radius_x 0.5`, `+10 upper_inner_radius_y 0.5`, `+11 upper_outer_radius_x 0.5`, `+12 upper_outer_radius_y 0.5`,
  `+13 upper lid y 0.0`, `+14 upper lid angle 0.0`, `+15 upper lid bend 0.0`,
  `+16 lower lid y 0.0`, `+17 lower lid angle 0.0`, `+18 lower lid bend 0.0` — [same](https://raw.githubusercontent.com/zayfod/pycozmo/master/pycozmo/procedural_face.py)
- So each eye has **8 independent corner radii** (x and y for each of 4 corners, distinguished as inner/outer and upper/lower) — this is the mechanism for shape-based emotion, not pupils.
- Lid geometry: upper lid uses `y_offset = -half_eye_height`, `angle_offset = 0.0`; lower lid uses `y_offset = half_eye_height + 1`, `angle_offset = 180.0`. Each lid is a rectangle (half-width `1.2 * eye_width`) plus a chord (half-width `1.2 * half_eye_width`), drawn on a 2× canvas for antialiasing — [same](https://raw.githubusercontent.com/zayfod/pycozmo/master/pycozmo/procedural_face.py)
- Eye body construction: **five filled rectangles + four corner pie slices**, with `corner_radius = width/20 + height/10` (= 12.8 at default resolution). The eye is then rotated by `angle`, scaled by `scale_x`/`scale_y`, and pasted with offsets scaled by `X_FACTOR = 0.55`, `Y_FACTOR = 0.25` — [same](https://raw.githubusercontent.com/zayfod/pycozmo/master/pycozmo/procedural_face.py)
- Constants: `DEFAULT_WIDTH = 128`, `DEFAULT_HEIGHT = 64`, `DEFAULT_EYE_WIDTH = 28`, `DEFAULT_EYE_HEIGHT = 40`; output frames downsampled `np_im[::2]` → **128×32**; resampling `Image.Resampling.NEAREST` — [same](https://raw.githubusercontent.com/zayfod/pycozmo/master/pycozmo/procedural_face.py)
- Generator bounds: `MAX_X_OFFSET = 10.0`, `MAX_Y_OFFSET = 50.0`, `MAX_EYE_SCALE = 0.25`, `BLINK_SCALE_X = 15.0`, `BLINK_SCALE_Y = 0.01`; eye `center_x` nudged ±12; eye x-offsets ±`int(width/5)` (= ±25 at default) — [same](https://raw.githubusercontent.com/zayfod/pycozmo/master/pycozmo/procedural_face.py)
- The source defines **no valid ranges** for the 43 params themselves — only the generator constants above — [same](https://raw.githubusercontent.com/zayfod/pycozmo/master/pycozmo/procedural_face.py)
- Confirmation of the 43-param split (5 + 19 + 19) from the pycozmo issue tracker discussion — [Lightrun mirror of pycozmo procedural face rendering issue](https://lightrun.com/answers/zayfod-pycozmo-procedural-face-rendering)

**Named emotion presets (pycozmo `expressions` module — 25 classes, each a `ProceduralFace` subclass taking `params`, `width=128`, `height=64`)**
- Amazement, Anger, Annoyance, Asleep, Boredom, Confusion, Despair, Disappointment, Disgust, Embarrassment, Excitement, Fear, Fury, Guilt, Happiness, Horror, Neutral, Pleading, Rejection, Sadness, Skepticism, Surprise, Suspicion, Tiredness, Vulnerability — [pycozmo.expressions API docs](https://pycozmo.readthedocs.io/en/latest/generated/pycozmo.expressions.expressions.html)

**Squash/stretch and the exact shapes per emotion (pycozmo `expressions/expressions.py`)**
- **Happiness** — both eyes `upper_outer_radius_x = 1.0`, `upper_inner_radius_x = 1.0`; `lids[1].y = 0.4`, `lids[1].bend = 0.4`. (i.e. top corners fully rounded + lower lid raised and bowed = the classic "smiling eye" arc.)
- **Sadness** — `eyes[0].lids[0].y = 0.6, angle = 20.0`; `eyes[1].lids[0].y = 0.6, angle = -20.0` (upper lids drop 60% and tilt mirror-wise inward-down).
- **Anger** — `eyes[0].lids[0].y = 0.6, angle = -30.0`; `eyes[1].lids[0].y = 0.6, angle = 30.0` (same drop, **opposite** tilt sign to Sadness — the whole anger/sadness distinction is the sign of the lid angle).
- **Surprise** — both eyes `scale_x = 1.25`, `scale_y = 1.25` (pure uniform stretch, +25%).
- **Tiredness** — `eyes[0]: lids[0].angle = 5.0, lids[0].y = 0.4, lids[1].y = 0.5`; `eyes[1]: lids[0].angle = -5.0, lids[0].y = 0.4, lids[1].y = 0.5`.
- **Asleep** — both eyes `center_y = 50.0`, `lids[0].y = 0.45`, `lids[1].y = 0.5` (eyes driven down the screen and nearly fully occluded).
- **Amazement** — `lids[1].y = 0.2` both eyes.
- **Confusion** — asymmetric: `eyes[0].lids[1].y = 0.2, bend = 0.2`; `eyes[1].lids[0].angle = -10.0, y = 0.3`, `eyes[1].lids[1].angle = 5.0, y = 0.2, bend = 0.2`.
- All above — [pycozmo expressions.py](https://raw.githubusercontent.com/zayfod/pycozmo/master/pycozmo/expressions/expressions.py)

**Vector's official public SDK surface (screen, not eyes)**
- `SCREEN_WIDTH = 184`, `SCREEN_HEIGHT = 96`; docstring: "184 x 96 color pixels in RGB565 format", active area **23.2 mm × 12.1 mm** → 17,664 px / 35,328 bytes per frame — [anki_vector/screen.py](https://raw.githubusercontent.com/anki/vector-python-sdk/master/anki_vector/screen.py)
- Public API: `dimensions()`, `convert_pixels_to_screen_data(pixel_data, image_width, image_height)`, `convert_image_to_screen_data(pil_image)`, `ScreenComponent.set_screen_with_image_data(image_data, duration_sec, interrupt_running=True)`, `ScreenComponent.set_screen_to_color(solid_color, duration_sec, interrupt_running=True)`. `duration_sec` has no default and is converted via `int(1000 * duration_sec)` — [same](https://raw.githubusercontent.com/anki/vector-python-sdk/master/anki_vector/screen.py)
- **Licence: Apache 2.0**, © 2018 Anki, Inc. — [same](https://raw.githubusercontent.com/anki/vector-python-sdk/master/anki_vector/screen.py)

**Firmware-level console variables (community-reverse-engineered Vector docs)**
- `kProcFace_EllipseDelta` is an integer console variable with range **1 to 90**. There is an override mode where "each eyes parameters operate on their respective eye," and another where left-eye params drive both eyes; a display-type setting "overrides whatever faces we're sending" with the console-edited parameters — [randym32 Vector docs, Console variables](https://randym32.github.io/Anki.Vector.Documentation/software-design/Console%20variables.html)
- Animator-facing control axes documented: brow, gaze direction (L/R and U/D), cheeks, eye openness/closure (including squint and sleepiness), head tilt, and **squash and stretch (how close or far apart the eyes are)**. Animation files store eye settings the system **interpolates between**, and "the animation system moves each working parameter from frame to frame over a set time period." The animator tool likely mapped buttons onto "a couple dozen preset 'canned' eye patterns." A joystick-and-sliders tool exposed four simplified axes: worry↔curiosity, mad↔happy, blink rate (slow↔fast), gaze L↔R. "Blinking is handled by a timer plus some intermediate steps." The page states plainly: "The eye parameters in the animation files are very complex." — [randym32 Vector docs, Eye animation](https://randym32.github.io/Anki.Vector.Documentation/tools/Eye%20animation.html)

**The animation team and pipeline**
- Anki recruited **Carlos Baena** (ex-Pixar animator, *Toy Story 3*, *Finding Nemo*) in 2015; "The first task that they needed help with was trying to figure out Cozmo's eyes" — [designboom](https://www.designboom.com/technology/anki-cozmo-07-07-2016/); [Fortune](https://fortune.com/2016/06/27/anki-pixar-dreamworks-robot-games/)
- Baena headed Anki's animation team, which used **Maya** to author robot motion; Anki synced Cozmo's four motors to Maya through a custom workflow so animators saw movement on robot prototypes in real time — [Fortune](https://fortune.com/2016/06/27/anki-pixar-dreamworks-robot-games/); [TechCrunch](https://techcrunch.com/2016/06/27/cozmo/)
- Cozmo's eyes have **no pupils** and change shape to show mood; after a period of no interaction the eyes "morph into a little game of Pong" to signal boredom — [designboom](https://www.designboom.com/technology/anki-cozmo-07-07-2016/)
- GDC 2017 (Visual Arts track) session **"Cozmo: Animation Pipeline for a Physical Robot"**, speakers **Molly Jameson and Daria Jerjomina (Anki)**. Abstract notes Cozmo has 300+ parts; animators normally use exaggerated squash-and-stretch but "Anki used real world physics so there was no 'cheating'." Covers animator fast-iteration tools, test/debug scripts, mapping animation data onto physical movement, and **streaming audio + animation data to the robot** with programmatic corrections — [GDC Vault](https://www.gdcvault.com/play/1024488/Cozmo-Animation-Pipeline-for-a)

### Inferences
- The 184×96 display (23.2 × 12.1 mm — roughly a **postage-stamp**, ~8 px/mm) forces the eyes to be large, high-contrast, pupil-free shapes: at that physical size a pupil or iris would be a few pixels and read as noise. Shape-and-lid deformation is the only emotion channel with enough pixel budget, which is exactly what the 19-param-per-eye model encodes.
- The parameter model is essentially a **2D rig**: translate (center_x/y), squash/stretch (scale_x/y), rotate (angle), silhouette (8 corner radii), occlusion (2 lids × y/angle/bend). Any reimplementation can reproduce Vector-class expressiveness with exactly those 19 channels.
- Emotion encoding is extremely economical: most presets touch only **2–6 of the 19 channels**. Anger vs. Sadness differ only in the *sign* of the upper-lid angle. This is directly reusable: build a neutral base and express emotions as sparse deltas, then interpolate the whole 43-vector for transitions.
- Because Vector's official SDK only accepts full framebuffers, any SDK-level procedural face must be rendered host-side at 184×96 RGB565 and pushed as images with `duration_sec` — a per-frame cost of 35,328 bytes.

### Gaps
- No primary source found for Vector's or Cozmo's **face render frame rate**. pycozmo's renderer and the Vector console-variable docs do not state one; the GDC Vault abstract does not either.
- Vector's **named eye-colour presets** (as offered in the companion app) appeared only as an unfetched support-page link ([support.anki.bot article 413](https://support.anki.bot/article/413-changing-vectors-eye-color)); I did not verify the preset names or the `set_eye_color` hue/saturation signature, so they should not be stated as fact.
- Numeric **blink timing** for Vector/Cozmo is not documented in any source found — only the qualitative "timer plus some intermediate steps" and pycozmo's `BLINK_SCALE_X = 15.0 / BLINK_SCALE_Y = 0.01` shape scalars.
- Whether Carlos Baena himself presented at GDC/SIGGRAPH: **not confirmed**; the one located talk credits Jameson and Jerjomina. Ex-DreamWorks staffing on the team is referenced in press generally but I found no named source.
- pycozmo is a reverse-engineering effort, not Anki documentation. Parameter *names* are pycozmo's, and may not match Anki's internal identifiers.

---

## Jibo: how its animations were authored, and the single-eye design

### Takeaway
Jibo's expressive system is documented only thinly and mostly in video form. What is verifiable: a dedicated in-house animator (Fardad Faridi), a named-animation database addressed from the SDK via **Embodied Speech tags**, and a deliberate design where three independently-rotating body segments plus screen graphics, LEDs and sound form the "face" — the single ball-shaped eye was one element of a whole-body expressive vocabulary.

### Cited Findings
- Jibo's **Lead Designer & Animator was Fardad Faridi**; a Robohub post hosts his video explaining why the eye was designed as a ball and why Jibo has one eye rather than two. The *text* of the post only poses these questions — the reasoning is in the embedded video, which I could not access — [Robohub, "Developing Jibo: Animating the eye"](https://robohub.org/developing-jibo-animating-the-eye/)
- Jibo's animation system is described as "a sophisticated animated system" building on **more than a decade of research from Cynthia Breazeal's MIT Media Lab group** — [Robohub](https://robohub.org/jibos-coordinated-expression-mechanisms-behind-the-scenes)
- A development video hosted by **Jesse Gray & Matt Berlin (Team Jibo / MIT Media Lab)** covers how Jibo uses **movement, sound, LEDs, and screen graphics** together to convey emotion and intention — [Robohub, "Jibo's coordinated expression: mechanisms behind the scenes"](https://robohub.org/jibos-coordinated-expression-mechanisms-behind-the-scenes)
- SDK-level animation access: **Embodied Speech (`es`) tags** request an animation to be played, e.g. `<es name='Eye_Curious_01'/>`; there is an **animation database searchable by category** — [Jibo SDK, Embodied Speech Markup Language reference (PDF)](https://hri2024.jibo.media.mit.edu/attachments/SDK-SDK---ESML-121023-203758.pdf)
- Mechanical basis for expression: "By controlling the movement of each section independently Jibo was able to quickly snap into a variety of expressive poses"; the screen UI "worked with voice and movement to form its facial character" — [HUGE Design write-up, via Robohub "Designing Jibo"](https://robohub.org/designing-jibo-subtracting-the-obvious-and-add-the-meaningful/)
- HUGE Design credits Faridi: "Fardad Faridi, Jibo's talented in-house animator, introduced us to the basics of character expression in animation" — [same](https://robohub.org/designing-jibo-subtracting-the-obvious-and-add-the-meaningful/)
- Press described the display as containing "a single, blinking iris" that "winks, blinks, and even emotes," creating "the impression of a living being" — [HeroX, "Meet Jibo"](https://www.herox.com/blog/297-meet-jibo-the-worlds-first-social-family-robot)

### Inferences
- The `Eye_Curious_01` naming pattern (`Eye_<Emotion>_<NN>`) implies Jibo's expressive vocabulary was a **library of discrete named clips with numbered variants**, not a parametric rig like Vector's — i.e. authored-and-baked rather than procedural. Variant numbering is the standard anti-repetition device: pick randomly among `_01`, `_02`, … so the same emotion never plays identically twice.
- Because Jibo's eye is a single rendered ball with an iris (unlike Vector's pupil-less abstract shapes), its emotion channel leans on **gaze direction and body orientation** rather than on eye-silhouette deformation.
- Faridi's involvement before the industrial design was locked suggests the body's three-segment articulation was chosen partly *for* animation, the inverse of Anki's constraint (animators adapting to real physics).

### Gaps
- **No parameter list, timing numbers, frame rate, or screen resolution** for Jibo's face were found. The two most promising sources are videos whose audio I could not access, and Jibo's developer documentation site is defunct.
- No source found describing a system explicitly named "Jibo moves"; the SDK material located uses "Embodied Speech tags" and "animation database" instead. The report should not assert the "Jibo moves" name without verification.
- The rationale for the single eye is on record only in an inaccessible video — **do not state a reason** for the one-eye choice from these sources.

---

## Standard numbers for making a face feel alive: blink, saccade, idle motion, transitions

### Takeaway
Human spontaneous blink rate is ~14–17/min (one blink every ~3.5–4.3 s), and saccades last ~20–40 ms for typical amplitudes. Robot-face libraries land close to this: RoboEyes' default auto-blinker fires every **1–4 s** (random) and its idle re-gaze every **1–3 s**, with macro animations of **500 ms**.

### Cited Findings
**Human baselines**
- Most adults blink **about 14 to 17 times a minute** — [Cleveland Clinic, Blinking](https://my.clevelandclinic.org/health/body/blinking)
- A 2008 optoelectronic study of eyelid motion found women ~**19/min** vs men ~**11/min** — [Spontaneous blinking in healthy persons (PubMed 18565090)](https://pubmed.ncbi.nlm.nih.gov/18565090/)
- Blink rate collapses under focused tasks: ~**3–4/min** while reading; Cleveland Clinic reports a drop to ~**5/min** at a screen — [Cleveland Clinic](https://my.clevelandclinic.org/health/body/blinking)
- Saccades last **20–200 ms depending on amplitude**, with **20–30 ms typical in reading**; microsaccades ~**20 ms**; the largest saccades reach **up to 300 ms** — [Wikipedia, Saccade](https://en.wikipedia.org/wiki/Saccade)
- Reading saccades specifically **20–40 ms** — [Eye-movement feature extraction study (arXiv 1703.09167)](https://arxiv.org/pdf/1703.09167)
- Visual-search task mean saccade duration **36.6 ms (SD 14.4)** in young adults — [arXiv 2004.02873](https://arxiv.org/pdf/2004.02873)

**What a shipping robot-eye library actually uses (FluxGarage RoboEyes defaults)**
- Auto-blinker: `blinkInterval = 1` s, `blinkIntervalVariation = 4` s; effective delay `blinkInterval*1000 + random(blinkIntervalVariation)*1000` ms → **1 to 4 s** between blinks
- Idle mode (spontaneous re-gaze = the saccade analogue): `idleInterval = 1` s, `idleIntervalVariation = 3` s → **1 to 3 s** between repositions
- Macro animations: `confusedAnimationDuration = 500` ms (horizontal shake, amplitude 20), `laughAnimationDuration = 500` ms (vertical shake, amplitude 5)
- Micro-motion / jitter: `hFlickerAmplitude = 2` px, `vFlickerAmplitude = 10` px, exposed via `setHFlicker(bool, byte)` / `setVFlicker(bool, byte)`
- All — [FluxGarage_RoboEyes.h](https://raw.githubusercontent.com/FluxGarage/RoboEyes/main/src/FluxGarage_RoboEyes.h)
- Tutorial-documented usage: `roboEyes.setAutoblinker(ON, 3, 2)` — i.e. base 3 s + up to 2 s random — [SunFounder RoboEyes 1.0 tutorial](https://docs.sunfounder.com/projects/summary-of-fun-projects/en/latest/arduino/roboeyes1.0.html)

**Expression transition timing**
- Vector/Cozmo: "The animation system moves each working parameter from frame to frame over a set time period," interpolating between stored keyframe eye settings — [randym32 Vector docs, Eye animation](https://randym32.github.io/Anki.Vector.Documentation/tools/Eye%20animation.html)

### Inferences
- RoboEyes' 1–4 s blink window corresponds to **15–60 blinks/min**, skewed faster than human baseline. Mapping to the human 14–17/min means a base interval of ~3 s plus ~2 s variation — exactly what the SunFounder example (`ON, 3, 2`) uses. That is the number to copy for naturalism; the library default is deliberately livelier than human.
- The two-level structure (fixed base + random variation) is the reusable pattern for every idle timer: never a fixed period, or the face reads as a metronome.
- Since human saccades complete in 20–40 ms, a gaze shift at 50 fps (20 ms/frame) should be **1–2 frames**, essentially instantaneous — gaze should *snap*, while lid and shape changes *ease*. Smoothly tweening a gaze shift over many frames is the most common tell of an unconvincing robot eye.

### Gaps
- No documented **breathing-cycle** numbers for any of these robot faces. Human resting respiration (~12–20/min) is the obvious analogue but I found no source applying it to a robot face, so it should be flagged as an inference if used.
- No source found giving a numeric **duration for an emotion-to-emotion transition** in Vector/Cozmo or Jibo (the Vector docs say only "a set time period").
- No source found quantifying a **robot-specific recommended blink rate** from HRI literature; the RoboEyes defaults are library convention, not a research finding.

---

## Open-source robot face projects: parameter sets, frame rates, licences

### Takeaway
**FluxGarage RoboEyes** is the most directly reusable project and the most completely documented: a full parameter set, a 50 fps default, named moods and 8-way gaze — but it is **GPL-3.0**, which is a hard constraint for closed-source reuse. Adafruit's Uncanny Eyes is a photorealistic-eyeball renderer with a different parameter philosophy (iris/pupil/sclera), and its licence is not stated in the repo.

### Cited Findings

**FluxGarage RoboEyes (Arduino / Adafruit GFX OLED)**
- **Licence: GPL-3.0.** Current release `FluxGarage_RoboEyes-1.1.1.zip`, dated **2025-09-03**. Dependency: Adafruit GFX library — [Arduino Libraries index entry](https://www.arduinolibraries.info/libraries/flux-garage-robo-eyes); [GitHub](https://github.com/FluxGarage/RoboEyes)
- Construction: `RoboEyes<AdafruitDisplay>` template, `RoboEyes(AdafruitDisplay &disp)`; `begin(int width, int height, byte frameRate)` sets screen size, clears the display, **starts with eyes closed**, and calls `setFramerate(frameRate)`
- Frame rate: `setFramerate(byte fps)` sets `frameInterval = 1000/fps`; **default `frameInterval = 20`, i.e. 50 fps**. `update()` calls `drawEyes()` only when `millis()-fpsTimer >= frameInterval`
- Geometry setters: `setWidth(byte leftEye, byte rightEye)`, `setHeight(byte leftEye, byte rightEye)`, `setBorderradius(byte leftEye, byte rightEye)`, `setSpacebetween(int space)` (may be negative)
- Geometry defaults: `screenWidth = 128`, `screenHeight = 64`; `eyeL/RwidthDefault = 36`, `eyeL/RheightDefault = 36`, `eyeL/RheightCurrent = 1` (starts closed), `eyeL/RborderRadiusDefault = 8`, `spaceBetweenDefault = 10`, `eyelidsHeightMax = 18`, `eyelidsHappyBottomOffsetMax = 21`
- Mood constants: `DEFAULT = 0`, `TIRED = 1`, `ANGRY = 2`, `HAPPY = 3`, via `setMood(unsigned char)`
- Gaze constants: `N = 1, NE = 2, E = 3, SE = 4, S = 5, SW = 6, W = 7, NW = 8`, plus `DEFAULT` = middle centre, via `setPosition(unsigned char)`
- Behaviour toggles: `setAutoblinker(bool, int interval, int variation)`, `setIdleMode(bool, int interval, int variation)`, `setCuriosity(bool)`, `setCyclops(bool)` (**single-eye mode**), `setHFlicker`/`setVFlicker(bool, byte amplitude)`, `setSweat(bool)`, `setDisplayColors(uint8_t background, uint8_t main)`
- Basic animation: `close()`, `open()`, `blink()`, each with a `(bool left, bool right)` overload for winking
- Macro animation: `anim_confused()`, `anim_laugh()`
- Layout helpers: `getScreenConstraint_X()` = `screenWidth-eyeLwidthCurrent-spaceBetweenCurrent-eyeRwidthCurrent`; `getScreenConstraint_Y()` = `screenHeight-eyeLheightDefault`
- Internal state flags (all default 0): `tired, angry, happy, curious, cyclops, eyeL_open, eyeR_open, hFlicker, vFlicker, autoblinker, idle, confused, laugh, sweat`
- Colour constants: `BGCOLOR = 0`, `MAINCOLOR = 1`; sweat drawing constants `sweatBorderradius = 3`, `sweat1/2/3XPosInitial = 2`, `sweat1/2/3YPos = 2`
- All of the above — [FluxGarage_RoboEyes.h](https://raw.githubusercontent.com/FluxGarage/RoboEyes/main/src/FluxGarage_RoboEyes.h)
- A `ConfigurationBoard` example ships with the library (File → Examples → FluxGarage RoboEyes for OLED Displays) — [Instructables write-up by the author](https://www.instructables.com/Smoothly-Animated-Robot-Eyes-on-OLED-Displays-With)
- Older 1.0-era API usage, still widely copied: `setHeight(36, 36)`, `setBorderradius(8, 8)`, `setSpacebetween(10)`, `setMood(HAPPY|TIRED|ANGRY)`, `setPosition(W|N|S|E|DEFAULT)`, `anim_confused()`, `anim_laugh()` — [SunFounder tutorial](https://docs.sunfounder.com/projects/summary-of-fun-projects/en/latest/arduino/roboeyes1.0.html)

**Adafruit Uncanny Eyes (Teensy 3.x + SSD1351 OLED / ST7735 TFT)**
- Configuration is in `config.h`. Display selected by enabling exactly one of `Adafruit_SSD1351.h` (default) or `Adafruit_ST7735.h`
- Eye *appearance* comes from swappable header files — `defaultEye.h`, `noSclera.h`, `dragonEye.h`, `goatEye.h` — one enabled at a time; custom looks are made by generating new header files
- Parameters: `SYMMETRICAL_EYELID` (simpler eyelid shape, for single-eye builds); `eyeInfo_t` per eye (display-select pin, wink pin or `-1`, rotation 0–3); `DISPLAY_DC` / `DISPLAY_RESET`; `JOYSTICK_X_PIN` / `JOYSTICK_Y_PIN` (commented out by default → **autonomous eye movement**), `X_FLIP` / `Y_FLIP`; `TRACKING` (upper eyelid follows the pupil); `LIGHT_PIN`, `LIGHT_PIN_FLIP`, `LIGHT_MIN`, `LIGHT_MAX`; `IRIS_MIN` / `IRIS_MAX` (range 0–1023, pupil size in bright vs dark light); `IRIS_SMOOTH` (filters light input to reduce twitchiness at the cost of response speed); `BLINK_PIN` (manual blink, `-1` to disable)
- `AUTOBLINK` is enabled by default and "makes the eyes automatically blink randomly every few seconds"; manual and automatic blinking can be combined
- No frame rate stated; the guide recommends a **72 MHz** Teensy board speed over 96 MHz because of SPI behaviour, and with multiple eyes the software splits processing time between them
- All — [Adafruit Animated Electronic Eyes, Software page](https://learn.adafruit.com/animated-electronic-eyes/software)
- **Licence: not stated.** The repo's file list shows only `convert`, `uncannyEyes`, and `README.md`, with **no LICENSE file** and no licence field in the sidebar — [github.com/adafruit/Uncanny_Eyes](https://github.com/adafruit/Uncanny_Eyes)

**Reachy Mini (Pollen Robotics / Hugging Face)**
- Pollen Robotics states all designs, code and tools are open-source — [Hugging Face blog, Reachy Mini](https://huggingface.co/blog/reachy-mini)
- **The "eyes" are not displays.** A hands-on review reports they are 16 mm C-mount fisheye lenses over a camera, with "the actual 'eye' is a Raspberry Pi Camera Module 2"; the reviewer notes someone built a separate ESP32 project to light up the eye lenses — [Jeff Geerling, Testing Reachy Mini](https://www.jeffgeerling.com/blog/2026/testing-reachy-mini-hugging-face-robot/)
- Sources conflict: several outlets describe "expressive screen-based eyes" ([designboom](https://www.designboom.com/technology/programmable-desktop-robot-reachy-mini-open-source-pollen-robotics-07-15-2025/)) and Yanko Design says "LED eyes" ([Yanko Design](https://www.yankodesign.com/2025/07/15/open-source-robot-reachy-mini-brings-ai-to-your-desktop/amp/)) — **contradicted by** Geerling's hands-on finding that they are camera lenses. Treat the press descriptions as unreliable.
- Expressiveness therefore comes from motion: the Python SDK (plus a simulation SDK) ships ~15 behaviours for motions like waving and head turns — [Hugging Face blog](https://huggingface.co/blog/reachy-mini); [Reachy Mini docs](https://huggingface.co/docs/reachy_mini/index.md)
- A community "Reachy Mini Controllable Eyes" mod exists under the `reachy-mini` GitHub topic; licence unverified — [GitHub topic: reachy-mini](https://github.com/topics/reachy-mini)

**Other**
- `ggldnl/procedural-expression-library` appeared in search as a procedural-expression project; I did not fetch it and cannot describe its parameters or licence — [Ecosyste.ms listing](https://awesome.ecosyste.ms/projects/github.com%2Fggldnl%2Fprocedural-expression-library)
- An 8×8 LED matrix library exposes an `MD_RobotEyes` class, i.e. the same idea at extremely low resolution — [Soldered 8x8 MAX7219 Matrix library docs](https://solderedelectronics.github.io/Soldered-8x8-MAX7219-LED-Matrix-Arduino-Library/class_m_d___robot_eyes.html)

### Inferences
- RoboEyes and Vector/pycozmo converge on nearly the same parameter model — per-eye width, height, border radius, spacing, position, lids — which is strong evidence this is the *right minimal set* for an abstract robot eye. RoboEyes is the simplified version (one border radius per eye vs Vector's eight; four moods vs 25 presets).
- **Licensing is the main reuse hazard**: RoboEyes is GPL-3.0, so linking it into a closed product is not viable — its *parameter design* is freely imitable, its *code* is not. Anki's `vector-python-sdk` is Apache-2.0 and safe to vendor; Uncanny Eyes has no declared licence, which is the worst case (no grant at all, despite being published by Adafruit, who normally use MIT/BSD) — permission would have to be confirmed.
- RoboEyes starting with `eyeHeightCurrent = 1` (closed) means every boot is an opening-eyes "waking up" beat. Cheap and worth copying.

### Gaps
- No licence declared for Adafruit Uncanny Eyes; could not confirm terms.
- No frame rate documented for Uncanny Eyes.
- Did not inspect `ggldnl/procedural-expression-library` or the Reachy Mini community eye mod; parameters and licences unknown.

---

## Frame rate: what these faces run at, and the minimum that reads as smooth

### Takeaway
The one hard, documented number is RoboEyes' **50 fps default** (`frameInterval = 20` ms), user-settable via `begin(width, height, frameRate)`. I found **no sourced threshold** for the minimum frame rate at which a robot face reads as smooth.

### Cited Findings
- RoboEyes: `frameInterval = 20` by default → **50 fps**; `setFramerate(byte fps)` computes `frameInterval = 1000/fps`; `begin()` takes `byte frameRate` as its third argument, so the rate is a first-class configuration knob; `update()` is a non-blocking gate on `millis()-fpsTimer >= frameInterval` — [FluxGarage_RoboEyes.h](https://raw.githubusercontent.com/FluxGarage/RoboEyes/main/src/FluxGarage_RoboEyes.h)
- The library's own framing is that the result is "smoothly animated robot eyes" at these defaults — [Instructables](https://www.instructables.com/Smoothly-Animated-Robot-Eyes-on-OLED-Displays-With)
- Uncanny Eyes: no frame rate stated; the guide notes performance depends on SPI/board clock (72 MHz preferred) and that multiple eyes split processing time — [Adafruit software page](https://learn.adafruit.com/animated-electronic-eyes/software)
- Vector's own display is 184×96 RGB565, so each pushed frame is 35,328 bytes — a bandwidth figure that bounds any SDK-driven animation rate — [anki_vector/screen.py](https://raw.githubusercontent.com/anki/vector-python-sdk/master/anki_vector/screen.py)
- pycozmo emits face frames at **128×32** after `np_im[::2]` downsampling, using nearest-neighbour resampling — [procedural_face.py](https://raw.githubusercontent.com/zayfod/pycozmo/master/pycozmo/procedural_face.py)

### Inferences
- 50 fps on an SSD1306 I²C OLED is an *aspiration*, not a guarantee: at 128×64 over I²C the transfer alone typically dominates. The `millis()`-gated `update()` design means the library degrades gracefully to whatever the bus allows rather than stuttering.
- Given that a human saccade is 20–40 ms and a blink is on the order of 100–150 ms, a 20 ms frame budget (50 fps) resolves a blink into ~5–8 frames — about the minimum for a blink to read as motion rather than a flicker. A face at 20–25 fps would render a blink in 2–3 frames and likely read as a glitch, which is the practical argument for staying at or above ~30 fps. **This is reasoning from the blink/saccade numbers, not a sourced finding.**

### Gaps
- **No source found** stating a minimum acceptable frame rate for robot faces, nor any perceptual study on the question. Any number in the report on this should be presented as an inference from blink/saccade durations, not as documented.
- Vector's and Cozmo's actual on-device face frame rates remain undocumented in everything I could reach.

---

## Indicating speech on a face with no mouth

### Takeaway
There is no documented "eye lip-sync" technique in the sources I could reach. The research literature's answer is different and better evidenced: a mouthless robot signals speech through **co-speech indicators matched to its body** — head and whole-body movement, lights, and rhythm keyed to the dialogue — rather than by animating the face.

### Cited Findings
- A puppetry-principles paper addresses exactly this: how a puppet without a mouth still shows it is speaking. Puppeteers held that movement should follow "the emotion, the listener, and the rhythm of the dialogue," and that the speech cue can come from the **head or whole body** instead of a mouth. The paper's design guideline is that robots should **pair speech with co-speech indicators suited to their body shape**. It notes non-humanoid robots have signalled speech with **lights and whole-body movement**, and that whole-body movement helped people identify **which robot in a group was talking** — [Invisible Strings: Deriving Puppetry Principles and their Hidden Connections to Robot Behavior Design (arXiv 2607.03289)](https://arxiv.org/pdf/2607.03289)
- Jibo's documented approach is consistent with this: it "uses movement, sound, LEDs, and screen graphics to communicate with people and convey emotion and intention," with the screen UI working together with voice and movement — [Robohub](https://robohub.org/jibos-coordinated-expression-mechanisms-behind-the-scenes); [Robohub, Designing Jibo](https://robohub.org/designing-jibo-subtracting-the-obvious-and-add-the-meaningful/)
- Jibo's SDK binds animation to speech structurally: **Embodied Speech tags inline animation requests into the utterance** (`<es name='Eye_Curious_01'/>`), so gesture is authored in the same stream as the words — [Jibo ESML reference (PDF)](https://hri2024.jibo.media.mit.edu/attachments/SDK-SDK---ESML-121023-203758.pdf)
- Anki's pipeline streamed **audio and animation data together** to the robot — [GDC Vault, Cozmo: Animation Pipeline for a Physical Robot](https://www.gdcvault.com/play/1024488/Cozmo-Animation-Pipeline-for-a)
- For contrast, the mouthed approach: companion-robot patents describe an eyes-nose-mouth display animated in sync with speech, driven by **phoneme mouth shapes**, eye gaze and eyebrow position, plus gestural cues such as turning the head away at a topic change — and note the robot "does not need a head at all" — [US 10,661,433, Companion robot for personal interaction](https://image-ppubs.uspto.gov/dirsearch-public/print/downloadPdf/10661433)

### Inferences
- The reusable mechanism is **inline markup**: Jibo's ESML and Anki's co-streamed audio+animation are the same architecture — the speech stream carries animation cues, so expression is authored by writers alongside dialogue rather than generated from the audio signal. For a mouthless face this is the practical substitute for lip-sync: tag the utterance, don't analyse the waveform.
- Mapping the puppetry guideline ("rhythm of the dialogue", co-speech indicators suited to the body) onto an eyes-only screen suggests driving a subtle eye-scale or lid oscillation from speech envelope/prosody, and/or a body/head nod per stressed syllable — but **no source I found documents such an implementation**, so this must be presented as a design proposal, not practice.

### Gaps
- **Found no reliable source** on eye-only speaking cues — pulsing eyes, lid oscillation keyed to amplitude, or any eye-based "lip-sync" substitute. This is a genuine hole in the literature as far as my searches reached, and the report should say so rather than imply such a technique is standard.
- No documentation found for how Vector specifically indicated that it was speaking (it has no mouth and a largely non-verbal voice).
