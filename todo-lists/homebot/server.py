"""Web server, so every phone and laptop on your WiFi talks to the same bot.

    python -m homebot.server

Then open http://<this-machine-ip>:8080 on any phone on the same WiFi.
Find the IP with:  ipconfig getifaddr en0   (macOS)
"""

from __future__ import annotations

from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel

from .brain import Brain
from .config import load_config
from .engines import make_engine
from .store import Store

WEB_DIR = Path(__file__).parent / "web"

load_dotenv()

config = load_config()
store = Store(config.resolved_db_path)
for _person in config.people:
    store.upsert_person(_person.name, _person.role, _person.notes)

# Built once at startup so a missing key fails immediately and loudly, rather
# than on the first message someone sends. The engine holds no per-user state,
# so every family member's Brain can share it.
engine = make_engine(config)

# One Brain per speaker, so each family member keeps their own conversation
# thread instead of everyone sharing one confusing history.
_brains: dict[str, Brain] = {}


def brain_for(speaker: str) -> Brain:
    if speaker not in _brains:
        _brains[speaker] = Brain(config, store, engine=engine)
    return _brains[speaker]


app = FastAPI(title="homebot")


class ChatIn(BaseModel):
    speaker: str
    text: str


class ItemIn(BaseModel):
    item: str
    qty: str = ""


@app.get("/")
def index() -> FileResponse:
    return FileResponse(WEB_DIR / "index.html")


@app.get("/api/state")
def state() -> dict:
    return {
        "household": config.household_name,
        "people": [p["name"] for p in store.list_people()],
        "tasks": store.list_tasks(status="open"),
        "chores": store.list_chores(),
        "shopping": store.list_shopping(),
        "facts": store.recall(),
    }


@app.post("/api/chat")
def chat(body: ChatIn) -> dict:
    if not body.text.strip():
        raise HTTPException(400, "Empty message.")
    store.upsert_person(body.speaker)
    try:
        reply = brain_for(body.speaker).ask(body.text, speaker=body.speaker)
    except Exception as e:
        raise HTTPException(502, f"{type(e).__name__}: {e}") from e
    return {"reply": reply}


@app.post("/api/task/{task_id}/complete")
def complete(task_id: int) -> dict:
    task = store.complete_task(task_id)
    if not task:
        raise HTTPException(404, f"No task with id {task_id}.")
    return task


@app.post("/api/shopping")
def add_item(body: ItemIn) -> dict:
    if not body.item.strip():
        raise HTTPException(400, "Empty item.")
    return store.add_shopping(body.item.strip(), body.qty.strip())


@app.post("/api/shopping/bought")
def bought(body: ItemIn) -> dict:
    row = store.mark_bought(body.item)
    if not row:
        raise HTTPException(404, f"'{body.item}' is not on the list.")
    return row


def main() -> None:
    import uvicorn

    print(f"homebot server for {config.household_name} (engine: {engine.name})")
    print(f"  open http://localhost:{config.server.port} on this machine")
    print("  on a phone, use this machine's WiFi IP instead of localhost")
    uvicorn.run(app, host=config.server.host, port=config.server.port)


if __name__ == "__main__":
    main()
