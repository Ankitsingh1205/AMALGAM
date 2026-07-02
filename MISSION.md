# AMALGAM Mission

Version: 1.0
Status: Active

This document is the live engineering roadmap for AMALGAM.
It documents only the current repository state and active mission.
It does not speculate about future implementations.

---

## Project Overview

| Field | Value |
|-------|-------|
| Project Name | AMALGAM |
| Current Version | 0.3.0 |
| Current Branch | `mission-7` |
| Current Active Mission | Mission 7 — Mission Engine |
| Current Milestone | Mission 7.1.5 — Event Bus Integration |
| Current Objective | Implement Mission Event Bus while preserving backward compatibility and maintaining a regression-free codebase |
| Overall Objective | Build an autonomous AI Operating System capable of understanding projects, planning work, executing work, reviewing work, recovering from failures, learning from execution, operating multiple agents, managing tools and knowledge, and coordinating autonomous software development |

---

## Mission Roadmap

| Mission | Objective | Status | Completion |
|---------|-----------|--------|------------|
| Genesis 1–5 | Core infrastructure: Brain, Planner, Executor, Dispatcher, Intent detection | Completed | 100% |
| Genesis 6–8 | Tool system: ToolRegistry, ActionRegistry, BaseTool, Calculator, PythonExecutor, FileTool | Completed | 100% |
| Mission 2 | Infrastructure: settings, constants, structured logging, diagnostics, version metadata | Completed | 100% |
| Mission 3 | Workspace Engine: read-only project introspection, scanner, analyzer, tree, git, dependency | Completed | 100% |
| Mission 4 | Knowledge Engine: AST parsing, symbol extraction, relationship builder, graph, search | Completed | 100% |
| Mission 5 | Agent Framework: BaseAgent, multi-agent pipeline, Scheduler, SharedContext, Messaging | Completed | 100% |
| Mission 6 | Autonomous Execution: Goal state machine, Evaluator, ReflectionEngine, RetryManager, TaskQueue, ExecutionMemory | Completed | 100% |
| Mission 6.4.3 | Security Audit: identified 3 critical, 6 high, 6 medium, 5 low findings | Completed | 100% |
| Mission 6.6 | Architecture documentation: initial ARCHITECTURE.md | Completed | 100% |
| Mission 7 | Mission Engine: Mission Core modules, Planner integration, persistence, event bus, and full regression suite | In Progress | ~75% |
| Mission 7.1.0 | Mission Core: Mission, MissionStatus, MissionPriority, MissionID dataclasses | Completed | 100% |
| Mission 7.1.1 | Epic: mission grouping and metadata | Completed | 100% |
| Mission 7.1.2 | Mission Graph: DAG with topological sort and cycle detection | Completed | 100% |
| Mission 7.1.3 | Planner Integration: Mission-aware plan generation | Completed | 100% |
| Mission 7.1.4 | Persistence: serialization/deserialization for Mission, Epic, MissionGraph | Completed | 100% |
| Mission 7.1.5 | Event Bus Integration: event publication, subscription, mission lifecycle notifications | In Progress | ~40% |
| Mission 7.2 | ChiefAgent orchestration | Pending | 0% |
| Mission 7.3 | FleetManager — agent lifecycle | Pending | 0% |
| Mission 7.4 | WorkPool — capability-based task distribution | Pending | 0% |
| Mission 7.5 | DependencyResolver — task DAG scheduler | Pending | 0% |
| Mission 7.6 | CapabilityRouter — load-aware routing | Pending | 0% |
| Mission 7.7 | KnowledgeRouter — topic-based context filtering | Pending | 0% |
| Mission 7.8 | Integration and end-to-end testing | Pending | 0% |

---

## Current Mission

### Mission 7 — Mission Engine

**Objective:** Build a complete Mission Engine subsystem including Mission Core dataclasses, Epic grouping, Mission Graph with DAG operations, Planner integration, persistence layer, event bus, and full regression suite.

### Completed Milestones

| Milestone | Description | Delivered |
|-----------|-------------|-----------|
| M7.1.0 | Mission Core: Mission, MissionStatus, MissionPriority, MissionID dataclasses with lifecycle and state transitions | `brain/mission/mission.py`, `brain/mission/mission_status.py`, `brain/mission/mission_priority.py`, `brain/mission/mission_id.py` |
| M7.1.1 | Epic: mission grouping and metadata container | `brain/mission/epic.py` |
| M7.1.2 | Mission Graph: DAG with topological sort (Kahn's), cycle detection, add/remove nodes and edges, validation | `brain/mission/graph.py` |
| M7.1.3 | Planner Integration: mission-aware plan generation — Planner reads Mission context and generates tasks aligned with mission objectives | `brain/planner/` |
| M7.1.4 | Persistence: serialization/deserialization (`to_dict()`/`from_dict()`) for Mission, Epic, and MissionGraph objects | `brain/mission/mission.py`, `brain/mission/epic.py`, `brain/mission/graph.py` |

### Current Milestone

**Mission 7.1.5 — Event Bus Integration.** Implement event publication, subscription, and mission lifecycle notifications while preserving backward compatibility and maintaining a regression-free codebase.

### Remaining Milestones (Within Mission 7)

| Milestone | Description |
|-----------|-------------|
| M7.1.5 | Event Bus: event publication, subscription, lifecycle event dispatch |
| M7-DOC | Populate empty mission specification files in `docs/missions/` with requirements |
| M7-SEC | Address 3 critical security findings from Mission 6.4.3 audit |
| M7-AUDIT | Full regression run, documentation audit, branch merge |

### Current Implementation Status

- Mission Core (7.1.0–7.1.4): fully implemented and tested
- Event Bus (7.1.5): in progress — event bus module under development
- 437 tests passing, 0 regressions
- 3 critical, 6 high security findings from Mission 6.4.3 audit remain unresolved
- 12 mission specification files in `docs/missions/` remain empty
- All four root documentation files (AGENTS.md, ARCHITECTURE.md, MISSION.md, TASK.md) are active

---

## Repository Health

| Metric | Value |
|--------|-------|
| Passing Tests | 437 |
| Test Framework | pytest |
| Test Files | 75 files in `tests/` |
| Regression Status | No known regressions |
| Architecture Stability | Stable — layered DAG with no circular imports (130+ modules verified) |
| Documentation Status | AGENTS.md (1996 lines), ARCHITECTURE.md (1432 lines), MISSION.md — all active and v1.0 |
| Code Quality Status | Production quality per AGENTS.md standards. Placeholder files exist in `docs/missions/` and some directories (`storage/cache/`, `plugins/`, `modules/`, `apps/`, `voice/`, `vision/`). `brain/session.py` is a placeholder. |
| Current Branch Status | `mission-7` — 2 commits ahead of baseline |
| Entry Point | `main.py` — Brain → Planner → Task → Executor → Dispatcher → Tool/Service |
| Python Version | Modern Python (via `pyproject.toml`) |

---

## Quality Metrics

| Metric | Value |
|--------|-------|
| Passing tests | 437 |
| Known regressions | 0 |
| Known technical debt | Placeholder files: `brain/session.py`, 12 empty `docs/missions/*.md` files, 7 empty future-layer directories |
| Known blockers | 3 critical security findings (eval/exec on unsanitized input, path traversal in FileTool). No input sanitization on user input. No workspace boundary enforcement. |
| Documentation completeness | AGENTS.md: complete (1996 lines). ARCHITECTURE.md: complete (1432 lines). MISSION.md: active. `docs/missions/`: 12 files empty. `docs/Changelog.md`: sparse. DECISIONS.md: does not exist. |

---

## Current Focus

### What Engineers Should Work On Next

1. **Mission 7.1.5 — Event Bus Integration** — Implement event publication, subscription, and mission lifecycle notifications
2. **Mission 7.2 — ChiefAgent** — Adaptive mission orchestration (after Event Bus)
3. **Security remediation** — Fix 3 critical findings: sanitize `exec()`/`eval()` inputs, workspace boundary enforcement in FileTool
4. **Populate mission specs** — Fill in the 12 empty `docs/missions/` files

### What Must NOT Be Changed

- The canonical runtime flow: User → Brain → Planner → Task → Executor → Dispatcher → Tool/Service
- Layer boundaries and import DAG direction
- Existing public APIs of Mission Core and Mission Graph classes
- AGENTS.md and ARCHITECTURE.md existing content (append only)

### Current Priorities

| Priority | Item |
|----------|------|
| P0 | Mission 7.1.5 — Event Bus Integration |
| P1 | Security: fix 3 critical audit findings |
| P2 | Implementation: Mission 7.2–7.8 in dependency order |
| P3 | Documentation: populate `docs/missions/` files |

---

## Next Milestones

| Order | Milestone | Description | Dependencies |
|-------|-----------|-------------|--------------|
| 1 | M7.1.5 | Event Bus Integration: event publication, subscription, lifecycle notifications | Mission 7.1.0–7.1.4 |
| 2 | M7-SEC | Remediate critical security findings (input sanitization, path traversal) | None |
| 3 | M7-DOC | Populate `docs/missions/MISSION_7_2.md` through `MISSION_7_8.md` | None |
| 4 | M7.2 | ChiefAgent adaptive orchestration | Event Bus |
| 5 | M7.3 | FleetManager agent lifecycle management | ChiefAgent |
| 6 | M7.4 | WorkPool capability-based distribution | FleetManager |
| 7 | M7.5 | DependencyResolver task DAG | WorkPool |
| 8 | M7.6 | CapabilityRouter load-aware routing | DependencyResolver |
| 9 | M7.7 | KnowledgeRouter topic-based filtering | CapabilityRouter |
| 10 | M7.8 | Integration and end-to-end tests | All M7.x sub-missions |
| 11 | M7-AUDIT | Full regression run, documentation audit, branch merge | M7.8 |

---

## Risks

| Risk | Category | Severity | Description | Mitigation |
|------|----------|----------|-------------|------------|
| Unsanitized eval/exec | Security | Critical | `Calculator.calculate()` and `PythonExecutor.execute()` pass user input directly to `eval()` and `exec()` | Add input validation allow-lists before tool execution |
| Path traversal in FileTool | Security | Critical | FileTool does not validate that resolved paths stay within workspace boundary | Add `Path.resolve()` + prefix check before all file operations |
| No cancellable timeouts | Security | High | Thread timeouts do not kill threads — non-cancellable execution | Replace thread-based timeout with subprocess-based execution |
| Prompt injection | Security | High | No input sanitization before LLM calls | Add prompt boundary markers and input validation |
| Empty mission docs | Process | Medium | 12 `docs/missions/` files are empty — mission requirements are not recorded | Populate with requirements before implementation |
| Placeholder code | Code Quality | Low | `brain/session.py` contains no implementation | Either implement or remove |
| Stale cache directory | Storage | Low | `storage/cache/`, `storage/embeddings/`, `storage/knowledge/` are empty | Clean up if unused, document if reserved |
| No file locking | Persistence | Medium | `memory.json` has no concurrent access protection | Add file locking or switch to SQLite |
| Pause → FAILED bug | State Machine | Medium | Pausing a goal incorrectly forces FAILED state instead of PAUSED | Fix state transition in Goal |

---

## Definition of Mission Complete

Mission 7 is complete when all of the following criteria are satisfied:

- All Mission 7.x sub-missions (7.1.0 through 7.8) are implemented and tested
- Mission Event Bus supports publication, subscription, and lifecycle event dispatch
- ChiefAgent, FleetManager, WorkPool, DependencyResolver, CapabilityRouter, KnowledgeRouter are implemented
- All 437+ tests pass with no regressions
- The 12 empty `docs/missions/` files are either populated or explicitly removed
- No breaking changes to existing public APIs
- Layer boundaries and import DAG are preserved
- Branch `mission-7` is ready for merge

A sub-mission (7.x) is complete only when:

- Its implementation is production quality
- Its tests exist and pass
- Its documentation in `docs/missions/` is populated
- No regressions exist in the wider test suite
- All layer boundaries are preserved
