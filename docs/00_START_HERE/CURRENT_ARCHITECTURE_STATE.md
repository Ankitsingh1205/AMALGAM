# CURRENT_ARCHITECTURE_STATE.md

> **Source of truth:** the repository code as read on this pass. This document describes
> ONLY what is implemented today. It does not propose changes or design future work.
> Historical/design documents were ignored except where code confirms them.
>
> **Maturity scale used below:** `STABLE` (implemented, wired into a runtime path, tested) /
> `FUNCTIONAL` (implemented and wired, lighter coverage) / `PARTIAL` (implemented but not
> fully wired into a live path) / `PLACEHOLDER` (stub/empty) / `LEGACY` (present but bypassed).
>
> **Two distinct runtimes exist in the tree and must not be confused:**
> 1. **The AMALGAM application** (`main.py` + kernel/brain/agents/...): the actual program.
> 2. **The `.amalgam-core` engineering loop** (`scripts/` + `.amalgam-core/`): development
>    tooling that tracks mission progress; it is NOT imported or run by the application.

---

## 1. Layer Architecture

**Current implementation.** Two coexisting execution surfaces are wired in code:

- **Primary CLI path (single-task):**
  `main.py` → `Brain.think()` → `kernel.Executor.execute()` → `Dispatcher.dispatch()` →
  Tool **or** Service (via `ActionRegistry`), with an LLM fallback for `chat`/`generate_code`.
- **Multi-agent path (task/mission orchestration):**
  `OrchestratorAgent` / `ChiefAgent` → `Scheduler` (pipeline) or `WorkPool`+`FleetManager`
  (distributed) → agents (`Planner/Research/Reviewer/Engineer`) → `EngineerAgent` →
  `AutonomousExecutor` → back down to the same kernel `Executor`/`Dispatcher`.

The layered stack that actually exists:
```
Interface        main.py (CLI REPL)
Brain            brain/ (intent, planner, routers)   |  Agents  agents/ (multi-agent)
Kernel           kernel/ (executor, dispatcher, action_registry, task, state)
Registries       ActionRegistry, ToolRegistry, ServiceRegistry, AgentRegistry
Tools            tools/          Services  services/          Engines  workspace/, knowledge/
Autonomy         brain/executor, goal, queue, evaluator, reflection, retry, memory
Mission          brain/mission/  Coordination brain/{shared_context,messaging,scheduler,fleet_manager,work_pool,dependency_resolver}
Config           config/ (constants, settings, models)
```

**Responsible modules.** `main.py`, `kernel/*`, `brain/*`, `agents/*`, `tools/*`, `services/*`,
`models/*`, `workspace/*`, `knowledge/*`, `config/*`.

**Dependencies.** Downward only in the primary path: brain→kernel→tools/services→config.
The multi-agent layer depends on brain coordination primitives and the mission subsystem.

**Public APIs.** `Brain.think(user_input) -> Task`; `Executor.boot()`, `Executor.execute(task)`;
`Dispatcher.dispatch(task)`.

**Current maturity.** Primary CLI path: `STABLE`. Multi-agent layering: `FUNCTIONAL` (imports
resolve, orchestrators run) but not driven from `main.py`.

**Known limitations.** `main.py` only exercises the single-task path; the multi-agent/mission
layers are reachable only by direct instantiation (no CLI/entry wiring). `brain/orchestrator.py`
is `LEGACY` (superseded by `agents/orchestrator_agent.py` and the `main.py` flow).

---

## 2. Major Subsystems

**Current implementation.** The codebase is organized into these live subsystems:

| Subsystem | Location | Role today |
|-----------|----------|------------|
| Kernel | `kernel/` | Boot + dispatch of `Task` objects to tools/services |
| Brain | `brain/` (top-level) | Intent detection, planning, routing |
| Multi-Agent | `agents/` + `brain/` coordination | Orchestrated agent pipelines & mission dispatch |
| Autonomous Executor | `brain/executor`, `goal`, `queue`, `evaluator`, `reflection`, `retry`, `memory` | Goal lifecycle loop |
| Mission Engine | `brain/mission/` | Mission metadata, DAG, event bus, executor bridge |
| Tools | `tools/` | Concrete capabilities (calc, python, files, memory, internet) |
| Services | `services/` | LLM, Ollama, Memory, Project, Diagnostics, Logger |
| Engines | `workspace/`, `knowledge/` | Deterministic project analysis (no LLM) |
| Models | `config/models.py`, `models/` | Role→model-name mapping and selection |
| Dev Loop | `scripts/` + `.amalgam-core/` | Mission-tracking tooling (not app runtime) |

**Responsible modules.** As above.

**Dependencies.** Kernel is the shared execution substrate reached by both the CLI path and
(transitively, via `EngineerAgent → AutonomousExecutor → KernelExecutor`) the agent path.

**Public APIs.** Each subsystem exposes a small facade: `Executor`, `Brain`, `ChiefAgent`,
`AutonomousExecutor`, `MissionExecutor`, `ToolRegistry`, `ServiceRegistry`, `Workspace`,
`KnowledgeEngine`.

**Current maturity.** Kernel/Tools/Services/Engines: `STABLE`. Autonomous + Mission +
Multi-Agent: `FUNCTIONAL`. Dev loop: `FUNCTIONAL` (separate from app).

**Known limitations.** Overlapping responsibilities exist (e.g., planning appears in
`brain/planner`, `PlannerAgent`, and `AutonomousExecutor._generate_plan`; routing appears in
`Router`, `CapabilityRouter`, `ModelSelector`, `KnowledgeRouter`). `services/internet.py` and
`services/knowledge.py` are `PLACEHOLDER` classes (the real capability lives in `tools/internet_tool.py`
and `knowledge/`).

---

## 3. Component Ownership

**Current implementation (who owns what, by registry/instantiation):**

- **`ActionRegistry`** (`kernel/action_registry.py`) owns the 7 action→(target,method) routes:
  `calculate→(calculator,calculate)`, `run_python→(python,execute)`,
  `list_files→(files,list_dir)`, `remember→(memory,remember)`, `recall→(memory,recall)`,
  `search_web→(internet,search)`, `project_summary→(project,summarize)`.
- **`ToolRegistry`** owns 5 tool instances: `calculator, python, files, memory, internet`.
- **`ServiceRegistry`** owns 4 service instances: `llm, memory, ollama, project`.
- **`AgentRegistry`** owns agent instances by name (`planner, researcher, reviewer, engineer`,
  and `chief` when registered), populated lazily by orchestrators.
- **`Dispatcher`** owns the three registries and performs routing + result printing.
- **`Executor`** owns `KernelState` + `Dispatcher`.
- **`ChiefAgent`** owns `WorkPool`, `DependencyResolver`, optional `FleetManager`, `Scheduler`.

**Responsible modules.** The four registries listed above.

**Dependencies.** Registries depend only on `config.constants` + the concrete classes they hold.

**Public APIs.** `get(name)`, `list_tools()`/`list_services()`/`list_all()`, `register(...)`.

**Current maturity.** `ActionRegistry`/`ToolRegistry`/`ServiceRegistry`: `STABLE`.
`AgentRegistry`: `FUNCTIONAL`.

**Known limitations.** There is **no `EngineRegistry`** in code; `workspace`/`knowledge`
engines are reached through the `project` **Service** (`ProjectService`), not a dedicated
engine registry. `ActionRegistry` routes are hardcoded (no dynamic registration).

---

## 4. Execution Flow (single-task CLI path)

**Current implementation.** `main.py` runs a REPL loop:
1. Read `user_input`; exit on `exit`/`quit`.
2. `Brain.think(user_input)`: `IntentAnalyzer.detect()` classifies into one of 8 intents
   (`math, memory, files, internet, python, coding, project, general`) using a precompiled
   math regex + keyword frozensets; `Planner.create_task(intent, user_input)` produces a `Task`.
3. `Executor.execute(task)` → `Dispatcher.dispatch(task)`.
4. Dispatcher looks up `ActionRegistry.get(action)`. If a route exists, it resolves the target
   in `ToolRegistry` first, else `ServiceRegistry`, then calls `method(task.data)` (special-casing
   `remember` for a (key,value) tuple), prints an `AMALGAM:` block, and returns the result.
5. If no route but action ∈ {`chat`,`generate_code`}, it calls `LLMService.ask(data, model)`.
6. Otherwise returns `Unknown action`.

**Responsible modules.** `main.py`, `brain/brain.py`, `brain/intent/intent.py`,
`brain/planner/planner.py`, `kernel/executor.py`, `kernel/dispatcher.py`, `kernel/action_registry.py`.

**Dependencies.** Brain→kernel→registries→tools/services→config.

**Public APIs.** `Brain.think()`, `Planner.create_task()`, `IntentAnalyzer.detect()`,
`Dispatcher.dispatch()`.

**Current maturity.** `STABLE`.

**Known limitations.** `Preprocessor`/`Pipeline` (`brain/preprocessor`, `brain/pipeline`) exist
but are **not** invoked by `Brain.think()`. Coding intent routes to `generate_code`→LLM (no
code is written/executed by this path). The Dispatcher performs presentation (`print`) itself,
coupling routing to console output. Only the 7 registered actions plus 2 LLM actions are reachable.

---

## 5. Runtime Flow (autonomous goal loop)

**Current implementation.** `AutonomousExecutor.run(description, priority, status_observer)`
creates a `Goal` and drives the canonical loop:
`analyze → plan → ready(enqueue tasks) → execute_loop → verify → (reflect → retry/replan) → complete/fail`.
- `_generate_plan()` is a keyword heuristic; `_create_tasks_from_plan()` turns the plan into
  queued task dicts.
- `_execute_loop()` dequeues from `TaskQueue`, runs each task through the kernel `Executor`
  under a **30s per-task timeout** (single-worker `ThreadPoolExecutor`), then `Evaluator`
  judges the result; on failure `ReflectionEngine` classifies the cause and `RetryManager`
  decides the next step (bounded by `MAX_RETRY_COUNT = 2`, escalating
  retry→alternative→replan→user→give_up).
- Every step is recorded via `ExecutionMemory`; on finish the executor flushes memory, resets
  retry budget, and clears the queue.

**Responsible modules.** `brain/executor/autonomous_executor.py`, `brain/goal/goal.py`,
`brain/queue/task_queue.py`, `brain/evaluator/evaluator.py`,
`brain/reflection/reflection_engine.py`, `brain/retry/retry_manager.py`,
`brain/memory/execution_memory.py`.

**Dependencies.** Uses the kernel `Executor` (aliased `KernelExecutor`) for actual dispatch,
so autonomous tasks flow through the same Dispatcher/registries as the CLI path.

**Public APIs.** `AutonomousExecutor.run(...) -> Goal`, `AutonomousExecutor.progress(goal_id)`;
`Goal.transition()`, `Goal.is_terminal()`, `Goal.as_dict()`.

**Current maturity.** `FUNCTIONAL` — full loop implemented with recovery and audit.

**Known limitations.** Task generation is heuristic keyword matching, not LLM planning.
Per-task timeout is fixed at 30s. `Goal` supports a `PAUSED` state but `_execute_loop` simply
breaks when the queue is paused (no external resume driver on this path).

---

## 6. Agent Interactions

**Current implementation.** Agents subclass `BaseAgent` (ABC) with lifecycle
`setup → run(shared_context) → teardown`, a private `AgentContext`, a shared `SharedContext`
blackboard, and a `Messaging` bus. Two orchestrators exist:

- **`OrchestratorAgent`** runs the fixed pipeline `planner → researcher → reviewer → engineer`
  by delegating to `Scheduler.run_pipeline()`, which calls each agent's `run()` in order and
  stores results under `result_<name>` in the shared context; any agent returning
  `success=False` halts the pipeline.
- **`ChiefAgent`** (central coordinator) offers three paths:
  1. `run()` — decompose a task: submits a `plan` task to the `WorkPool`, resolves sub-task
     dependencies with `DependencyResolver`, schedules ready tasks, and waits on a
     `threading.Event` driven by `task_completed`/`task_failed` messages.
  2. `execute_mission()`/`execute_graph()`/`resume_execution()`/`cancel_execution()`/
     `graceful_shutdown()` — validate a `MissionGraph` via `Planner.plan_missions()`, then
     execute sequentially (`MissionExecutor`) or distributed (`WorkPool`+`FleetManager`),
     publishing lifecycle events to an optional `MissionEventBus`.
  3. `run_pipeline()` — same agent chain as `OrchestratorAgent`, via `Scheduler`.

Agents communicate only through `SharedContext` (data) and `Messaging` (events); no agent
calls another agent directly. `ChiefAgent` sends heartbeats to `FleetManager`.

**Responsible modules.** `agents/base_agent.py`, `agents/orchestrator_agent.py`,
`agents/chief_agent.py`, `agents/planner_agent.py`, `agents/research_agent.py`,
`agents/reviewer_agent.py`, `agents/engineer.py`; `brain/scheduler.py`, `brain/messaging.py`,
`brain/shared_context.py`, `brain/agent_registry.py`, `brain/agent_context.py`.

**Dependencies.** Agents → brain coordination primitives; `EngineerAgent` → `AutonomousExecutor`
→ kernel; `ChiefAgent` → `WorkPool`/`DependencyResolver`/`FleetManager`/`Scheduler`/`MissionExecutor`.

**Public APIs.** `BaseAgent.run(shared_context)`, `send_message`/`receive_messages`;
`OrchestratorAgent.execute(task)`; `ChiefAgent.run/execute_mission/run_pipeline/execute(task)`;
`Scheduler.run_pipeline/run_parallel`.

**Current maturity.** Agent pipeline (`Scheduler.run_pipeline`): `FUNCTIONAL`. ChiefAgent
mission/sequential path: `FUNCTIONAL`. ChiefAgent distributed path: `PARTIAL`.

**Known limitations.** The distributed `WorkPool` path broadcasts `work_available` and tracks
completion via messages, but **no autonomous worker loop in the running application calls
`WorkPool.steal_task()`** — workers that pull and execute pool tasks are supplied externally
(e.g., in tests), so distributed execution can time out (`execute_mission` uses a 300s bound).
`ResearchAgent._research_files()` calls `FileTool.list_files(".")`, but `FileTool` exposes
`list_dir` (no `list_files`), so that branch raises and is caught as `{"error": ...}`.
`ReviewerAgent` rejects tasks containing dangerous patterns (`exec(`, `os.system`, `rm -rf`,
`__import__`, `subprocess`, etc.) and tasks whose type is outside its supported heuristic set.

---

## 7. Mission System

**Current implementation.** The mission subsystem (`brain/mission/`) is metadata + orchestration:
- **`Mission`** — a dataclass (id, title, description, priority, status, children, dependencies,
  metadata, error, optional `event_bus`). Enforces a **10-state machine**
  (`created→analyzing→planning→ready→running→verifying→completed`, plus `recovering`, and
  terminal `failed`/`cancelled`) via `_VALID_TRANSITIONS`; `transition()` publishes
  `MISSION_STATUS_CHANGED` + terminal events to the event bus.
- **`MissionGraph`** — a DAG of missions with `add_mission`, `add_dependency` (cycle-checked),
  `get_dependencies`/`get_dependents`, `roots`/`leaves`, `topological_sort` (Kahn),
  `has_cycle`, `validate`, `to_dict`/`from_dict`.
- **`MissionExecutor`** — bridges a `MissionGraph` to execution: orders via
  `Planner.plan_missions()`, moves each mission through its states, and executes each by calling
  `AutonomousExecutor.run()` with a `status_observer` that maps Goal statuses to Mission statuses.
  Supports `halt_on_failure` and `cancel()`.
- **`MissionEventBus`** — synchronous pub/sub with deterministic dispatch, exception isolation,
  and optional bounded history. **`Epic`** groups missions. **`MissionPersistence`** saves/loads
  graphs. **`MissionID`**, **`MissionPriority`**, **`MissionEvent`/`MissionEventType`** supporting types.

**Responsible modules.** `brain/mission/{mission,graph,mission_executor,event_bus,event,
event_types,epic,persistence,mission_id,mission_priority,mission_status}.py`.

**Dependencies.** `MissionExecutor` → `Planner` + `AutonomousExecutor` (so missions ultimately
run through the kernel). `ChiefAgent` orchestrates missions. `Mission` optionally holds an event bus.

**Public APIs.** `Mission.transition/add_child/add_dependency/to_dict/from_dict`;
`MissionGraph.*` (above); `MissionExecutor.execute(graph, halt_on_failure)`, `.cancel()`;
`MissionEventBus.subscribe/publish/unsubscribe/event_history`.

**Current maturity.** Mission/Graph/EventBus/Executor: `FUNCTIONAL` (well-formed, exercised by
`ChiefAgent` and tests). Persistence: `FUNCTIONAL`.

**Known limitations.** Missions are pure metadata (no self-execution, by design). Two execution
routes exist for a graph — sequential (`MissionExecutor`) and distributed (`ChiefAgent`+`WorkPool`);
the distributed route shares the worker-loop limitation from §6. Per-mission execution reduces to
a heuristic autonomous goal (title+description as the goal description).

---

## 8. Tool System

**Current implementation.** Tools implement small, concrete capabilities and are held in
`ToolRegistry` (5 tools):
- `Calculator.calculate(expr)`; `PythonExecutor.execute(code)` (runs via `exec`);
  `FileTool` (`read, write, list_dir, exists, backup, append, delete, copy, move, replace_text`);
  `MemoryTool.remember/recall` (delegates to `MemoryService`); `InternetTool.search` (DuckDuckGo).
- `BaseTool` is an ABC with `execute(*args, **kwargs)`.
- **Mission-7.1.8 tool-integration layer (present, separate):** `ToolWrapper` (adds per-tool
  `timeout`, bounded `max_retries`, returns a `ToolResult`), `ToolResult` (`ok`/`fail`/`to_dict`/
  `from_dict`), and `CapabilityValidator` (validates actions/tools against `ActionRegistry`/
  `ToolRegistry`).

**Responsible modules.** `tools/{base_tool,calculator,python_executor,file_tool,memory_tool,
internet_tool,tool_registry,tool_wrapper,tool_result,capability_validator}.py`.

**Dependencies.** `Dispatcher` → `ToolRegistry` → tool instances. `MemoryTool` → `MemoryService`.
`CapabilityValidator` → `ActionRegistry` + `ToolRegistry`.

**Public APIs.** `ToolRegistry.get(name)`, `list_tools()`; each tool's method; `ToolWrapper.invoke(...)`.

**Current maturity.** Core 5 tools: `STABLE`. `ToolWrapper`/`ToolResult`/`CapabilityValidator`: `PARTIAL`.

**Known limitations.** The **main `Dispatcher` does not use `ToolWrapper`/`CapabilityValidator`**
— it calls tool methods directly with no timeout/retry/`ToolResult` wrapping (those are used by
the mission tool-integration path only). `PythonExecutor` uses `exec` (arbitrary code execution;
`ReviewerAgent` guards some patterns but the kernel path does not). `InternetTool` depends on
external network. FileTool operations are unrestricted (no workspace-boundary enforcement in code read).

---

## 9. Memory System

**Current implementation.** Two layers exist:
- **`MemoryService`** (`services/memory.py`) — a JSON-backed key/value store persisted to
  `storage/memory/memory.json` (path from `settings.MEMORY_FILE`). Methods: `load`, `save`,
  `remember(key,value)`, plus `recall`/`forget`/`show_all` (referenced by callers). Registered
  in `ServiceRegistry` as `memory` and exposed as a tool via `MemoryTool`.
- **`ExecutionMemory`** (`brain/memory/execution_memory.py`) — an audit/replay log built ON TOP
  of `MemoryService`. It records every autonomous step (`goal`, `plan`, `task`, `action`,
  `output`, `error`, `reflection`) under `execution:<goal>:<step>:<ts>` keys, keeps a per-goal
  in-memory index for fast `recall`, batches writes (`batch_size=10`), and prunes to
  `max_records_per_goal=1000`.

**Responsible modules.** `services/memory.py`, `brain/memory/execution_memory.py`,
`tools/memory_tool.py`.

**Dependencies.** `ExecutionMemory` → `MemoryService`; `MemoryTool` → `MemoryService`;
`AutonomousExecutor` → `ExecutionMemory`. Reached from CLI via `remember`/`recall` actions.

**Public APIs.** `MemoryService.remember/recall/forget/show_all/save/load`;
`ExecutionMemory.record/recall/recall_latest/flush`.

**Current maturity.** `MemoryService`: `STABLE`. `ExecutionMemory`: `FUNCTIONAL`.

**Known limitations.** It is a flat JSON key/value store — no embeddings, vector search, or
semantic retrieval (research/recall are substring/key matches). All execution history and
user memory share one `memory.json`. No concurrency locking on `MemoryService` file writes
observed in the read (it is called from single-threaded paths).

---

## 10. Model / Provider System

**Current implementation.** Model selection is a static role→name mapping in
`config/models.py`:
```
general  → qwen3:8b        coding    → qwen2.5-coder:7b   reasoning → deepseek-r1:8b
creative → llama3.1:8b     fast      → gemma3:4b
```
- **`ModelRegistry`** (`models/registry.py`) wraps `settings.MODELS` with `get(role)`/`list_models()`.
- **`ModelSelector`** (`models/selector.py`) selects a model from a plan string.
- **`Router`** (`brain/router.py`) maps prompt keywords → coding/reasoning/creative/general model.
- **`LLMService`** (`services/llm.py`) calls the model via the Ollama client;
  **`OllamaService`** checks `is_running`, `list_models`, `count_models` against
  `settings.OLLAMA_HOST` (`http://127.0.0.1:11434`).

**Responsible modules.** `config/models.py`, `config/settings.py`, `models/registry.py`,
`models/selector.py`, `brain/router.py`, `services/llm.py`, `services/ollama_service.py`.

**Dependencies.** `Planner`/`Dispatcher` → `ModelRegistry`; `LLMService` → Ollama HTTP;
`Router` → `settings.MODELS`.

**Public APIs.** `ModelRegistry.get(role)`, `list_models()`; `ModelSelector.select(plan)`;
`Router.choose_model(prompt)`; `LLMService.ask(prompt, model)`; `OllamaService.is_running()`.

**Current maturity.** Local Ollama routing: `FUNCTIONAL` (depends on a running Ollama daemon).

**Known limitations.** There is **no multi-provider abstraction in the application** — the app
targets Ollama only; the 5 models are hardcoded. (A separate provider-failover concept exists
only in the dev-loop `scripts/provider.py`, not in the app.) Multiple selection mechanisms
coexist (`ModelRegistry`, `ModelSelector`, `Router`) without a single unified router.

---

## 11. Scheduler / Fleet Status

**Current implementation.**
- **`Scheduler`** (`brain/scheduler.py`) — deterministic multi-agent runner:
  `run_pipeline(agent_names, shared_context)` executes agents strictly in order (halts on
  failure/exception); `run_parallel(agent_names, ...)` runs them concurrently with a thread pool
  capped at `min(len, 32)`. This is the scheduler used by `OrchestratorAgent` and `ChiefAgent.run_pipeline`.
- **`FleetManager`** (`brain/fleet_manager.py`) — tracks agents via asynchronous `heartbeat`/
  `register` messages on the `Messaging` bus; stores `capabilities`, `load`, `status`,
  `consecutive_failures`, `last_seen`; supports `report_health`, `get_fleet_state`,
  `increment/clear_failures`, `unregister`, and `reap_dead_agents(timeout=60s)`.
- **`WorkPool`** (`brain/work_pool.py`) — capability-keyed deques; `submit_task`, `steal_task`,
  `complete_task`, `fail_task`, `requeue_task`, broadcasting `work_available`/`task_completed`/
  `task_failed`.
- **`DependencyResolver`** (`brain/dependency_resolver.py`) — Kahn topological sort with `CycleError`.
- **`CapabilityRouter`** can do least-connections load-aware agent selection when given a
  `FleetManager`.

**Responsible modules.** `brain/{scheduler,fleet_manager,work_pool,dependency_resolver,
capability_router}.py`.

**Dependencies.** `Scheduler` → `AgentRegistry` + `Messaging`. `FleetManager`/`WorkPool` → `Messaging`.
`ChiefAgent` orchestrates all of these.

**Public APIs.** `Scheduler.run_pipeline/run_parallel`; `FleetManager.register/report_health/
get_fleet_state/reap_dead_agents`; `WorkPool.submit_task/steal_task/complete_task/fail_task/requeue_task`;
`DependencyResolver.resolve(tasks)`.

**Current maturity.** `Scheduler` (sequential pipeline): `FUNCTIONAL`/`STABLE`.
`DependencyResolver`: `STABLE`. `FleetManager`: `FUNCTIONAL`. `WorkPool`: `PARTIAL`.

**Known limitations.** As in §6/§7, the WorkPool distributed model has **no in-application
worker thread** that steals and executes tasks; it is driven by external callers/tests.
`reap_dead_agents` is not called on a timer by any running loop in the read. There is also a
separate `kernel/scheduler.py` file (not examined in depth this pass; project index describes
the kernel-level `scheduler.py`/`event_bus.py`/`permissions.py` as placeholder/near-empty) —
the scheduler actually wired to agents is `brain/scheduler.py`.

---

## 12. Recovery Mechanisms

**Current implementation.** Application-level recovery is built into the autonomous loop:
- **`ReflectionEngine`** classifies failures (missing_dependency, invalid_path, runtime_exception,
  wrong_tool, wrong_planning, service_unavailable, unknown) into a strategy (retry/replan/
  alternative/user) using keyword frozensets — deterministic, no LLM.
- **`RetryManager`** enforces `MAX_RETRY_COUNT=2` per goal and escalates
  retry → alternative → replan → user → give_up via `decide_next_step()`.
- **`AutonomousExecutor`** applies these in `_handle_failure`/`_replan`, and wraps each task in a
  30s `ThreadPoolExecutor` timeout.
- **`Goal`** has a `PAUSED` state; **`TaskQueue`** supports pause/resume/cancel and requeue.
- **`ChiefAgent`** provides `cancel_execution()`, `resume_execution(persistence_path)` (reloads a
  persisted `MissionGraph`, resets in-flight missions to `READY`), and `graceful_shutdown()`.
- **`MissionExecutor.cancel()`** stops the sequential loop; **`WorkPool.requeue_task`** returns a
  stolen task; **`FleetManager.reap_dead_agents`** removes stale agents.

**Responsible modules.** `brain/reflection/reflection_engine.py`, `brain/retry/retry_manager.py`,
`brain/executor/autonomous_executor.py`, `brain/goal/goal.py`, `brain/queue/task_queue.py`,
`agents/chief_agent.py`, `brain/mission/mission_executor.py`, `brain/mission/persistence.py`.

**Dependencies.** Reflection+Retry are consumed by `AutonomousExecutor`; resume relies on
`MissionPersistence`.

**Public APIs.** `ReflectionEngine.reflect(...)`, `should_escalate_to_user()`;
`RetryManager.can_retry/record_attempt/decide_next_step/reset`;
`ChiefAgent.cancel_execution/resume_execution/graceful_shutdown`.

**Current maturity.** Goal-level reflect/retry/replan: `FUNCTIONAL`. Mission resume/cancel: `FUNCTIONAL`.

**Known limitations.** Recovery strategy selection is keyword-based, not adaptive. `MAX_RETRY_COUNT`
is fixed at 2. `resume_execution` requires a persisted graph file. A **second, separate** recovery
system exists only for the dev loop (`scripts/recovery.py`: `FailureClass`, `RetryStrategy`) and is
not used by the application at runtime.

---

## 13. Context System

**Current implementation.** "Context" exists at three distinct scopes:
- **Runtime agent context (in-app):** `SharedContext` — a thread-safe blackboard (`get/set/
  update/snapshot/record/get_history/clear`, deque-based history, `__slots__`), used by agents
  to pass `task`, `goal`, `plan`, `research`, `review`, `result_<agent>`, etc.; `AgentContext`
  — per-agent private state/history; `KnowledgeRouter` — topic-subscription filter over
  `SharedContext` so agents load only subscribed topics.
- **Kernel state (in-app):** `KernelState` (`Booting`/`Online`, loaded counts).
- **Engineering-loop context (dev tooling, NOT app runtime):** the `.amalgam-core/` directory +
  `scripts/context.py`. `STATE.json` is the single source of truth for the dev loop;
  `context.py` provides `status/complete/next/checkpoint/resume/audit/rebuild` and regenerates
  `MISSION.md`, `TASK.md`, `CONTEXT.md` from it. `registry.py` discovers repo components into
  `REGISTRY.json`; `fingerprint.py` writes SHA-256 `CHECKSUMS.json` + git head/branch;
  `loop.py` models a 17-stage engineering loop; `bootstrap.py` initializes the directory.

**Responsible modules.** In-app: `brain/shared_context.py`, `brain/agent_context.py`,
`brain/knowledge_router.py`, `kernel/state.py`. Dev loop: `scripts/*`, `.amalgam-core/*`.

**Dependencies.** `SharedContext`/`AgentContext` are used across agents and the scheduler.
The `.amalgam-core` tooling is standalone (stdlib only) and is not imported by the application.

**Public APIs.** `SharedContext.get/set/update/snapshot`; `AgentContext.*`;
`KnowledgeRouter.subscribe/publish/get_context`; (dev-loop CLI) `python scripts/context.py <cmd>`.

**Current maturity.** In-app context primitives: `FUNCTIONAL`/`STABLE`. Dev-loop context system:
`FUNCTIONAL` but **out of sync** (see limitations).

**Known limitations.** `.amalgam-core/STATE.json` is **stale/illustrative**: it reports
`current_mission = M7.2 (in_progress)`, `completed = M7.1.8`, `tests = 806`,
`provider = openai/gpt-4o`, `current_branch = core/amalgam-core-v1` — the `gpt-4o` provider does
not match the application's Ollama-only model config, confirming `.amalgam-core` tracks the
development process, not the running app. There is no runtime bridge between `SharedContext`
(app) and `STATE.json` (dev loop).

---

## 14. Remaining Architectural Gaps (as-is observations)

These are gaps observed in the current code. They are recorded, not proposed for fixing.

1. **Single-task CLI vs. multi-agent/mission layers are not connected at an entry point.**
   `main.py` only runs `Brain→Executor→Dispatcher`. `ChiefAgent`/`OrchestratorAgent`/
   `MissionExecutor` are reachable only by direct instantiation.
2. **No in-application worker loop for `WorkPool`.** Distributed mission execution depends on
   external/test workers calling `steal_task`/`complete_task`; otherwise it relies on the 300s timeout.
3. **Duplicated/overlapping routing & planning.** `Router`, `CapabilityRouter`, `ModelSelector`,
   `KnowledgeRouter` all route; planning logic is duplicated across `Planner.create_task`,
   `PlannerAgent._generate_plan`, and `AutonomousExecutor._generate_plan`.
4. **Mission-7.1.8 tool safety layer is not on the live path.** `ToolWrapper` (timeout/retry) and
   `CapabilityValidator` exist but the kernel `Dispatcher` calls tools directly.
5. **`brain/orchestrator.py` is legacy** and duplicates memory/LLM handling now owned by the
   Brain/Dispatcher path.
6. **Latent bug:** `ResearchAgent._research_files` calls `FileTool.list_files`, which does not
   exist (`FileTool` has `list_dir`); the call is swallowed as an error dict.
7. **Unused primitives:** `Preprocessor`/`Pipeline` are implemented but not invoked by `Brain.think`.
8. **Placeholder services:** `services/internet.py` and `services/knowledge.py` are empty stubs
   (real behavior lives in `tools/internet_tool.py` and the `knowledge/` engine).
9. **Version drift:** `config/settings.py` `APP_VERSION = "0.3.0"` while repository tags reach
   `amalgam-core-v1.1-stable`; the boot banner therefore reports 0.3.0.
10. **No `EngineRegistry`.** The Tool/Service/Engine taxonomy is only partially realized: engines
    are accessed via the `project` Service, not a dedicated registry.
11. **Security surface:** `PythonExecutor` uses `exec`; `Calculator` evaluates expressions;
    FileTool has no workspace-boundary enforcement in the code read. Guarding exists only in
    `ReviewerAgent` (agent path), not in the kernel dispatch path.
12. **The "Reasoning" pillar** (of the Four-Pillars concept) has no dedicated component; reasoning
    is implicit in `Planner`, `ReflectionEngine`, and heuristics.
13. **Dev-loop vs app divergence:** `.amalgam-core` (STATE/HISTORY/loop/provider/recovery) is a
    parallel system not wired into the application runtime.
14. **`kernel/scheduler.py`, `kernel/event_bus.py`, `kernel/permissions.py`** exist in the tree
    but are not part of the live dispatch path (the active scheduler is `brain/scheduler.py`);
    their contents were not examined in depth on this pass.

*End of CURRENT_ARCHITECTURE_STATE.md — documents the repository as implemented; no changes proposed.*
