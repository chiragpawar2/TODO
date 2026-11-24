# The "No Face" Camp: Abstract Presence in Voice Assistants, and the Automotive Divergence Toward Faces

Scope note: this researcher covered the faceless/abstract pole (smart speakers, phone assistants), the in-car category that converged on faces, the Japanese maximalist pole (Gatebox), and the trust/privacy/expectation evidence. A recurring and important finding is that **the major faceless platforms have published almost no explicit "we rejected a face" rationale** — the one well-documented explicit rejection comes from Mercedes-Benz, and the best-documented explicit *adoption* rationale comes from NIO. That asymmetry is itself a finding.

## How Alexa, Siri, Google Assistant, Cortana and Bixby express state WITHOUT a face — the exact visual vocabulary

### Takeaway
Each faceless assistant encodes state in a **single abstract geometric primitive** (ring, orb, dot cluster) modulated on three axes only: hue, motion type, and directionality. Amazon's is the most formally specified and the only one with a published state table; Bixby's is the least documented.

### Cited Findings

**Amazon Alexa — light ring (the most complete published vocabulary).** Amazon's own Alexa brand guidelines specify the states, naming colors only (no hex/RGB values given) — [Amazon Alexa Brand Guidelines: Light Ring](https://developer.amazon.com/en-US/alexa/branding/alexa-guidelines/brand-guidelines/light-ring):
- Primary states, all blue: **Listening** = blue, directional (moving around the ring, toward the speech source); **Thinking** = blue, alternating (shown after speech ends, before the response); **Responding** = blue, pulsing (screened devices show no ring during responses).
- Secondary states: **Setup** = orange, cycling; **Microphone muted** = red, solid/steady; **Notification** = yellow, pulsing; **Incoming call** = green, pulsing; **Active call** = green, cycling; **Volume** = white, contextual; **Error** = purple, quick pulsing; **Do Not Disturb** = purple, slow pulsing; **Away mode** = white, cycling.
- The only stated design guidance on the page is "Depict the device as accurately as possible," plus an instruction to show the correct indicator for listening/thinking/responding. **No rationale for the color or motion choices is given.** — [Amazon](https://developer.amazon.com/en-US/alexa/branding/alexa-guidelines/brand-guidelines/light-ring)
- Third-party documentation corroborates the same mapping (spinning orange during setup/no internet, solid red = mic off, pulsing yellow = waiting notification, spinning green = active call/Drop In, purple flash = Do Not Disturb) — [PCWorld](https://www.pcworld.com/article/578763/what-flashing-lights-on-amazon-echo-speaker-mean.html)
- **Patent:** Amazon Technologies holds US9786294B1, "Visual indication of an operational state," covering a voice-controlled device that lights indicators in a particular pattern to convey its operational state, including transition from an inactive to an active state after detecting sound — [Google Patents US9786294B1](https://patents.google.com/patent/US9786294B1). (Only abstract/figure-level summary was reviewed; exact claim scope unverified.)
- A related filing, EP 3437329 A4, covers an indicator for a personal assistant application's state, but the applicant could not be confirmed from the index entry — [EPO Global Patent Index](https://data.epo.org/gpi/EP3437329A4). **Treat the Amazon attribution of this second one as unverified.**
- The directional-listening behavior is functionally significant: hobbyist documentation notes the ring lights toward the voice source, which is effectively a gaze cue without eyes — [Adafruit](https://blog.adafruit.com/2020/06/19/making-a-spooky-alexa-mask-alexa-arduino/)

**Apple Siri — orb/glow, which has migrated across three form factors.**
- Current generation (iOS 27): the glowing animation around the device bezels is gone, replaced by "a floating dark orb made out of Liquid Glass" — [MacStories, iOS and iPadOS 27 Review](https://www.macstories.net/stories/ios-and-ipados-27-review/5/)
- On iPhone, Siri now appears as a glowing **pill-shaped** orb expanding directly out of the Dynamic Island; reporting attributes the pill (rather than circular) shape to the hardware constraint of the current Dynamic Island, with a circle possible on iPhone 18 — [MacRumors](https://www.macrumors.com/2026/06/16/iphone-18-could-make-siri-a-circle/)
- On Vision Pro, Siri is a glass orb with a glowing waveform inside — described by designer Ben Geskin as "too impersonal," which motivated his concept adding a Finder-style face to a gradient orb — [Yanko Design](https://www.yankodesign.com/2025/09/02/siri-gets-a-dedicated-avatar-in-vision-pro-thanks-to-this-ui-concept/); [BetaNews](https://betanews.com/article/this-stunning-apple-vision-pro-concept-brings-siri-to-life/)
- Siri was historically characterized as visually "detached and aloof" relative to Cortana's emotive ring — [PCWorld](https://www.pcworld.com/article/431767/cortanas-ui-now-expresses-18-different-emotions-siri-remains-detached-and-aloof.html)

**Google Assistant — four dots.**
- The four dots communicate what the Assistant is doing: ready, listening, thinking, talking; they hover and bounce depending on what you ask — [Made By Google design review, Medium](https://medium.com/brand-marketing-blog/made-by-google-design-review-f30d16dd0bca)
- Google's creative director framed motion as the carrier of meaning: the way the dots move communicates more than just a dot pattern — [same source](https://medium.com/brand-marketing-blog/made-by-google-design-review-f30d16dd0bca)
- The dots derive from Google's 2015 identity update, intended as "a dynamic distillation of the logotype for interactive, assistive, and transitional moments" — [Designboom](https://www.designboom.com/design/new-google-logo-09-01-2015/)
- **Google previously shipped a face and removed it:** voice search once displayed an animation of a bodyless face talking; it was replaced with dots that morph into vertical lines, a change reviewers welcomed — [PhoneArena](https://www.phonearena.com/news/google-voice-and-song-search-get-ai-based-makeover_id175654)
- The now-ubiquitous "AI sparkle" icon was inspired by the negative space between the Google Assistant dots — [Google Design](https://design.google/library/ai-sparkle-icon-research-pozos-schmidt)

**Microsoft Cortana — ring.** This is the one case with a direct designer statement on choosing abstraction over a character:
- Microsoft chose a small animated circle rather than a holographic character like the Halo one — [The Register](https://www.theregister.com/2015/02/11/cortana_details_windows_10/)
- Program manager **Marcus Ash** said the team "settled pretty quickly on the idea of a simple geometric shape" — [The Register](https://www.theregister.com/2015/02/11/cortana_details_windows_10/); see also [TechCrunch](https://techcrunch.com/2014/03/03/microsofts-cortana-gets-a-sneak-preview-looks-like-a-circle-and-will-call-you-whatever-you-want/)
- The ring nonetheless carried an unusually large emotional range: PCWorld reported the UI expressed **18 different moods**, built from ring variations (e.g., a lighter ring outside a darker one) — and noted that many of them looked nearly identical — [PCWorld](https://www.pcworld.com/article/431767/cortanas-ui-now-expresses-18-different-emotions-siri-remains-detached-and-aloof.html); corroborated by [Poppastring](https://www.poppastring.com/blog/cortana-has-emotions)
- Early Windows Phone 8.1 builds showed the blue ring logo turning into a bouncy ball on tap — [Neowin](https://www.neowin.net/news/new-animations-and-features-spotted-in-cortana/)

**Samsung Bixby.** I found **no reliable documentation of Bixby's state-animation vocabulary.** The only sourced design fact located: Bixby's original logo was designed by Samsung with design firm Pentagram — [Wikipedia: Bixby (software)](https://en.wikipedia.org/wiki/Bixby_(software)). This is a genuine gap.

### Inferences
- The shared grammar across all five is: **one shape, hue = category of event, motion = process stage, direction = spatial attention.** A face would occupy the same communicative channels but add involuntary signals (gaze, expression valence) that designers cannot fully control or localize.
- Cortana's 18 near-indistinguishable moods is evidence that an abstract primitive has a low expressive ceiling: past roughly 6–8 states, viewers cannot discriminate. This is the strongest functional argument *for* a face, and it comes from the faceless camp's own implementation.
- Google's removal of a talking-face voice-search animation in favor of dots is the closest thing to a documented face→abstraction retreat at a major platform.

### Gaps
- Bixby's state vocabulary (colors, motions, meanings) — not documented in accessible sources.
- Exact hex/RGB values for Alexa's ring states — Amazon publishes color names only.
- Full claim scope of US9786294B1 and whether EP 3437329 is Amazon's.

## What designers at these companies have publicly said about avoiding a face

### Takeaway
**This is largely an evidentiary void, and the report should say so plainly.** Repeated targeted searching found no Amazon or Apple statement explaining the absence of a face. Microsoft (Cortana) and Google (persona/naming) offer partial rationale. The only crisp, quotable rejection of a face by a major company comes from **Mercedes-Benz**, in the automotive category.

### Cited Findings
- **Microsoft, Cortana:** program manager Marcus Ash — the team "settled pretty quickly on the idea of a simple geometric shape," chosen over a holographic Halo-style character — [The Register](https://www.theregister.com/2015/02/11/cortana_details_windows_10/)
- **Google, persona level (not visual):** the Assistant team weighed a matter-of-fact "oracle" framing against a more characterful persona and concluded users should not mistake it for a person; they rejected a human name in favor of "Google Assistant" as more approachable across cultures and as a way to avoid associating it with a single gender — [Variety, 2019](https://variety.com/2019/digital/features/google-assistant-name-personality-voice-technology-design-1203340223/) (fetch of the full article was blocked by a paywall redirect; findings are from search-surfaced excerpts and should be re-verified against the original before quoting verbatim)
- **Google design guidance:** all voices project a persona whether or not you plan for one — [Google Design, UI & UX Principles for Voice Assistants](https://design.google/library/speaking-the-same-language-vui)
- **Amazon:** the available designer-level commentary concerns *voice and persona*, not facelessness — e.g., a voice designer describing wanting friendly, human-like traits without users developing a relationship as if with a real person — [Forbes](https://www.forbes.com/sites/startupnationcentral/2018/11/15/meet-the-voice-designer-helping-amazons-alexa-be-part-of-your-family/); Amazon's Smart Home head reportedly cited research that a woman's voice is perceived as "more sympathetic" — [TechRadar](https://www.techradar.com/news/the-problem-with-alexa-whats-the-solution-to-sexist-voice-assistants)
- **Mercedes-Benz, the explicit rejection.** CTO and board member **Markus Schäfer** at CES 2024: "Once, we thought we were going to have a face looking at you." Internal studies killed it: "Some people like it, but quite a lot more people dislike the human face." The chosen alternative is "a 'star cloud' that somehow represents something like a human being, but it's not a face." — [InsideEVs](https://insideevs.com/news/704386/mercedes-ai-human-face/)
- HCI literature treats facelessness as the unmarked default rather than a headline decision — a CHI 2019 paper uses Google Assistant simply as an example of a voice assistant with no face — [CHI 2019, "Hey Google, Can I Ask You Something in Private?"](http://library.usc.edu.ph/ACM/CHI2019/1proc/paper258.pdf)

### Inferences
- The absence of published rationale suggests facelessness at Amazon/Apple/Google was **not a deliberated rejection of a face but a default inherited from product category** (a speaker, a phone OS layer) — the design energy went into voice persona, name and gender, which is where all the public discourse sits.
- Mercedes is the useful data point for a designer weighing the choice because it is the one case where a face was prototyped, user-tested, and killed on evidence — and the stated reason was **net negative affect**, not expectation management.
- Mercedes' chosen compromise ("represents something like a human being, but it's not a face") names a distinct third option between face and pure abstraction: an *anthropomorphic-but-featureless presence*.

### Gaps
- No Amazon or Apple primary source on the no-face decision. This likely requires ACM/industrial-design archives, Echo industrial-design oral histories, or Apple HIG/keynote material not surfaced by web search.
- Mercedes' internal study methodology, sample, and metrics are not published — only Schäfer's characterization.

## In-car assistants that chose a face, and why cars went this direction

### Takeaway
Cars converged on faces for reasons specific to the cabin: the driver's eyes are occupied, the vehicle is a semi-private "companion" space on long journeys, and a physical/visual agent appears to reduce rather than increase cognitive load. Chinese and Japanese OEMs went furthest; German OEMs split, with Mercedes explicitly backing away from a human face and BMW/MINI using a light-sphere or a non-human character.

### Cited Findings

**NIO NOMI — physical rotating round-screen face (the most documented case).**
- Form: a ball-shaped head with a circular display; eye and head animation is manga-inspired; industrial design settled on a minimalist approach — [Star Global case study](https://star.global/cases/nio-nomi/); [CnEVPost](https://cnevpost.com/2021/03/30/what-is-nomi-heres-everything-you-need-to-know/)
- **Deliberately mouthless.** NIO found adding a mouth made matching voice to mouth movement harder, and the mouthless form "more harmonious and reasonable." NIO's engineers reasoned explicitly about the uncanny valley — rendered in the source as the "Valley of Terror": people are drawn to AI resembling humans, but as resemblance grows, subtle differences make people fearful — [CnEVPost](https://cnevpost.com/2021/03/30/what-is-nomi-heres-everything-you-need-to-know/)
- **Face integrity as a design rule:** NIO treated the face as analogous to a person's face whose integrity cannot be broken, and therefore refused to overlay functional prompts on it — specifically rejecting a fatigue-detection teacup icon — [CnEVPost](https://cnevpost.com/2021/03/30/what-is-nomi-heres-everything-you-need-to-know/)
- **Gaze and motion behavior:** NOMI turns its face toward someone opening the door and greets them; when a user reaches for the center screen it lowers its head to see what they want, then raises it when the hand withdraws — [CnEVPost](https://cnevpost.com/2021/03/30/what-is-nomi-heres-everything-you-need-to-know/)
- **Emotion engine architecture:** links the vehicle gateway, the car's main system, an emotion library, and the screen's motor drivers to coordinate expression, voice and subtle movement; NIO described synchronizing all three as harder than syncing voice with on-screen text — [CnEVPost](https://cnevpost.com/2021/03/30/what-is-nomi-heres-everything-you-need-to-know/)
- Expression style is minimalist emoji-like symbols; default is a happy face, with an occasional **red angry face** used as a reminder for poor driving habits — [CnEVPost](https://cnevpost.com/2021/03/30/what-is-nomi-heres-everything-you-need-to-know/)
- Stated intent, from a NIO designer: the team "wanted the system to feel alive, and to feel part of the car, so we came up with this head and face for the vehicle" — [just-auto interview](https://www.just-auto.com/interview/sit-down-we-need-to-talk-facetime-with-nio/)
- Animation was sourced from film/animation craft so movements are "not simply robotic and mechanical, but driven by emotions," which required custom hardware (motors, belts) for very small movements — [just-auto](https://www.just-auto.com/interview/sit-down-we-need-to-talk-facetime-with-nio/)
- Design brief from co-design partner Star: make NOMI appear both premium (to match the car) and appealing (to charm the user) — [Star Global](https://star.global/cases/nio-nomi/)
- Hardware/history: development began 2015; from 2015–2018 NOMI was designed to communicate mainly through expressions and simple sounds; debuted on the ES8 in 2017; NOMI Mate first, NOMI Halo (2018) used a round car-grade AMOLED screen plus a halo; purely circular exterior, megapixel screen, minimalist industrial design intended to resist obsolescence — [CnEVPost](https://cnevpost.com/2021/03/30/what-is-nomi-heres-everything-you-need-to-know/)
- Won a **2020 Red Dot Design Award**, with jury praise for its likeable, expressive animated face — [Star Global](https://star.global/cases/nio-nomi/)
- Name is pronounced like "Know Me," reflecting its purpose — [CnEVPost](https://cnevpost.com/2021/03/30/what-is-nomi-heres-everything-you-need-to-know/)

**Mercedes MBUX — a face prototyped and rejected; glowing star instead.**
- The MBUX Virtual Assistant is a "'living' star avatar" using animations to express different moods and states of being, with avatar colors representing the assistant's emotions — [Mercedes-Benz Media](https://media.mbusa.com/releases/release-ebe78e1e0abb0f8a2f173a4032054126-mercedes-benz-heralds-a-new-era-for-the-user-interface-with-human-like-virtual-assistant-powered-by-generative-ai)
- Visually, a glowing three-pointed star that changes colors and animations based on how the driver interacts with it; Mercedes says it senses the driver's mood from various factors and responds with "empathy" — [InsideEVs](https://insideevs.com/news/704386/mercedes-ai-human-face/)
- Mercedes nonetheless *showed* a humanlike avatar forming from a condensing star cloud, plus a second avatar nicknamed **"Little Benz"** with an expressive face intended for a stronger personal connection — [Mercedes-Benz Media, CES 2024](https://media.mbusa.com/releases/release-0e178e07b0fab83c4ebb38fc7d1f7e0e-mercedes-benz-presents-vision-of-hyper-personalised-user-experience-at-ces-2024)
- Rejection rationale and Schäfer quotes: see previous section — [InsideEVs](https://insideevs.com/news/704386/mercedes-ai-human-face/)

**BMW / MINI.**
- Older coverage describes BMW's Intelligent Personal Assistant visual as "spheres of light in differing sizes and brightness levels," said to give it "a 'face' with a clearly visible point of focus and identifiable states of activity via gestures." **Caveat: this source's date metadata was unreliable and it appears to predate the 2026 system** — [LinkedIn commentary, Sam Livingstone](https://www.linkedin.com/pulse/in-car-virtual-assistant-avatar-presents-huge-design-sam-livingstone)
- **MINI** uses a non-human character: a "digital character" in the form of a dog named **Spike** as its in-car AI assistant — [InsideEVs](https://insideevs.com/news/704386/mercedes-ai-human-face/); [BMW Group Press, MINI Intelligent Personal Assistant avatar](https://www.press.bmwgroup.com/ireland/photo/detail/P90513930/MINI-Intelligent-Personal-Assistant-MINI-Avatar)
- 2026 state of play: BMW demoed the AI-powered Intelligent Personal Assistant with Alexa+ technology on the iX3 at CES 2026; rollout from H2 2026 in Germany and the US, then across models on BMW Operating System 9 and X — [BMW Group Press, CES 2026](https://www.press.bmwgroup.com/global/article/detail/T0454649EN/the-bmw-ix3-ushers-in-next-generation-innovations-at-ces-2026?language=en); [Automotive Interiors World](https://www.automotiveinteriorsworld.com/news/personal-assistants/bmw-ix3-debuts-next-gen-ai-assistant-at-ces-2026.html)
- The China-market Neue Klasse IPA (with Alibaba) is described as having "an expressive avatar, emotional voice modulation, and empathetic persona," without visual detail — [BMWBlog](https://www.bmwblog.com/2025/03/26/bmw-idrive-x-alibaba-ai-china-neue-klasse/)

**Toyota Kirobo Mini.**
- A palm-sized (~10 cm) companion robot sold through Toyota dealerships in Japan; handles casual conversation, reads facial expressions, remembers likes/dislikes and places visited together; can link with compatible cars to bring journey details into the chat — [Toyota Canada](https://www.toyota.ca/toyota/en/connect/340/how-this-toyota-robot-detects-your-emotions); [TechRadar](https://www.techradar.com/news/world-of-tech/toyota-has-created-a-tiny-robot-designed-to-tug-at-your-heartstrings-1329814)
- Priced around ¥39,800 with a ~¥300/month companion-app fee; descends from Kirobo, which flew to the ISS — [Origin of Bots](https://www.originofbots.com/robot/kirobo-mini-by-toyota-details-specifications-rating); [Silicon Republic](https://www.siliconrepublic.com/machines/kirobo-mini-japan-robot-companion-toyota)
- Coverage frames it explicitly as an emotional/loneliness product — "designed to tug at your heartstrings" — [TechRadar](https://www.techradar.com/news/world-of-tech/toyota-has-created-a-tiny-robot-designed-to-tug-at-your-heartstrings-1329814); [IBTimes](https://www.ibtimes.co.uk/toyota-unveils-baby-robot-aging-japan-help-childless-women-experience-maternal-instinct-1584487)

**Honda NeuV.**
- A boxy electric commuting concept with an "emotion engine," using SoftBank AI, aiming to "enable machines to artificially generate their own emotions"; intended to hold dialogue with the driver based on the car's own emotional state. Time framed it as Honda's first effort to put the technology inside a vehicle and as revealing of Japanese attitudes toward AI — [Time](https://time.com/4602600/honda-car-emotional-ai-artifical-intelligence-neuv/)

**Other dashboard-robot precedents cited in the HCI literature** — [Li et al., arXiv:2402.11853v2](https://arxiv.org/html/2402.11853v2):
- Williams et al. (2013), **AIDA**, used the driver's own smartphone as the robot's face and improved sociability versus the smartphone alone.
- Karatas et al. (2016), **NAMIDA**, reduced system-induced attention overload.
- Tanaka et al. (2020): a dashboard robot (**Robohon**) was well accepted, caused minimal distraction, and improved driving behavior.
- Wang et al. (2021): a **Nao** robot in simulated autonomous driving increased likability, perceived warmth and competence, and reduced workload.
- Zihsler et al. (2016) studied trust in self-driving cars using human-like robot heads.

### Inferences
- The automotive convergence on faces is best explained by three cabin-specific conditions, each with at least partial empirical support in the sources: (1) the driver's visual channel is committed to the road, so a peripheral, glanceable *social* object offloads work from the auditory channel (NOMI reduced auditory workload, p < .001 in non-driving tests — [Li et al.](https://arxiv.org/html/2402.11853v2)); (2) journeys are long and solitary, making companionship a product feature rather than a side effect (Kirobo Mini, NeuV); (3) the car is already a bounded, personally owned space, so the privacy objection that dogs home speakers is weaker.
- NOMI's two most transferable design rules for any face designer: **remove the mouth** (eliminates lip-sync failure, a chief uncanny-valley trigger) and **treat the face as inviolable** (never composite status icons onto it). Both are explicitly reasoned, not incidental.
- The German/Chinese split maps onto the trust evidence rather than onto taste: Mercedes' research found a human face net-disliked, while NIO's face is cartoon-abstract and mouthless. The sources are consistent with the view that **cartoon/non-human faces survive user testing and photoreal human faces do not.** MINI's dog and Mercedes' star are both retreats from human likeness, not from character.

### Gaps
- The definitive NIO designer interview at [automotiveinteriorsworld.com](https://www.automotiveinteriorsworld.com/features/exclusive-interview-adding-the-human-touch-nios-nomi-mate-ai.html) returned HTTP 403 and could not be read; its quotes are only partially available via search excerpts.
- No current (2026) description of BMW's Intelligent Personal Assistant avatar visuals was found; the light-sphere description is from undated, probably older commentary.
- Whether Honda NeuV reached production is not established by the sources found.
- Most NIO and Mercedes rationale is company-supplied (interviews, press, agency case studies), so it reflects their own framing.

## Gatebox and the Japanese maximalist opposite pole

### Takeaway
Gatebox represents the far end of the spectrum: not a face as a state indicator but a full fictional character with a biography, projected as a hologram, explicitly engineered for emotional attachment and marketed to a loneliness-adjacent audience. It demonstrates that the face/abstraction axis is really a *relationship-intensity* axis.

### Cited Findings
- Gatebox is an Echo-like voice-powered home assistant in which an anime character, **Azuma Hikari**, is projected inside a glass tube — [Digital Trends](https://www.digitaltrends.com/home/gatebox-azuma-hikari-virtual-assistant-news/)
- Functionally it overlaps with a smart speaker (wakes you, turns on lights when you come home) but adds unprompted outbound contact: she sends text messages throughout the day via Gatebox's native chat app, recognizes her "master's" voice, and learns his sleeping habits — [Digital Trends](https://www.digitaltrends.com/home/gatebox-azuma-hikari-virtual-assistant-news/); [Vice](https://www.vice.com/en/article/this-holographic-anime-character-could-be-your-next-girlfriend/)
- Attachment is the explicit design goal: the more the owner speaks to her, the more she learns about their life and can offer "a sense of emotional, albeit virtual, support"; the maker framed her as the user's ideal wife after further updates — [Vice](https://www.vice.com/en/article/this-holographic-anime-character-could-be-your-next-girlfriend/); [Futurism](https://futurism.com/this-is-the-holographic-ai-servant-of-your-dreams-or-maybe-your-nightmares)
- Target audience and the accompanying criticism: described as designed specifically for *otaku*, and commentary linked it to young people in Japan avoiding relationships — [Tech Times](https://www.techtimes.com/articles/189322/20161219/gatebox-virtual-assistant-is-the-holographic-anime-companion-for-lonely-people-can-it-compete-with-amazon-echo.htm); [ISPR](https://ispr.info/2017/03/09/japanese-companys-answer-to-amazon-echo-anime-holograms-with-comforting-personalities-for-the-lonely/)
- Capability honesty problem at launch: Japanese only, and "she is still learning," her language skills growing — the capability was far below what the character implied — [Digital Trends](https://www.digitaltrends.com/home/gatebox-azuma-hikari-virtual-assistant-news/)
- Original price roughly US$2,500–2,700; a later **Gatebox Grande** used a 65-inch 4K OLED and was repositioned for larger applications such as a digital concierge — [Hypebeast](https://hypebeast.com/2021/3/gatebox-grande-anime-hologram-store-guides-news)
- An academic analysis exists treating Gatebox as assistive-technology companion — [ResearchGate](https://www.researchgate.net/publication/332081893_GATEBOX_-_An_analysis_on_assistive_technology_companion) (abstract-level only)

### Inferences
- Gatebox's pivot from the bedroom "wife" product to the Grande digital concierge is consistent with the maximalist character strategy being commercially narrow: a strong character fixes the product to one relationship and one audience, whereas a light ring is audience-neutral. This is a real cost of a face that rarely appears in design discussion.
- Gatebox is the clearest illustration of the over-promise risk: a fully realized character with a biography, paired with Japanese-only, limited-turn conversation.

### Gaps
- No current (2025–2026) information found on whether Gatebox is still sold or supported.
- Coverage is almost entirely 2016–2017 tech journalism; no peer-reviewed user study of Gatebox attachment outcomes was located.

## Documented evidence on trust, privacy perception and attachment: faced vs faceless

### Takeaway
The strongest direct evidence — a within-subjects study that covered and uncovered NIO's NOMI — shows a face substantially increases trust, warmth, engagement, and *reduces* measured stress and workload. But the sample is tiny, the context is a car rather than a home, and the privacy literature points the other way for always-listening home devices: anthropomorphism is associated with higher privacy concern in reviews and with *reduced* privacy vigilance via social presence. There is no study I found that directly tests faced vs faceless smart speakers on privacy comfort.

### Cited Findings

**Direct faced/faceless comparison (in-car).** Li et al. tested NOMI with 10 participants in China, running each task with NOMI visible and with NOMI covered by a blanket — [arXiv:2402.11853v2](https://arxiv.org/html/2402.11853v2):
- **Trust** in the assistant's responses rose from **2.6 to 4.3** with NOMI visible (paired t-test, p < .001).
- **Warmth** (1–5): **5.0** with NOMI, **3.3** without, **2.9** for other in-car VAs. Agreeableness: 5.0 / 3.9 / 3.7. Neuroticism and conscientiousness barely moved, which the authors attribute to voice being unchanged.
- With NOMI covered, the assistant's personality scores fell close to those of generic VAs — the authors suggest a robot's personality is hard to convey when voice and appearance don't match.
- **Stress** fell 2.1 → 1.6 (p = .015); **mental workload** 2.3 → 1.6 (p = .045); **interference** 2.9 → 2.5 (p = .037); auditory workload showed no significant on-road change but dropped in non-driving tests, mainly offline (p < .001).
- **Engagement** rose 1.6 → 3.0 on-road (p < .001).
- Qualitative attachment: participants described companionship and reduced loneliness; one said, "It's like having a pet or a child that won't bother you." Some reported forming an attachment only once they could picture the assistant.
- **Counter-currents in the same study:** some participants worried NOMI could distract drivers and create road-safety risks (the authors link this to Lee et al. 2001).
- **Authors' own caveats:** n=10, single country, Mandarin only, self-reported ratings, NOMI's facial expressions not controlled, **and some p-values in the text do not match the tables** — so the specific numbers should be verified against the published version before being quoted as definitive.

**Familiarity reverses the effect.** Cheng et al. (2022): drivers *familiar* with their in-car infotainment system trusted a highly anthropomorphic robot assistant **less** than unfamiliar drivers did — cited in [Li et al.](https://arxiv.org/html/2402.11853v2)

**Voice alone already raises trust (so some of the "face" effect may be anthropomorphism in general).** CHI 2024, Cohn et al., "Believing Anthropomorphism": adding a computer-generated voice increases both perceived anthropomorphism of LLMs and trust that the information they provide is accurate — [arXiv:2405.06079](https://arxiv.org/pdf/2405.06079). The paper does not address privacy.

**Privacy: anthropomorphism cuts both ways.**
- A systematic review of smart-speaker privacy reports that information sensitivity and anthropomorphism significantly impact user privacy concerns — [Privacy in smart speakers: A systematic literature review](https://www.researchgate.net/publication/364443596_Privacy_in_smart_speakers_A_systematic_literature_review)
- Voice interaction creates a sense of social presence that "could lead to a neglect of privacy," and users frequently conflate the intelligent assistant with the device — [Privacy and smart speakers: A multi-dimensional approach](https://www.tandfonline.com/doi/full/10.1080/01972243.2021.1897914)
- A review of conversational-agent studies found higher perceived anthropomorphism and fewer privacy concerns were linked to higher information disclosure — [arXiv:2406.09037](https://arxiv.org/pdf/2406.09037)
- A PLOS-indexed study found anthropomorphism and informativeness can **mitigate** perceived risks of AI voice assistants, reducing innovation resistance — [PMC11978003](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC11978003/)
- Conversely, a 2025 *Cyberpsychology* study found persuasion-literacy training improved recognition of persuasive attempts by intelligent voice assistants **while reducing** anthropomorphic perceptions and trust in them — i.e., anthropomorphism and critical scrutiny trade off — [Cyberpsychology](https://cyberpsychology.eu/article/view/39538)
- The always-listening microphone is the specific trigger: in a CSCW study, many users with no prior privacy concerns became more worried after learning about the always-listening feature — [Lau, Zimmerman & Schaub, CSCW 2018, "Alexa, Are You Listening?"](https://dl.acm.org/doi/10.1145/3274371) ([PDF](https://www.key4biz.it/wp-content/uploads/2018/11/cscw102-lau-1.pdf))
- **Conflicting baseline:** one study reports smart-speaker privacy concerns are generally quite low; another finds users express few concerns but their rationalizations indicate incomplete understanding of the risks — suggesting low stated concern reflects limited awareness rather than genuine comfort — [Privacy Attitudes of Smart Speaker Users](https://www.researchgate.net/publication/336184996_Privacy_Attitudes_of_Smart_Speaker_Users); [Lau et al. CSCW 2018](https://dl.acm.org/doi/10.1145/3274371)
- Relationship formation and trust are empirically linked: survey work finds people do develop socially-natured relationships with voice assistants, linked to trust in devices, trust in manufacturers, and anthropomorphism — [Seymour & Van Kleek, arXiv:2108.01923](https://arxiv.org/pdf/2108.01923)
- Social behaviors short of a face already drive disclosure: Alexa backchanneling ("mm-hm") elicited more self-disclosure and improved user experience — [arXiv:2204.10191](https://arxiv.org/pdf/2204.10191)

**Non-face faced-agent comparisons.** Pollmann et al. (2020): a Pepper robot made a game feel more entertaining than a voice assistant did, while **voice-performance ratings stayed unchanged** — cited in [Li et al.](https://arxiv.org/html/2402.11853v2)

### Inferences
- The honest synthesis for a designer: **a face reliably buys affect (warmth, engagement, companionship, subjective trust) without buying any perceived improvement in actual competence or voice performance** (Pollmann et al.; the "Do I Sound as Capable as I Look?" result below). The gain is relational, not functional.
- On privacy the evidence supports a **two-sided mechanism**: anthropomorphism lowers *felt* risk and raises disclosure (PLOS/arXiv review), which makes users more comfortable — but that comfort is a reduction in vigilance rather than a reduction in actual risk, and the Cyberpsychology training study shows the comfort disappears once users are taught to scrutinize. A designer adding a face to an always-listening home device is therefore trading informed consent for comfort, which is an ethical exposure as much as a UX decision.
- Cheng et al.'s familiarity reversal and Li et al.'s "experienced VA users were less impressed" both suggest **the face premium decays with expertise** — it is strongest at first contact and on naive users.
- Mercedes' finding (human face net-disliked) and NOMI's success (cartoon mouthless face loved) are not contradictory: they bracket the uncanny valley from either side.

### Gaps
- **No study found that directly tests faced vs faceless *smart speakers* on privacy comfort in the home.** All the direct faced/faceless manipulation evidence is automotive. This is the single biggest evidentiary hole for the report's central question.
- Mercedes' internal study is unpublished.
- The Seymour & Van Kleek paper's publication venue could not be confirmed; do not attribute it to CHI.

## What happens to expectations when you add a face — does it over-promise intelligence?

### Takeaway
Yes, and this is the best-theorized cost of a face. The literature formalizes it as the **Social Robot Expectation Gap** (and Komatsu et al.'s "adaptation gap"): humanlike appearance inflates capability expectations independent of actual capability, and the resulting disconfirmation produces frustration and reduced trust. The standard prescribed remedy is literally a less humanlike appearance.

### Cited Findings
- Komatsu et al. (2012) is the origin cited for the **adaptation gap**: for robots with a human-like appearance, overly high expectations of characteristics and capabilities relative to actual functions create an expectation gap; humanlike appearance attributes humanlike qualities regardless of the robot's actual capabilities — cited in [Li et al., arXiv:2402.11853v2](https://arxiv.org/html/2402.11853v2) and in [What did you expect? A human-centered approach to investigating and reducing the social robot expectation gap](https://www.researchgate.net/publication/377463551_What_did_you_expect_A_human-centered_approach_to_investigating_and_reducing_the_social_robot_expectation_gap)
- The gap is formalized as an evaluation framework: when human expectations do not match robot capabilities, disconfirmed expectations occur; the "gap" indicates the distance between users' expectations and the robot's capabilities — [Applying the Social Robot Expectation Gap Evaluation Framework](https://www.researchgate.net/publication/372224050_Applying_the_Social_Robot_Expectation_Gap_Evaluation_Framework)
- Consequence: any gap between a user's expectations and the reality of a robot's capability can result in frustration and reduced trust — [same framework literature](https://www.researchgate.net/publication/377463551_What_did_you_expect_A_human-centered_approach_to_investigating_and_reducing_the_social_robot_expectation_gap)
- **Prescribed remedy is appearance restraint:** one way to decrease the gap "is to use less humanlike robot appearances" — [ibid.](https://www.researchgate.net/publication/377463551_What_did_you_expect_A_human-centered_approach_to_investigating_and_reducing_the_social_robot_expectation_gap); see also [Warning: This Robot is Not What it Seems!](https://www.researchgate.net/publication/340366871_Warning_This_Robot_is_Not_What_it_Seems_Exploring_Expectation_Discrepancy_Resulting_from_Robot_Design)
- **An important contrary result:** a recent study found robot-like appearance and semantic-free utterances were **not** significantly associated with perceived competency or agency, contrary to expectation — [Do I Sound as Capable as I Look? Impact of Robot Communication Style and Appearance on User Perception, ACM](https://dl.acm.org/doi/10.1145/3717511.3749305). This weakens the strong form of the appearance→expectation claim.
- Related recent work on the expectation/experience mismatch in social HRI — ["Take Nothing on Its Look": Revealing Users' Expectations and Experiences in Social Human–Robot Interaction](https://doi.org/10.1145/3772070)
- Minimalism as a design doctrine within the face camp: Karatas et al. (2023) favor minimal designs that keep only expressive anthropomorphic elements — cited in [Li et al.](https://arxiv.org/html/2402.11853v2)
- **Observed in the field:** in the NOMI study, nearly all participants said the robot-equipped assistant met or exceeded expectations, but **experienced VA users were less impressed** — one dismissed it as "essentially the MBUX assistant with a robot face." Requested improvements were all capability, not appearance: emotional responsiveness, multi-turn dialogue, memory, more varied tone. Offline operation hurt the experience **even with NOMI present**, i.e., the face did not compensate for failed capability — [arXiv:2402.11853v2](https://arxiv.org/html/2402.11853v2)
- Cortana's 18 near-identical moods is the mirror-image failure: abstraction under-promises and under-delivers discriminable information — [PCWorld](https://www.pcworld.com/article/431767/cortanas-ui-now-expresses-18-different-emotions-siri-remains-detached-and-aloof.html)

### Inferences
- The decisive design variable is not face/no-face but **where on the human-likeness scale the face sits.** Both successful face cases in this research (NOMI, MINI's Spike) are non-human or deliberately incomplete (mouthless, animal), and both rejected cases (Mercedes' human avatar, Gatebox's full-biography character) are high human-likeness. Karatas et al.'s "keep only the expressive elements" is the operative rule.
- The NOMI offline finding is the most practically useful single data point for the trade-off: **a face amplifies both success and failure.** It makes a working assistant feel like a companion and a broken one feel like a disappointing companion, which is worse than a broken light ring.
- A coherent decision rule the report could offer: choose abstraction when the device is always-listening in a shared private space, when capability is uneven or degrades offline, when the product must serve many audiences and cultures, and when the state set is small (≤6–8 states). Choose a face when the user's visual attention is otherwise committed, when companionship is an explicit product value, when the relationship is single-user and long-duration, and when the face can be kept cartoon-abstract and mouthless.

### Gaps
- Komatsu et al. (2012) was not read in the original; all characterizations are second-hand through citing papers.
- No longitudinal study found on whether the face-driven trust premium persists past initial novelty (Cheng et al. and the "experienced users less impressed" finding are suggestive but not longitudinal).
- No quantitative evidence found on the expressive ceiling of abstract indicators (the Cortana 18-mood problem is journalistic observation, not a measured discrimination study).
