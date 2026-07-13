"""Generate amalgam_source_dump.txt - full recursive source code dump of AMALGAM."""

from pathlib import Path
import sys

EXCLUDE_DIRS = {".git", ".venv", "venv", "node_modules", "__pycache__", "dist", "build", ".pytest_cache", ".claude"}
INCLUDE_EXT = {".py", ".json", ".yaml", ".yml", ".md", ".toml", ".ini"}
WORKSPACE = Path(__file__).resolve().parents[1]
OUTPUT = WORKSPACE / "amalgam_source_dump.txt"

SEPARATOR = "=" * 78

def should_exclude(path: Path) -> bool:
    return any(part in EXCLUDE_DIRS for part in path.parts)

def is_target_file(path: Path) -> bool:
    return path.suffix.lower() in INCLUDE_EXT

def is_binary(path: Path) -> bool:
    try:
        with open(path, "rb") as f:
            chunk = f.read(8192)
        return b"\0" in chunk
    except Exception:
        return True

def collect_files(root: Path) -> list[Path]:
    files = []
    for p in sorted(root.rglob("*")):
        if not p.is_file():
            continue
        if should_exclude(p):
            continue
        if not is_target_file(p):
            continue
        files.append(p)
    return files

def main():
    sys.stdout.write(f"Scanning {WORKSPACE} ...\n")
    files = collect_files(WORKSPACE)
    sys.stdout.write(f"Found {len(files)} target files.\n")

    with open(OUTPUT, "w", encoding="utf-8", errors="replace") as out:
        for i, fp in enumerate(files):
            rel = fp.relative_to(WORKSPACE)
            sys.stdout.write(f"  [{i+1}/{len(files)}] {rel}\n")

            out.write(SEPARATOR + "\n")
            out.write(f"FILE: {fp.resolve()}\n")
            out.write(SEPARATOR + "\n")

            try:
                content = fp.read_text(encoding="utf-8", errors="replace")
                out.write(content)
            except Exception as e:
                out.write(f"[ERROR READING FILE: {e}]\n")

            out.write("\n")

    sys.stdout.write(f"\nDone. Output written to {OUTPUT}\n")
    sys.stdout.write(f"Total files dumped: {len(files)}\n")

if __name__ == "__main__":
    main()
