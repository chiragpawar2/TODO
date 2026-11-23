"""One engine for Gemini, Groq, OpenRouter, Cerebras and Ollama.

All of them expose the same OpenAI-shaped chat API, so they differ only by
base URL, model name and which environment variable holds the key. That is why
switching provider is a one-line change in config.yaml.
"""

from __future__ import annotations

import json
import os
from typing import Any

from .base import Engine, Reply, ToolCall

# base_url, default model, env var holding the key, where to get one
PRESETS: dict[str, dict[str, Any]] = {
    "gemini": {
        "base_url": "https://generativelanguage.googleapis.com/v1beta/openai/",
        "model": "gemini-3.8-flash",
        "api_key_env": "GEMINI_API_KEY",
        "signup": "https://aistudio.google.com/apikey",
    },
    "groq": {
        "base_url": "https://api.groq.com/openai/v1",
        "model": "openai/gpt-oss-120b",
        "api_key_env": "GROQ_API_KEY",
        "signup": "https://console.groq.com/keys",
    },
    "openrouter": {
        "base_url": "https://openrouter.ai/api/v1",
        "model": "qwen/qwen3-8b:free",
        "api_key_env": "OPENROUTER_API_KEY",
        "signup": "https://openrouter.ai/keys",
    },
    "cerebras": {
        "base_url": "https://api.cerebras.ai/v1",
        "model": "qwen-3-32b",
        "api_key_env": "CEREBRAS_API_KEY",
        "signup": "https://cloud.cerebras.ai",
    },
    "ollama": {
        "base_url": "http://localhost:11434/v1",
        "model": "qwen3:8b",
        "api_key_env": None,  # a local model needs no key
        "signup": "https://ollama.com (then: ollama pull qwen3:8b)",
    },
}


class OpenAICompatEngine(Engine):
    def __init__(self, engine: str, model: str | None, base_url: str | None,
                 api_key_env: str | None, max_tokens: int):
        try:
            from openai import OpenAI
        except ImportError as e:  # pragma: no cover - dependency guidance
            raise RuntimeError(
                "The 'openai' package is required for this engine.\n"
                "  pip install -r requirements.txt"
            ) from e

        preset = PRESETS.get(engine, {})
        self.name = engine
        self.model = model or preset.get("model")
        self.max_tokens = max_tokens
        base = base_url or preset.get("base_url")
        env_var = api_key_env or preset.get("api_key_env")

        if not base:
            raise RuntimeError(
                f"Engine '{engine}' is not a known preset, so config.yaml must set "
                f"brain.base_url and brain.model explicitly. "
                f"Known presets: {', '.join(PRESETS)}."
            )

        key = os.environ.get(env_var) if env_var else None
        if env_var and not key:
            raise RuntimeError(self.describe_missing_key(env_var, preset.get("signup", "")))

        # Ollama needs no key but the client insists on a non-empty string.
        self.client = OpenAI(api_key=key or "not-needed", base_url=base)

    # --- translation to the OpenAI dialect ---------------------------------

    @staticmethod
    def _tools(tools: list[dict[str, Any]]) -> list[dict[str, Any]]:
        return [
            {
                "type": "function",
                "function": {
                    "name": t["name"],
                    "description": t["description"],
                    "parameters": t["input_schema"],
                },
            }
            for t in tools
        ]

    @staticmethod
    def _messages(system: str, messages: list[dict[str, Any]]) -> list[dict[str, Any]]:
        out: list[dict[str, Any]] = [{"role": "system", "content": system}]
        for m in messages:
            if m["role"] == "user":
                out.append({"role": "user", "content": m["text"]})
            elif m["role"] == "assistant":
                entry: dict[str, Any] = {"role": "assistant", "content": m.get("text") or None}
                if m.get("tool_calls"):
                    entry["tool_calls"] = [
                        {
                            "id": c.id,
                            "type": "function",
                            "function": {"name": c.name, "arguments": json.dumps(c.args)},
                        }
                        for c in m["tool_calls"]
                    ]
                out.append(entry)
            elif m["role"] == "tool":
                out.append(
                    {"role": "tool", "tool_call_id": m["id"], "content": m["content"]}
                )
        return out

    # --- the request -------------------------------------------------------

    def complete(self, system, messages, tools) -> Reply:
        response = self.client.chat.completions.create(
            model=self.model,
            max_tokens=self.max_tokens,
            messages=self._messages(system, messages),
            tools=self._tools(tools),
            tool_choice="auto",
        )
        choice = response.choices[0].message

        calls: list[ToolCall] = []
        for call in getattr(choice, "tool_calls", None) or []:
            # Arguments arrive as a JSON string. Smaller open models sometimes
            # emit malformed JSON, so a bad parse becomes an empty-args call
            # rather than a crash - dispatch() will report the missing argument
            # and the model gets a chance to correct itself.
            try:
                args = json.loads(call.function.arguments or "{}")
            except (json.JSONDecodeError, TypeError):
                args = {}
            if not isinstance(args, dict):
                args = {}
            calls.append(ToolCall(id=call.id, name=call.function.name, args=args))

        return Reply(text=(choice.content or "").strip(), tool_calls=calls)
