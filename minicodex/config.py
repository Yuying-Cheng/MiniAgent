from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class AgentConfig:
    api_key: str | None
    base_url: str
    model: str
    workspace: Path
    max_steps: int = 10
    request_timeout: int = 90
    command_timeout: int = 30
    max_tool_output_chars: int = 6000
    max_context_chars: int = 60000

    @classmethod
    def from_env(
        cls,
        *,
        workspace: str | None = None,
        model: str | None = None,
        base_url: str | None = None,
        max_steps: int | None = None,
    ) -> "AgentConfig":
        return cls(
            api_key=os.getenv("AGENT_API_KEY") or os.getenv("OPENAI_API_KEY"),
            base_url=(
                base_url
                or os.getenv("AGENT_BASE_URL")
                or os.getenv("OPENAI_BASE_URL")
                or "https://api.openai.com/v1"
            ).rstrip("/"),
            model=model or os.getenv("AGENT_MODEL") or os.getenv("OPENAI_MODEL") or "gpt-4o-mini",
            workspace=Path(workspace or os.getcwd()).resolve(),
            max_steps=max_steps or int(os.getenv("AGENT_MAX_STEPS", "10")),
            request_timeout=int(os.getenv("AGENT_REQUEST_TIMEOUT", "90")),
            command_timeout=int(os.getenv("AGENT_COMMAND_TIMEOUT", "30")),
            max_tool_output_chars=int(os.getenv("AGENT_MAX_TOOL_OUTPUT_CHARS", "6000")),
            max_context_chars=int(os.getenv("AGENT_MAX_CONTEXT_CHARS", "60000")),
        )

