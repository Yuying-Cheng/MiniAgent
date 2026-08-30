from __future__ import annotations

import unittest

from minicodex.agent import MiniCodexAgent


class DummyClient:
    def complete(self, messages: list[dict[str, str]]) -> str:
        del messages
        return '{"action":"final","answer":"ok"}'


class DummyTools:
    pass


class ProtocolParsingTest(unittest.TestCase):
    def test_parses_fenced_json(self) -> None:
        agent = MiniCodexAgent(DummyClient(), DummyTools(), verbose=False)  # type: ignore[arg-type]
        decision = agent._parse_decision('```json\n{"action":"final","answer":"ok"}\n```')

        self.assertEqual(decision["action"], "final")
        self.assertEqual(decision["answer"], "ok")

    def test_recovers_json_from_extra_text(self) -> None:
        agent = MiniCodexAgent(DummyClient(), DummyTools(), verbose=False)  # type: ignore[arg-type]
        decision = agent._parse_decision('sure\n{"action":"final","answer":"ok"}\nthanks')

        self.assertEqual(decision["action"], "final")


if __name__ == "__main__":
    unittest.main()
