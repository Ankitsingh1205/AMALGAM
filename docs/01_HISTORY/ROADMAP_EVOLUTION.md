# ROADMAP_EVOLUTION.md

> **Document type:** Design-history recovery (engineering historian).
> **Source:** `AMALGAM_FULL_CONVERSATION.md`.
> **Purpose:** Preserve EVERY roadmap version that appeared in the conversation, **separately
> and in full**. Per instruction: *"If multiple roadmap versions exist, preserve every version
> separately. Never attempt to reconcile conflicts. Mark conflicts explicitly."*
> **This document does NOT decide which roadmap was "correct."** It records all of them.
>
> **Sourcing legend:** `[VERBATIM]` quoted from conversation (timestamp given);
> `[RECOVERED]` paraphrased from earlier full read.

---

## Roadmap version count

At least **SEVEN** distinct roadmaps/mission-plans appeared, plus a separate version-number
roadmap. They are listed below in chronological order of appearance. Each is a SEPARATE
artifact; they conflict with one another and are NOT merged.

```
R0  Juju-AI version roadmap        (6/27 ~1:33 AM)  V0.1..V5.0
R1  Amalgam milestone framing      (6/27 ~10:33 AM) Milestone 1..5 (Foundation..Ecosystem)
R2  Genesis roadmap                (6/27 ~10:58 AM) Genesis-1..5
G   Version milestones             (6/28 ~2:00 AM)  v0.3..v1.0
A   "AMALGAM v0.3 Mission Plan"     (6/28 ~2:03 AM)  Mission 1..7
B   Post-Mission-4 revision        (6/29 ~10:38 AM) Mission 5..10
C   "the one we should stick to"    (6/29 ~2:22 PM)  Mission 1..10
D   "Engineer Core" pivot          (6/29 ~10:36 PM) Mission 6..13
E   Proposed Mission 7 roadmap      (7/2  ~3:51 PM)  Mission 7.1..7.8  (PROPOSED, NOT followed)
```

---

## R0 - Juju-AI version roadmap (pre-AMALGAM name)

`[VERBATIM]` **6/27/2026, ~1:33 AM** (while still named "Juju AI"):
> ### Version 0.1 - ✅ Local AI / Chat interface / Multiple models
> ### Version 0.2 - Long-term memory / User profile / Preferences
> ### Version 0.3 - PDF knowledge / Internet search
> ### Version 0.4 - Voice assistant / Vision
> ### Version 0.5 - Windows automation / AI agents
> ### Version 1.0 - **Juju AI OS**

`[VERBATIM]` **6/27/2026, 1:43:59 AM** (expanded version roadmap, same session):
> ### V0.1 Brain / Multiple models / Memory / Profile
> ### V0.5 Voice / Internet / Images / Vision
> ### V1.0 Juju AI
> ### V2.0 Real-time voice / Desktop overlay / Wake word / Automation
> ### V3.0 SRGPT / Deploy online / Students use it / Campus-wide knowledge
> ### V5.0 Mobile app / Desktop app / Website / Cloud sync / AI agents

**Status:** SUPERSEDED (project renamed AMALGAM; this roadmap not carried forward verbatim).

---

## R1 - Amalgam milestone framing (Foundation..Ecosystem)

`[VERBATIM]` **6/27/2026, 10:33:31 AM**:
> ### Milestone 1 - Foundation - Core architecture / Multi-model support / Memory foundation.
> ### Milestone 2 - Intelligence - Knowledge / Internet / Routing.
> ### Milestone 3 - Interaction - Voice / Vision / Personality.
> ### Milestone 4 - Autonomy - Automation / Agents / Workflow assistance.
> ### Milestone 5 - Ecosystem - SRGPT / Mobile / Cloud synchronization / Plugin system.

**Status:** SUPERSEDED by the Genesis numbering, then the Mission numbering.

---

## R2 - Genesis roadmap

`[VERBATIM]` **6/27/2026, ~10:58 AM**:
> ### ✅ Genesis-1 (Today) - Project structure / Core skeleton
> ### Genesis-2 - Memory Engine
> ### Genesis-3 - Model Router
> ### Genesis-4 - Personality Engine
> ### Genesis-5 - Tool System

**CONFLICT (explicit):** This roadmap does NOT match what was built. Actual Genesis-2 =
Ollama integration; Genesis-4 = brain sub-modules (Personality Engine never built);
Genesis-5 = kernel/brain rename + boot (Tool System arrived in Genesis-6/7/8). See GENESIS.md.
**Status:** PARTIALLY FOLLOWED / DIVERGED.

---

## G - Version milestones (v0.3..v1.0)

`[VERBATIM]` **6/28/2026, 2:00:36 AM**:
> ### v0.3 - Stabilization - Clean architecture / Consistent naming / Reliable tests / Better error handling
> ### v0.4 - Core Capabilities - Browser automation / Internet search / PDF reading / Git integration / Project indexing
> ### v0.5 - Knowledge - RAG / Embeddings / Semantic search / Long-term memory
> ### v0.6 - Agents - Planner Agent / Coding Agent / Research Agent / Review Agent / Parallel execution
> ### v0.7 - Desktop OS - Voice / Vision / Windows automation / Clipboard / Screen understanding
> ### v1.0 - A stable local AI Operating System.

**CONFLICT (explicit) vs. actual tags:** v0.4/v0.5/v0.7 as described were NOT reached. Actual
tags: v0.3.0-alpha (Mission 1), v0.6.0 "Autonomous Agent Framework" (Mission 6.4 - NOT the
"Agents" content described here), v0.6.6, amalgam-core-v1.0/v1.1. v0.4 "Core Capabilities"
(Browser/PDF/Git) was never built. **Status:** ABANDONED / DIVERGED.

---

## A - "AMALGAM v0.3 Mission Plan" (the first numbered mission roadmap)

`[VERBATIM]` **6/28/2026, 2:03:15 AM** ("Roadmap (locked)"):
> - **Mission 1:** Foundation Stabilization
> - **Mission 2:** Logging & Configuration
> - **Mission 3:** Unified Routing Engine
> - **Mission 4:** Plugin Loader
> - **Mission 5:** Dependency Injection
> - **Mission 6:** Kernel State Machine
> - **Mission 7:** Browser & Knowledge Engine

**CONFLICT (explicit):** Labeled "locked" but was NOT followed past Mission 2:
- Mission 3 "Unified Routing Engine" -> actually built Workspace Engine.
- Mission 4 "Plugin Loader" -> actually built Knowledge Engine.
- Mission 5 "Dependency Injection" -> actually built Integration.
- Mission 6 "Kernel State Machine" -> actually built Engineer Core / Autonomous Agent.
- Mission 7 "Browser & Knowledge Engine" -> actually built Mission Engine (Browser never built).
**Status:** SUPERSEDED (Missions 1-2 followed; 3-7 relabeled).

---

## B - Post-Mission-4 revision

`[RECOVERED]` **6/29/2026, ~10:38 AM** (stated after Mission 4 approval):
> Mission 5 = Memory 2.0
> Mission 6 = Agent Framework
> Mission 7 = Plugin System
> Mission 8 = Dependency Injection (DI)
> Mission 9 = API / Remote
> Mission 10 = v1.0

**CONFLICT (explicit):** Directly contradicts Scheme A AND the later Schemes C/D. Mission 5
did NOT become "Memory 2.0" (it became Integration). **Status:** SUPERSEDED within hours.

---

## C - "The one we should stick to"

`[VERBATIM]` **6/29/2026, 2:09:36 PM** (self-described as final):
> ✅ Mission 1 Stabilization
> ✅ Mission 2 Infrastructure
> ✅ Mission 3 Workspace
> ✅ Mission 4 Knowledge
> 🔄 Mission 5 Integration (✅ Memory ✅ Files ✅ Internet ✅ Python ✅ Project Analysis ⬜ Code Navigation)
> ⬜ Mission 6 Personal Knowledge Base
> ⬜ Mission 7 Git Intelligence
> ⬜ Mission 8 Browser
> ⬜ Mission 9 Vision
> ⬜ Mission 10 Voice

`[VERBATIM]` accompanying rule:
> **We don't change the roadmap unless you explicitly decide to.**

**CONFLICT (explicit):** Despite the "don't change" rule, this roadmap was abandoned the SAME
NIGHT (6/29 ~10:36 PM) in favor of Scheme D. Mission 6 "Personal Knowledge Base", Mission 7
"Git Intelligence", Mission 8 "Browser", Mission 9 "Vision", Mission 10 "Voice" were all
abandoned - none were built. **Status:** ABANDONED (same day).

---

## D - "Engineer Core" pivot (the scheme actually built for Mission 6)

`[VERBATIM]` **6/29/2026, 10:36:17 PM**:
> Mission 6  Engineer Core
> Mission 7  Tool System
> Mission 8  LLM Integration
> Mission 9  Autonomous Task Loop
> Mission 10 Self Verification
> Mission 11 Self Debugging
> Mission 12 Mission Memory
> Mission 13 Self Improvement

`[VERBATIM]` Mission 6 internal sub-roadmap (6/29 10:59:51 PM):
> **6.0** Extend FileTool / **6.1** Create EngineerAgent / **6.2** Create CommandTool /
> **6.3** Automatic verification / **6.4** Retry & self-debug loop / **6.5** Integrate with Orchestrator

**CONFLICT (explicit) with C:** In Scheme C, Mission 6 = "Personal Knowledge Base" and
Mission 7 = "Git Intelligence". In Scheme D, Mission 6 = "Engineer Core" and Mission 7 =
"Tool System". These are irreconcilable; both are preserved.
**PARTIAL-FOLLOW:** Mission 6 was built (as Engineer Core -> Autonomous -> Multi-Agent ->
Fleet). Missions 7-13 as named here (Tool System / LLM Integration / Autonomous Task Loop /
Self Verification / Self Debugging / Mission Memory / Self Improvement) were NOT built under
these labels; Mission 7 became "Mission Engine" instead. **Status:** PARTIALLY FOLLOWED.

---

## E - Proposed Mission 7 roadmap (PROPOSED, explicitly NOT followed)

`[VERBATIM]` **7/2/2026, 3:51:30 PM** ("Mission 7 Roadmap (Proposed)"):
> ### Mission 7.1 - Autonomous Runtime Foundation (RuntimeContext / SessionManager /
>   CheckpointManager / ExecutionState / lifecycle start-pause-resume-stop)
> ### Mission 7.2 - Mission Engine v2
> ### Mission 7.3 - Planning Engine v2
> ### Mission 7.4 - Event Bus
> ### Mission 7.5 - Model Router
> ### Mission 7.6 - Workspace Intelligence
> ### Mission 7.7 - Fleet Intelligence
> ### Mission 7.8 - Production AI OS

**CONFLICT (explicit) with what was built:** The IMPLEMENTED Mission 7 tree (per repo git log)
was 7.1.0 Mission Core / 7.1.1 Epic / 7.1.2 Graph / 7.1.3 Planner Integration / 7.1.4
Persistence / 7.1.5 Event Bus / 7.1.6 Scheduler Integration / 7.1.7 AutonomousExecutor
integration / 7.1.8 Tool Integration, then 7.2 ChiefAgent orchestration, 7.3 ChiefAgent +
FleetManager. This does NOT match Scheme E's 7.1 "Runtime Foundation" / 7.2 "Mission Engine
v2" / 7.3 "Planning Engine v2" etc. **Status:** PROPOSED, NOT FOLLOWED. The user explicitly
chose (7/2 3:45 PM) to skip formal specs and drive by prompt instead.

`[Historian note]` Scheme E's "Mission 7.4 = Event Bus" is a *proposal only*. The actual
Mission 7.4 was never defined or started. Per instruction, no Mission 7.4 is created here.

---

## Also-proposed roadmaps that were architectural, not mission-numbered

`[VERBATIM]` **6/29/2026, 11:10:26 AM** - the "Alpha/Beta/Gamma/Delta" roadmap (from the
Architecture v1.0 freeze):
> ## Alpha (Done) - Foundation / Infrastructure / Workspace / Knowledge
> ## Beta - Architecture Integration / Engine Registry / Workspace integration / Knowledge integration / Reasoning
> ## Gamma - Browser / Vision / Git / Voice
> ## Delta - Plugin SDK / Agent Framework / Background Jobs / Multi-model orchestration

**Status:** Partially followed (Alpha done; Beta partially via Mission 5; Gamma/Delta not built).

---

## Conflict summary table (NOT reconciled - for navigation only)

| Mission # | Scheme A | Scheme B | Scheme C | Scheme D | Scheme E (7.x) | ACTUALLY BUILT |
|-----------|----------|----------|----------|----------|----------------|----------------|
| 1 | Foundation Stab. | - | Stabilization | - | - | Foundation Stabilization ✅ |
| 2 | Logging & Config | - | Infrastructure | - | - | Core Infrastructure ✅ |
| 3 | Unified Routing | - | Workspace | - | - | Workspace Engine ✅ |
| 4 | Plugin Loader | - | Knowledge | - | - | Knowledge Engine ✅ |
| 5 | Dependency Injection | Memory 2.0 | Integration | - | - | Integration (5.1/5.2 ✅, 5.3 abandoned) |
| 6 | Kernel State Machine | Agent Framework | Personal KB | Engineer Core | - | Engineer Core->Autonomous->Multi-Agent->Fleet ✅ |
| 7 | Browser & Knowledge | Plugin System | Git Intelligence | Tool System | Runtime Foundation | Mission Engine (7.1.0-7.3) ✅ |
| 8 | - | DI | Browser | LLM Integration | Mission Engine v2 | NOT BUILT |
| 9 | - | API/Remote | Vision | Autonomous Task Loop | Planning Engine v2 | NOT BUILT |
| 10 | - | v1.0 | Voice | Self Verification | Model Router | NOT BUILT |
| 11 | - | - | - | Self Debugging | - | NOT BUILT |
| 12 | - | - | - | Mission Memory | - | NOT BUILT |
| 13 | - | - | - | Self Improvement | - | NOT BUILT |

`[Historian note]` Every cell is preserved as it appeared. The table is a navigation aid, NOT
a reconciliation. The same mission number legitimately means up to five different things.

*End of ROADMAP_EVOLUTION.md*
