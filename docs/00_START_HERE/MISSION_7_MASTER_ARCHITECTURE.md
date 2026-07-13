# MISSION 7 MASTER ARCHITECTURE (AS-BUILT)

**Status:** FROZEN (as-built, written at Mission 7.7 closure)
**Scope:** Missions 7.1 - 7.6 as actually implemented
**Governance note:** The Project Constitution required this document to be
written and frozen *before* Mission 7 implementation. That did not happen;
implementation ran ahead of specification. This as-built edition is the
retroactive cure for that constitutional violation. It documents what exists
at tag `v0.7.6`, verified by a 925-test suite. Divergences from the original
Mission 7 vision are recorded in Section 9, not hidden.

---

## 1. Mission 7 Objective (Original)

Transform AMALGAM from a reactive assistant into an autonomous engineering
organization: take a large objective, decompose it into missions, assign
work to specialized agents, execute autonomously, detect failures, recover,
review its own work, and produce production-ready output.

## 2. Layered Architecture (As-Built)

    +--------------------------------------------------------------+
    |  CLI (main.py)                                               |
    |    - interactive REPL (reactive path)                        |
    |    - --mission GOAL (orchestration path)   [Mission 7.5]     |
    +--------------------------------------------------------------+
    |  Orchestration (brain/)                                      |
    |    ChiefAgent -> DependencyResolver -> WorkPool              |
    |    FleetManager, Messaging, SharedContext                    |
    |    FleetWorker (steal/execute/report loop) [Mission 7.5]     |
    +--------------------------------------------------------------+
    |  Mission Engine (brain/engine, loop, recovery, context)      |
    |    17-stage loop, checkpoint/recovery, DAG scheduling        |
    +--------------------------------------------------------------+
    |  Autonomous Core (brain/executor)                            |
    |    Goal state machine, TaskQueue, Evaluator,                 |
    |    ReflectionEngine, RetryManager, ExecutionMemory           |
    +--------------------------------------------------------------+
    |  Kernel (kernel/)                                            |
    |    Executor.boot() -> Dispatcher -> ActionRegistry           |
    |    Dispatch routes ALL tool actions through ToolWrapper      |
    |    (CapabilityValidator + PermissionChecker)  [Mission 7.5]  |
    +--------------------------------------------------------------+
    |  Tools (tools/) - hardened            [Mission 7.6]          |
    |    Calculator (AST whitelist), PythonExecutor (subprocess    |
    |    isolation), FileTool (workspace confinement), web, etc.   |
    +--------------------------------------------------------------+
    |  Services (services/)                                        |
    |    LLMService (Ollama), MemoryService, Logger, Diagnostics   |
    +--------------------------------------------------------------+

## 3. Agent Organization

- **ChiefAgent** - mission owner: submits planning work, resolves the
  dependency DAG, schedules ready tasks into the WorkPool, tracks
  completion/failure via Messaging.
- **PlannerAgent** - decomposes a goal into ordered steps (LLM-backed).
- **EngineerAgent / ResearchAgent / ReviewerAgent** - specialized
  executors wrapped over the autonomous core.
- **FleetWorker** - generic in-process worker: steals capability-matched
  tasks, executes a supplied handler, reports complete/fail. The
  production worker loop that Missions 6.6-7.3 lacked.

## 4. Work Distribution

WorkPool implements work-stealing: `submit_task(task, capability)` ->
`steal_task(worker, capabilities)` -> `complete_task` / `fail_task`,
with all transitions announced on Messaging. Dependencies are enforced
by DependencyResolver (topological order; a task is only schedulable
when all `depends_on` predecessors completed).

## 5. Safety and Security Model (Mission 7.5 + 7.6)

1. Every kernel-dispatched tool action passes ToolWrapper:
   capability validation -> permission check -> bounded timeout ->
   bounded retry -> structured ToolResult.
2. Calculator: AST whitelist evaluation only (SEC-001 resolved).
3. PythonExecutor: isolated subprocess, empty env, timeout (SEC-002).
4. FileTool: workspace-root confinement; traversal and absolute
   escapes rejected pre-syscall (SEC-003/004).
5. Dispatcher returns results; presentation is CLI-owned (ARCH-005).

## 6. Model Strategy

Local-first via Ollama. General reasoning: qwen3:8b. Code generation:
qwen2.5-coder:7b. Routing per config/models.py. No cloud dependency.

## 7. State and Recovery

.amalgam-core/STATE.json checkpoints loop phase/stage/mission/goal with
schema validation; RecoveryManager resumes an interrupted loop.
ExecutionMemory preserves a full audit trail of autonomous runs.

## 8. Verification

925 tests passing at closure (910 baseline verified in Mission 7.4 +
15 regression tests added in 7.5/7.6). Baseline is cross-platform
(hardcoded C:\AMALGAM paths removed).

## 9. Divergence Register (Vision vs. As-Built)

| Planned (7.0-7.8 chain) | As-built reality |
|---|---|
| 7.4 Execution Fabric | Superseded: delivered as FleetWorker + wiring (7.5) |
| 7.5 Verification Layer | Partial: Evaluator + ReviewerAgent exist; review is not an enforced gate |
| 7.6 Reasoning Layer | NOT BUILT - planning remains heuristic; deferred to Mission 8 |
| 7.7 Memory Fabric | Partial: SharedContext + ExecutionMemory; no long-term semantic memory |
| 7.8 Production Hardening | Delivered early as security hardening (7.6 as-built) |

The unmet intelligence layer is the defining scope of Mission 8.
