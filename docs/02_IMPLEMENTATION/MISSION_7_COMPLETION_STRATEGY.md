# MISSION_7_COMPLETION_STRATEGY.md

Purpose: define the closure path for Mission 7 — the sequence required to close the gaps that already exist.

Sources: MISSION_7_GAP_ANALYSIS.md, MISSION_7_IMPLEMENTATION_MATRIX.md, MASTER_ARCHITECTURE_PLAN.md.

Scope rules honored: no new features, no Mission 7.4 design, no roadmap expansion. This document only
orders the closure of the existing architecture. The unbuilt proposed capabilities (7.4-7.8) are explicitly
OUT OF SCOPE for closure — defining or building them would be new work and is not part of closing the
implemented Mission 7.

---

## 1. Mission 7 completion definition

Mission 7 is "architecturally complete" when the work already implemented (7.0 Architecture Lock through
7.3) reaches a sound, runnable, verified, and safe state that satisfies Mission 7's own success criteria and
the Definition of Done (MASTER_ARCHITECTURE_PLAN §10). Concretely, completion requires that:

- All implemented 7.0-7.3 work is committed and attributed (no uncommitted sub-steps; label conflicts resolved).
- The multi-agent / mission loop is reachable and exercised from the application entry point (not only by
  direct instantiation).
- The full test suite is re-run from the repository and passes with no regressions (an authoritative count
  is established; the stack becomes VERIFIED rather than claimed).
- The safety layer that Mission 7 already produced (ToolWrapper / CapabilityValidator) and kernel-path
  security boundaries are on the live path.
- The end-to-end autonomous loop (plan -> execute -> evaluate -> reflect -> retry -> mission orchestration
  -> deliver) demonstrably runs.

Note: 7.4-7.8 remain RESERVED / UNDEFINED (MASTER §5). They are NOT required to close the implemented Mission
7 and are not addressed here.

---

## 2. Current completion score

No numeric score is invented; each dimension is rated from the sources.

- Implemented: SUBSTANTIAL. 7.1.0-7.1.8 plus 7.2 (ChiefAgent) and 7.3 (FleetManager) code is present
  (7.1.1/7.1.2/7.1.3 files exist but are uncommitted). 7.4-7.8 are not implemented (out of scope).
  Evidence: MATRIX (7.1.x/7.2/7.3); GAP_ANALYSIS §1.
- Integrated: PARTIAL. The Mission Engine is INTEGRATED as a subsystem but is NOT reachable from main.py;
  the 7.1.8 tool-safety layer is CODE EXISTS (not on the dispatch path); the 7.3 distributed path is CODE
  EXISTS (no in-app worker loop). Evidence: MATRIX; GAP_ANALYSIS §3; CURRENT_ARCHITECTURE §14.1/§14.2/§14.4.
- Verified: NONE. No test suite was re-run; all counts (through 806 / 910) are conversation claims.
  Evidence: MATRIX summary; MASTER_ARCHITECTURE_PLAN §1 (authoritative test count UNKNOWN).
- Production-ready: NO. Entry-point wiring, live-path safety boundaries, and verification are all unmet;
  a latent research bug exists. Evidence: GAP_ANALYSIS §3/§4.

---

## 3. Blocking closure items

These are the BLOCKING gaps from GAP_ANALYSIS that must be closed before Mission 7 can complete.

### Verification baseline missing
- Current problem: No Mission 7 item is VERIFIED; every test figure is an unre-run claim.
- Why it blocks Mission 7 completion: The Definition of Done requires tests that pass and are verified
  against the repository; without a real baseline, no other closure item can be confirmed.

### Multi-agent / mission layer not reachable from the entry point
- Current problem: main.py runs only the single-task path; ChiefAgent / OrchestratorAgent / MissionExecutor
  are reachable only by direct instantiation.
- Why it blocks Mission 7 completion: Mission 7's defining autonomous loop cannot be invoked by running the
  application, so the mission's success criteria are unreachable end-to-end.

### No in-application WorkPool worker loop
- Current problem: Distributed mission execution depends on a worker calling WorkPool.steal_task; none exists
  in the application, so it relies on external/test workers or a timeout.
- Why it blocks Mission 7 completion: The distributed half of the fleet/mission execution (a core 7.3
  deliverable) does not actually run autonomously.

### 7.1.8 tool-safety layer not on the live dispatch path
- Current problem: ToolWrapper (timeout/retry) and CapabilityValidator exist but the kernel Dispatcher calls
  tools directly.
- Why it blocks Mission 7 completion: Autonomous tool execution runs without the safety guarantees 7.1.8 was
  meant to deliver, so the mission's own deliverable is not effective at runtime.

### Latent ResearchAgent bug (FileTool.list_files)
- Current problem: ResearchAgent._research_files calls FileTool.list_files, which does not exist; the call is
  swallowed as an error.
- Why it blocks Mission 7 completion: The "understand the project" stage of the autonomous loop is partially
  broken, so the loop cannot reliably run end-to-end.

### Kernel-path security surface unguarded
- Current problem: PythonExecutor uses exec, Calculator evaluates expressions, and FileTool has no
  workspace-boundary enforcement on the kernel path; guarding exists only in the agent path.
- Why it blocks Mission 7 completion: Unattended autonomous file/code operations are unsafe on the live path,
  which is incompatible with the production-grade autonomy Mission 7 targets.

### End-to-end autonomous loop not demonstrably closed
- Current problem: The loop's parts are INTEGRATED as a subsystem but are neither entry-wired nor verified.
- Why it blocks Mission 7 completion: This is the aggregate outcome of the items above; until it is
  demonstrable, Mission 7 does not meet its own success criteria. (Closing the items above closes this.)

---

## 4. Non-blocking technical debt

These are IMPORTANT or DEFERRED gaps (GAP_ANALYSIS §2/§4). They should be closed for a clean Mission 7, but
they do not, on their own, prevent the autonomous loop from running.

- Attribution debt: 7.1.1 / 7.1.2 / 7.1.3 lack dedicated commits; the two 7.1.6 commits describe different
  integrations (PlannerAgent vs Scheduler); 7.2 has no standalone commit. (IMPORTANT)
- Duplicated / overlapping routing and planning (Router / CapabilityRouter / ModelSelector / KnowledgeRouter;
  planning in three places). (IMPORTANT)
- "Reasoning" pillar has no dedicated component. (IMPORTANT)
- Dev-loop vs application divergence; STATE.json stale and internally contradictory (reports M7.2 in_progress,
  gpt-4o provider vs the app's Ollama-only config). (IMPORTANT)
- Unexamined kernel files (kernel/scheduler.py, kernel/event_bus.py, kernel/permissions.py) — behavior UNKNOWN. (IMPORTANT)
- Preprocessor / Pipeline implemented but not invoked; legacy brain/orchestrator.py off the live path. (DEFERRED)
- No EngineRegistry; placeholder services (internet.py, knowledge.py); version drift (APP_VERSION 0.3.0). (DEFERRED)

Out of scope (not closure debt): 7.5 / 7.6 / 7.7 / 7.8 are unbuilt PROPOSED capabilities and 7.4 is UNDEFINED;
these are future/reserved, not debt of the implemented stack, and are not addressed by this closure.

---

## 5. Recommended closure order

Ordered by dependency. Each phase closes existing gaps only; it does not design fixes, add features, or
define 7.4. A phase's purpose is stated in terms of the gap it closes.

Phase 1 — Establish trustworthy baseline
- Re-run the full test suite from the repository to replace claimed counts with a VERIFIED baseline (closes
  the "verification baseline missing" blocker).
- Reconcile attribution: commit / attribute 7.1.1-7.1.3 and resolve the 7.1.6 description conflict (closes
  the attribution debt so the baseline maps to real, labeled work).
- Close the latent ResearchAgent FileTool.list_files bug (a known correctness defect that the baseline will surface).
Rationale: nothing downstream can be trusted until the true test state and correct attribution exist.

Phase 2 — Make the loop runnable on one path
- Wire the multi-agent / mission layer to the application entry point (closes the entry-point disconnect).
- Put the 7.1.8 tool-safety layer (ToolWrapper / CapabilityValidator) on the kernel dispatch path (closes the
  "tool-safety not on live path" blocker).
- Provide an in-application driver for the WorkPool so distributed execution runs (closes the "no worker loop"
  blocker) — or, if the distributed path is explicitly scoped out, document that decision.
Rationale: integration must precede safety hardening and end-to-end demonstration; there is no runnable loop to harden or verify until this is done.

Phase 3 — Harden the live path
- Enforce kernel-path security boundaries for PythonExecutor / Calculator / FileTool (closes the "kernel-path
  security surface" blocker).
Rationale: unattended autonomy over the now-runnable path must be safe before it is exercised as complete.

Phase 4 — Demonstrate, re-verify, and freeze
- Demonstrate the end-to-end autonomous loop running from the entry point (closes the aggregate "loop not
  demonstrably closed" blocker).
- Re-run the full suite to confirm no regressions were introduced by Phases 1-3.
- Synchronize documentation (correct STATE.json and the version string) and then freeze/tag the result.
Rationale: closure is only real once the integrated, hardened loop is shown to run and the suite is green.

Non-blocking debt (Section 4) may be addressed opportunistically within these phases or in a dedicated
cleanup pass; it does not gate the phases above except where noted (attribution in Phase 1).

---

## 6. Exit criteria

Mission 7 can officially close only when ALL of the following are true:

1. Every implemented 7.0-7.3 unit is committed and attributed; the 7.1.6 label conflict is resolved; no
   claimed-complete sub-step remains uncommitted.
2. The full test suite has been re-run from the repository and passes with no regressions; the authoritative
   test count is recorded (the stack is VERIFIED, not claimed).
3. The multi-agent / mission loop is reachable and has been exercised from the application entry point.
4. The 7.1.8 tool-safety layer (ToolWrapper / CapabilityValidator) is on the live dispatch path.
5. Distributed execution is driven by an in-application mechanism, OR the distributed path is explicitly and
   documentedly scoped out of Mission 7.
6. Kernel-path security boundaries (PythonExecutor / Calculator / FileTool) are enforced.
7. The latent ResearchAgent FileTool.list_files defect is closed.
8. The end-to-end autonomous loop (plan -> execute -> evaluate -> reflect -> retry -> mission orchestration
   -> deliver) has been demonstrated running.
9. Documentation is synchronized (STATE.json accurate; APP_VERSION corrected) and the architecture is
   preserved and audited, then frozen/tagged.
10. 7.4-7.8 are recorded as remaining RESERVED / UNDEFINED and are confirmed NOT to be a prerequisite for
    closing the implemented Mission 7.

When items 1-9 hold and item 10 is acknowledged, the implemented Mission 7 is architecturally complete and may
be frozen. This document defines only that closure; it introduces no new features and no Mission 7.4 design.
