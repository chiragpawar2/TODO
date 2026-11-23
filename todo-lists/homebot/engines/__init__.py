"""Picks the AI engine named in config.yaml."""

from __future__ import annotations

from ..config import Config
from .base import Engine, Reply, ToolCall
from .claude import ClaudeEngine
from .openai_compat import PRESETS, OpenAICompatEngine

__all__ = ["Engine", "Reply", "ToolCall", "make_engine", "PRESETS"]


def make_engine(config: Config) -> Engine:
    brain = config.brain
    engine = (brain.engine or "gemini").lower()

    if engine == "claude":
        return ClaudeEngine(
            model=brain.model, max_tokens=brain.max_tokens, effort=brain.effort
        )

    return OpenAICompatEngine(
        engine=engine,
        model=brain.model,
        base_url=brain.base_url,
        api_key_env=brain.api_key_env,
        max_tokens=brain.max_tokens,
    )
