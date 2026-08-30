from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from minicodex.tools import WorkspaceTools


class WorkspaceToolsTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.workspace = Path(self.temp_dir.name)
        self.tools = WorkspaceTools(self.workspace, max_output_chars=2000)

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_write_read_and_replace_file(self) -> None:
        written = self.tools.write_file("app.py", "print('bug')\n")
        self.assertTrue(written.success)

        replaced = self.tools.replace_text("app.py", "bug", "ok")
        self.assertTrue(replaced.success)

        read = self.tools.read_file("app.py")
        self.assertTrue(read.success)
        self.assertIn("print('ok')", read.content)

    def test_append_and_search_text(self) -> None:
        self.tools.write_file("pkg/app.py", "def add(a, b):\n    return a + b\n")
        appended = self.tools.append_file("pkg/app.py", "\nprint(add(2, 3))\n")
        self.assertTrue(appended.success)

        result = self.tools.search_text("add", path="pkg")
        self.assertTrue(result.success)
        self.assertIn("pkg/app.py:1", result.content)
        self.assertIn("pkg/app.py:4", result.content)

    def test_rejects_path_escape(self) -> None:
        result = self.tools.execute("write_file", {"path": "../outside.txt", "content": "no"})
        self.assertFalse(result.success)
        self.assertIn("escapes workspace", result.content)

    def test_runs_command_in_workspace(self) -> None:
        self.tools.write_file("hello.py", "print('hello')\n")
        result = self.tools.run_command("python hello.py")
        self.assertTrue(result.success, result.content)
        self.assertIn("hello", result.content)

    def test_refuses_obviously_risky_command(self) -> None:
        result = self.tools.run_command("git reset --hard HEAD")
        self.assertFalse(result.success)
        self.assertIn("refused", result.content)


if __name__ == "__main__":
    unittest.main()
