from __future__ import annotations

import io
import unittest
from unittest.mock import patch

from minicodex.cli import interactive_loop, run_task


class FakeAgent:
    def __init__(self) -> None:
        self.tasks: list[str] = []

    def run(self, task: str) -> str:
        self.tasks.append(task)
        return f"done: {task}"


class CliTest(unittest.TestCase):
    def test_run_task_quiet_prints_final_answer(self) -> None:
        agent = FakeAgent()
        output = io.StringIO()

        with patch("sys.stdout", output):
            status = run_task(agent, "fix bug", quiet=True)  # type: ignore[arg-type]

        self.assertEqual(status, 0)
        self.assertEqual(agent.tasks, ["fix bug"])
        self.assertIn("done: fix bug", output.getvalue())

    def test_interactive_loop_accepts_task_and_quit(self) -> None:
        agent = FakeAgent()
        inputs = iter(["fix bug", ":quit"])
        output = io.StringIO()

        with patch("builtins.input", lambda _prompt: next(inputs)):
            with patch("sys.stdout", output):
                status = interactive_loop(agent)  # type: ignore[arg-type]

        self.assertEqual(status, 0)
        self.assertEqual(agent.tasks, ["fix bug"])
        self.assertIn("MiniCodex interactive mode", output.getvalue())
        self.assertIn("Task finished", output.getvalue())


if __name__ == "__main__":
    unittest.main()
