"""Loads config.yaml into plain dataclasses."""

from __future__ import annotations

from dataclasses import dataclass, field, fields
from pathlib import Path

import yaml

PROJECT_ROOT = Path(__file__).resolve().parent.parent


@dataclass
class Person:
    name: str
    role: str = "member"
    notes: str = ""


@dataclass
class BrainConfig:
    # gemini | groq | openrouter | cerebras | ollama | claude
    engine: str = "gemini"
    # None means "use the engine's own default" - see engines/openai_compat.py
    model: str | None = None
    base_url: str | None = None
    api_key_env: str | None = None
    effort: str | None = None          # Claude only; Haiku rejects it
    max_tokens: int = 800
    history_turns: int = 8

    @classmethod
    def from_raw(cls, raw: dict) -> "BrainConfig":
        """Ignore unknown keys so an old config file keeps working."""
        known = {f.name for f in fields(cls)}
        unknown = set(raw) - known
        if unknown:
            print(f"[homebot] Ignoring unknown brain settings: {', '.join(sorted(unknown))}")
        return cls(**{k: v for k, v in raw.items() if k in known})


@dataclass
class ServerConfig:
    host: str = "0.0.0.0"
    port: int = 8080


@dataclass
class Config:
    household_name: str = "our home"
    room: str = "living room"
    people: list[Person] = field(default_factory=list)
    languages: list[str] = field(default_factory=lambda: ["English"])
    brain: BrainConfig = field(default_factory=BrainConfig)
    server: ServerConfig = field(default_factory=ServerConfig)
    db_path: str = "homebot.db"

    @property
    def resolved_db_path(self) -> Path:
        path = Path(self.db_path)
        return path if path.is_absolute() else PROJECT_ROOT / path


def load_config(path: str | Path | None = None) -> Config:
    """Read config.yaml, falling back to config.example.yaml if it doesn't exist yet."""
    if path is None:
        path = PROJECT_ROOT / "config.yaml"
        if not path.exists():
            example = PROJECT_ROOT / "config.example.yaml"
            if not example.exists():
                raise FileNotFoundError(
                    "No config.yaml found. Copy config.example.yaml to config.yaml."
                )
            print("[homebot] No config.yaml yet - using config.example.yaml.")
            path = example

    raw = yaml.safe_load(Path(path).read_text()) or {}

    return Config(
        household_name=raw.get("household_name", "our home"),
        room=raw.get("room", "living room"),
        people=[
            Person(
                name=p["name"],
                role=p.get("role", "member"),
                notes=p.get("notes", ""),
            )
            for p in raw.get("people", [])
        ],
        languages=raw.get("languages") or ["English"],
        brain=BrainConfig.from_raw(raw.get("brain") or {}),
        server=ServerConfig(**(raw.get("server") or {})),
        db_path=raw.get("db_path", "homebot.db"),
    )
