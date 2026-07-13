"""Read-only qwen2.5-coder:7b contract smoke test for the owner's Ollama host.

This script never executes a plan or mutates repository files. It validates
that the configured local model can emit an EngineeringPlan accepted by the
same strict schema used in production.
"""
from __future__ import annotations

from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from brain.repository_context import RepositoryContextEngine
from brain.structured_reasoning import StructuredReasoner


def main() -> int:
    root = Path.cwd()
    before = RepositoryContextEngine(root).build()
    reasoner = StructuredReasoner(model="qwen2.5-coder:7b")
    plan = reasoner.plan(
        "Propose a plan to add one documentation sentence; do not execute it",
        before,
    )
    plan.validate()
    after = RepositoryContextEngine(root).build()
    if before.dirty_files != after.dirty_files:
        raise RuntimeError("read-only reasoning changed the repository")
    print(f"MODEL    : qwen2.5-coder:7b")
    print(f"PLAN     : {plan.plan_id} ({plan.plan_hash[:12]})")
    print(f"TASKS    : {len(plan.tasks)}")
    print("MUTATION : none")
    print("MISSION 8 MODEL SMOKE: PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
