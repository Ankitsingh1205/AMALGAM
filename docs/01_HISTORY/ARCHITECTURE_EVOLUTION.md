# ARCHITECTURE_EVOLUTION.md

> **Document type:** Design-history recovery (engineering historian).
> **Source:** `AMALGAM_FULL_CONVERSATION.md` (design history). Repo cited separately.
> **Purpose:** Record how AMALGAM's architecture changed over time, in order, with the
> original wording, marking conflicts and never reconciling them.
>
> **Sourcing legend:** `[VERBATIM]` quoted (timestamp given); `[RECOVERED]` paraphrased from
> earlier full read; `[REPO]` repository evidence.

---

## Timeline of architectural states

```
A0  Orchestrator-first skeleton      6/27 ~10:36 AM   core/ + services/
A1  core/->brain, engine/->kernel    6/27 ~8:03 PM    Genesis-5 rename
A2  Task/Dispatcher/ActionRegistry    6/27-6/28        Genesis-6..8
A3  Workspace Engine layer            6/29 ~10:03 AM   Mission 3 (read-only, between Planner & Kernel)
A4  Knowledge Engine + Four Pillars   6/29 ~10:08 AM   Mission 4
A5  Tool/Service/Engine + Golden Rule 6/29 ~11:10 AM   Architecture v1.0 FROZEN
A6  Multi-agent runtime               7/1  ~2:21 AM    Mission 6.5
A7  Fleet/Dynamic scheduling          7/1  ~5:07 PM    Mission 6.6
A8  Mission Engine                    7/2-7/8          Mission 7.1.x
A9  .amalgam-core engineering loop    7/6              external-to-app infra
```

---

## A0 - Orchestrator-first skeleton (the founding architecture)

`[VERBATIM]` **6/27/2026, 10:36:06 AM**:
> ```
> AMALGAM -> ORCHESTRATOR -> [ Brain | Memory | Knowledge | Tools | Interface ]
> ```

`[VERBATIM]` The governing decision:
> **The LLM is not the brain. The Orchestrator is.**

`[RECOVERED]` Implemented as `core/` (orchestrator, router, planner, session) + `services/`
(memory, knowledge, llm, internet). **Status:** IMPLEMENTED (Genesis-1).

---

## A1 - The core->brain / engine->kernel rename (Genesis-5)

**Timestamp:** 6/27/2026, ~8:03 PM.
`[RECOVERED]` `core/` renamed to `brain/`; `engine/` renamed to `kernel/`; all imports
updated `from core.` -> `from brain.`. `KernelState` (kernel/state.py), `Executor.boot()`,
`OllamaService`, `ModelRegistry`, and an `interfaces/` folder introduced. Architecture rated
"9.9/10" at this point.
**Significance:** established the brain(thinks)/kernel(executes) split that survives to the end.
**Status:** IMPLEMENTED. **Related:** every later mission sits on this split.

---

## A2 - Task / Dispatcher / ActionRegistry (Genesis-6..8)

**Timestamp:** 6/27/2026 8:37 PM - 6/28/2026 ~1:14 AM.
`[RECOVERED]` `kernel/task.py` (Task dataclass), `kernel/dispatcher.py` (routes Task by
action), `kernel/action_registry.py` (action string -> (tool, method)). Dispatcher refactored
to use ActionRegistry, removing an if-chain. `tools/base_tool.py`, ToolRegistry,
ServiceRegistry.
**Significance:** the ActionRegistry became the universal extension point ("add a new tool
without touching the Dispatcher").
**Status:** IMPLEMENTED.

`[RECOVERED]` Codex's Genesis-8 audit flagged "5 duplicate routing mechanisms" (Router,
ToolRouter, ModelSelector, ModelRegistry, Planner). **CONFLICT (unresolved):** a "Unified
Routing Engine" was proposed (Scheme A Mission 3) to collapse these but was never built.

---

## A3 - Workspace Engine layer (Mission 3)

**Timestamp:** 6/29/2026, ~10:03 AM.
`[VERBATIM]` placement:
> the **Workspace Engine sits between planning and execution**.

`[RECOVERED]` `workspace/` package, read-only, deterministic (no LLM). Answers "Tell me
about this project."
**Status:** IMPLEMENTED. **Dependencies:** brain/kernel split.

---

## A4 - Knowledge Engine + "Four Pillars of Intelligence" (Mission 4)

**Timestamp:** 6/29/2026, 10:08:36 AM.
`[VERBATIM]` the Four Pillars (govern all later architecture):
> ### 🟦 Workspace  > **What exists?**
> ### 🟩 Knowledge  > **How is it connected?**
> ### 🟨 Memory     > **What happened before?**
> ### 🟥 Reasoning  > **What should happen next?**
> Everything else-Browser, Git, Vision, Voice, Agents-will plug into these four pillars.

`[VERBATIM]` constraint: "Mission 4 is **NOT RAG**. No embeddings. No vector database. Pure
engineering." (uses Python `ast`). **Status:** IMPLEMENTED.

---

## A5 - Tool / Service / Engine layering + Golden Rule (Architecture v1.0 FROZEN)

**Timestamp:** 6/29/2026, 11:10:26 AM. **This is the defining architecture event.**

`[VERBATIM]` the layer stack:
> ```
> USER -> Conversation Interface -> ORCHESTRATOR -> BRAIN -> INTENT ANALYZER -> PLANNER
> -> TASK -> EXECUTOR -> DISPATCHER -> [Tools | Services | Engines | Future]
> ```
> ## Layer 5 - Registries: ActionRegistry / ToolRegistry / ServiceRegistry / EngineRegistry (new)
> ## Layer 6 - Tools (perform actions) ## Layer 7 - Services (state/external) ## Layer 8 - Engines (analyze/understand)

`[VERBATIM]` the Golden Rule:
> # Golden Rule  Every new module must answer:
> > **Am I a Tool, a Service, or an Engine?**
> If the answer isn't clear, the design isn't finished.

`[VERBATIM]` the three definitions:
> - **Tools** perform actions (Calculator/Python/Files/Internet).
> - **Services** maintain state or external communication (LLM/Memory/Diagnostics).
> - **Engines** analyze and understand (Workspace/Knowledge/Vision(future)/Git(future)).

**CONFLICT (unresolved) - the EngineRegistry:** The `EngineRegistry` was declared "new" and
central here, but the repo's actual dispatcher routes via ActionRegistry to Tools OR Services
(Workspace/Knowledge were reached through `ProjectService`, a Service). Whether a distinct
`EngineRegistry` class was ever implemented is not confirmed. Recorded, not reconciled.

**Status:** ACCEPTED as design ("frozen"); partially implemented. **Related:** Mission 5.

---

## A5b - The Constitution v1.0 (10 Principles)

**Timestamp:** 6/29/2026, ~9:29 AM (written during Mission 2, governs everything after).
`[VERBATIM]` (condensed, `docs/Constitution.md`):
> P1 The Brain thinks. It never executes.
> P2 The Kernel executes. It never reasons.
> P3 The Dispatcher coordinates execution. It never contains business logic.
> P4 Tools perform actions. They never communicate directly with one another.
> P5 Services provide infrastructure. They do not make product decisions.
> P6 Every module must be replaceable.
> P7 Configuration belongs in one place.
> P8 Every feature must include automated tests.
> P9 Every architectural decision must scale to 100 tools / 50 services / 20 agents / 500+ files.
> P10 User approval comes before autonomous execution whenever actions can modify user data.

`[Historian note]` These principles echo the five Genesis-era principles (see GENESIS.md);
they were re-expressed and expanded, not contradicted.

---

## A6 - Multi-agent runtime (Mission 6.5)

**Timestamp:** 7/1/2026, 2:21:48 AM.
`[VERBATIM]` target topology:
> User Goal -> Orchestrator Agent -> [ Planner | Engineer | Research | Reviewer ] -> Shared Memory -> Kernel/Tools

`[VERBATIM]` locked rules:
> No agent may call another agent directly. All communication uses structured messages.
> Every agent returns structured results, not free-form text. Every orchestration step is logged.

`[RECOVERED]` Implemented via BaseAgent, OrchestratorAgent, PlannerAgent, ResearchAgent,
ReviewerAgent, plus brain/messaging.py, agent_context.py, agent_registry.py, shared_context.py.
**Status:** IMPLEMENTED (232 tests). **Dependencies:** Mission 6.4 autonomous core.

---

## A7 - Fleet / Dynamic scheduling (Mission 6.6)

**Timestamp:** 7/1/2026, 5:07 PM.
`[RECOVERED]` DynamicScheduler (kernel/scheduler.py), FleetManager, HealthMonitor, WorkPool
(work-stealing), DependencyResolver (topological), KnowledgeRouter, CapabilityRouter,
dependency-graph execution + sequential fallback. **Status:** IMPLEMENTED (247 tests).
**Dependencies:** Mission 6.5. **Related:** ChiefAgent (7.2) later drives the fleet.

---

## A8 - Mission Engine (Mission 7.1.x)

**Timestamp:** 7/2/2026 - 7/8/2026.
`[RECOVERED]` A `brain/mission/` package: Mission dataclass + state machine, Epic, Mission
Graph (cycle detection, topological sort), Mission persistence, Mission Event Bus,
MissionExecutor integrated with PlannerAgent, then with AutonomousExecutor, then with the
tool system. ChiefAgent orchestration (7.2) and ChiefAgent+FleetManager (7.3) on top.

`[VERBATIM]` **Mission 7 Master Architecture existed only as a 25-section table of contents**
(7/2 3:26 PM), which is why implementation stalled until the team switched to prompt-driven
specs. The 25 TOC sections were: Vision, Design Principles, High-Level Architecture, Layered
Architecture, Agent Hierarchy, Mission Engine, Planning Engine, Event Bus, Memory Topology,
Knowledge System, Runtime Architecture, Scheduler Design, Fleet Management, Tool Ecosystem,
Model Routing, Workspace Intelligence, Security Model, Configuration, Observability,
Performance Targets, Folder Structure, Public APIs, Testing Strategy, Milestones (7.0->7.8),
Future Roadmap.
**Status:** IMPLEMENTED (7.1.0-7.3); the TOC's deeper sections were never fleshed out.

---

## A9 - `.amalgam-core` engineering-loop infrastructure (7/6/2026)

**Timestamp:** 7/6/2026, 3:01-4:09 AM.
`[Historian note]` This is architecture ABOUT the development process, not a feature of the
running app. It made missions resumable and model-agnostic.

`[VERBATIM]` the file set (final "v1.1"):
> .amalgam-core/ : AGENTS.md, LOOP.md, CONTEXT.md, MISSION.md, TASK.md, STATE.json,
> HISTORY.json, REGISTRY.json, WORKFLOW.yaml, SESSION.json, CHECKPOINT.json, QUEUE.json

`[VERBATIM]` LOOP.md's 17-stage loop:
> 1 Repository Inspection 2 Architecture Analysis 3 Existing Code Discovery 4 Dependency
> Discovery 5 Reuse Decision 6 Planning 7 Implementation 8 Static Validation 9 Testing
> 10 Failure Recovery 11 Regression Testing 12 Documentation Update 13 Checkpoint Save
> 14 State Update 15 Mission Update 16 History Update 17 Completion

`[RECOVERED]` Design rule: **STATE.json is the single source of truth**; MISSION.md/TASK.md/
CONTEXT.md are GENERATED from it by `scripts/context.py`. Scripts: bootstrap.py, context.py,
registry.py, loop.py, recovery.py, fingerprint.py, engine.py, provider.py.
**CONFLICT / defect recorded:** first audit scored it **30/100** (context.py & registry.py
were 0 bytes; STATE-to-document pipeline missing; bootstrap generated a state that failed its
own schema; LOOP.md vs WORKFLOW.yaml mismatch). Later stabilized to ~98/100.
**Status:** IMPLEMENTED then stabilized. **Repository evidence:** `[REPO]` `.amalgam-core/`
and `scripts/` directories; commits `443c952`/`3c44d71` "AMALGAM Core v1.0 infrastructure".

---

## Recurring architectural conflicts (recorded, NOT reconciled)

1. **"AI OS" vs "Personal AI Platform"** - user's label vs AI's label; both persisted.
2. **Orchestrator's role** - declared "the brain" (Genesis) but became a legacy bypass by
   Mission 5 (main.py drove Brain->Planner->Task->Executor->Dispatcher directly).
3. **EngineRegistry** - declared a core new layer (A5) but not confirmed implemented as a
   distinct registry; engines were reached via a Service (ProjectService).
4. **Unified Routing Engine** - flagged as needed (5 duplicate routers) but never built.
5. **Genesis roadmap vs built Genesis** - names diverged (see GENESIS.md).

*End of ARCHITECTURE_EVOLUTION.md*
