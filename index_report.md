# AMALGAM OS — Full Project Index Report

**Generated:** 2026-07-02  
**Scope:** Every file in the repository has been read and indexed.

---

## 1. Project Overview

**Name:** AMALGAM OS (amalgam-os)  
**Version:** 0.3.0  
**Description:** Artificial Intelligence Operating System — a multi-agent AI framework with autonomous goal execution, knowledge graph capabilities, and workspace analysis. Built on Ollama for local LLM inference.

**Key Dependencies:** ollama, requests, pytest  
**Python:** >=3.10  
**Default Models:** qwen3:8b (general), qwen2.5-coder:7b (coding), deepseek-r1:8b (reasoning), llama3.1:8b (creative), gemma3:4b (fast)

---

## 2. Execution Pipeline (Canonical Runtime Flow)

```
User → Brain → IntentAnalyzer → Planner → Task → Executor → Dispatcher → Tool/Service

User → OrchestratorAgent → PlannerAgent → ResearchAgent → ReviewerAgent → EngineerAgent

User → AutonomousExecutor → Goal → Analyze → Plan → Queue → Execute → Evaluate → Reflect → Retry
```

---

## 3. Files Read (Complete)

### Root Files (12 files)
| File | Lines | Content |
|------|-------|---------|
| `main.py` | 43 | Entry point: Brain → Executor REPL loop |
| `pyproject.toml` | 15 | Project metadata and dependencies |
| `requirements.txt` | 2 | ollama, requests |
| `ROO.md` | 27 | AMALGAM development rules for AI agents |
| `AI_RULES/AMALGAM_GLOBAL.md` | 93 | Global engineering rules (SOLID, no TODOs, Windows env) |
| `.agent.md` | 56 | Agent behavior configuration |
| `.gitignore` | 21 | Python/venv/IDE ignores |
| `LICENSE` | 0 | Empty |
| `.cd` | 0 | Empty |
| `MISSION_6.4.3_SECURITY_AUDIT.md` | 233 | Full security audit (3 critical, 6 high findings) |
| `benchmark.py` | 116 | Mission 6.4.2 performance benchmark |
| `benchmark_652.py` | 245 | Mission 6.5.2 post-optimization benchmark |
| `benchmark_662.py` | 115 | Mission 6.6.2 adaptive layer benchmark |
| `benchmark_post.py` | 85 | Quick post-optimization benchmark |
| `mission6_01.py` | 55 | Mission 6.0.1: file_tool.py backup |
| `mission6_02.py` | 75 | Mission 6.0.2: add methods to file_tool.py |
| `mission6_03.py` | 63 | Mission 6.1: Create EngineerAgent |
| `output.txt` | binary | Benchmark output data |
| `storage/memory/memory.json` | ~2000 | Execution memory persistence records |

### `config/` (7 files)
| File | Lines | Purpose |
|------|-------|---------|
| `__init__.py` | 1 | Empty package marker |
| `constants.py` | 78 | All action/intent/tool/service/goal/task/evaluation/reflection constants |
| `models.py` | 7 | Model role→name mappings (5 models) |
| `settings.py` | 23 | Runtime config (OLLAMA_HOST, MEMORY_FILE, LOG_LEVEL, APP_NAME) |
| `version.py` | 15 | Build metadata (version, env, python, OS) |
| `constants.py.bak` | - | Backup |

### `kernel/` (10 files)
| File | Lines | Purpose |
|------|-------|---------|
| `__init__.py` | 0 | Empty |
| `executor.py` | 65 | Boot kernel (displays metadata), execute/dispatch tasks |
| `dispatcher.py` | 128 | Routes tasks via ActionRegistry to tools/services, LLM fallback |
| `action_registry.py` | 21 | Maps action constants to (target_name, method_name) |
| `task.py` | 25 | Task dataclass (intent, action, model, tool, data) |
| `state.py` | 22 | KernelState (boot status, models/services/tools loaded) |
| `event_bus.py` | 0 | Empty/placeholder |
| `permissions.py` | 0 | Empty/placeholder |
| `scheduler.py` | 0 | Empty/placeholder |
| `action_registry.py.bak`, `dispatcher.py.bak` | - | Backups |

### `brain/` — Core module (25+ files)

**Top-level (15 files):**
| File | Lines | Purpose |
|------|-------|---------|
| `__init__.py` | 0 | Empty |
| `brain.py` | 21 | think() → intent → plan → Task |
| `orchestrator.py` | 61 | Legacy direct memory/LLM processing |
| `router.py` | 44 | Model selection by keyword (frozenset-optimized) |
| `agent_registry.py` | 65 | Central agent registration/lookup |
| `agent_context.py` | 61 | Per-agent isolated private state |
| `shared_context.py` | 75 | Thread-safe blackboard (__slots__-optimized) |
| `messaging.py` | 161 | In-memory message bus with subscribe/broadcast |
| `scheduler.py` | 170 | Deterministic pipeline + parallel execution |
| `dependency_resolver.py` | 74 | Kahn's algorithm topological sort for task DAGs |
| `work_pool.py` | 137 | Capability-aware distributed task queue with work stealing |
| `fleet_manager.py` | 94 | Agent health/lifecycle management with heartbeats |
| `capability_router.py` | 98 | Task→capability routing with load-aware dispatch |
| `knowledge_router.py` | 62 | Topic-based filtered context routing |
| `session.py` | 8 | Placeholder session manager |
| `constants.py` | 71 | Centralized frozensets for keyword matching |

**Subpackages (13 files):**
| Subpackage | File | Lines | Purpose |
|------------|------|-------|---------|
| `intent/` | `intent.py` | 77 | IntentAnalyzer: classifies user input into 8 intent types |
| `planner/` | `planner.py` | 101 | Planner: creates Task objects from intent + user input |
| `executor/` | `autonomous_executor.py` | 629 | Full goal lifecycle (analyze→plan→queue→execute→evaluate→reflect→retry) |
| `goal/` | `goal.py` | 150 | Goal dataclass with 14-status state machine |
| `evaluator/` | `evaluator.py` | 131 | Execution result validation (success/failure/partial/unknown) |
| `reflection/` | `reflection_engine.py` | 160 | Failure analysis + recovery strategy selection |
| `retry/` | `retry_manager.py` | 136 | Bounded retry with strategy escalation |
| `queue/` | `task_queue.py` | 214 | FIFO queue with pause/resume/cancel, O(1) progress |
| `memory/` | `execution_memory.py` | 184 | Batched audit log for goal execution steps |
| `mission/` | `mission.py` | 165 | Mission dataclass with state machine |
| `mission/` | `mission_id.py` | 55 | UUID4 wrapper |
| `mission/` | `mission_priority.py` | 15 | Priority enum (LOW=1, NORMAL=5, HIGH=10, CRITICAL=20) |
| `mission/` | `mission_status.py` | 83 | 9-state lifecycle enum with transition table |
| `mission/` | `epic.py` | 129 | Epic: group of missions |
| `mission/` | `graph.py` | 402 | Mission DAG with cycle detection, topological sort |
| `mission/` | `node.py` | 0 | Empty |
| `mission/` | `dependency.py` | 0 | Empty |
| `pipeline/` | `pipeline.py` | 10 | Preprocessor wrapper |
| `preprocessor/` | `preprocessor.py` | 11 | Input normalizer (strip, lowercase) |
| `tools/` | `tool_router.py` | 25 | Routes plan keywords to model/tool names |

### `agents/` (8 files)
| File | Lines | Purpose |
|------|-------|---------|
| `__init__.py` | 0 | Empty |
| `base_agent.py` | 117 | Abstract agent with setup→run→teardown lifecycle, messaging, context |
| `chief_agent.py` | 159 | Mission orchestration with capability-aware work stealing |
| `planner_agent.py` | 103 | Creates Goal + heuristic plan from task description |
| `research_agent.py` | 116 | Gathers context (memory, files, project, web) |
| `reviewer_agent.py` | 100 | Deterministic quality/safety checks |
| `engineer.py` | 109 | Executes tasks via AutonomousExecutor, wraps FileTool/PythonExecutor |
| `orchestrator_agent.py` | 160 | Full pipeline: Planner→Research→Reviewer→Engineer |

### `services/` (12 files)
| File | Lines | Purpose |
|------|-------|---------|
| `__init__.py` | 0 | Empty |
| `logger.py` | 85 | Structured logging (DEBUG/INFO/WARNING/ERROR) |
| `llm.py` | 43 | Ollama chat wrapper |
| `ollama_service.py` | 44 | Ollama health check, list/count models |
| `memory.py` | 71 | JSON-persistent key-value store (remember/recall/forget) |
| `project_service.py` | 25 | Workspace + knowledge engine summary |
| `diagnostics.py` | 162 | Health check (config, memory, tools, services, ollama, storage) |
| `service_registry.py` | 26 | Service registration (LLM, Memory, Ollama, Project) |
| `internet.py` | 6 | Empty placeholder |
| `knowledge.py` | 6 | Empty placeholder |
| `service_registry.py.bak` | - | Backup |

### `tools/` (9 files)
| File | Lines | Purpose |
|------|-------|---------|
| `__init__.py` | 1 | Empty |
| `base_tool.py` | 6 | Abstract tool interface |
| `calculator.py` | 14 | eval()-based math expression solver |
| `python_executor.py` | 24 | exec() sandbox with stdout capture |
| `file_tool.py` | 69 | File CRUD (read/write/list/exists/backup/append/delete/copy/move/replace) |
| `memory_tool.py` | 28 | Remember/recall via MemoryService |
| `internet_tool.py` | 24 | Web search via requests to DuckDuckGo |
| `tool_registry.py` | 27 | Registers 5 tools (Calculator, PythonExecutor, FileTool, MemoryTool, InternetTool) |
| `file_tool.py.bak`, `file_tool.py.mission6.bak` | - | Backups |

### `knowledge/` (10 files)
| File | Lines | Purpose |
|------|-------|---------|
| `__init__.py` | 2 | Exports KnowledgeEngine |
| `engine.py` | 72 | Orchestrates document reading, symbol indexing, relationship building, graph |
| `documents.py` | 60 | Scans docs/ and spec/ for .md/.rst/.txt |
| `parser.py` | 111 | AST-based Python symbol + import extraction |
| `symbols.py` | 36 | Module/class/function symbol indexing |
| `relationships.py` | 46 | Import relationships + package hierarchy |
| `graph.py` | 43 | Node/edge knowledge graph construction |
| `index.py` | 15 | Lookup indexes for documents, symbols, relationships |
| `search.py` | 57 | Search symbols (prioritized), documents (by match count), relationships |
| `report.py` | 20 | KnowledgeReport dataclass |

### `workspace/` (9 files)
| File | Lines | Purpose |
|------|-------|---------|
| `__init__.py` | 2 | Exports Workspace |
| `workspace.py` | 39 | Public API: root detection, scan, report |
| `scanner.py` | 56 | Root detection (.git/pyproject.toml markers), recursive scan with skip dirs |
| `analyzer.py` | 83 | Read README, detect packages, count modules/tests, summarize deps |
| `tree.py` | 60 | Hierarchical directory tree builder |
| `project.py` | 44 | ProjectInfo + WorkspaceReport dataclasses |
| `summary.py` | 15 | Compact report summary |
| `git.py` | 28 | Read-only Git info (is_repository, current_branch) |
| `dependency.py` | 59 | Parse requirements.txt and pyproject.toml |

### `models/` (4 files)
| File | Lines | Purpose |
|------|-------|---------|
| `__init__.py` | 1 | Empty |
| `registry.py` | 18 | ModelRegistry wrapping settings.MODELS |
| `selector.py` | 28 | Plan keyword → model role → model name |
| `test_models.py` | - | Tests |

### `builder/` (6 files)
| File | Lines | Purpose |
|------|-------|---------|
| `__init__.py` | 1 | Exports Builder |
| `engine.py` | 10 | Builder (create_module, verify, doctor) |
| `generator.py` | 4 | Placeholder |
| `mission.py` | 4 | Placeholder |
| `registry.py` | 1 | Empty MISSIONS dict |
| `templates.py` | 1 | Empty TEMPLATES dict |

### `cli/` (3 files)
| File | Lines | Purpose |
|------|-------|---------|
| `__init__.py` | 1 | Empty |
| `main.py` | 19 | `amalgam <command>` dispatcher |
| `commands.py` | 8 | Maps verify/doctor to Builder methods |

### `tests/` (71 files)
Test files count: **70** (one `__init__.py` + 70 test files)

Coverage includes: action_registry, agent_context, agent_registry, autonomous_executor, autonomous_regression, base_agent, brain, calculator, capability_router, chief_agent, config, dependency_resolver, diagnostics, engineer_agent, evaluator, execution_memory, executor, file_tool, fleet_manager, goal, goal_regression, intent, internet_tool, kernel, knowledge (documents, engine, graph, index, parser, relationships, search, symbols), logger, memory (regression, tool), messaging, mission (core, epic, graph), models, ollama_service, orchestrator_agent, pipeline, planner, planner_agent, python_executor, reflection, registry, research_agent, retry_manager, reviewer_agent, scheduler, service_registry, shared_context, task, task_queue, tool_router, version, work_pool, workspace (analyzer, dependency, git, scanner, tree, workspace)

### `docs/` (15 files)
- `Architecture.md` (102 lines) — Canonical flow, infrastructure, workspace engine
- `Changelog.md` (18 lines) — v0.3.0 and Mission 3 changelog
- `Development.md` (42 lines) — Guardrails, config, logging, diagnostics guidelines
- `Requirements.md` (0 lines) — Empty
- `Roadmap.md` (0 lines) — Empty
- `docs/missions/` — 12 files (MISSION_6.6 to MISSION_7_8), all **empty**

### `storage/` (4 items)
- `memory/memory.json` — Execution memory records (~2000 lines)
- `cache/`, `embeddings/`, `knowledge/` — Empty

### Other directories (all **empty**)
`plugins/`, `modules/`, `apps/`, `voice/`, `vision/`, `scripts/`, `data/`, `assets/`, `logs/`

### Config files
- `.claude/settings.local.json` — Allows pytest and git reset permissions

---

## 4. Architecture Summary

### Multi-Agent Pipeline
```
OrchestratorAgent
  → PlannerAgent (creates Goal + plan)
  → ResearchAgent (gathers memory/files/project/web context)
  → ReviewerAgent (validates plan quality and safety)
  → EngineerAgent (executes via AutonomousExecutor)
```

### Autonomous Goal Lifecycle
```
Goal → ANALYZING → PLANNING → READY → RUNNING → VERIFYING → COMPLETED
                              ↓ (failure)
                          REFLECTING → RETRY → RUNNING
                              ↓
                          REPLANNING → RUNNING
                              ↓
                          FAILED
```

### Module Dependency DAG (no circular deps)
```
agents → brain → kernel → (services, tools, models) → config
services → (workspace, knowledge) → (no back-edges)
```

### Security Audit Status (MISSION_6.4.3)
- **3 Critical**: exec()/eval() on unsanitized input, path traversal in FileTool
- **6 High**: Thread safety, non-cancellable timeouts, prompt injection, file overwrite
- **6 Medium**: Pause→FAILED bug, stale cache, no file locking, fragile detection
- **5 Low**: Inconsistent API, missing validation, dead code, fragile planning
- **1 State Machine Bug**: Pause incorrectly forces FAILED
- **No circular dependencies** in ~130+ module import graph

---

**Total files indexed:** 130+ Python source files + 15 docs + 70 tests + config/data files  
**Total lines read:** ~12,000+ lines of source code  
**Total project size:** ~47 directories, ~200+ files
