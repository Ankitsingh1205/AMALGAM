#!/usr/bin/env python3
"""
AMALGAM Registry Engine

Responsibilities:
    - Recursively discover AMALGAM packages and modules from the repository.
    - Collect component metadata: name, path, category, public modules,
      dependencies, children, parent package, last modified.
    - Rebuild REGISTRY.json from repository inspection (no hardcoded entries).
    - Provide four CLI commands: status, scan, rebuild, validate.

Reuses helpers from scripts/context.py (get_project_root, core_dir, now_iso,
load_json, save_json) so no logic is duplicated across the scripts package.

Python standard library only. No repository-specific hardcoded entries.
"""

from __future__ import annotations

import ast
import json
import sys
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# scripts/ is a namespace package (no __init__.py): when this file is invoked
# directly via `py scripts/registry.py`, Python only puts scripts/ on sys.path,
# so `import scripts.context` would fail. Inserting the repository root makes
# the sibling helper imports resolvable without duplicating logic from
# scripts/context.py.
_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from scripts.context import (  # noqa: E402 -- path bootstrap is above.
    core_dir,
    get_project_root,
    load_json,
    now_iso,
    save_json,
)


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

REGISTRY_FILE = "REGISTRY.json"
REGISTRY_VERSION = "1.0"

# Candidate top-level directories to discover. Listed in priority order from
# the audit specification. Existence is verified at scan time; missing
# directories are silently skipped (no hardcoded component entries emitted).
DISCOVER_DIR_CANDIDATES: list[str] = [
    "agents",
    "brain",
    "kernel",
    "services",
    "tools",
    "workspace",
    "tests",
    "scripts",
    "providers",
    "configs",
    "docs",
]

# Directory names never treated as packages (caches, venvs, build artefacts).
SKIP_DIR_NAMES: set[str] = {
    "__pycache__",
    ".git",
    ".venv",
    ".pytest_cache",
    ".amalgam-core",
    ".claude",
    ".idea",
    ".vscode",
    "node_modules",
    "logs",
    "data",
    "assets",
    "storage",
}

# File extensions treated as importable Python modules.
PY_SUFFIX = ".py"
INIT_FILE = "__init__.py"

COMMAND_MAP: dict[str, str] = {
    "status": "cmd_status",
    "scan": "cmd_scan",
    "rebuild": "cmd_rebuild",
    "validate": "cmd_validate",
}


# ---------------------------------------------------------------------------
# Errors
# ---------------------------------------------------------------------------

class RegistryError(Exception):
    """Raised when registry discovery, validation, or rebuild fails."""
    pass


# ---------------------------------------------------------------------------
# Component model
# ---------------------------------------------------------------------------

@dataclass
class Component:
    """Metadata record for a discovered AMALGAM Python component.

    A component is either a Python package (directory with __init__.py) or a
    Python module (.py file). Components are stored in REGISTRY.json keyed by
    their top-level category (the repository-root directory that contains them).
    """
    name: str
    path: str
    category: str
    public_modules: list[str] = field(default_factory=list)
    dependencies: list[str] = field(default_factory=list)
    children: list[str] = field(default_factory=list)
    parent_package: str | None = None
    last_modified: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Serialize this component to a JSON-friendly dictionary."""
        return asdict(self)


# ---------------------------------------------------------------------------
# Discovery helpers
# ---------------------------------------------------------------------------

def _is_amalgam_package_dir(path: Path) -> bool:
    """Return True if path is a directory containing an __init__.py."""
    return path.is_dir() and (path / INIT_FILE).exists()


def _should_skip_dir(path: Path) -> bool:
    """Return True if a directory must never be recursed into."""
    if path.name in SKIP_DIR_NAMES:
        return True
    # Skip hidden directories (.git, .venv, .pytest_cache and similar).
    if path.name.startswith(".") and path.name not in (".",):
        return True
    return False


def public_modules_of(resource: Path, root: Path) -> list[str]:
    """Return the list of importable submodule names owned by a package.

    A package's public modules are its direct .py files (excluding __init__)
    and its direct subpackages (directories containing __init__.py). Each
    entry is a fully-qualified dotted name relative to the repository root.

    Args:
        resource: Directory treated as a package.
        root: Repository root used to compute dotted names.

    Returns:
        Sorted list of fully-qualified public module names. Empty when the
        resource is a module or not a directory.
    """
    if not resource.is_dir():
        return []
    rel_parts = resource.relative_to(root).parts
    prefix = ".".join(rel_parts)
    found: list[str] = []
    for child in sorted(resource.iterdir()):
        if _should_skip_dir(child):
            continue
        if child.is_file() and child.suffix == PY_SUFFIX and child.name != INIT_FILE:
            found.append(f"{prefix}.{child.stem}")
        elif _is_amalgam_package_dir(child):
            found.append(f"{prefix}.{child.name}")
    return found


def children_of(resource: Path) -> list[str]:
    """Return immediate child names of a package directory.

    Children are direct .py files (excluding __init__) and direct subpackages.
    Names are short (not dotted). Empty for module files and non-directories.

    Args:
        resource: Directory treated as a package.

    Returns:
        Sorted list of immediate child names.
    """
    if not resource.is_dir():
        return []
    found: list[str] = []
    for child in sorted(resource.iterdir()):
        if _should_skip_dir(child):
            continue
        if child.is_file() and child.suffix == PY_SUFFIX and child.name != INIT_FILE:
            found.append(child.name)
        elif _is_amalgam_package_dir(child):
            found.append(child.name)
    return found


def dependencies_of(module_path: Path, root: Path) -> list[str]:
    """Return AMALGAM-internal module dependencies parsed from import statements.

    Uses the AST (not module execution) so imports to missing modules are still
    recorded. Only first-segment names matching a discovered top-level
    AMALGAM package directory are reported; stdlib and third-party imports are
    filtered out.

    Args:
        module_path: .py file to analyse.
        root: Repository root used to resolve the set of internal packages.

    Returns:
        Sorted unique list of fully-qualified AMALGAM dependencies this module
        imports. Each entry is a dotted name whose first segment is a top-level
        AMALGAM package.
    """
    try:
        source = module_path.read_text(encoding="utf-8")
    except OSError:
        return []
    try:
        tree = ast.parse(source, filename=str(module_path))
    except SyntaxError:
        return []

    internal_roots: set[str] = {
        d.name for d in root.iterdir() if _is_amalgam_package_dir(d)
    }
    internal_roots.update(
        stem for stem in (p.stem for p in root.glob("*.py") if p.name != "bootstrap.py")
        if stem not in {"__init__"}
    )

    extracted: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if not alias.name or alias.name.startswith("."):
                    continue
                top = alias.name.split(".")[0]
                if top in internal_roots:
                    extracted.add(alias.name)
        elif isinstance(node, ast.ImportFrom):
            # Skip relative imports (level > 0) -- internal to a single package.
            if node.level and node.level > 0:
                continue
            if not node.module:
                continue
            top = node.module.split(".")[0]
            if top in internal_roots:
                extracted.add(node.module)

    return sorted(extracted)


def parent_package_of(resource: Path, root: Path) -> str | None:
    """Return the dotted name of the parent package, or None at root level.

    Args:
        resource: Package directory or module file.
        root: Repository root.

    Returns:
        Dotted parent name, or None when the resource is directly under root.
    """
    rel = resource.relative_to(root)
    parts = rel.parts
    if len(parts) <= 1:
        return None
    parent_parts = parts[:-1]
    return ".".join(parent_parts) if parent_parts else None


def last_modified_iso(path: Path) -> str | None:
    """Return an ISO 8601 UTC timestamp of a path's last modification time.

    Args:
        path: File or directory whose mtime is queried.

    Returns:
        ISO 8601 string, or None when the path does not exist.
    """
    if not path.exists():
        return None
    mtime = path.stat().st_mtime
    return datetime.fromtimestamp(mtime, tz=timezone.utc).isoformat()


def _relative_path_str(path: Path, root: Path) -> str:
    """Return a forward-slash relative path string from root."""
    return path.relative_to(root).as_posix()


# ---------------------------------------------------------------------------
# Component discovery
# ---------------------------------------------------------------------------

def discover_components(root: Path) -> dict[str, list[dict[str, Any]]]:
    """Walk the repository and return components grouped by top-level category.

    For each candidate directory in DISCOVER_DIR_CANDIDATES that exists at the
    repository root, recursively descend into packages and collect every
    Python package (dir with __init__.py) and Python module (.py file).

    Args:
        root: Repository root directory.

    Returns:
        Dict mapping category name -> list of Component dicts. Categories
        whose directory does not exist are omitted entirely (never emitted
        as empty placeholders).
    """
    components: dict[str, list[dict[str, Any]]] = {}

    for category in DISCOVER_DIR_CANDIDATES:
        category_dir = root / category
        if not category_dir.is_dir():
            continue
        members: list[dict[str, Any]] = []
        _collect_in_category(category_dir, category, root, members)
        if members:
            components[category] = members

    return components


def _collect_in_category(
    category_dir: Path,
    category: str,
    root: Path,
    out: list[dict[str, Any]],
) -> None:
    """Recursively collect components within a single top-level category.

    The category directory itself is registered as a Component (when it is a
    package); every subpackage and every .py module below it is collected in a
    deterministic depth-first order.

    Args:
        category_dir: Top-level directory of the category.
        category: Its short name (e.g. "agents").
        root: Repository root for relative-path computation.
        out: Accumulator list to append Component dicts to.
    """
    # First, register the category directory itself (whether or not it has an
    # __init__.py -- consistent representation of the top-level package).
    out.append(_build_component(category_dir, category, root).to_dict())

    # Then recurse depth-first, in sorted order, into packages and modules.
    for child in sorted(category_dir.iterdir()):
        if _should_skip_dir(child):
            continue
        if _is_amalgam_package_dir(child):
            _recurse_package(child, category, root, out)
        elif child.is_file() and child.suffix == PY_SUFFIX and child.name != INIT_FILE:
            out.append(_build_component(child, category, root).to_dict())


def _recurse_package(
    package_dir: Path,
    category: str,
    root: Path,
    out: list[dict[str, Any]],
) -> None:
    """Recursively collect a package and its descendants.

    Args:
        package_dir: Directory containing __init__.py.
        category: Top-level category name.
        root: Repository root.
        out: Accumulator list.
    """
    out.append(_build_component(package_dir, category, root).to_dict())
    for child in sorted(package_dir.iterdir()):
        if _should_skip_dir(child):
            continue
        if _is_amalgam_package_dir(child):
            _recurse_package(child, category, root, out)
        elif child.is_file() and child.suffix == PY_SUFFIX and child.name != INIT_FILE:
            out.append(_build_component(child, category, root).to_dict())


def _build_component(resource: Path, category: str, root: Path) -> Component:
    """Construct a Component record for a single file or directory.

    Args:
        resource: .py module file or package directory.
        category: Top-level category name.
        root: Repository root for relative paths.

    Returns:
        A populated Component dataclass.
    """
    is_dir = resource.is_dir()
    name = resource.name if is_dir else resource.stem
    return Component(
        name=name,
        path=_relative_path_str(resource, root),
        category=category,
        public_modules=public_modules_of(resource, root) if is_dir else [],
        dependencies=dependencies_of(resource, root) if not is_dir else [],
        children=children_of(resource) if is_dir else [],
        parent_package=parent_package_of(resource, root),
        last_modified=last_modified_iso(resource),
    )


# ---------------------------------------------------------------------------
# Registry IO
# ---------------------------------------------------------------------------

def load_registry() -> dict[str, Any]:
    """Return the current REGISTRY.json contents, or an empty dict when absent."""
    loaded = load_json(REGISTRY_FILE)
    return loaded if isinstance(loaded, dict) else {}


def save_registry(components: dict[str, list[dict[str, Any]]], verified: bool) -> dict[str, Any]:
    """Persist REGISTRY.json with the standard envelope and return its contents.

    Args:
        components: Discovered components grouped by category.
        verified: True once a scan has produced a complete registry.

    Returns:
        The REGISTRY.json dictionary that was written.
    """
    registry: dict[str, Any] = {
        "version": REGISTRY_VERSION,
        "generated_at": now_iso(),
        "components": components,
        "verified": verified,
    }
    save_json(REGISTRY_FILE, registry)
    return registry


# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------

def cmd_status() -> None:
    """Print a concise summary of the current REGISTRY.json contents."""
    registry = load_registry()
    print()
    print("AMALGAM REGISTRY STATUS")
    print("-" * 50)
    if not registry:
        print("REGISTRY.json is missing or empty. Run 'scan' or 'rebuild'.")
        print()
        return

    components = registry.get("components", {})
    total = sum(len(v) for v in components.values() if isinstance(v, list))
    print(f"Version        : {registry.get('version', '—')}")
    print(f"Generated at    : {registry.get('generated_at', '—')}")
    print(f"Verified        : {registry.get('verified', False)}")
    print(f"Total components: {total}")
    print("-" * 50)
    print("Categories")
    for category in sorted(components):
        members = components[category]
        print(f"  {category:<14} {len(members):>3} component(s)")
    print()


def cmd_scan() -> None:
    """Discover components and write REGISTRY.json (does not validate depth)."""
    root = get_project_root()
    print(f"[REGISTRY] Scanning repository: {root}")
    components = discover_components(root)
    registry = save_registry(components, verified=bool(components))
    total = sum(len(v) for v in components.values())
    print(f"[REGISTRY] Discovered {total} component(s) across {len(components)} categories.")
    for category in sorted(components):
        print(f"  {category:<14} {len(components[category]):>3}")
    print(f"[REGISTRY] Wrote {core_dir() / REGISTRY_FILE}")
    print()


def cmd_rebuild() -> None:
    """Run scan followed by validate; guarantees a clean, verified registry."""
    print("[REGISTRY] Rebuild = scan + validate")
    print()
    cmd_scan()
    cmd_validate()


def cmd_validate() -> None:
    """Verify REGISTRY.json still reflects the live repository.

    Recomputes the discovery snapshot and compares it to the persisted
    REGISTRY.json. Reports drift (missing components, extra components,
    mismatched paths) but does NOT modify the file.
    """
    registry = load_registry()
    if not registry:
        print("[REGISTRY] ERROR: REGISTRY.json is missing or empty. Run 'scan' first.")
        print()
        return

    root = get_project_root()
    live = discover_components(root)
    persisted = registry.get("components", {})

    print("[REGISTRY] Validating REGISTRY.json against live repository...")
    print()

    drift = False
    categories = sorted(set(live) | set(persisted))
    for category in categories:
        live_paths = {c["path"] for c in live.get(category, [])}
        kept_paths = {c["path"] for c in persisted.get(category, [])}
        if live_paths == kept_paths:
            print(f"  OK   {category:<14} {len(live_paths)} component(s) match")
            continue
        drift = True
        missing = sorted(live_paths - kept_paths)
        extra = sorted(kept_paths - live_paths)
        print(f"  DRIFT {category}")
        if missing:
            print(f"     missing in registry ({len(missing)}):")
            for p in missing[:10]:
                print(f"        - {p}")
            if len(missing) > 10:
                print(f"        ... and {len(missing) - 10} more")
        if extra:
            print(f"     stale in registry ({len(extra)}):")
            for p in extra[:10]:
                print(f"        - {p}")
            if len(extra) > 10:
                print(f"        ... and {len(extra) - 10} more")

    verified_flag = bool(registry.get("verified"))
    print()
    if drift:
        print("VERDICT: DRIFT DETECTED. Run 'rebuild' to regenerate REGISTRY.json.")
    elif not verified_flag:
        print("VERDICT: Clean structure but 'verified' flag is false. Run 'rebuild'.")
    else:
        print("VERDICT: CLEAN — REGISTRY.json matches the repository.")
    print()


# ---------------------------------------------------------------------------
# CLI dispatch
# ---------------------------------------------------------------------------

def print_help() -> None:
    """Print the available commands and their purpose."""
    print("AMALGAM Registry Engine")
    print()
    print("Commands:")
    for cmd in COMMAND_MAP:
        print(f"  py scripts/registry.py {cmd}")
    print()
    print("  status    : Show the current REGISTRY.json summary.")
    print("  scan      : Discover components and write REGISTRY.json.")
    print("  rebuild   : Scan followed by validate (clean refresh).")
    print("  validate  : Compare REGISTRY.json against the live repository.")
    print()


def main() -> None:
    """Parse CLI arguments and dispatch to the requested command."""
    if len(sys.argv) < 2:
        print("Usage: py scripts/registry.py <command>")
        print()
        print_help()
        sys.exit(0)

    cmd = sys.argv[1].lower()
    if cmd in ("help", "--help", "-h"):
        print_help()
        sys.exit(0)

    func_name = COMMAND_MAP.get(cmd)
    if func_name is None:
        print(f"ERROR: Unknown command '{cmd}'.")
        print_help()
        sys.exit(1)

    func = globals().get(func_name)
    if func is None:
        print(f"ERROR: Internal dispatch failure for '{cmd}' -> '{func_name}'.")
        sys.exit(1)

    try:
        func()
    except RegistryError as exc:
        print(f"ERROR: {exc}")
        sys.exit(1)
    except Exception as exc:  # Surface unexpected failures explicitly.
        print(f"ERROR: Command '{cmd}' failed: {exc}")
        sys.exit(1)


if __name__ == "__main__":
    main()
