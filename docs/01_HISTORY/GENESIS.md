# GENESIS.md

> **Document type:** Design-history recovery (engineering historian).
> **Source:** `c:\AMALGAM\AMALGAM_FULL_CONVERSATION.md` (ChatGPT export). Repository
> `git log` is cited separately as implementation evidence.
> **Scope:** The pre-Mission "Genesis" phase (project birth through Genesis-8), before the
> numbered "Mission" workflow began (6/26/2026 - 6/28/2026).
> **Rules honored:** Nothing invented. Original wording quoted where available. Conflicts
> marked, not reconciled. Design history (conversation) and implementation history (repo)
> kept separate. No future missions created.
>
> **Sourcing legend:**
> - `[VERBATIM]` = quoted from the conversation, timestamp given.
> - `[RECOVERED]` = paraphrased from an earlier full read of the conversation; wording is
>   approximate but the fact is corroborated by repository `git log` where noted.
> - `[REPO]` = repository evidence (git commit / file), implementation history.

---

## 0. Pre-history (before the name "AMALGAM")

**Timestamp span:** 6/26/2026 - 6/27/2026 ~1:47 AM
**Conversation order:** earliest messages in the export.

`[RECOVERED]` Before any AMALGAM code, the user set up a local AI environment: Python, Git,
Docker, Ollama, and Open WebUI. Five Ollama models were pulled:

`[VERBATIM]` **6/27/2026, 1:40:27 AM** (user paste of `ollama list`):
```
gemma3:4b           a2af6cc3eb7f    3.3 GB
qwen2.5-coder:7b    dae161e27b0e    4.7 GB
llama3.1:8b         46e0c10c039e    4.9 GB
deepseek-r1:8b      6995872bfe4c    5.2 GB
qwen3:8b            500a1f067a9f    5.2 GB
```

`[VERBATIM]` **6/27/2026, 1:40:30 AM** - the "stop hoarding models, start building" rule:
> # 🚫 STOP DOWNLOADING MODELS
> ... They end up with 30 models -> Don't know which one to use -> Never build anything.

### Naming evolution (a real conflict of candidate names)

`[RECOVERED]` The project was first called **"Juju AI"** (folder `D:\Juju-AI` proposed,
6/27 ~1:33 AM).

`[VERBATIM]` **6/27/2026, 1:44:25 AM** - candidate names brainstormed (AI's list):
> NOVA AI / AETHER / SENTIENT / ATLAS / NEXUS / OMNIA / AURORA / ORION / HELIOS / KAIROS
> ... My personal favorite ## AETHER

`[VERBATIM]` **6/27/2026, 1:45:48 AM** - the "Orion" availability check (why it was dropped):
> ## 1. Is "ORION" already used?  **Yes.** The name **Orion** is used in many technology
> projects, including NASA's Orion spacecraft ... it's **not a unique brand**.

`[RECOVERED]` User then tried **"stu ai"** (6/27 1:47:10 AM), which the AI said was good only
for a student edition, not the core platform.

`[VERBATIM]` **6/27/2026, 1:47:36 AM** - the name AMALGAM is chosen (user proposed "amalgam ai"):
> **Amalgam AI** is honestly the first name you've suggested that made me stop and think.
> ### Meaning  "Amalgam" means:
> > **A combination of many different things into one unified whole.**
> ... ## My verdict  This is the first name in our discussion that I think is worth keeping.
> I'd rate it **9.5/10**.

**Status:** ACCEPTED. The project became **AMALGAM**; folder `C:\Users\ankit\Projects\AMALGAM`.
**Dependencies:** none (naming decision).

### Positioning debate: "AI OS" vs "Personal AI Platform" (unreconciled nuance)

`[VERBATIM]` **6/27/2026, 10:33:31 AM** - the AI pushes back on the "AI OS" label:
> I'd describe it as: > **A Personal AI Platform**  ... Because Windows is still your
> operating system. Your software **runs on top of Windows** ...

`[VERBATIM]` **6/27/2026, 10:33:31 AM** - the AI also reframed the user's self-update wish:
> You wrote: > "Amalgam updates itself automatically."
> I'd change that to: > **"Amalgam proposes improvements, explains why they're useful, and
> asks for approval before making meaningful changes."**

**CONFLICT (unreconciled):** The user consistently called AMALGAM an "AI OS" / "AI Operating
System"; the AI repeatedly preferred "Personal AI Platform". Both labels persist throughout
the conversation. Recorded here without reconciliation.

---

## 1. The founding architecture decision (Orchestrator-first)

**Timestamp:** 6/27/2026, ~10:36 AM
**Conversation order:** immediately after the vision was locked, before any code.

`[VERBATIM]` The single most important Genesis-era architectural statement:
> **The important idea is this:**
> > **The LLM is not the brain. The Orchestrator is.**
> That decision will shape everything we build.

`[VERBATIM]` **6/27/2026, 10:36:06 AM** - the first architecture diagram + motto:
> # Project: AMALGAM  ## Motto  > **"One Intelligence. Infinite Capabilities."**
> ```
> AMALGAM -> ORCHESTRATOR -> [ Brain | Memory | Knowledge | Tools | Interface ]
> ```

`[VERBATIM]` **6/27/2026, 10:33:31 AM** - the five founding Principles (quoted, condensed):
> ## Principle 1  **No single model is trusted with everything.** Specialists beat generalists.
> ## Principle 2  **Memory belongs to Amalgam, not the model.**
> ## Principle 3  **Every important action is explainable.**
> ## Principle 4  **Human approval for high-impact actions.** (Deleting files / registry /
>   installing software / pushing code)
> ## Principle 5  **Everything is replaceable.** (Models are plugins.)

`[VERBATIM]` **6/27/2026, 10:53:25 AM** - the "AI kernel" framing:
> Instead of thinking: > "Let's build an AI." Think: > **"Let's build an AI kernel."**
> Just like an operating system kernel coordinates hardware, **AMALGAM Core** will
> coordinate models, memory, tools, and knowledge.

**Status:** ACCEPTED and DURABLE - the Orchestrator/kernel-first idea survived into the
final architecture (though the concrete `orchestrator.py` later became a legacy bypass; see
ARCHITECTURE_EVOLUTION.md and MISSION_HISTORY.md Mission 5).

---

## 2. The original Genesis roadmap (later diverged - conflict marked)

**Timestamp:** 6/27/2026, ~10:58 AM
**Conversation order:** stated at the end of Genesis-1.

`[VERBATIM]` The roadmap as first written:
> ### ✅ Genesis-1 (Today) - Project structure / Core skeleton
> ### Genesis-2 - Memory Engine
> ### Genesis-3 - Model Router
> ### Genesis-4 - Personality Engine
> ### Genesis-5 - Tool System

**CONFLICT (unreconciled):** This original Genesis roadmap was NOT followed exactly. What was
actually built (see below): Genesis-2 = Ollama integration (not "Memory Engine", since memory
already shipped in Genesis-1); Genesis-4 = brain sub-modules (not "Personality Engine");
Genesis-5 = kernel/brain rename + boot (not "Tool System"). Preserved as-is per instruction.

---

## 3. Genesis-1 - Core Architecture & Persistent Memory

**Timestamp:** 6/27/2026, ~10:53 AM - 11:14 AM
**Conversation order:** first code written.
**Original proposal / build steps:**

`[VERBATIM]` **6/27/2026, 10:53:25 AM** - "define responsibilities before behavior":
> # Today we will create exactly 5 core files  Inside `core/`:
> orchestrator.py / router.py / planner.py / session.py / __init__.py
> ... We are defining responsibilities before behavior.

`[VERBATIM]` The first stub code (orchestrator.py, 6/27 10:55 AM):
```python
class Orchestrator:
    def __init__(self):
        self.version = "Genesis"
        self.status = "Initializing"
    def start(self):
        print("AMALGAM Orchestrator Started")
    def process(self, user_input: str):
        print(f"Received: {user_input}")
```

`[RECOVERED]` Then `services/` was created (memory.py, knowledge.py, llm.py, internet.py,
__init__.py) and `main.py`. `MemoryService` was upgraded to persist to `data/memory.json`
(using `json` + `os`), giving `remember key=value` / `recall key`.

`[VERBATIM]` **6/27/2026, 11:04:03 AM** - first working feature declared:
> This is the **first working feature** of AMALGAM. You now have: ✅ Core ✅ Orchestrator
> ✅ Memory Service ✅ First executable version

`[VERBATIM]` **6/27/2026, 11:13:55 AM** - persistent memory verified:
> 🎉 **YES!** ... **AMALGAM has permanent memory now.**

**Surrounding context:** A debugging episode occurred - `recall name` returned "Memory not
found" because it was tested before a `remember` under the new code; verified working after
`test_memory.py` proved `MemoryService` itself was correct.

**Status:** IMPLEMENTED.
**Repository evidence:** `[REPO]` commit `71f74aa` "Genesis-1: Core architecture and
persistent memory"; `[REPO]` commit `85216fe` "Genesis-1.1: Add .gitignore and remove
Python cache files".
**Dependencies:** none (foundation). **Related:** later Mission 1 hardened this same
memory/dispatcher foundation; Mission 5.1 exposed memory through the pipeline.

---

## 4. Genesis-2 - Connect AMALGAM to Ollama

**Timestamp:** 6/27/2026, ~11:29 AM
`[RECOVERED]` `pip install ollama`; `LLMService` connected to the Ollama API
(`http://127.0.0.1:11434`); first real AI response from Qwen3:8b through the AMALGAM CLI.
Flow: Orchestrator -> LLMService -> ollama.Client -> Qwen3:8b.
**Status:** IMPLEMENTED.
**Repository evidence:** `[REPO]` commit `deb8b04` "Genesis-2: Connect AMALGAM to Ollama".
**Dependencies:** Genesis-1. **Related:** Genesis-3 (router), later Mission 2 (LLM failure handling).

---

## 5. Genesis-3 - Model Router

**Timestamp:** 6/27/2026, ~12:08 PM
`[RECOVERED]` `config/models.py` with 5 model role->name mappings; `router.py` keyword-based
routing (coding -> qwen2.5-coder:7b, reasoning -> deepseek-r1:8b, creative -> llama3.1:8b,
fast -> gemma3:4b, general -> qwen3:8b).
**Status:** IMPLEMENTED (commit message "Genesis-3: Automatic model routing" recovered).
**Dependencies:** Genesis-2. **Related:** the Router later became one of the "5 duplicate
routing mechanisms" flagged by Codex (see MISSION_HISTORY.md Mission 1 audit).

---

## 6. Genesis-4 - Brain sub-modules + storage cleanup

**Timestamp:** 6/27/2026, ~12:17 PM - 12:33 PM
`[RECOVERED]` Sub-modules added: `core/pipeline/`, `core/preprocessor/`, `core/intent/`,
`core/planner/`, `core/tools/tool_router.py`. Genesis-4.1 Preprocessor (normalize text),
4.2 Intent Analyzer (keyword classification), 4.3 Planner (intent->action), 4.4 Tool Router
(action->model/tool). Project cleanup: `storage/` created (memory/knowledge/cache/embeddings);
`data/memory.json` moved to `storage/memory/memory.json`; new dirs agents/, models/, tools/,
knowledge/, voice/, vision/, plugins/, logs/.
**Status:** IMPLEMENTED (commit message "Genesis-4: Project cleanup and storage architecture"
recovered).
**CONFLICT:** original roadmap called Genesis-4 "Personality Engine"; the Personality Engine
was never built.
**Dependencies:** Genesis-3. **Related:** these submodules (intent/planner) became core to
Mission 5.1.

---

## 7. Genesis-5 - Kernel Boot (core->brain, engine->kernel rename)

**Timestamp:** 6/27/2026, ~8:03 PM
**Significance:** the largest Genesis-era architectural rename.
`[RECOVERED]` `engine/` renamed to `kernel/`, `core/` renamed to `brain/`; all imports
updated `from core.` -> `from brain.`. `KernelState` created (kernel/state.py: version,
status, models/memory/tools/services loaded). Kernel `Executor` gained a `boot()` method
with startup display. `OllamaService` created (wraps ollama.Client; list_models/is_running/
count_models; note: Ollama SDK 0.6.2 returns Pydantic objects, not dicts). `ModelRegistry`
(models/registry.py). `interfaces/` folder (llm.py, memory.py, tool.py, agent.py,
knowledge.py). Architecture rated "9.9/10" at this stage.
**Status:** IMPLEMENTED (commit message "Genesis-5: Kernel Boot + OllamaService +
ModelRegistry" recovered).
**CONFLICT:** original roadmap called Genesis-5 "Tool System"; the tool system actually
arrived in Genesis-6/7/8.
**Dependencies:** Genesis-4. **Related:** the brain/kernel split is the backbone of every
later mission.

---

## 8. Genesis-6 - Task system, Dispatcher, first native tool

**Timestamp:** 6/27/2026, ~8:37 PM - 9:04 PM (multiple sprints)
`[RECOVERED]` `kernel/task.py` (Task dataclass: intent, action, model, tool, data);
`Executor.execute()` accepts Task objects. Sprint 2: `kernel/dispatcher.py` (routes Task by
action). Sprint 3: `tools/calculator.py` (first non-LLM tool). Sprint 4: Intent Analyzer
upgraded to phrase lists. Sprint 5: `brain/brain.py` (`Brain.think()` = IntentAnalyzer +
Planner). Sprint 6: `main.py` simplified to Brain + Kernel; Orchestrator removed from the
execution path.
**Status:** IMPLEMENTED. **Dependencies:** Genesis-5.
**Related:** "Mode 2 Turbo" workflow (complete files, one test per sprint, git commit per
sprint) adopted here.

---

## 9. Genesis-7 - Tool + Service registries

**Timestamp:** 6/28/2026, ~1:00 AM - 1:08 AM
`[RECOVERED]` `tools/python_executor.py` (exec + redirect_stdout); `tools/file_tool.py`
(read/write/list_dir via pathlib); `tools/tool_registry.py` (name->instance: calculator,
python, files); `services/service_registry.py` (llm, memory, ollama).
**Status:** IMPLEMENTED. **Dependencies:** Genesis-6.

---

## 10. Genesis-8 - BaseTool, MemoryTool, ActionRegistry, InternetTool + Codex adoption

**Timestamp:** 6/28/2026, ~1:14 AM - 2:02 AM
`[RECOVERED]` `tools/base_tool.py` (base class; Calculator/Python/File inherit it);
`tools/memory_tool.py`; `kernel/action_registry.py` (action string -> (tool, method) tuples;
Dispatcher refactored to use it, removing the if-chain); `tools/internet_tool.py`
(requests; `pip install requests`). Codex desktop app was adopted here for implementation;
Codex ran a full architectural audit (found "5 duplicate routing mechanisms", stale tests,
hardcoded values, empty docs, missing dispatcher guardrails; rated 8.8/10 by the architect).
This audit directly produced the "AMALGAM v0.3 Mission Plan" that began the numbered
missions (see MISSION_HISTORY.md / ROADMAP_EVOLUTION.md Scheme A).
**Status:** IMPLEMENTED.
**Repository evidence:** `[REPO]` commit `96210c8` "Genesis-8.1: Introduce BaseTool
architecture"; `[REPO]` commit `ab22942` "Cleanup: Remove temporary test scripts".
**Dependencies:** Genesis-7. **Related:** ActionRegistry is the extension point every later
Tool/Service/Engine plugs into; Codex adoption started the Mission era.

---

## 11. Genesis phase - transition to Missions

`[VERBATIM]` **6/28/2026, ~1:33 AM** - the proposal to end Genesis numbering:
> Instead of calling the next milestone **Genesis-9**, let's call it:
> > **AMALGAM v0.3 - Stabilization**

`[RECOVERED]` "Genesis-9" was briefly proposed as either "AMALGAM Build System" or
"Stabilization", then superseded entirely by the mission-based workflow once Codex was
adopted. **No Genesis-9 was ever built.** The next unit of work was **Mission 1**.

**Repository evidence for the whole Genesis phase (`[REPO]` git log, oldest first):**
```
71f74aa  Genesis-1: Core architecture and persistent memory
85216fe  Genesis-1.1: Add .gitignore and remove Python cache files
deb8b04  Genesis-2: Connect AMALGAM to Ollama
ab22942  Cleanup: Remove temporary test scripts
96210c8  Genesis-8.1: Introduce BaseTool architecture
```
`[Historian note]` The repo `git log` does NOT contain individual commits for Genesis-3,
-4, -5, -6, -7 (only Genesis-1, 1.1, 2, and 8.1 are tagged in messages). Those milestones
are recovered from the conversation ("design history") but were evidently squashed or
committed under other messages in the repo ("implementation history"). This is the first
clear place where design history and implementation history diverge; see
IMPLEMENTATION_HISTORY.md.

*End of GENESIS.md*
