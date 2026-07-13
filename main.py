"""AMALGAM entrypoint.

Modes (Mission 7.5):
    python main.py                       Interactive REPL (reactive path).
    python main.py --mission "GOAL"      Multi-agent mission orchestration:
                                         ChiefAgent -> WorkPool -> FleetWorkers.

Prior to Mission 7.5 the multi-agent system (Missions 6.5 - 7.3) was only
reachable from the test suite. This CLI wires PlannerAgent decomposition
and worker execution to the same kernel dispatch path used by the REPL.
"""

from __future__ import annotations

import argparse

from brain.brain import Brain
from kernel.executor import Executor
from kernel.task import Task
from config import constants
from services.logger import get_logger


def _print_result(action: str, result: object) -> None:
    """Present a dispatch result to the user (moved out of Dispatcher, ARCH-005)."""
    print()
    if action == constants.ACTION_PROJECT_SUMMARY and isinstance(result, dict):
        summary = result.get("summary", {})
        print("AMALGAM")
        print()
        print(f"Project Root : {summary.get('project_root')}")
        print(f"Packages     : {len(summary.get('python_packages', []))}")
        print(f"Documents    : {summary.get('documents')}")
        print(f"Symbols      : {summary.get('symbols')}")
        print(f"Relations    : {summary.get('relationships')}")
    else:
        print("AMALGAM:")
        print()
        print(result)


def run_interactive() -> None:
    """Reactive REPL: Brain intent analysis -> kernel dispatch."""
    logger = get_logger("cli")

    brain = Brain()
    kernel = Executor()
    kernel.boot()

    while True:
        try:
            user_input = input("\nYou: ")

            if user_input.lower() in constants.APP_EXIT_COMMANDS:
                print("AMALGAM shutting down...")
                logger.info("shutdown requested")
                break

            task = brain.think(user_input)
            result = kernel.execute(task)
            _print_result(getattr(task, "action", ""), result)

        except KeyboardInterrupt:
            print("\nAMALGAM shutting down...")
            logger.info("shutdown interrupted")
            break

        except Exception as e:
            logger.error(f"Runtime Error: {e}")


def run_mission(goal: str, timeout: float = 300.0) -> dict:
    """Execute a goal through the multi-agent orchestration stack.

    Builds the fleet (Messaging, WorkPool, FleetManager, agents,
    FleetWorkers), submits the goal to the ChiefAgent, and blocks until
    the mission completes or fails.

    Args:
        goal: Natural-language mission goal.
        timeout: Maximum seconds to wait for mission completion.

    Returns:
        The ChiefAgent mission result dictionary.
    """
    import threading
    import uuid

    from agents.chief_agent import ChiefAgent
    from agents.planner_agent import PlannerAgent
    from brain.dependency_resolver import DependencyResolver
    from brain.fleet_manager import FleetManager
    from brain.fleet_worker import FleetWorker
    from brain.messaging import Messaging
    from brain.shared_context import SharedContext
    from brain.work_pool import WorkPool

    logger = get_logger("cli.mission")

    kernel = Executor()
    kernel.boot()

    messaging = Messaging()
    work_pool = WorkPool(messaging)
    resolver = DependencyResolver()
    fleet = FleetManager()
    context = SharedContext()
    context.set("task", goal)

    # ----- Planner capability: decompose the goal into sub-tasks -------
    planner_agent = PlannerAgent(shared_context=context, messaging=messaging)

    def planner_handler(task: dict) -> dict:
        plan_context = SharedContext()
        plan_context.set("task", task.get("data", goal))
        outcome = planner_agent.run(plan_context)
        steps = outcome.get("plan", []) if isinstance(outcome, dict) else []

        sub_tasks = []
        previous_id = None
        for step in steps:
            step_id = str(uuid.uuid4())
            sub_tasks.append({
                "id": step_id,
                "depends_on": [previous_id] if previous_id else [],
                "required_capability": "llm",
                "action": constants.ACTION_CHAT,
                "data": str(step),
            })
            previous_id = step_id
        return {"tasks": sub_tasks}

    # ----- LLM capability: execute steps through the kernel ------------
    def llm_handler(task: dict) -> object:
        kernel_task = Task(
            intent="mission_step",
            action=task.get("action", constants.ACTION_CHAT),
            data=task.get("data"),
        )
        return kernel.execute(kernel_task)

    workers = [
        FleetWorker("planner_1", ["planner"], work_pool, planner_handler),
        FleetWorker("worker_1", ["llm"], work_pool, llm_handler),
        FleetWorker("worker_2", ["llm"], work_pool, llm_handler),
    ]
    for worker in workers:
        worker.start()

    chief = ChiefAgent(work_pool, resolver, context, messaging, fleet_manager=fleet)

    logger.info("mission starting", goal=goal)
    print(f"\nAMALGAM mission: {goal}\n")

    result: dict = {"success": False, "errors": ["Mission timed out"]}
    runner = threading.Thread(target=lambda: result.update(chief.run(context)), daemon=True)
    runner.start()
    runner.join(timeout=timeout)

    for worker in workers:
        worker.stop()

    print()
    print("AMALGAM mission result:")
    print()
    print(f"  Success : {result.get('success')}")
    errors = result.get("errors") or []
    if errors:
        print(f"  Errors  : {errors}")

    logger.info("mission finished", success=result.get("success"))
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description="AMALGAM - local-first autonomous agent OS")
    parser.add_argument(
        "--mission",
        metavar="GOAL",
        help="run a goal through the multi-agent orchestration stack",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=300.0,
        help="mission timeout in seconds (default: 300)",
    )
    args = parser.parse_args()

    if args.mission:
        run_mission(args.mission, timeout=args.timeout)
    else:
        run_interactive()


if __name__ == "__main__":
    main()
