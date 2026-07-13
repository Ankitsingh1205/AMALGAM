"""Mandatory deterministic review gate with optional structured model findings."""
from __future__ import annotations

from brain.engineering_contracts import EngineeringPlan, ReviewVerdict


class EngineeringReviewer:
    def review(self, plan: EngineeringPlan, changed_files: list[str], test_evidence: list[dict]) -> ReviewVerdict:
        scope = {path for task in plan.tasks for path in task.affected_paths}
        changed = set(changed_files)
        findings: list[str] = []
        checks = {
            "scope": changed.issubset(scope),
            "tests": bool(test_evidence) and all(item.get("passed") for item in test_evidence),
            "security": not any(self._sensitive(path) for path in changed),
            "architecture": all(task.action in {"write_file", "replace_text", "run_python", "list_files"} for task in plan.tasks),
            "acceptance": all(task.acceptance_criteria for task in plan.tasks),
        }
        if not checks["scope"]:
            findings.append(f"unplanned changed paths: {sorted(changed - scope)}")
        if not checks["tests"]:
            findings.append("required verification did not pass")
        if not checks["security"]:
            findings.append("sensitive file pattern detected")
        if not checks["architecture"]:
            findings.append("unregistered action detected")
        if not checks["acceptance"]:
            findings.append("task lacks acceptance criteria")
        evidence = [f"changed={sorted(changed)}", f"planned={sorted(scope)}", f"tests={test_evidence}"]
        return ReviewVerdict(all(checks.values()), findings, evidence, checks)

    @staticmethod
    def _sensitive(path: str) -> bool:
        lowered = path.lower()
        return any(token in lowered for token in (".env", "secret", "credential", "private_key", "id_rsa"))
