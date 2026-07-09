# MASTER_ARCHITECTURE_PLAN.md

**The single source of truth for AMALGAM future development.**

Status: Active planning baseline
Scope: Synthesizes only the authorized recovery/canon documents. Adds nothing new.

---

## Preamble

This document is the consolidated starting point for all future AMALGAM work. It is built
**only** from these seven sources and cites them throughout:

- PROJECT_CONSTITUTION.md (permanent laws)
- MISSION_CANON.md (authoritative registry of executed missions)
- ROADMAP_CANON.md (reserved mission namespace 7.4-10)
- CURRENT_ARCHITECTURE_STATE.md (code-as-implemented)
- IMPLEMENTATION_HISTORY.md (repository/git evidence)
- RECOVERY_VALIDATION.md (cross-validation, conflicts, confidence)
- CONVERSATION_INDEX_STEP4_DECISIONS.md (extracted design decisions)

**Rules honored in this document:**
- No new missions are invented; no Mission 7.4+ implementation is defined.
- Uncertainty is preserved. Where a fact is not established by the sources, it is written as
  **UNKNOWN**. Gaps are not filled with assumptions.
- Conflicts are recorded, not resolved (per PROJECT_CONSTITUTION governance and the
  RECOVERY_VALIDATION conflict register).

---

## 1. Current AMALGAM State

**Two distinct runtimes exist and must not be confused** (source: CURRENT_ARCHITECTURE_STATE, preamble):
1. **The AMALGAM application** — `main.py` + `kernel/brain/agents/...` (the actual program).
2. **The `.amalgam-core` engineering loop** — `scripts/` + `.amalgam-core/` (development
   tooling that tracks mission progress; NOT imported or run by the application).

**Wired execution surfaces** (source: CURRENT_ARCHITECTURE_STATE §1):
- **Primary CLI path (single-task):** `main.py` -> `Brain.think()` -> `kernel.Executor.execute()`
  -> `Dispatcher.dispatch()` -> Tool or Service (via `ActionRegistry`), LLM fallback for
  `chat`/`generate_code`. Maturity: **STABLE**.
- **Multi-agent path (task/mission orchestration):** `OrchestratorAgent` / `ChiefAgent` ->
  `Scheduler` or `WorkPool`+`FleetManager` -> agents -> `EngineerAgent` -> `AutonomousExecutor`
  -> back to the same kernel. Maturity: **FUNCTIONAL**, but **not driven from `main.py`**
  (reachable only by direct instantiation).

**Subsystem maturity summary** (source: CURRENT_ARCHITECTURE_STATE §2):
Kernel / Tools / Services / Engines = STABLE; Autonomous Executor + Mission Engine + Multi-Agent
= FUNCTIONAL; ChiefAgent distributed path + WorkPool + Mission-7.1.8 tool-safety layer = PARTIAL;
`brain/orchestrator.py` = LEGACY; `services/internet.py` and `services/knowledge.py` = PLACEHOLDER.

**Model/provider posture** (source: CURRENT_ARCHITECTURE_STATE §10): local Ollama only; five
hardcoded models (general=qwen3:8b, coding=qwen2.5-coder:7b, reasoning=deepseek-r1:8b,
creative=llama3.1:8b, fast=gemma3:4b). No multi-provider abstraction exists in the application.

**Canonical position** (source: MISSION_CANON, closing): Current Canonical Mission = **Mission 7.3
Completed**. Next Reserved Mission = **Mission 7.4** (reserved namespace only). Repository HEAD is
a fingerprint-refresh commit one ahead of tag `amalgam-core-v1.1-stable` (source: IMPLEMENTATION_HISTORY §3).

**Version drift (open defect):** `config/settings.py` `APP_VERSION = "0.3.0"` while tags reach
`amalgam-core-v1.1-stable`; boot banner reports 0.3.0 (source: CURRENT_ARCHITECTURE_STATE §14.9).

**Authoritative test count:** UNKNOWN. All recorded counts are historical claims, never re-run
(source: RECOVERY_VALIDATION §3.4).

---

## 2. Completed Missions

Only missions with implementation status in MISSION_CANON are listed. Test figures are historical
claims, not live re-runs (source: RECOVERY_VALIDATION §3.4).

### Mission 7.1 - Mission Engine
- **Delivered:** Mission subsystem decomposed into 7.1.0 Mission Core, 7.1.1 Epic Model,
  7.1.2 Mission Graph, 7.1.3 Planner Integration, 7.1.4 Persistence, 7.1.5 Event Bus,
  7.1.6 Scheduler Integration, 7.1.7 AutonomousExecutor Integration, 7.1.8 Tool Integration
  (source: MISSION_CANON; CONVERSATION_INDEX_STEP4 Decision #3).
- **Repository evidence:** commits `d091b37` (7.1.0), `d085a85` (7.1.4), `1452cb0` (7.1.5),
  `89fb555` (7.1.6), `b47b7da` (7.1.7), `57d6a0d` (7.1.8; tag `mission-7.1-complete`), plus a
  re-commit stabilization pass and tag `amalgam-core-v1.0` at 7.1.7 (source: IMPLEMENTATION_HISTORY §1/§2).
- **Status:** Implemented.
- **Preserved conflict:** sub-steps **7.1.1, 7.1.2, 7.1.3 have no dedicated commits** in the repo
  (design narrative lists 9 steps; git log shows 6) — source: RECOVERY_VALIDATION V-5 / D-6.
- **Tests (claim):** 806 passed at 7.1.8.

### Mission 7.2 - ChiefAgent orchestration
- **Delivered:** central coordination via ChiefAgent (task decomposition over WorkPool +
  DependencyResolver) (source: MISSION_CANON; CONVERSATION_INDEX_STEP4 Decision #4c).
- **Repository evidence:** no standalone commit; bundled in `59be106` "finalize Mission 7.2 and
  Mission 7.3 orchestration" (source: IMPLEMENTATION_HISTORY §1; RECOVERY_VALIDATION V-6 / D-8).
- **Status:** Implemented (bundled).
- **Preserved conflict:** design treats 7.2 as a discrete unit; repository bundles it with 7.3.

### Mission 7.3 - FleetManager / agent lifecycle
- **Delivered:** integration of ChiefAgent with FleetManager (agent lifecycle: unregister,
  increment_failures, clear_failures) for distributed mission execution (source: MISSION_CANON;
  CONVERSATION_INDEX_STEP4 Decision #5b).
- **Repository evidence:** commit `c8f2ece` "Mission 7.3 complete: integrate ChiefAgent with
  FleetManager", finalized in `59be106`; audit artifacts under `9dd9f13` (tag
  `amalgam-core-v1.1-stable`) (source: IMPLEMENTATION_HISTORY §1/§2).
- **Status:** Implemented.
- **Tests (claim):** 910 passed (bundled 7.2 + 7.3; no 7.2-only figure — source: RECOVERY_VALIDATION §3.2).
- **Note:** the distributed execution path is documented as PARTIAL — no in-application worker
  loop drives `WorkPool.steal_task` (source: CURRENT_ARCHITECTURE_STATE §6/§14.2).

---

## 3. Historical Roadmap vs Actual Implementation

Conflicting versions are preserved, not reconciled (source: RECOVERY_VALIDATION §2C;
CONVERSATION_INDEX_STEP4 Decisions #2, #4a/b/c, #5a/b, #6a/b/c).

**Mission 7 identity across schemes** (source: RECOVERY_VALIDATION §2C table): "Browser &
Knowledge" (A) / "Plugin System" (B) / "Git Intelligence" (C) / "Tool System" (D) / "Runtime
Foundation" (E) / **"Mission Engine" (built)**.

**Proposed 7.1-7.3 labels vs implemented labels** (source: CONVERSATION_INDEX_STEP4; the proposed
scheme is isolated, not merged):

| Number | Proposed label (roadmap) | Early deliverable label | Implemented (built) |
|--------|--------------------------|-------------------------|---------------------|
| 7.1 | Autonomous Runtime Foundation | — | Mission Engine (7.1.0-7.1.8) |
| 7.2 | Mission Engine v2 | "Epic Model" (absorbed into 7.1.1) | ChiefAgent orchestration |
| 7.3 | Planning Engine v2 | "Mission Graph"/"Planner Integration" (early numbering) | FleetManager / agent lifecycle |
| 7.4 | Event Bus | "Persistence" (absorbed into 7.1.4) | UNKNOWN (never specified) |
| 7.5 | Model Router | — | Not implemented |
| 7.6 | Workspace Intelligence | — | Not implemented |
| 7.7 | Fleet Intelligence | — | Not implemented |
| 7.8 | Production AI OS | — | Not implemented |

**Direction of divergence** (source: RECOVERY_VALIDATION §4 note): the design history is richer
than the implementation history (more missions, finer sub-numbers, a claimed `v0.3.0-alpha` tag
that does not exist); the repository is narrower (squashed early history, bundled/duplicated late
commits) but contradicts no hard repository fact.

**Other preserved roadmap conflicts** (source: RECOVERY_VALIDATION §2A/§2B): v0.6.0 attributed to
"Mission 6" vs "Mission 6.4" (V-1); "Mission 6 FROZEN" vs 6.5/6.6 continuing (V-2); Mission 6.4/6.5
plan-vs-build renumbering (V-3); "we don't change the roadmap" rule broken the same night (S-5).
These remain open by design.

---

## 4. Current Architecture Gaps

Recorded from code as-is; not proposed for fixing here (source: CURRENT_ARCHITECTURE_STATE §14,
corroborated by RECOVERY_VALIDATION §4).

1. **Entry-point disconnect:** `main.py` runs only the single-task path; ChiefAgent /
   OrchestratorAgent / MissionExecutor are reachable only by direct instantiation (§14.1).
2. **No in-application WorkPool worker loop:** distributed mission execution depends on
   external/test workers calling `steal_task`; otherwise relies on a 300s timeout (§14.2).
3. **Duplicated/overlapping routing & planning:** `Router`, `CapabilityRouter`, `ModelSelector`,
   `KnowledgeRouter` all route; planning is duplicated across `Planner.create_task`,
   `PlannerAgent._generate_plan`, and `AutonomousExecutor._generate_plan` (§14.3).
4. **Mission-7.1.8 tool-safety layer not on the live path:** `ToolWrapper` (timeout/retry) and
   `CapabilityValidator` exist but the kernel `Dispatcher` calls tools directly (§14.4).
5. **`brain/orchestrator.py` is LEGACY** and duplicates memory/LLM handling now owned by the
   Brain/Dispatcher path (§14.5).
6. **Latent bug:** `ResearchAgent._research_files` calls `FileTool.list_files`, which does not
   exist (`FileTool` has `list_dir`); the call is swallowed as an error dict (§14.6).
7. **Unused primitives:** `Preprocessor`/`Pipeline` are implemented but not invoked by
   `Brain.think` (§14.7).
8. **Placeholder services:** `services/internet.py` and `services/knowledge.py` are empty stubs
   (§14.8).
9. **Version drift:** `APP_VERSION = "0.3.0"` vs tags reaching `amalgam-core-v1.1-stable` (§14.9).
10. **No `EngineRegistry`:** engines are reached via the `project` Service, not a dedicated
    registry; the Tool/Service/Engine taxonomy is only partially realized (§14.10; RECOVERY_VALIDATION S-6/D-12).
11. **Security surface:** `PythonExecutor` uses `exec`; `Calculator` evaluates expressions;
    FileTool has no workspace-boundary enforcement in the code read; guarding exists only in
    `ReviewerAgent` (agent path), not the kernel path (§14.11).
12. **"Reasoning" pillar has no dedicated component;** reasoning is implicit in `Planner`,
    `ReflectionEngine`, and heuristics (§14.12).
13. **Dev-loop vs app divergence:** `.amalgam-core` (STATE/HISTORY/loop/provider/recovery) is a
    parallel system not wired into the application runtime; `STATE.json` is stale (reports M7.2
    in_progress, tests 806, provider openai/gpt-4o) (§14.13; §13 limitations).
14. **Unexamined kernel files:** `kernel/scheduler.py`, `kernel/event_bus.py`,
    `kernel/permissions.py` exist but are not on the live dispatch path and were not examined in
    depth (§14.14). Their contents/behavior: **UNKNOWN**.

---

## 5. Mission 7 Remaining Namespace

These identifiers are RESERVED only (source: ROADMAP_CANON). No implementation is defined here.
Historical references are recorded to preserve evolution; they do NOT constitute a plan.

### Mission 7.4
- **Historical references:** three non-reconciled meanings — "Persistence" (early 7.1.x deliverable
  numbering, absorbed into 7.1.4); "Event Bus" (proposed roadmap; Event Bus was actually built as
  7.1.5); "undefined/unspecified" (final state) (source: CONVERSATION_INDEX_STEP4 Decisions #6a/#6b/#6c).
- **Current status:** RESERVED; **no written specification exists** — the identifier carries no
  objective (source: ROADMAP_CANON; CURRENT_ARCHITECTURE_STATE §14 / RECOVERY_VALIDATION 1.7:
  a `mission-7.4` branch exists but contains no 7.4 code).
- **Known dependencies:** Mission 7.3 (completed) precedes it by numbering; repository
  stabilization was repeatedly requested before starting 7.4 (source: CONVERSATION_INDEX_STEP4 #6c).
- **Unknowns:** objective, scope, deliverables, architecture, tests, acceptance criteria — all **UNKNOWN**.

### Mission 7.5
- **Historical references:** "Model Router" / "Model Intelligence Layer"; proposed as a first-class
  subsystem, variously slotted as a Mission 7 component and as Mission 7.5 (source:
  CONVERSATION_INDEX_STEP4 Decision #7; ROADMAP_CANON).
- **Current status:** RESERVED; proposed only, not implemented.
- **Known dependencies:** UNKNOWN (cluster evidence suggests it would follow Mission 7 completion;
  not established as a hard dependency).
- **Unknowns:** whether it will be adopted, its scope, deliverables, and acceptance criteria — **UNKNOWN**.

### Mission 7.6
- **Historical references:** "Workspace Intelligence" — appears once as a proposed roadmap item,
  no elaboration (source: CONVERSATION_INDEX_STEP4 Decision #8; ROADMAP_CANON).
- **Current status:** RESERVED; proposed only, not implemented.
- **Known dependencies:** UNKNOWN.
- **Unknowns:** objective, scope, deliverables, acceptance criteria — **UNKNOWN**.

### Mission 7.7
- **Historical references:** "Fleet Intelligence" — appears once as a proposed roadmap item,
  no elaboration (source: CONVERSATION_INDEX_STEP4 Decision #9; ROADMAP_CANON).
- **Current status:** RESERVED; proposed only, not implemented.
- **Known dependencies:** UNKNOWN.
- **Unknowns:** objective, scope, deliverables, acceptance criteria — **UNKNOWN**.

### Mission 7.8
- **Historical references:** "Production AI OS" — appears once as the proposed roadmap's endpoint,
  no elaboration (source: CONVERSATION_INDEX_STEP4 Decision #10; ROADMAP_CANON).
- **Current status:** RESERVED; proposed only, not implemented.
- **Known dependencies:** UNKNOWN.
- **Unknowns:** objective, scope, deliverables, acceptance criteria — **UNKNOWN**.

---

## 6. Mission 8 Reserved Direction

- **Historical references:** multiple non-reconciled identities — "Dependency Injection",
  "Browser", "SQLite" — consistently framed as the "serious autonomy" milestone (~75-80%
  autonomous engineer; the point AMALGAM becomes the primary dev system) (source:
  CONVERSATION_INDEX_STEP4 Decision #11; ROADMAP_CANON).
- **Current status:** RESERVED; no settled objective or specification.
- **Known dependencies:** Mission 7 (complete) precedes it by numbering (source:
  CONVERSATION_INDEX_STEP4 #11). Nothing further established.
- **Unknowns:** which identity (if any) applies, scope, deliverables, acceptance criteria — **UNKNOWN**.

---

## 7. Mission 9 Reserved Direction

- **Historical references:** non-reconciled identities — "API & Remote Execution" vs "Vision" —
  consistently framed as a "smarter / parallel" milestone (~90% autonomous) (source:
  CONVERSATION_INDEX_STEP4 Decision #12; ROADMAP_CANON).
- **Current status:** RESERVED; no settled objective or specification.
- **Known dependencies:** Mission 8 by ordinal sequence only; not otherwise established.
- **Unknowns:** which identity (if any) applies, scope, deliverables, acceptance criteria — **UNKNOWN**.

---

## 8. Mission 10 Reserved Direction

- **Historical references:** the v1.0 / "OS" endpoint (~95%+ autonomous), variously tagged
  "Voice" or "model-agnostic backend"; explicitly noted "not my target" in one occurrence
  (source: CONVERSATION_INDEX_STEP4 Decision #13; ROADMAP_CANON).
- **Current status:** RESERVED; brainstorming-level; no settled objective or specification.
- **Known dependencies:** Mission 9 by ordinal sequence only; not otherwise established.
- **Unknowns:** which identity (if any) applies, scope, deliverables, acceptance criteria — **UNKNOWN**.

---

## 9. Architecture Decision Process

Binding process for turning any reserved identifier into work (source: PROJECT_CONSTITUTION §3, §4, §8, §9).

- **Ownership:** architectural and roadmap authority rests with the project owner. Frozen
  architectural decisions and public boundaries change only by explicit owner decision (§8).
- **The Golden Rule of placement:** every new module must answer whether it is a **Tool**
  (performs actions), a **Service** (provides infrastructure/external communication), or an
  **Engine** (analyzes/understands). If unclear, the design is not finished (§3).
- **Permanent architecture laws that constrain any decision (§3):** Brain thinks / Kernel
  executes; dependency direction is downward only; the Dispatcher holds no business logic;
  extension happens at the registry, not the Dispatcher; tools are isolated; engines are
  read-only and deterministic; missions own metadata not execution; no agent calls another agent
  directly.
- **How a decision is made (§8):** evaluate against the permanent principles and the durable
  scale question; place it correctly under the Golden Rule; accept only after it is implemented,
  tested, and audited against the architecture; then freeze it.
- **Roadmap changes (§8):** occur only by explicit owner decision; prior roadmap versions are
  preserved in full, never overwritten. New missions enter only with a specification (objective,
  scope, deliverables, acceptance criteria) that fits the existing architecture and carries a
  single objective. Undefined missions are not started.
- **Amendment (§9):** amendments expand and must not silently contradict permanent principles;
  changes to frozen architecture, dependency direction, layer ownership, public boundaries, or
  the roadmap require explicit owner approval; additive capabilities that fit the architecture
  and follow the Golden Rule do not.

---

## 10. Definition of Done for Future Missions

A mission is complete ONLY when all of the following hold (source: PROJECT_CONSTITUTION §4;
pattern corroborated by MISSION_CANON completion evidence):

1. **Specification first.** A specification (objective, scope, deliverables, acceptance criteria)
   existed before implementation; a table of contents is not a specification; undefined work is
   not started.
2. **One objective.** The mission delivered its single declared objective with no scope creep.
3. **Deliverables implemented** to production quality (no placeholders, no dead code).
4. **Tests pass** and existing tests still pass with no regressions; test results are treated as
   claims until reproduced from the repository.
5. **Architecture preserved.** Layer boundaries, dependency direction, and public APIs intact;
   the Golden Rule satisfied.
6. **Audited against the architecture** before acceptance; reported results (including test
   counts) verified against the repository, not accepted at face value.
7. **Documentation synchronized** with the code in the same effort (version strings, architecture
   docs, status records must not drift).
8. **Frozen before advancing.** The working state is frozen (committed/tagged) before the next
   mission begins; completed work is not reopened casually.
9. **Stop when done.** When the mission meets this definition, work stops; the next mission is not
   begun and undefined future work is not started speculatively.

---

*This plan synthesizes only the seven authorized sources. It invents no missions, defines no
Mission 7.4+ implementation, and marks every unestablished fact as UNKNOWN. Conflicts are
preserved per the RECOVERY_VALIDATION register and PROJECT_CONSTITUTION governance.*
