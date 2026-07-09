# Conversation Planning Index - Step 4: Architectural Decisions

Derived ONLY from CONVERSATION_INDEX_STEP3_CLUSTERS.md (19 clusters, 629 occurrences).
The original conversation was NOT opened.
Nothing is invented; nothing is resolved; conflicting versions are kept as separate decisions.

Where the same mission number carries multiple historical meanings, each meaning is a distinct decision entry.
Status vocabulary: Proposed / Implemented / Changed / Abandoned / Unknown.

---

====================================================
Decision #1
Name: Mission 7 as architecture-first autonomous OS
Source Cluster: Cluster #1 (Mission 7 - overall roadmap & architecture framing)
Mission Reference: 7, 7.0
Status: Implemented
Original Idea: Mission 7 would transform AMALGAM from a tool orchestrator into an autonomous operating system, gated by a CTO-level architecture review and a deep production audit before any code was written.
Evolution: Started vaguely scoped as a 'feature mission'; shifted to 'build an operating system, not features'; formalized via a Mission 7.0 Architecture Lock and a MISSION_7_MASTER_ARCHITECTURE document; introduced spec-first discipline (agent refused to implement an undefined 7.1); ended with an attempt to recover the lost original roadmap.
Final Known State: Mission 7.0 Architecture Lock was accepted and Mission 7 implementation proceeded under it. The overall framing as 'autonomous OS' governed all subsequent 7.x work.
Dependencies: Mission 6 (frozen at v0.6.6.1 baseline before Mission 7 entered)
Confidence: High
====================================================

====================================================
Decision #2
Name: Mission 7 Proposed Roadmap (alternate 7.1-7.3 labels)
Source Cluster: Cluster #2 (Mission 7 Proposed Roadmap)
Mission Reference: 7.1, 7.2, 7.3
Status: Proposed (not implemented under these labels)
Original Idea: A single late-appearing scheme proposed: 7.1 = Autonomous Runtime Foundation; 7.2 = Mission Engine v2; 7.3 = Planning Engine v2.
Evolution: Appeared once as 'Mission 7 Roadmap (Proposed)' and generated a 7.1 implementation prompt; the implemented 7.1/7.2/7.3 used entirely different labels (Mission Engine / ChiefAgent / FleetManager).
Final Known State: This scheme was NOT adopted for the implemented work. It remains an isolated proposal in the record, not merged with implemented labels.
Dependencies: Not specified
Confidence: High
====================================================

====================================================
Decision #3
Name: Mission 7.1 - Mission Engine (implemented)
Source Cluster: Cluster #3 (Mission 7.1 - Mission Engine)
Mission Reference: 7.1, 7.1.0, 7.1.1, 7.1.2, 7.1.3, 7.1.4, 7.1.5, 7.1.6, 7.1.7, 7.1.8
Status: Implemented
Original Idea: Build the Mission Engine — mission metadata, lifecycle, dependency graph, persistence, event bus, and executor/scheduler/tool integration — as the first major subsystem of Mission 7.
Evolution: Decomposed into nine sequential sub-steps (7.1.0 Mission Core, 7.1.1 Epic Model, 7.1.2 Mission Graph, 7.1.3 Planner Integration, 7.1.4 Persistence, 7.1.5 Event Bus, 7.1.6 Scheduler Integration, 7.1.7 AutonomousExecutor Integration, 7.1.8 Tool Integration). An internal early numbering briefly used 7.2=Epic, 7.3=Graph, 7.4=Persistence before the 7.1.x scheme settled. Implemented one sub-step at a time with vertical-slice discipline.
Final Known State: All nine sub-steps (7.1.0-7.1.8) implemented and tagged (mission-7.1-complete, amalgam-core-v1.0).
Dependencies: Mission 6.4 (autonomous executor), Mission 6.5 (agents), Mission 6.6 (scheduler/fleet)
Confidence: High
====================================================

====================================================
Decision #4a
Name: Mission 7.2 meaning A - Epic Model (early label, superseded)
Source Cluster: Cluster #4 (Mission 7.2 - ChiefAgent orchestration)
Mission Reference: 7.2
Status: Changed (absorbed into 7.1.1)
Original Idea: Early internal numbering assigned '7.2 = Epic Model' as the next deliverable after 7.1.0 Mission Core.
Evolution: Superseded when the 7.1.x sub-step scheme was adopted; the Epic Model became 7.1.1 instead.
Final Known State: This meaning of 7.2 no longer applies; it was replaced by the 7.1.1 label.
Dependencies: 7.1.0
Confidence: Medium
====================================================

====================================================
Decision #4b
Name: Mission 7.2 meaning B - Mission Engine v2 (proposed, not adopted)
Source Cluster: Cluster #2 (Mission 7 Proposed Roadmap)
Mission Reference: 7.2
Status: Proposed (not implemented under this label)
Original Idea: The alternate proposed roadmap assigned '7.2 = Mission Engine v2'.
Evolution: This label was proposed once and never used for the implemented work.
Final Known State: Not adopted. The implemented 7.2 is ChiefAgent orchestration (Decision #4c).
Dependencies: Would have depended on proposed 7.1 (Autonomous Runtime Foundation)
Confidence: High
====================================================

====================================================
Decision #4c
Name: Mission 7.2 meaning C - ChiefAgent orchestration (implemented)
Source Cluster: Cluster #4 (Mission 7.2 - ChiefAgent orchestration)
Mission Reference: 7.2
Status: Implemented
Original Idea: Establish central coordination via a ChiefAgent that decomposes and orchestrates task execution across the fleet.
Evolution: Followed the Mission 7.1 architecture freeze; engineering laws were codified before 7.2 began; implemented as ChiefAgent orchestration pipeline with task decomposition.
Final Known State: Implemented, committed, and approved.
Dependencies: Mission 7.1 (complete)
Confidence: Medium
====================================================

====================================================
Decision #5a
Name: Mission 7.3 meaning A - Planning Engine v2 (proposed, not adopted)
Source Cluster: Cluster #2 (Mission 7 Proposed Roadmap)
Mission Reference: 7.3
Status: Proposed (not implemented under this label)
Original Idea: The alternate proposed roadmap assigned '7.3 = Planning Engine v2'.
Evolution: This label was proposed once and never used for the implemented work.
Final Known State: Not adopted. The implemented 7.3 is FleetManager agent lifecycle (Decision #5b).
Dependencies: Would have depended on proposed 7.2 (Mission Engine v2)
Confidence: High
====================================================

====================================================
Decision #5b
Name: Mission 7.3 meaning B - FleetManager agent lifecycle (implemented)
Source Cluster: Cluster #5 (Mission 7.3 - FleetManager / agent lifecycle)
Mission Reference: 7.3
Status: Implemented
Original Idea: Integrate central coordination with fleet management for distributed mission execution — specifically FleetManager agent lifecycle (unregister, increment_failures, clear_failures).
Evolution: Inspection-first approach applied; spec drawn from MISSION.md; much of the discussion was a repository-stabilization effort separating genuine 7.3 changes from 7.1.8/7.2 leftovers rather than new architecture.
Final Known State: Implemented, committed, and approved.
Dependencies: Mission 7.2 (ChiefAgent orchestration), Mission 6.6 (fleet manager)
Confidence: Medium
====================================================

====================================================
Decision #6a
Name: Mission 7.4 meaning A - Persistence (early label, superseded)
Source Cluster: Cluster #6 (Mission 7.4 - Event Bus & undefined)
Mission Reference: 7.4
Status: Changed (absorbed into 7.1.4)
Original Idea: Early internal numbering assigned '7.4 = Persistence' as a deliverable after the Mission Graph.
Evolution: Superseded when the 7.1.x sub-step scheme was adopted; Persistence became 7.1.4 instead.
Final Known State: This meaning of 7.4 no longer applies; it was replaced by the 7.1.4 label.
Dependencies: 7.1.2 (Mission Graph)
Confidence: Medium
====================================================

====================================================
Decision #6b
Name: Mission 7.4 meaning B - Event Bus (proposed roadmap)
Source Cluster: Cluster #6 (Mission 7.4 - Event Bus & undefined)
Mission Reference: 7.4
Status: Proposed (never implemented as 7.4; Event Bus was implemented as 7.1.5)
Original Idea: The proposed Mission 7 roadmap assigned '7.4 = Event Bus'.
Evolution: The Event Bus was actually implemented as sub-step 7.1.5. This proposed label for a top-level 7.4 was never acted upon.
Final Known State: Not adopted as a 7.4 deliverable; functionality exists under 7.1.5.
Dependencies: Not specified
Confidence: Medium
====================================================

====================================================
Decision #6c
Name: Mission 7.4 meaning C - undefined / unspecified (final state)
Source Cluster: Cluster #6 (Mission 7.4 - Event Bus & undefined)
Mission Reference: 7.4
Status: Unknown (never specified)
Original Idea: After the prior 7.4 labels were superseded, 7.4 remained as the next mission identifier after 7.3 but was never given a specification.
Evolution: Repeated 'stabilize repo / do not start 7.4 yet' sequencing; 'if its proposal is good, that becomes 7.4'; agent (Kiro) discovered that no Mission 7.4 specification exists; tool choice (Kiro) was made for eventual 7.4 work.
Final Known State: Explicitly discovered as undefined — 'no written specification'. The identifier is reserved but carries no objective.
Dependencies: Mission 7.3 (complete)
Confidence: High
====================================================

====================================================
Decision #7
Name: Mission 7.5 - Model Router
Source Cluster: Cluster #7 (Mission 7.5 - Model Router)
Mission Reference: 7.5
Status: Proposed (not implemented)
Original Idea: Build a Model Router as a first-class subsystem — 'Model Intelligence Layer' — deciding which model handles which task.
Evolution: Recurs across multiple discussions; variously slotted as a Mission 7 first-class component and as the specific Mission 7.5 deliverable.
Final Known State: Remains a proposal only. No implementation exists under this label.
Dependencies: Not specified (would logically follow Mission 7 completion per cluster evidence)
Confidence: Medium
====================================================

====================================================
Decision #8
Name: Mission 7.6 - Workspace Intelligence
Source Cluster: Cluster #8 (Mission 7.6 - Workspace Intelligence)
Mission Reference: 7.6
Status: Proposed (not implemented)
Original Idea: A proposed roadmap item labeled 'Workspace Intelligence' for Mission 7.6.
Evolution: Appears only once as a proposed roadmap entry; no further discussion or elaboration found.
Final Known State: Proposed only. No implementation, no specification, no further detail.
Dependencies: Not specified
Confidence: Low
====================================================

====================================================
Decision #9
Name: Mission 7.7 - Fleet Intelligence
Source Cluster: Cluster #9 (Mission 7.7 - Fleet Intelligence)
Mission Reference: 7.7
Status: Proposed (not implemented)
Original Idea: A proposed roadmap item labeled 'Fleet Intelligence' for Mission 7.7.
Evolution: Appears only once as a proposed roadmap entry; no further discussion or elaboration found.
Final Known State: Proposed only. No implementation, no specification, no further detail.
Dependencies: Not specified
Confidence: Low
====================================================

====================================================
Decision #10
Name: Mission 7.8 - Production AI OS
Source Cluster: Cluster #10 (Mission 7.8 - Production AI OS)
Mission Reference: 7.8
Status: Proposed (not implemented)
Original Idea: A proposed roadmap item labeled 'Production AI OS' for Mission 7.8 — the endpoint of the proposed Mission 7 roadmap.
Evolution: Appears only once as the proposed roadmap's endpoint; no further discussion or elaboration found.
Final Known State: Proposed only. No implementation, no specification, no further detail.
Dependencies: Not specified
Confidence: Low
====================================================

====================================================
Decision #11
Name: Mission 8 - serious autonomy milestone
Source Cluster: Cluster #11 (Mission 8 planning)
Mission Reference: 8
Status: Proposed (multiple conflicting identities; not implemented)
Original Idea: Mission 8 would be the point where AMALGAM becomes the primary development system (~75-80% autonomous engineer).
Evolution: Its feature identity varies across schemes — Dependency Injection, Browser, and SQLite were each proposed at different times. The framing as 'serious autonomy' and 'workflow readiness' remains consistent.
Final Known State: Unspecified. The identifier is reserved and carries consistent framing but no settled objective or specification.
Dependencies: Mission 7 (complete)
Confidence: Medium
====================================================

====================================================
Decision #12
Name: Mission 9 - smarter/parallel agents
Source Cluster: Cluster #12 (Mission 9 planning)
Mission Reference: 9
Status: Proposed (multiple conflicting identities; not implemented)
Original Idea: Mission 9 would deliver genuinely parallel agents and reach ~90% autonomy.
Evolution: Labeled differently across schemes (API & Remote Execution vs Vision) while consistently framed as a 'smarter / parallel' milestone.
Final Known State: Unspecified. The identifier is reserved with consistent framing but no settled objective or specification.
Dependencies: Mission 8 (not specified beyond ordinal sequence)
Confidence: Low
====================================================

====================================================
Decision #13
Name: Mission 10 - AMALGAM OS v1.0 endpoint
Source Cluster: Cluster #13 (Mission 10 planning)
Mission Reference: 10
Status: Proposed (brainstorming-level; not implemented)
Original Idea: Mission 10 would be the v1.0 / 'OS' endpoint reaching ~95%+ autonomy for software engineering workflows.
Evolution: Variously tagged Voice or model-agnostic across schemes; treated as a long-horizon target; explicitly noted 'not my target' in one occurrence.
Final Known State: Unspecified. The identifier is reserved at brainstorming level with no settled objective or specification.
Dependencies: Mission 9 (not specified beyond ordinal sequence)
Confidence: Low
====================================================

====================================================
Decision #14
Name: Local model strategy - DeepSeek V4 Pro primary
Source Cluster: Cluster #14 (Local model strategy)
Mission Reference: 7
Status: Implemented (for development tooling, not as AMALGAM runtime architecture)
Original Idea: Choose DeepSeek V4 Pro (via NVIDIA API) as the primary model for Mission 7 architecture and implementation work.
Evolution: Converged on DeepSeek V4 Pro for architecture work; other models (Kimi, Nemotron) noted for specific tasks.
Final Known State: DeepSeek V4 Pro was used as the primary development model for Mission 7 work. This is a tooling decision, not an in-product architecture decision.
Dependencies: None (external to AMALGAM runtime)
Confidence: Low
====================================================

====================================================
Decision #15
Name: Provider-agnostic abstraction
Source Cluster: Cluster #15 (Cloud/local hybrid & provider routing)
Mission Reference: 7
Status: Proposed (brainstorming-level)
Original Idea: A provider abstraction layer that prevents vendor lock-in and fits naturally into the Mission 7 architecture.
Evolution: Appears as a single strand; no further elaboration or specification found.
Final Known State: Proposed only. Not implemented as an in-product subsystem.
Dependencies: Not specified
Confidence: Low
====================================================

====================================================
Decision #16
Name: Agent architecture evolution toward multi-agent orchestration
Source Cluster: Cluster #16 (Agent architecture)
Mission Reference: 7, 7.9
Status: Implemented (partially, through Mission 7.2/7.3); Proposed (7.9 Agent Operating System)
Original Idea: The agent framework would evolve in Mission 7 from single-agent toward multi-agent orchestration with multiple workers and a pipeline.
Evolution: Multi-agent orchestration was implemented via ChiefAgent (7.2) and FleetManager (7.3). A further concept 'Mission 7.9 Agent Operating System' was mentioned as a documentation/workflow system, not as a coding mission.
Final Known State: Multi-agent orchestration is implemented. The '7.9 Agent Operating System' label exists as a brainstorming reference for formalizing the agent workflow, not as a defined mission.
Dependencies: Mission 7.1 (Mission Engine), Mission 6.5 (agent framework)
Confidence: Medium
====================================================

====================================================
Decision #17
Name: Memory architecture - four domains and project-state engine
Source Cluster: Cluster #17 (Memory architecture)
Mission Reference: 7
Status: Proposed (partially implemented via .amalgam-core)
Original Idea: Mission 7 would introduce four memory domains and a project-state engine (.amalgam-core / STATE) that replaces manual/LLM memory with a structured context engineering layer.
Evolution: The .amalgam-core project-state engine was built as development tooling (STATE.json, context.py, etc.). The 'four memory domains' concept was discussed but not all domains are confirmed as distinct runtime subsystems.
Final Known State: The project-state engine (.amalgam-core) exists as dev-loop tooling. The broader 'four memory domains' and 'context engineering layer' remain partially realized proposals.
Dependencies: Not specified
Confidence: Medium
====================================================

====================================================
Decision #18
Name: Tool architecture (embedded in Mission 7.1.8)
Source Cluster: Cluster #18 (Tool architecture - empty)
Mission Reference: 7.1.8
Status: Implemented (as part of Mission 7.1.8 Tool Integration)
Original Idea: Tool architecture was not discussed as a separate thread; it was realized as the 7.1.8 Tool Integration sub-step within Mission 7.1.
Evolution: No independent tool-architecture cluster exists; the work appeared entirely within the Mission 7.1 implementation cluster.
Final Known State: Implemented as 7.1.8 (ToolWrapper, ToolResult, CapabilityValidator); however per prior recovery documents these are not wired into the main Dispatcher.
Dependencies: Mission 7.1.7 (AutonomousExecutor Integration)
Confidence: Medium
====================================================

====================================================
Decision #19
Name: Long-term scalable patterns and permanent foundations
Source Cluster: Cluster #19 (Future subsystems / long-term)
Mission Reference: 7
Status: Proposed (brainstorming/philosophy-level)
Original Idea: Current mission patterns (Initial -> Stabilization -> Optimization -> Production Readiness) must scale to all future missions and become a permanent engineering and documentation foundation.
Evolution: Recurs as a forward-looking strand insisting on scalability; mentions 'Mission 7.9 Agent Operating System' and 'documentation system as a permanent foundation'; references beyond-Mission-10 experiments.
Final Known State: These are design philosophy statements and brainstorming, not concrete implementation decisions. No specific future subsystem was defined or built from this cluster.
Dependencies: Not specified
Confidence: Medium
====================================================

---

## Mission Dependency View

Extracted only from cluster evidence. 'Not specified' means the cluster data does not establish a dependency.

### Mission 7.1:
- Depends on: Mission 6.4 (autonomous executor), Mission 6.5 (agents), Mission 6.6 (scheduler/fleet)
- Delivers: Mission Engine (7.1.0-7.1.8)
- Status: Implemented

### Mission 7.2:
- Depends on: Mission 7.1 (complete)
- Delivers: ChiefAgent orchestration pipeline
- Status: Implemented
- Note: Two other meanings existed (Epic Model = absorbed into 7.1.1; Mission Engine v2 = proposed, not adopted)

### Mission 7.3:
- Depends on: Mission 7.2 (ChiefAgent), Mission 6.6 (fleet manager)
- Delivers: FleetManager agent lifecycle integration
- Status: Implemented
- Note: One other meaning existed (Planning Engine v2 = proposed, not adopted)

### Mission 7.4:
- Depends on: Mission 7.3 (complete)
- Delivers: UNDEFINED — never specified
- Status: Unknown / Reserved
- Note: Three historical meanings (Persistence = absorbed into 7.1.4; Event Bus = absorbed into 7.1.5; undefined = final state). No specification exists.

### Mission 7.5:
- Depends on: Not specified (would logically follow Mission 7 completion)
- Delivers: Model Router (proposed)
- Status: Proposed only

### Mission 7.6:
- Depends on: Not specified
- Delivers: Workspace Intelligence (proposed)
- Status: Proposed only — single mention, no elaboration

### Mission 7.7:
- Depends on: Not specified
- Delivers: Fleet Intelligence (proposed)
- Status: Proposed only — single mention, no elaboration

### Mission 7.8:
- Depends on: Not specified
- Delivers: Production AI OS (proposed)
- Status: Proposed only — single mention, no elaboration

### Mission 8:
- Depends on: Mission 7 (complete)
- Delivers: Undefined (Dependency Injection / Browser / SQLite proposed at various times)
- Status: Proposed — consistent framing as 'serious autonomy / ~75-80%' but no settled specification
- Note: Multiple conflicting identities, not resolved

### Mission 9:
- Depends on: Mission 8 (ordinal sequence only)
- Delivers: Undefined (API & Remote Execution / Vision proposed at various times)
- Status: Proposed — consistent framing as 'smarter / parallel / ~90%' but no settled specification
- Note: Multiple conflicting identities, not resolved

### Mission 10:
- Depends on: Mission 9 (ordinal sequence only)
- Delivers: Undefined (AMALGAM OS v1.0 / Voice / model-agnostic proposed at various times)
- Status: Proposed — brainstorming-level long-horizon target, no settled specification
- Note: Multiple conflicting identities, not resolved; explicitly noted 'not my target' in one occurrence

---

Total decisions: 19 (with 7.2 split into 4a/4b/4c, 7.3 split into 5a/5b, and 7.4 split into 6a/6b/6c = 24 distinct decision entries)
Clusters represented: All 19 (including empty Cluster 18, recorded as Decision #18)
Conflicting versions preserved: 7.2 (3 versions), 7.3 (2 versions), 7.4 (3 versions)
Nothing invented. Nothing resolved. Evolution preserved.
