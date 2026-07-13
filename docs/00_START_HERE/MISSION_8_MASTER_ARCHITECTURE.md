# MISSION 8 MASTER ARCHITECTURE

**Status:** FROZEN before implementation
**Mission:** Primary Engineering System — Repository-Aware Autonomous Engineering Loop
**Model:** Existing local Ollama model `qwen2.5-coder:7b`; no fine-tuning or distillation
**Depends on:** Mission 7 / `amalgam-core-v1.2-stable`

## 1. Objective

Turn the Mission 7 orchestration substrate into a repository-aware engineering system that reconstructs its state without chat history, proposes schema-valid plans with a local model, pauses for exact-plan approval, executes through the Kernel safety path, tests and reviews its work, performs bounded materially changed repairs, and creates a verified local commit.

## 2. Authority boundary

| Action | Authority |
|---|---|
| Repository inspection, status, planning | Autonomous, read-only |
| Repository file edits | Only after explicit approval of the exact plan hash |
| Routine planned tests | Autonomous after plan approval |
| Local branch and commit | Autonomous only after tests and review pass |
| File deletion, broad rewrite, dependency changes | Always explicit approval |
| Secrets, external side effects, deployment | Always explicit approval |
| Push, merge, rebase, tag, remote changes, force/reset | Always explicit approval |

Approval is scope-bound, hash-bound, and invalidated by any changed affected path, action, acceptance criterion, or verification command. On repair exhaustion AMALGAM persists `blocked`, reports evidence and attempted strategies, and requests human help.

## 3. Dependency laws

1. Deterministic repository engines are read-only and contain no model logic.
2. Model reasoning belongs to Brain/services and proposes data; it never executes tools.
3. ChiefAgent orchestrates but never directly accesses tools.
4. Every mutation is executed by Kernel Dispatcher through ToolWrapper, capability validation, permission checking, and workspace confinement.
5. Deterministic schema, DAG, scope, authority, test, review, and Git gates remain authoritative over model output.

## 4. Structured contracts

- `RepositoryContext`: root, branch, dirty files, state, mission, next legal action, recent commits, bounded docs/source summaries, provenance and timestamp.
- `ReasoningIntent`: intent, action, confidence, rationale, requires_plan.
- `EngineeringPlan`: plan_id, goal, tasks (id/action/capability/dependencies/affected_paths/acceptance criteria), verification commands, risks, approval requirements, hash.
- `ApprovalRecord`: plan_id, plan_hash, approved_at; valid only for the exact canonical plan.
- `ReviewVerdict`: approved, findings, evidence, security/architecture/scope/test checks.
- `RepairStrategy`: failure class, root cause, evidence, changed strategy and bounded next actions.
- `MissionCheckpoint`: lifecycle state, completed task IDs, repair count, review state, commit SHA, evidence.
- `FinalReport`: verified facts only: plan, diff scope, tests, review, commit, unresolved risks.

## 5. Lifecycle

`inspect → reason → plan → awaiting_approval → execute → test → review → repair/replan → ready_to_commit → completed`

Terminal alternatives: `aborted` or `blocked`. Checkpoints are written atomically after every transition. Resume never repeats completed task IDs.

## 6. Components

- **8.1 Repository Context Engine:** bounded repository reconstruction using existing workspace/knowledge/Git facilities plus canonical docs and state.
- **8.2 Structured Reasoning:** role-aware Ollama JSON generation with timeout, validation, bounded retries, and safe fallback. Deterministic fast paths remain for exact commands/math.
- **8.3 Mission Control:** `status`, `run`, `resume`, `approve`, `abort`; exact-plan approval and scope enforcement.
- **8.4 Review/Repair:** mandatory structured reviewer gate; failure classification and materially changed bounded repair.
- **8.5 Git Boundary:** read status/diff/history; separately gated local branch/commit; never remote/destructive operations.
- **8.6 Demonstration:** a real bounded AMALGAM change reaches approval pause, edit, test, controlled repair, review, checkpoint and local commit.
- **8.7 Freeze:** full tests, security/architecture audits, completion report, version/state sync.

## 7. Model behavior

`qwen2.5-coder:7b` receives compact repository context and registry-derived action contracts. JSON is parsed and validated; prose outside JSON, unknown actions, cyclic DAGs, out-of-workspace paths, destructive operations, or malformed responses fail closed. Ollama failure never grants authority and never modifies files.

## 8. Retry and stop rules

- Structured model generation: maximum 2 repair prompts after the first response.
- Engineering repair: maximum 2 attempts.
- Identical repair strategy/hash is rejected.
- Stale approval, unplanned file change, missing test evidence, failed review, secret detection, or authority violation prevents commit.
- Exhaustion transitions to `blocked` with diagnosis and recommended human decisions.

## 9. Acceptance criteria

Mission 8 closes only when a fresh process derives current state without chat history; structured local reasoning fails safely; no pre-approval mutation is possible; execution cannot bypass Kernel safety; interruption resumes without duplication; review is mandatory; repair is bounded and materially changed; a real objective reaches passing tests and a safe local commit; remote/destructive/dependency/secret actions remain gated; and all prior/new tests pass.

## 10. Non-goals

No model fine-tuning/distillation, cloud AI, deployment, browser automation, package upgrades, autonomous remote Git operations, unrestricted shell, or general-purpose self-modification.

## 11. Freeze rule

This architecture is the authority for Mission 8. Changes require a documented roadmap/architecture amendment and owner approval before implementation continues.
