from __future__ import annotations

import json
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Any


class LLMError(RuntimeError):
    """Raised when the remote language model cannot return a usable answer."""


@dataclass
class OpenAICompatibleChatClient:
    api_key: str | None
    base_url: str
    model: str
    timeout: int = 90

    def complete(self, messages: list[dict[str, str]]) -> str:
        if not self.api_key:
            raise LLMError(
                "Missing API key. Set AGENT_API_KEY or OPENAI_API_KEY before running the agent."
            )

        payload: dict[str, Any] = {
            "model": self.model,
            "messages": messages,
            "temperature": 0.2,
        }
        data = json.dumps(payload).encode("utf-8")
        request = urllib.request.Request(
            f"{self.base_url.rstrip('/')}/chat/completions",
            data=data,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )

        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                body = response.read().decode("utf-8")
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            raise LLMError(f"Model request failed with HTTP {exc.code}: {detail}") from exc
        except urllib.error.URLError as exc:
            raise LLMError(f"Model request failed: {exc.reason}") from exc

        try:
            decoded = json.loads(body)
            content = decoded["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError, json.JSONDecodeError) as exc:
            raise LLMError(f"Unexpected model response: {body[:1000]}") from exc

        if isinstance(content, list):
            return "\n".join(str(item.get("text", item)) for item in content)
        return str(content)

