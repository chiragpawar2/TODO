"""Talk to the bot by typing. This is Stage 1 - no microphone needed yet.

    python -m homebot.cli
    python -m homebot.cli --speaker Chirag --verbose
"""

from __future__ import annotations

import argparse
import sys

from dotenv import load_dotenv

from .brain import Brain
from .config import load_config
from .store import Store

BANNER = """
homebot - {household}
Type what you would say out loud. Commands:
  /who NAME     say who is talking now
  /state        print what the bot currently knows
  /quit         exit
"""


def main() -> int:
    parser = argparse.ArgumentParser(description="Chat with the home assistant.")
    parser.add_argument("--speaker", help="Who is talking, e.g. --speaker Chirag")
    parser.add_argument("--config", help="Path to a config file")
    parser.add_argument("--verbose", action="store_true", help="Show each tool call")
    args = parser.parse_args()

    load_dotenv()
    config = load_config(args.config)
    store = Store(config.resolved_db_path)

    # Make sure everyone from config.yaml exists in the database.
    for person in config.people:
        store.upsert_person(person.name, person.role, person.notes)

    try:
        brain = Brain(config, store)
    except RuntimeError as e:
        # Missing key, missing package, or an unknown engine name.
        print(f"\n{e}\n", file=sys.stderr)
        store.close()
        return 1

    speaker = args.speaker or (config.people[0].name if config.people else None)

    print(BANNER.format(household=config.household_name))
    print(f"(engine: {brain.engine.name} - speaking as {speaker or 'unknown'}, change with /who NAME)\n")

    try:
        while True:
            try:
                text = input(f"{speaker or 'you'} > ").strip()
            except (EOFError, KeyboardInterrupt):
                print()
                break

            if not text:
                continue
            if text in ("/quit", "/exit"):
                break
            if text.startswith("/who"):
                parts = text.split(maxsplit=1)
                if len(parts) == 2:
                    speaker = parts[1].strip()
                    store.upsert_person(speaker)
                    print(f"  now speaking as {speaker}")
                else:
                    print("  usage: /who NAME")
                continue
            if text == "/state":
                print(store.briefing() or "  (nothing known yet)")
                continue

            try:
                reply = brain.ask(text, speaker=speaker, verbose=args.verbose)
            except Exception as e:
                print(f"  [error] {type(e).__name__}: {e}", file=sys.stderr)
                continue

            print(f"bot > {reply}\n")
    finally:
        store.close()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
