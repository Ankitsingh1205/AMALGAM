# MISSION_7_EXECUTION_CHECKLIST.md

Purpose: an executable checklist derived from MISSION_7_COMPLETION_STRATEGY.md and MISSION_7_GAP_ANALYSIS.md.

Rules honored: no new features; no Mission 7.4 design; every task maps to an existing documented gap. Each
task cites its gap source. Nothing here defines 7.4-7.8 (RESERVED / UNDEFINED, out of scope for closure).

Legend: each task lists the source gap, the Evidence required to consider it done, and the Completion condition.

---

## Phase 1 — Establish trustworthy baseline
(Closes: verification-baseline, attribution debt, latent ResearchAgent bug.)

[ ] Task: Re-run the full test suite from the repository and record the authoritative result.
- Maps to gap: "No Mission 7 item is VERIFIED" (GAP_ANALYSIS §2; STRATEGY §3, Phase 1).
- Evidence required: a captured pytest run (pass/fail totals and runtime) taken from the current tree, not a conversation claim.
- Completion condition: an authoritative test count exists and is recorded; the prior claimed figures (e.g., 806 / 910) are replaced by a re-run result.

[ ] Task: Commit and attribute the uncommitted Mission-Engine sub-steps 7.1.1, 7.1.2, 7.1.3.
- Maps to gap: "7.1.1 / 7.1.2 / 7.1.3 lack dedicated commits" (GAP_ANALYSIS §2; MATRIX 7.1.1-7.1.3 PARTIAL).
- Evidence required: repository commits (or documented attribution) tying epic.py / graph.py / planner integration to 7.1.1 / 7.1.2 / 7.1.3.
- Completion condition: no claimed-complete 7.1 sub-step remains without repository attribution.

[ ] Task: Resolve the 7.1.6 commit-description conflict.
- Maps to gap: "7.1.6 commit-description conflict (PlannerAgent vs Scheduler)" (GAP_ANALYSIS §2; MATRIX 7.1.6).
- Evidence required: a single reconciled statement of what 7.1.6 delivered, consistent with the code and commits.
- Completion condition: the record no longer contains two contradictory descriptions of 7.1.6.

[ ] Task: Close the latent ResearchAgent FileTool.list_files defect.
- Maps to gap: "Latent ResearchAgent bug (FileTool.list_files does not exist)" (GAP_ANALYSIS §4; CURRENT_ARCHITECTURE §14.6).
- Evidence required: the research file-listing path executes without the swallowed error; covered by a test.
- Completion condition: ResearchAgent's file-research stage runs correctly and the fix is reflected in the re-run suite.

---

## Phase 2 — Make the loop runnable on one path
(Closes: entry-point disconnect, tool-safety layer off the dispatch path, no WorkPool worker loop.)

[ ] Task: Wire the multi-agent / mission layer to the application entry point.
- Maps to gap: "Multi-agent / mission layer not reachable from the entry point" (GAP_ANALYSIS §3; CURRENT_ARCHITECTURE §14.1).
- Evidence required: an invocation from main.py (the application entry point) that reaches ChiefAgent / MissionExecutor without direct instantiation.
- Completion condition: the mission / multi-agent path is reachable by running the application.

[ ] Task: Place the 7.1.8 tool-safety layer on the live dispatch path.
- Maps to gap: "Mission-7.1.8 tool-safety layer not on the live dispatch path" (GAP_ANALYSIS §3; CURRENT_ARCHITECTURE §14.4; MATRIX 7.1.8 CODE EXISTS).
- Evidence required: the kernel Dispatcher routes tool calls through ToolWrapper / CapabilityValidator (timeout / retry / validation), confirmed by a test.
- Completion condition: tool execution on the live path carries the 7.1.8 safety guarantees.

[ ] Task: Provide an in-application driver for the WorkPool (or explicitly scope the distributed path out).
- Maps to gap: "No in-application WorkPool worker loop" (GAP_ANALYSIS §3; CURRENT_ARCHITECTURE §14.2; MATRIX 7.3 distributed = CODE EXISTS).
- Evidence required: either a running in-app worker that calls WorkPool.steal_task, OR a documented decision that the distributed path is out of scope for Mission 7.
- Completion condition: distributed execution runs from within the application, or its exclusion is recorded.

---

## Phase 3 — Harden the live path
(Closes: kernel-path security surface.)

[ ] Task: Enforce kernel-path security boundaries for PythonExecutor, Calculator, and FileTool.
- Maps to gap: "Kernel-path security surface unguarded" (GAP_ANALYSIS §4; CURRENT_ARCHITECTURE §14.11).
- Evidence required: workspace-boundary / execution guards apply on the kernel path (not only the agent path), confirmed by tests exercising rejection cases.
- Completion condition: autonomous file/code operations on the live path are bounded and cannot escape the workspace or run unguarded.

---

## Phase 4 — Demonstrate, re-verify, and freeze
(Closes: end-to-end autonomous loop not demonstrably closed; synchronizes documentation; freezes.)

[ ] Task: Demonstrate the end-to-end autonomous loop from the entry point.
- Maps to gap: "End-to-end autonomous loop not demonstrably closed" (GAP_ANALYSIS §5; STRATEGY §3).
- Evidence required: a recorded run showing plan -> execute -> evaluate -> reflect -> retry -> mission orchestration -> deliver invoked from the application.
- Completion condition: the loop that defines Mission 7 is shown to run end-to-end.

[ ] Task: Re-run the full suite to confirm no regressions from Phases 1-3.
- Maps to gap: verification (GAP_ANALYSIS §2) applied after integration/hardening (STRATEGY §5, Phase 4).
- Evidence required: a green re-run with no regressions against the Phase 1 baseline.
- Completion condition: the suite passes with no regressions introduced by the closure work.

[ ] Task: Synchronize documentation (STATE.json and APP_VERSION).
- Maps to gap: "Dev-loop vs application divergence; stale STATE.json" and "version drift" (GAP_ANALYSIS §4; CURRENT_ARCHITECTURE §14.9/§14.13).
- Evidence required: STATE.json reflects the true current mission/tests/provider (Ollama-only), and APP_VERSION matches the released tag line.
- Completion condition: the project's status and version records are accurate and internally consistent.

[ ] Task: Audit against the architecture, then freeze/tag the result.
- Maps to gap: Definition of Done (MASTER_ARCHITECTURE_PLAN §10) applied at closure (STRATEGY §5, Phase 4).
- Evidence required: an architecture audit confirming layer boundaries / dependency direction preserved, followed by a commit/tag of the frozen state.
- Completion condition: the closed Mission 7 state is audited and frozen.

---

## Final Mission 7 closure checklist

All must be checked before Mission 7 officially closes (mirrors STRATEGY §6 exit criteria):

[ ] Every implemented 7.0-7.3 unit is committed and attributed; the 7.1.6 conflict is resolved; no
    claimed-complete sub-step remains uncommitted. (Phase 1)
[ ] The full test suite has been re-run from the repository and passes with no regressions; the authoritative
    count is recorded (VERIFIED, not claimed). (Phase 1 + Phase 4)
[ ] The multi-agent / mission loop is reachable and exercised from the application entry point. (Phase 2)
[ ] The 7.1.8 tool-safety layer (ToolWrapper / CapabilityValidator) is on the live dispatch path. (Phase 2)
[ ] Distributed execution runs from an in-application mechanism, OR the distributed path is explicitly and
    documentedly scoped out. (Phase 2)
[ ] Kernel-path security boundaries (PythonExecutor / Calculator / FileTool) are enforced. (Phase 3)
[ ] The latent ResearchAgent FileTool.list_files defect is closed. (Phase 1)
[ ] The end-to-end autonomous loop has been demonstrated running from the entry point. (Phase 4)
[ ] Documentation is synchronized (STATE.json accurate; APP_VERSION corrected) and the architecture is
    audited, then frozen/tagged. (Phase 4)
[ ] 7.4-7.8 are recorded as remaining RESERVED / UNDEFINED and confirmed NOT to be a prerequisite for closing
    the implemented Mission 7. (scope acknowledgment; no 7.4 design performed)

When every box above is checked, the implemented Mission 7 is architecturally complete and may be frozen.
This checklist introduces no new features and no Mission 7.4 design; each task closes an existing documented gap.
