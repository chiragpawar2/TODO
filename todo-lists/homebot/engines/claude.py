"""The Claude engine - kept available as a paid upgrade path.

Costs more than the free tiers but is the most reliable at picking the right
action from a messy spoken sentence. Switch to it by setting
`engine: claude` in config.yaml.
"""

from __future__ import annotations

import os
from typing import Any

from .base import Engine, Reply, ToolCall

DEFAULT_MODEL = "claude-haiku-4-5"


class ClaudeEngine(Engine):
    name = "claude"

    def __init__(self, model: str | None, max_tokens: int, effort: str | None = None):
        try:
            import anthropic
        except ImportError as e:  # pragma: no cover - dependency guidance
            raise RuntimeError(
                "The 'anthropic' package is required for this engine.\n"
                "  pip install -r requirements.txt"
            ) from e

        if not os.environ.get("ANTHROPIC_API_KEY"):
            raise RuntimeError(
                self.describe_missing_key(
                    "ANTHROPIC_API_KEY", "https://console.anthropic.com/settings/keys"
                )
            )

        self.client = anthropic.Anthropic()
        self.model = model or DEFAULT_MODEL
        self.max_tokens = max_tokens
        self.effort = effort

    @staticmethod
    def _messages(messages: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Neutral format -> Anthropic content blocks.

        Consecutive tool results must be merged into one user turn; sending them
        as separate turns teaches the model to stop calling tools in parallel.
        """
        out: list[dict[str, Any]] = []
        for m in messages:
            if m["role"] == "user":
                out.append({"role": "user", "content": m["text"]})
            elif m["role"] == "assistant":
                blocks: list[dict[str, Any]] = []
                if m.get("text"):
                    blocks.append({"type": "text", "text": m["text"]})
                for c in m.get("tool_calls", []):
                    blocks.append(
                        {"type": "tool_use", "id": c.id, "name": c.name, "input": c.args}
                    )
                out.append({"role": "assistant", "content": blocks})
            elif m["role"] == "tool":
                block = {
                    "type": "tool_result",
                    "tool_use_id": m["id"],
                    "content": m["content"],
                }
                if out and out[-1]["role"] == "user" and isinstance(out[-1]["content"], list):
                    out[-1]["content"].append(block)
                else:
                    out.append({"role": "user", "content": [block]})
        return out

    def complete(self, system, messages, tools) -> Reply:
        kwargs: dict[str, Any] = {
            "model": self.model,
            "max_tokens": self.max_tokens,
            # Marking the system prompt cacheable bills it at about 10% on
            # repeat calls. Volatile text is kept out of it by brain.py.
            "system": [
                {"type": "text", "text": system, "cache_control": {"type": "ephemeral"}}
            ],
            "tools": [
                {
                    "name": t["name"],
                    "description": t["description"],
                    "input_schema": t["input_schema"],
                }
                for t in tools
            ],
            "messages": self._messages(messages),
        }
        # Haiku 4.5 rejects the effort setting, so only send it when asked for.
        if self.effort:
            kwargs["output_config"] = {"effort": self.effort}

        response = self.client.messages.create(**kwargs)

        if response.stop_reason == "refusal":
            return Reply(refused=True)

        text = "".join(b.text for b in response.content if b.type == "text").strip()
        calls = [
            ToolCall(id=b.id, name=b.name, args=dict(b.input))
            for b in response.content
            if b.type == "tool_use"
        ]
        return Reply(text=text, tool_calls=calls)
