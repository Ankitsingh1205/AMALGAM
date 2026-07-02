# AGENTS.md

# AMALGAM AI Operating Manual

Version: 1.0

Status: Active

This document is the authoritative operating manual for every AI coding agent working on AMALGAM.

Examples include but are not limited to:

- OpenCode
- Claude Code
- Continue
- Kimi
- OpenAI Codex
- Gemini CLI
- Cursor
- Cline
- Roo Code
- Future AI coding agents

Every implementation must follow this document.

If any prompt conflicts with AGENTS.md, this document takes priority unless the user explicitly overrides it.

---

# Project Identity

Project Name

AMALGAM

Project Type

Artificial Intelligence Operating System

Primary Language

Python

Architecture

Layered Modular Architecture

Development Style

Incremental Mission-Based Development

Current Development Methodology

Mission Driven Engineering

Every feature is implemented through numbered missions.

No feature may bypass the mission workflow.

---

# Project Vision

AMALGAM is an autonomous AI Operating System.

Its purpose is to become an intelligent software engineering platform capable of:

- Understanding projects
- Planning work
- Executing work
- Reviewing work
- Recovering from failures
- Learning from execution
- Operating multiple agents
- Managing tools
- Managing knowledge
- Coordinating autonomous software development

AMALGAM is NOT a chatbot.

AMALGAM is NOT a wrapper around an LLM.

AMALGAM is an engineering operating system.

Every design decision must move the project toward long-term autonomy.

Short-term convenience must never compromise long-term architecture.

---

# Core Architecture Principles

Every contribution to AMALGAM must preserve the following principles.

These principles are permanent.

Violating them requires explicit approval from the project owner.

---

## Principle 1

Architecture before implementation.

Never write code before understanding where it belongs.

If uncertain, inspect the repository first.

---

## Principle 2

Reuse before creation.

Before creating any new module:

- Search existing code.
- Reuse existing abstractions.
- Extend existing components where appropriate.

Duplicate implementations are forbidden.

---

## Principle 3

Layer separation.

Each layer has exactly one responsibility.

Responsibilities must never leak across layers.

---

## Principle 4

Composition over inheritance.

Prefer composing small reusable components.

Avoid deep inheritance trees.

---

## Principle 5

Deterministic behaviour.

The same input should produce the same output whenever possible.

Avoid hidden randomness.

---

## Principle 6

Small incremental changes.

Large rewrites are forbidden.

Implement features in small reviewable milestones.

Every milestone must leave the repository in a working state.

---

## Principle 7

Backward compatibility.

Existing public APIs must continue working.

Breaking APIs requires explicit approval.

---

## Principle 8

Mission-first development.

Every feature belongs to a Mission.

Never implement unrelated features during another Mission.

Avoid scope creep.

---

## Principle 9

Test before completion.

A task is not complete until:

- Tests pass.
- Existing tests continue passing.
- No regressions exist.

---

## Principle 10

The repository is the source of truth.

Never assume.

Never invent architecture.

Always inspect existing code before making design decisions.

---

# Core Engineering Principles

The following principles are permanent and must never be violated.

## 1. Single Responsibility

Every module should have one clearly defined responsibility.

A Planner plans.

A Scheduler schedules.

An Executor executes.

A Mission stores metadata.

No component should own responsibilities belonging to another layer.

---

## 2. Separation of Concerns

Planning, execution, persistence, routing, memory, scheduling, and tooling must remain independent.

Cross-layer shortcuts are forbidden.

---

## 3. Composition over Duplication

Before creating new code:

1. Search the repository.
2. Reuse existing modules.
3. Extend existing abstractions where appropriate.

Never duplicate working implementations.

---

## 4. Backward Compatibility

Existing public APIs must remain functional.

New capabilities must be additive.

Breaking changes require explicit user approval.

---

## 5. Deterministic Behaviour

Identical inputs should produce identical outputs whenever practical.

Avoid hidden randomness.

Avoid implicit global state.

---

## 6. Test-Driven Stability

Every implementation must include regression tests.

No feature is considered complete until the full test suite passes.

Never ignore failing tests.

---

## 7. Incremental Development

Large features must be divided into small milestones.

Each milestone should:

- compile
- pass tests
- remain reviewable
- remain reversible

---

## 8. Architecture First

Architecture is more important than implementation speed.

If a shortcut weakens long-term maintainability, reject it.

---

## 9. No Silent Assumptions

If required information is unavailable:

- inspect the repository
- inspect documentation
- inspect tests

Do not invent missing behaviour.

---

## 10. Minimal Changes

Modify the smallest amount of code necessary.

Prefer extending existing systems instead of rewriting them.

---

## 11. Strong Typing

Use Python typing consistently.

Avoid unnecessary use of Any.

Prefer explicit types.

---

## 12. Production Quality

Placeholder implementations are prohibited.

Temporary hacks are prohibited.

TODO-only implementations are prohibited.

Every committed implementation should be production quality.

---

## 13. Self Verification

Before reporting completion:

- run tests
- inspect modified files
- verify imports
- verify public APIs
- verify formatting

Never assume success without verification.

---

## 14. Repository Respect

Never rename large parts of the project.

Never reorganize folders unless explicitly requested.

Preserve repository history.

---

## 15. Long-Term Thinking

Every implementation should be evaluated against future scalability.

Choose designs that remain maintainable as AMALGAM grows.

---

# Repository Understanding Rules

Every AI agent must understand the repository before making changes.

Implementation without understanding is prohibited.

---

## Repository Inspection Order

Before modifying code, inspect the repository in the following order:

1. Project root
2. README.md
3. AGENTS.md
4. ARCHITECTURE.md
5. MISSION.md
6. TASK.md

After documentation review:

- inspect the target module
- inspect related modules
- inspect existing tests
- inspect dependency relationships

Only then begin implementation.

---

## Existing Code First

Always search the repository before creating new code.

Questions to answer before implementing:

- Does this already exist?
- Can this be reused?
- Can this be extended?
- Would duplication be created?

Prefer extension over duplication.

---

## Preserve Architecture

New code must follow the existing architecture.

Do not introduce parallel systems.

Do not create competing implementations.

Every new module should integrate naturally into the current design.

---

## Respect Layer Boundaries

Allowed dependency direction:

Mission
↓

Planner
↓

Scheduler
↓

Executor
↓

Tools

Higher layers may coordinate lower layers.

Lower layers must never depend on higher layers.

Examples:

✓ Planner may read Mission.

✓ Scheduler may use Planner.

✓ Executor may execute Scheduler output.

✗ Mission must never import Executor.

✗ Mission must never import Scheduler.

✗ Tools must never import Planner.

---

## File Modification Policy

Modify existing files only when necessary.

Create new files only when they introduce genuinely new functionality.

Avoid unnecessary file creation.

Avoid unnecessary file movement.

Avoid unnecessary renaming.

---

## Code Reuse Policy

Before implementing any feature:

1. Search the repository.
2. Search related modules.
3. Search tests.
4. Search utilities.

If an implementation already exists:

Reuse it.

If partial functionality exists:

Extend it.

Never duplicate production code.

---

## Repository Navigation

When exploring the repository:

Prefer reading

- architecture
- interfaces
- models
- tests

before implementation details.

Understanding the system is more valuable than immediately writing code.

---

## Documentation Awareness

Whenever documentation exists:

Treat documentation as part of the project.

Code should remain consistent with documentation.

If implementation differs from documentation:

Report the inconsistency.

Do not silently ignore it.

---

## Unknown Behaviour

If behaviour cannot be determined:

Inspect code.

Inspect tests.

Inspect documentation.

If uncertainty still exists:

Report uncertainty explicitly.

Never fabricate missing behaviour.

---

## Large Refactoring

Large refactoring is prohibited unless explicitly requested.

Examples:

- folder restructuring
- module splitting
- package renaming
- architecture replacement

These require user approval.

---

## Working Philosophy

Understand first.

Modify second.

Verify third.

Report fourth.

Never reverse this order.

---

# Coding Standards

Every implementation must follow these coding standards.

These rules apply to every language used in AMALGAM unless explicitly overridden.

---

## General Principles

Code must prioritize:

- readability
- maintainability
- determinism
- extensibility
- correctness

Code is written for humans first.

Performance optimizations should never reduce readability unless clearly justified.

---

## Python Standards

Use modern Python.

Prefer standard library solutions before introducing third-party dependencies.

Avoid unnecessary dependencies.

Use explicit imports.

Avoid wildcard imports.

Example:

✓ from pathlib import Path

✗ from pathlib import *

---

## Typing

All public functions should use type hints.

Prefer:

list[str]

dict[str, Any]

set[str]

tuple[...]

Avoid Any unless unavoidable.

Strong typing improves maintainability.

---

## Dataclasses

Prefer dataclasses for structured models.

Use:

- frozen=True when immutable
- slots=True when appropriate
- default_factory for mutable fields

Avoid mutable default arguments.

---

## Functions

Functions should perform one responsibility.

Avoid extremely long functions.

Prefer extracting helper methods over deeply nested logic.

Keep interfaces simple.

---

## Classes

Classes should represent one concept.

Avoid "God classes".

Prefer composition over inheritance unless inheritance is clearly justified.

---

## Naming

Use descriptive names.

Examples:

MissionGraph

MissionPlanner

ExecutionContext

Avoid abbreviations that reduce clarity.

---

## Comments

Comments should explain:

WHY

not

WHAT

Bad:

Increment x

Good:

Increment retry counter after transient network failure.

---

## Docstrings

Public classes and public methods should include concise docstrings.

Docstrings should describe:

- purpose
- parameters
- return values
- exceptions (when relevant)

---

## Logging

Use structured logging.

Avoid print() inside production code.

Log useful operational events.

Do not log secrets.

Do not log API keys.

Do not log credentials.

---

## Error Handling

Never silently swallow exceptions.

Catch only exceptions that can be handled.

Unexpected exceptions should propagate with meaningful context.

Avoid bare:

except:

Prefer specific exception types.

---

## Configuration

Configuration values should not be hardcoded.

Prefer configuration files or centralized constants.

Magic numbers should be avoided.

---

## Determinism

Repeated execution with identical inputs should produce identical outputs whenever practical.

Avoid hidden randomness.

Document any intentionally non-deterministic behavior.

---

## Performance

Optimize only after correctness.

Prefer algorithmic improvements over micro-optimizations.

Avoid premature optimization.

---

## Security

Never introduce:

- eval()
- exec()
- unsafe shell execution
- insecure deserialization

Validate external inputs.

Sanitize filesystem paths.

Treat user input as untrusted.

---

## Dependencies

Before adding a new dependency:

- justify its need
- verify maintenance status
- verify license compatibility

Prefer existing project dependencies whenever possible.

---

## Code Quality Checklist

Before considering implementation complete:

✓ Code compiles

✓ Imports resolve

✓ Tests pass

✓ Type hints added

✓ Public APIs preserved

✓ Logging appropriate

✓ No duplicate logic

✓ No dead code

✓ No placeholder implementations

✓ Documentation updated where necessary

---

# Implementation Workflow

Every implementation must follow this workflow.

Skipping steps is prohibited.

---

## Phase 1 — Understand

Before writing code:

1. Read AGENTS.md
2. Read ARCHITECTURE.md
3. Read MISSION.md
4. Read TASK.md
5. Inspect the target module
6. Inspect related modules
7. Inspect existing tests

Do not begin implementation until sufficient understanding has been established.

---

## Phase 2 — Plan

Before modifying code:

- identify affected modules
- identify dependencies
- identify public APIs
- identify existing tests
- identify possible regressions

Implementation should begin only after a clear plan exists.

---

## Phase 3 — Implement

Modify the minimum amount of code necessary.

Prefer extending existing modules.

Avoid introducing unnecessary abstractions.

Avoid unnecessary files.

Keep changes focused on the current task.

---

## Phase 4 — Verify

After implementation:

- verify imports
- verify formatting
- verify typing
- verify serialization
- verify compatibility
- verify public APIs

Every change should be validated before testing.

---

## Phase 5 — Test

Always execute the complete project test suite.

Never assume success.

Fix regressions before reporting completion.

If tests fail:

- identify root cause
- fix implementation
- rerun tests

Repeat until stable.

---

## Phase 6 — Review

Before reporting completion:

Review:

- architecture
- maintainability
- readability
- duplication
- performance
- security

Improve implementation if necessary.

---

## Phase 7 — Report

Every completed task must end with a structured report.

The report should contain:

- Architecture Summary
- Files Modified
- Tests Added
- Total Tests Passing
- Remaining Work

Do not include unnecessary commentary.

---

# Definition of Done

A task is considered complete only if:

✓ Implementation is complete

✓ Public APIs remain compatible

✓ No duplicate logic exists

✓ Documentation remains consistent

✓ All tests pass

✓ No regressions are introduced

✓ The implementation follows the architecture

✓ The repository remains buildable

If any requirement is not satisfied, the task is NOT complete.

---

# AI Agent Behaviour

Every AI agent working on AMALGAM must operate according to the following behavioural
rules. These rules apply to every agent regardless of implementation language, model
provider, or host platform.

---

## Core Behavioural Rules

### Rule 1 — Understand Before Acting

Never modify code without understanding where it belongs in the architecture.

Before any modification:

- Read AGENTS.md.
- Read ARCHITECTURE.md.
- Read MISSION.md (when present).
- Read TASK.md (when present).
- Inspect the target module.
- Inspect related modules.
- Inspect existing tests.

Implementation without understanding is prohibited.

---

### Rule 2 — The Repository Is the Source of Truth

Never assume.

Never invent architecture.

Never fabricate APIs that do not exist in the repository.

Never fabricate test results.

Never fabricate repository state.

Never guess module names, file locations, or import paths.

Always inspect the repository before answering or acting.

---

### Rule 3 — Report Uncertainty Explicitly

If the required information cannot be determined:

- State what is unknown.
- State what was inspected.
- State what remains uncertain.

Do not proceed with implementation until uncertainty is resolved.

Do not fabricate missing behaviour.

Do not pretend certainty.

---

### Rule 4 — Never Continue Into Future Missions

When the assigned task or mission is complete:

Stop.

Do not begin the next mission.

Do not implement additional features.

Do not make speculative improvements.

Do not refactor unrelated code.

Wait for explicit instructions for the next mission.

---

### Rule 5 — Never Silently Ignore Errors

Every error must be:

- Logged.
- Reported.
- Investigated.

Never catch an exception and do nothing.

Never suppress error output.

Never hide test failures.

If an error cannot be handled, escalate it explicitly.

---

### Rule 6 — Inspect Before Modifying

Before modifying any file:

- Read the file first.
- Identify its imports.
- Identify its public API.
- Identify its callers.
- Identify its dependencies.

Do not edit a file until its role in the system is understood.

---

### Rule 7 — Respect Layer Boundaries

Allowed dependency direction:

```
Mission
  ↓
Planner
  ↓
Scheduler
  ↓
Executor
  ↓
Tools / Services / Knowledge / Memory
```

Higher layers may coordinate lower layers.

Lower layers must never import higher layers.

Violating layer boundaries requires explicit user approval.

---

### Rule 8 — Verify After Acting

After every modification:

- Verify imports resolve.
- Verify the file compiles.
- Run the complete test suite.
- Fix any regression before reporting completion.

Never assume success without verification.

---

### Rule 9 — Preserve Existing Public APIs

Existing public methods, classes, and module-level exports must continue to work.

Add new capabilities.

Never remove existing functionality without explicit approval.

Never rename public APIs without explicit approval.

---

### Rule 10 — Use the Windows Environment

Always use PowerShell commands.

Python commands:

- `py` for invoking Python.
- `py -m pytest` for running tests.
- `py -m pip` for package management.

Never assume Linux utilities (cat, head, grep, tail).

Repository root is `C:\AMALGAM`.

---

## Behaviour During Failure

If tests fail after a modification:

1. Identify the root cause.
2. Fix the implementation.
3. Rerun the test suite.
4. Repeat until all tests pass.

Do not commit code with failing tests.

Do not ignore test failures.

Do not disable tests to make the suite pass.

---

## Behaviour During Uncertainty

If the correct action is unclear:

1. State the uncertainty explicitly.
2. Offer the top 2–3 alternatives with trade-offs.
3. Wait for user direction.

Do not proceed with implementation during uncertainty.

---

# Git Workflow

Every AI agent must follow this workflow for all Git operations.

Violating these rules requires explicit user approval.

---

## Rule 1 — Never Commit Automatically

Commits must only be made when explicitly requested by the user.

Do not commit after completing a task unless the user asks for it.

Do not commit as part of a cleanup step.

Do not commit to save progress.

---

## Rule 2 — Never Push Automatically

Pushes must only be made when explicitly requested by the user.

Do not push after a commit unless the user asks for it.

Do not force-push under any circumstances.

Force-push is forbidden unless the user explicitly overrides this rule.

---

## Rule 3 — Never Rewrite Git History

Never use:

- `git rebase`
- `git commit --amend`
- `git reset --hard`
- `git push --force`
- `git push --force-with-lease`

Unless explicit user approval is given.

---

## Rule 4 — Always Inspect Before Committing

Before committing, the agent must:

- Inspect `git status`.
- Inspect `git diff`.
- Inspect `git log --oneline -10`.
- Verify that only intended files are staged.
- Verify that no secrets are staged.

---

## Rule 5 — Never Stage Unrelated Files

A commit must contain only files directly related to the current task.

Never stage:

- Unrelated modifications.
- Temporary files.
- Backup files (`*.bak`).
- Cache directories.
- Virtual environment files.
- IDE configuration files.

---

## Rule 6 — Never Commit Secrets

Never commit:

- API keys.
- Passwords.
- Tokens.
- Cookies.
- Private keys.
- Environment files with secrets.
- Configuration files with credentials.

Inspect every staged file for secret content before committing.

---

## Rule 7 — Write Concise Commit Messages

Commit messages must be:

- One line of summary (under 72 characters).
- Descriptive of what changed and why.
- Consistent with existing repository style.

Example:

```
Add workspace boundary enforcement to FileTool (Mission 6.4.4)
```

---

## Rule 8 — Pull Before Working

Before starting any modification:

- Inspect `git status` for pending changes.
- Inspect `git log --oneline -5` for recent activity.
- If there are upstream changes, report them.

Never start work on a stale branch without informing the user.

---

## Rule 9 — No Empty Commits

Never create an empty commit.

Never use `git commit --allow-empty`.

---

# Standard Response Format

Every completed task must end with a structured response using the following format.

---

## Required Fields

### Architecture Summary

Describe how the implementation fits into the existing architecture.

Identify the layer(s) affected.

Identify dependencies introduced or modified.

Confirm that layer boundaries are preserved.

---

### Files Created

List every file created with its full path relative to the repository root.

---

### Files Modified

List every file modified with its full path relative to the repository root.

---

### Tests Added

List every test added (file path and test function names).

---

### Pytest Result

State the exact number of tests passed, failed, and the total runtime.

Format:

```
406 passed in 39.17s
```

---

### Remaining Work

State any remaining tasks for the current mission.

State any known limitations or incomplete areas.

If the task is fully complete, state:

```
No remaining work. Task is complete.
```

---

## Example

```
Architecture Summary

Added workspace boundary enforcement to FileTool at the tools layer.
No new dependencies. Layer boundaries preserved.

Files Created

None.

Files Modified

tools/file_tool.py

Tests Added

tests/test_file_tool.py::test_file_tool_rejects_path_traversal
tests/test_file_tool.py::test_file_tool_allows_workspace_paths

Pytest Result

408 passed in 41.23s

Remaining Work

No remaining work. Task is complete.
```

---

## Prohibited Response Content

Never include:

- Emojis (unless the user explicitly requests them).
- Summaries of your actions before or after the report.
- Commentary about the LLM, token limits, or platform.
- Praise or self-congratulation.
- Unsolicited follow-up questions.

The response must be the structured report and nothing else.

---

# Layer Ownership

Every layer in AMALGAM has exactly one responsibility and a defined set of
permitted actions.

Violating layer ownership requires explicit user approval.

---

## Layer Ownership Table

| Layer | Primary Responsibility | Must Never Do |
|---|---|---|
| **Mission** | Store mission metadata (id, title, status, dependencies). Define the dependency graph. Serialize/deserialize missions. | Execute work. Schedule agents. Interact with tools. Import Executor or Scheduler. |
| **Planner** | Create plans and tasks from user intent. Decompose missions into executable steps. Generate goal objects. | Execute tasks. Dispatch to tools. Interact with services directly. Modify mission metadata. |
| **Scheduler** | Execute agents in ordered pipelines. Manage parallel execution. Resolve dependencies. | Plan missions. Execute tasks directly. Own mission data. Import upper-layer agents for execution. |
| **Executor** | Boot the kernel. Dispatch tasks to tools/services via the Dispatcher. Execute the autonomous goal loop. | Plan tasks. Schedule agents. Own mission metadata. Modify shared context outside of execution. |
| **Tools** | Provide concrete capabilities (calculator, file operations, Python execution, memory, internet). | Plan tasks. Route actions. Import Planner or Scheduler. Make architectural decisions. |
| **Memory** | Persist key-value data to disk. Provide recall/remember/forget operations. Manage execution memory. | Plan tasks. Dispatch work. Import brain-level orchestrators. |
| **Knowledge** | Build project knowledge graphs. Index symbols, documents, and relationships. Provide search capabilities. | Execute work. Route tasks. Modify project files. |
| **Agents** | Coordinate multi-agent pipelines (PlannerAgent, ResearchAgent, ReviewerAgent, EngineerAgent). | Bypass the Dispatcher for tool access. Execute tools directly without registration. Own lower-layer data. |
| **Config** | Provide centralized constants and settings. Define action names, intent names, tool names, service names, statuses. | Execute any logic. Import any other project module. Depend on runtime state. |
| **Services** | Provide infrastructure (LLM, Ollama, logging, diagnostics, project). Register services for discovery. | Own business logic. Plan tasks. Route actions. |
| **Models** | Map model roles to model names. Select models based on task type. | Execute inference directly. Own business logic. |
| **Workspace** | Provide read-only project metadata (root, packages, dependencies, tree, Git info). | Modify files. Execute actions. Change Git history. Alter routing. |

---

## Dependency Direction Diagram

```
agents/
  ↓  imports from
brain/
  ↓  imports from
kernel/
  ↓  imports from
services/  tools/  models/
  ↓  imports from
config/

(standalone branch)
services/project_service.py
  →  workspace/    (leaf — imports nothing)
  →  knowledge/
      →  workspace/    (workspace never imports knowledge)
```

No circular dependencies exist in the core module graph.
Verify all 130+ modules follow this DAG before adding new imports.


## Enforcement

Before writing code in any layer, verify:

1. The component belongs to this layer.
2. The component does not own responsibilities of another layer.
3. The component does not import a layer above it.

If uncertainty exists, inspect the layer ownership table before proceeding.

---

# Refactoring Policy

Refactoring is restructuring existing code without changing its external behavior.

---

## When Refactoring Is Allowed

Refactoring may be performed when:

- Explicitly requested by the user.
- Required to fix a bug that cannot be fixed without restructuring.
- Required to integrate a new feature that cannot be added without restructuring (with user approval).

Refactoring is NOT allowed when:

- Unrelated to the current mission.
- Driven by personal preference.
- Driven by speculative future needs.
- Performed as a cleanup step after completing a task.

---

## How to Preserve Compatibility

Before refactoring:

1. Identify every public API in the affected module.
2. Identify every caller of every public API.
3. Ensure every existing caller will continue to work.

During refactoring:

- Keep public method signatures unchanged.
- Keep public class names unchanged.
- Keep module-level exports unchanged.

After refactoring:

- Run the full test suite.
- Verify all existing tests pass.
- Verify no regression in caller modules.

---

## Regression Requirements

A refactor is not complete until:

- All existing tests pass.
- No test was modified to accommodate the refactor.
- No test was removed.
- The full test suite completes in comparable time.

---

## Architecture Review Requirements

Large refactors require:

- User approval before starting.
- An architecture impact analysis before implementing.
- A structured report after completion.

Examples of large refactors:

- Folder restructuring.
- Module splitting.
- Package renaming.
- Architecture replacement.
- API signature changes.

These are prohibited unless explicitly requested.

---

# Security Policy — Expanded

The following security rules extend the existing Coding Standards security section.
Every rule in this section is permanent and must never be violated.

---

## Secret Handling

Never log:

- API keys.
- Passwords.
- Tokens.
- Cookies.
- Secrets.
- Private keys.
- Environment variables containing credentials.
- Any value that grants access to external systems.

Never expose credentials in:

- Print statements.
- Log records.
- Error messages.
- Return values.
- Exception messages.
- Source code comments.

Never write secrets into source control:

- Inspect every staged file for secret content before committing.
- Use environment variables or configuration files for credentials.
- Never hardcode credentials in source files.

---

## Path Traversal Prevention

Every filesystem operation must enforce workspace boundaries.

Before reading, writing, or deleting a file:

1. Resolve the path with `Path.resolve()`.
2. Verify the resolved path is within the workspace root.
3. Reject paths that escape the workspace root.
4. Log the rejection.

Never allow user-controlled input to specify arbitrary filesystem paths without
boundary validation.

---

## Input Sanitization

Treat every external input as untrusted:

- User input from the CLI.
- LLM output.
- Data loaded from disk.
- Data received over the network.
- Data from external APIs.

Before passing input to any tool or service:

1. Validate the input type.
2. Validate the input length.
3. Validate the input structure.
4. Reject inputs that do not match expected schemas.

Never pass raw user input to `eval()`, `exec()`, `os.system()`, or `subprocess`.

---

## Least Privilege

Every tool and service should operate with the minimum permissions necessary.

- FileTool: operate within workspace boundaries only.
- PythonExecutor: execute in a restricted sandbox.
- Calculator: restrict to arithmetic operations only.
- MemoryService: restrict to configured memory file path.

Never grant a tool more access than its defined responsibility requires.

---

## Audit Trail

Every execution step must be recorded in ExecutionMemory with:

- Timestamp.
- Goal ID.
- Step name.
- Action taken.
- Result or error.

This ensures every autonomous action is traceable and debuggable.

---

# Error Recovery Policy

When an execution failure occurs, AMALGAM follows a canonical recovery workflow.

---

## Standard Recovery Workflow

```
Implementation
  ↓
Verification
  ↓
Testing
  ↓
Failure Detected
  ↓
Fix
  ↓
Retest
  ↓
Report
```

---

## Recovery Steps

### 1. Detect Failure

Failures are detected by the Evaluator during the autonomous execution loop.

Failure sources:

- Explicit errors returned by tools/services.
- Error strings in tool/service output.
- Timeout during execution.
- Missing output.

---

### 2. Reflect

The ReflectionEngine analyzes the failure:

- Classifies the root cause (missing dependency, invalid path, runtime exception,
  wrong tool, wrong plan, service unavailable, unknown).
- Selects a recovery strategy (retry, replan, alternative, user, give_up).

---

### 3. Retry

The RetryManager decides the next step:

- If retries remain: retry with the same approach.
- If retries exhausted and strategy is retry: try an alternative approach.
- If retries exhausted and strategy is alternative: replan the goal.
- If retries exhausted and strategy is replan: escalate to user.
- If all strategies exhausted: give up and mark goal FAILED.

Maximum retry count is defined in `config/constants.py` (`MAX_RETRY_COUNT`).

---

### 4. Replan (If Applicable)

When the strategy is replan:

- Clear pending tasks from the queue.
- Reset the retry budget.
- Increment the plan version.
- Generate a new plan from the goal description.
- Create new tasks from the new plan.
- Enqueue the new tasks.
- Transition back to RUNNING.

---

### 5. Escalate (If Applicable)

When all automated strategies are exhausted:

- Mark the goal FAILED.
- Record the error in the goal object.
- Include the error in the execution report.
- Do not silently discard the failure.

---

### 6. Report

After recovery (successful or not):

- Record the final goal state in ExecutionMemory.
- Return the goal to the caller.
- The caller (OrchestratorAgent or EngineerAgent) reports the outcome.

---

## Recovery Constraints

- Never retry indefinitely. Always enforce `MAX_RETRY_COUNT`.
- Never skip reflection. Every failure must be analyzed.
- Never swallow errors. Every failure must be recorded.
- Never mark a paused goal as FAILED (pause should transition to PAUSED, not FAILED).

---

# Forbidden Actions

The following actions are permanently forbidden in AMALGAM.

Violating any of these rules requires explicit user approval.

---

## Implementation Forbidden Actions

- Placeholder implementations.
- TODO-only implementations.
- Dead code (functions, classes, or variables never used).
- Duplicate implementations (implementing something that already exists).
- Temporary hacks intended to be "fixed later".

Every committed implementation must be production quality.

---

## Architecture Forbidden Actions

- Unrelated refactoring during a mission.
- Automatic dependency upgrades.
- Breaking public APIs.
- Creating competing implementations of existing systems.
- Introducing parallel systems.
- Skipping layer boundaries.

---

## Execution Forbidden Actions

- Silent failures (swallowing exceptions without logging or reporting).
- Infinite retry loops.
- Executing tasks without evaluation.
- Bypassing the Dispatcher for tool access.
- Executing tools without ToolRegistry registration.

---

## Repository Forbidden Actions

- Committing without explicit user request.
- Pushing without explicit user request.
- Force-pushing.
- Rewriting Git history.
- Committing secrets or credentials.
- Renaming directories without user approval.
- Reorganizing folders without user approval.

---

## Testing Forbidden Actions

- Disabling tests to make the suite pass.
- Modifying tests to match broken implementation.
- Removing tests without replacement.
- Reporting success without running tests.
- Fabricating test results.

---

# Documentation Policy

Documentation is part of the project and must remain consistent with the code.

---

## Public API Documentation

Every public class and public method must have a docstring describing:

- Purpose.
- Parameters (names, types, meanings).
- Return value (type and meaning).
- Exceptions raised (when relevant).

Example:

```python
def evaluate(self, output: Any = None, error: Optional[str] = None,
             expected: Any = None) -> dict:
    """Evaluate an execution result and return a structured verdict.

    Args:
        output: The raw execution output.
        error: An error string, if any.
        expected: An optional expected value for comparison.

    Returns:
        A dictionary with keys: status, verified, message, output.
    """
```

---

## Architecture Documentation

Architecture documentation lives in `docs/Architecture.md`.

When a new module is added:

- Document its purpose.
- Document its layer.
- Document its public API.
- Document its dependencies.

When architecture changes:

- Update `docs/Architecture.md` in the same commit as the code change.
- Never leave architecture documentation out of sync with the code.

---

## Mission Documentation

Mission documentation lives in `docs/missions/`.

Each mission must have:

- A mission number (e.g., `MISSION_7_1`).
- A description of what the mission implements.
- A list of files affected.
- A list of tests added.
- A status (planned, in_progress, completed, blocked).

Mission documentation files should not remain empty. If a mission file exists,
it must contain the mission specification.

---

## Keeping Documentation Synchronized

When code changes:

- If public APIs change: update docstrings.
- If architecture changes: update `docs/Architecture.md`.
- If mission specification changes: update `docs/missions/`.
- If the changelog is affected: update `docs/Changelog.md`.

Never modify code without updating the corresponding documentation.

---

## Documentation Quality

Documentation must be:

- Accurate (matches the current code).
- Actionable (can be used to understand how to use or modify the system).
- Concise (no filler, no speculation, no future plans).

Documentation must NOT be:

- Outdated (describing behaviour that no longer exists).
- Speculative (describing future features as if they exist).
- Placeholder (empty files with meaningful names).
- Vague (using ambiguous language).

---

# Stop Conditions

After completing the assigned task:

Stop.

Do not continue into the next milestone.

Do not implement additional features.

Do not make speculative improvements.

Wait for the next task.

---

# Version History

## Version 1.0

- Initial release of the AMALGAM AI Operating Manual.
- Compiled during Mission 7.
- Incorporates all Mission 6 architecture, security audit findings, and
  Mission 7 infrastructure planning.

## Current Status

- Document status: Active.
- Document purpose: Permanent operating manual for every AI agent working on AMALGAM.
- Supersedes: No prior version.
- Mandatory reading for: All AI coding agents before any repository modification.

---

## Document Maintenance

This document evolves with the project.

When the architecture changes, this document must be updated.

When new rules are established, this document must be updated.

When existing rules are found to be insufficient, this document must be updated.

The repository is the source of truth.

This document is the operating manual for that truth.

