from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from minicodex.agent import MiniCodexAgent
from minicodex.tools import WorkspaceTools


class FakeClient:
    def __init__(self, responses: list[str]) -> None:
        self.responses = responses
        self.calls = 0

    def complete(self, messages: list[dict[str, str]]) -> str:
        del messages
        response = self.responses[self.calls]
        self.calls += 1
        return response


class MiniCodexAgentTest(unittest.TestCase):
    def test_agent_tool_loop_reaches_final_answer(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            workspace = Path(temp)
            (workspace / "app.py").write_text("print('bug')\n", encoding="utf-8")
            client = FakeClient(
                [
                    '{"thought":"inspect file","action":"tool","tool":"read_file","args":{"path":"app.py"}}',
                    '{"thought":"fix bug","action":"tool","tool":"replace_text","args":{"path":"app.py","old":"bug","new":"ok"}}',
                    '{"thought":"verify","action":"tool","tool":"run_command","args":{"command":"python app.py"}}',
                    '{"thought":"done","action":"final","answer":"Fixed app.py and verified it."}',
                ]
            )
            agent = MiniCodexAgent(
                client,  # type: ignore[arg-type]
                WorkspaceTools(workspace),
                max_steps=5,
                verbose=False,
            )

            answer = agent.run("Fix app.py")

            self.assertEqual(answer, "Fixed app.py and verified it.")
            self.assertEqual((workspace / "app.py").read_text(encoding="utf-8"), "print('ok')\n")
            self.assertEqual(client.calls, 4)


if __name__ == "__main__":
    unittest.main()

