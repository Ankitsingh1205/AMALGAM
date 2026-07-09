# PROJECT_CONSTITUTION.md

**The Permanent Constitution of AMALGAM**

Status: Permanent
Nature: Foundational engineering law

---

## Preamble

This constitution defines the permanent engineering laws that govern the AMALGAM project.
It is not a history, not a roadmap, and not an implementation guide. It fixes what must
remain true regardless of which feature is being built or who is building it.

Every article is grounded in AMALGAM's recovered record. Where that record preserved a
contradiction, this constitution preserves it as well and does not resolve it. The goal of
this document is permanence, not completeness: it states only the laws that endure.

---

## 1. Vision

### What AMALGAM fundamentally is

AMALGAM is a local-first AI operating system: a single system that coordinates multiple AI
models, tools, memory, knowledge, and autonomous agents into one intelligence. Its motto is
**"One Intelligence. Infinite Capabilities,"** and its operating purpose is to **turn AI into
action**. Its engineering heartbeat is a continuous cycle: **Think, Plan, Execute, Learn.**

One founding conviction is permanent: **the language model is not the brain.** AMALGAM
reasons, plans, and coordinates above the models it uses. Models are capabilities it
orchestrates, never the seat of control.

The project's own name for itself varied through its history — a personal AI platform, a
local-first AI operating system, and an autonomous software-engineering operating system were
each used at different times. This constitution does not reconcile that label. It fixes only
the enduring essence stated above and leaves the precise product category open, exactly as
the record left it.

### What problem it solves

AMALGAM exists to accomplish complex, multi-step work from a single interface by
orchestrating models, tools, memory, and agents — planning, executing, validating,
reflecting, and recovering — rather than returning conversation alone. It coordinates AI
systems; it is not itself merely one of them.

### Long-term objective

To be the best-engineered local-first AI operating system for developers and technical
professionals. Success is measured by engineering quality and reliability — not by size,
download count, or breadth of features. Every significant decision is tested against a
durable question: *if AMALGAM were used by thousands of developers, would this choice still
make sense?* If not, it is reconsidered now, not later.

### Non-goals

- AMALGAM is not a chatbot and not "another" AI chat front-end.
- AMALGAM is not a thin wrapper around a single language model.
- AMALGAM does not try to own every capability; it integrates external capabilities rather
  than reimplementing or owning them.
- AMALGAM does not pursue scale or popularity at the expense of engineering quality.
- AMALGAM does not act on a user's data without approval; unsupervised autonomy over user
  data is out of scope.

---

## 2. Core Principles

These principles are permanent. Violating one is a defect, not a style choice.

1. **Mission-driven development.** Every capability is delivered through a defined mission
   with a single objective. No feature bypasses the mission workflow, and unrelated work is
   never smuggled into a mission.
2. **The repository and the record are the source of truth.** Architecture and history are
   established by what the repository contains and what the preserved record documents —
   never by assumption. Nothing is invented to fill a gap.
3. **Thinking is separated from execution.** Reasoning and planning are permanently separated
   from execution. The reasoning layer never executes; the execution layer never reasons.
4. **Layered architecture with one-directional dependencies.** The system is organized in
   layers, and dependencies flow in one direction only. A lower layer never depends on a
   layer above it.
5. **Single ownership of responsibility.** Each responsibility has exactly one owner.
   Duplicated ownership and competing implementations of the same responsibility are defects.
6. **Reuse before creation.** Existing components are reused or extended before new ones are
   created. Duplicating working behavior is prohibited.
7. **Determinism by default.** Where a task can be solved by deterministic engineering, it is,
   without invoking a language model. Identical inputs should yield identical outputs wherever
   practical.
8. **Test-backed validation.** Every feature ships with automated tests. Work is not complete
   until its tests pass and existing tests continue to pass.
9. **Replaceable components.** Every module is designed to be replaceable behind a stable
   boundary.
10. **A single source of configuration.** Configuration lives in one place, not scattered
    across the system.
11. **Build, integrate, test, freeze.** Work proceeds in small increments. Each increment is
    integrated, tested, and left in a working state before the next begins.
12. **Design for scale.** Every architectural decision is evaluated against substantial future
    growth in tools, services, agents, and files.
13. **Approval before autonomous action on user data.** Actions that can modify a user's data
    require user approval before they execute.
14. **Conflicts in the record are preserved, not reconciled.** When the historical record
    contains contradictions, they are marked and preserved, never silently resolved or
    overwritten.

---

## 3. Architecture Laws

These are permanent structural constraints. They change only through the Amendment Process.

- **The Brain / Kernel division is permanent.** A reasoning-and-planning layer (the Brain)
  decides what to do; an execution layer (the Kernel) carries it out. This split does not
  change.
- **Dependency direction is fixed and downward.** Coordination flows from higher layers to
  lower layers — mission and planning above; scheduling and execution below; tools, services,
  and engines at the base; configuration beneath all. A lower layer must never import or
  depend upon a higher layer.
- **The Dispatcher coordinates; it holds no business logic.** All routing of work to tools and
  services passes through the dispatch layer. It coordinates execution and never embeds
  product decisions.
- **Extension happens at the registry, not the Dispatcher.** New capabilities are added by
  registration, without modifying dispatch logic. Tools are reached only through the
  Dispatcher and only when registered; nothing bypasses this path.
- **The Golden Rule of placement.** Every new module must answer whether it is a **Tool**
  (performs actions), a **Service** (provides infrastructure or external communication), or an
  **Engine** (analyzes and understands). If the answer is unclear, the design is not finished.
- **Tools are isolated.** Tools perform actions and never communicate directly with one
  another. Services provide infrastructure and never make product decisions.
- **Engines are read-only and deterministic.** Components that analyze and understand the
  project are read-only, deterministic, and independent of any language model and of the
  reasoning layer.
- **Missions own metadata, not execution.** The mission layer holds identity, status,
  dependency structure, and lifecycle. It never executes work and never depends on the
  executor or the scheduler.
- **The Scheduler owns ordering, not planning or work.** Scheduling orders and parallelizes
  agent execution and resolves dependencies. It does not plan missions, own mission data, or
  perform the work itself.
- **Central coordination owns orchestration, not capability.** The central coordinating agent
  (ChiefAgent) composes planning, scheduling, dependency resolution, and fleet coordination.
  It orchestrates other components; it never bypasses the dispatch path to reach tools
  directly.
- **Agents are indirectly coupled.** No agent calls another agent directly. Agents
  communicate only through shared context and structured messages, and every agent returns
  structured results rather than free-form text.
- **Frozen architecture stays frozen.** Once an architectural decision is accepted and frozen,
  it changes only by explicit owner decision.

---

## 4. Mission Philosophy

- **One objective per mission.** Each mission answers a single guiding question and delivers
  one coherent objective. Scope creep is prohibited; work that belongs to a different
  objective waits for its own mission.
- **Specification precedes implementation.** No mission is implemented without a specification
  that defines its objective, scope, deliverables, and acceptance criteria. The specification
  may take the form of a directed prompt rather than a formal document, but it must exist and
  be substantive. A table of contents is not a specification. Undefined work is not started.
- **Missions are split into incremental phases.** Larger missions are divided into phases that
  progress from core implementation to stabilization, optimization, and production hardening.
  Each phase leaves the repository in a working state.
- **Acceptance criteria and explicit constraints.** Every mission declares what it will
  deliver and, equally, what it will not touch. Constraints that forbid redesigning unrelated
  architecture are part of the mission.
- **Definition of Done.** A mission is complete only when its deliverables are implemented,
  its tests pass, existing tests still pass with no regressions, the architecture is
  preserved, and the result has been reviewed against the architecture. Until then it is not
  done.
- **Architecture audit before acceptance.** Completed work is audited against the architecture
  before it is accepted. Reported results are verified against the repository; unverified
  claims — including test counts — are not accepted at face value, and an audit may reject or
  downgrade work.
- **Regression is not permitted.** Existing passing tests must continue to pass. Tests are
  never disabled, weakened, or deleted to make a suite appear green.
- **Freeze before advancing.** When a mission meets its Definition of Done, its working state
  is frozen before the next mission begins. Completed work is not reopened casually.
- **Stop when done.** When a mission is complete, work stops. The next mission is not begun,
  and undefined future work is not started speculatively.

---

## 5. Engineering Standards

- **Testing.** Automated tests accompany every feature. The full suite must pass before
  completion, and regressions block completion. Test results are treated as claims until they
  are reproduced from the repository.
- **Determinism.** Prefer deterministic implementations; reserve language-model calls for
  tasks that genuinely require them.
- **Production quality only.** Placeholder implementations, dead code, and abandoned stubs are
  defects. Superseded modules are retired, not left to accumulate.
- **Documentation stays synchronized.** Documentation is part of the system and must match the
  code. Version strings, architecture documents, and status records must not drift from
  reality; drift is a defect to be corrected.
- **Commits and releases mark working states.** History is organized into logical, labeled
  commits, and stable milestones are tagged. Each tagged state is a working state.
- **Refactoring restraint.** The system is not rewritten wholesale. Improvements are
  incremental and preserve existing public boundaries. Working subsystems are left working,
  and large restructuring requires explicit approval.
- **Performance after correctness.** Correctness comes first. Performance is validated by
  benchmarks in a dedicated optimization phase, never at the expense of correctness or
  clarity.

---

## 6. AI Collaboration Rules

AMALGAM is built by AI engineering agents working under human direction. The following bind
every such agent.

- **Repository first.** Understand the repository and the preserved record before acting.
  Inspect the target and related components before modifying anything.
- **Inspect before implementing.** No implementation without understanding where it belongs.
  If required information is unavailable, inspect for it; if it remains unknown, say so.
- **Never hallucinate.** Do not invent architecture, APIs, file locations, results, or
  history. Do not fabricate test outcomes or repository state. Reported results are verified
  against the repository.
- **Require a specification.** Refuse to implement undefined work. If a mission's
  specification does not exist, it must be created before implementation, not imagined during
  it.
- **Preserve the architecture.** Follow the existing architecture and layer boundaries. Do not
  introduce parallel or competing systems, and do not break existing public boundaries.
- **Separate design from implementation.** Design intent (the design record) and
  implementation fact (the repository) are distinct and are kept distinct. Neither is
  presented as the other.
- **Recovery documents take precedence for history.** When reconstructing intent or history,
  the preserved recovery documents are authoritative over memory or re-interpretation.
  Conflicts in the record are preserved and marked, not reconciled.
- **Report uncertainty and stop at boundaries.** State what is unknown and what was inspected.
  When a task is complete, stop; do not drift into unrelated or future work.

---

## 7. Documentation Standards

AMALGAM's documents fall into fixed categories, and each category has a distinct role.

- **Canonical documents** define present truth: the operating manual, the architecture
  description, the current architecture state, and this constitution. They govern how the
  system is built and describe what exists now.
- **Historical documents** record the past. Design history (how intent evolved) and
  implementation history (what the repository actually contains) are kept strictly separate.
  Superseded content is preserved and marked, never rewritten to appear consistent.
- **Runtime and process documents** track the state of ongoing work. Among these, a single
  state record is the source of truth for development progress.
- **Generated documents** are derived from the state record and are never edited by hand; they
  are regenerated from their source. Hand-editing a generated document is prohibited.
- **How documentation evolves.** When code changes, the documents that describe it change with
  it, in the same effort. Documentation must be accurate, substantive, and current; a
  placeholder or a table of contents is not documentation. Conflicts between documents are
  surfaced and marked rather than silently resolved.

---

## 8. Governance

- **Ownership of decisions.** Architectural and roadmap authority rests with the project
  owner. Frozen architectural decisions and public boundaries change only by explicit owner
  decision.
- **How architectural decisions are made.** A change is evaluated against the permanent
  principles and the durable scale question, placed correctly under the Golden Rule, and
  accepted only after it is implemented, tested, and audited against the architecture.
  Accepted decisions are then frozen.
- **How roadmap changes happen.** The roadmap changes only by explicit owner decision. When it
  changes, prior roadmap versions are preserved in full rather than deleted or overwritten;
  the record shows every version and its conflicts.
- **How new missions are introduced.** A new mission enters only with a specification —
  objective, scope, deliverables, acceptance criteria — that fits the existing architecture
  and carries a single objective. Undefined missions are not started.
- **How deprecated ideas are handled.** Ideas that are abandoned, deferred, or only partially
  realized are archived with their status and rationale, not erased. A placeholder left for a
  deferred idea is never treated as an implemented feature.

---

## 9. Amendment Process

- **This constitution is permanent but amendable.** It changes only by explicit project-owner
  decision and only on the basis of evidence — repository fact or preserved design history —
  never on assumption.
- **Amendments expand; they do not quietly contradict.** New articles clarify or extend
  existing ones. An amendment that would reverse a permanent principle (Sections 2 and 3)
  requires explicit owner approval and must state what it supersedes. Superseded text is
  preserved and marked, consistent with the rule that conflicts are recorded, not overwritten.
- **What requires owner approval.** Changing a frozen architectural decision; altering the
  fixed dependency direction or layer ownership; breaking or renaming an existing public
  boundary; changing the roadmap; or amending the permanent principles of this constitution.
- **What does not.** Additive capabilities that fit the architecture and follow the Golden
  Rule; new tools introduced through registration without altering the dispatch path;
  corrections that bring documentation back into sync with the code; and clarifying language
  that does not change the meaning of a permanent law.
- **Versioning.** Each amendment is versioned and dated, and its rationale is recorded, so the
  constitution's own history remains as traceable as the system it governs.

---

*This constitution states permanent law only. It contains no implementation detail, no
roadmap, and no mission numbering. Every article is grounded in AMALGAM's recovered record;
where that record preserved a conflict, this document preserves it and does not resolve it.*
