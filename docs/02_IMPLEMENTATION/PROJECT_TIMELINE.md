# PROJECT_TIMELINE.md

## AMALGAM — Chronological Engineering History

**Document type:** Knowledge Recovery Pass 1  
**Source:** AMALGAM_FULL_CONVERSATION.md (158,112 lines, exported 7/8/2026 20:11:03)  
**Conversation span:** 6/26/2026 – 7/8/2026 (12 days)  
**Rule:** Never infer. Never hallucinate. Quote original wording whenever possible.  
**Note on post-conversation missions:** HISTORY.json in `.amalgam-core/` records M7.1.7 (772 tests, 7/6/2026), M7.1.8 (806 tests), and M7.2 ("ChiefAgent orchestration", in_progress as of 7/8/2026). These missions are documented from the repository artefacts; they do not appear in the exported conversation and may have been completed in a separate session or a later portion of the same session not included in the export.

---

---

## PRE-PROJECT SETUP (Day 0 — 6/26/2026, evening)

**Sequence:** 0  
**Date:** 6/26/2026, ~9:50 PM – 1:47 AM (6/27)

### What happened

User (Ankit) began with a Windows environment setup session. No AMALGAM code was written during this period. The following events occurred in order:

- **Git installed** — resolved PATH issue by adding `C:\Program Files\Git\cmd`.
- **PrivateGPT attempted** — cloned `zylon-ai/private-gpt`, encountered Poetry dependency failure (`private-gpt[media-core]` conflict). Abandoned.
- **Python environment** — Python 3.11.9 (x64) installed alongside existing Python 3.14.3.
- **Ollama installed** — confirmed with `ollama --version 0.30.10`.
- **Models downloaded** — `qwen3:8b` (5.2 GB), `deepseek-r1:8b`, `llama3.1:8b`, `qwen2.5-coder:7b`, `gemma3:4b` pulled via `ollama pull`.
- **Open WebUI installed** — Docker Desktop installed, Open WebUI container deployed at `http://localhost:3000`. First successful chat with `qwen3:8b`.
- **Project renamed** — User originally called the project "Juju AI", then considered "ORION", "STU AI", and finally settled on **"AMALGAM"** (~1:47 AM).

**Original naming rationale (quoted):** AI architect rated "Amalgam AI" 9.5/10, stating: *"'Amalgam' means a combination of many different things into one unified whole. That matches your vision almost perfectly: Multiple LLMs, Memory, Knowledge, Internet, Voice, Vision, Automation, Agents, Image generation — All combined into one AI."*

**User's stated goal (quoted):** *"my motive is to have own my own ai with existing data an ai models have in 2026 till date and after installation i can do anything with my model or ai"*

**Completion status:** Complete (pre-project environment ready)  
**Next planned:** Day 1 — Begin AMALGAM architecture design

---

## MILESTONE 1 — Project Foundation & Architecture Design (Day 1 — 6/27/2026, morning)

**Sequence:** 1  
**Date:** 6/27/2026, ~10:27 AM – 11:00 AM  
**Mission / Sub-mission:** Not yet numbered. "Day 1 of AMALGAM."

### Objective

Design the complete project structure before writing any code. Define the architecture, folder layout, and core principles.

### Why it was started

User had selected the name "AMALGAM" overnight. The AI architect proposed spending Day 1 as engineers: *"We are not downloading anything. We're going to become architects."*

### Major architecture decision

Architecture defined as **"Personal AI Platform"** (not a chatbot, not an LLM wrapper):  
*"AMALGAM is a Personal AI Platform that orchestrates multiple AI models, tools, memory, automation, and knowledge into a single intelligent system."*

**Core principles established:**
1. Architecture before implementation
2. Reuse before creation
3. Layer separation (one responsibility per layer)
4. Composition over inheritance
5. Deterministic behaviour
6. Small incremental changes
7. Backward compatibility
8. Mission-first development
9. Test before completion
10. Repository is the source of truth

**Folder structure created:**
```
AMALGAM/
├── apps/, core/, services/, modules/, data/, config/, docs/, scripts/, tests/, assets/
```

### Files introduced

- `C:\Users\ankit\Projects\AMALGAM\` — project root created
- `.git/` — `git init` run; first Git repository
- `docs/Architecture.md`, `docs/Changelog.md`, `docs/Development.md`, `docs/Requirements.md`, `docs/Roadmap.md` — created empty
- `README.md`, `.gitignore`, `LICENSE`, `requirements.txt`, `pyproject.toml` — created empty

### Tests added

None (design phase only).

### Completion status

Complete. Folder structure confirmed via `tree /F`.

### Next planned mission

Genesis-1: persistent memory engine.

---

## MILESTONE 2 — Genesis-1: Core Architecture and Persistent Memory (6/27/2026)

**Sequence:** 2  
**Date:** 6/27/2026, ~10:53 AM – 11:18 AM  
**Mission / Sub-mission:** Genesis-1

### Objective

Build the first working feature: a persistent memory engine that survives across sessions, plus the skeleton orchestration pipeline.

### Why it was started

After the architecture design, the AI architect directed: *"We will create main.py and the memory engine first, because persistent memory is the difference between a chatbot and an AI assistant."*

### Major implementation

- `core/orchestrator.py` — `Orchestrator` class with `start()`, `process()` handling `remember key=value` and `recall key` commands.
- `services/memory.py` — `MemoryService` with `remember(key, value)`, `recall(key)`, `show_all()`, `load()`, `save()`. Persists to JSON on disk.
- `data/memory.json` — JSON key-value store, initially `{}`.
- Remaining skeleton files created: `core/router.py`, `core/planner.py`, `core/session.py`, `core/__init__.py`, `services/knowledge.py`, `services/internet.py`, `services/llm.py`, `main.py`.

### Major architecture decision

Memory storage path set to `data/memory.json`. (Later migrated to `storage/memory/memory.json` during Genesis-4 cleanup.)

### Tests added

None at this milestone; memory was tested manually via `main.py`.

**Test confirmation (quoted from session):**
```
You: remember name=Ankit
Stored: name
[exit and restart]
You: recall name
Ankit
```

### Completion status

Complete. Persistent memory working across sessions.

### Git commits

- `"Genesis-1: Core architecture and persistent memory"` — 26 files, 164 insertions, hash `71f74aa`
- `"Genesis-1.1: Add .gitignore and remove Python cache files"` — hash `85216fe`

### Next planned mission

Genesis-2: Connect AMALGAM to Ollama for real LLM responses.

---

## MILESTONE 3 — Genesis-2: Ollama Integration (6/27/2026)

**Sequence:** 3  
**Date:** 6/27/2026, ~11:20 AM – 11:30 AM  
**Mission / Sub-mission:** Genesis-2

### Objective

Connect AMALGAM's `LLMService` to the local Ollama API so that AMALGAM can generate real AI responses instead of placeholder output.

### Why it was started

The Orchestrator's `process()` method printed `f"Received: {user_input}"` rather than generating a real AI answer. The next logical step was wiring the LLM layer.

### Major implementation

- `pip install ollama 0.6.2` — Ollama Python SDK installed.
- `services/llm.py` — `LLMService` updated with `ask(prompt, model)` calling `ollama.Client(host="http://127.0.0.1:11434").chat(...)`.
- `core/orchestrator.py` — `Orchestrator` updated to call `LLMService.ask()` for non-memory inputs.

### Major architecture decision

**Ollama Python SDK 0.6.2 returns Pydantic objects, not plain dicts.** Access pattern is `response.message.content`, not `response["message"]["content"]`. This was discovered empirically when `response["message"]` raised `KeyError`.

The final working client instantiation:
```python
self.client = ollama.Client(host="http://127.0.0.1:11434")
result = self.client.chat(model=model, messages=[{"role": "user", "content": prompt}])
return result.message.content
```

### Tests added

None. Verified manually:
```
You: What is Python?
[Model Selected: qwen3:8b]
AMALGAM:
Python is a high-level, interpreted programming language...
```

### Completion status

Complete. First real AI response through AMALGAM pipeline confirmed.

### Git commit

`"Genesis-2: Connect AMALGAM to Ollama"`

### Next planned mission

Genesis-3: Automatic model routing based on task type.

---

## MILESTONE 4 — Genesis-3: Automatic Model Routing (6/27/2026)

**Sequence:** 4  
**Date:** 6/27/2026, ~12:08 PM – 12:15 PM  
**Mission / Sub-mission:** Genesis-3

### Objective

Build a model router that automatically selects the best local model based on the type of user request, so the user no longer needs to manually choose a model.

### Why it was started

AMALGAM always used `qwen3:8b` regardless of input. The AI architect noted: *"Instead of asking 'Which AI is better?' you'll ask 'Which AI should I use for this task?'"*

### Major implementation

- `config/models.py` — `MODELS` dict: `{"general": "qwen3:8b", "coding": "qwen2.5-coder:7b", "reasoning": "deepseek-r1:8b", "creative": "llama3.1:8b", "fast": "gemma3:4b"}`.
- `core/router.py` — `Router.choose_model(prompt)` using keyword lists for coding (`"python"`, `"code"`, etc.), reasoning (`"math"`, `"equation"`, etc.), creative (`"poem"`, `"story"`, etc.). Returns general model as fallback.
- `core/orchestrator.py` — `process()` updated to call `self.router.choose_model(user_input)` before calling `self.llm.ask()`.

### Major architecture decision

Keyword-based routing acknowledged as a temporary "Version 1" approach. Intent: replace with AI-based classification in a later mission. Quoted: *"I actually don't want to fix this with more keywords. I want to redesign Genesis-3."*

### Tests added

None. Verified manually:
```
You: Write Python code to print Hello World
[Model Selected: qwen2.5-coder:7b]
```

### Completion status

Complete.

### Git commit

`"Genesis-3: Automatic model routing"`

### Next planned mission

Genesis-4: Pipeline architecture expansion (preprocessor, intent, planner, tool router sub-modules).

---

## MILESTONE 5 — Genesis-4: Pipeline Architecture Expansion (6/27/2026)

**Sequence:** 5  
**Date:** 6/27/2026, ~12:17 PM – 12:45 PM  
**Mission / Sub-mission:** Genesis-4

### Objective

Expand the `core/` module into a proper sub-module pipeline: Preprocessor → Intent Analyzer → Planner → Tool Router. Establish modular architecture inside the core layer.

### Why it was started

The AI architect observed that AMALGAM was still a monolithic `Orchestrator`. The long-term architecture required clear responsibility separation: *"The LLM is not the center anymore. The Orchestrator is."*

### Major implementation

**New sub-modules created in `core/`:**
- `core/pipeline/pipeline.py` — `Pipeline.run(text)` chains Preprocessor.
- `core/preprocessor/preprocessor.py` — `Preprocessor.process(text)`: strips, lowercases, removes newlines.
- `core/intent/intent.py` — `IntentAnalyzer.analyze(text)`: keyword-based classification → `"coding"`, `"math"`, `"memory"`, `"creative"`, `"web"`, `"general"`.
- `core/planner/planner.py` — `Planner.plan(intent)`: maps intent → action string (`"use_coder"`, `"use_calculator"`, etc.).
- `core/tools/tool_router.py` — `ToolRouter.route(plan)`: maps action → model name or tool name.

**Project cleanup (sub-phase):**
- `tests/` directory created; all `test_*.py` files moved there.
- `data/memory.json` moved to `storage/memory/memory.json`.
- `MemoryService` path updated to `storage/memory/memory.json`.
- New directories added: `agents/`, `models/`, `tools/`, `knowledge/`, `voice/`, `vision/`, `plugins/`, `logs/`, `storage/cache/`, `storage/embeddings/`.

### Major architecture decision

Separation of concerns established:
- Preprocessor → normalises input
- Intent Analyzer → classifies purpose
- Planner → decides action
- Tool Router → selects model/tool

Tests for pipeline, intent, planner, and tool router created in `tests/`.

### Tests added

- `tests/test_pipeline.py`
- `tests/test_intent.py`
- `tests/test_planner.py`
- `tests/test_tool_router.py`

### Completion status

Complete.

### Git commit

`"Genesis-4: Project cleanup and storage architecture"`

### Next planned mission

Genesis-5: Rename `core/` → `brain/`, `engine/` → `kernel/`; introduce KernelState, OllamaService, ModelRegistry.

---

## MILESTONE 6 — Genesis-5: Kernel Architecture + AI OS Identity (6/27/2026, evening)

**Sequence:** 6  
**Date:** 6/27/2026, ~8:03 PM – 9:05 PM  
**Mission / Sub-mission:** Genesis-5

### Objective

Rename the core infrastructure to reflect the "AI Operating System" identity. Establish the Kernel as the execution layer, the Brain as the intelligence layer. Introduce dynamic boot diagnostics.

### Why it was started

The AI architect decided: *"I want AMALGAM to have a kernel, just like Windows or Linux."* The existing `core/` and `engine/` names were replaced with `brain/` and `kernel/` respectively to communicate purpose rather than implementation. Quote: *"brain/ → Thinks. kernel/ → Executes."*

### Major implementation

**Architecture renames:**
- `core/` → `brain/`
- All `from core.` imports → `from brain.`

**New files:**
- `kernel/state.py` — `KernelState` dataclass: `version`, `status`, `models_loaded`, `memory_loaded`, `tools_loaded`, `services_loaded`, `.ready()`.
- `kernel/executor.py` — `Executor.boot()` prints AMALGAM OS startup banner with version, environment, Python version, OS, kernel status, model/service counts.
- `services/ollama_service.py` — `OllamaService`: `list_models()` (returns `[model.model for model in response.models]`), `is_running()`, `count_models()`.
- `interfaces/` folder — `llm.py`, `memory.py`, `tool.py`, `agent.py`, `knowledge.py`, `__init__.py` created (interface contracts for future use).

**Key API discovery:** Ollama Python SDK `0.6.2` returns `ListResponse` with `.models` attribute (Pydantic objects); model name accessed via `model.model`, not `model["name"]`.

### Major architecture decision

**Architecture declared "frozen" at 9.9/10.** Architecture diagram:
```
agents/ → brain/ → kernel/ → services/ tools/ models/ → config/
```

### Tests added

`tests/test_ollama_service.py`, `tests/test_kernel.py` (implicit from manual testing; Codex later formalised these).

### Completion status

Complete.

### Git commit

`"Genesis-5: Kernel Boot + OllamaService + ModelRegistry"` (inferred from session context; exact hash not specified in conversation).

### Next planned mission

Genesis-6: Task system — replace string-based dispatch with `Task` objects. Introduce `Dispatcher`.

---

## MILESTONE 7 — Genesis-6: Task System and Dispatcher (6/27/2026 – 6/28/2026, early AM)

**Sequence:** 7  
**Date:** 6/27/2026, ~8:37 PM – 6/28/2026, ~1:00 AM  
**Mission / Sub-mission:** Genesis-6 (Sprints 1–6)

### Objective

Replace string-based kernel dispatch with a typed `Task` object system. Introduce the `Dispatcher` as the single execution router. Remove `Orchestrator` from the execution path.

### Why it was started

The AI architect noted: *"The LLM is not the center anymore. The Orchestrator is."* But after review, the solution was to make `Brain` + `Kernel` + `Dispatcher` the correct chain, and reduce `Orchestrator` to a legacy stub.

### Major implementation

**Sprint 1 — Task object (`kernel/task.py`):**
```python
class Task:
    intent: str, action: str, model: str = None, tool: str = None, data = None
```

**Sprint 2 — Dispatcher (`kernel/dispatcher.py`):**
- `Dispatcher.dispatch(task)` routes by `task.action` field.

**Sprint 3 — Calculator Tool (`tools/calculator.py`):**
- First non-LLM execution. `Calculator.calculate(expr)` uses `eval()`.
- Dispatcher routes `action="calculate"` → `Calculator`.

**Sprint 4 — Intent Analyzer upgraded:**
- Removed `"python"` as sole coding trigger.
- Added `coding_phrases` list: `"write code"`, `"generate code"`, `"debug"`, etc.

**Sprint 5 — Brain integration (`brain/brain.py`):**
- `Brain.think(user_input)` = `IntentAnalyzer.detect()` + `Planner.create_task()`.
- `Planner` updated to use `ModelRegistry`.

**Sprint 6 — `main.py` simplified:**
- `Orchestrator` removed from execution path.
- Main loop: `brain.think() → kernel.execute()`.

### Files introduced

`kernel/task.py`, `kernel/dispatcher.py`, `tools/calculator.py`, `brain/brain.py`.

### Tests added

`tests/test_task.py`, `tests/test_calculator.py`, `tests/test_brain.py`.

### Completion status

Complete. First end-to-end pipeline without Orchestrator verified.

### Next planned mission

Genesis-7: Add native tools — PythonExecutor, FileTool, ToolRegistry, ServiceRegistry.

---

## MILESTONE 8 — Genesis-7: Native Tools + Registries (6/28/2026, early AM)

**Sequence:** 8  
**Date:** 6/28/2026, ~1:00 AM – 1:10 AM  
**Mission / Sub-mission:** Genesis-7 (Sprints 1–4)

### Objective

Add three native tools (PythonExecutor, FileTool, MemoryTool) and formalise their registration through ToolRegistry and ServiceRegistry.

### Why it was started

AMALGAM needed native capabilities beyond the LLM. The Calculator proved the pattern. Extension to Python execution, file access, and structured memory lookups was the immediate next step.

### Major implementation

**Sprint 1 — PythonExecutor (`tools/python_executor.py`):**
- `execute(code)` uses `exec()` + `contextlib.redirect_stdout()`.

**Sprint 2 — FileTool (`tools/file_tool.py`):**
- `read(path)`, `write(path, content)`, `list_dir(path)` using `pathlib.Path`.

**Sprint 3 — ToolRegistry (`tools/tool_registry.py`):**
- Eagerly instantiates: `{"calculator": Calculator(), "python": PythonExecutor(), "files": FileTool()}`.

**Sprint 4 — ServiceRegistry (`services/service_registry.py`):**
- Eagerly instantiates: `{"llm": LLMService(), "memory": MemoryService(), "ollama": OllamaService()}`.

### Files introduced

`tools/python_executor.py`, `tools/file_tool.py`, `tools/tool_registry.py`, `services/service_registry.py`.

### Tests added

`tests/test_python_executor.py`, `tests/test_file_tool.py`, `tests/test_registry.py`, `tests/test_service_registry.py`.

### Completion status

Complete.

### Next planned mission

Genesis-8: BaseTool, MemoryTool, ActionRegistry, InternetTool.

---

## MILESTONE 9 — Genesis-8: ActionRegistry, MemoryTool, InternetTool + Codex Integration (6/28/2026)

**Sequence:** 9  
**Date:** 6/28/2026, ~1:14 AM – 2:17 AM  
**Mission / Sub-mission:** Genesis-8 (Sprints 1–5)

### Objective

Introduce BaseTool base class; add MemoryTool and InternetTool; introduce ActionRegistry to eliminate the Dispatcher `if-chain`; adopt Codex as the implementation engine.

### Why it was started

The Dispatcher contained growing `if task.action == ...` chains. The AI architect designed ActionRegistry to make adding new capabilities a one-line registration, without touching the Dispatcher.

### Major implementation

**Sprint 1 — BaseTool:**
- `tools/base_tool.py` — `BaseTool` with `execute(*args, **kwargs)`. Calculator, PythonExecutor, FileTool updated to inherit it.

**Sprint 2 — MemoryTool (`tools/memory_tool.py`):**
- Wraps `MemoryService`: `remember(key, value)`, `recall(key)`.
- **Bug found:** `MemoryTool` was missing from `ToolRegistry` (import not added). Root-caused by running `python -c "from tools.tool_registry import ToolRegistry; r=ToolRegistry(); print(r.list_tools())"` — confirmed via runtime, not code inspection.

**Sprint 3 — ActionRegistry (`kernel/action_registry.py`):**
- Maps action string → `(tool_name, method_name)` tuple.
- Dispatcher refactored to use ActionRegistry: `route = self.actions.get(action); tool = self.tools.get(tool_name); method = getattr(tool, method_name)`.

**Sprint 4 — InternetTool (`tools/internet_tool.py`):**
- `search(query)` using `requests` library. `pip install requests 2.34.2` (urllib3, charset_normalizer installed).

**Sprint 5 — Codex integration:**
- User installed OpenAI Codex desktop app.
- AMALGAM project attached to Codex.
- First Codex prompt: architectural audit of 70+ files.
- Codex engineering report produced (graded 8.8/10).

**Codex report findings:** 5 duplicate routing mechanisms, stale tests (print-only smoke scripts), hardcoded values, empty docs, missing Dispatcher guardrails.

**AI architect disagreements with Codex:** Retained `EventBus`, `Scheduler`, `Permissions` (flagged as dead by Codex) for future use.

### Files introduced

`tools/base_tool.py`, `tools/memory_tool.py`, `kernel/action_registry.py`, `tools/internet_tool.py`.

### Tests added

`tests/test_memory_tool.py`, `tests/test_action_registry.py`, `tests/test_internet_tool.py`.

### Completion status

Complete. Codex integration established. Codex quota exhausted at ~2:14 AM.

### Key decision

**Official development workflow established:**  
`User (Founder) → ChatGPT (Chief Architect) → Codex (Implementation) → Testing → Git`

### Next planned mission

Mission 1 (v0.3 plan): Foundation Stabilization — formally handed to Codex.

---

## MILESTONE 10 — v0.3 Mission 1: Foundation Stabilization (6/28/2026, ~9:25 AM)

**Sequence:** 10  
**Date:** 6/28/2026, ~9:25 AM  
**Mission / Sub-mission:** Mission 1 (v0.3 series)

### Objective

Perform a complete stabilization pass on the codebase: dependency metadata, package init files, test conversion, memory robustness, Dispatcher guardrails, LLM failure handling, CLI error boundary.

### Why it was started

Codex's own architectural audit identified multiple classes of instability. The AI architect defined this as the prerequisite for all future missions: *"A task is not complete until tests pass, existing tests continue passing, and no regressions exist."*

### Major implementation

Codex executed the full stabilization pass in one session after quota reset:

- `requirements.txt`, `pyproject.toml` — populated with runtime and test dependencies (`ollama`, `requests`, `pytest`).
- **8 `__init__.py` files added** — `brain/intent/`, `brain/planner/`, `brain/pipeline/`, `brain/preprocessor/`, `brain/tools/`, `config/`, `models/`, `tools/`.
- `kernel/executor.py` — hardcoded boot counts replaced with dynamic counts from registries.
- `kernel/dispatcher.py` — guardrails added: malformed tasks, unknown actions, missing tools, missing methods, bad memory payloads, service exceptions.
- `services/memory.py` — path made project-relative; `storage/memory/` directory auto-created.
- `services/llm.py`, `services/ollama_service.py` — Ollama failure handling; readable error messages instead of crashes.
- `main.py` — exception boundary around the CLI loop (no longer crashes on runtime errors).
- `tools/internet_tool.py` — URL encoding added for search queries.
- **18 test files converted** from smoke scripts (`print(...)` only) to assertion-based pytest tests.

### Tests added

18 test files updated/converted. 4 new test files: `tests/test_config.py` (partial — Mission 2 added full config tests), `tests/test_executor.py`, `tests/test_dispatcher.py`, and others.

**Test result (quoted):** `"46 passed in 12.01s"`

### Completion status

Complete. Tagged `v0.3.0-alpha`.

### Git commit

`"Mission 1: Foundation Stabilization"`  
**Tag:** `v0.3.0-alpha`

**AI Architect rating:** 9.6/10

### Next planned mission

Mission 2: Core Infrastructure (Logging, Configuration, Diagnostics, Versioning). Codename: "Project Atlas."

---

## MILESTONE 11 — Product Definition & Vision Consolidation (6/29/2026, ~9:17–9:45 AM)

**Sequence:** 11  
**Date:** 6/29/2026, ~9:17 AM – 9:43 AM  
**Mission / Sub-mission:** Not a code mission. Product architecture session.

### Objective

Define AMALGAM's product identity, competitive positioning, slogan, target audience, and permanent roadmap before continuing implementation.

### Why it was started

After Mission 1 stabilization, the AI architect paused to establish permanent product direction before adding more features.

### Key decisions made

- **Slogan:** `"AMALGAM OS — The operating system that turns AI into action."`
- **Target user (Phase 1):** Developers and technical power users.
- **Vision statement:** *"Build the world's best local-first AI Operating System."*
- **Architecture philosophy (four pillars):**
  - Workspace → "What exists?"
  - Knowledge → "How is it connected?"
  - Memory → "What happened before?"
  - Reasoning → "What should happen next?"
- **RFC system proposed** for major future features.
- **ADR (Architecture Decision Record) system proposed** as permanent documentation practice.
- **ToolFK.com research** → inspired "Skill Engine" concept (Skills combine tools into outcomes); this concept was proposed but deferred.
- **Provider Framework concept approved as future Epic** (Telegram storage idea from user reframed as `providers/` with `TelegramStorageProvider`, `GoogleDriveProvider`, `LocalStorageProvider`, `S3Provider`).
- **Permanent development rule established:** *"Build → Integrate → Test → Freeze → Next subsystem. Every new subsystem must become usable before the next begins."*

### Files introduced

None (design session).

### Completion status

Complete (session goal met).

### Next planned mission

Mission 2: Core Infrastructure.

---

## MILESTONE 12 — v0.3 Mission 2: Core Infrastructure (6/29/2026, ~9:43 AM)

**Sequence:** 12  
**Date:** 6/29/2026, ~9:43 AM – 9:54 AM  
**Mission / Sub-mission:** Mission 2 (v0.3 series). Codename: "Project Atlas."

### Objective

Build the infrastructure that every future feature depends on: centralized configuration, structured logging, diagnostics engine, version management.

### Why it was started

Before adding capabilities, the AI architect declared: *"Build infrastructure only. Do not add user-facing AI capabilities."*

### Major implementation

Implemented by Codex in one pass:

**Epic 2.1 — Configuration:**
- `config/settings.py` — centralized runtime settings (`APP_VERSION`, `OLLAMA_HOST`, `MEMORY_PATH`, `LOG_LEVEL`, `REQUEST_TIMEOUT`, etc.).
- `config/constants.py` — immutable constants (action names, tool names, service names, status strings).
- `config/version.py` — runtime version metadata (version, build type, environment).
- All modules updated to consume settings/constants instead of hardcoded values.

**Epic 2.2 — Logging:**
- `services/logger.py` — reusable structured logger with `DEBUG`, `INFO`, `WARNING`, `ERROR`.
- `kernel/executor.py`, `kernel/dispatcher.py`, `main.py` — internal events now logged via structured logger.
- Intentional: direct `print()` preserved for user-facing output (boot display, AI responses).

**Epic 2.3 — Diagnostics:**
- `services/diagnostics.py` — `DiagnosticsService` with structured health checks: configuration, memory, tool registry, service registry, Ollama availability, storage directories.

**Epic 2.4 — Boot display:**
- `kernel/executor.py` — boot now shows: app version, build type, environment, Python version, OS.
- `kernel/state.py` — version/status sourced from `config/settings`.

**Documentation updated:** `docs/Architecture.md`, `docs/Development.md`, `docs/Changelog.md`.

### Tests added

`tests/test_config.py`, `tests/test_version.py`, `tests/test_logger.py`, `tests/test_diagnostics.py`.

**Test result (quoted):** `"53 passed in 12.74s"`

### Completion status

Complete.

**AI Architect rating:** 9.9/10

### Next planned mission

Mission 3: Workspace Engine.

---

## MILESTONE 13 — v0.3 Mission 3: Workspace Engine (6/29/2026, ~10:03 AM)

**Sequence:** 13  
**Date:** 6/29/2026, ~10:03 AM  
**Mission / Sub-mission:** Mission 3 (v0.3 series)

### Objective

Create a new read-only `workspace/` package that gives AMALGAM a structured understanding of the current project: root detection, file scanning, package identification, Git info, dependency parsing, summary.

### Why it was started

The AI architect argued: *"Before an AI can use the world, it must understand the project it is standing in."* The Workspace Engine provides deterministic, LLM-free facts about the local project. It answers: "What exists?"

### Major implementation

Codex created the entire `workspace/` package in one pass:

- `workspace/workspace.py` — `Workspace(start_path)` public API: `report()` → `WorkspaceReport`, `scan()` → list of paths, `as_dict()`.
- `workspace/scanner.py` — Directory scanning, ignores `__pycache__`, `.git`.
- `workspace/analyzer.py` — Metadata analysis.
- `workspace/project.py` — `WorkspaceReport` dataclass with `project.root`, `project.python_packages`, etc.
- `workspace/tree.py` — Directory tree building.
- `workspace/dependency.py` — Parses `requirements.txt` and `pyproject.toml`.
- `workspace/git.py` — Detects Git repository, reads current branch from `.git/HEAD` (no subprocess).
- `workspace/summary.py` — Summary report generation.
- `workspace/__init__.py` — `from workspace.workspace import Workspace`.

**Architecture constraint:** Workspace is read-only and never modifies files. It does not enter the Brain/Planner/Kernel/Dispatcher execution path.

### Tests added

`tests/test_workspace.py`, `tests/test_workspace_scanner.py`, `tests/test_workspace_analyzer.py`, `tests/test_workspace_dependency.py`, `tests/test_workspace_git.py`, `tests/test_workspace_tree.py`.

**Test result (quoted):** `"64 passed in 12.00s"`

**AI Architect rating:** 10/10

### Completion status

Complete.

### Next planned mission

Mission 4: Knowledge Engine (deterministic code intelligence via Python `ast` module).

---

## MILESTONE 14 — v0.3 Mission 4: Knowledge Engine (6/29/2026, ~10:08–10:38 AM)

**Sequence:** 14  
**Date:** 6/29/2026, ~10:08 AM – 10:38 AM  
**Mission / Sub-mission:** Mission 4 (v0.3 series). Codename: "Project Athena."

### Objective

Build a deterministic, LLM-free Knowledge Engine that understands code relationships: symbol index, import graph, document reader, search APIs. Answers: "How is the project connected?"

### Why it was started

Workspace provides facts. Knowledge provides relationships. The AI architect stated: *"Workspace = Eyes. Knowledge = Brain."* Without Knowledge, AMALGAM cannot answer questions like *"Where is Dispatcher defined?"* or *"Which files import Workspace?"*

### Major architecture decision

**No LLMs, no embeddings, no vector databases.** The Knowledge Engine uses Python's built-in `ast` module for deterministic, reproducible extraction. Quote: *"Pure engineering. We first understand the project deterministically. Semantic AI search comes later."*

### Major implementation

Codex created the `knowledge/` package (quota hit mid-session; manually completed):

- `knowledge/engine.py` — `KnowledgeEngine(start_path)`. `build()` → `KnowledgeReport`. `search_symbols(query)`, `search_documents(query)`, `search_relationships(query)`.
- `knowledge/parser.py` — `PythonParser.parse_file(root, path)` using `ast.parse()`. Extracts: classes, functions, methods, imports, module names.
- `knowledge/symbols.py` — `SymbolIndex.build(root, paths)` → list of `{name, qualified_name, kind, module, line}` dicts.
- `knowledge/relationships.py` — `RelationshipBuilder.build(root, paths, packages)` → import and package hierarchy edges.
- `knowledge/graph.py` — `KnowledgeGraph.build(symbols, relationships)` → `{nodes, edges}`.
- `knowledge/index.py` — `KnowledgeIndex.build(docs, symbols, relationships)` → lookup maps.
- `knowledge/search.py` — `KnowledgeSearch`: `search_symbols`, `search_documents`, `search_relationships`. **Bug fixed:** `search_symbols` sorted results by priority `class(0) > function(1) > module(2)` to prevent module entries appearing before class entries.
- `knowledge/documents.py` — `DocumentReader.read(root)` scans `docs/`, `spec/`, root `README.*`.
- `knowledge/report.py` — `KnowledgeReport` dataclass.
- `knowledge/__init__.py` — `from knowledge.engine import KnowledgeEngine`.

**Bug found and fixed during this milestone:**  
`test_knowledge_engine_exposes_search_apis` failed: `search_symbols("Service")` returned `"pkg.service"` (module) instead of `"pkg.service.Service"` (class). Root cause: `SymbolIndex` adds module entries before class entries; search was returning the module first. Fix: sort by `priority = {"class": 0, "function": 1, "module": 2}`.

### Tests added

8 test files: `tests/test_knowledge_documents.py`, `tests/test_knowledge_engine.py`, `tests/test_knowledge_graph.py`, `tests/test_knowledge_index.py`, `tests/test_knowledge_parser.py`, `tests/test_knowledge_relationships.py`, `tests/test_knowledge_search.py`, `tests/test_knowledge_symbols.py`.

**Test result (quoted):** `"73 passed in 11.82s"`

**AI Architect rating:** Fully approved.

### Completion status

Complete.

### Next planned mission

Mission 5: Integration — expose all built subsystems (Memory, Files, Internet, Python, Workspace, Knowledge) through the execution pipeline.

---

## MILESTONE 15 — Architecture v1.0 Frozen (6/29/2026, ~11:10 AM)

**Sequence:** 15  
**Date:** 6/29/2026, ~11:10 AM  
**Mission / Sub-mission:** Architectural decision (no code written)

### Objective

Formally freeze the AMALGAM v1.0 architecture to prevent continued drift. Define the three-category component classification system.

### Why it was started

During Mission 5 design, repeated attempts to integrate Workspace and Knowledge into the pipeline (as Tool, Service, etc.) revealed the architecture was not yet cleanly defined. The AI architect called a stop to establish permanent classification rules before implementing.

### Architecture v1.0 (frozen)

**Layer definitions:**
- Layer 1: Interface (CLI/GUI/Voice/API)
- Layer 2: Orchestrator (session/conversation lifecycle)
- Layer 3: Brain (Intent Analyzer, Planner, Reasoning)
- Layer 4: Kernel (Task, Executor, Dispatcher)
- Layer 5: Registries (ActionRegistry, ToolRegistry, ServiceRegistry)
- Layer 6: Tools — perform actions (Calculator, Python, Files, Internet)
- Layer 7: Services — stateful/external (LLM, Memory, Diagnostics)
- Layer 8: Engines — analyze and understand, read-only (Workspace, Knowledge, Vision, Git)

**Golden Rule (quoted):** *"Every new module must answer: Am I a Tool, a Service, or an Engine?"*

**Dispatcher design decision:**
- Changed to try `ToolRegistry` first, then `ServiceRegistry` if not found.
- Enables services (like `ProjectService`) to be invoked through the same `ActionRegistry` → `Dispatcher` pattern as tools, without a parallel dispatch path.

### Completion status

Complete (decision recorded).

---

## MILESTONE 16 — v0.5 Mission 5.1: Capability Integration (6/29/2026, ~11:25 AM)

**Sequence:** 16  
**Date:** 6/29/2026, ~11:11 AM – 11:25 AM  
**Mission / Sub-mission:** Mission 5 Sprint 1 (v0.5 series)

### Objective

Integrate Memory, Files, Internet, and Python execution into the Brain → Planner → Dispatcher pipeline so users can invoke them through natural language.

### Why it was started

Four capabilities (Memory, Files, Internet, Python) already existed as Tools, but the `IntentAnalyzer` never produced their intents and the `Planner` never created their tasks. The AI architect observed: *"Everything on this list uses systems you've already built. No new subsystem."*

### Major implementation

**`brain/intent/intent.py` extended:**
- `INTENT_MEMORY`: detected by `lower.startswith("remember ")` or `lower.startswith("recall ")`.
- `INTENT_FILES`: detected by `"list files"`, `"show files"`, `"directory"`, `"folders"`, `"ls"`.
- `INTENT_INTERNET`: detected by `"search "`, `"search web"`, `"google"`, `"find online"`.
- `INTENT_PYTHON`: detected by `"run python"`, `"execute python"`, `"python:"`.

**`brain/planner/planner.py` extended:**
- `INTENT_MEMORY` → `ACTION_REMEMBER` or `ACTION_RECALL` (with `key=value` parsing for remember).
- `INTENT_FILES` → `ACTION_LIST_FILES` with `data="."`.
- `INTENT_INTERNET` → `ACTION_SEARCH_WEB` with query extracted from input.
- `INTENT_PYTHON` → `ACTION_RUN_PYTHON` with code extracted from input.
- `INTENT_CODING` → `ACTION_GENERATE_CODE` (existing).

**Test result (quoted):** `"73 passed in 11.70s"`

### Completion status

Complete.

### Next planned mission

Mission 5.2: Workspace + Knowledge integration via ProjectService.

---

## MILESTONE 17 — v0.5 Mission 5.2: Project Analysis Integration (6/29/2026, ~12:00 PM)

**Sequence:** 17  
**Date:** 6/29/2026, ~11:30 AM – 12:00 PM  
**Mission / Sub-mission:** Mission 5 Sprint 2 (v0.5 series)

### Objective

Expose the Workspace and Knowledge engines through the execution pipeline via a new `ProjectService`. Make "Explain my project" return real project analysis instead of an LLM guess.

### Why it was started

Workspace (375 symbols, 164 relationships) and Knowledge engines were built but not accessible through the pipeline. The AI architect stated: *"An AI developer spends far more time understanding its own project than browsing websites."*

### Major implementation

**`services/project_service.py` CREATED:**
```python
class ProjectService:
    def summarize(self, _=None):
        workspace = Workspace(self.root).report()
        knowledge = KnowledgeEngine(self.root).build()
        return {"workspace": workspace.as_dict(), "knowledge": knowledge.as_dict(), "summary": {...}}
```

**`config/constants.py` extended:**
- `SERVICE_PROJECT = "project"`
- `ACTION_PROJECT_SUMMARY = "project_summary"`
- `INTENT_PROJECT = "project"`

**`services/service_registry.py` updated:**
- `ProjectService()` added under `SERVICE_PROJECT` key. (Caused test_service_registry failure; test updated to `{"llm", "memory", "ollama", "project"}`.)

**`brain/intent/intent.py` extended:**
- `project_phrases` list added before `INTENT_GENERAL` fallback. Detects: `"explain my project"`, `"summarize my project"`, `"project overview"`, `"project architecture"`, etc.

**`brain/planner/planner.py` extended:**
- `INTENT_PROJECT` → `Task(action=ACTION_PROJECT_SUMMARY)`.

**`kernel/action_registry.py` extended:**
- `ACTION_PROJECT_SUMMARY: (SERVICE_PROJECT, "summarize")`.

**`kernel/dispatcher.py` updated:**
- `if target is None: target = self.services.get(target_name)` — Dispatcher now falls back to ServiceRegistry if ToolRegistry returns `None`. This enables services to be invoked through the same routing path as tools.

**`kernel/dispatcher.py` — output formatting:**
```python
if action == constants.ACTION_PROJECT_SUMMARY:
    summary = result["summary"]
    print(f"Project Root : {summary['project_root']}")
    print(f"Packages     : {len(summary['python_packages'])}")
    print(f"Documents    : {summary['documents']}")
    print(f"Symbols      : {summary['symbols']}")
    print(f"Relations    : {summary['relationships']}")
```

**FIRST END-TO-END DEMO (quoted from session):**
```
You: Explain my project
AMALGAM
Project Root : C:\Users\ankit\Projects\AMALGAM
Packages     : 16
Documents    : 5
Symbols      : 375
Relations    : 164
```

### Tests added

`tests/test_intent.py` extended with `test_detects_project_request`.

**Test result (quoted):** `"74 passed"` (one new test added).

### Completion status

Complete. First integration of Workspace + Knowledge engines into the execution pipeline.

### Next planned mission

Mission 5.3: Code Navigation ("Find Dispatcher", "Who imports Workspace?").

---

## MILESTONE 18 — Tooling Upgrade: Cline + Local Qwen (6/29/2026, ~2:51–4:21 PM)

**Sequence:** 18  
**Date:** 6/29/2026, ~2:51 PM – 4:21 PM  
**Mission / Sub-mission:** Development workflow upgrade (not a code mission)

### Objective

Replace manual copy-paste development with an autonomous local coding agent (Cline + Ollama + qwen2.5-coder:7b) to match the Codex workflow without cloud quotas.

### Why it was started

Codex daily quota repeatedly exhausted mid-mission. User stated: *"ye sab se fast qwn hai jo mere pc mein dalwaye thay tum?"* and *"limit ka drama na ho."*

### Events

1. **GitHub Student Pack application** — Applied and rejected (reasons: 2FA missing, billing info missing, location mismatch — user in Patna, university in Telangana). Decision: don't wait 1.5 months; continue without GitHub Pro.

2. **Roo Code** — Installed (VS Code extension v3.54.0). Gemini 2.5 Pro API connected. Codebase indexing attempted (required Qdrant — deferred). Roo stayed at "Queued" indefinitely when connected to Ollama — root cause: tool-calling compatibility issue between Roo and local models.

3. **Cline** — Installed (VS Code extension by saoudrizwan). Connected to Ollama at `http://127.0.0.1:11434` with `qwen2.5-coder:7b`. Initial error: `"model is required"` — fixed by manually entering model name. **Connection confirmed.**

4. **ROO.md** — Created in project root with AMALGAM development rules for all AI agents.

### Final workflow established

```
User (Founder) → ChatGPT (CTO/Architect) → Cline + Qwen (Senior Engineer)
→ pytest → ChatGPT (review) → Next Mission
```

### Completion status

Complete. Cline + Ollama + qwen2.5-coder:7b operational.

---

## MILESTONE 19 — v0.5 Mission 5.3: Code Navigation (Started 6/29/2026, ~4:21 PM)

**Sequence:** 19  
**Date:** 6/29/2026, ~4:21 PM  
**Mission / Sub-mission:** Mission 5 Sprint 3 (v0.5 series)

### Objective

Enable natural-language code navigation commands: "Find Dispatcher", "Show Planner", "Who imports Workspace?", using the existing `KnowledgeEngine`.

### Why it was started

375 symbols and 164 relationships already existed in the Knowledge Engine but were not accessible through the pipeline. The AI architect argued: *"You're sitting on the data needed to answer those questions."*

### Architecture plan

```
User
  ↓
Brain (INTENT_PROJECT)
  ↓
Planner (ACTION_FIND_SYMBOL)
  ↓
Dispatcher
  ↓
ProjectService.find_symbol(query)
  ↓
KnowledgeEngine.search_symbols()
```

No new engine — extension of existing `ProjectService` and `KnowledgeEngine`.

### Completion status

**Started only.** Cline prompt given at ~4:21 PM. Implementation and test results not recorded in the exported conversation. Mission status at end of conversation: in progress.

### Tests added

Not specified (mission not completed in exported conversation).

### Next planned mission

Not explicitly decided; session ended.

---

---

## POST-CONVERSATION MILESTONES (7/6/2026 — from repository artefacts only)

The following milestones are documented from `.amalgam-core/HISTORY.json` and `.amalgam-core/MISSION.md`. They do not appear in the exported conversation and were completed after 6/29/2026.

---

## MILESTONE 20 — Mission 7.1.7: Mission Executor Integration (7/6/2026, ~1:31 AM – 2:30 AM)

**Sequence:** 20  
**Date:** 7/6/2026, ~1:31 AM – 2:30 AM  
**Mission / Sub-mission:** M7.1.7

### Objective (from HISTORY.json)

"Integrate Mission execution with AutonomousExecutor."

### Major implementation (from HISTORY.json)

- `brain/mission/mission_executor.py` — modified.
- `agents/chief_agent.py` — modified.

### Tests added (from HISTORY.json)

15 tests in `tests/test_mission_orchestration.py`:
- `TestExecuteGraph`, `TestMissionExecutorCancellation` (3 tests), `TestResumeExecution` (3 tests), `TestCancelExecution` (3 tests), `TestGracefulShutdown` (3 tests), `TestBackwardCompatibility` (2 tests).

**Test result (quoted):** `"772 passed in 138.51s"`, 0 failures.

### Completion status

Complete. LOOP_COMPLETE verdict.

### Next planned mission

M7.1.8

---

## MILESTONE 21 — Mission 7.1.8: Tool Integration (7/6/2026, ~5:00 AM – 6:00 AM)

**Sequence:** 21  
**Date:** 7/6/2026, ~5:00 AM – 6:00 AM  
**Mission / Sub-mission:** M7.1.8

### Objective (from HISTORY.json and MISSION_7_1_8.md)

"Integrate Mission execution with the existing Tool ecosystem by providing a universal `ToolResult` abstraction, capability validation, permission checks, retry/timeout wrapping, and lifecycle event integration."

### Major implementation (from MISSION_7_1_8.md)

**Files created:**
- `tools/tool_result.py` — `ToolResult` frozen dataclass with `ok()`/`fail()` builders and `to_dict()`/`from_dict()` serialization.
- `tools/capability_validator.py` — `CapabilityValidator`: validates action → tool lookup via `ActionRegistry` + `ToolRegistry`.
- `tools/tool_wrapper.py` — `ToolWrapper` with retry, timeout (`ThreadPoolExecutor`), permission checking, lifecycle events via `MissionEventBus`.

**Files modified:**
- `kernel/permissions.py` — populated with `PermissionChecker` (workspace boundary enforcement for FileTool; was empty).
- `tests/test_mission_tool_integration.py` — expanded from 2 to 36 tests.

### Major architecture decision (from MISSION_7_1_8.md)

*"Layer boundaries preserved: tools never import brain, agents, kernel, or services. Existing APIs unchanged."*

**Note (from architecture inspection):** `tools/tool_wrapper.py` imports from `brain.mission.event` and `brain.mission.event_types`. This is a layer boundary violation (tools importing brain) that was noted during the Mission 7.4 architecture inspection but was already present in the committed code.

### Tests added (from HISTORY.json)

34 new tests in `tests/test_mission_tool_integration.py`.

**Test result (quoted from HISTORY.json):** `"806 passed in 149.05s"`, 0 failures.

**Commit hash:** `c305e5d29a246db06b57cee245087c049d44f31d`  
**Branch:** `core/amalgam-core-v1`

### Completion status

Complete. LOOP_COMPLETE verdict.

### Next planned mission

M7.2 — ChiefAgent orchestration.

---

## MILESTONE 22 — Mission 7.2: ChiefAgent Orchestration (Started 7/6/2026, ~5:52 PM — In Progress as of 7/8/2026)

**Sequence:** 22  
**Date:** Started 7/6/2026, ~5:52 PM. Status as of 7/8/2026: `in_progress`.  
**Mission / Sub-mission:** M7.2

### Objective (from STATE.json)

"ChiefAgent orchestration."

### What was implemented (from reading `agents/chief_agent.py` directly)

The code in `agents/chief_agent.py` carries the comment `# Central orchestration API — Mission 7.2` identifying these additions:

- `ChiefAgent.run_pipeline(ctx, pipeline)` — executes the multi-agent pipeline (PlannerAgent → ResearchAgent → ReviewerAgent → EngineerAgent) via `Scheduler`.
- `ChiefAgent.execute(task, priority)` — convenience method: creates a fresh `SharedContext` and calls `run_pipeline()`.
- `ChiefAgent._register_agents()` — lazily registers the standard agent fleet into `AgentRegistry`.
- `ChiefAgent.DEFAULT_PIPELINE` — `["planner", "researcher", "reviewer", "engineer"]`.

### Completion status

**In progress.** State as of 7/8/2026 (from STATE.json): `"current_stage": "idle"`, `"task_status": "pending"`. No active task queued. Branch: `core/amalgam-core-v1` (working tree not clean).

**Test baseline (from CONTEXT.md):** Last run shows 806 passed, but `tests.status = "not_run"` (baseline recorded from M7.1.8; no new run confirmed for M7.2).

### Next planned mission

Not specified. Mission 7.4 architecture inspection was performed on 7/8/2026 (see note below).

---

---

## APPENDIX A — Permanent Architecture Rules (established during development)

The following rules were explicitly stated and accepted during the conversation. They are quoted verbatim.

### Execution pipeline (immutable)

*"User → Brain → Planner → Task → Executor → Dispatcher → Tool / Service"*

### Golden Rule

*"Every new module must answer: Am I a Tool, a Service, or an Engine?"*

### Development loop

*"Build → Integrate → Test → Freeze → Next subsystem."*
*"Every new subsystem must become usable before the next begins."*

### Three-category component classification

- **Tools:** perform actions (Calculator, Python, Files, Internet)
- **Services:** stateful or external (LLM, Memory, Diagnostics, ProjectService)
- **Engines:** analyze and understand, read-only (Workspace, Knowledge)

### Brain principle

*"The Brain never executes. It only decides who should do the work."*

### Kernel principle

*"The Kernel never reasons. It only executes."*

### Dispatcher architecture decision (v1.0 frozen)

Dispatcher tries ToolRegistry first, then ServiceRegistry if not found. This allows services to be invoked through the same `ActionRegistry` path as tools.

### Test policy

*"A task is not complete until all tests pass, existing tests continue passing, and no regressions exist."*

### Workflow (established 6/28/2026)

```
User (Founder) → ChatGPT (Chief Architect) → Coding Agent (Senior Engineer) → pytest → ChatGPT (review)
```

---

## APPENDIX B — Test Count Progression

| Milestone | Test result | Date |
|-----------|-------------|------|
| Genesis-1 (end) | Not formalised (manual) | 6/27/2026 |
| Genesis-2 (end) | Not formalised | 6/27/2026 |
| Mission 1 complete | **46 passed in 12.01s** | 6/28/2026 |
| Mission 2 complete | **53 passed in 12.74s** | 6/29/2026 |
| Mission 3 complete | **64 passed in 12.00s** | 6/29/2026 |
| Mission 4 complete | **73 passed in 11.82s** | 6/29/2026 |
| Mission 5.1 complete | **73 passed in 11.70s** | 6/29/2026 |
| Mission 5.2 complete | **74 passed** | 6/29/2026 |
| M7.1.7 complete | **772 passed in 138.51s** | 7/6/2026 |
| M7.1.8 complete | **806 passed in 149.05s** | 7/6/2026 |

**Gap note:** The jump from 74 tests (end of conversation, 6/29) to 772 tests (M7.1.7, 7/6) represents approximately 698 tests added in missions not present in the exported conversation. These include at minimum: Mission 5.3, Mission 6.x, Mission 7.1.x series.

---

## APPENDIX C — Key Files Introduced (Chronological)

| File | Milestone |
|------|-----------|
| `main.py`, `core/orchestrator.py`, `services/memory.py`, `data/memory.json` | Genesis-1 |
| `services/llm.py` (functional) | Genesis-2 |
| `config/models.py`, `core/router.py` | Genesis-3 |
| `core/pipeline/`, `core/preprocessor/`, `core/intent/`, `core/planner/`, `core/tools/` | Genesis-4 |
| `kernel/state.py`, `kernel/executor.py`, `services/ollama_service.py`, `interfaces/` | Genesis-5 |
| `kernel/task.py`, `kernel/dispatcher.py`, `tools/calculator.py`, `brain/brain.py` | Genesis-6 |
| `tools/python_executor.py`, `tools/file_tool.py`, `tools/tool_registry.py`, `services/service_registry.py` | Genesis-7 |
| `tools/base_tool.py`, `tools/memory_tool.py`, `kernel/action_registry.py`, `tools/internet_tool.py` | Genesis-8 |
| `config/settings.py`, `config/constants.py`, `config/version.py`, `services/logger.py`, `services/diagnostics.py` | Mission 2 |
| `workspace/` (9 files) | Mission 3 |
| `knowledge/` (10 files) | Mission 4 |
| `services/project_service.py` | Mission 5.2 |
| `tools/tool_result.py`, `tools/capability_validator.py`, `tools/tool_wrapper.py`, `kernel/permissions.py` | M7.1.8 |
| `ROO.md` | Tooling setup 6/29 |

---

*Document compiled: 7/8/2026. Source: AMALGAM_FULL_CONVERSATION.md (158,112 lines) + repository artefacts.*
