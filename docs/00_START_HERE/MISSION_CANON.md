# MISSION_CANON.md

**The Authoritative Registry of AMALGAM Mission Execution**

Status: Canonical
Nature: Registry of executed missions (not a roadmap, not a narrative history)

---

## Preamble

This document is the canonical registry of every mission AMALGAM has actually executed. It
records what was built, not what was planned. It is not a roadmap and not a design narrative.

**Sources (priority order).** Compiled only from the recovered documents, highest priority
first: IMPLEMENTATION_HISTORY.md (repository evidence), CURRENT_ARCHITECTURE_STATE.md,
MISSION_HISTORY.md, RECOVERY_VALIDATION.md, PROJECT_CONSTITUTION.md. The repository was not
inspected directly and the original conversation was not reread.

**Evidence tiers.** Repository-commit-backed evidence is treated as strongest. Where a mission
is documented in the recovered design history but has no surviving dedicated commit (the
pre-release missions), that absence is stated plainly in its entry; it is not treated as
disproof, and it is not filled in with invented commits.

**Conflicts.** Where the evidence conflicts, the conflict is preserved in the Notes field of
the affected mission and is not resolved.

**Entry template.** Every canonical mission below records exactly these fields, in order:
Mission ID, Status, Objective, Repository Evidence, Primary Commits, Major Components
Introduced, Architecture Impact, Tests, Dependencies, Artifacts, Completion Evidence, Notes.

---

## Genesis Foundation (pre-mission)

Genesis work predates the numbered mission sequence and is recorded here only as
repository-backed context. It is **not** a numbered mission and is not counted in the canon.

- **Repository-backed Genesis commits:** `71f74aa` Genesis-1 (core architecture and persistent
  memory), `85216fe` Genesis-1.1 (.gitignore + cache cleanup), `deb8b04` Genesis-2 (connect
  AMALGAM to Ollama), `96210c8` Genesis-8.1 (introduce BaseTool architecture); `ab22942`
  (cleanup of temporary test scripts).
- **Divergence (preserved):** Genesis-3, Genesis-4, Genesis-5, Genesis-6, and Genesis-7 are
  described in the design history but have **no surviving dedicated commits** in the recovered
  repository evidence.

---

## Canonical Missions

### Mission 1 — Foundation Stabilization

- **Mission ID:** Mission 1
- **Status:** Completed (design-history evidence; no dedicated repository commit)
- **Objective:** Make the existing architecture consistent and reliable without adding new
  features (dependency metadata, package initialization, a working test suite, better memory
  handling, a robust dispatcher, clearer kernel boot information, a stable CLI).
- **Repository Evidence:** No dedicated commit. Per IMPLEMENTATION_HISTORY, the earliest
  surviving feature commit is `c2bd9dc` (v0.6.0); all pre-release work was squashed or
  absorbed before it. The stabilized dispatcher, memory handling, and CLI persist in the
  current tree.
- **Primary Commits:** None dedicated (absorbed before `c2bd9dc`).
- **Major Components Introduced:** Dispatcher guardrails (unknown action / missing tool /
  missing method / malformed task / service failure), project-relative memory path with
  directory auto-creation, dynamic kernel boot counts, CLI exception boundary, Ollama-failure
  handling in the LLM path.
- **Architecture Impact:** Hardened the kernel dispatch and memory foundations reused by every
  later mission. Explicitly did not redesign architecture.
- **Tests:** 46 passed (historical claim, not a live re-run).
- **Dependencies:** Genesis foundation.
- **Artifacts:** `requirements.txt` / `pyproject.toml` metadata; package `__init__.py` files
  (referenced in the recovered record).
- **Completion Evidence:** Recorded complete with "46 passed" and a design-history grade of
  9.6/10.
- **Notes:** The design history states Mission 1 was tagged `v0.3.0-alpha`, but **that tag
  does not exist in the repository** (divergence preserved, not reconciled).

### Mission 2 — Core Infrastructure (Logging & Configuration)

- **Mission ID:** Mission 2
- **Status:** Completed (design-history evidence; no dedicated repository commit)
- **Objective:** Deliver the last infrastructure layer before capability work — central
  configuration, structured logging, diagnostics, and a version system.
- **Repository Evidence:** No dedicated commit. Configuration, logging, diagnostics, and
  version modules are present in the current tree per CURRENT_ARCHITECTURE_STATE.
- **Primary Commits:** None dedicated (absorbed before `c2bd9dc`).
- **Major Components Introduced:** Central configuration (`config/`), structured logging
  service, diagnostics service, version system.
- **Architecture Impact:** Established the single-source configuration and structured-logging
  foundations later relied upon across the system.
- **Tests:** 53 passed (historical claim, not a live re-run).
- **Dependencies:** Mission 1.
- **Artifacts:** None recorded beyond the modules above.
- **Completion Evidence:** Recorded "officially complete" with 53 passing tests and
  "Architecture preserved."
- **Notes:** The recovered record states the Constitution (ten principles) and the project
  slogan were authored during this mission; recorded as context, not as deliverables.

### Mission 3 — Workspace Engine ("Project Atlas")

- **Mission ID:** Mission 3
- **Status:** Completed (design-history evidence; no dedicated repository commit)
- **Objective:** Teach AMALGAM to understand its own project before changing it — a read-only,
  deterministic project-analysis engine answering "Tell me about this project" with no LLM.
- **Repository Evidence:** No dedicated commit. The `workspace/` package is present in the
  current tree per CURRENT_ARCHITECTURE_STATE.
- **Primary Commits:** None dedicated (absorbed before `c2bd9dc`).
- **Major Components Introduced:** `workspace/` engine (project scan, dependency, tree, git,
  and summary analysis), read-only and deterministic.
- **Architecture Impact:** Introduced the Workspace pillar of the "Four Pillars" and the rule
  that analysis engines are read-only, deterministic, and independent of any language model.
- **Tests:** 64 passed (historical claim, not a live re-run).
- **Dependencies:** Mission 2.
- **Artifacts:** None recorded beyond the `workspace/` package.
- **Completion Evidence:** Recorded "APPROVED, Grade 10/10" with "64 passed."
- **Notes:** In an earlier roadmap this slot was labeled "Unified Routing Engine"; it was
  replaced by the Workspace Engine before work began (label divergence preserved).

### Mission 4 — Knowledge Engine ("Project Athena")

- **Mission ID:** Mission 4
- **Status:** Completed (design-history evidence; no dedicated repository commit)
- **Objective:** Build a deterministic project-knowledge engine (symbols, documents,
  relationships, search) that answers questions about the codebase without invoking an LLM;
  explicitly not RAG and with no embeddings or vector database.
- **Repository Evidence:** No dedicated commit. The `knowledge/` package is present in the
  current tree per CURRENT_ARCHITECTURE_STATE.
- **Primary Commits:** None dedicated (absorbed before `c2bd9dc`).
- **Major Components Introduced:** `knowledge/` engine (graph, index, parser, symbols,
  documents, relationships, search, report), deterministic and independent of the Brain.
- **Architecture Impact:** Added the Knowledge pillar; formalized the "Four Pillars"
  (Workspace, Knowledge, Memory, Reasoning) as the frame for later capability work.
- **Tests:** 73 passed (historical claim, not a live re-run).
- **Dependencies:** Mission 3 (Workspace).
- **Artifacts:** None recorded beyond the `knowledge/` package.
- **Completion Evidence:** Recorded complete with "73 passed."
- **Notes:** In an earlier roadmap this slot was labeled "Plugin Loader"; it was replaced by
  the Knowledge Engine (label divergence preserved). A single failing symbol-search test was
  recorded as fixed by hand during completion.

### Mission 5 — Integration

- **Mission ID:** Mission 5 (delivered as 5.1 and 5.2; 5.3 abandoned)
- **Status:** Partially completed — 5.1 and 5.2 completed; 5.3 abandoned
- **Objective:** Integrate the Workspace and Knowledge engines into the brain and dispatch
  path so the system can act on project understanding (intent/planner integration; a combined
  project service).
- **Repository Evidence:** No dedicated commit. `services/project_service.py` (combining
  Workspace and Knowledge) is present in the current tree per CURRENT_ARCHITECTURE_STATE.
- **Primary Commits:** None dedicated (absorbed before `c2bd9dc`).
- **Major Components Introduced:** Extended intent detection and planning for the new
  capabilities (5.1); `ProjectService` combining Workspace + Knowledge, with the dispatcher
  upgraded to route to Tools or Services (5.2).
- **Architecture Impact:** First end-to-end multi-engine feature; established the Tool-or-
  Service dispatch routing. During this mission the Tool/Service/Engine "Golden Rule" and the
  frozen architecture baseline were declared.
- **Tests:** 73 passed (5.1); 74 passed (5.2) — historical claims, not a live re-run.
- **Dependencies:** Mission 3 (Workspace) and Mission 4 (Knowledge).
- **Artifacts:** None recorded beyond `services/project_service.py`.
- **Completion Evidence:** Mission 5.2 recorded complete, with a first end-to-end project
  summary demonstration.
- **Notes:** Sub-mission 5.3 ("Code Navigation") was started but never completed (see the
  Non-Canonical section). This mission was redesigned repeatedly in the design history
  (an earlier "Dependency Injection" label, a proposed then cancelled Capability Router);
  those churned proposals were not built and are preserved as design history, not canon.

### Mission 6.0 — Engineer Core (FileTool extension)

- **Mission ID:** Mission 6.0
- **Status:** Completed (design-history evidence; no dedicated repository commit)
- **Objective:** Extend the file tool with the engineering file operations needed for
  autonomous code work.
- **Repository Evidence:** No dedicated commit. The extended file-tool operations persist in
  the current tree per CURRENT_ARCHITECTURE_STATE; helper scripts `mission6_01.py`,
  `mission6_02.py`, `mission6_03.py` exist in the tree.
- **Primary Commits:** None dedicated (absorbed before `c2bd9dc`).
- **Major Components Introduced:** File tool extensions (existence check, backup, append,
  delete, copy, move, in-place text replacement).
- **Architecture Impact:** Provided the file-manipulation substrate for the autonomous
  engineering capabilities that followed.
- **Tests:** Not separately recorded.
- **Dependencies:** Genesis file tool.
- **Artifacts:** `mission6_01.py`, `mission6_02.py`, `mission6_03.py`.
- **Completion Evidence:** Recorded delivered as a patch to the file tool.
- **Notes:** The Mission 6 sub-roadmap named discrete units 6.1/6.2/6.3 (EngineerAgent /
  CommandTool / automatic verification), but the recovered record does not confirm these were
  built as discrete numbered units; the implemented arc jumped to 6.4. Gap preserved, not
  invented.

### Mission 6.4 — Autonomous Agent Core

- **Mission ID:** Mission 6.4
- **Status:** Completed (repository-commit-backed; released as v0.6.0)
- **Objective:** Give AMALGAM an autonomous goal-execution loop able to plan, execute,
  evaluate, reflect, retry, and record its own work.
- **Repository Evidence:** Commit `c2bd9dc` "Release v0.6.0: Autonomous Agent Framework"
  (tags `v0.6.0` and `v0.6.5`; branch `mission-6-stable`). The autonomous-loop packages are
  present in the current tree per CURRENT_ARCHITECTURE_STATE.
- **Primary Commits:** `c2bd9dc` (tags `v0.6.0`, `v0.6.5`).
- **Major Components Introduced:** Goal state machine, task queue, evaluator, reflection
  engine, retry manager, execution memory, and the autonomous executor that drives them.
- **Architecture Impact:** Introduced the autonomous goal lifecycle and the deterministic
  reflect/retry recovery model that later missions build on.
- **Tests:** Conflicting reports — 74 passed (Codex) versus 176 passed (Kimi).
- **Dependencies:** Mission 6.0 (Engineer Core).
- **Artifacts:** `MISSION_6.4.3_SECURITY_AUDIT.md`; `benchmark.py`.
- **Completion Evidence:** Recorded "Mission 6 status frozen" at "AMALGAM v0.6.0 — Autonomous
  Agent Framework."
- **Notes:** Test-count conflict (74 vs 176) is unresolved and preserved. Tags `v0.6.0` and
  `v0.6.5` point at the **same** commit `c2bd9dc`. The design plan had labeled 6.4 as a
  "retry & self-debug loop"; the built 6.4 is the "Autonomous Agent Core" (label divergence
  preserved). A "Mission 6 frozen at v0.6.0" statement coexists with later 6.5/6.6 work — a
  timeline tension preserved, not reconciled.

### Mission 6.5 — Multi-Agent Orchestration

- **Mission ID:** Mission 6.5
- **Status:** Completed (design-history evidence; no dedicated repository commit)
- **Objective:** Evolve the single autonomous agent into a coordinated multi-agent system.
- **Repository Evidence:** No dedicated commit (work sits between `c2bd9dc` v0.6.0 and
  `410b67f` v0.6.6). The agent classes and coordination primitives are present in the current
  tree per CURRENT_ARCHITECTURE_STATE; `benchmark_652.py` exists in the tree.
- **Primary Commits:** None dedicated (absorbed between `c2bd9dc` and `410b67f`).
- **Major Components Introduced:** Base agent lifecycle, orchestrator agent, the planner /
  research / reviewer / engineer agents, agent registry, agent context, agent messaging, and
  the shared execution context.
- **Architecture Impact:** Established the multi-agent runtime and the permanent rule that no
  agent calls another agent directly — all coordination is via shared context and structured
  messages, and agents return structured results.
- **Tests:** 232 passed (historical claim, not a live re-run).
- **Dependencies:** Mission 6.4.
- **Artifacts:** `benchmark_652.py` (optimization-phase benchmark).
- **Completion Evidence:** Recorded complete with "232 tests."
- **Notes:** No dedicated commit survives for this mission; evidence is the present-tree agent
  code plus the benchmark artifact.

### Mission 6.6 — Fleet / Dynamic Scheduling

- **Mission ID:** Mission 6.6
- **Status:** Completed (repository-commit-backed; released as v0.6.6)
- **Objective:** Add fleet management and dynamic scheduling over the multi-agent runtime.
- **Repository Evidence:** Commit `410b67f` "Mission 6.6 complete - awaiting final audit"
  (tag `v0.6.6`). The scheduler, fleet manager, work pool, dependency resolver, and routers
  are present in the current tree per CURRENT_ARCHITECTURE_STATE.
- **Primary Commits:** `410b67f` (tag `v0.6.6`).
- **Major Components Introduced:** Dynamic scheduler, fleet manager, health monitoring, work
  pool (work-stealing), dependency resolver (topological), knowledge router, capability
  router, and dependency-graph execution with sequential fallback.
- **Architecture Impact:** Introduced the fleet/scheduling layer that central coordination
  later drives.
- **Tests:** 247 passed (recorded as `247 passed in 368.45s`; historical claim, not a live
  re-run).
- **Dependencies:** Mission 6.5.
- **Artifacts:** `benchmark_662.py` (optimization-phase benchmark).
- **Completion Evidence:** Recorded complete; the commit itself notes it awaited a final audit,
  and the recovered record states 247 tests were confirmed after audit.
- **Notes:** The design history records that an initial completion report misstated file paths
  and test counts and was audited before acceptance — an example of the audit-before-accept
  rule. The distributed work-pool path is documented in CURRENT_ARCHITECTURE_STATE as not
  driven by an in-application worker loop.

### Mission 7.1 — Mission Engine (7.1.0 through 7.1.8)

- **Mission ID:** Mission 7.1 (sub-steps 7.1.0–7.1.8)
- **Status:** Completed (repository-commit-backed)
- **Objective:** Build the Mission Engine — mission metadata and lifecycle, a mission
  dependency graph, persistence, an event bus, and executor/scheduler/tool integration.
- **Repository Evidence:** Multiple commits (below); the `brain/mission/` package is present
  in the current tree per CURRENT_ARCHITECTURE_STATE.
- **Primary Commits:** `d091b37` (Mission Core / 7.1.0), `d085a85` (7.1.4 foundation + docs),
  `1452cb0` (7.1.5 event bus), `89fb555` (7.1.6 planner integration), `ed28829` (7.1 cleanup),
  `b47b7da` (7.1.7 autonomous-executor integration), `57d6a0d` (7.1.8 tool integration; tag
  `mission-7.1-complete`); re-commit pass `2bcd3ad` (7.1.5), `419230f` (7.1.6), `c305e5d`
  (7.1.7; tag `amalgam-core-v1.0`), `9443634` (7.1.8); plus `443c952` and `3c44d71`
  (AMALGAM Core v1.0 infrastructure).
- **Major Components Introduced:** Mission dataclass and state machine, epic grouping, mission
  graph (cycle detection, topological sort), mission persistence, mission event bus, and the
  mission executor bridging the graph to the autonomous executor.
- **Architecture Impact:** Added the Mission subsystem as metadata-and-orchestration only —
  missions hold identity, status, and dependencies and never execute work themselves.
- **Tests:** 772 passed at 7.1.7 (`138.51s`); 806 passed at 7.1.8 (`149.05s`) — historical
  claims, not a live re-run.
- **Dependencies:** Mission 6.4 (autonomous executor), Mission 6.5 (agents), Mission 6.6
  (scheduler/fleet).
- **Artifacts:** `docs/missions/` mission specification files (several empty per the recovered
  index); `.amalgam-core/` engineering-loop directory.
- **Completion Evidence:** Tag `mission-7.1-complete` on `57d6a0d`; tag `amalgam-core-v1.0` on
  `c305e5d`.
- **Notes:** Sub-steps 7.1.1, 7.1.2, and 7.1.3 (Epic / Graph / Planner Integration) appear in
  the design narrative but have **no dedicated commits**. Sub-steps 7.1.5–7.1.8 were committed
  **twice** (a stabilization re-commit pass). "AMALGAM Core v1.0" was **double-committed**
  (`443c952` and `3c44d71`). All preserved, not reconciled.

### Mission 7.2 — ChiefAgent Orchestration

- **Mission ID:** Mission 7.2
- **Status:** Completed (repository-commit-backed; bundled with 7.3)
- **Objective:** Establish central coordination — a chief agent that decomposes and
  orchestrates task execution across the fleet.
- **Repository Evidence:** Commit `59be106` "feat(chief): finalize Mission 7.2 and Mission 7.3
  orchestration." The chief-agent implementation is present in the current tree per
  CURRENT_ARCHITECTURE_STATE.
- **Primary Commits:** `59be106` (shared with Mission 7.3).
- **Major Components Introduced:** Central coordinating agent (ChiefAgent) with task
  decomposition over the work pool and dependency resolver.
- **Architecture Impact:** Established central orchestration that composes planning,
  scheduling, and dependency resolution without bypassing the dispatch path.
- **Tests:** Reported within the combined 910-passed figure for 7.2/7.3 (historical claim,
  not a live re-run).
- **Dependencies:** Mission 7.1.
- **Artifacts:** None recorded beyond the chief-agent implementation.
- **Completion Evidence:** Finalized in commit `59be106`.
- **Notes:** There is **no standalone Mission 7.2 commit**; it is bundled with Mission 7.3 in
  `59be106`, although the design history treats 7.2 as a discrete unit. Preserved, not
  reconciled.

### Mission 7.3 — ChiefAgent + FleetManager Integration

- **Mission ID:** Mission 7.3
- **Status:** Completed (repository-commit-backed)
- **Objective:** Integrate central coordination with fleet management for distributed mission
  execution.
- **Repository Evidence:** Commit `c8f2ece` "Mission 7.3 complete: integrate ChiefAgent with
  FleetManager," finalized in `59be106`. Related audit/stabilization commit `9dd9f13`
  (tag `amalgam-core-v1.1-stable`); current HEAD `102ba30` is a fingerprint refresh one commit
  ahead of that tag.
- **Primary Commits:** `c8f2ece`, `59be106`.
- **Major Components Introduced:** Integration of the chief agent with the fleet manager;
  distributed mission execution paths (sequential and work-pool-based).
- **Architecture Impact:** Completed the central-coordination-over-fleet model. The
  distributed path is documented in CURRENT_ARCHITECTURE_STATE as functional but not driven by
  an in-application worker loop.
- **Tests:** 910 passed (historical claim, not a live re-run).
- **Dependencies:** Mission 7.2; Mission 6.6 (fleet manager).
- **Artifacts:** Architecture-audit artifacts added under `9dd9f13`.
- **Completion Evidence:** Commit `c8f2ece` and finalization in `59be106`; stabilization tag
  `amalgam-core-v1.1-stable`.
- **Notes:** The recovered record describes the final hours as a repository-stabilization pass
  preceding any Mission 7.4 work. The 910 figure is a historical report, not a live re-run.

---

## Hotfixes (repository-backed, not numbered missions)

### HF-001 — Paused Goal State and Resume Handling

- **Mission ID:** HF-001 (hotfix, not a numbered mission)
- **Status:** Completed (repository-commit-backed; released as v0.6.6.1)
- **Objective:** Add a paused goal state and resume handling to the autonomous goal lifecycle.
- **Repository Evidence:** Commit `469e7b1` "HF-001: Add paused goal state and resume handling"
  (tag `v0.6.6.1`).
- **Primary Commits:** `469e7b1` (tag `v0.6.6.1`).
- **Major Components Introduced:** Paused state in the goal lifecycle plus resume handling.
- **Architecture Impact:** Extended the goal state machine with pause/resume semantics.
- **Tests:** Not separately recorded.
- **Dependencies:** Mission 6.4 (goal lifecycle).
- **Artifacts:** None recorded.
- **Completion Evidence:** Tag `v0.6.6.1` on `469e7b1`.
- **Notes:** The design history mentions HF-002, HF-003 (cancelled) and HF-004 (deferred);
  only HF-001 has repository evidence, so only HF-001 is recorded here.

---

## Non-Canonical: Abandoned Work and Historical Proposals

This section exists to keep implemented missions strictly separate from work that was never
completed. Nothing here is part of the canon, and nothing here is a roadmap.

- **Mission 5.3 — Code Navigation (abandoned).** Started but never completed; no completion
  evidence and no test result exist in the recovered record. It is not counted as a completed
  mission.
- **Historical proposals (not implemented).** Numerous capabilities were proposed across the
  project's design history but never built. They are catalogued as design history in the
  recovery documents (see FUTURE_PROPOSALS.md and ROADMAP_EVOLUTION.md) and are deliberately
  excluded from this registry. They confer no reservation and imply no plan.
- **Mission 7.4 (undefined).** A branch named `mission-7.4` exists in the repository evidence,
  but it points at earlier (7.1.6 / 7.3) commits and contains **no Mission 7.4 code**, and no
  specification for Mission 7.4 exists in the recovered record.

---

Current Canonical Mission:

Mission 7.3 Completed

Next Reserved Mission:

Mission 7.4
