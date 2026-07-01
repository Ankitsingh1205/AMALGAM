# AMALGAM Global Engineering Rules

Repository is the single source of truth.

Always read existing code before making changes.

Never rewrite completed missions.

Never duplicate existing functionality.

Maintain backward compatibility.

Prefer extension over replacement.

Keep AutonomousExecutor as the execution backend.

Follow SOLID principles.

Avoid circular dependencies.

Every new module requires tests.

All code must compile.

All tests must pass.

No TODOs.

No placeholder implementations.

When editing:

1. Read related files first.
2. Understand dependencies.
3. Make the smallest correct change.
4. Preserve coding style.
5. Verify imports.
6. Verify tests.

Final response must include:

- Files created
- Files modified
- Tests added
- Tests passed
- Architecture impact
- Remaining work

## Repository Workflow

- Read the repository before making architectural decisions.
- Reuse existing modules whenever possible.
- Prefer composition over inheritance unless inheritance is clearly justified.
- Do not introduce breaking API changes.
- Keep commits focused and atomic.

## Performance Rules

- Optimize only after correctness.
- Avoid unnecessary allocations.
- Minimize memory growth.
- Reuse existing services instead of creating duplicates.

## AI Behaviour

Never guess.

If repository context is insufficient, inspect related files before modifying code.

When uncertain, preserve existing behavior.

Every architectural change must include a dependency impact analysis.

### Windows Environment

Always use:

py
py -m pytest
py -m pip

Never assume Linux.

Shell:
PowerShell

Repository root:
C:\AMALGAM

Avoid Linux utilities such as:
head
grep
cat