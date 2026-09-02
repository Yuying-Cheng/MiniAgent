from __future__ import annotations

import json
from typing import Any

from .llm import OpenAICompatibleChatClient
from .prompts import SYSTEM_PROMPT
from .tools import WorkspaceTools


class MiniCodexAgent:
    def __init__(
        self,
        client: OpenAICompatibleChatClient,
        tools: WorkspaceTools,
        *,
        max_steps: int = 10,
        max_context_chars: int = 60000,
        verbose: bool = True,
    ) -> None:
        self.client = client
        self.tools = tools
        self.max_steps = max_steps
        self.max_context_chars = max_context_chars
        self.verbose = verbose

    def run(self, task: str) -> str:
        messages: list[dict[str, str]] = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": task},
        ]

        for step in range(1, self.max_steps + 1):
            messages = self._compact(messages)
            raw = self.client.complete(messages)
            decision = self._parse_decision(raw)

            thought = str(decision.get("thought", "")).strip()
            action = decision.get("action")
            if self.verbose:
                print(f"\n[{step}/{self.max_steps}] {thought or '(no thought)'}")

            if action == "final":
                answer = str(decision.get("answer", "")).strip()
                if self.verbose:
                    print(f"\nFinal:\n{answer}")
                return answer

            if action != "tool":
                messages.append({"role": "assistant", "content": raw})
                messages.append(
                    {
                        "role": "user",
                        "content": 'Invalid action. Reply with action="tool" or action="final" JSON only.',
                    }
                )
                continue

            tool_name = str(decision.get("tool", "")).strip()
            args = decision.get("args", {})
            if not isinstance(args, dict):
                args = {}
            result = self.tools.execute(tool_name, args)

            if self.verbose:
                status = "ok" if result.success else "failed"
                preview = result.content[:1200]
                print(f"Tool {tool_name} {status}:\n{preview}")

            messages.append({"role": "assistant", "content": raw})
            messages.append(
                {
                    "role": "user",
                    "content": (
                        f"Tool result for {tool_name}:\n{result.to_json()}\n"
                        "Continue. Use final when the task is complete."
                    ),
                }
            )

        answer = f"Stopped after reaching max_steps={self.max_steps}. The task may be incomplete."
        if self.verbose:
            print(f"\nFinal:\n{answer}")
        return answer

    def _parse_decision(self, raw: str) -> dict[str, Any]:
        text = raw.strip()
        if text.startswith("```"):
            text = text.strip("`")
            if text.startswith("json"):
                text = text[4:].strip()

        try:
            return json.loads(text)
        except json.JSONDecodeError:
            start = text.find("{")
            end = text.rfind("}")
            if start != -1 and end != -1 and end > start:
                try:
                    return json.loads(text[start : end + 1])
                except json.JSONDecodeError:
                    pass
        return {
            "thought": "The model returned invalid JSON.",
            "action": "invalid",
            "raw": raw,
        }

    def _compact(self, messages: list[dict[str, str]]) -> list[dict[str, str]]:
        total = sum(len(message["content"]) for message in messages)
        if total <= self.max_context_chars or len(messages) <= 4:
            return messages

        system = messages[0]
        recent = messages[-8:]
        summary = {
            "role": "user",
            "content": (
                "Older interaction history was compacted to keep the context small. "
                "Continue using the latest tool results and task state."
            ),
        }
        return [system, summary, *recent]

