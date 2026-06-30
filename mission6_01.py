
"""
Mission 6.0.1
Safely backs up tools/file_tool.py and reports readiness for upgrade.

This is the first automation step for Engineer Core.
"""

from pathlib import Path
import shutil
import sys

ROOT = Path.cwd()
FILE = ROOT / "tools" / "file_tool.py"

print("="*60)
print("AMALGAM Mission 6.0.1")
print("="*60)

if not FILE.exists():
    print(f"[ERROR] Could not find: {FILE}")
    print("Run this script from the AMALGAM project root.")
    sys.exit(1)

backup = FILE.with_suffix(FILE.suffix + ".bak")
shutil.copy2(FILE, backup)

print(f"[OK] Backup created: {backup.name}")
print(f"[OK] Target file: {FILE}")

text = FILE.read_text(encoding="utf-8")

checks = [
    ("read(", "read()"),
    ("write(", "write()"),
    ("list_dir(", "list_dir()"),
]

print("\nCurrent capabilities:")
for token, label in checks:
    print(f"  {'✓' if token in text else '✗'} {label}")

print("\nMission 6 next upgrade will add:")
for item in [
    "exists()",
    "backup()",
    "append()",
    "replace_text()",
    "copy()",
    "move()",
    "delete()",
]:
    print(f"  + {item}")

print("\nSTATUS: READY FOR MISSION 6.0.2")
