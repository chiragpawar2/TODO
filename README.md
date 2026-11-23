# homebot

A home assistant for the family: a character on a small screen, and the lists and tasks it looks after.

## Project layout

| Folder | What lives there |
|---|---|
| `todo-character/` | Everything about the character. `homebot/face/` (renderer, expressions, animator, sentence reader, lip sync), `tests/` (all expression and conversation suites), `design/` (references, pitch sheets, prompts, research), `prototypes/` (the phone/web build of the face), `explorations/` (the scripts that made the sheets, and the fixer's check scripts), `models/` (the local emotion model, not in git). |
| `todo-lists/` | Everything about the to-do and list experience. `homebot/` (brain, store, tools, engines, server, web), `config.example.yaml`, the local database, and `prototype/` (the lists screen, built with `prototype/build.py`). |

`homebot` is one Python package split across the two folders, so imports such as `homebot.face` and `homebot.brain` work unchanged.

## Run

```bash
./run.sh face      # the character on screen
./run.sh tests     # character test suites
./run.sh server    # web/API server
./run.sh cli       # text chat
```

---

# homebot

A home AI assistant for the whole family. It keeps track of everyone's tasks,
the household chores, the shopping list, and the small facts worth remembering —
and every phone and laptop in the house talks to the same bot.

Runs on a laptop today. The same code moves to a Raspberry Pi or an old phone
later, with a microphone and speaker attached, without changes.

---

## Setup

**1. Python 3.10 or newer.** Your Mac ships with 3.9, which the Claude library
does not support:

```bash
brew install python@3.12
```

**2. Create an isolated environment and install the libraries:**

```bash
cd ~/Desktop/Personal/TODO
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

**3. Get a free API key.** The default engine is Google Gemini, which has a
free tier and needs no credit card. Create a key at
https://aistudio.google.com/apikey

```bash
cp .env.example .env
```

Then open `.env` and paste the key after `GEMINI_API_KEY=`.

**4. Describe your household:**

```bash
cp config.example.yaml config.yaml
```

Open `config.yaml` and put in the real names of the people in your house.

---

## Use it

**Talk by typing** (start here):

```bash
python -m homebot.cli --speaker Chirag
```

Try saying things like:

- `remind me to pay the electricity bill on Friday`
- `add 2 litres of milk to the shopping list`
- `whose turn is it to wash the dishes?`
- `Aai is allergic to peanuts, remember that`
- `what do I have to do today?`

Add `--verbose` to watch every action it takes behind the scenes.

**Open it on phones and laptops:**

```bash
python -m homebot.server
```

Then on this machine open http://localhost:8080. On a phone, find this
machine's WiFi address and use that instead:

```bash
ipconfig getifaddr en0
```

Everyone sees the same tasks, chores and shopping list, live.

---

## How it works

```
   You speak  ──▶  brain.py  ──▶  engines/  ──▶  Gemini, Groq, Ollama
                      │                 │            or Claude
                      │                 └── decides which action to take
                      ▼
                  tools.py  ──▶  store.py  ──▶  homebot.db
                                                (one SQLite file =
                                                 your whole household)
```

| File | What it does |
|---|---|
| `homebot/config.py` | Reads `config.yaml` |
| `homebot/store.py` | The household memory — people, tasks, chores, shopping, facts |
| `homebot/tools.py` | The 14 actions the bot can perform |
| `homebot/brain.py` | The conversation loop that lets the AI use those actions |
| `homebot/engines/` | One file per AI provider — swap by editing `config.yaml` |
| `homebot/cli.py` | Talk by typing |
| `homebot/server.py` | Web API for phones and laptops |
| `homebot/web/index.html` | The page the family opens |

The whole household lives in `homebot.db`. Copy that one file and you have
moved or backed up everything.

---

## Choosing the AI

Change one line in `config.yaml` to switch provider. Nothing else changes —
Gemini, Groq, OpenRouter, Cerebras and Ollama all speak the same dialect, so
they share a single adapter.

| `engine:` | Cost | Notes |
|---|---|---|
| `gemini` | **free** | The default. Most generous free tier, good at picking the right action |
| `groq` | **free** | Very fast — the best choice once voice is added. 200K tokens/day cap |
| `openrouter` | **free** | Many models from one key. 50 requests/day until you top up |
| `cerebras` | **free** | Very fast |
| `ollama` | **free forever** | Runs on your own Mac. No key, works offline, nothing leaves the house |
| `claude` | ~$1.50/month | The most reliable at understanding messy spoken requests |

**A privacy note worth knowing.** On free hosted tiers — Gemini's included —
your prompts and replies may be used to improve the provider's models, and
human reviewers may see them. For a device listening in your living room, that
is worth a thought. `ollama` is the only option where nothing ever leaves your
house. Switching to it is one line.

**What keeps usage low**, whichever engine you pick:

| Setting | Why |
|---|---|
| `history_turns: 8` | Only recent conversation is resent, not the whole day |
| `max_tokens: 800` | Replies stay short; output is the expensive part |

On the Claude engine the unchanging part of the prompt is also marked
cacheable, billing at about 10% on repeat calls. Volatile things — the clock,
who is speaking — are deliberately kept out of that cached part, which is the
mistake that normally destroys caching savings.

Using `claude`? Leave `effort:` blank for Haiku — it rejects that setting.

---

## Where this is going

- [x] Stage 1 — talk by typing, on a laptop
- [x] Stage 2 — memory and real actions (tasks, chores, shopping, facts)
- [x] Stage 4 — phones and laptops on the home WiFi
- [ ] Stage 3 — voice: microphone in, speaker out
- [ ] Stage 5 — wake word, so nobody has to press anything
- [ ] Move onto a Raspberry Pi or an old phone, starting automatically on boot

Voice will use Whisper for listening and Piper for speaking. Both run on the
device itself and are free, so your raw audio never leaves the house — only
text goes to the cloud.
