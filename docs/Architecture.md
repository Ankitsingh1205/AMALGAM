# AMALGAM OS Architecture

## Canonical Runtime Flow

AMALGAM OS preserves this execution path:

User -> Brain -> Planner -> Task -> Executor -> Dispatcher -> Tool / Service

Mission 2 adds infrastructure around that path without changing routing or task
execution responsibilities.

## Infrastructure Modules

### Configuration

Runtime settings live in `config/settings.py`.

Immutable runtime names and action constants live in `config/constants.py`.

Model role mappings remain in `config/models.py` and are exposed through
`config/settings.py` for centralized consumption.

### Logging

Reusable structured logging lives in `services/logger.py`.

The logger emits structured records with:

- timestamp
- level
- source
- message
- context

The logger currently supports `DEBUG`, `INFO`, `WARNING`, and `ERROR`.

### Diagnostics

`services/diagnostics.py` provides `DiagnosticsService`, which returns a
structured health report for:

- configuration
- memory
- tool registry
- service registry
- Ollama availability
- storage

Diagnostics are infrastructure-only and are not part of the user request
execution path.

### Versioning

`config/version.py` exposes runtime metadata:

- application version
- build type
- environment
- Python version
- operating system

The kernel displays this metadata during boot.

## Workspace Engine

Mission 3 adds a read-only Workspace Engine in the top-level `workspace/`
package.

The Workspace Engine provides project information only. It does not execute
actions and is not part of the request execution path.

Primary API:

```python
from workspace import Workspace

report = Workspace(".").report()
data = report.as_dict()
```

Responsibilities:

- detect the project root
- scan directories
- build a project tree
- detect Python packages
- read README, `requirements.txt`, and `pyproject.toml`
- detect Git repositories by reading `.git`
- count modules and tests
- summarize dependencies
- return a structured workspace report

Workspace internals:

- `workspace/scanner.py`: root detection and directory scanning
- `workspace/tree.py`: project tree construction
- `workspace/analyzer.py`: project metadata analysis
- `workspace/dependency.py`: dependency parsing
- `workspace/git.py`: read-only Git repository metadata
- `workspace/project.py`: report data objects
- `workspace/summary.py`: compact report summary
- `workspace/workspace.py`: public API facade
