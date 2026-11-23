"""What every engine must provide, and the neutral message format they share.

brain.py never learns which provider is in use. It builds a conversation in the
neutral format below, hands it to an engine, and gets a Reply back. Each engine
translates to and from its provider's own dialect.

Neutral message shapes:
    {"role": "user",      "text": str}
    {"role": "assistant", "text": str, "tool_calls": [ToolCall]}
    {"role": "tool",      "id": str, "name": str, "content": str}
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


@dataclass
class ToolCall:
    id: str
    name: str
    args: dict[str, Any]


@dataclass
class Reply:
    text: str = ""
    tool_calls: list[ToolCall] = field(default_factory=list)
    refused: bool = False


class Engine(ABC):
    """One AI provider."""

    name: str = "engine"

    @abstractmethod
    def complete(
        self,
        system: str,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]],
    ) -> Reply:
        """Send one request. `tools` uses the neutral schema from tools.py."""

    @staticmethod
    def describe_missing_key(env_var: str, where: str) -> str:
        return (
            f"No {env_var} found.\n"
            f"  1. Get a free key at {where}\n"
            f"  2. Add this line to your .env file:\n"
            f"     {env_var}=your-key-here"
        )
