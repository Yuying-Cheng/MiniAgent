from __future__ import annotations

import json
import os
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any


IGNORED_DIRS = {".git", "__pycache__", ".pytest_cache", ".mypy_cache", ".venv", "venv"}
RISKY_COMMAND_PATTERNS = [
    r"\bgit\s+reset\s+--hard\b",
    r"\bgit\s+push\b",
    r"\brm\s+.*-rf\b",
    r"\bdel\s+.*\/s\b",
    r"\bformat\b",
    r"\bshutdown\b",
    r"\bRemove-Item\b.*\b-Recurse\b",
]


@dataclass
class ToolResult:
    success: bool
    content: str

    def to_json(self) -> str:
        return json.dumps(
            {"success": self.success, "content": self.content},
            ensure_ascii=False,
            indent=2,
        )


class WorkspaceTools:
    def __init__(
        self,
        workspace: Path,
        *,
        command_timeout: int = 30,
        max_output_chars: int = 6000,
    ) -> None:
        self.workspace = workspace.resolve()
        self.command_timeout = command_timeout
        self.max_output_chars = max_output_chars

    def execute(self, name: str, args: dict[str, Any]) -> ToolResult:
        if not isinstance(args, dict):
            return ToolResult(False, "Tool args must be a JSON object.")

        try:
            if name == "list_files":
                return self.list_files(**args)
            if name == "search_text":
                return self.search_text(**args)
            if name == "read_file":
                return self.read_file(**args)
            if name == "write_file":
                return self.write_file(**args)
            if name == "append_file":
                return self.append_file(**args)
            if name == "replace_text":
                return self.replace_text(**args)
            if name == "run_command":
                return self.run_command(**args)
            return ToolResult(False, f"Unknown tool: {name}")
        except TypeError as exc:
            return ToolResult(False, f"Invalid arguments for {name}: {exc}")
        except Exception as exc:
            return ToolResult(False, f"{type(exc).__name__}: {exc}")

    def list_files(
        self,
        path: str = ".",
        recursive: bool = True,
        max_entries: int = 200,
    ) -> ToolResult:
        base = self._resolve(path)
        if not base.exists():
            return ToolResult(False, f"Path does not exist: {path}")

        entries: list[str] = []
        iterator = base.rglob("*") if recursive else base.iterdir()
        for entry in iterator:
            if self._is_ignored(entry):
                continue
            rel = entry.relative_to(self.workspace).as_posix()
            entries.append(rel + ("/" if entry.is_dir() else ""))
            if len(entries) >= max_entries:
                break

        return ToolResult(True, "\n".join(entries) or "(empty)")

    def search_text(
        self,
        query: str,
        path: str = ".",
        case_sensitive: bool = False,
        regex: bool = False,
        max_matches: int = 50,
    ) -> ToolResult:
        if not query:
            return ToolResult(False, "Query cannot be empty.")

        base = self._resolve(path)
        if not base.exists():
            return ToolResult(False, f"Path does not exist: {path}")

        flags = 0 if case_sensitive else re.IGNORECASE
        try:
            pattern = re.compile(query if regex else re.escape(query), flags)
        except re.error as exc:
            return ToolResult(False, f"Invalid regex: {exc}")

        files = [base] if base.is_file() else (p for p in base.rglob("*") if p.is_file())
        matches: list[str] = []
        for file_path in files:
            if self._is_ignored(file_path) or not self._looks_like_text(file_path):
                continue
            try:
                lines = file_path.read_text(encoding="utf-8", errors="replace").splitlines()
            except OSError:
                continue
            for line_no, line in enumerate(lines, start=1):
                if pattern.search(line):
                    rel = file_path.relative_to(self.workspace).as_posix()
                    matches.append(f"{rel}:{line_no}: {line}")
                    if len(matches) >= max_matches:
                        return ToolResult(True, "\n".join(matches) + "\n... match limit reached")

        return ToolResult(True, "\n".join(matches) or "(no matches)")

    def read_file(
        self,
        path: str,
        start_line: int = 1,
        max_lines: int = 200,
    ) -> ToolResult:
        target = self._resolve(path)
        if not target.is_file():
            return ToolResult(False, f"Not a file: {path}")

        text = target.read_text(encoding="utf-8", errors="replace")
        lines = text.splitlines()
        start = max(start_line, 1) - 1
        end = min(start + max(max_lines, 1), len(lines))
        numbered = [f"{idx + 1:4}: {line}" for idx, line in enumerate(lines[start:end], start)]
        suffix = ""
        if end < len(lines):
            suffix = f"\n... truncated, showing lines {start + 1}-{end} of {len(lines)}"
        return ToolResult(True, "\n".join(numbered) + suffix)

    def write_file(
        self,
        path: str,
        content: str,
        overwrite: bool = True,
    ) -> ToolResult:
        target = self._resolve(path)
        if target.exists() and not overwrite:
            return ToolResult(False, f"File already exists: {path}")

        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(str(content), encoding="utf-8", newline="\n")
        return ToolResult(True, f"Wrote {path} ({len(str(content).splitlines())} lines).")

    def append_file(
        self,
        path: str,
        content: str,
    ) -> ToolResult:
        target = self._resolve(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        with target.open("a", encoding="utf-8", newline="\n") as stream:
            stream.write(str(content))
        return ToolResult(True, f"Appended to {path} ({len(str(content).splitlines())} lines).")

    def replace_text(
        self,
        path: str,
        old: str,
        new: str,
        count: int = 1,
    ) -> ToolResult:
        target = self._resolve(path)
        if not target.is_file():
            return ToolResult(False, f"Not a file: {path}")
        if old == "":
            return ToolResult(False, "The old text cannot be empty.")

        text = target.read_text(encoding="utf-8", errors="replace")
        matches = text.count(old)
        if matches == 0:
            return ToolResult(False, f"Text not found in {path}.")

        replace_count = matches if count is None or count < 0 else count
        updated = text.replace(old, new, replace_count)
        target.write_text(updated, encoding="utf-8", newline="\n")
        return ToolResult(True, f"Replaced {min(matches, replace_count)} occurrence(s) in {path}.")

    def run_command(self, command: str, timeout: int | None = None) -> ToolResult:
        if self._looks_risky(command) and os.getenv("MINICODEX_ALLOW_RISKY_COMMANDS") != "1":
            return ToolResult(
                False,
                "Command refused by safety policy. Set MINICODEX_ALLOW_RISKY_COMMANDS=1 to allow it.",
            )

        timeout = timeout or self.command_timeout
        try:
            if os.name == "nt":
                completed = subprocess.run(
                    ["powershell", "-NoProfile", "-Command", command],
                    cwd=self.workspace,
                    capture_output=True,
                    text=True,
                    encoding="utf-8",
                    errors="replace",
                    timeout=timeout,
                )
            else:
                completed = subprocess.run(
                    command,
                    cwd=self.workspace,
                    shell=True,
                    capture_output=True,
                    text=True,
                    encoding="utf-8",
                    errors="replace",
                    timeout=timeout,
                )
        except subprocess.TimeoutExpired as exc:
            partial = (exc.stdout or "") + (exc.stderr or "")
            return ToolResult(False, self._trim(f"Command timed out after {timeout}s.\n{partial}"))

        output = (
            f"exit_code={completed.returncode}\n"
            f"stdout:\n{completed.stdout}\n"
            f"stderr:\n{completed.stderr}"
        )
        return ToolResult(completed.returncode == 0, self._trim(output))

    def _resolve(self, path: str) -> Path:
        requested = Path(path)
        if requested.is_absolute():
            resolved = requested.resolve()
        else:
            resolved = (self.workspace / requested).resolve()

        try:
            resolved.relative_to(self.workspace)
        except ValueError as exc:
            raise ValueError(f"Path escapes workspace: {path}") from exc
        return resolved

    def _is_ignored(self, path: Path) -> bool:
        return any(part in IGNORED_DIRS for part in path.relative_to(self.workspace).parts)

    def _looks_like_text(self, path: Path) -> bool:
        try:
            chunk = path.read_bytes()[:2048]
        except OSError:
            return False
        return b"\0" not in chunk

    def _looks_risky(self, command: str) -> bool:
        return any(re.search(pattern, command, flags=re.IGNORECASE) for pattern in RISKY_COMMAND_PATTERNS)

    def _trim(self, text: str) -> str:
        if len(text) <= self.max_output_chars:
            return text
        head = text[: self.max_output_chars // 2]
        tail = text[-self.max_output_chars // 2 :]
        return f"{head}\n... output truncated ...\n{tail}"

