# FUTURE_PROPOSALS.md

> **Document type:** Design-history recovery (engineering historian).
> **Source:** `AMALGAM_FULL_CONVERSATION.md`.
> **Purpose:** Recover every capability/feature that was PROPOSED but NOT completed - deferred,
> abandoned, or accepted-for-future. Each item records the original proposal, timestamp,
> status, and dependencies. **No future mission is created here** (per instruction); this only
> catalogs proposals that already appeared in the conversation.
>
> **Status vocabulary:** ACCEPTED-FUTURE (approved for later) / DEFERRED (postponed, no commit)
> / ABANDONED (explicitly dropped or superseded) / PARTIAL (a fragment shipped).
>
> **Sourcing legend:** `[VERBATIM]` / `[RECOVERED]` / `[REPO]`.

---

## 1. Provider Framework (Bring-Your-Own-Infrastructure)

**Timestamp:** 6/29/2026, ~10:14-10:16 AM. **Origin:** user's "free 250 GB Telegram storage" idea.
`[VERBATIM]`:
> ### ✅ Future Epic  > **Provider Framework**
> Inside it: Local Storage / Telegram Storage / Google Drive / Dropbox / OneDrive / S3 / Self-hosted storage

`[VERBATIM]` principle: "AMALGAM shouldn't own anything. It should integrate everything."
**Status:** ACCEPTED-FUTURE. PARTIAL only - `.amalgam-core/provider.py` (7/6) realizes
provider failover for coding models; the storage Provider Framework was never built.
**Dependencies:** Engine/Service abstraction. **Related missions:** none numbered.

---

## 2. Personal Knowledge Base (proposed as Mission 6, Scheme C)

**Timestamp:** 6/29/2026, 12:06:27 PM.
`[VERBATIM]`:
> ### I actually think this should be **Mission 6**. Not browser automation. Not voice.
> A **Personal Knowledge Base**.
> ... knowledge_base/ (resume.md, ideas.md, architecture.md, ...) + commands: learn / summarize / search knowledge / find all AI ideas.
Three levels described: Level 1 key-value memory (shipped), Level 2 Knowledge Base folder,
Level 3 full RAG.
**Status:** ABANDONED as a numbered mission (Scheme C's Mission 6 was replaced by the
"Engineer Core" pivot, Scheme D). **Dependencies:** Knowledge Engine (Mission 4).

---

## 3. RAG / Embeddings / Semantic search

**Timestamp:** 6/28/2026, 2:00 AM (v0.5 milestone) and reiterated as "Level 3" (6/29 12:06 PM).
`[VERBATIM]` Mission 4 explicitly EXCLUDED it: "Mission 4 is **NOT RAG**. No embeddings. No
vector database."
**Status:** DEFERRED (was slated for "v0.5 - Knowledge"; never built). **Dependencies:**
Knowledge Engine.

---

## 4. Browser Engine / Browser automation

**Timestamps / appearances:** v0.4 milestone (6/28 2:00 AM); Scheme C Mission 8 (6/29 2:09 PM);
Scheme D Mission 7 "Tool System" region; "Gamma" roadmap (6/29 11:10 AM).
`[VERBATIM]` (6/29 11:10 AM, deferred intent): "# ❌ Mission 4 is NOT Browser." and later a
"real browser engine (navigate / inspect DOM / extract / login / click / download / upload)."
**Status:** ABANDONED / never built. Repeatedly deferred in favor of internal capabilities.
**Dependencies:** Tool layer.

## 5. Vision

**Appearances:** v0.7 "Desktop OS" (6/28 2:00 AM); Scheme C Mission 9 (6/29 2:09 PM); "Gamma".
**Status:** DEFERRED / never built. `[REPO]` an empty `vision/` directory exists (placeholder).

## 6. Voice

**Appearances:** v0.7 "Desktop OS"; Scheme C Mission 10 (6/29 2:09 PM); "Gamma".
`[VERBATIM]` (Genesis-era vision, 6/27): '"Hey Juju..." -> "Yes?" ... No typing.'
**Status:** DEFERRED / never built. `[REPO]` an empty `voice/` directory exists (placeholder).

## 7. Git Intelligence

**Appearances:** Scheme C Mission 7 (6/29 2:09 PM); "Gamma".
`[VERBATIM]` intended capability: "Show modified files. / Explain today's commits."
**Status:** ABANDONED as a numbered mission. `[Historian note]` a read-only `workspace/git.py`
(branch detection) shipped in Mission 3, but "Git Intelligence" as a feature did not.

## 8. Plugin System / Plugin SDK / Plugin Loader

**Appearances:** Scheme A Mission 4 "Plugin Loader" (6/28); Scheme B Mission 7 "Plugin System";
"Delta" roadmap (6/29 11:10 AM: "Plugin SDK").
**Status:** ABANDONED / never built. `[REPO]` an empty `plugins/` directory exists (placeholder).

## 9. Dependency Injection

**Appearances:** Scheme A Mission 5 "Dependency Injection"; Scheme B Mission 8 "DI".
`[VERBATIM]` (Codex-audit backlog): "Container -> inject() -> Dispatcher".
**Status:** ABANDONED / never built as a mission.

## 10. Kernel State Machine

**Appearances:** Scheme A Mission 6 "Kernel State Machine"; Codex-audit "biggest thing missed."
`[VERBATIM]` proposed states: "BOOTING / READY / THINKING / PLANNING / EXECUTING / WAITING /
ERROR / SHUTDOWN."
**Status:** ABANDONED as a distinct mission. `[Historian note]` state-machine logic DID appear
later inside the Goal lifecycle (Mission 6.4) and Mission lifecycle (7.1.x), but not as the
"Kernel State Machine" originally proposed.

## 11. Self-Improvement / self-updating AMALGAM

**Appearances:** user's founding vision (6/27 10:33 AM: "it can even update with himself...
asking me permission"); Scheme D Mission 13 "Self Improvement."
`[VERBATIM]` architect's explicit deferral: "Self-improvement is **not Version 0.3**.
Self-improvement is **Version 2.0+**." User agreed ("AMALGAM khud ko baad mein update karega").
**Status:** DEFERRED to v2.0+. **Dependencies:** the entire autonomous engineering stack.

## 12. Self Verification / Self Debugging (Scheme D Missions 10-11)

`[VERBATIM]` Mission 10 "Self Verification" (74 tests -> find failures -> repair -> 74 passed);
Mission 11 "Self Debugging" (compiler error -> analyze -> fix -> retry).
**Status:** PARTIAL - realized early inside the Autonomous Agent Core (Evaluator +
ReflectionEngine + RetryManager, Mission 6.4), not as standalone Missions 10-11.

## 13. Mission Memory (Scheme D Mission 12)

**Status:** PARTIAL - the ExecutionMemory (6.4) and the `.amalgam-core` HISTORY.json/STATE.json
system (7/6) cover part of this intent; not built as "Mission 12."

## 14. Desktop / Mobile / Web clients, API server, Cloud Sync

**Appearances:** Juju roadmap V5.0 (6/27); v2.0/v3.0 vision (6/28 1:55 AM); "Delta".
`[VERBATIM]` (v2.0/v3.0): "API server / Web UI / Mobile companion / Distributed execution /
Remote workers ... Runs continuously / Watches projects."
**Status:** DEFERRED (v2.0/v3.0 vision; nothing built).

## 15. SRGPT (university deployment)

**Appearances:** throughout (6/27 onward). The originating real-world use case (SR University
assistant built on the AMALGAM platform).
**Status:** DEFERRED (never built; positioned as a downstream product on top of AMALGAM).

---

## Summary table (proposals NOT completed)

| Proposal | First seen | Status |
|----------|-----------|--------|
| Provider Framework (Telegram/BYOI) | 6/29 | ACCEPTED-FUTURE / PARTIAL (provider.py) |
| Personal Knowledge Base | 6/29 | ABANDONED (as Mission 6) |
| RAG / Embeddings | 6/28 | DEFERRED |
| Browser Engine | 6/28 | ABANDONED |
| Vision | 6/28 | DEFERRED (empty dir) |
| Voice | 6/27 | DEFERRED (empty dir) |
| Git Intelligence | 6/29 | ABANDONED (partial: git.py) |
| Plugin System / SDK | 6/28 | ABANDONED (empty dir) |
| Dependency Injection | 6/28 | ABANDONED |
| Kernel State Machine | 6/28 | ABANDONED (partial elsewhere) |
| Self-Improvement | 6/27 | DEFERRED to v2.0+ |
| Self Verify / Debug | 6/29 | PARTIAL (in 6.4) |
| Mission Memory | 6/29 | PARTIAL (.amalgam-core) |
| Desktop/Mobile/Web/API/Cloud | 6/27 | DEFERRED (v2/v3) |
| SRGPT | 6/27 | DEFERRED |

*End of FUTURE_PROPOSALS.md*
