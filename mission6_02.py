
from pathlib import Path
import shutil
import sys

ROOT = Path.cwd()
TARGET = ROOT / "tools" / "file_tool.py"

print("Mission 6.0.2")

if not TARGET.exists():
    print("Run this from the AMALGAM root directory.")
    sys.exit(1)

backup = TARGET.with_suffix(TARGET.suffix + ".mission6.bak")
shutil.copy2(TARGET, backup)

text = TARGET.read_text(encoding="utf-8")

additions = """

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
"""

if "def exists(" in text:
    print("Already upgraded.")
    sys.exit(0)

idx = text.rfind("\n")
text = text.rstrip() + additions + "\n"

if "import shutil" not in text:
    text = text.replace("from pathlib import Path", "from pathlib import Path\nimport shutil")

TARGET.write_text(text, encoding="utf-8")

print("Updated:", TARGET)
print("Backup:", backup)
print("Done.")
