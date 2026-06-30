from pathlib import Path
import shutil


class FileTool:

    def read(self, path: str):

        try:
            return Path(path).read_text(encoding="utf-8")

        except Exception as e:
            return f"Read Error: {e}"

    def write(self, path: str, content: str):

        try:
            Path(path).write_text(content, encoding="utf-8")
            return "File saved."

        except Exception as e:
            return f"Write Error: {e}"

    def list_dir(self, path="."):

        try:
            return [p.name for p in Path(path).iterdir()]

        except Exception as e:
            return f"Directory Error: {e}"

    def exists(self, path: str):
        return Path(path).exists()

    def backup(self, path: str):
        src = Path(path)
        if not src.exists():
            return False
        dst = src.with_suffix(src.suffix + ".bak")
        shutil.copy2(src, dst)
        return str(dst)

    def append(self, path: str, text: str):
        with open(path, "a", encoding="utf-8") as f:
            f.write(text)
        return True

    def delete(self, path: str):
        p = Path(path)
        if p.exists():
            p.unlink()
        return True

    def copy(self, src: str, dst: str):
        shutil.copy2(src, dst)
        return True

    def move(self, src: str, dst: str):
        shutil.move(src, dst)
        return True

    def replace_text(self, path: str, old: str, new: str):
        p = Path(path)
        t = p.read_text(encoding="utf-8")
        if old not in t:
            return False
        p.write_text(t.replace(old, new), encoding="utf-8")
        return True

