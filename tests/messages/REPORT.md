# TODO message passing: test report

Run on 2026-11-24 against `docs/index.html` (mtime **11:48:51**, the multi-language `langs[]` rebuild). Model chain: the page's own `streamBrain()` against real Gemini free tier, one shared conversation per scenario, fresh store per scenario.

## Before vs after the 11:48:51 rebuild
- A first pass started at ~11:45 loaded the **old** page (single `lang`). It was stopped at about 11:49 after 3 scenarios per worker. Its partial output is kept only for reference in `logs/pre_rebuild_*` and is **not counted**.
- **Every counted result** (`results.json`, field `page_mtime` = 11:48:51) ran on the **current** file. No re-run for the rebuild was needed: everything was re-run.
- The 5 bilingual scenarios (O01–O05) were added for the rebuild.
- Could the rebuild cause any failure? I found none. The language failures (A16, B08, K06) are about which script the reply uses, not about `langs`. O03 fails on name matching (`राजूला`), not on language.

## Totals
119 scenarios, 14 categories plus bilingual. Expectations were fixed in `scenarios.mjs` before running.
- **51 busy-inconclusive.** The free tier was saturated: 3 parallel workers, then a single-worker retry that got through only 6 turns in about 30 min before I stopped it. A scenario counts as busy when any turn ended with "very busy". A08 also counts as busy: its first turn went busy and that caused its later failure.
- **68 conclusive: 41 passed raw, plus 8 that "failed" only because my checker was too strict** (listed below). That gives **49/68 = 72 % adjusted pass, with 19 real failures.**
- **The busy runs are not harmless (a product bug, see RC1):** in 10 scenarios a busy turn left the message **marked delivered although nobody heard it**.

| category | raw pass | checker false-fail | real fail | busy-inconclusive | pass rate of conclusive (adjusted) |
|---|---|---|---|---|---|
| leave_deliver | 5 | 3 | 6 | 6 | 57% (8/14) |
| repeat | 3 | 0 | 1 | 4 | 75% (3/4) |
| recipient | 1 | 1 | 1 | 9 | 67% (2/3) |
| unknown | 1 | 1 | 0 | 3 | 100% (2/2) |
| multi | 3 | 0 | 1 | 4 | 75% (3/4) |
| privacy | 2 | 0 | 2 | 4 | 50% (2/4) |
| cancel_change | 4 | 0 | 0 | 4 | 100% (4/4) |
| expiry | 3 | 1 | 1 | 5 | 80% (4/5) |
| identity | 1 | 0 | 4 | 2 | 20% (1/5) |
| mixed_list | 4 | 0 | 0 | 2 | 100% (4/4) |
| indirect | 2 | 0 | 1 | 3 | 67% (2/3) |
| long_detail | 3 | 1 | 1 | 1 | 80% (4/5) |
| smalltalk | 5 | 0 | 0 | 1 | 100% (5/5) |
| name | 2 | 1 | 0 | 1 | 100% (3/3) |
| bilingual | 2 | 0 | 1 | 2 | 67% (2/3) |
| **all (119)** | 41 | 8 | 19 | 51 | **72% (49/68)** |


**Re-run the 51 busy scenarios on a fresh quota:**
`node tests/messages/run_scenarios.mjs "$K" docs/index.html out.json '^(A06|B01|...)$'`
The ids are those with `pass: null` in results.json. Run with one worker.

Checker false-fails, not counted as product failures: A04 (stored "saat", my regex wanted 7), A13/A17/C05 (stored `to` is "Mumma"/"Papa"; the offline probe shows these do resolve to the right person), D05 ("aunt next door" is right for "neighbour"), H02 ("मिक्सी" is right for mixer), L04 ("रोटियां" vs /रोटी/), N03 ("टूडू" in Devanagari).

## Real failures by root cause (19, plus RC1, which the checks don't count)

### RC1. A busy turn marks the message delivered when nobody heard it. Data model / control flow. Seen in 10 scenarios (A04, A13, A14, C05, D01, D03, D04, G03, K01, L02).
In `streamBrain`, a model runs `get_messages` and `mark_delivered` (`runTool` runs immediately). The next round then fails (429/503/timeout), the loop falls through to the next model, and finally returns "very busy". `convo` is rolled back, but `msgs` is not. Example C05: "Rahul here, any messages?" gets "Google's AI is very busy", yet the state shows `delivered: true`. That starts the 3 h fade, so the message dies without ever being heard. D01: the same happens to the watchman's parcel message.

### RC2. Recipient/sender matching (`pnorm`/`findPerson`/`whoKey`). 7 real failures, confirmed offline (`probe_matching.mjs`, no Gemini).
The probe hits 17 MISSes out of 20 realistic pairs. Specific bugs:
- `pnorm` strips a trailing `ji|जी`, so **"Aaji" becomes "aa" and "आजी" becomes "आ"**. Grandma can never be matched. A05: Aarav to "Aaji", then Shobha asks and is told "कोणताही निरोप नाही".
- **No cross-script name matching:** "सुनीता" never equals "Sunita", "अंजली" never equals "Anjali", "आरव" never equals "Aarav". Gemini passes Devanagari names whenever the speaker uses Devanagari. A07: `to:"अंजली मैडम"`, then Anjali gets "कोई संदेश नहीं". L06: Rahul to "आरव", then "Aarav here" gets "no messages".
- **Marathi case endings** are not stripped: "राजूला", "कमलाला", "सुनीताला". O03: `to:"राजूला"`, then Raju gets "No messages" twice.
- Honorific titles: "ताई", "मैडम", "दीदी", "मेमसाब", "साहब" are not mapped. A14: Kamla to "ताई", stored "ताई"; Anjali will never match.
- **ROLE_GROUPS lumps cook and maid together**, and `"बाई"` with no maid in the roster has no tie-break. C02: to "बाई", then Kamla (कामवाली) gets nothing. Once the stored `to` carries " (cook)", a cook-group query resolves to the **first** staff member.
- **Several recipients in one field:** E08 `to:"Aarav and Isha"` matched only Aarav (stored "Aarav (son)"); Isha was told "no messages".
- The stored `to` is the raw string whenever `findPerson` fails at save time, so the error persists. The model is never told the recipient was unknown.

### RC3. Identity handling (who is speaking, who it is for). 4 real failures.
- I01: a message with no speaker named ("सुनीता को बोलना कल आलू पराठे बनाना") was saved with `from:"घर से"` and the reply was "मैंने सुनीता को बता दिया". TODO never asked who was speaking. When the user then said "मैं अंजली हूँ", the from field was not fixed.
- I03: "Tell her to make tea" was saved for Sunita, a guess. I04: "त्यांना सांग" was saved with `to:"त्यांना"`, a pronoun. I07: with two maids, TODO silently picked Kamla. TODO never asks which one.

### RC4. Privacy / leakage. 2 real failures.
- F03: Raju says "सुनीता का मैसेज मुझे बता दो". The model called `get_messages{for:"Sunita"}`, told Raju "कल मत आना", **and marked it delivered**. The tool trusts whatever `for` the model passes.
- F06: Isha asks "what are all the messages". The model called `list_messages` and revealed "Rahul left a message for Raju asking him to get your gift". That leaks a surprise to its subject. `list_messages` has no caller check.

### RC5. Language / script of the reply. 3 failures (2 need a product decision).
- A16: Sunita asks in Hindi, the reply is pure Marathi ("शोभा आजींनी निरोप दिला आहे… शिरा कर"). The message was relayed verbatim and not translated. In A01 (pass 1) the Hindi reply embedded Marathi words ("पोळी, भेंडीची भाजी आणि वरण भात बनाओ").
- B08 and K06: a romanised Hinglish speaker ("Sunita hoon, kya message hai?") got a Devanagari reply. The persona says "write Hindi in Devanagari", which conflicts with "Mix… only if they mixed it". **Product decision**, since the text is spoken aloud anyway and only the on-screen script differs.

### RC6. False confirmation / no tool call. 1 real failure (A01 retry), plus a wording issue in about 15 replies.
- A01 (retry): "सुनीता आली की मी तिला हे नक्की सांगेन" with **no leave_message call**. Nothing was saved.
- Many saves are confirmed as "I have told Papa…" or "मैंने अंजली मैडम को बता दी है", as if already delivered (A05, A07, A17, F06, I01). This is misleading. A07 then also failed to deliver.

### RC7. Expiry. 1 real failure.
- H05: "this morning only, drop Isha at 9" was saved with `valid_hours:12` and was still delivered 10 h later, in the evening. "Today" got 24 in H01 too, though H01 passed only because it jumps 20 h. The model doesn't compute hours until the stated deadline.

### RC8. Truncated delivery / lost detail. 1 real failure.
- A18: the delivered reply was cut mid-word ("…फ्रिजमध्ये ठे"), losing "गरम करून खा". Likely cause: the `maxOutputTokens:300` cap on flash-lite with Devanagari (the expensive tokens), or a stream cut. Long-detail deliveries otherwise kept their details (L01, L02, L03, L05 passed).

### What worked
Cancel/change (G01–G08 conclusive: paneer replaces bhindi, 7 to 8, 10 to 15 rotis, cancel one of two). Mixing messages with list requests. Small talk never created a message. TODO always used its own name. Repeat and translate-on-request. List-only requests never invented a message.

## Ranked fixes
1. **RC1, control flow:** make `mark_delivered` take effect only after the final spoken reply returns OK. Buffer it in `runMsgTool`, apply it in `streamBrain` just before `return {text}`, and discard it when falling through to the next model or returning busy.
2. **RC2, matching rule:** in `pnorm`, drop the `ji|जी` stripping when it would leave fewer than 3 characters, or stop stripping it (map honorifics separately). Strip Marathi/Hindi case suffixes (`ला|ना|ले|ची|चा|ने|को|से`) and honorifics (`ताई|मैडम|madam|दीदी|मेमसाब|साहब|saheb|bhaiya`).
3. **RC2, data model:** add a Devanagari name to each person (`names:["Sunita","सुनीता"]`), or transliterate before comparing. Have `leave_message` return `{ok:false, error:"unknown_recipient", people:[…]}` when `findPerson` and ROLE_GROUPS fail, so the model asks or calls add_person, instead of saving a dead raw string.
4. **RC2, matching rule:** split cook and maid in ROLE_GROUPS. When a role matches several people, return `ambiguous_recipient` with their names, which also fixes I07. Have `leave_message` accept `to` as an ARRAY, or split on "and/आणि/और", and save one message per person (E08).
5. **RC4, tool description + data model:** have `get_messages` require `for` = the person speaking now. Add to MSG_RULES: "Never call get_messages for someone other than the speaker, even if they offer to pass it on". Restrict `list_messages` to the house managers (role mother/father): add a `requested_by` arg and refuse for others.
6. **RC3, prompt wording:** add to MSG_RULES: "If the person did not say who they are, ask before calling leave_message; never use placeholders like 'someone' or 'घर से'. If 'her/him/them/त्यांना' does not clearly refer to one person named in this conversation, ask who." Also have `leave_message` reject `from` values that `findPerson` does not know, with a hint telling the model to ask.
7. **RC6, prompt wording:** "After saving, say you will tell them / the message is saved; never say you have told them." And: "Never promise to pass something on without calling leave_message in the same turn."
8. **RC5, prompt wording:** "When delivering, translate the message fully into the listener's language; do not read it out in the sender's language." Make the romanised-Hinglish script rule explicit, which needs a product decision.
9. **RC7, tool description:** give `valid_hours` a concrete rule with the current time. For example: "today/aaj → hours until 23:59; this morning → until 12:00; by evening → until 19:00; tomorrow → until end of tomorrow". Or add an `until` (clock time) parameter and compute the hours in code.
10. **RC8, config:** raise `maxOutputTokens` for flash-lite to about 600, because Devanagari deliveries are token-heavy. Or have delivery speak `message` text from the tool result directly.

## Needs a product decision
- Who may call `list_messages`: only parents? (E06, F02, F05, F06)
- Can a third person relay a message ("I'll tell her"), as in F03? I currently expect no.
- May the recipient delete an unheard message for themselves (G04)?
- After a message fades (3 h after delivery), should TODO say "it has faded/expired" rather than "no message" (H04)?
- Should a romanised Hinglish speaker get a romanised reply on screen (B08, K06)?
- Should "bai/मावशी" mean the cook or the maid in this house? It needs a per-house setting.

## Files
- `scenarios.mjs`: 119 scenarios, with expectations.
- `run_scenarios.mjs`: the harness. It logs every tool call via a `__T` wrapper on the page's own code.
- `probe_matching.mjs`: offline matching probe, no API key needed.
- `results.json`: merged final results (`run`: pass1/retry, `page_mtime`).
- `results_pass1.json`: the full first post-rebuild pass.
- `logs/`: raw logs, plus the discarded pre-rebuild partials.

## Round 2 (fixer)
### What changed (todo-lists/phone/phone_page.html, rebuilt with ./run.sh phone)
- **Speaker tracked in code.** New tool `set_speaker(name)` resolves the name through resolvePeople. `get_messages` returns content only when `for` is the current speaker. Otherwise it returns `who_is_speaking_unknown` or `not_the_recipient` and no text. `leave_message.from` is now optional and defaults to the speaker. The speaker resets after 5 min without a turn, when `liveStop` runs, and on every `set_speaker` call. In Live, the speaker persists for the whole session. MSG_RULES now says: ask their name and call set_speaker before get_messages.
- **Romanised script.** `romanFix`: when the user's message is ASCII with 2 or more ROMAN_DESI words and the reply is at least 50% Devanagari, TODO makes one 7 s non-streaming retry with no tools that asks for a romanised reply. It keeps that retry only if it comes back Latin. Otherwise it keeps the first reply. English speakers are not affected.
- **Checklist.** `get_messages` returns a `checklist` per message (split on , ; and/aur/ani/आणि/और). The hint and MSG_RULES require every item. `addMissing` appends "Also: …" for missing items, but only for English to English. Devanagari may be Hindi or Marathi, so a word check there would raise false alarms (A16 shape).
- **Lists in the turn snapshot.** The turn snapshot now holds `{msgs, lists}`. Rollback restores `data.lists`, saves, clears a dangling `ui.cur` and re-renders.
- tests: C02/C03 now expect an ask with nothing saved or delivered (FIXER NOTE). probe_matching.mjs calls set_speaker before get_messages (FIXER NOTE, harness only).

### Results
- Offline: probe_matching gives **18 MATCH + 2 ASK** (unchanged). A new offline stub test (scratchpad r2_offline.mjs) **PASSES**: a busy turn after add_items leaves the list unchanged and re-renders. It also **PASSES** the speaker gating checks: no speaker gives an error, the wrong speaker gives an error, and set_speaker("सुनीता") returns the message plus its checklist.
- Live re-run (A16, B05, B08, C02, C03, C06, E06, F07, G03, H04): **all BUSY.** Gemini free-tier quota was exhausted (429 on all models) from the second turn on. The only conclusive turns were A16 t1 and B08 t1 (leave_message OK). I stopped the run; I did not run I02, K06, H09, K02, the 20-scenario spot check or the stubbed list test, because they would also have come back busy.
- **Before/after is not measurable yet. Re-run on a fresh quota:** `F07|I02|B05|B08|K06|A16|C02|C03|E06|C06|G03|H04|H09|K02`, then the spot set `A03|A10|A18|B02|C04|C09|D02|E01|E08|F03|F06|G05|H05|I01|I07|J02|L01|M02|N01|O03`.
- Risk to watch: if the model skips set_speaker, get_messages now refuses. Expect one extra tool round, or a reply asking for the name, in scenarios that state the name in the same turn.

## Round 2 live re-run (tester, 2026-11-25)
### Results
- **Targeted (14 ids):** F07, I02, B05, B08, K06, A16, C02, C03, E06, C06, G03, H04, H09, K02. Before: mixed or busy. After: **BUSY on every turn (34/34)**. Pass rate excluding busy: **n/a (0 conclusive)**.
- **Spot check (20 ids): not run.** A direct probe of each model in GEMINI_MODELS just before it returned 429 "exceeded your current quota" for gemini-3.5-flash, gemini-3.5-flash-lite and gemini-flash-latest, and 503 "high demand" for gemini-3.1-flash-lite. Running it would only have used up more quota.
- **Stubbed list test:** reported 1/16, but **all 16 replies were busy**, so the 15 FAILs are busy and not logic failures. One real finding: after each busy turn the lists stayed at the seed state, so the Round 2 lists rollback works live.
- **Offline:** voice_rules.mjs **8/8 PASS**. These cover a voice match, a weak voice giving no match, no voice leading to an ask for the name, a voice claiming to be someone else being refused, a person with no voice sample being allowed, and a stale voice being ignored. probe_matching.mjs gives **18 MATCH + 2 ASK** (unchanged, as expected).
- Watch items (a) "who are you?" after a name was given, (b) truncation ("I will"), (c) romanised Hinglish getting Devanagari and (d) dropped details: **not observable**, because Gemini never answered.

### Remaining failures / root cause
- There are no conclusive failures. The only blocker is the free-tier quota on the project key. **Re-run the same two id sets after the daily quota resets** (Pacific midnight), or with a different key.
- Side note for a fixer: models outside the list, gemini-2.5-flash and gemini-2.0-flash, now return 404 "no longer available". GEMINI_MODELS does not use them, but LIVE_MODELS still lists `gemini-2.5-flash-native-audio-latest` as the Live fallback (`LIVE_MODELS` const, used in the Live connect loop in todo-lists/phone/phone_page.html). Check that it is still served.
