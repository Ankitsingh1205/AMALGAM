# LOOP.md

# AMALGAM Engineering Loop

Version: 1.0
Status: Active
Scope: `.amalgam-core/`

This document defines the permanent engineering loop followed by every coding model working on AMALGAM.

It is the canonical execution algorithm for all engineering work. Every stage must be executed in order. No stage may be skipped. No stage may be reordered.

This document supports interruption recovery, checkpoint resumption, and deterministic replay.

---

# Loop Overview

The engineering loop consists of 17 sequential stages organized into four phases:

| Phase | Stages | Purpose |
|-------|--------|---------|
| UNDERSTAND | 1-5 | Repository Inspection, Architecture Analysis, Existing Code Discovery, Dependency Discovery, Reuse Decision |
| PLAN | 6 | Planning — what to modify and how |
| EXECUTE | 7-9 | Implementation, Static Validation, Testing |
| RECOVER | 10-11 | Failure Recovery, Regression Testing |
| COMPLETE | 12-17 | Documentation Update, Checkpoint Save, State Update, Mission Update, History Update, Completion |

Each stage is defined with:
- Purpose
- Inputs
- Outputs
- Failure handling
- Resume behaviour
- Checkpoint behaviour

---

# Dependency Graph

```
   1 ──► 2 ──► 3 ──► 4 ──► 5 ──► 6 ──► 7 ──► 8 ──► 9
                                                     │
                                               ┌─────▼─────┐
                                               │  SUCCESS?  │
                                               └─────┬─────┘
                                         ┌────────────┴────────────┐
                                         ▼ YES                     ▼ NO
                                  12 ──► 13 ──► 14       10 ──► 11
                                         │                     │
                                         ▼                     │ (retry)
                                  15 ──► 16 ──► 17        ┌───▼────┐
                                                           │ RETURN  │
                                                           │ TO 7     │
                                                           └──────────┘
```

---

# Checkpoint Architecture

Each stage writes its output to a checkpoint slot in `.amalgam-core/STATE.json`. On interruption, the loop resumes from the last completed stage by reading the checkpoint pointer.

Checkpoint format:

```json
{
  "loop": {
    "phase": "EXECUTE",
    "stage": 7,
    "stage_name": "Implementation",
    "mission_id": "M7.1.5",
    "goal_id": "uuid",
    "retry_count": 0,
    "max_retries": 3,
    "started_at": "ISO8601",
    "last_success_at": "ISO8601",
    "checkpoints": {
      "stage_1": "completed",
      "stage_2": "completed",
      "stage_3": "completed",
      "stage_4": "completed",
      "stage_5": "completed",
      "stage_6": "completed",
      "stage_7": "in_progress",
      "stage_8": "pending",
      "stage_9": "pending",
      "stage_10": "pending",
      "stage_11": "pending",
      "stage_12": "pending",
      "stage_13": "pending",
      "stage_14": "pending",
      "stage_15": "pending",
      "stage_16": "pending",
      "stage_17": "pending"
    },
    "artifacts": {
      "inspection_report": {},
      "architecture_analysis": {},
      "code_discovery": {},
      "dependency_discovery": {},
      "reuse_decision": {},
      "plan": {},
      "implementation_summary": {},
      "static_validation": {},
      "test_result": {},
      "recovery_log": [],
      "regression_result": {}
    }
  }
}
```

On startup, the model reads `STATE.json`. If `loop.stage` is greater than 0, the loop resumes from that stage using the stored artifacts.

---

# Stage Definitions

---

## Stage 1: Repository Inspection

### Phase
UNDERSTAND

### Purpose
Establish a complete understanding of the project structure, documentation, current mission, current task, and repository state before any modification.

### Inputs
- `.amalgam-core/STATE.json` — prior loop state (if resuming, skip to last completed stage; if fresh, stage pointer is 0)
- The repository root directory `C:\AMALGAM`

### Operations
1. Inspect project root directory listing.
2. Read `AGENTS.md` (root level).
3. Read `ARCHITECTURE.md`.
4. Read `MISSION.md`.
5. Read `TASK.md`.
6. Read `.amalgam-core/AGENTS.md`.
7. Read `.amalgam-core/STATE.json` to determine if resuming or starting fresh.
8. Inspect `git status`.
9. Inspect `git log --oneline -10`.
10. Record current branch, current HEAD, recent commits.
11. Record current test count baseline from `MISSION.md`.
12. Record current mission and milestone from `MISSION.md` and `TASK.md`.

### Outputs
Structured inspection report containing:
- Current branch name
- Current commit hash
- Recent 10 commit messages
- Git status (clean vs dirty)
- Current mission ID, milestone, objective
- Current test count baseline
- Identified documentation files and their status
- Repository structure overview (layers present)
- Resumption decision (fresh start or resume from stage N)

### Failure Handling
If `git status` fails: record error, continue with manual inspection.
If a documentation file is missing: report missing file explicitly. Do not fabricate content.
If repository root cannot be read: escalate — this is unrecoverable.

### Resume Behaviour
If resuming from a completed Stage 1, skip inspection and load the stored `artifacts.inspection_report` from `STATE.json`. Verify that the stored report still matches current repository state (branch, HEAD). If mismatched, re-execute Stage 1.

### Checkpoint Behaviour
On completion, write `artifacts.inspection_report` to `STATE.json`. Set `checkpoints.stage_1` to `completed`. Set `loop.stage` to `2`.

---

## Stage 2: Architecture Analysis

### Phase
UNDERSTAND

### Purpose
Identify the architectural layer(s) affected by the current task. Verify that proposed modifications will preserve layer boundaries and the import DAG.

### Inputs
- Stage 1 output (inspection report)
- `ARCHITECTURE.md` — layer ownership table, dependency direction diagram, import rules
- `TASK.md` — scope, expected file changes, constraints

### Operations
1. From `TASK.md`, extract the expected file changes.
2. For each file, determine its architectural layer using the layer ownership table.
3. Verify that the file's layer is consistent with the task scope.
4. Trace the dependency direction for each affected layer.
5. Verify that no proposed change violates:
   - Layer boundaries (lower layers importing higher layers)
   - Import DAG (circular dependencies)
   - Ownership rules (one layer owns one responsibility)
6. Identify any cross-layer interactions required by the task.
7. Flag any architectural concerns for escalation.

### Outputs
Structured architecture analysis containing:
- Affected layers (e.g., Brain, Kernel, Services, Tools)
- Layer ownership verification for each file
- Dependency path verification
- Import rule compliance check (pass/fail per proposed import)
- Architectural concerns flagged (if any)
- Confirmation that proposed changes are architecturally sound

### Failure Handling
If a proposed change violates layer boundaries: escalate. Do not proceed. Record violation explicitly.
If affected layers cannot be determined: escalate. Do not fabricate layer assignments.
If `ARCHITECTURE.md` is inconsistent with repository: report discrepancy. Do not proceed.

### Resume Behaviour
If resuming from a completed Stage 2, load `artifacts.architecture_analysis` from `STATE.json`. Verify the analysis against the current `TASK.md` scope. If scope has changed, re-execute Stage 2.

### Checkpoint Behaviour
On completion, write `artifacts.architecture_analysis` to `STATE.json`. Set `checkpoints.stage_2` to `completed`. Set `loop.stage` to `3`.

---

## Stage 3: Existing Code Discovery

### Phase
UNDERSTAND

### Purpose
Search the repository for existing implementations that overlap with the current task. Identify reusable modules, classes, functions, utilities, patterns, and abstractions before writing any new code.

### Inputs
- Stage 1 output (repository structure)
- Stage 2 output (affected layers)
- `TASK.md` — scope and expected deliverables

### Operations
1. For each expected deliverable, search the repository.
2. Search by name: glob patterns matching the deliverable concept.
3. Search by content: grep for related function/class definitions.
4. Search in the affected layers first, then in adjacent layers.
5. Search in `tests/` for related test patterns.
6. Identify:
   - Exact matches (implementation already exists)
   - Partial matches (extendable implementations)
   - Related patterns (similar abstractions that could inform design)
   - Gaps (no existing implementation)
7. For each match, record: module path, class/function name, public API, test coverage.

### Outputs
Structured code discovery report containing:
- Exact matches found: module path, class name, public methods, reuse recommendation
- Partial matches found: module path, class name, methods that can be extended, extension recommendation
- Related patterns found: module path, pattern description, design guidance
- Gaps identified: no existing implementation, new module required
- Total reuse potential (percentage of task that can leverage existing code)

### Failure Handling
If a search fails (glob/grep error): retry once with broader scope. If persists, note failure and proceed with manual inspection.
If a match is found but its API is uncertain: read the module. Do not assume.

### Resume Behaviour
If resuming from a completed Stage 3, load `artifacts.code_discovery` from `STATE.json`. Re-verify top 3 matches against current repository state. If code has changed since discovery, re-execute Stage 3.

### Checkpoint Behaviour
On completion, write `artifacts.code_discovery` to `STATE.json`. Set `checkpoints.stage_3` to `completed`. Set `loop.stage` to `4`.

---

## Stage 4: Dependency Discovery

### Phase
UNDERSTAND

### Purpose
Identify all dependencies that the proposed implementation will touch. Map import relationships, caller-callee chains, and transitive dependencies.

### Inputs
- Stage 2 output (affected layers, import compliance)
- Stage 3 output (existing code matches)
- `TASK.md` — expected file changes

### Operations
1. For each expected-modified file, identify all current imports.
2. For each expected-new file, enumerate proposed imports.
3. For each existing module to be extended, identify its importers (who depends on it).
4. For each public API to be preserved, identify all callers.
5. Build a dependency map: for each proposed change, list every module that could be transitively affected.
6. Verify that no proposed import creates a forbidden pattern (per `ARCHITECTURE.md` import rules).
7. Verify that no proposed import introduces circularity.

### Outputs
Structured dependency discovery report containing:
- Current imports per affected file
- Proposed imports per new/changed file
- Caller-callee map for each public API
- Transitive dependency graph
- Forbidden import check results
- Circularity check results
- Full affected-module list (transitive closure)

### Failure Handling
If import analysis fails on a file: read the file directly. Do not skip.
If a caller cannot be identified: search with multiple patterns. If still not found, report uncertainty.
If a proposed import creates a forbidden pattern: redesign. Do not proceed.

### Resume Behaviour
If resuming from a completed Stage 4, load `artifacts.dependency_discovery` from `STATE.json`. Spot-check top 5 dependency edges against current code. If dependencies have changed, re-execute Stage 4.

### Checkpoint Behaviour
On completion, write `artifacts.dependency_discovery` to `STATE.json`. Set `checkpoints.stage_4` to `completed`. Set `loop.stage` to `5`.

---

## Stage 5: Reuse Decision

### Phase
UNDERSTAND

### Purpose
Make a final determination on what to reuse, what to extend, and what to create. This is the gate between UNDERSTAND and PLAN. No implementation begins before this decision is recorded.

### Inputs
- Stage 1 output (inspection report)
- Stage 2 output (architecture analysis)
- Stage 3 output (code discovery)
- Stage 4 output (dependency discovery)
- `.amalgam-core/AGENTS.md` — reuse policy, refactoring policy, file policy

### Operations
1. For each expected deliverable, apply the reuse decision algorithm:
   - If exact match exists: **REUSE**. No new code. Only integration wiring permitted.
   - If partial match exists: **EXTEND**. Add functionality to existing module. Preserve all existing public APIs.
   - If no match but pattern exists: **CREATE** by following the existing pattern. New module in correct layer.
   - If no match and no pattern: **CREATE** with architectural justification. New module in correct layer.
2. For each REUSE decision: verify the reused module's test coverage.
3. For each EXTEND decision: list the specific methods/classes to extend. Verify backward compatibility.
4. For each CREATE decision: justify architectural placement. Verify no duplication.
5. Aggregate: produce a final action list (reuse/extension/create per deliverable).

### Outputs
Structured reuse decision report containing:
- Per-deliverable decision: REUSE | EXTEND | CREATE
- For REUSE: module path, integration wiring needed, test baseline
- For EXTEND: module path, exact classes/methods to extend, compatibility verification
- For CREATE: new module path, architectural justification, anti-duplication verification
- Final action list: ordered by dependency (create modules first, then extend, then wire integration)
- Reuse compliance confirmation (no duplication created)

### Failure Handling
If a deliverable has no viable reuse/extension path and no architectural justification for creation: escalate. Do not fabricate.
If backward compatibility cannot be verified for an extension: escalate. Do not proceed.
If duplication is detected: redesign immediately. Do not proceed.

### Resume Behaviour
If resuming from a completed Stage 5, load `artifacts.reuse_decision` from `STATE.json`. Verify against current Stage 3 and Stage 4 outputs. If codebase has changed, re-execute Stage 5.

### Checkpoint Behaviour
On completion, write `artifacts.reuse_decision` to `STATE.json`. Set `checkpoints.stage_5` to `completed`. Set `loop.stage` to `6`. Transition `loop.phase` to `PLAN`.

---

## Stage 6: Planning

### Phase
PLAN

### Purpose
Produce a detailed implementation plan that specifies exact modifications, creation order, validation steps, and success criteria. This plan becomes the executable blueprint for Stages 7-17.

### Inputs
- Stage 2 output (architecture analysis — affected layers)
- Stage 3 output (code discovery — existing modules)
- Stage 4 output (dependency discovery — affected modules)
- Stage 5 output (reuse decision — action list)
- `TASK.md` — scope, constraints, success criteria, validation checklist

### Operations
1. Order the final action list from Stage 5 by dependency: create new modules before modifying existing ones; modify callees before modifying callers.
2. For each action, produce a micro-plan:
   - Exact file(s) to modify or create
   - Exact lines/sections to change (from code discovery)
   - Exact imports to add/remove (from dependency discovery)
   - Public APIs to preserve/add
   - Tests to add (identify test file and test function names)
3. Validate the plan against constraints:
   - No scope creep: every action maps to a task deliverable
   - No breaking API changes: preserved public APIs remain unchanged
   - Layer boundaries: no cross-layer violations
   - Import DAG: no circular or forbidden imports
4. Produce a complete validation checklist derived from `.amalgam-core/AGENTS.md` quality checklist.
5. Estimate affected test count and identify which existing tests may be impacted.

### Outputs
Structured implementation plan containing:
- Ordered action sequence (create/extend/integrate)
- Per-action micro-plan: files, lines, imports, APIs, tests
- Constraint compliance verification
- Full validation checklist (aligns with `.amalgam-core/AGENTS.md`)
- Identified test files to create/modify
- Expected total test count after implementation
- Success criteria (from `TASK.md`)

### Failure Handling
If plan ordering creates a dependency cycle: reorder. If cycle is unresolvable, escalate.
If a required test file cannot be identified: flag explicitly. Do not skip.
If the plan exceeds task scope: trim to scope boundaries. Record what was trimmed and why.

### Resume Behaviour
If resuming from a completed Stage 6, load `artifacts.plan` from `STATE.json`. Verify plan against current codebase state. If code has changed since plan, re-execute Stages 3-6.

### Checkpoint Behaviour
On completion, write `artifacts.plan` to `STATE.json`. Set `checkpoints.stage_6` to `completed`. Set `loop.stage` to `7`. Transition `loop.phase` to `EXECUTE`.

---

## Stage 7: Implementation

### Phase
EXECUTE

### Purpose
Execute the implementation plan: create new files, modify existing files, add tests. This is the only stage that modifies source code. Every modification must follow the plan, remain minimal, and preserve existing public APIs.

### Inputs
- Stage 6 output (implementation plan — ordered action sequence with micro-plans)
- Stage 3 output (code discovery — existing module contents for modification reference)
- Stage 5 output (reuse decision — REUSE/EXTEND/CREATE classification)
- `.amalgam-core/AGENTS.md` — coding standards, security policy, error handling policy

### Operations
For each action in the ordered sequence:

**For CREATE actions:**
1. Write the new file in the correct architectural layer.
2. Apply full coding standards: explicit imports, type hints, docstrings, no dead code.
3. Verify imports resolve against the project dependency direction.
4. Verify no duplication of existing code (cross-check against Stage 3 output).

**For EXTEND actions:**
1. Read the existing file fully before any modification.
2. Identify public APIs that must be preserved (from Stage 4 dependency discovery).
3. Add new code within existing abstractions.
4. Do not rename public methods or classes.
5. Do not change existing method signatures.
6. Verify backward compatibility after each modification.

**For REUSE actions:**
1. Write only the integration wiring (imports, call setup).
2. Do not modify the reused module.
3. Verify the reused module's public API is called correctly.

**For all actions:**
- Modify the minimum amount of code.
- Apply security rules: no eval/exec on unsanitized input, path traversal prevention, secret handling.
- Apply error handling rules: specific exception types, no bare except, no silent swallowing.
- Update imports in the affected module's `__init__.py` if the module uses package-level exports.
- Add tests immediately after each implementation action.

### Outputs
Implementation artifacts:
- New files created (paths)
- Existing files modified (paths, specific changes)
- New test files created (paths, test functions)
- Modified test files (paths, test functions)

### Failure Handling
If a file write fails: retry once. If persists, record error in `STATE.json` artifact and stop. Do not skip the file.
If a modification breaks imports: fix imports immediately. If unfixable, revert the modification and record failure.
If backward compatibility is broken: revert the breaking change immediately. Record the violation.
If a security rule violation is detected during implementation: revert. Record the violation. Do not proceed.
If tests added fail to pass at implementation time: fix implementation first. Do not defer test failures.

### Resume Behaviour
This stage is the primary resumption point. On resume:
1. Read `STATE.json` to determine which actions within the implementation plan have been completed.
2. Identify the next incomplete action.
3. For partially written files, read the file's current content and resume from the last completed modification.
4. For partially executed actions, resume from the last completed atomic operation (a file write or an edit is atomic; resume after the last atomic operation).
5. Verify that files modified before interruption are in a compilable state. If not, repair to compilable state before continuing.

### Checkpoint Behaviour
After each atomic action (each file write, each test addition), update `STATE.json`:
- Set `loop.stage` to `7`.
- Set `loop.stage_name` to `Implementation`.
- Record completed actions in `artifacts.implementation_summary.actions_completed`.
- Set `loop.last_success_at` to current timestamp.

If the loop is interrupted mid-stage, resumption occurs at the last completed atomic action within Stage 7.

On full completion of Stage 7, write the complete `artifacts.implementation_summary` to `STATE.json`. Set `checkpoints.stage_7` to `completed`. Set `loop.stage` to `8`.

---

## Stage 8: Static Validation

### Phase
EXECUTE

### Purpose
Verify that all modified and created files compile, imports resolve, type hints are valid, public APIs are consistent, and no dead code exists — before running any tests.

### Inputs
- Stage 7 output (implementation artifacts — new files, modified files, test files)
- Stage 6 output (implementation plan — expected public APIs, expected imports)
- `.amalgam-core/AGENTS.md` — coding standards, quality checklist

### Operations
1. **Import resolution check:** For every new and modified file, verify that every import resolves to an existing module or is a new module that itself passes this check.
2. **Compilation check:** For every new and modified file, attempt to compile the module (`py -c "import module_path"` equivalent inspection). Verify no syntax errors.
3. **Type hint check:** Verify that all public functions have type hints. Verify that `Any` usage is justified or eliminated.
4. **Docstring check:** Verify that all public classes and public methods have docstrings covering purpose, parameters, return values, and exceptions.
5. **Public API consistency check:** Compare the actual public API of modified modules against the expected public API from Stage 6. Verify no unintended changes.
6. **Dead code check:** Verify that no unused functions, classes, or variables were introduced.
7. **Duplicate code check:** Cross-check new code against existing code (from Stage 3). Verify no duplication was introduced.
8. **Security surface check:** Verify that no `eval()`, `exec()`, unsafe shell execution, or insecure deserialization was introduced. Verify that user-controlled input has boundary validation.
9. **Layer boundary check:** Verify that all imports respect the dependency direction. No new imports from lower-to-higher layers.

### Outputs
Structured static validation report containing:
- Import resolution results (pass/fail per file)
- Compilation results (pass/fail per file)
- Type hint completeness (pass/fail per file, missing hints listed)
- Docstring completeness (pass/fail per file, missing docstrings listed)
- Public API consistency (pass/fail per modified module)
- Dead code detection results (pass/fail, dead code items listed)
- Duplicate code detection results (pass/fail, duplicates listed)
- Security surface results (pass/fail, violations listed)
- Layer boundary results (pass/fail, violations listed)
- Overall verdict: READY_FOR_TESTING | BLOCKED

### Failure Handling
Per failure category:
- **Import resolution failure:** Fix the import. Rerun import check on that file.
- **Compilation failure:** Fix syntax. Rerun compilation check.
- **Type hint failure:** Add missing type hints. Rerun.
- **Docstring failure:** Add missing docstrings. Rerun.
- **Public API consistency failure:** If API changed unintentionally, revert. If intentional but not approved, escalate.
- **Dead code failure:** Remove dead code. Rerun.
- **Duplicate code failure:** Choose one implementation, remove the duplicate, rerun.
- **Security violation:** Fix immediately. If cannot fix without architectural change, escalate. Do not proceed.
- **Layer boundary violation:** Fix import direction. If architectural redesign required, escalate.

After any fix, rerun the entire Stage 8. Do not proceed to Stage 9 unless verdict is READY_FOR_TESTING.

### Resume Behaviour
If resuming from a completed Stage 8, load `artifacts.static_validation` from `STATE.json`. Spot-check 3 files (top modified files). If any check fails, re-execute Stage 8 fully.

### Checkpoint Behaviour
On completion, write `artifacts.static_validation` to `STATE.json`. Set `checkpoints.stage_8` to `completed`. Set `loop.stage` to `9`.

---

## Stage 9: Testing

### Phase
EXECUTE

### Purpose
Execute the complete project test suite. Verify that all existing tests pass, all new tests pass, and no regressions exist. This is the primary quality gate.

### Inputs
- Stage 7 output (new test files, modified test files)
- Stage 1 output (baseline test count from `MISSION.md`)
- `.amalgam-core/AGENTS.md` — testing policy

### Operations
1. Execute the full test suite: `py -m pytest tests/`
2. Parse the pytest output: total passed, total failed, total runtime.
3. Compare current test count against the baseline from Stage 1.
4. For each failure:
   - Identify the failing test name and file.
   - Determine root cause: implementation error, new test error, regression, environment issue, flaky test.
   - Record root cause classification.
5. Verify that all new tests from Stage 7 pass.
6. Verify that no previously-passing tests now fail (regression detection).
7. If all tests pass: record success in `STATE.json`.
8. If any test fails: record all failures in `STATE.json` with root cause classifications.

### Outputs
Structured test result containing:
- Total tests passed
- Total tests failed
- Total runtime
- Baseline comparison (current count vs Stage 1 baseline)
- All-new-tests pass/fail status
- Regression list (any previously-passing tests that now fail)
- Root cause classifications per failure
- Overall verdict: TESTS_ALL_PASS | TESTS_PARTIAL_FAIL | TESTS_REGRESSION

### Failure Handling
Based on verdict:

**TESTS_REGRESSION:**
- Immediately halt further progress.
- Identify the regression root cause.
- Fix implementation immediately (return to Stage 7 for the affected module).
- Rerun Stage 9.
- Do not proceed past Stage 9 while any regression exists.

**TESTS_PARTIAL_FAIL:**
- If failures are only in new tests (not regressions): fix new tests (return to Stage 7 for test fixes).
- If failures are in existing tests but not regressions (intermittent/flaky): investigate. If flaky, note and proceed with caution. If deterministic, treat as regression.
- Rerun Stage 9 after fixes.

**TESTS_ALL_PASS:**
- Record the exact pass count and runtime.
- Proceed to Stage 12 (COMPLETE phase).

### Resume Behaviour
If resuming from a completed Stage 9, load `artifacts.test_result` from `STATE.json`. Re-run the full test suite to confirm results. If results differ from stored results, treat as new failures and follow failure handling.

### Checkpoint Behaviour
If TESTS_ALL_PASS: write `artifacts.test_result` to `STATE.json`. Set `checkpoints.stage_9` to `completed`. Set `loop.stage` to `12`. Transition `loop.phase` to `COMPLETE`.

If any failures: write `artifacts.test_result` to `STATE.json`. Set `loop.stage` to `10`. Set `loop.retry_count` to `loop.retry_count + 1`. Transition `loop.phase` to `RECOVER`.

If `loop.retry_count >= loop.max_retries`: record final failure in `STATE.json`. Escalate. Do not loop further.

---

## Stage 10: Failure Recovery

### Phase
RECOVER

### Purpose
Analyze test failures from Stage 9, classify root causes, select recovery strategies, and execute fixes. This stage is the bridge between test failure and corrected implementation.

### Inputs
- Stage 9 output (test result with detailed failure list and root cause classifications)
- Stage 7 output (implementation artifacts)
- Stage 6 output (implementation plan)
- `ARCHITECTURE.md` — goal lifecycle recovery workflow

### Operations
For each test failure:

1. **Root cause classification:**
   - `IMPLEMENTATION_ERROR` — code logic is wrong
   - `IMPORT_ERROR` — module import fails
   - `TYPE_ERROR` — type mismatch in implementation
   - `API_BREAK` — public API changed unintentionally
   - `DEPENDENCY_ERROR` — transitive dependency broken
   - `TEST_ERROR` — test itself is incorrect (not implementation)
   - `ENVIRONMENT_ERROR` — environment-specific (missing dependency, wrong path)
   - `FLAKY_ERROR` — intermittent, non-deterministic
   - `UNKNOWN` — cannot classify

2. **Strategy selection:**
   - `IMPLEMENTATION_ERROR | IMPORT_ERROR | TYPE_ERROR | DEPENDENCY_ERROR` → **FIX_IMPLEMENTATION** — return to Stage 7 for the affected module
   - `API_BREAK` → **FIX_OR_ESCALATE** — if unintentional, revert API; if intentional but not approved, escalate
   - `TEST_ERROR` → **FIX_TESTS** — return to Stage 7 for test corrections
   - `ENVIRONMENT_ERROR` → **FIX_ENVIRONMENT** — install dependency, fix path
   - `FLAKY_ERROR` → **NOTE_AND_RETEST** — record flakiness, rerun
   - `UNKNOWN` → **INVESTIGATE** — inspect failing code directly

3. **Strategy execution:**
   - Apply the selected strategy.
   - After applying fix, do NOT re-run Stage 8 (static validation) unless the fix changed imports or public APIs.
   - After applying fix, proceed directly to Stage 11.

### Outputs
Structured recovery log containing:
- Per-failure: root cause classification, selected strategy, fix applied, fix location
- All failures addressed (no failure left unhandled)
- Recovery verdict: ALL_FIXES_APPLIED | PARTIAL_FIXES | ESCALATED

### Failure Handling
If a failure cannot be classified (UNKNOWN persists after investigation): escalate. Do not guess a fix.
If a fix applied fails to resolve the failure (verified in Stage 11): reclassify with new root cause. Apply new strategy. Increment retry count in `STATE.json`.
If retry count exceeds maximum: escalate. Mark the goal FAILED in `STATE.json`.

### Resume Behaviour
If resuming from a partially completed Stage 10, load `artifacts.recovery_log` from `STATE.json`. Identify failures not yet addressed (those without a fix entry). Resume from first unaddressed failure.

### Checkpoint Behaviour
After each fix is applied, append to `artifacts.recovery_log` in `STATE.json`:
```
{
  "failure_test": "test_name",
  "root_cause": "IMPLEMENTATION_ERROR",
  "strategy": "FIX_IMPLEMENTATION",
  "fix_location": "module_path:line",
  "fix_description": "description",
  "applied_at": "ISO8601"
}
```

On completion of all fixes, set `checkpoints.stage_10` to `completed`. Set `loop.stage` to `11`.

---

## Stage 11: Regression Testing

### Phase
RECOVER

### Purpose
Rerun the complete test suite after recovery fixes from Stage 10. Verify that all existing tests pass, all new tests pass, all regressions are resolved, and no new failures were introduced by the fixes.

### Inputs
- Stage 10 output (recovery log — all fixes applied)
- Stage 9 output (original test result — failure baseline for comparison)
- Stage 1 output (baseline test count)

### Operations
1. Execute the full test suite: `py -m pytest tests/`
2. Compare current test result against Stage 9 result:
   - Verify all failures from Stage 9 are now passing.
   - Verify no new failures appeared.
   - Verify test count is at or above baseline.
3. If all Stage 9 failures are resolved and no new failures exist: **RECOVERY_SUCCESS**.
4. If some Stage 9 failures persist: identify which fixes failed. Return to Stage 10 for reclassification and new strategy. Increment retry count.
5. If new failures appeared from fixes: classify these as new failures. Append to recovery log. Return to Stage 10.
6. If retry count exceeds maximum: **RECOVERY_FAILED**. Escalate. Mark goal FAILED in `STATE.json`. Stop.

### Outputs
Structured regression test result containing:
- Total tests passed
- Total tests failed
- Failure comparison: Stage 9 failures resolved, Stage 9 failures still failing, new failures introduced
- Test count vs baseline
- Recovery success/failure verdict: RECOVERY_SUCCESS | RECOVERY_PARTIAL | RECOVERY_FAILED

### Failure Handling

**RECOVERY_SUCCESS:**
- Record result in `STATE.json`.
- Reset retry count to 0.
- Proceed to Stage 12 (COMPLETE phase).

**RECOVERY_PARTIAL:**
- Return to Stage 10 for remaining failures.
- Increment retry count.

**RECOVERY_FAILED:**
- Escalate. Mark goal FAILED. Do NOT proceed to COMPLETE phase.
- Record final state in `STATE.json`. Set `loop.phase` to `TERMINATED`.

### Resume Behaviour
If resuming from a completed Stage 11 (RECOVERY_SUCCESS), load `artifacts.regression_result` from `STATE.json` and proceed to Stage 12.

### Checkpoint Behaviour
On RECOVERY_SUCCESS: write `artifacts.regression_result` to `STATE.json`. Set `checkpoints.stage_11` to `completed`. Set `loop.stage` to `12`. Reset `loop.retry_count` to `0`. Transition `loop.phase` to `COMPLETE`.

On RECOVERY_PARTIAL: write `artifacts.regression_result` to `STATE.json`. Set `loop.stage` to `10`. Set `loop.retry_count` to `current + 1`.

On RECOVERY_FAILED: write `artifacts.regression_result` to `STATE.json`. Set `loop.phase` to `TERMINATED`. Set all remaining `checkpoints.stage_*` to `skipped`. Stop execution.

---

## Stage 12: Documentation Update

### Phase
COMPLETE

### Purpose
Update all documentation to reflect the completed implementation. Ensure docstrings, architecture documentation, mission documentation, and changelog remain synchronized with the code.

### Inputs
- Stage 7 output (implementation artifacts — new modules, modified modules)
- Stage 8 output (static validation — docstring completeness report)
- `ARCHITECTURE.md` — for architecture documentation update
- `MISSION.md` — for mission progress update
- `docs/missions/` — for mission specification population
- `.amalgam-core/AGENTS.md` — documentation policy

### Operations
1. **Docstring audit:** For every new and modified public class/method, verify docstring covers purpose, parameters, return value, and exceptions. Fix any gaps found in Stage 8 that remain.
2. **Architecture documentation update:** If a new module was created, add its entry to `ARCHITECTURE.md`:
   - Document its purpose.
   - Document its layer.
   - Document its public API.
   - Document its dependencies.
   If architecture changed (new layer, new dependency direction), update the relevant sections.
3. **Mission documentation update:** Update `MISSION.md`:
   - Mark the current milestone as completed.
   - Update the completion percentage.
   - Update the test count baseline to the new pass count from Stage 9/11.
   - Add the new milestone to the roadmap if applicable.
4. **TASK.md update:** Update `TASK.md`:
   - Check off completed validation items.
   - Update session notes with completion summary.
5. **Mission specification file:** If the current mission has a corresponding file in `docs/missions/`, populate it with:
   - Mission number.
   - Description of what was implemented.
   - List of files affected.
   - List of tests added.
   - Status: completed.
6. **Changelog update:** If `docs/Changelog.md` exists, append an entry for this implementation.

### Outputs
Documentation update summary containing:
- Files updated (paths)
- Docstrings added/fixed (count)
- Architecture entries added/modified (count)
- Mission status changes (milestone marked complete, percentage updated)
- TASK.md changes (checklist items checked)
- Mission spec files populated (count)
- Changelog entry added (yes/no)

### Failure Handling
If a documentation file cannot be written: retry. If persists, record failure. Proceed to Stage 13 with the failure noted.
If architecture documentation changes are uncertain: flag for review. Do not write speculative entries.

### Resume Behaviour
If resuming from a completed Stage 12, load `artifacts.documentation_update` from `STATE.json`. Spot-check the updated documentation files against current code. If documentation is out of sync, re-execute Stage 12.

### Checkpoint Behaviour
On completion, write `artifacts.documentation_update` to `STATE.json`. Set `checkpoints.stage_12` to `completed`. Set `loop.stage` to `13`.

---

## Stage 13: Checkpoint Save

### Phase
COMPLETE

### Purpose
Write a final comprehensive checkpoint to `.amalgam-core/STATE.json` that captures the complete loop state for future resumption, audit, and replay. This is the persistence gate before the remaining completion stages.

### Inputs
- All prior stage outputs (artifacts from Stages 1-12)
- Current `STATE.json` content

### Operations
1. Aggregate all stage artifacts into a complete `artifacts` block.
2. Set all `checkpoints.stage_*` to their final values (1-12 completed; 13-17 in_progress/pending).
3. Set `loop.stage` to `13`.
4. Set `loop.stage_name` to `Checkpoint Save`.
5. Set `loop.last_success_at` to current timestamp.
6. Record final test pass count from Stage 9 or Stage 11.
7. Record final mission ID and milestone ID.
8. Record final git HEAD and branch.
9. Write the complete `STATE.json`.
10. Verify `STATE.json` is valid JSON (parse re-read).

### Outputs
Finalized `STATE.json` with all artifacts, checkpoint statuses, and loop metadata.

### Failure Handling
If `STATE.json` write fails: retry. If persists, write to alternate path `.amalgam-core/STATE.backup.json` and record the fallback.
If `STATE.json` is invalid JSON after write: rewrite. Validate again.

### Resume Behaviour
If resuming from a completed Stage 13, read `STATE.json`. Verify it contains all stage 1-12 artifacts. If incomplete, re-execute Stage 13.

### Checkpoint Behaviour
On completion, set `checkpoints.stage_13` to `completed`. Set `loop.stage` to `14`.

---

## Stage 14: State Update

### Phase
COMPLETE

### Purpose
Update all `.amalgam-core/` infrastructure files to reflect the completed engineering loop. This ensures the next model invocation sees the correct project state.

### Inputs
- Stage 13 output (final `STATE.json`)
- `.amalgam-core/REGISTRY.json` — current state (may be empty)
- `.amalgam-core/HISTORY.json` — existing history (may be empty)
- `.amalgam-core/CONTEXT.md` — current state (may be empty)
- `.amalgam-core/WORKFLOW.yaml` — current state (may be empty)
- Stage 9/11 output (final test result)

### Operations
1. **REGISTRY.json:** Append an entry for the completed task:
   ```json
   {
     "mission_id": "M7.1.5",
     "milestone": "7.1.5",
     "completed_at": "ISO8601",
     "test_count": 535,
     "files_created": ["path1", "path2"],
     "files_modified": ["path3"],
     "status": "completed"
   }
   ```
2. **HISTORY.json:** Append a history entry documenting the completed engineering loop:
   ```json
   {
     "timestamp": "ISO8601",
     "loop_version": "1.0",
     "mission_id": "M7.1.5",
     "total_stages_completed": 17,
     "retries_used": 0,
     "final_test_count": 535,
     "duration": "duration_string"
   }
   ```
3. **CONTEXT.md** and **WORKFLOW.yaml:** If these are part of the infrastructure, update accordingly. If they remain empty/placeholder, note that in the history entry.

### Outputs
Updated infrastructure files:
- `REGISTRY.json` — new entry appended
- `HISTORY.json` — new entry appended
- `CONTEXT.md` — updated if applicable
- `WORKFLOW.yaml` — updated if applicable

### Failure Handling
If a JSON file write fails: retry. If persists, note failure in `HISTORY.json` error field and continue.
If JSON parsing of existing `REGISTRY.json` or `HISTORY.json` fails: repair the file (fix JSON syntax), then write.

### Resume Behaviour
If resuming from a completed Stage 14, verify that the entries written to `REGISTRY.json` and `HISTORY.json` are present and valid. If missing, re-execute Stage 14.

### Checkpoint Behaviour
On completion, set `checkpoints.stage_14` to `completed`. Set `loop.stage` to `15`.

---

## Stage 15: Mission Update

### Phase
COMPLETE

### Purpose
Update the mission state in `.amalgam-core/MISSION.md` to reflect the completed milestone. This ensures mission tracking remains accurate across model invocations.

### Inputs
- Project `MISSION.md` — current mission roadmap, milestone statuses
- `.amalgam-core/MISSION.md` — core mission tracking (may be empty)
- Stage 7 output (implementation artifacts)
- Stage 9/11 output (test result)

### Operations
1. Read `.amalgam-core/MISSION.md`. If empty, initialize it with a mission tracking header.
2. Record the completed milestone:
   ```
   ### M7.1.5 — Completed
   - Description: Event Bus Integration
   - Completed at: ISO8601
   - Files created: [list]
   - Files modified: [list]
   - Tests added: [count]
   - Test result: NNN passed in X.Xs
   - Status: COMPLETED
   ```
3. If the project `MISSION.md` has a corresponding milestone entry, verify `.amalgam-core/MISSION.md` is consistent.
4. Identify the next pending milestone (from project `MISSION.md`) and record it as `NEXT_MILESTONE`.

### Outputs
Updated `.amalgam-core/MISSION.md` with completed milestone entry and next milestone pointer.

### Failure Handling
If `.amalgam-core/MISSION.md` cannot be written: retry. If persists, note failure and proceed to Stage 16.

### Resume Behaviour
If resuming from a completed Stage 15, verify the milestone entry in `.amalgam-core/MISSION.md`. If missing or incorrect, re-execute Stage 15.

### Checkpoint Behaviour
On completion, set `checkpoints.stage_15` to `completed`. Set `loop.stage` to `16`.

---

## Stage 16: History Update

### Phase
COMPLETE

### Purpose
Append a structured completion entry to `.amalgam-core/HISTORY.json` documenting the full loop execution for audit, replay, and learning.

### Inputs
- Stage 14 output (updated `HISTORY.json` with basic entry)
- All stage artifacts (from `STATE.json`)

### Operations
1. Read the current `HISTORY.json`.
2. Append a comprehensive completion entry:
   ```json
   {
     "entry_id": "uuid",
     "loop_version": "1.0",
     "mission_id": "M7.1.5",
     "milestone": "7.1.5 — Event Bus Integration",
     "started_at": "ISO8601",
     "completed_at": "ISO8601",
     "total_duration": "duration",
     "stages": {
       "completed": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17],
       "retried": [],
       "skipped": []
     },
     "retries_used": 0,
     "recoveries": 0,
     "files_created": ["path1"],
     "files_modified": ["path2"],
     "tests_added": ["test_func_1", "test_func_2"],
     "test_result": {
       "passed": 535,
       "failed": 0,
       "runtime": "X.Xs"
     },
     "architecture_verdict": "PRESERVED",
     "backward_compatibility": "PRESERVED",
     "security_verdict": "PASS",
     "verdict": "COMPLETE",
     "next_milestone": "M7.2"
   }
   ```
3. Validate the JSON.
4. Write `HISTORY.json`.

### Outputs
Finalized `HISTORY.json` with comprehensive completion entry.

### Failure Handling
If `HISTORY.json` write fails: retry. If persists, write to `.amalgam-core/HISTORY.backup.json`.
If JSON validation fails: fix syntax error, revalidate, rewrite.

### Resume Behaviour
If resuming from a completed Stage 16, verify the completion entry exists in `HISTORY.json`. If missing, re-execute Stage 16.

### Checkpoint Behaviour
On completion, set `checkpoints.stage_16` to `completed`. Set `loop.stage` to `17`.

---

## Stage 17: Completion

### Phase
COMPLETE

### Purpose
Mark the engineering loop as complete. Produce the final structured report. Transition the loop to terminal state. Stop execution.

### Inputs
- All prior stage outputs (complete loop artifacts)
- Stage 9/11 output (final test result)
- `.amalgam-core/AGENTS.md` — output format rules

### Operations
1. Set `loop.stage` to `17`.
2. Set `loop.stage_name` to `Completion`.
3. Set all remaining `checkpoints.stage_*` to `completed`.
4. Set `loop.phase` to `TERMINATED`.
5. Write final `STATE.json`.
6. Produce the structured completion report (format per `.amalgam-core/AGENTS.md` output format rules):
   - Architecture Summary
   - Files Created
   - Files Modified
   - Tests Added
   - Pytest Result
   - Remaining Work
7. Output the report.
8. Stop. Do not begin the next mission. Do not implement additional features.

### Outputs
- Final `STATE.json` with phase `TERMINATED`
- Structured completion report (output to user)
- Loop termination signal

### Failure Handling
If report generation fails: retry. If persists, output minimal report (Architecture Summary and Pytest Result only) with note that full report generation failed.
If `STATE.json` final write fails: the loop is still considered complete if Stages 1-16 are check pointed.

### Resume Behaviour
If resuming from a completed Stage 17, output the stored report from `STATE.json` and stop. Do not re-execute any stage.

### Checkpoint Behaviour
Final `STATE.json` state after Stage 17:
```json
{
  "loop": {
    "phase": "TERMINATED",
    "stage": 17,
    "stage_name": "Completion",
    "retry_count": 0,
    "completed_at": "ISO8601",
    "checkpoints": {
      "stage_1": "completed",
      ...
      "stage_17": "completed"
    },
    "verdict": "LOOP_COMPLETE"
  }
}
```

---

# Interruption Recovery Protocol

When a model invocation is interrupted (provider timeout, rate limit, user stop, system crash), the next model invocation follows this protocol:

## Startup

1. Read `.amalgam-core/STATE.json`.
2. If `loop.phase` is `TERMINATED`: the previous loop completed. Start fresh (Stage 1).
3. If `loop.phase` is not `TERMINATED`: the previous loop was interrupted.
4. Read `loop.stage` — this is the last stage that was in progress.
5. Read `checkpoints.stage_N` for stages 1 through `loop.stage - 1` — these should be `completed`.
6. Verify that each completed checkpoint's artifacts are present in `STATE.json`.
7. If any completed checkpoint is missing artifacts: fall back to the last stage with complete artifacts. Re-execute from that stage.

## Resumption Rules

| Interrupted Stage | Resume Behaviour |
|-------------------|------------------|
| Stage 1-5 (UNDERSTAND) | Re-execute the interrupted stage. UNDERSTAND artifacts are small and fast to regenerate. |
| Stage 6 (PLAN) | Load `artifacts.plan`. Verify against current `TASK.md`. If scope unchanged, resume from incomplete action. If scope changed, re-execute Stages 3-6. |
| Stage 7 (IMPLEMENTATION) | Load `artifacts.implementation_summary`. Identify completed vs pending actions. Resume from next incomplete action. Verify all completed files are in a compilable state. |
| Stage 8 (STATIC VALIDATION) | Reload all files from Stage 7 artifacts. Re-execute Stage 8 fully. |
| Stage 9 (TESTING) | Re-execute Stage 9 fully. Tests are fast to rerun. |
| Stage 10-11 (RECOVERY) | Load `artifacts.recovery_log` and `artifacts.regression_result`. Resume from first unaddressed failure or re-execute Stage 11. |
| Stage 12-14 (COMPLETE early) | Load artifacts. Verify documentation/infrastructure files are updated. If incomplete, re-execute the interrupted stage. |
| Stage 15-17 (COMPLETE late) | Load artifacts. Execute the interrupted stage from scratch. These stages are idempotent (append to infrastructure files). |

## Resumption Verification

Before resuming work on any incomplete stage:
1. Verify that all completed stages' artifacts are consistent with current repository state.
2. Check `git status` — if repository has changed since the interrupted loop, record the changes.
3. If changes to the repository are unrelated to the loop's task, proceed with resumption.
4. If changes affect files the loop was modifying, treat as a conflict: re-execute from Stage 3 (code discovery) to detect the new state.

---

# Loop Invariants

These invariants must hold at every stage boundary:

1. **Layer boundaries preserved:** No import crosses from lower to higher layer.
2. **No circular imports:** The import DAG remains acyclic.
3. **No duplicate implementations:** Every new code extends or creates; never duplicates.
4. **Public APIs preserved:** Existing public methods, classes, and exports remain unchanged (EXTEND adds; never removes or renames without approval).
5. **No dead code:** Every introduced function, class, and variable is used.
6. **No placeholder code:** Every implementation is production quality.
7. **No security violations:** No eval/exec on unsanitized input. Filesystem ops within workspace boundaries.
8. **State is checkpointed:** `STATE.json` reflects the true current stage.
9. **Retry count bounded:** `loop.retry_count` never exceeds `loop.max_retries`.
10. **Scope preserved:** Every action maps to a `TASK.md` deliverable.

---

# Termination Conditions

The engineering loop terminates under these conditions:

| Condition | Verdict | Phase |
|-----------|---------|-------|
| Stage 17 completes successfully | LOOP_COMPLETE | TERMINATED |
| Stage 11 RECOVERY_FAILED (max retries exceeded) | LOOP_FAILED | TERMINATED |
| Stage 10 escalation (unrecoverable failure) | LOOP_FAILED | TERMINATED |
| Stage 1 unrecoverable (repository unreadable) | LOOP_FAILED | TERMINATED |
| Stage 2 layer violation cannot be resolved | LOOP_FAILED | TERMINATED |
| Stage 5 duplication cannot be eliminated | LOOP_FAILED | TERMINATED |
| User explicitly stops execution | LOOP_PAUSED | PAUSED (resumable) |

In all termination conditions, `STATE.json` is written with the terminal state before stopping.

---

# Version History

## Version 1.0
- Initial release of the AMALGAM Engineering Loop.
- Defines the 17-stage permanent execution algorithm.
- Supports checkpoint-based interruption recovery.
- Designed for deterministic replay across model invocations.
- Mission-independent, reusable forever.

---

# Document Maintenance

This document evolves with the project.
When the engineering loop changes, this document must be updated.
When new stages are added or stages are reordered, this document must be updated.
When checkpoint format changes, this document must be updated.

The `.amalgam-core/` directory is the permanent engineering infrastructure.
This document is the execution algorithm for that infrastructure.

ENGINEERING LOOP COMPLETE