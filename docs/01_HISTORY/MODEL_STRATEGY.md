# MODEL_STRATEGY.md

> **Document type:** Design-history recovery (engineering historian).
> **Source:** `AMALGAM_FULL_CONVERSATION.md`. Repo cited separately.
> **Purpose:** Recover how AMALGAM's strategy for AI models and coding agents evolved -
> both the *runtime* models AMALGAM routes to, and the *development* agents used to build it.
> **Rules honored:** nothing invented; original wording quoted where available; conflicts
> marked; recovered as it appeared.
>
> **Sourcing legend:** `[VERBATIM]` quoted (timestamp given); `[RECOVERED]` paraphrased from
> earlier full read; `[REPO]` repository evidence.

---

## PART 1 - Runtime models (models AMALGAM itself routes to)

### The five local Ollama models (installed 6/26-6/27, foundation)

`[VERBATIM]` **6/27/2026, 1:40:30 AM**:
> ✅ Qwen3:8B (General assistant) / ✅ DeepSeek-R1:8B (Reasoning & problem solving) /
> ✅ Llama3.1:8B (General conversation) / ✅ Qwen2.5-Coder:7B (Programming) /
> ✅ Gemma3:4B (Fast lightweight model)

`[VERBATIM]` **6/27/2026, 1:40:30 AM** - the "stop hoarding" rule:
> # 🚫 STOP DOWNLOADING MODELS ... 30 models -> Don't know which one to use -> Never build anything.

**Status:** IMPLEMENTED (these five persisted as the default model set; see `config/models.py`).

### The Model Router (Genesis-3)

`[RECOVERED]` **6/27/2026, ~12:08 PM** - `config/models.py` (5 role->name mappings) +
keyword-based `router.py`: coding->qwen2.5-coder:7b, reasoning->deepseek-r1:8b,
creative->llama3.1:8b, fast->gemma3:4b, general->qwen3:8b.
**Design intent** `[VERBATIM]` (6/27 11:13 PM area): "You won't manually choose models
anymore. AMALGAM will."
**Status:** IMPLEMENTED. **CONFLICT:** later flagged by Codex as one of "5 duplicate routing
mechanisms"; a "Unified Routing Engine" was proposed but never built.

### Model-selection guidance for the 14B upgrade attempt

`[RECOVERED]` **6/30/2026** - a `qwen2.5-coder:14b` pull was attempted for heavier coding.
It initially failed with `CUDA error: shared object initialization failed` on the RTX 3050
6GB, was diagnosed (Ollama 0.30.11 / port 11434 already in use / stale process), and
eventually loaded successfully (`llama-server started`, `runner.vram="4.0 GiB"`). Guidance
given: keep 7B for quick tasks, 14B for architecture/multi-file edits.
**Status:** the 14B ran but was NOT adopted as the primary engine (see Part 2).

### Nemotron 3 Ultra evaluation (deferred)

`[RECOVERED]` **6/30/2026, ~12:32 AM** - NVIDIA "Nemotron 3 Ultra / OpenCode" was researched
(1M-token context, MoE Mamba+Transformer, agent-focused). Verdict: interesting, but "let it
be for later" - do NOT switch the foundation mid-build; benchmark against Qwen 14B later.
**Status:** DEFERRED (never adopted in-conversation).

---

## PART 2 - Development agents (agents used to BUILD AMALGAM)

`[Historian note]` This is a long "tool-hopping saga." The models/agents were switched
repeatedly, mostly because of quota limits and Windows/Python-3.14 friction. Recorded in
order; each switch is a real event.

### Codex (adopted Genesis-8, primary early implementer)

`[RECOVERED]` **6/28/2026, ~1:44 AM** - the OpenAI Codex desktop app was adopted. Workflow:
"You (Founder) -> ChatGPT (Chief Architect) -> Codex (Implementation) -> Testing -> Git."
Codex ran the Genesis-8 audit and implemented Missions 1-4.
**CONFLICT / blocker:** Codex quota exhausted repeatedly (6/28 2:14 AM "Resets: Jul 28";
again mid-Mission-4). **Status:** used heavily early; abandoned as sole implementer once
quota ran out.

### The tool-hopping saga (6/29 evening)

`[RECOVERED]` After Codex quota ran out, the following were tried in sequence to find an
unlimited local coding agent:
- **Roo Code** (VS Code ext) + Qwen via Ollama - "Queued" issues.
- **Cline** + qwen2.5-coder:7b - configured, "model is required" fixed manually.
- **OpenCode** (npm) - required Node.js (not installed).
- **Aider** (`pip install aider-chat`) - FAILED on Python 3.14 (`setuptools.build_meta`).
- **Gemini CLI** - chosen "winner" (user had Gemini Pro); required Node.js (installed via
  Chocolatey: `nodejs-lts v24.18.0`, npm 11.16.0); then Google DEPRECATED consumer
  "Sign in with Google" for Gemini CLI as of 6/18/2026 -> switched to API key -> quota
  ("Usage limit reached for all Pro models").

`[VERBATIM]` **6/29/2026, 9:19:44 PM** - the ranked comparison ("Research Mission R-001"):
> | Codex | 10 | | OpenCode | 9.5 | | Aider | 9.2 | | OpenHands | 8.8 | | Cline | 8 | | Roo | 7 |

`[Historian note]` The tool-hopping directly triggered the "Engineer Core" pivot (Mission 6,
Scheme D): rather than depend on external agents, AMALGAM would become its own coding agent.
`[VERBATIM]` 6/29 10:36 PM: every mission must answer "Does this make AMALGAM less dependent
on external coding agents?"

### Continue + local models (6/30)

`[RECOVERED]` **6/30/2026** - Continue (VS Code) tried with DeepSeek/Qwen/Gemma-tools.
Finding: Continue could read/edit individual files but **could not reliably do autonomous
recursive traversal** - it hallucinated files (e.g. `utils/file_walker.py`, which did not
exist). Conclusion (verbatim): "the limiting factor appears to be Continue Agent
orchestration, NOT Ollama, NOT hardware, NOT prompt quality."
**Status:** kept for inline edits only; not used as the autonomous agent.

### Kimi (7/1 onward - built Mission 6.4, later 7.1.x)

`[RECOVERED]` Kimi (Moonshot) was used against the real repo. It built the Autonomous Agent
Core (Mission 6.4) and later Mission 7.1.x work. It notably REFUSED to implement Mission 7.1
without a spec (7/2), which the architect praised as correct behavior.
**CONFLICT (verbatim, preserved):** Kimi reported "176 passed" for Mission 6.4 while Codex
reported "74 passed"; the architect sided with 74.
**Status:** IMPLEMENTED significant portions; interruptions due to "Too many people are
chatting with Kimi right now" + pytest exceeding the ~300s environment limit.

### Claude Code (7/1 - reviewer role)

`[RECOVERED]` Claude Code was evaluated and found strong at repository understanding, git,
architecture summarization, and security review. Assigned the "Senior Reviewer" role, not
the primary implementer. User stated they had high effective quota ("million token access
per account ... 10 accounts").

### Gemini (Mission 6.6 Phase 1 implementer)

`[RECOVERED]` Gemini implemented Mission 6.6.1 Phase 1 (Fleet infrastructure); a Codex report
for later phases was audited and found to have misreported paths/test counts before acceptance.

### OpenCode (7/6 - built .amalgam-core)

`[RECOVERED]` OpenCode ran the 11 parallel "workers" that produced the `.amalgam-core`
infrastructure (bootstrap/context/registry/loop/recovery/fingerprint/engine/provider + the
markdown/JSON state files).

---

## PART 3 - The locked division of labor (multi-AI team)

`[RECOVERED]` **7/1/2026, ~7:45 PM** - the roles were formalized:
> - **ChatGPT** -> CTO / System Architect / Final Auditor / roadmap / code review.
> - **Gemini / Codex** -> bulk implementation (large code generation).
> - **Claude Code / Kimi** -> deep review, security, refactoring, medium implementation.
> - **AMALGAM (eventual goal)** -> becomes its own engineering agent (Mission 6 pivot).

`[VERBATIM]` the governing continuity rule (7/1 ~1:44 AM):
> **Conversation = Temporary Working Memory** / **Repository = Permanent Source of Truth**

`[Historian note]` This rule is why the `.amalgam-core` state system (STATE.json as single
source of truth) was later built: so any model (Kimi/GLM/DeepSeek/OpenCode) could resume the
same work after a crash or quota limit.

---

## PART 4 - Provider Framework (model/backend abstraction - future)

`[RECOVERED]` **6/29/2026, ~10:14 AM** - originating from the user's "free Telegram storage"
idea, the architect generalized it to a **Provider Framework** (Bring-Your-Own-Infrastructure):
> providers/ : LocalStorageProvider / TelegramStorageProvider / GoogleDriveProvider /
> OneDriveProvider / S3Provider ... and analogously Model Provider / Browser Provider /
> Voice Provider / Memory Provider.

`[VERBATIM]` design principle: "AMALGAM shouldn't own anything. It should integrate everything."
The `.amalgam-core/provider.py` (7/6) is the closest realized fragment (provider failover for
coding models), but the full storage/model Provider Framework was **NOT built**.
**Status:** APPROVED as a future Epic; largely UNIMPLEMENTED. See FUTURE_PROPOSALS.md.

---

## Conflicts recorded (NOT reconciled)

1. **Best coding agent** - ranked Codex #1, but Codex was abandoned (quota); the "winner"
   changed at least six times (Roo -> Cline -> OpenCode -> Aider -> Gemini CLI -> Kimi/Claude/OpenCode).
2. **Test-count contradiction** - Kimi "176 passed" vs Codex "74 passed" for Mission 6.4.
3. **Runtime model routing** - Genesis Router vs the multiple later routers (CapabilityRouter,
   KnowledgeRouter, tool_router, ModelSelector); a unifying router was never built.
4. **14B vs 7B** - 14B loaded but was not made primary; strategy stayed multi-model.

*End of MODEL_STRATEGY.md*
