"""Read-only qwen2.5-coder:7b contract smoke test for the owner's Ollama host.

This script never executes a plan or mutates repository files. It validates
that the configured local model can emit an EngineeringPlan accepted by the
same strict schema used in production.
"""
from __future__ import annotations

from pathlib import Path
import os
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from brain.repository_context import RepositoryContextEngine
from brain.structured_reasoning import StructuredReasoner
from services.llm import LLMService, StructuredLLMError
from config import settings

MODEL = "qwen2.5-coder:7b"


def _ollama_host() -> str:
    return (
        os.environ.get("OLLAMA_HOST")
        or os.environ.get("AMALGAM_OLLAMA_HOST")
        or getattr(settings, "OLLAMA_HOST", None)
        or "http://127.0.0.1:11434"
    )


def _preflight() -> int | None:
    """Validate the Ollama environment before running the plan smoke.

    Returns a process exit code if the preflight fails (caller returns it),
    or ``None`` if the preflight passed and the plan smoke may proceed.
    """
    host = _ollama_host()
    print(f"OLLAMA HOST : {host}")
    print(f"MODEL       : {MODEL}")

    try:
        import ollama  # noqa: F401
    except ImportError:
        print("SMOKE FAIL: 'ollama' Python package is not installed.")
        print("  fix: pip install ollama")
        print("  then: ollama serve")
        return 1

    service = LLMService()
    if service.client is None:
        print("SMOKE FAIL: Ollama client unavailable.")
        print(str(service._unavailable_detail()))
        return 1

    try:
        resp = service.client.list()
        raw_models = None
        if isinstance(resp, dict):
            raw_models = resp.get("models", [])
        else:
            raw_models = getattr(resp, "models", None) or []
        available = set()
        for m in raw_models:
            name = m.get("name") if isinstance(m, dict) else getattr(m, "model", None)
            if name:
                available.add(name)
        if available and MODEL not in available:
            print(
                f"WARNING: model '{MODEL}' not found in Ollama. "
                f"Pull it with: ollama pull {MODEL}"
            )
    except Exception as error:
        # Do not crash on Ollama list() API quirks; just warn.
        print(f"WARNING: could not list Ollama models: {error}")

    return None


def main() -> int:
    preflight = _preflight()
    if preflight is not None:
        return preflight

    root = Path.cwd()
    try:
        before = RepositoryContextEngine(root).build()
        reasoner = StructuredReasoner(model=MODEL)
        plan = reasoner.plan(
            "Propose a plan to add one documentation sentence; do not execute it",
            before,
        )
        plan.validate()
        after = RepositoryContextEngine(root).build()
        if before.dirty_files != after.dirty_files:
            raise RuntimeError("read-only reasoning changed the repository")
    except StructuredLLMError as error:
        print(f"SMOKE FAIL: {error}")
        return 1
    print(f"PLAN     : {plan.plan_id} ({plan.plan_hash[:12]})")
    print(f"TASKS    : {len(plan.tasks)}")
    print("MUTATION : none")
    print("MISSION 8 MODEL SMOKE: PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
