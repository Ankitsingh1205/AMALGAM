"""Separate read/local-write Git boundary. Remote and destructive actions do not exist."""
from __future__ import annotations

from pathlib import Path
import re
import subprocess


class GitSafetyError(RuntimeError):
    pass


class GitService:
    SECRET_PATTERN = re.compile(r"(?i)(api[_-]?key|password|secret|private[_-]?key)\s*[:=]\s*['\"]?[^\s'\"]+")

    def __init__(self, root: str | Path):
        self.root = Path(root).resolve()

    def changed_files(self) -> list[str]:
        output = self._run("status", "--porcelain")
        return [line[3:] for line in output.splitlines() if len(line) > 3]

    def diff(self) -> str:
        return self._run("diff", "--", ".")

    def recent(self) -> list[str]:
        return self._run("log", "-5", "--pretty=%h %s").splitlines()

    def local_commit(self, message: str, allowed_paths: set[str]) -> str:
        changed = set(self.changed_files())
        if not changed:
            raise GitSafetyError("nothing to commit")
        if not changed.issubset(allowed_paths):
            raise GitSafetyError(f"unplanned files cannot be committed: {sorted(changed - allowed_paths)}")
        diff = self.diff()
        if self.SECRET_PATTERN.search(diff):
            raise GitSafetyError("possible secret detected in diff")
        # Untracked files do not appear in ``git diff``. Scan their actual
        # text before staging so a newly-created credential cannot bypass the
        # diff-based guard. Binary/unreadable files fail closed.
        for path in sorted(changed):
            candidate = (self.root / path).resolve()
            try:
                candidate.relative_to(self.root)
                content = candidate.read_text(encoding="utf-8") if candidate.is_file() else ""
            except (ValueError, UnicodeDecodeError, OSError) as exc:
                raise GitSafetyError(f"cannot safely inspect changed file {path}: {exc}") from exc
            if self.SECRET_PATTERN.search(content):
                raise GitSafetyError(f"possible secret detected in {path}")
        for path in sorted(changed):
            subprocess.run(["git", "add", "--", path], cwd=self.root, check=True, timeout=15)
        subprocess.run(["git", "commit", "-m", message], cwd=self.root, check=True, timeout=30,
                       capture_output=True, text=True)
        return self._run("rev-parse", "HEAD")

    def _run(self, *args: str) -> str:
        result = subprocess.run(["git", *args], cwd=self.root, capture_output=True, text=True, timeout=15)
        if result.returncode:
            raise GitSafetyError(result.stderr.strip() or "git command failed")
        return result.stdout.strip()
