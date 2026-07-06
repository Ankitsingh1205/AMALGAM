# AGENTS.md

# AMALGAM Engineering Constitution

Version: 1.0
Status: Active
Scope: `.amalgam-core/`

This document is the permanent engineering constitution for every AI model and coding agent working on AMALGAM.

It is mission-independent, reusable forever, and takes priority over any conflicting prompt unless the user explicitly overrides it.

---

# Repository Philosophy

AMALGAM is an AI Operating System, not a chatbot or an LLM wrapper.

The repository is the single source of truth. Assumptions are forbidden; inspection is mandatory.

Every change must move the project toward long-term autonomy, maintainability, and architectural integrity.

Short-term convenience must never compromise long-term architecture.

Production quality is the only acceptable quality. Placeholders, hacks, and TODO-only implementations are prohibited.

---

# Engineering Principles

1. **Architecture before implementation.** Understand where code belongs before writing it.
2. **Reuse before creation.** Search the repository before adding new modules.
3. **Layer separation.** Each layer has exactly one responsibility.
4. **Composition over inheritance.** Prefer small composable components.
5. **Deterministic behaviour.** Identical inputs yield identical outputs whenever practical.
6. **Small incremental changes.** No large rewrites. Every milestone leaves the repository working.
7. **Backward compatibility.** Public APIs remain functional. Breaking changes require approval.
8. **Mission-first development.** Every feature belongs to a mission. No scope creep.
9. **Test before completion.** Nothing is done until the full suite passes.
10. **Minimal changes.** Modify the smallest amount of code necessary.
11. **Strong typing.** Use explicit type hints. Avoid `Any`.
12. **No silent assumptions.** Inspect, then act. Never invent missing behaviour.
13. **Long-term thinking.** Designs must remain maintainable as the project grows.

---

# Architecture Rules

## Layer Ownership

Each layer owns one responsibility. Responsibilities must never leak.

Allowed dependency direction (higher layers may coordinate lower layers; lower layers must never import higher layers):

```
Mission
  -> Planner
  -> Scheduler
  -> Executor
  -> Tools / Services / Knowledge / Memory
  -> Config / Workspace / Models
```

## Permanent Rules

- A lower layer must never import a higher layer.
- No circular dependencies may be introduced.
- No parallel systems competing with existing components.
- No layer shortcuts across boundaries.
- New modules must integrate naturally into the existing design.
- Large refactors require explicit user approval.
- Folder restructuring, module splitting, and package renaming require explicit approval.

## Dependency Direction

```
agents/ -> brain/ -> kernel/ -> services/ tools/ models/ -> config/
services/project_service -> workspace/ (leaf)
knowledge/ -> workspace/
```

Workspace never imports knowledge. Config imports nothing.

---

# Coding Standards

## Language

Primary language: Python (modern).
Prefer the standard library before introducing dependencies.
Justify every new dependency.

## Imports

- Use explicit imports.
- Wildcard imports are forbidden.

## Typing

- All public functions use type hints.
- Prefer `list[str]`, `dict[str, Any]`, `set[str]`, `tuple[...]`.
- Avoid `Any` unless unavoidable.

## Dataclasses

- Prefer dataclasses for structured models.
- Use `frozen=True` for immutable models.
- Use `slots=True` where appropriate.
- Use `default_factory` for mutable fields.
- Mutable default arguments are forbidden.

## Functions

- One responsibility per function.
- Extract helpers instead of deep nesting.
- Keep interfaces simple.

## Classes

- One concept per class.
- God classes are forbidden.
- Prefer composition over inheritance.

## Naming

- Descriptive names: `MissionGraph`, `MissionPlanner`, `ExecutionContext`.
- Avoid unclear abbreviations.

## Comments

- Comments explain **why**, not **what**.
- Bad: `Increment x`
- Good: `Increment retry counter after transient network failure.`

## Docstrings

Every public class and public method must include a concise docstring describing:
- Purpose.
- Parameters (names, types, meanings).
- Return value (type and meaning).
- Exceptions raised, when relevant.

## Logging

- Structured logging only.
- `print()` is forbidden in production code.
- Never log secrets, API keys, tokens, cookies, or credentials.

## Configuration

- No hardcoded configuration values.
- Use config files or centralized constants.
- Magic numbers are forbidden.

## Determinism

- Identical inputs produce identical outputs whenever practical.
- Document any intentionally non-deterministic behaviour.

## Performance

- Correctness first, optimization later.
- Prefer algorithmic improvements over micro-optimizations.
- No premature optimization.

## Quality Checklist

Before considering implementation complete:
- Code compiles.
- Imports resolve.
- Type hints added.
- Public APIs preserved.
- Logging appropriate.
- No duplicate logic.
- No dead code.
- No placeholder implementations.

---

# Documentation Rules

Documentation is part of the project and must remain synchronized with the code.

## Public API Documentation

Every public class and method must have a docstring covering purpose, parameters, return value, and exceptions.

## Architecture Documentation

Architecture documentation lives in `docs/Architecture.md`.

When a module is added or changed:
- Document its purpose.
- Document its layer.
- Document its public API.
- Document its dependencies.

Never leave architecture documentation out of sync with the code.

## Documentation Quality

Documentation must be:
- Accurate: matches current code.
- Actionable: usable for understanding and modification.
- Concise: no filler, no speculation, no future plans.

Documentation must NOT be:
- Outdated.
- Speculative.
- Placeholder.
- Vague.

## Synchronization

When code changes:
- Public API changes update docstrings.
- Architecture changes update `docs/Architecture.md`.
- Mission specification changes update `docs/missions/`.
- Changelog updates `docs/Changelog.md`.

---

# Testing Policy

A task is not complete until:
- The full test suite passes.
- Existing tests continue passing.
- No regressions exist.

## Requirements

- Every implementation includes regression tests.
- Run the complete project test suite after every change.
- Never assume success without running tests.
- Identify root cause, fix implementation, rerun tests until stable.

## Forbidden

- Disabling tests to make the suite pass.
- Modifying tests to match broken implementations.
- Removing tests without replacement.
- Reporting success without running tests.
- Fabricating test results.

## Environment

- Use `py` for invoking Python.
- Use `py -m pytest` for running tests.
- Repository root is `C:\AMALGAM`.

---

# Git Commit Policy

## Authorization

- Commit only when explicitly requested by the user.
- Push only when explicitly requested by the user.
- No automatic commits, pushes, or progress saves.

## History

- Never rewrite history.
- Never use `git rebase`, `git commit --amend`, `git reset --hard`, `git push --force`, or `git push --force-with-lease` without explicit approval.
- No empty commits.
- No `git commit --allow-empty`.

## Before Committing

- Inspect `git status`.
- Inspect `git diff`.
- Inspect `git log --oneline -10`.
- Verify only intended files are staged.
- Verify no secrets are staged.

## Staging

- A commit contains only files directly related to the current task.
- Never stage unrelated modifications, temporary files, backups, caches, virtual environments, or IDE configurations.

## Secrets

- Never commit API keys, passwords, tokens, cookies, private keys, or environment files containing credentials.
- Inspect every staged file for secret content before committing.

## Messages

- One summary line, under 72 characters.
- Descriptive of what changed and why.
- Consistent with existing repository style.

Example:
```
Add workspace boundary enforcement to FileTool (Mission 6.4.4)
```

## Before Working

- Inspect `git status` for pending changes.
- Inspect `git log --oneline -5` for recent activity.
- Report upstream changes before starting on a stale branch.

---

# Repository Inspection Policy

Implementation without understanding is prohibited.

## Inspection Order

Before modifying code, inspect in this order:
1. Project root
2. `README.md`
3. `AGENTS.md`
4. `ARCHITECTURE.md`
5. `MISSION.md`
6. `TASK.md`

Then:
- Inspect the target module.
- Inspect related modules.
- Inspect existing tests.
- Inspect dependency relationships.

Only then begin implementation.

## Unknown Behaviour

If behaviour cannot be determined:
- Inspect code.
- Inspect tests.
- Inspect documentation.
- Report uncertainty explicitly if it persists.

Never fabricate missing behaviour.

---

# Reuse Existing Code Policy

Before creating any new module:
1. Search the repository.
2. Search related modules.
3. Search tests.
4. Search utilities.

If an implementation exists, reuse it.
If partial functionality exists, extend it.
Never duplicate production code.

## File Policy

- Modify existing files only when necessary.
- Create new files only for genuinely new functionality.
- Avoid unnecessary file creation, movement, or renaming.

## Refactoring Policy

Refactoring is allowed only when:
- Explicitly requested by the user.
- Required to fix a bug that cannot be fixed without restructuring.
- Required to integrate a feature that cannot be added without restructuring, with approval.

Refactoring is NOT allowed when:
- Unrelated to the current mission.
- Driven by personal preference.
- Driven by speculative future needs.
- Performed as cleanup after a completed task.

## Compatibility

Before refactoring:
- Identify every public API in the affected module.
- Identify every caller of every public API.
- Ensure every existing caller will continue to work.

During refactoring:
- Keep public method signatures unchanged.
- Keep public class names unchanged.
- Keep module-level exports unchanged.

After refactoring:
- Run the full test suite.
- Verify no regression in caller modules.

---

# Performance Policy

- Optimize only after correctness.
- Prefer algorithmic improvements over micro-optimizations.
- No premature optimization.
- Performance optimizations must not reduce readability unless clearly justified.
- Repeated execution with identical inputs should produce identical outputs whenever practical.

---

# Security Policy

## Secret Handling

Never log, print, expose, or commit:
- API keys.
- Passwords.
- Tokens.
- Cookies.
- Secrets.
- Private keys.
- Environment variables containing credentials.

Never hardcode credentials in source files. Use environment variables or configuration files.

## Path Traversal Prevention

Every filesystem operation must enforce workspace boundaries:
1. Resolve the path with `Path.resolve()`.
2. Verify the resolved path is within the workspace root.
3. Reject paths that escape the workspace root.
4. Log the rejection.

Never allow user-controlled input to specify arbitrary filesystem paths without boundary validation.

## Input Sanitization

Treat every external input as untrusted: CLI input, LLM output, disk data, network data, API data.

Before passing input to any tool or service:
1. Validate the type.
2. Validate the length.
3. Validate the structure.
4. Reject inputs that do not match expected schemas.

Never pass raw user input to `eval()`, `exec()`, `os.system()`, or `subprocess`.

## Least Privilege

Every tool and service operates with the minimum permissions necessary:
- FileTool: workspace boundaries only.
- PythonExecutor: restricted sandbox.
- Calculator: arithmetic only.
- MemoryService: configured memory file path only.

## Forbidden Functions

- `eval()`
- `exec()`
- Unsafe shell execution.
- Insecure deserialization.

## Audit Trail

Every execution step must be recorded in ExecutionMemory with timestamp, goal ID, step name, action taken, and result or error.

---

# Error Handling Policy

- Never silently swallow exceptions.
- Catch only exceptions that can be handled.
- Unexpected exceptions must propagate with meaningful context.
- Bare `except:` is forbidden. Use specific exception types.
- Every error must be logged, reported, and investigated.
- Never suppress error output.
- Never hide test failures.
- If an error cannot be handled, escalate it explicitly.

## Recovery Workflow

```
Implementation -> Verification -> Testing -> Failure -> Fix -> Retest -> Report
```

- Identify root cause.
- Fix implementation.
- Rerun tests until stable.
- Enforce maximum retry counts. No infinite retry loops.
- Never skip reflection on a failure.
- Never mark a paused goal as FAILED.

---

# Mission Development Rules

Every feature is implemented through numbered missions. No feature may bypass the mission workflow.

## Mission-First

- Every feature belongs to a mission.
- No unrelated features during another mission.
- No scope creep.
- No speculative improvements.
- No refactoring of unrelated code.

## Increments

- Large features are divided into small milestones.
- Every milestone must compile, pass tests, remain reviewable, and remain reversible.

## Stop Conditions

When the assigned task is complete:
- Stop.
- Do not begin the next mission.
- Do not implement additional features.
- Wait for explicit instructions for the next mission.

---

# AI Behaviour Rules

## Core Rules

1. **Understand before acting.** Never modify code without understanding where it belongs. Read the docs, inspect the module, inspect related modules, inspect tests.
2. **The repository is the source of truth.** Never assume, invent architecture, fabricate APIs, fabricate test results, or guess module names, file locations, or import paths. Always inspect.
3. **Report uncertainty explicitly.** State what is unknown, what was inspected, and what remains uncertain. Do not fabricate missing behaviour.
4. **Never continue into future missions.** When the assigned task is complete, stop.
5. **Never silently ignore errors.** Log, report, investigate every error. Never suppress error output.
6. **Inspect before modifying.** Read the file, identify imports, public API, callers, and dependencies before editing.
7. **Respect layer boundaries.** Lower layers never import higher layers.
8. **Verify after acting.** Verify imports, compilation, and tests after every modification.
9. **Preserve existing public APIs.** Add capabilities; never remove or rename without approval.
10. **Use the Windows environment.** Use PowerShell. Use `py` for Python, `py -m pytest` for tests, `py -m pip` for packages. Never assume Linux utilities.

## During Failure

1. Identify root cause.
2. Fix implementation.
3. Rerun the test suite.
4. Repeat until all tests pass.

Do not commit failing code. Do not ignore failures. Do not disable tests.

## During Uncertainty

1. State the uncertainty explicitly.
2. Offer the top 2-3 alternatives with trade-offs.
3. Wait for user direction.

Do not proceed with implementation during uncertainty.

## API Provider Constraints

- Never spawn parallel subagents or concurrent tasks.
- Execute one step at a time and wait for completion before starting the next.
- Set a timeout of at least 300000ms (5 minutes) on every bash or tool call.
- On rate-limit or server errors: wait 5 seconds, retry up to 3 times with exponential backoff, then report and stop.

---

# Output Format Rules

Every completed task must end with a structured report.

## Required Fields

### Architecture Summary
Describe how the implementation fits the existing architecture. Identify the affected layers. Identify dependencies introduced or modified. Confirm layer boundaries are preserved.

### Files Created
List every file created with its full path relative to the repository root.

### Files Modified
List every file modified with its full path relative to the repository root.

### Tests Added
List every test added with file path and test function names.

### Pytest Result
State the exact number passed, failed, and total runtime.

Format:
```
406 passed in 39.17s
```

### Remaining Work
State any remaining tasks for the current mission and any known limitations or incomplete areas.

If fully complete:
```
No remaining work. Task is complete.
```

## Prohibited Content

Never include:
- Emojis unless explicitly requested.
- Summaries of actions before or after the report.
- Commentary about the LLM, token limits, or platform.
- Praise or self-congratulation.
- Unsolicited follow-up questions.

The response must be the structured report and nothing else.

---

# Version History

## Version 1.0
- Initial release of the AMALGAM engineering constitution.
- Mission-independent, reusable forever.
- Supersedes no prior version in this scope.

---

# Document Maintenance

This document evolves with the project.
When the architecture changes, this document must be updated.
When new rules are established, this document must be updated.
When existing rules become insufficient, this document must be updated.

The repository is the source of truth.
This document is the operating manual for that truth.

AGENTS COMPLETE