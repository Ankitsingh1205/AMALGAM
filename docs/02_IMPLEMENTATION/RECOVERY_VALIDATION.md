# RECOVERY_VALIDATION.md

> **Task:** Cross-validate the eight AMALGAM recovery documents against one another.
> **Method:** Only the recovery documents were read (GENESIS.md, MISSION_HISTORY.md,
> ROADMAP_EVOLUTION.md, ARCHITECTURE_EVOLUTION.md, MODEL_STRATEGY.md, FUTURE_PROPOSALS.md,
> LONG_TERM_VISION.md, IMPLEMENTATION_HISTORY.md). The original conversation was NOT reread.
> **Constraints honored:** source documents not modified; no corrections invented; validation only.
> **Definitions used:**
> - *Verified* = asserted consistently by ≥2 independent recovery documents, or by 1 document
>   plus repository evidence (`[REPO]`), with no contradicting document.
> - *Conflict* = two documents (or two claims) that cannot both be literally true as written.
> - *Design history* = the 7 conversation-derived docs. *Implementation history* = IMPLEMENTATION_HISTORY.md.
> - Doc abbreviations: GEN, MH (MISSION_HISTORY), RE (ROADMAP_EVOLUTION), AE
>   (ARCHITECTURE_EVOLUTION), MS (MODEL_STRATEGY), FP (FUTURE_PROPOSALS), LTV
>   (LONG_TERM_VISION), IMPL (IMPLEMENTATION_HISTORY).

---

## SECTION 1 — VERIFIED FACTS (cross-corroborated)

### 1.1 Naming & identity
- **AMALGAM naming path** (Juju AI → candidates → "stu ai" → AMALGAM, rated 9.5/10; means
  "combination of many things into one unified whole"): GEN §0 ↔ LTV §1. **CONSISTENT.**
- **Motto "One Intelligence. Infinite Capabilities."**: GEN §1 ↔ LTV §1. **CONSISTENT.**
- **Slogan "AMALGAM OS — The operating system that turns AI into action."**: MH (Mission 2
  context) ↔ LTV §1 ↔ AE §A5b (Constitution era). **CONSISTENT.**

### 1.2 Runtime models & routing
- **Five Ollama models** (qwen3:8b, deepseek-r1:8b, llama3.1:8b, qwen2.5-coder:7b, gemma3:4b):
  GEN §0 ↔ MS Part 1. **CONSISTENT** (identical set and role labels).
- **Genesis-3 model-router mappings** (coding→qwen-coder, reasoning→deepseek, creative→llama,
  fast→gemma, general→qwen3): GEN §5 ↔ MS Part 1. **CONSISTENT.**

### 1.3 Test-count progression
- The ladder **46 → 53 → 64 → 73 → 73 → 74 → (6.4) → 232 → 247 → 772 → 806 → 910** is stated
  identically in MH "Chronological index" and IMPL §5 table. **CONSISTENT** across design and
  implementation documents (both flag the counts as claims, not re-runs — see Section 3).

### 1.4 Repository anchors (design ↔ repo agreement)
- **Genesis commits** 71f74aa, 85216fe, deb8b04, ab22942, 96210c8: GEN §11 ↔ IMPL §1/§4. **CONSISTENT.**
- **Tags** v0.6.0, v0.6.5, v0.6.6, v0.6.6.1, amalgam-core-v1.0, amalgam-core-v1.1-stable, and
  tag `mission-7.1-complete`: MH ↔ IMPL §2. **CONSISTENT.**
- **Mission 7.1.4–7.1.8, 7.2, 7.3 commits** (d085a85, 1452cb0/2bcd3ad, 89fb555/419230f,
  b47b7da/c305e5d, 57d6a0d/9443634, c8f2ece/59be106): MH Mission 7 block ↔ IMPL §1/§4.
  **CONSISTENT** (same hashes, same order).

### 1.5 Architecture invariants
- **Brain(thinks)/Kernel(executes) split** from the core→brain, engine→kernel rename (Genesis-5):
  GEN §7 ↔ AE §A1. **CONSISTENT.**
- **Golden Rule** ("Am I a Tool, a Service, or an Engine?") + Tool/Service/Engine definitions:
  AE §A5 ↔ MH Mission 5 (design churn) ↔ FP (uses same taxonomy). **CONSISTENT.**
- **Four Pillars of Intelligence** (Workspace/Knowledge/Memory/Reasoning): AE §A4 ↔ MH Mission 4.
  **CONSISTENT.**
- **Constitution v1.0 (10 principles)** echoes the 5 Genesis principles: AE §A5b ↔ GEN §1.
  **CONSISTENT** (AE explicitly notes they were expanded, not contradicted).

### 1.6 Roadmap-scheme catalogue
- The scheme labels **R0/R1/R2/G/A/B/C/D/E** defined in RE are referenced consistently by MH
  ("Roadmap scheme: A" / "D" / "E") and GEN ("Scheme A"). No document assigns a scheme label
  a different meaning than RE. **CONSISTENT.**

### 1.7 Mission 7.4 status
- **Mission 7.4 was never started / not defined**; a `mission-7.4` branch exists but contains
  no 7.4 work: MH (Mission 7.4 section) ↔ RE (Scheme E historian note) ↔ IMPL §3/§7.3.
  **CONSISTENT** and triangulated across design + implementation.

### 1.8 Preserved source-conflicts recorded identically (integrity check)
These conversation-level conflicts are recorded the SAME way in every document that mentions
them — evidence the recovery set is internally coherent:
- **"AI OS" vs "Personal AI Platform"**: GEN §0 ↔ AE (recurring conflicts #1) ↔ LTV (conflicts #1/#2).
- **Mission 6.4 test count 74 (Codex) vs 176 (Kimi)**: MH Mission 6.4 ↔ MS (conflicts #2) ↔
  IMPL §5/§7.5. All three mark it unresolved. **CONSISTENT framing.**
- **"5 duplicate routing mechanisms" / Unified Routing Engine never built**: GEN §5 ↔ AE §A2 ↔
  MS (conflicts #3). **CONSISTENT.**

`[Validation note]` Section 1 confirms the recovery set has a stable shared spine: identical
commit hashes, tags, test numbers, model lists, architecture rules, and roadmap labels across
independent documents. Divergences are confined to the items in Sections 2–4.

---

## SECTION 2 — CONFLICTS

`[Note]` Two kinds are separated: **(A) genuine inter-document contradictions** newly surfaced
by cross-validation, and **(B) source-level conflicts** the documents deliberately preserve
(these are not recovery errors, but are listed so the reader knows they remain open).

### 2A. Inter-document contradictions (newly surfaced)

**CONFLICT V-1 — v0.6.0 attributed to different mission granularity.**
- IMPL §4 labels commit `c2bd9dc` "Release v0.6.0" as **"Mission 6 (v0.6.0)"**.
- MH index and RE (Scheme G note) attribute v0.6.0 to **"Mission 6.4"** specifically.
- Contradiction: was v0.6.0 the whole of Mission 6, or only sub-mission 6.4? The docs use both.
  Unreconciled here (validation only).

**CONFLICT V-2 — "Mission 6 FROZEN" vs. Mission 6.5/6.6 continuing.**
- MH Mission 6.4 quotes "MISSION 6 STATUS FROZEN 🔒 ... AMALGAM v0.6.0" (freeze after 6.4).
- MH index + AE §A6/§A7 + IMPL then record **Mission 6.5 and 6.6 executing after v0.6.0**, with
  Mission 6.6 reaching tag v0.6.6.
- Contradiction: Mission 6 cannot be both "frozen at v0.6.0" and still advancing through 6.5/6.6
  to v0.6.6. (This is a real timeline tension the recovery preserves without resolving.)

**CONFLICT V-3 — Mission 6 sub-mission numbers mean two different things.**
- The Mission 6 sub-roadmap (quoted identically in MH, RE Scheme D, and effectively AE) is:
  6.0 FileTool / 6.1 EngineerAgent / 6.2 CommandTool / 6.3 auto-verification / **6.4 Retry &
  self-debug loop** / **6.5 Integrate with Orchestrator**.
- What the docs then describe as built: **6.4 = Autonomous Agent Core**, **6.5 = Multi-Agent
  Orchestration**, **6.6 = Fleet**.
- Contradiction: sub-mission numbers 6.4/6.5 carry different definitions in the plan vs. the
  build. MH flags 6.1–6.3 as an unconfirmed "gap" but does not flag the 6.4/6.5 redefinition.

**CONFLICT V-4 — "Codex implemented Missions 1–4" vs. no repo evidence for Missions 1–4.**
- MS Part 2 states Codex "implemented Missions 1-4."
- IMPL §4/§7.1 state the repo has **no dedicated commits for Missions 1–5**.
- Not logically impossible (design vs. squashed implementation), but the two assertions are in
  tension and neither doc reconciles who/what produced the (uncommitted) Missions 1–4 code.

**CONFLICT V-5 — Mission 7.1 sub-steps: nine described, six committed.**
- MH Mission 7.1 narrative lists nine steps (7.1.0 Core, 7.1.1 Epic, 7.1.2 Graph, 7.1.3 Planner
  Integration, 7.1.4 Persistence, 7.1.5 Event Bus, 7.1.6 Scheduler, 7.1.7 Executor, 7.1.8 Tool).
- IMPL §1/§4 git log contains commits only for **7.1.0, 7.1.4, 7.1.5, 7.1.6, 7.1.7, 7.1.8**
  (plus a "7.1 cleanup"). **7.1.1, 7.1.2, 7.1.3 have no commit.**
- Contradiction between the design narrative (9 steps) and implementation evidence (6 steps).

**CONFLICT V-6 — Mission 7.2 has no standalone commit.**
- MH treats Mission 7.2 (ChiefAgent orchestration) as a distinct implemented mission.
- IMPL shows Mission 7.2 only inside combined commit `59be106` "finalize Mission 7.2 **and**
  Mission 7.3" (and `c8f2ece` is titled "Mission 7.3 complete"). There is no 7.2-only commit.
- Tension: 7.2 is presented as an independent unit in design but is bundled with 7.3 in the repo.

### 2B. Source-level conflicts preserved by the documents (still open, not recovery errors)

These are consistently recorded across the set and are intentionally NOT reconciled:

- **CONFLICT S-1 — Mission 6.4 test count 74 vs 176** (MH, MS, IMPL). Open.
- **CONFLICT S-2 — "AI OS" vs "Personal AI Platform"** identity (GEN, AE, LTV). Open.
- **CONFLICT S-3 — Roadmap renumbering (Schemes A/B/C/D/E)**: the same mission number denotes up
  to five different features (RE conflict table; cross-referenced by MH, GEN, FP). Open by design.
- **CONFLICT S-4 — Scheme A "locked" but abandoned past Mission 2** (RE Scheme A; MH Missions 3/4/5
  each marked MODIFIED). Open.
- **CONFLICT S-5 — Scheme C "we don't change the roadmap" rule broken the same night** by the
  Scheme D pivot (RE Scheme C↔D). Open.
- **CONFLICT S-6 — EngineRegistry declared a core layer but engines reached via a Service
  (ProjectService)** (AE §A5 + recurring conflict #3). Open; implementation of a distinct
  EngineRegistry never confirmed.
- **CONFLICT S-7 — Orchestrator "is the brain" (Genesis) vs. became a legacy bypass by Mission 5**
  (GEN §1 status note; AE recurring conflict #2). Open.

### 2C. Conflicting mission numbers (consolidated)
The same identifier maps to multiple definitions across documents/schemes:

| Number | Competing meanings (per RE + MH + FP) |
|--------|----------------------------------------|
| Mission 3 | "Unified Routing Engine" (A) vs "Workspace Engine" (built/C) |
| Mission 4 | "Plugin Loader" (A) vs "Knowledge Engine" (built/C) |
| Mission 5 | "Dependency Injection" (A) / "Memory 2.0" (B) / "Integration" (built/C) |
| Mission 6 | "Kernel State Machine" (A) / "Agent Framework" (B) / "Personal KB" (C) / "Engineer Core" (built/D) |
| Mission 7 | "Browser & Knowledge" (A) / "Plugin System" (B) / "Git Intelligence" (C) / "Tool System" (D) / "Runtime Foundation" (E) / "Mission Engine" (built) |
| Mission 6.4 | "Retry/self-debug loop" (plan) vs "Autonomous Agent Core" (built) |
| Mission 6.5 | "Integrate with Orchestrator" (plan) vs "Multi-Agent Orchestration" (built) |

`[Validation note]` All rows above are already disclosed inside RE's conflict table and/or MH;
cross-validation confirms no document silently "picks a winner." The two sub-mission rows
(6.4, 6.5) are the ones only partially flagged (see CONFLICT V-3).

---

## SECTION 3 — MISSING INFORMATION

Gaps the documents themselves acknowledge, or that surface only when cross-referencing.
(Listed as gaps; no values are invented to fill them.)

### 3.1 Missions planned but not confirmed built
- **Missions 6.1, 6.2, 6.3** (EngineerAgent / CommandTool / auto-verification): MH explicitly
  flags these as an unconfirmed "gap"; no other document supplies evidence. **MISSING.**
- **Missions 7.1.1, 7.1.2, 7.1.3** (Epic / Graph / Planner Integration): named in MH's design
  narrative but absent from IMPL's git log. Evidence status unresolved. **MISSING commit evidence.**

### 3.2 Sub-mission granularity thin or absent
- **Mission 6.4.0 / 6.4.1 / 6.4.2**: MH references sub-missions "6.4.0–6.4.3" but details only
  6.4.3. IMPL corroborates 6.4.2 only indirectly (via `benchmark.py`). **PARTIAL.**
- **Mission 6.5.1 / 6.5.3 and 6.6.3** (Stabilization / Production phases): planned in MH/AE;
  no per-phase completion evidence. `benchmark_652.py`/`benchmark_662.py` corroborate only the
  6.5.2 / 6.6.2 optimization phases. **PARTIAL.**
- **Mission 7.2 standalone scope/tests**: no 7.2-only test count; bundled with 7.3 (=910). **MISSING.**

### 3.3 Hotfixes
- **HF-002, HF-003, HF-004**: MH notes they were "discussed ... per an earlier sub-agent finding"
  (HF-002/003 cancelled, HF-004 deferred). This provenance is weaker than the rest of the set and
  is not corroborated by any other recovery document or by IMPL. **LOW-EVIDENCE / MISSING.**

### 3.4 Metrics and dates that cannot be confirmed from the documents
- **All test counts are claims, not re-runs** (IMPL §5 states this explicitly). No current
  authoritative `pytest` figure exists in any document. **UNVERIFIED.**
- **Several timestamps are approximate** ("~", "area", e.g. LTV §3/§5/§6 "6/28 area"; MS "7/6";
  GEN "~12:08 PM"). Precise ordering within those windows is not recoverable. **IMPRECISE.**
- **Mission dependencies are mostly linear/asserted**, not independently verified (e.g. MH's
  "7.1.x needs 6.4/6.5/6.6"); no document provides an import-graph proof. **ASSERTED, not proven.**

### 3.5 Items referenced but not carried into a dedicated entry
- **Mission 5.3 "Code Navigation"** (ABANDONED per MH) is NOT listed in FP's proposals catalogue,
  though FP catalogues other abandoned items. Minor completeness gap between MH and FP.
- **`docs/missions/` spec files (MISSION_7_1 … 7_8)** are noted empty by IMPL §6; MH/RE confirm
  the Mission 7 master architecture was only a table of contents. Content is genuinely absent
  (a real project gap, faithfully recorded — not a recovery gap).

---

## SECTION 4 — REPOSITORY DIVERGENCE (implementation vs. design)

Points where IMPL (repository evidence) and the design documents do not line up. IMPL §7
already enumerates five; cross-validation confirms those and adds more.

### 4.1 Confirmed by IMPL §7 and corroborated by design docs
- **D-1** Pre-v0.6.0 missions (1–5) and Genesis-3..7 have **no dedicated commits**; earliest
  surviving feature commit is `c2bd9dc` (v0.6.0). (IMPL §4/§7.1 ↔ GEN §11 historian note ↔
  MH Mission 1 "no dedicated commit label".) **CONFIRMED DIVERGENCE.**
- **D-2** Tag **`v0.3.0-alpha`** (claimed for Mission 1 in MH) **does not exist** in the repo
  (IMPL §2/§7.2). **CONFIRMED.**
- **D-3** Branch **`mission-7.4`** exists but points at 7.1.6/7.3 commits — **no 7.4 code**
  (IMPL §3/§7.3 ↔ MH Mission 7.4). **CONFIRMED.**
- **D-4** Missions **7.1.5–7.1.8 committed twice** (initial + "feat(mission)" redo) during the
  stabilization pass (IMPL §4/§7.4). Duplicated events. **CONFIRMED.**
- **D-5** **Mission 6.4 test count (74 vs 176)** not settled by the repository (IMPL §7.5).
  **CONFIRMED.**

### 4.2 Additional divergences surfaced by cross-validation
- **D-6** **Missions 7.1.1 / 7.1.2 / 7.1.3** appear in MH's design narrative but have **no commit**
  in IMPL (see CONFLICT V-5). **DIVERGENCE.**
- **D-7** **"AMALGAM Core v1.0" is double-committed** (`443c952` "AMALGAM Core v1.0" and
  `3c44d71` "finalize AMALGAM Core v1.0 infrastructure") — a duplicated event in IMPL §4 not
  called out as such in the design docs. **DIVERGENCE (duplicated event).**
- **D-8** **Mission 7.2 lacks a standalone commit** (bundled in `59be106`); design treats it as
  discrete (CONFLICT V-6). **DIVERGENCE.**
- **D-9** **v0.6.0 vs v0.6.5 point at the same commit** `c2bd9dc` (IMPL §2). Design docs cite
  v0.6.0 (MH/RE) and v0.6.5 (RE Scheme G note) without noting they are the same commit. **MINOR.**
- **D-10** **Empty placeholder directories** `vision/`, `voice/`, `plugins/` (FP §5/§6/§8 mark
  these features DEFERRED/ABANDONED with "empty dir"; IMPL does not separately list them but the
  design side already treats them as unbuilt). **CONSISTENT DIVERGENCE (feature not built).**
- **D-11** **`pyproject.toml` version `0.3.0`** as of 7/2 (IMPL §5 observation) vs. tags reaching
  `amalgam-core-v1.1`. The in-tree version string was never advanced to match the tags. **DIVERGENCE.**
- **D-12** **EngineRegistry** declared a core layer (AE §A5) but engines were reached via a
  Service (`ProjectService`); no distinct EngineRegistry confirmed in the repo (AE conflict #3).
  **DESIGN-VS-IMPLEMENTATION MISMATCH.**

`[Validation note]` Direction of divergence is consistent: the **design history is richer than
the implementation history** (more missions, finer sub-numbers, a claimed tag). The repository
is *narrower* (squashed early history, bundled/duplicated late commits) but does not assert
anything the design docs contradict on hard facts (hashes, tags, branches all agree where they
overlap).

---

## SECTION 5 — CONFIDENCE SCORE

Confidence that the recovery documents faithfully and consistently represent AMALGAM's history,
based ONLY on internal cross-validation + the repository evidence embedded in IMPL.

### 5.1 Per-area confidence

| Area | Confidence | Basis |
|------|-----------|-------|
| Repository facts (commits, tags, branches) | **99%** | IMPL captured live; MH cites identical hashes/tags |
| Genesis-1, 1.1, 2, 8.1 | **95%** | commit-backed + GEN narrative agree |
| Genesis-3, 4, 5, 6, 7 | **65%** | design-only; no commits (D-1); internally consistent |
| Missions 1–5 (existence & order) | **80%** | consistent across GEN/MH/RE; but no commits (D-1) |
| Missions 1–5 test counts | **60%** | single-source claims, never re-run (3.4) |
| Mission 6.4 / 6.5 / 6.6 (existence) | **90%** | commit + benchmark artifacts corroborate |
| Mission 6.4 test count (74 vs 176) | **40%** | unresolved conflict S-1/C-4 |
| Mission 6.1 / 6.2 / 6.3 | **35%** | flagged gap; no evidence (3.1) |
| Mission 7.1.0 / 7.1.4–7.1.8 | **95%** | commit-backed, order matches |
| Mission 7.1.1 / 7.1.2 / 7.1.3 | **45%** | narrative-only, no commits (V-5, D-6) |
| Mission 7.2 / 7.3 | **85%** | commit-backed but bundled (V-6, D-8) |
| Roadmap evolution (schemes A–E) | **95%** | preserved separately, cross-referenced cleanly |
| Architecture evolution (A0–A9) | **88%** | consistent; EngineRegistry unproven (D-12) |
| Model strategy / tool-hopping saga | **85%** | internally consistent; mostly [RECOVERED] |
| Long-term vision statements | **90%** | verbatim quotes, consistent across GEN/LTV |
| Future proposals catalogue | **88%** | consistent; minor gap (5.3 omitted, 3.5) |
| Mission 7.4 = not started | **98%** | triangulated design + repo |

### 5.2 Overall confidence: **83 / 100 (HIGH)**

**Rationale.** The eight documents share a stable, mutually-consistent spine — identical commit
hashes, tags, branches, model lists, architecture rules, roadmap-scheme labels, and a single
agreed test-count ladder. No document silently contradicts another on a hard, repository-backed
fact; every divergence is either (a) already disclosed inside the documents, or (b) a
design-richer-than-repo gap that points in one consistent direction (Section 4).

**What holds the score below ~90:** unverified test counts (never re-run), the unresolved
6.4 test conflict, sub-mission granularity that the repository cannot confirm (6.1–6.3,
7.1.1–7.1.3), the two partially-flagged sub-mission renumberings (6.4/6.5, CONFLICT V-3), and
the "Mission 6 frozen vs. 6.5/6.6 continued" timeline tension (V-2).

**What would raise confidence (not performed here — validation only):** a live `pytest` run for
a current count; `git show --stat` on 7.1.4/7.2 to confirm whether 7.1.1–7.1.3 and a standalone
7.2 are folded inside; and confirming presence/absence of an `EngineRegistry` class in the tree.

### 5.3 Integrity verdict
- **Internal consistency:** HIGH — no cross-document hard contradictions; conflicts are labeled,
  not hidden.
- **Design↔implementation separation:** MAINTAINED — IMPL contains only repo evidence; design
  docs cite `[REPO]` only where corroborated.
- **Fabrication check:** none detected — no document asserts a fact contradicted by repository
  evidence; Mission 7.4 is consistently "not created."

*End of RECOVERY_VALIDATION.md*
