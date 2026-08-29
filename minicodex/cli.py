from __future__ import annotations

import argparse
import sys

from .agent import MiniCodexAgent
from .config import AgentConfig
from .llm import LLMError, OpenAICompatibleChatClient
from .tools import WorkspaceTools


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run a small local coding agent.")
    parser.add_argument("task", nargs="*", help="Programming task for the agent.")
    parser.add_argument("--workspace", help="Workspace directory. Defaults to current directory.")
    parser.add_argument("--model", help="Model name. Defaults to AGENT_MODEL or OPENAI_MODEL.")
    parser.add_argument("--base-url", help="OpenAI-compatible base URL ending in /v1.")
    parser.add_argument("--max-steps", type=int, help="Maximum tool/model loop steps.")
    parser.add_argument("--quiet", action="store_true", help="Only print the final answer.")
    args = parser.parse_args(argv)

    task = " ".join(args.task).strip()
    if not task:
        if sys.stdin.isatty():
            task = input("Task: ").strip()
        else:
            task = sys.stdin.read().strip()
    if not task:
        print("No task provided.", file=sys.stderr)
        return 2

    config = AgentConfig.from_env(
        workspace=args.workspace,
        model=args.model,
        base_url=args.base_url,
        max_steps=args.max_steps,
    )
    client = OpenAICompatibleChatClient(
        api_key=config.api_key,
        base_url=config.base_url,
        model=config.model,
        timeout=config.request_timeout,
    )
    tools = WorkspaceTools(
        config.workspace,
        command_timeout=config.command_timeout,
        max_output_chars=config.max_tool_output_chars,
    )
    agent = MiniCodexAgent(
        client,
        tools,
        max_steps=config.max_steps,
        max_context_chars=config.max_context_chars,
        verbose=not args.quiet,
    )

    try:
        answer = agent.run(task)
    except LLMError as exc:
        print(f"LLM error: {exc}", file=sys.stderr)
        return 1

    if args.quiet:
        print(answer)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

