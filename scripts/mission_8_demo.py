"""Deterministic end-to-end Mission 8 engineering-loop demonstration.

The demo creates a real Git repository, reconstructs its context, presents an
exact plan, proves no pre-approval mutation, executes through the kernel,
runs verification, passes mandatory review, and creates a local commit.
The planner is deterministic so CI does not require Ollama; production uses
StructuredReasoner with the same EngineeringPlan contract and qwen2.5-coder:7b.
"""
from __future__ import annotations

from pathlib import Path
import subprocess
import sys
import tempfile

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from brain.engineering_contracts import EngineeringPlan, PlanTask
from brain.engineering_controller import EngineeringController


class DemoReasoner:
    def plan(self, goal, context):
        return EngineeringPlan(
            plan_id="mission-8-demo-plan",
            goal=goal,
            tasks=[PlanTask(
                id="implement",
                description="Add a tested production health-report module",
                action="write_file",
                capability="files",
                affected_paths=["health_report.py"],
                acceptance_criteria=["returns a structured healthy status"],
                data={
                    "path": "health_report.py",
                    "content": (
                        '"""Production health-report primitive."""\n\n'
                        "def health_report() -> dict[str, str]:\n"
                        "    return {\"status\": \"healthy\", \"system\": \"amalgam\"}\n"
                    ),
                },
            )],
            verification_commands=["python scripts/verify_health.py"],
        )


def git(root: Path, *args: str) -> str:
    result = subprocess.run(["git", *args], cwd=root, check=True,
                            capture_output=True, text=True)
    return result.stdout.strip()


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="amalgam-mission8-") as directory:
        root = Path(directory)
        git(root, "init", "-q")
        git(root, "config", "user.name", "AMALGAM Demo")
        git(root, "config", "user.email", "demo@amalgam.local")
        (root / ".gitignore").write_text(
            ".amalgam-core/MISSION_8_STATE.json\n__pycache__/\n", encoding="utf-8")
        scripts = root / "scripts"
        scripts.mkdir()
        (scripts / "verify_health.py").write_text(
            "import sys\nfrom pathlib import Path\nsys.path.insert(0, str(Path.cwd()))\n"
            "from health_report import health_report\n"
            "assert health_report() == {'status': 'healthy', 'system': 'amalgam'}\n",
            encoding="utf-8",
        )
        docs = root / "docs" / "00_START_HERE"
        docs.mkdir(parents=True)
        (docs / "ROADMAP_CANON.md").write_text("Mission 8 IN PROGRESS", encoding="utf-8")
        (docs / "MISSION_8_MASTER_ARCHITECTURE.md").write_text("FROZEN", encoding="utf-8")
        git(root, "add", ".")
        git(root, "commit", "-qm", "demo baseline")

        controller = EngineeringController(root, reasoner=DemoReasoner())
        pending = controller.run("Implement a tested production health report")
        assert pending["status"] == "awaiting_approval"
        assert not (root / "health_report.py").exists(), "mutation occurred before approval"
        print(f"PLAN     : {pending['plan']['plan_id']} ({pending['plan_hash'][:12]})")
        print("AUTHORITY: PASSED - repository unchanged before exact approval")

        result = controller.approve(pending["plan"]["plan_id"])
        assert result["status"] == "completed"
        assert result["review"]["approved"] is True
        assert all(item["passed"] for item in result["tests"])
        assert git(root, "show", "HEAD:health_report.py")
        assert not git(root, "status", "--porcelain")
        print("EXECUTE  : PASSED - kernel-scoped file change")
        print("VERIFY   : PASSED - acceptance test and mandatory review")
        print(f"COMMIT   : {result['commit_sha']}")
        print("MISSION 8 DEMO: PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
