# Commercial Home / Desk / Social Robots With an On-Screen or Projected Character Face — Product Landscape

> Scope note from the researcher: this survey was conducted under a tight tool-call budget. Products below are grouped into (A) facts verified against cited sources in this session, and (B) products in the assignment brief that I could NOT verify in this session and that are therefore listed explicitly as gaps rather than filled in from memory. Nothing in the Cited Findings sections is written from recollection — every line carries a URL.

## Q1: The catalogue — company, country, year, status, price, face hardware, face content

### Takeaway
Verified-face products cluster hard around one pattern: **two animated eyes on a small emissive display, with no mouth**. Of the products whose face content I could verify in this session, eyes-only designs (Anki Vector, Anki Cozmo, Mayfield Kuri, Sony aibo, Groove X LOVOT, Amazon Astro, LG Q9, Reachy Mini) outnumber full-face / mouth-bearing designs (Embodied Moxie) by roughly 8:1. Only Samsung Ballie uses projection, and notably it projects *content*, not a face.

### Cited Findings

**Anki Vector (Anki, USA; 2018; discontinued after Anki's 2019 shutdown; relaunched by Digital Dream Labs)**
- Face is a small color display at **184 x 96 pixels** showing cartoon eyes — [Slashdot/Fast Company](https://hardware.slashdot.org/story/18/08/08/2212241/ankis-new-robot-has-artificial-emotional-intelligence); [The Gadgeteer review](https://the-gadgeteer.com/2018/12/31/anki-vector-robot-review/)
- Panel technology is **contested in the press**: Gadgeteer, TechHive and Gear Patrol describe a 184x96 **IPS** color display, while Tom's Guide and Trusted Reviews call it **OLED** — [TechHive](https://www.techhive.com/article/3329938/anki-vector-robot-review.html); contradicted by [Tom's Guide](https://www.tomsguide.com/us/anki-vector,review-5891.html) and [Trusted Reviews](https://www.trustedreviews.com/reviews/anki-vector)
- Face content: **two pixelated eyes/pupils only, no mouth**; the eyes light up/react when the camera recognises a face, and eye colour was user-selectable in the app — [The Gadgeteer](https://the-gadgeteer.com/2018/12/31/anki-vector-robot-review/)
- The face panel is a user-replaceable part ("LCD Facial Display"), per iFixit's repair guide — [iFixit](https://ts.ifixit.com/Guide/Anki+Vector+LCD+Facial+Display+Replacement/123278)
- An API was to expose the face as a general full-colour screen to developers — [Tom's Hardware](https://www.tomshardware.com/uk/news/anki-vector-price-hands-on-release,37562.html)

**Vector's successor — Vector 2.0 (Digital Dream Labs, USA; international release Oct 2022; $399.99)**
- Digital Dream Labs **bought Anki's assets in 2020** and announced the international release of Vector 2.0 in **October 2022**, at **$399.99 plus a SaaS subscription**, with an optional mobile app — [Robotics 24/7](https://www.robotics247.com/article/digital_dream_labs_ships_upgraded_vector_2_0_social_robot)
- Upgrade is a **2 MP camera** improving facial-expression recognition; facial data stored locally on the robot, never uploaded to cloud; optional **Escape Pod ($99)** add-on enables local-only operation — [Robotics 24/7](https://www.robotics247.com/article/digital_dream_labs_ships_upgraded_vector_2_0_social_robot)

**Anki Cozmo (Anki, USA; 2016; discontinued 2019)**
- Face is an **OLED display used as a face** — [Wikipedia: Cozmo](https://en.wikipedia.org/wiki/Cozmo)
- Animation and expression design was **led by animator Carlos Baena**, previously a Pixar animator — [Wikipedia: Cozmo](https://en.wikipedia.org/wiki/Cozmo); Baena worked on *Toy Story 3* and *WALL-E* — [Fortune](https://fortune.com/2016/06/27/anki-pixar-dreamworks-robot-games/)
- Note: the brief's name "Carlos Pedro Reyes" does not match; the documented animator is **Carlos Baena** — [Wikipedia: Cozmo](https://en.wikipedia.org/wiki/Cozmo)
- Eyes-only idle behaviour: if left alone, **the eyes morph into a game of Pong** — [Fortune](https://fortune.com/2016/06/27/anki-pixar-dreamworks-robot-games/)

**Jibo (Jibo Inc., USA; 2017; dead 2019; $899)**
- Priced at **$899**; Amazon's Echo undercut it by nearly $700, and Chinese knockoffs appeared by 2016 — [The Robot Report](https://www.therobotreport.com/jibo-social-robot-analyzing-what-went-wrong/)
- Cancelled international orders in 2016; Indiegogo offered full refunds for unfulfilled orders — [The Robot Report](https://www.therobotreport.com/jibo-social-robot-analyzing-what-went-wrong/)
- **Withdrew its business registration in November 2018** and sold its technology to **SQN Venture Partners** — [The Robot Report](https://www.therobotreport.com/jibo-social-robot-analyzing-what-went-wrong/)
- Servers shut down in 2019; the robot delivered its own farewell message and did a last dance; "Hey Jibo" still worked but other voice commands did not — [Yahoo Tech](https://tech.yahoo.com/general/article/2019-03-04-social-robot-jibo-shutting-down-message.html); [IEEE Spectrum](https://spectrum.ieee.org/jibo-is-probably-totally-dead-now)
- Design commentary: Jibo **over-engineered its motion to seem more human, to offset its non-human look**; a former employee said the company explored downgrading the motor system — [The Robot Report](https://www.therobotreport.com/jibo-social-robot-analyzing-what-went-wrong/)

**Mayfield Kuri (Mayfield Robotics / Bosch-backed, USA; announced CES 2017 at $700; cancelled July 2018; company closed 31 Oct 2018)**
- **This is the strongest documented "eyes only, deliberately" case in the whole landscape.** The designers' stated rationale: *"We realized that if Kuri had a screen, and the screen showed anything other than eyes, Kuri would break character and become an object."* — [IEEE Spectrum](https://spectrum.ieee.org/mayfield-robotics-announces-kuri-a-700-mobile-home-robot)
- Consequence of that rule: besides the eyes and a colour-changing chest light, Kuri had **no general display**; it communicated through beeps plus expressive head and eye motion — [IEEE Spectrum](https://spectrum.ieee.org/mayfield-robotics-announces-kuri-a-700-mobile-home-robot)
- The **camera was hidden behind the left eye**, deliberately placed to be hard to see — [IEEE Spectrum](https://spectrum.ieee.org/mayfield-robotics-announces-kuri-a-700-mobile-home-robot)
- Eyes used for state signalling: a voice command put Kuri to rest, after which **he closes his eyes and dozes off** — [IEEE Spectrum](https://spectrum.ieee.org/mayfield-robotics-announces-kuri-a-700-mobile-home-robot)
- Price **$700** at CES 2017 announcement — [IEEE Spectrum](https://spectrum.ieee.org/mayfield-robotics-announces-kuri-a-700-mobile-home-robot); production halted July 2018 with refunds offered to all buyers, shipped or not — [TechCrunch](https://techcrunch.com/2018/07/25/mayfield-robotics-ceases-production-of-kuri-robot-amid-a-questionable-future); company shut down 31 October 2018 — [Engadget](https://www.engadget.com/2018/08/22/kuri-robot-creator-mayfield-robotics-to-shut-down/)
- Press framing at launch: "like an Amazon Echo designed by Pixar" — [TechCrunch](https://techcrunch.com/2017/01/03/home-robot-kuri-is-like-an-amazon-echo-designed-by-pixar/)

**Sony aibo ERS-1000 (Sony, Japan; Japan 11 Jan 2018, US Sept 2018; still in market)**
- Eyes are **two OLED displays**, which give the appearance of blinking and closing and support a range of expressions — [Sony press release](https://sony.mediaroom.com/2018-08-23-Sony-Announces-Limited-First-Litter-Edition-Release-of-aibo-in-U-S); the OLED eyes can follow the owner around the room — [IEEE Spectrum](https://spectrum.ieee.org/sony-advanced-aibo-robot-dog-unleashed)
- **Eyes only — no screen mouth** (mouth is physical dog geometry) — [Sony press release](https://sony.mediaroom.com/2018-08-23-Sony-Announces-Limited-First-Litter-Edition-Release-of-aibo-in-U-S)
- Japan price **¥198,000 (~$1,736)** from 11 Jan 2018 — [TechCrunch](https://techcrunch.com/2018/08/23/sonys-adorable-new-aibo-comes-to-the-us-in-sept-priced-at-2899); US SRP **$2,899** incl. charging station, toys and three years of AI Cloud service — [Engadget](https://www.engadget.com/2018-08-23-sony-aibo-us-launch.html)

**Groove X LOVOT (Groove X, Japan; 2018 announce / 2019 ship; shipping, now 3rd generation)**
- Eyes are built from **six stacked 2D display layers** forming iris and pupil, enabling depth and sustained eye contact / returned gaze — [Japan Gov Online (Highlighting Japan)](https://gov-online.go.jp/eng/publicity/book/hlj/html/202106/202106_10_en.html); "six layers of projections to create an impression of depth" — [designboom](https://designboom.com/?p=560016)
- **Eyes only, no mouth** on the display — [Japan Gov Online](https://gov-online.go.jp/eng/publicity/book/hlj/html/202106/202106_10_en.html)
- Industrial design credited to **Kota Nezu** (znug design) in Japanese trade press — [MONOist](https://monoist.itmedia.co.jp/mn/articles/1812/19/news059_2.html)
- Pricing by generation: 2018 expectation **~$3,000** plus **~$90/month** subscription — [Tom's Hardware](https://www.tomshardware.com/news/lovot-groove-x-social-robot-pet%2C38353.html), [designboom](https://designboom.com/?p=560016); **LOVOT 2.0 (2022): ¥349,800** + monthly service fee — [Impress Watch](https://www.watch.impress.co.jp/docs/news/1412150.html); **LOVOT 3.0 (May 2024): ¥577,500**, monthly running cost from **¥9,900** — [PC Watch](https://pc.watch.impress.co.jp/docs/news/1596287.html)
- Critical reception was not uniformly warm — Gizmodo's headline framing was "as cute as it is soulless" — [Gizmodo](https://gizmodo.com/this-japanese-robot-is-as-cute-as-it-is-soulless-1831228466)

**Amazon Astro (Amazon, USA; home version Sept 2021 Day 1 Edition; business version Nov 2023, killed July 2024)**
- Face is a **10.1-inch HD touchscreen, 1280 x 800**, with depth sensors and two red night-vision LEDs — [ReviewGeek](https://www.reviewgeek.com/134037/amazon-astro-review/)
- Face content: **two eyes that wink and blink, no mouth**; combined with screen movement they make Astro seem less like a surveillance camera on wheels — [Tom's Guide](https://www.tomsguide.com/news/amazon-astro)
- The screen **rotates/tilts around the body** to face you but is locked in landscape — [TechAdvisor](https://www.techadvisor.com/article/744829/amazon-astro-everything-you-need-to-know-about-the-smart-home-robot.html); it turns the screen in the direction of travel before moving — [Yahoo Tech](https://tech.yahoo.com/home/articles/amazons-astro-might-not-save-120000069.html)
- **Documented face-design criticism:** TechCrunch judged Astro's eyes **less expressive than Anki's Cozmo**, which had ex-Pixar and DreamWorks animators — [TechCrunch](https://techcrunch.com/?p=2208839). A reviewer noted the **eyes disappear whenever Alexa responds**, leaving a standard Echo screen, which broke the character illusion — [review via BusinessGhana](https://businessghana.com/site/news/technology/264104/Amazon-Astro-review-too-much-Alexa-not-enough-arms)
- The face doubles as an Echo Show 10 equivalent (video calls, streaming, smart home) — [ReviewGeek](https://www.reviewgeek.com/134037/amazon-astro-review/)
- **Astro for Business** launched Nov 2023, discontinued announcement July 2024, support ended **25 September 2024**; Amazon said it wanted to "accelerate our progress... to make Astro the best in-home robot" — [TechCrunch](https://techcrunch.com/2024/07/03/amazon-discontinues-astro-for-business-security-robot); [Engadget](https://www.engadget.com/amazon-pulls-the-plug-on-the-business-version-of-its-astro-robot-193907015.html). Home Astro was explicitly **not** affected at that time — [TechSpot forum/report](https://www.techspot.com/community/topics/amazon-shuts-down-its-astro-business-robot-with-an-eye-on-expanding-the-household-version.286743/)

**Embodied Moxie (Embodied Inc., USA; 2020–2021; dead December 2024; $799–$1,200)**
- **The main mouth-bearing exception.** Moxie had a **human-like animated face capable of a range of human-like emotions** (i.e. full cartoon face, not eyes-only) and maintained eye contact with children — [Axios](https://www.axios.com/2024/12/10/moxie-kids-robot-shuts-down); [Popular Science](https://www.popsci.com/technology/moxie-robot-offline/)
- Price **$799** for the robot — [Gizmodo](https://gizmodo.com/moxies-799-robot-companion-for-children-is-going-to-die-2000536581); other coverage cites a **$1,200** all-in figure — [inkl](https://inkl.com/news/a-1-200-ai-powered-robot-for-autistic-kids-is-going-to-die-because-its-maker-is-going-under)
- Shut down Dec 2024 after a **critical funding round fell through**; robots were expected to stop functioning **within days** because core features were cloud-dependent — [Axios](https://www.axios.com/2024/12/10/moxie-kids-robot-shuts-down)

**LG "Q9" / CLoi AI agent (LG, South Korea; shown CES 2024)**
- **Expresses emotion through digital eyes on its screen** — [Tom's Guide](https://tomsguide.com/news/the-new-samsung-ballie-robot-wows-at-ces-2024-an-ai-companion-with-a-built-in-projector)
- LG's head of home appliances said they gave it a **walking (two-legged) form rather than rolling, because a rolling design would make "sympathizing" hard to achieve** — i.e. an explicit anthropomorphism-over-utility design argument — [Tom's Guide](https://tomsguide.com/news/the-new-samsung-ballie-robot-wows-at-ces-2024-an-ai-companion-with-a-built-in-projector)

**Samsung Ballie (Samsung, South Korea; concept 2020, re-launched CES 2024, CES 2025; ship date repeatedly slipped)**
- **The projection case — and it is NOT a projected face.** Ballie is bowling-ball-sized with spatial LiDAR and a **1080p projector** used to show movies, video calls and greetings on nearby surfaces, aimed at floor, wall or ceiling based on viewer position — [Engadget](https://www.engadget.com/samsungs-ballie-robot-ball-showed-up-at-ces-2024-with-a-new-look-and-a-built-in-projector-224231693.html); [designboom](https://www.designboom.com/technology/samsung-ballie-ai-robot-ces-2024-01-09-2024/)
- At CES 2025 described as the "world's first switchable lens projector", able to throw near (floor) or far (wall); **no price was given in the presentation** — [BGR](https://bgr.com/tech/samsungs-ballie-might-be-the-coolest-ai-robot-we-see-at-ces-2025)
- Samsung has said it expects to ship Ballie "later this year" — [Digital Trends](https://www.digitaltrends.com/home/samsung-ballie-release-date-ces-2025/)

**Hugging Face / Pollen Robotics Reachy Mini (France/USA; announced July 2025; shipping)**
- Launch pricing **$299 Lite / $449 Wireless** (July 2025) — [TechCrunch](https://techcrunch.com/2025/07/09/hugging-face-opens-up-orders-for-its-reachy-mini-desktop-robots); current listed pricing on Hugging Face's and Pollen's own pages is **$399 Lite / $499 Wireless** (wireless includes onboard compute, Wi-Fi, battery), ~90-day delivery — [Hugging Face blog](https://huggingface.co/blog/reachy-mini); [Pollen Robotics](https://pollen-robotics.com/reachy-mini/blog/reachy-mini-announcement/)
- Face is **screen-based animated eyes that blink** (reported in Chinese-language launch coverage; eye detail is thin) — [iThome](https://www.ithome.com.tw/news/169983)

**MIXI Romi (MIXI, Japan; Romi since ~2021; "Romi Lacatan" model a CES 2025 Innovation Award honoree; shipping)**
- Romi **Lacatan**: **¥89,800** base (**¥98,780** incl. tax) plus membership **¥1,780/month** (**¥1,958** incl. tax) — [Business Insider Japan](https://www.businessinsider.jp/article/2507-mixi-new-ai-talking-robot/?page=2)
- CES 2025 Innovation Awards honoree; adds AI features including the ability to see and talk about its surroundings — [CES](https://ces.tech/innovation-awards/2025/conversational-ai-robot-romi); [Notebookcheck](https://www.notebookcheck.net/Mixi-Romi-Lacatan-conversational-AI-robot-selected-as-CES-Innovation-Awards-Honoree.933279.0.html)
- A limited **Hello Kitty edition**, 150 units, released 1 November, **¥88,000** — [Business Insider Japan](https://www.businessinsider.jp/article/2507-mixi-new-ai-talking-robot/?page=2)
- Face: a 2021-era hands-on describes a *"ぴえん"* (teary/pleading) face and a "face exercise" function cycling through various expressions — implying a **multi-expression cartoon face, not eyes-only** — [HugKum](https://hugkum.sho.jp/469659). **Treat the eyes-vs-mouth classification for Romi as unconfirmed** pending a spec-level source.

**Sharp RoBoHoN (Sharp, Japan; 2016; still sold in Japan)**
- Launch price **¥198,000 (~£1,282)** plus a recurring service fee — [Digital Trends](https://qa2.www.digitaltrends.com/mobile/sharp-robohon-smartphone-robot-news); a **lite** variant (SR-05M-Y) is listed at **¥78,990** — [Kakaku.com](https://kakaku.com/hobby/robot/)
- Face/screen note: RoBoHoN's distinguishing display is a **body-mounted projector** (it is a projector-phone robot) — I did **not** verify in this session whether the projector is ever used for a face, and its facial features appear to be moulded/LED rather than a screen. Flagged as a gap below.

**Gatebox (Gatebox / Vinclu, Japan; 2016–2018)**
- In 2018 available from the company's site for **¥150,000** plus **¥1,500/month** subscription; its camera registers faces and movement — [Mobile Marketing Magazine](https://mobilemarketingmagazine.com/?p=110727)
- Gatebox is the clearest **projected character** product in the set: the "face" is a full projected anime character in a glass cylinder, not a face on the robot's own body. (Form factor is widely documented; the projection-of-a-whole-character distinction is my inference from the product's design, not a quoted source.)

**Temi (Robotemi, Israel; 2018; shipping)**
- Described as a three-foot, **video-screen-equipped** personal assistant at **$1,499**; its tablet actively **re-aims to centre the user's face** in the camera view — [O'Reilly](https://www.oreilly.com/content/?p=3156)
- Temi's screen is a **general-purpose Android tablet, not a character face** — this makes it a useful "utility screen, no character" counterexample. (Classification is my inference from the cited description.)

**KEYi Tech Loona and Energize Lab Eilik (China; desk/companion robots; shipping)**
- **Loona**: ~**$499–$500** at official and major retailers, often discounted to **$499.90**; used units $299–$400; mobile, 360° floor and desk navigation, gesture recognition, GPT-4o-powered conversation — [KEYi Tech](https://keyirobot.com/blogs/loona-tutorials/loona-robot-price-in-2025-is-this-smart-pet-worth-the-cost). **Caveat: this is the manufacturer's own blog, i.e. not independent.**
- **Eilik**: ~**$139.99** (one retailer listing £139.99), with a wider observed range **$139.99–$179.98** — [Creative Bloq](https://www.creativebloq.com/entertainment/looking-for-a-unique-stocking-filler-how-about-a-robot-desk-pet-or-keychain); [KEYi Tech guide](https://keyirobot.com/en-us/blogs/buying-guide/eilik-robot)
- **Eilik's screen is reported inconsistently**: one KEYi guide calls it screen-free, another says it has an **onboard screen interface running built-in mini games**, and its expressions are described as **OLED expressions** — [KEYi Tech](https://keyirobot.com/en-us/blogs/buying-guide/eilik-robot). Eilik in fact ships with an emissive expression panel; the "screen-free" claim is from a competitor-owned blog and should be discounted. Needs a first-party Energize Lab spec to settle.
- Eilik is stationary ("fixed base footprint stays put") vs Loona's mobility — [KEYi Tech](https://keyirobot.com/en-us/blogs/buying-guide/eilik-robot)
- **EMO** (Living.AI) appears in the same desk-pet category with a screen face and is described as high-priced — [KEYi Tech](https://keyirobot.com/en-us/blogs/buying-guide/emo-robot-price-is-this-ai-pet-worth-the-high-price-tag). Not independently verified here.

**Yukai Engineering (Japan; founded Dec 2007; faceless-by-design house)**
- Founded **December 2007**, founder **Shunsuke Aoki** (co-founder of teamLab and pixiv); has raised **$5.77M**; products include **Qoobo (2018)** and **Mirumi**, launched via crowdfunding — [CB Insights](https://www.cbinsights.com/company/yukai-engineering); [originofbots](https://www.originofbots.com/companies/models/yukai-engineering)
- Qoobo described as a therapeutic companionship cushion that "achieved global success" — [DigiTimes PR](https://www.digitimes.com/news/a20251224PR201.html?chid=9)
- Yukai does design, circuit, mechanical and software work in-house — [Yukai](https://www.ux-xu.com/business-en)

### Inferences
- The default commercial grammar for a robot face is **two eyes, emissive, small, no mouth, mounted on a moving head/screen gimbal**. Across eight verified eyes-only products this is not convergent accident; Kuri's designers articulated the reason explicitly (a screen showing anything but eyes "breaks character").
- The **face is the cheapest expressive channel**: Vector's 184x96 panel and Cozmo's small OLED are near-trivial parts, while Jibo's expressive motion required a heavily over-engineered motor system that the company considered downgrading. Expressiveness-per-dollar strongly favours the screen face.
- **Dual-use screens degrade character.** Astro's eyes vanish when Alexa UI takes the display, and reviewers flagged exactly that as character-breaking. Kuri's team pre-empted this failure mode by refusing a general-purpose screen; Temi accepted it and reads as an appliance.
- **Projection is used for content, not character.** Ballie projects media, Gatebox projects a whole character body. No verified product projects a *face onto its own shell*.
- Price distribution is bimodal: ~$140–$500 desk pets (Eilik, Reachy Mini, Loona, Vector) vs ~$800–$5,000 companions (Moxie, Jibo, aibo, LOVOT, RoBoHoN). The mid/high tier has the worse survival record.

### Gaps
- **Products in the brief I could not verify in this session and must not guess at:** Nabaztag (Violet, France, 2005), Keepon (BeatBots), Blue Frog Robotics Buddy, Misty Robotics Misty I/II, Casio Moflin, Moorebot, Enabot EBO, Yukai Bocco / Nékojita FuFu, Amazon Echo Show / Alexa's blue-ring "abstract light" face treatment, and "Vector-like Chinese clones". Searches for several of these returned nothing usable (the Yukai query returned only company profiles; the aibo query returned nothing on Nabaztag or Buddy; the Vector 2.0 query returned nothing on Misty).
- **No screen size or resolution found** for: Cozmo (the widely circulated 128x64 figure traces to hobbyist OLED-eye projects *inspired by* Cozmo, **not** to Anki documentation — [Wikipedia: Cozmo](https://en.wikipedia.org/wiki/Cozmo)), Jibo, aibo, LOVOT, Moxie, Romi, Reachy Mini, Eilik, Loona, LG Q9.
- **Vector's panel technology is genuinely unresolved** in secondary sources (IPS vs OLED). A teardown-level source is needed.
- **No fuseproject case study or designer interview on Jibo's face** was found; retrospectives praise the eye-like screen as interaction design but none document how fuseproject shaped it.
- **Astro's current status in 2025–2026 is unverified.** All retrieved coverage stops at the July 2024 business-version shutdown. Do not state that home Astro is alive or dead without a fresh check.
- **RoBoHoN's face mechanism** (projector vs moulded face vs LED eyes) is unverified.
- **Ballie's ship status and price as of late 2026** is unverified; coverage shows repeated slippage with no price ever announced.
- Romi's face composition (eyes-only vs eyes+mouth) is unconfirmed at spec level.
- Nothing found on 2026-launched products; the newest verified items are Reachy Mini (Jul 2025) and Romi Lacatan (CES 2025 honoree).

## Q2: Eyes-only vs eyes-plus-mouth/eyebrows — the explicit tally

### Takeaway
Among products whose face content I verified in this session the split is roughly **8 eyes-only : 1 full face**, with Embodied Moxie the lone verified mouth-bearing design — and Moxie is dead. The tally is the clearest signal in the dataset, but it is built on 10 verified entries, not the full 20+ catalogue, because of the call budget.

### Cited Findings

**EYES ONLY, no mouth (verified):**
1. **Anki Vector** — two pixelated eyes/pupils on a 184x96 display — [The Gadgeteer](https://the-gadgeteer.com/2018/12/31/anki-vector-robot-review/); [Slashdot/Fast Company](https://hardware.slashdot.org/story/18/08/08/2212241/ankis-new-robot-has-artificial-emotional-intelligence)
2. **Anki Cozmo** — OLED face, eye-driven expression (eyes become a Pong game when idle) — [Wikipedia](https://en.wikipedia.org/wiki/Cozmo); [Fortune](https://fortune.com/2016/06/27/anki-pixar-dreamworks-robot-games/)
3. **Mayfield Kuri** — eyes only, by explicit design rule; no other display content permitted — [IEEE Spectrum](https://spectrum.ieee.org/mayfield-robotics-announces-kuri-a-700-mobile-home-robot)
4. **Sony aibo** — two OLED displays for eyes, blink/close/expressions — [Sony](https://sony.mediaroom.com/2018-08-23-Sony-Announces-Limited-First-Litter-Edition-Release-of-aibo-in-U-S)
5. **Groove X LOVOT** — six stacked display layers forming iris and pupil; gaze-holding — [Japan Gov Online](https://gov-online.go.jp/eng/publicity/book/hlj/html/202106/202106_10_en.html)
6. **Amazon Astro** — two eyes that wink and blink on a 10.1" 1280x800 panel — [Tom's Guide](https://www.tomsguide.com/news/amazon-astro); [ReviewGeek](https://www.reviewgeek.com/134037/amazon-astro-review/)
7. **LG Q9 / CLoi AI agent** — "expresses emotion through digital eyes on the screen" — [Tom's Guide](https://tomsguide.com/news/the-new-samsung-ballie-robot-wows-at-ces-2024-an-ai-companion-with-a-built-in-projector)
8. **Reachy Mini** — screen-based eyes that blink — [iThome](https://www.ithome.com.tw/news/169983)

**EYES PLUS MOUTH / FULL FACE (verified):**
1. **Embodied Moxie** — "human-like animated face" able to display a range of human-like emotions — [Axios](https://www.axios.com/2024/12/10/moxie-kids-robot-shuts-down); maintained eye contact — [Popular Science](https://www.popsci.com/technology/moxie-robot-offline/)

**PROBABLE full-face, unconfirmed:**
- **MIXI Romi** — a hands-on describes a "ぴえん" face and a cycling "face exercise" of expressions, suggesting more than eyes — [HugKum](https://hugkum.sho.jp/469659)

**NOT a character face at all (verified):**
- **Samsung Ballie** — a 1080p content projector, no face — [Engadget](https://www.engadget.com/samsungs-ballie-robot-ball-showed-up-at-ces-2024-with-a-new-look-and-a-built-in-projector-224231693.html)
- **Temi** — general-purpose tracking tablet — [O'Reilly](https://www.oreilly.com/content/?p=3156)

### Inferences
- **No verified product in this set uses eyebrows as a separate screen element.** The eyebrow function is absorbed into eye-shape deformation (squash/stretch/tilt of the eye rectangles), which is what Vector and Cozmo do and what the hobbyist OLED-eye ecosystem that copied them replicates.
- The eyes-only convention plausibly survives because it is **language-free, mouth-sync-free and lip-sync-free**: a mouth on screen creates an expectation of speech-synchronised animation that a cloud-latency voice assistant cannot meet. Moxie, the one product that committed to a full human-like face, was also the one marketed on sustained conversational interaction — and the one that died fastest after its cloud dependency broke. This is a correlation I can support with the shutdown facts but **not** a documented causal claim.
- Kuri's rule is the generalisable principle the other eight products appear to follow without saying so: **the display must only ever be a face, or the character collapses into an object.** Astro is the controlled experiment that fails it.

### Gaps
- **The tally is incomplete.** Eilik, Loona, EMO, Nabaztag, Buddy, Misty, Keepon, Moflin, Qoobo, EBO, Bocco, RoBoHoN and Gatebox are all unclassified here. Several (Eilik, Loona, EMO, Buddy) are likely eyes-only; Gatebox is a full projected character. I did not verify any of these and deliberately leave them out of the count rather than inflate it.
- **No documented eyebrow case found**, in either direction — I found no source stating a product does or does not use eyebrows.
- No source found that quantifies or researches the eyes-only convention as a convention (e.g. an HRI paper or designer round-table). The Kuri quote is the only first-hand rationale I located.

## Q3: Commercial outcome, and whether failure was ever tied to face/character design

### Takeaway
The failures are consistently attributed to **price, cloud dependency, feature thinness and competition from smart speakers — not to the face**. The only face-specific design criticism I found anywhere is directed at Amazon Astro (eyes less expressive than Cozmo's; eyes disappearing when Alexa takes the screen), and Astro's face is widely cited as the thing that *redeems* it rather than the thing that killed it.

### Cited Findings
- **Jibo** — dead. Causes cited: delayed shipments, cancelled international orders with Indiegogo refunds, Echo undercutting the $899 price by ~$700, knockoffs by 2016, and consistently selling the vision rather than the reality of the product — [The Robot Report](https://www.therobotreport.com/jibo-social-robot-analyzing-what-went-wrong/). Tech sold to SQN Venture Partners — same source. No face-design cause cited.
- **Jibo's motion, not its face, was the cost sink**: the company over-engineered motion to compensate for a non-human look and considered downgrading the motors — [The Robot Report](https://www.therobotreport.com/jibo-social-robot-analyzing-what-went-wrong/)
- **Kuri** — cancelled July 2018, company closed 31 Oct 2018, full refunds to all buyers — [TechCrunch](https://techcrunch.com/2018/07/25/mayfield-robotics-ceases-production-of-kuri-robot-amid-a-questionable-future); [Engadget](https://www.engadget.com/2018/08/22/kuri-robot-creator-mayfield-robotics-to-shut-down/). No face-design cause cited; the eyes-only design was praised at launch.
- IEEE Spectrum treats Anki, Jibo and Kuri as a single category failure with shared lessons — [IEEE Spectrum](https://spectrum.ieee.org/anki-jibo-and-kuri-what-we-can-learn-from-social-robotics-failures)
- **Moxie** — dead Dec 2024; proximate cause a **critical funding round that fell through**; the aggravating factor was that core features were **cloud-dependent**, so robots stopped working within days — [Axios](https://www.axios.com/2024/12/10/moxie-kids-robot-shuts-down). Coverage emphasised the emotional cost to children — [Cybernews](https://cybernews.com/gadgets/moxie-robot-kids-toy-shutting-down/); [IBTimes](https://ibtimes.com/moxie-ai-robot-company-bankrupt-3754811)
- The Moxie shutdown was read in the trade press as an argument for **on-device rather than cloud AI** — [AppleInsider](https://appleinsider.com/articles/24/12/10/the-death-of-a-robot-designed-for-autistic-children-proves-apples-on-device-ai-is-the-right-path) (opinion, not reportage)
- **Vector/Anki** — Anki's assets were bought by Digital Dream Labs in 2020 and the product relaunched; DDL's Escape Pod explicitly addresses cloud dependency by enabling local-only operation — [Robotics 24/7](https://www.robotics247.com/article/digital_dream_labs_ships_upgraded_vector_2_0_social_robot)
- **Astro for Business** — discontinued July 2024, bricked 25 Sept 2024, framed by Amazon as refocusing on the home — [TechCrunch](https://techcrunch.com/2024/07/03/amazon-discontinues-astro-for-business-security-robot); covered elsewhere as Amazon "bricking" the robots — [Inc.](https://www.inc.com/amazon-bricking-its-astro-for-business-robots.html)
- **Face-tied criticism (the only instances found):** Astro's eyes are **less expressive than Cozmo's** ex-Pixar-animated face — [TechCrunch](https://techcrunch.com/?p=2208839); and Astro's **eyes vanish when Alexa answers**, reverting to an Echo screen and breaking the illusion — [review via BusinessGhana](https://businessghana.com/site/news/technology/264104/Amazon-Astro-review-too-much-Alexa-not-enough-arms)
- **Face-tied praise:** Astro's winking, blinking eyes plus screen motion are credited with making it feel less like surveillance-on-wheels — [Tom's Guide](https://www.tomsguide.com/news/amazon-astro)
- **Survivors** all have a face and most have recurring revenue: aibo (Sony, since 2018, AI Cloud subscription — [Engadget](https://www.engadget.com/2018-08-23-sony-aibo-us-launch.html)), LOVOT (three generations, monthly fee from ¥9,900 — [PC Watch](https://pc.watch.impress.co.jp/docs/news/1596287.html)), Romi (¥1,780/month — [Business Insider Japan](https://www.businessinsider.jp/article/2507-mixi-new-ai-talking-robot/?page=2)), RoBoHoN (recurring service fee — [Digital Trends](https://qa2.www.digitaltrends.com/mobile/sharp-robohon-smartphone-robot-news)), Gatebox (¥1,500/month — [Mobile Marketing Magazine](https://mobilemarketingmagazine.com/?p=110727))
- **Faceless survivor:** Qoobo, a faceless tactile cushion, is described as having achieved global success — [DigiTimes PR](https://www.digitimes.com/news/a20251224PR201.html?chid=9) (PR source — weak)

### Inferences
- **The face is not what kills these products.** Across Jibo, Kuri, Anki and Moxie, the documented causes are funding, pricing against smart speakers, shipping execution and cloud dependency. Face/character design shows up in post-mortems only as the thing reviewers liked.
- There is, however, one real face-design failure mode in the record: **sharing the face panel with a general-purpose assistant UI.** Astro is the only product where a reviewer named a face behaviour as what broke the character, and the behaviour was the Alexa UI pre-empting the eyes.
- **Recurring-revenue + face survives; one-time-purchase + face dies.** Every verified survivor (aibo, LOVOT, Romi, RoBoHoN, Gatebox) charges monthly; the dead (Jibo, Kuri, Cozmo/Vector-as-Anki, Moxie) were predominantly hardware-margin businesses. The face is orthogonal to this.
- **Cloud dependency is the recurring character-specific tragedy**, because a character that dies is narratively worse than an appliance that dies — visible in the Jibo farewell-dance and Moxie "I love you… goodbye" coverage. DDL's Escape Pod is the only verified commercial response to this.

### Gaps
- **"Which companies deliberately chose NO face, and did they say why?" is substantially unanswered.** I verified only that Yukai Engineering builds faceless tactile products (Qoobo, Mirumi) and that Samsung Ballie and Temi have no character face — but I found **no statement from Samsung, Temi, Yukai or Casio (Moflin) explaining the choice**. My Yukai search returned only company profiles. This needs a dedicated pass over Yukai interviews, Casio's Moflin press kit and Samsung's Ballie design commentary.
- No post-mortem found that attributes any shutdown to the face or character design. If one exists I did not find it; I would state in the report that the record is silent rather than that the record is negative.
- No documented commercial figures (units sold, revenue) for any product in this survey.
- The fuseproject–Jibo design relationship is undocumented in anything I retrieved.
- Nothing retrieved covers 2026 launches or current-year status for Astro, Ballie or LG Q9.
