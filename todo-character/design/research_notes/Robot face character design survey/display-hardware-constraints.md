# Practical Hardware and Legibility Constraints for a Pi-Based Animated Character Face

Scope: hardware available to a hobbyist in 2026, real SPI framerate limits, and legibility rules for a device on a living-room shelf viewed from a few metres.

## What small displays are actually available for a Raspberry Pi in 2026?

### Takeaway
Three distinct tiers exist: cheap SPI panels ($15–40, 128x64 to 480x320, 10–90 fps depending on pixel count), DSI/DPI panels that behave like a real framebuffer at 60 fps (Pimoroni HyperPixel 2.1 Round, Raspberry Pi Touch Display 2, $40–110), and e-paper (unusable for animation). For a face viewed from a few metres, physical size matters more than resolution, which pushes toward the DSI tier or a 2.8–3.5in SPI panel.

### Cited Findings

**Round LCD (GC9A01)**
- Waveshare 1.28in Round LCD Module (SKU 19192): 240x240, IPS, 65K RGB, GC9A01 driver, 4-wire SPI, 3.3V/5V, active area Φ32.4 mm, module 40.4 x 37.5 mm, pixel size 0.135 x 0.135 mm, **$14.99** single unit ($14.31 at 100+). Brightness and viewing angle are **not published** on the product page — [Waveshare 1.28inch LCD Module](https://www.waveshare.com/product/displays/lcd-oled/1.28inch-lcd-module.htm)
- Touch variant (GC9A01 + CST816S touch over I2C) also 240x240 IPS; retail ~AU$31.50 inc GST — [Core Electronics](https://core-electronics.com.au/128inch-round-lcd-display-module-with-touch-240240-pixels.html); ~$21.41 for the plain module at RobotShop CA — [RobotShop](https://ca.robotshop.com/products/waveshare-240x240-general-128inch-round-lcd-display-module-65k-rgb)
- Adafruit sells a 1.28in 240x240 round IPS board at 16-bit colour with a Pillow-compatible Python library for the Pi — [Adafruit learn guide](https://learn.adafruit.com/adafruit-1-28-240x240-round-tft-lcd?view=all)
- Φ32.4 mm of active area is about the size of a large coin. Note the *physical* smallness, not the resolution, is the binding constraint for a shelf device.

**Round DPI (the serious round option)**
- Pimoroni HyperPixel 2.1 Round (PIM579): **480x480 minus corners, ~229 PPI, 2.1in IPS, 18-bit colour (262,144), 175° viewing angle, 60 FPS, active area 53.28 x 53.28 mm** — [Pimoroni](https://shop.pimoroni.com/products/hyperpixel-round); ~AU$109.95 inc GST
- Software caveat: recent Raspberry Pi OS releases do not fully support the round HyperPixel; Pimoroni/resellers direct users to a provided Bookworm image — [The Pi Hut listing](https://thepihut.com/collections/raspberry-pi-hats/products/hyperpixel-2-1-round-hi-res-display-for-raspberry-pi)
- No luminance (nits) figure is published by Pimoroni or any reseller found.

**Square / rectangular SPI IPS**
- Adafruit PiTFT 2.8in, 240x320, ILI9341 — benchmarked at **59.81 fps** with fbcp-ili9341 — [fbcp-ili9341](https://github.com/juj/fbcp-ili9341)
- Adafruit PiTFT 3.5in, 320x480, HX8357D — **21.29 fps**; Waveshare 3.5in (B), 320x480 ILI9486 — **12.97 fps**; maithoga 3.5in ILI9486L — **13.56 fps**; KeDei v6.3 3.5in MPI3501 — **4.8 fps** — [fbcp-ili9341](https://github.com/juj/fbcp-ili9341)
- Adafruit 1.54in 240x240 ST7789 — **92.23 fps**; Waveshare 1.3in 240x240 ST7789VW — **91.69 fps** — [fbcp-ili9341](https://github.com/juj/fbcp-ili9341)
- Arduino A000096 1.77in 128x160 ST7735R — **180.56 fps** — [fbcp-ili9341](https://github.com/juj/fbcp-ili9341)

**OLED**
- SSD1306 128x64 monochrome: luma.oled community benchmarks put a Pi 3B at ~102.77 fps on one 128x64 panel and ~68 fps over SPI; a Pi Zero W managed ~19 fps over I2C — [luma.oled wiki](https://github.com/rm-hull/luma.oled/wiki/Usage-&-Benchmarking). The wiki's table layout makes panel/row attribution ambiguous; treat as rough.
- I2C at 400 kHz: 1024 bytes of frame data takes ~23 ms, capping full-frame updates below ~30 fps once overhead is counted; a Pi 4 was measured at up to 1000 kHz I2C — [DisplayModule](https://www.displaymodule.com/blogs/knowledge/spi-vs-i2c-for-oled-speed-pin-count). A vendor source, so weight accordingly.
- SSD1351 colour OLED: Adafruit 1.5in 128x128 16-bit breakout w/ microSD + EYESPI, **US$39.95** ($35.96 at 10–99) — [Adafruit 1431](https://www.adafruit.com/products/1431). Cheaper bare module: Orient Display AOC128128A0-1.50W, ~£20.63 ex VAT — [DigiKey](https://www.digikey.co.uk/en/products/detail/orient-display/AOC128128A0-1-50W/22531888)
- Adafruit 1.27in 128x96 SSD1351 benchmarked at **91.55 fps** — but note its rated SPI is only 20 MHz and the obtained bus was 18 MHz; the high fps comes from the tiny pixel count — [fbcp-ili9341](https://github.com/juj/fbcp-ili9341)

**E-paper (ruled out for animation)**
- Waveshare 2.13in e-Paper HAT+: 2 s full refresh, 0.3 s partial, 1.8 s fast refresh — [Waveshare wiki](https://waveshare.com/wiki/2.13inch_e-Paper_HAT%2B); Waveshare itself calls these figures experimental.
- 7.5in HAT V2: 4 s full / 0.4 s partial / 1.5 s fast — [Waveshare wiki](https://www.waveshare.com/wiki/7.5inch_e-Paper_HAT_Manual); 13.3in HAT (B): 22 s full / 2.9 s partial — [Waveshare wiki](https://www.waveshare.com/wiki/13.3inch_e-Paper_HAT_(B)_Manual)
- Partial refresh cannot be used indefinitely: manuals direct a full refresh after several partials (one FAQ says a full clear after ~5 partials), and panels without partial refresh need ≥180 s between refreshes — [3.52in manual](https://waveshare.com/wiki/3.52inch_e-Paper_HAT_Manual), [5in FAQ](https://docs.waveshare.com/5inch_e-Paper/FAQ), [1.54in manual](https://www.waveshare.com/wiki/1.54inch_e-Paper_Module_Manual)

**DSI touchscreens**
- Raspberry Pi Touch Display 2, 7in: **$60**, 720x1280, active area 88 x 155 mm, powered from the Pi, in production until at least January 2030 — [Raspberry Pi](https://raspberrypi.com/products/touch-display-2); Waveshare lists it as IPS with **170° viewing angle** and 5-point capacitive touch over I2C — [Waveshare](https://www.waveshare.com/product/raspberry-pi-touch-display-2.htm)
- 5in variant: **$40**, same 1280x720, 24-bit RGB, 5-point multitouch; Tom's Hardware gives viewing angle as 80° vs 85° for the 7in — [Tom's Hardware](https://www.tomshardware.com/uk/raspberry-pi/raspberry-pi-releases-smaller-five-inch-touch-display-2-lower-in-price-same-resolution-as-larger-model). **Conflict:** Waveshare says 170° for the 7in while Tom's says 85°; these are likely half-angle vs full-angle conventions, but the sources are not reconciled.
- 10.1in: 1200x1920, 10-point touch, **$80/£77**; needs four DSI lanes so it is **not compatible with Pi 4 or earlier, nor the Zero series** — [CNX Software](https://www.cnx-software.com/2025/08/18/raspberry-pi-touch-display-2-gets-40-5-inch-variant-with-1280x720-resolution/)
- 7in and 5in connect to the DSI port and draw power from GPIO; compatible with all Pis from 1B+ onward **except the Zero series, which has no DSI port** — [Raspberry Pi](https://raspberrypi.com/products/touch-display-2)
- Waveshare 2.8in DSI LCD: 480x640 portrait, IPS, **160° viewing angle**, 5-point capacitive touch; supports Pi 5/4B/3B+/3A+ and CM3/3+/4 (CM needs an adapter board) — [Waveshare](https://www.waveshare.com/product/raspberry-pi/2.8inch-dsi-lcd.htm)

### Inferences
- The display landscape splits cleanly by interface, not by shape. SPI panels are cheap and small but framerate-bound; DSI/DPI panels are a normal Linux framebuffer at 60 fps and cost 2–7x more.
- For a shelf device at 2–4 m, the 1.28in round GC9A01 (Φ32.4 mm) is almost certainly too physically small for a face to read, regardless of its adequate 240x240 resolution. The HyperPixel 2.1 Round (53.28 mm) or a 2.8in+ panel is the realistic floor.
- E-paper is disqualified for any animated face: even best-case 0.3 s partial refresh is ~3 fps, and the mandated periodic full refresh produces a visible multi-second flash.

### Gaps
- **No brightness (nits) figure was found for any of these panels** — not Waveshare's GC9A01 module, not HyperPixel Round, not the Pi Touch Display 2. This is a real hole for the living-room readability question.
- Viewing angle is not published for the Waveshare 1.28in round module or the Adafruit round TFT.
- No GC9A01 entry exists in any benchmark table found.
- 2026-current prices could not be confirmed for most reseller listings; several pages were stale or sold out. Waveshare's own $14.99 and Raspberry Pi's $40/$60/$80 are the most reliable figures.

## What refresh rate can a Raspberry Pi realistically drive over SPI?

### Takeaway
Full-frame SPI refresh is bandwidth-bound and scales inversely with pixel count: ~90 fps at 240x240, ~60 fps at 240x320, and only ~13–21 fps at 320x480. The crucial 2026 caveat is that the driver that achieved those numbers (fbcp-ili9341) is dead, so a modern builder should expect the lower, kernel-driver numbers (~40 fps at 320x240) unless they write their own update path.

### Cited Findings
- **Bandwidth rule:** a 320x240 16bpp display needs about **73.728 MHz of SPI clock to reach 60 fps** at full refresh. SPI speed = core_freq / CDIV — [fbcp-ili9341](https://github.com/juj/fbcp-ili9341)
- Measured fps at 240x240 (ST7789/ST7789VW): **91.69–92.23 fps** at an obtained bus of 84.5–85 MHz — [fbcp-ili9341](https://github.com/juj/fbcp-ili9341)
- ILI9341 panels, nominally rated 10 MHz, were overclocked to **70–80 MHz** in practice and all ran well — [fbcp-ili9341](https://github.com/juj/fbcp-ili9341). The ILI9341 datasheet spec is 25 MHz, so this is out-of-spec overclocking that happens to work — [PJRC forum](https://forum.pjrc.com/threads/38752-Playing-around-with-yet-another-version-of-ILI9341_t3-library-(ILI9341_t3n)?p=215648)
- **Bit depth dominates bandwidth gains:** the ILI9486L achieved ~56.8% more bus bandwidth than the ILI9486 (50 MHz vs 31.88 MHz) yet its framerate barely improved, because it needs 24 bits per pixel where the ILI9486 uses 16 — [fbcp-ili9341](https://github.com/juj/fbcp-ili9341)
- **Core clock governor matters:** Pi 3B and Zero W default to a 400 MHz core but drop to 250 MHz under no load, cutting SPI bandwidth by about 60% — [fbcp-ili9341](https://github.com/juj/fbcp-ili9341)
- **The driver is retired.** The Feb 2024 update states "The era of fbcp-ili9341 has come to an end." It was built on the VideoCore DispmanX API, which is deprecated, unavailable on Pi 5 and later, and no longer enabled by default even on Pi 0–4; Raspberry Pi moved to the KMS compositor stack, which needs a different SPI driver interface. The author considers the repo stale. **It also only worked on 32-bit OSes.** — [fbcp-ili9341](https://github.com/juj/fbcp-ili9341)
- **Modern (post-DispmanX) figure:** a notro GUD test on a Raspberry Pi 4 at 62.5 MHz SPI reported about **40.8 fps for a 320x240 RGB565 frame** uncompressed and ~42 fps with highest compression, and was SPI-bus-limited rather than CPU-limited. This used a mipi-dbi driver, not an ILI9341-specific one — [notro gist](https://gist.github.com/notro/1fbd5df09c71261d0d7773a755ac9ee8)
- Hackster reported the fbcp-ili9341 driver pushing Pi SPI displays "up to 60 FPS" — [Hackster](https://www.hackster.io/news/new-driver-can-push-raspberry-pi-spi-displays-up-to-60-fps-fa6d73b57f05); treat as the best case for that now-dead driver.
- An Instructables GC9A01 writeup on CircuitPython (on an RP2040 Pico, **not a Pi**) reported only ~9 fps and noted video playback on 240x240 SPI screens is not straightforward — [Instructables](https://www.instructables.com/Connected-Round-Screen-240x240-GC9A01-Controller-t)

### Inferences
- Rough budget: bits per frame = W x H x bpp. At 240x240 RGB565 that is 921,600 bits; at 60 MHz SPI that is ~65 fps theoretical, ~50 fps realistic after overhead. This matches the measured numbers and is the right back-of-envelope for a builder.
- A 240x240 face at 30 fps is comfortably achievable over SPI even with the modern kernel path. A 320x480 face at 30 fps is **not** achievable with full-frame updates.
- **Dirty-rectangle updates are the single biggest lever.** A character face is mostly static background with small moving regions (eyes, mouth), so pushing only changed tiles can multiply effective framerate several times over. This is how to get smooth animation on a 320x480 panel.
- Choosing a DSI/DPI panel sidesteps the entire problem: HyperPixel Round is specified at 60 FPS and Pi Touch Display 2 is a normal framebuffer. For an animation-heavy project this is likely the correct architectural call.

### Gaps
- No published benchmark exists for GC9A01 on a Raspberry Pi at all. The 240x240 ST7789 figures are the closest proxy.
- No post-KMS (Pi 5, 64-bit) benchmark was found for any SPI panel. The 40.8 fps GUD figure is a Pi 4 mipi-dbi result.
- No measured figures for dirty-region/partial-update throughput were found, so the multiplier above is an inference, not a measurement.

## Legibility at 240x240 / 320x240 from across a room

### Takeaway
The authoritative pixel-level guidance is the ADA-referenced low-resolution variable-message-sign table: features 7 px tall need a 1 px stroke and 10–12 px features need a 2 px stroke. Legibility distance is driven overwhelmingly by feature *height*, not by stroke width or contrast, which keeps improving with size while the others plateau.

### Cited Findings
- **Pixel stroke table (ADA/access-board, Table 11B-703.8.5, Pixel Count for Low Resolution VMS):** a 7-pixel-high character uses a 1-pixel stroke; 10 to 12-pixel characters use 2-pixel strokes — [Access Board / corada](https://www.corada.com/documents/2016CBCPG/11b-703-8-variable-message-signs)
- **Height dominates:** "unlike other key variables (e.g., contrast, luminance, and stroke width) legibility distance continues to improve with increases in letter height" — [US Access Board, VMS legibility](https://www.access-board.gov/research/communication/variable-message-signing/vms-legibility/)
- NIST derived a formula giving the letter stroke width needed for legibility at any given distance for an observer of any given visual acuity, tied to visual angle and the Snellen chart — [NIST Technical Note 1180](https://nvlpubs.nist.gov/nistpubs/Legacy/TN/nbstechnicalnote1180.pdf)
- **Pixel pitch, not just resolution, sets legibility distance:** an FHWA changeable-message-sign study tested 2-pixel-stroke fonts and found a 20 mm pixel pitch full-colour display gives a longer legibility distance than the previous generation using a 1.6-inch pitch — [FHWA](https://www.fhwa.dot.gov/publications/research/safety/15027/004.cfm)
- **Stroke-width effects are contrast-dependent, not universal:** research on retroreflective highway signs found narrow stroke width significantly increased legibility on high-contrast signs — [SWOV](https://swov.nl/en/publicatie/luminance-and-contrast-requirements-legibility-and-visibility-highway-signs-paper)
- Vendor rule of thumb for LED displays: optimal viewing distance in feet ≈ 3x the pixel pitch in mm — [Daktronics](https://www.daktronics.com/en-us/support/kb/000030569). Vendor source; a heuristic.
- Common heuristic ratio: stroke width ≈ 1/5 of letter height, with letter height = viewing distance in feet / 10 — [signage calculator](https://www.ultimatefinancecalculator.com/calculators/signage-size-by-viewing-distance-calculator). Non-authoritative.

### Inferences
Applying the sources to this specific problem:
- **Never draw a 1 px stroke on a face.** At 240x240, the ADA table's 1 px stroke is only sanctioned for features ~7 px tall. A face eyebrow or mouth line is a large feature, so it falls in the 2 px-minimum band at minimum — and because the character is viewed at 2–4 m rather than reading distance, strokes should be scaled far beyond the table: **a practical floor is ~4% of the display's smaller dimension (≈8–10 px at 240x240)** for any line that must read across a room.
- **The Daktronics 3x-pitch rule is the most damning number for small SPI panels.** The Waveshare 1.28in round has 0.135 mm pixel pitch, giving an "optimal" viewing distance of ~0.4 m. A 2–4 m viewing distance means the viewer is 5–10x past the pitch-optimal distance — individual pixels are irrelevant, and the *whole display* subtends a tiny visual angle. The correct reading is that resolution is never the constraint; angular size of the physical panel is.
- Because the research shows height keeps paying off while contrast and stroke plateau, the design rule is: **make the eyes and mouth occupy a large fraction of the panel.** A face with small features on a large empty field wastes the only variable that keeps scaling.
- Thin lines and small details fail for two compounding reasons: at these pitches a 1–2 px line subtends well under one arcminute at 3 m (below the ~1 arcminute 20/20 acuity limit derived from the Snellen relationship NIST uses), and anti-aliasing a thin line spreads its already-marginal contrast across neighbouring pixels, dropping effective contrast below threshold. Hard-edged, thick, high-contrast shapes are the only forms that survive.

### Gaps
- No single authoritative "minimum stroke width per viewing distance" table was found; the NIST formula requires inputs (acuity, luminance) and the pixel table is for signage characters, not faces.
- **No research was found on legibility of non-text graphics (faces, iconography) at distance.** All usable quantitative sources are text/character legibility. The transfer to facial features is an inference.
- No specific contrast-ratio minimum (e.g. a numeric ratio target) was found from an authoritative source for this use case.

## OLED versus LCD for a glowing face on black, and burn-in risk

### Takeaway
OLED's advantage is structural: a black pixel emits nothing, so a glowing face on black shows no backlight bleed or grey halo — exactly the look this design wants. Burn-in is a genuine but manageable risk at the hours-per-day scale: the evidence points to months-to-years, not hours, and brightness is the main lever.

### Cited Findings
- **Burn-in timeline:** burn-in "won't likely occur after just a few hours"; tests indicate permanent burn-in will likely only occur after months or years of displaying static elements. In one RTINGS long-term test, **subtitles caused burn-in after roughly 7,100 hours** of viewing — [Engadget](https://engadget.com/2203219/oled-burn-in-risks-explained/), [RTINGS](https://www.rtings.com/tv/learn/real-life-oled-burn-in-test)
- **Brightness is the dominant factor:** in RTINGS' test, the maximum-brightness CNN TV showed more severe burn-in than the 200-nit CNN TV — [RTINGS](https://www.rtings.com/tv/learn/real-life-oled-burn-in-test)
- **Cumulative duration counts, and splitting it does not help:** LG has said static content present for 30 minutes twice a day is equivalent to one hour of static content once per day — [Engadget](https://engadget.com/2246417/tvs-at-risk-of-burn-in/)
- **Colour matters:** in RTINGS' 20/7 test, the **red sub-pixel degrades fastest, then blue, then green** — [RTINGS](https://www.rtings.com/tv/learn/real-life-oled-burn-in-test)
- **Newer panels are not inherently safer:** RTINGS found 2020–2023 OLEDs in their accelerated test did not consistently show less permanent burn-in than the 2017 LG C7; newer panels are brighter and more efficient, giving headroom to reduce output, which RTINGS frames as a risk-reduction measure rather than a guaranteed fix — [RTINGS](https://www.rtings.com/tv/learn/oled-burn-in-not-improved-as-expected), [Tom's Hardware](https://www.tomshardware.com/monitors/modern-oled-tvs-are-just-as-susceptible-to-burn-in-as-older-models-but-theyre-much-brighter-longevity-test-highlights-luminance-headroom-and-efficiency-as-mitigations)
- **Standard mitigations:** screensavers, pixel shift, panel refresh, and logo luminance adjustment (which reduces brightness around static images specifically); lowering overall brightness on static-heavy content reduces risk; Sony advises against leaving a paused game onscreen for hours or days — [Engadget](https://engadget.com/2246417/tvs-at-risk-of-burn-in/)
- **LCD has no OLED-style burn-in**, though it can show temporary image retention — [Engadget](https://engadget.com/2203219/oled-burn-in-risks-explained/)

### Inferences
- The optical case for OLED here is strong and specific. A glowing-face-on-black design is precisely the content where LCD's weakness shows: an LCD's "black" is a lit backlight blocked imperfectly by the liquid crystal, so the field around the face is dark grey and, in a dim living room, visibly glowing with a halo around bright features. On OLED the surround is genuinely off, so the face appears to float. For this one design, OLED is not a marginal upgrade but the whole aesthetic.
- Burn-in risk is **real but tractable for this project**, and the mitigations map neatly onto a character face:
  - A face is intrinsically animated — blinking, saccades, idle drift — which is varied content, the low-risk category.
  - Apply **micro-drift**: translate the whole face by a few pixels on a slow cycle. This is pixel shift, implemented in one line of blit offset.
  - Run at **moderate brightness**, not maximum. This is the strongest single lever per the evidence.
  - **Avoid saturated red** for large persistent features (a red mouth held for hours is the worst case given red's fastest degradation). Cyan/green/white features are safer.
  - Blank or dim the display when nobody is present (a PIR sensor or schedule), since cumulative static hours is what accrues.
- The 7,100-hour subtitle figure is a useful calibration: at 8 h/day that is ~2.4 years of continuous static content. A face with any idle animation and drift should far outlast that.
- **Practical counterweight:** every colour OLED available at this size is small (SSD1351 is 1.5in/128x128) and relatively expensive ($39.95 vs $14.99 for a larger-resolution LCD). Given that angular size is the real legibility constraint, a builder may be forced to choose a larger LCD over a better-looking small OLED. A dark-room LCD halo can be partly mitigated with a dark bezel, a neutral-density/AR front layer, and keeping the face's own luminance high so the contrast ratio perceptually improves.

### Gaps
- **All burn-in evidence found is from TV and monitor panels, not from small SSD1306/SSD1351 PMOLED modules**, which use different materials and drive schemes. PMOLED lifetime is often specified in hours-to-half-brightness by the manufacturer, but no such figure was found for these specific modules. This is a meaningful extrapolation gap.
- No measured contrast ratio was found for any of the specific LCD panels surveyed, so the OLED-vs-LCD black-level difference could not be quantified for these parts.

## Round versus rectangular, power, brightness, enclosures, and existing projects

### Takeaway
Round panels suit a single cyclopean "eye" or a full circular face and read as a deliberate object rather than a screen; rectangular panels suit two-eye layouts and are far cheaper per unit area. Enclosures and reference designs are the weakest-supported area: almost nothing off-the-shelf exists, and most published Pi face projects use small SPI TFTs with custom 3D-printed housings.

### Cited Findings

**Round vs rectangular (hardware facts)**
- The round GC9A01 is addressed as a square 240x240 raster with the corners physically absent — the Waveshare module is 240x240 with a Φ32.4 mm circular active area — [Waveshare](https://www.waveshare.com/product/displays/lcd-oled/1.28inch-lcd-module.htm)
- HyperPixel 2.1 Round is explicitly described as "480x480 pixels, minus the corners" — [Pimoroni](https://shop.pimoroni.com/products/hyperpixel-round)
- Round options are also notably more expensive per unit of area and have thinner software support than rectangular ones (see the HyperPixel Round Bookworm-image caveat above) — [The Pi Hut](https://thepihut.com/collections/raspberry-pi-hats/products/hyperpixel-2-1-round-hi-res-display-for-raspberry-pi)

**Power and brightness**
- Waveshare's GC9A01 module requires the host to drive the backlight via GPIO or PWM to control brightness; there is a dedicated BL pin alongside DIN→MOSI, CLK→SCLK, CS→CE0, plus DC and RST — [Waveshare pin table](https://waveshare.com/wiki/Template:1.28inch_LCD_Module_Interface), [Display_Lib_RPI README](https://raw.githubusercontent.com/gavinlyonsrepo/Display_Lib_RPI/main/extra/doc/gc9a01a/README.md)
- The GC9A01 module runs on 3.3 V or 5 V — [Waveshare](https://www.waveshare.com/product/displays/lcd-oled/1.28inch-lcd-module.htm)
- Raspberry Pi Touch Display 2 (5in and 7in) draws power from the Pi's GPIO pins, so no separate supply is needed — [Raspberry Pi](https://raspberrypi.com/products/touch-display-2)
- SPI must be explicitly enabled in the Pi's configuration before any of these panels work — [Display_Lib_RPI README](https://raw.githubusercontent.com/gavinlyonsrepo/Display_Lib_RPI/main/extra/doc/gc9a01a/README.md)

**Enclosures**
- Waveshare's DSI product tables show "with case" variants for the 4.3in and 7in displays but **none for the 2.8in** — [Waveshare 2.8inch DSI LCD](https://www.waveshare.com/product/raspberry-pi/2.8inch-dsi-lcd.htm)
- A targeted search for a round 2.8in DSI display, an enclosure, or a desktop robot kit for these panels returned nothing matching.

**Existing open-source Pi face projects**
- **Robot Eyes** (Hackster, MIT-licensed): a lightweight face engine driving smooth animated eyes on a Raspberry Pi with a **1.8in ST7735 TFT** — [Hackster](https://www.hackster.io/calvinsewornu123/robot-eyes-smooth-animated-eyes-on-raspberry-pi-9deff6) (page returned HTTP 403 to direct fetch; details are from search-result metadata only)
- **Adafruit Animated Snake Eyes Bonnet:** drives "two small OLED or TFT LCD displays"; a Pi 2 or newer is recommended, a Pi Zero or other single-core board runs the code but performance lags, and Pi 4/Pi 5 now work. The guide notes the Pi's faster CPU and **dual SPI buses** could yield faster framerates. No specific panel part numbers, resolutions, or measured framerates are given, and the project is described as "not-inexpensive" — [Adafruit](https://learn.adafruit.com/animated-snake-eyes-bonnet-for-raspberry-pi/overview)
- **Emo** (Electromaker): open-source personal companion robot using a **Waveshare 2in IPS display** in the head on a Raspberry Pi 4; rated expert-level — [Electromaker](https://electromaker.io/project/view/emo-your-personal-companion-robot)
- **Rodney** (CodeProject): ROS-based autonomous robot whose head uses a **7in touchscreen**, with the face driven by ROS topics — [CodeProject](https://www.codeproject.com/Articles/1259980/Rodney-A-Long-Time-Coming-Autonomous-Robot-Part-5)
- **Bot Ekko** (GitHub): Pi-based robot with a digital face, MediaPipe gesture detection, ESP32 sensor integration; **license not established** from search results — [GitHub](https://github.com/knownbug06/bot_ekko)
- Commercial/educational comparators reviewed by Raspberry Pi's own magazine: McRoboFace and Ohbot Pi — [McRoboFace review](https://magazine.raspberrypi.com/articles/mcroboface-review), [Ohbot Pi review](https://magazine.raspberrypi.com/articles/ohbot-pi-review). Neither review establishes open-source status.

### Inferences
- **Round design implications:** the circular mask is a hard constraint, not a decoration — anything near the corners of the 240x240 buffer is simply invisible, so the usable area is π/4 ≈ 79% of the raster. A round panel strongly suggests either one large cyclops eye (where the circle *is* the iris, which is extremely legible at distance because the feature fills the panel) or a whole circular head. Two eyes inside one circle wastes the format. The bezel-free circular form also reads as an object rather than a gadget, which matters for a living-room shelf.
- **Rectangular design implications:** a 320x240 landscape panel naturally accommodates two eyes plus a mouth, and is the only format where a conventional face layout is efficient. The cost is that it reads as a screen, and the empty background is where LCD halo is most visible.
- **Two-panel option:** the Snake Eyes Bonnet's dual-SPI-bus approach (two small displays, one per eye) is the established pattern for maximising apparent eye size at low cost, and sidesteps the per-panel bandwidth limit by splitting across buses. The tradeoff is no mouth and a mechanically harder enclosure.
- **Living-room readability:** no nits figures exist for any of these panels, so this cannot be answered from sources. The structural facts that do apply: IPS panels have wide viewing angles (160–175° quoted across the range), which matters for a shelf device viewed off-axis; backlight brightness is under software PWM control on the SPI modules, so auto-dimming is straightforward; and OLED's lack of a backlight means it is typically *dimmer* than a backlit LCD in a bright room while being far better in a dim one. For a lit living room, a backlit IPS LCD at high brightness is the safer bet; for a dim room, OLED wins decisively.
- **Power:** the SPI modules are trivial loads (small backlight plus logic at 3.3 V); the Pi itself dominates total consumption. The DSI Touch Displays are powered from GPIO, which means the Pi's own supply must have headroom — undersized supplies are a common failure mode here.
- **Enclosure reality:** a builder should plan on 3D printing. The combination of panel, Pi, and a specific face aesthetic means a custom housing is effectively mandatory, and the lack of any off-the-shelf "Pi face device" case is consistent across the surveyed vendors.

### Gaps
- **No off-the-shelf enclosure or published reference design for a Pi-based face device was found.** This is a genuine negative finding, not a search failure — Waveshare offers cases only for its 4.3in and 7in DSI panels, and no vendor sells a face-device housing.
- **No brightness/nits data for any surveyed panel**, so "is it readable in a lit living room?" cannot be answered quantitatively from sources. Only the structural argument above is supportable.
- No measured power consumption figures (mA) were found for any of these display modules.
- Robot Eyes and Bot Ekko could not be fetched directly (403 and not attempted respectively), so their framerates, libraries, and licenses are unverified beyond search-result metadata.
- No project was found that documents a *measured* framerate for an animated face on a Pi SPI display — the closest data remains the generic panel benchmarks in section 2.
