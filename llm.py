"""Thin wrapper around the Anthropic API shared by all agents."""
from __future__ import annotations

import json
import os
import re

from . import config


def extract_json(text: str):
    """Parse JSON from a model reply, tolerating code fences and stray prose."""
    text = re.sub(r"^```(?:json)?\s*|\s*```$", "", text.strip(), flags=re.M).strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        start, end = text.find("{"), text.rfind("}")
        if start != -1 and end > start:
            return json.loads(text[start : end + 1])
        raise


class LLMClient:
    def __init__(self, api_key: str | None = None, model: str | None = None):
        import anthropic  # imported lazily so tests don't need the SDK

        key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not key:
            raise ValueError("No Anthropic API key found. Set ANTHROPIC_API_KEY or enter it in the UI.")
        self._client = anthropic.Anthropic(api_key=key)
        self.model = model or config.MODEL

    def complete(self, system: str, user: str, max_tokens: int = 1500, temperature: float = 0.3) -> str:
        resp = self._client.messages.create(
            model=self.model,
            max_tokens=max_tokens,
            temperature=temperature,
            system=system,
            messages=[{"role": "user", "content": user}],
        )
        return "".join(b.text for b in resp.content if b.type == "text")

    def complete_json(self, system: str, user: str, max_tokens: int = 1500, retries: int = 1):
        system += "\n\nRespond with a single valid JSON object only. No prose, no code fences."
        last_err = None
        for _ in range(retries + 1):
            raw = self.complete(system, user, max_tokens=max_tokens, temperature=0.2)
            try:
                return extract_json(raw)
            except json.JSONDecodeError as e:
                last_err = e
        raise ValueError(f"Model did not return valid JSON: {last_err}")
