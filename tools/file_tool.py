"""Filesystem tool with workspace confinement (Mission 7.6, SEC-003/004).

``FileTool`` optionally confines every operation to a workspace root.
When ``workspace_root`` is provided, all paths are resolved and must
stay inside that root -- traversal (``..``), absolute escapes, and
symlink escapes are rejected before any filesystem call happens.

``workspace_root=None`` preserves the historical unrestricted behavior
for callers that manage their own sandbox (e.g. tests using tmp_path).
The production registry (``tools.tool_registry``) always constructs the
confined variant.
"""

from pathlib import Path
import shutil
from typing import Optional


class FileToolPermissionError(Exception):
    """Raised when a path escapes the configured workspace root."""


class FileTool:

    def __init__(self, workspace_root: Optional[Path] = None):
        self._root = Path(workspace_root).resolve() if workspace_root else None

    def _resolve(self, path) -> Path:
        """Resolve ``path`` and enforce workspace confinement."""
        p = Path(path)
        if self._root is not None and not p.is_absolute():
            p = self._root / p
        p = p.resolve()
        if self._root is not None:
            try:
                p.relative_to(self._root)
            except ValueError:
                raise FileToolPermissionError(
                    f"Permission Error: path '{path}' escapes workspace root"
                )
        return p

    def read(self, path: str):
        try:
            return self._resolve(path).read_text(encoding="utf-8")
        except Exception as e:
            return f"Read Error: {e}"

    def write(self, path: str, content: str):
        try:
            self._resolve(path).write_text(content, encoding="utf-8")
            return "File saved."
        except Exception as e:
            return f"Write Error: {e}"

    def list_dir(self, path="."):
        try:
            return [p.name for p in self._resolve(path).iterdir()]
        except Exception as e:
            return f"Directory Error: {e}"

    def exists(self, path: str):
        try:
            return self._resolve(path).exists()
        except FileToolPermissionError:
            return False

    def backup(self, path: str):
        src = self._resolve(path)
        if not src.exists():
            return False
        dst = src.with_suffix(src.suffix + ".bak")
        shutil.copy2(src, dst)
        return str(dst)

    def append(self, path: str, text: str):
        with open(self._resolve(path), "a", encoding="utf-8") as f:
            f.write(text)
        return True

    def delete(self, path: str):
        p = self._resolve(path)
        if p.exists():
            p.unlink()
        return True

    def copy(self, src: str, dst: str):
        shutil.copy2(self._resolve(src), self._resolve(dst))
        return True

    def move(self, src: str, dst: str):
        shutil.move(self._resolve(src), self._resolve(dst))
        return True

    def replace_text(self, path: str, old: str, new: str):
        p = self._resolve(path)
        t = p.read_text(encoding="utf-8")
        if old not in t:
            return False
        p.write_text(t.replace(old, new), encoding="utf-8")
        return True
