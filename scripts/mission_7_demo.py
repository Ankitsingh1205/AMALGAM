"""Mission 7 end-to-end closure demo (Mission 7.7).

Exercises the COMPLETE Mission 7 orchestration stack in one run:

    ChiefAgent -> WorkPool (planner capability)
        -> FleetWorker(planner) decomposes the goal
        -> ChiefAgent + DependencyResolver schedule sub-tasks in DAG order
        -> FleetWorker(compute) executes each step through the KERNEL
           (Dispatcher -> ToolWrapper -> hardened Calculator)
        -> ChiefAgent aggregates completion -> mission result

The planner is deterministic (no LLM) so the demo is reproducible and
CI-runnable; with Ollama available the identical stack runs LLM-backed
via ``python main.py --mission "GOAL"``.

Exit code 0 = every verification assertion passed.
"""

import sys
import uuid
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from agents.chief_agent import ChiefAgent
from brain.dependency_resolver import DependencyResolver
from brain.fleet_manager import FleetManager
from brain.fleet_worker import FleetWorker
from brain.messaging import Messaging
from brain.shared_context import SharedContext
from brain.work_pool import WorkPool
from kernel.executor import Executor
from kernel.task import Task
from config import constants

GOAL = "Compute the mission telemetry: 144*82, then (11808+192)/100, then 2**10"
EXPECTED = {"144*82": 11808, "(11808+192)/100": 120.0, "2**10": 1024}


def main() -> int:
    kernel = Executor()
    kernel.boot()

    messaging = Messaging()
    work_pool = WorkPool(messaging)
    resolver = DependencyResolver()
    fleet = FleetManager(messaging)
    context = SharedContext()
    context.set("task", GOAL)

    executed: dict[str, object] = {}

    def planner_handler(task: dict) -> dict:
        """Deterministic decomposition: goal -> dependent compute steps."""
        steps = list(EXPECTED.keys())
        sub_tasks, previous = [], None
        for expression in steps:
            step_id = str(uuid.uuid4())
            sub_tasks.append({
                "id": step_id,
                "depends_on": [previous] if previous else [],
                "required_capability": "compute",
                "action": constants.ACTION_CALCULATE,
                "data": expression,
            })
            previous = step_id
        print(f"  [planner] decomposed goal into {len(sub_tasks)} dependent steps")
        return {"tasks": sub_tasks}

    def compute_handler(task: dict) -> object:
        """Execute a step through the kernel dispatch path (ToolWrapper)."""
        result = kernel.execute(Task(
            intent="mission_step",
            action=task["action"],
            data=task["data"],
        ))
        executed[task["data"]] = result
        print(f"  [worker]  {task['data']} = {result}")
        return result

    workers = [
        FleetWorker("planner_1", ["planner"], work_pool, planner_handler),
        FleetWorker("compute_1", ["compute"], work_pool, compute_handler),
        FleetWorker("compute_2", ["compute"], work_pool, compute_handler),
    ]
    for worker in workers:
        worker.start()

    chief = ChiefAgent(work_pool, resolver, context, messaging, fleet_manager=fleet)

    print(f"MISSION : {GOAL}")
    print("STACK   : ChiefAgent -> WorkPool -> FleetWorkers -> Kernel -> ToolWrapper -> Calculator")
    print()

    result = chief.run(context)

    for worker in workers:
        worker.stop()

    print()
    print(f"RESULT  : success={result.get('success')} errors={result.get('errors') or 'none'}")

    # ----------------------------- verification -----------------------------
    failures = []
    if not result.get("success"):
        failures.append(f"mission reported failure: {result.get('errors')}")
    for expression, expected in EXPECTED.items():
        actual = executed.get(expression)
        if actual != expected:
            failures.append(f"step '{expression}': expected {expected}, got {actual!r}")

    if failures:
        print("VERIFY  : FAILED")
        for failure in failures:
            print(f"  - {failure}")
        return 1

    print("VERIFY  : PASSED - goal decomposed, DAG-scheduled, kernel-executed, aggregated")
    return 0


if __name__ == "__main__":
    sys.exit(main())
