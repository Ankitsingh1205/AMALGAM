from __future__ import annotations

import concurrent.futures
import uuid
from typing import Any, Optional

from brain.goal.goal import Goal
from brain.queue.task_queue import TaskQueue
from brain.evaluator.evaluator import Evaluator
from brain.reflection.reflection_engine import ReflectionEngine
from brain.retry.retry_manager import RetryManager
from brain.memory.execution_memory import ExecutionMemory
from kernel.executor import Executor as KernelExecutor
from kernel.task import Task
from config import constants
from services.logger import get_logger


class AutonomousExecutor:
    """Autonomous execution engine that orchestrates goal completion.

    The executor follows a canonical loop:

    Goal → Analyze → Plan → Queue Tasks → Execute → Verify → Reflect → Retry → Complete

    Each step is recorded in execution memory. The loop continues automatically
    until the goal reaches a terminal state or recovery becomes impossible.

    Attributes:
        _kernel: Existing ``KernelExecutor`` for dispatching tasks.
        _queue: ``TaskQueue`` for sequential task management.
        _evaluator: ``Evaluator`` for result validation.
        _reflection: ``ReflectionEngine`` for failure analysis.
        _retry: ``RetryManager`` for bounded retry logic.
        _memory: ``ExecutionMemory`` for audit records.
        _execution_timeout: Maximum seconds to wait for a single task.
        _logger: Structured logger instance.
    """

    def __init__(
        self,
        kernel_executor: Optional[KernelExecutor] = None,
        task_queue: Optional[TaskQueue] = None,
        evaluator: Optional[Evaluator] = None,
        reflection: Optional[ReflectionEngine] = None,
        retry: Optional[RetryManager] = None,
        memory: Optional[ExecutionMemory] = None,
        execution_timeout: float = 30.0,
    ) -> None:
        self._kernel = kernel_executor or KernelExecutor()
        self._queue = task_queue or TaskQueue()
        self._evaluator = evaluator or Evaluator()
        self._reflection = reflection or ReflectionEngine()
        self._retry = retry or RetryManager()
        self._memory = memory or ExecutionMemory()
        self._execution_timeout = execution_timeout
        self._logger = get_logger("autonomous_executor")
        # Reuse a single thread pool across all task executions to avoid
        # the overhead of creating and tearing down a pool for every task.
        self._executor = concurrent.futures.ThreadPoolExecutor(max_workers=1)
        # Cache for goal snapshots to avoid repeated as_dict() constructions.
        self._last_goal_key: Optional[tuple] = None
        self._last_goal_dict: Optional[dict] = None

    def _snapshot(self, goal: Goal) -> dict:
        """Return the goal dict, caching when the goal state hasn't changed."""
        key = (goal.status, goal.plan_version, goal.error, goal.result)
        if self._last_goal_key != key:
            self._last_goal_dict = goal.as_dict()
            self._last_goal_key = key
        return self._last_goal_dict

    def __del__(self) -> None:
        """Ensure the thread pool is shut down on GC."""
        self._executor.shutdown(wait=False)

    def run(self, description: str, priority: int = constants.GOAL_PRIORITY_NORMAL) -> Goal:
        """Run the full autonomous loop for a new goal.

        Creates a ``Goal``, transitions it through the lifecycle, and
        returns the terminal goal object.

        Args:
            description: Human-readable goal description.
            priority: Optional priority (default ``NORMAL``).

        Returns:
            The completed or failed ``Goal``.
        """
        goal = Goal(
            id=str(uuid.uuid4()),
            description=description,
            priority=priority,
            status=constants.GOAL_STATUS_NEW,
        )

        self._logger.info("goal created", goal_id=goal.id, description=description)
        self._memory.record(goal.id, "created", goal=self._snapshot(goal))

        try:
            self._analyze(goal)
            self._plan(goal)
            self._ready(goal)
            self._execute_loop(goal)
        except Exception as e:
            goal.transition(constants.GOAL_STATUS_FAILED)
            goal.error = str(e)
            self._memory.record(
                goal.id,
                "fatal_error",
                goal=self._snapshot(goal),
                error=goal.error,
            )
            self._logger.error("fatal error in autonomous loop", goal_id=goal.id, error=goal.error)

        if not goal.is_terminal():
            goal.transition(constants.GOAL_STATUS_FAILED)
            goal.error = "Loop exited without reaching a terminal state."

        self._memory.record(goal.id, "finished", goal=self._snapshot(goal))
        self._logger.info("goal finished", goal_id=goal.id, status=goal.status)

        # Cleanup: flush execution memory, release retry budget, and clear the queue
        self._memory.flush()
        self._retry.reset(goal.id)
        self._queue.clear_pending()

        return goal

    def _analyze(self, goal: Goal) -> None:
        """Transition the goal to ``ANALYZING`` and record the step."""
        goal.transition(constants.GOAL_STATUS_ANALYZING)
        self._memory.record(goal.id, "analyze", goal=self._snapshot(goal))
        self._logger.info("goal analyzing", goal_id=goal.id)

    def _plan(self, goal: Goal) -> None:
        """Transition the goal to ``PLANNING``, create a plan, and record it."""
        goal.transition(constants.GOAL_STATUS_PLANNING)
        goal.plan = self._generate_plan(goal.description)
        self._memory.record(goal.id, "plan", goal=self._snapshot(goal), plan=goal.plan)
        self._logger.info("goal planned", goal_id=goal.id, plan=goal.plan)

    def _ready(self, goal: Goal) -> None:
        """Transition the goal to ``READY`` and create queued tasks from the plan."""
        goal.transition(constants.GOAL_STATUS_READY)
        tasks = self._create_tasks_from_plan(goal)
        for task in tasks:
            self._queue.enqueue(task)
        self._memory.record(
            goal.id,
            "ready",
            goal=self._snapshot(goal),
        )
        self._logger.info("goal ready", goal_id=goal.id, task_count=len(tasks))

    def _execute_loop(self, goal: Goal) -> None:
        """Core execution loop: dequeue, execute, evaluate, reflect, retry."""
        goal.transition(constants.GOAL_STATUS_RUNNING)
        self._memory.record(goal.id, "running", goal=self._snapshot(goal))

        while not goal.is_terminal():
            if self._queue.is_paused():
                self._logger.debug("queue paused", goal_id=goal.id)
                break

            if self._queue.is_empty():
                # All tasks completed successfully
                goal.transition(constants.GOAL_STATUS_VERIFYING)
                self._memory.record(goal.id, "verifying", goal=self._snapshot(goal))
                if self._verify_goal(goal):
                    goal.transition(constants.GOAL_STATUS_COMPLETED)
                    goal.result = "All tasks completed successfully."
                else:
                    goal.transition(constants.GOAL_STATUS_FAILED)
                    goal.error = "Verification failed after all tasks completed."
                self._memory.record(goal.id, "verified", goal=self._snapshot(goal))
                break

            task = self._queue.dequeue()
            if task is None:
                continue

            self._memory.record(
                goal.id,
                "task_started",
                goal=self._snapshot(goal),
                task=task,
            )

            output, error = self._execute_task(task)

            verdict = self._evaluator.evaluate(output=output, error=error)

            self._memory.record(
                goal.id,
                "task_evaluated",
                goal=self._snapshot(goal),
                task=task,
                action=task.get("action"),
                output=output,
                error=error,
            )

            if self._evaluator.is_success(verdict):
                self._queue.complete_current(result=output)
                self._logger.info("task succeeded", goal_id=goal.id, task_id=task.get("id"))
                continue

            # Failure path: reflect, retry, or escalate
            self._queue.fail_current(error=verdict.get("message"))
            self._logger.info("task failed", goal_id=goal.id, task_id=task.get("id"))

            self._handle_failure(goal, task, output, error, verdict)

            if goal.is_terminal():
                break

    def _execute_task(self, task: dict) -> tuple[Any, Optional[str]]:
        """Dispatch a single task through the kernel executor with a timeout.

        Args:
            task: Task dictionary with at least ``action`` and ``data``.

        Returns:
            Tuple of (output, error). Error is ``None`` on success.
        """
        action = task.get("action")
        data = task.get("data")
        model = task.get("model")

        kernel_task = Task(
            intent=task.get("intent", constants.INTENT_GENERAL),
            action=action,
            model=model,
            data=data,
        )

        try:
            future = self._executor.submit(self._kernel.execute, kernel_task)
            output = future.result(timeout=self._execution_timeout)
            return output, None
        except TimeoutError:
            return None, f"Execution timed out after {self._execution_timeout} seconds"
        except Exception as e:
            return None, str(e)

    def _handle_failure(
        self,
        goal: Goal,
        task: dict,
        output: Any,
        error: Optional[str],
        verdict: dict,
    ) -> None:
        """Handle a task failure by reflecting, retrying, or escalating."""
        goal.transition(constants.GOAL_STATUS_REFLECTING)

        reflection = self._reflection.reflect(
            action=task.get("action"),
            output=str(output) if output is not None else None,
            error=error or verdict.get("message"),
        )

        self._memory.record(
            goal.id,
            "reflected",
            goal=self._snapshot(goal),
            task=task,
            reflection=reflection.get("reasoning"),
            error=error,
        )
        self._logger.info(
            "reflection generated",
            goal_id=goal.id,
            root_cause=reflection.get("root_cause"),
            strategy=reflection.get("strategy"),
        )

        decision = self._retry.decide_next_step(goal.id, reflection.get("strategy", ""))

        self._memory.record(
            goal.id,
            "retry_decision",
            goal=self._snapshot(goal),
            task=task,
            output=decision.get("message"),
        )
        self._logger.info(
            "retry decision",
            goal_id=goal.id,
            next_step=decision.get("next_step"),
        )

        next_step = decision.get("next_step")

        if next_step == constants.REFLECTION_STRATEGY_RETRY:
            self._retry.record_attempt(goal.id)
            # Re-enqueue the same task
            self._queue.enqueue(task.copy())
            goal.transition(constants.GOAL_STATUS_RUNNING)
            return

        if next_step == constants.REFLECTION_STRATEGY_REPLAN:
            self._retry.reset(goal.id)
            goal.transition(constants.GOAL_STATUS_REPLANNING)
            self._replan(goal)
            return

        if next_step == constants.REFLECTION_STRATEGY_ALTERNATIVE:
            self._retry.record_attempt(goal.id)
            # Create an alternative task and enqueue it
            alt_task = self._create_alternative_task(task)
            if alt_task:
                self._queue.enqueue(alt_task)
                goal.transition(constants.GOAL_STATUS_RUNNING)
                return
            else:
                self._logger.warning(
                    "no safe alternative task available, failing goal",
                    goal_id=goal.id,
                )

        # Escalation or give up
        goal.transition(constants.GOAL_STATUS_FAILED)
        goal.error = decision.get("message", "Recovery impossible.")

    def _replan(self, goal: Goal) -> None:
        """Replan a goal by clearing pending tasks and generating a new plan."""
        self._logger.info("replanning goal", goal_id=goal.id)
        self._queue.clear_pending()
        self._retry.reset(goal.id)
        goal.plan_version += 1
        goal.plan = self._generate_plan(goal.description)
        tasks = self._create_tasks_from_plan(goal)
        for task in tasks:
            self._queue.enqueue(task)
        self._memory.record(goal.id, "replan", goal=self._snapshot(goal), plan=goal.plan)
        goal.transition(constants.GOAL_STATUS_RUNNING)

    def _verify_goal(self, goal: Goal) -> bool:
        """Verify that the goal has been completed successfully.

        A goal passes verification only if every task belonging to the
        *current* plan version was completed successfully. For tasks
        that were retried, only the final status matters.

        Args:
            goal: The goal to verify.

        Returns:
            ``True`` if verification passes.
        """
        history = self._queue.list_history()
        current_plan_tasks = [
            entry for entry in history
            if entry.get("plan_version") == goal.plan_version
        ]

        if not current_plan_tasks:
            return False

        # Group by task id and take the final status of each task
        final_status: dict[str, str] = {}
        for entry in current_plan_tasks:
            tid = entry.get("id")
            if tid is not None:
                final_status[tid] = entry.get("status", "")

        return all(
            status == constants.TASK_STATUS_COMPLETED
            for status in final_status.values()
        )

    def _generate_plan(self, description: str) -> str:
        """Generate a high-level plan from a goal description.

        This is a deterministic heuristic planner. For more complex goals,
        an LLM-based planner can be substituted.

        Args:
            description: Goal description.

        Returns:
            A plan string.
        """
        text = description.lower()

        if any(word in text for word in ["calculate", "math", "compute", "sum"]):
            return "1. Extract the mathematical expression. 2. Execute calculator."

        if any(word in text for word in ["read", "file", "open", "content"]):
            return "1. Identify the file path. 2. Read the file. 3. Return contents."

        if any(word in text for word in ["write", "save", "create file"]):
            return "1. Identify target path. 2. Write content. 3. Verify file exists."

        if any(word in text for word in ["list", "show files", "directory", "ls"]):
            return "1. Identify target directory. 2. List files."

        if any(word in text for word in ["python", "run code", "execute script"]):
            return "1. Extract the Python code. 2. Execute via PythonExecutor. 3. Return output."

        if any(word in text for word in ["search", "web", "find online"]):
            return "1. Extract search query. 2. Search the web. 3. Return results."

        if any(word in text for word in ["remember", "store", "save data"]):
            return "1. Extract key and value. 2. Store in memory."

        if any(word in text for word in ["recall", "retrieve", "fetch memory"]):
            return "1. Extract key. 2. Recall from memory. 3. Return value."

        if any(word in text for word in ["project", "repository", "summarize", "overview"]):
            return "1. Analyze workspace. 2. Build knowledge graph. 3. Summarize results."

        return "1. Analyze user request. 2. Select appropriate tool or model. 3. Execute and return result."

    def _create_tasks_from_plan(self, goal: Goal) -> list[dict]:
        """Create concrete task dictionaries from a goal plan.

        This is a heuristic mapper. It inspects the goal description and
        plan to infer the right action and data.

        Args:
            goal: The goal with a plan.

        Returns:
            List of task dictionaries.
        """
        text = goal.description.lower()
        tasks = []

        # Math
        if goal.description.strip().replace(" ", "").replace(".", "").replace("(", "").replace(")", "").isdigit() or \
           any(op in goal.description for op in ["+", "-", "*", "/"]):
            tasks.append({
                "id": str(uuid.uuid4()),
                "plan_version": goal.plan_version,
                "intent": constants.INTENT_MATH,
                "action": constants.ACTION_CALCULATE,
                "data": goal.description.strip(),
            })
            return tasks

        # Memory: remember
        if text.startswith("remember "):
            payload = goal.description[9:]
            if "=" in payload:
                key, value = payload.split("=", 1)
                tasks.append({
                    "id": str(uuid.uuid4()),
                    "plan_version": goal.plan_version,
                    "intent": constants.INTENT_MEMORY,
                    "action": constants.ACTION_REMEMBER,
                    "data": (key.strip(), value.strip()),
                })
            return tasks

        # Memory: recall
        if text.startswith("recall "):
            tasks.append({
                "id": str(uuid.uuid4()),
                "plan_version": goal.plan_version,
                "intent": constants.INTENT_MEMORY,
                "action": constants.ACTION_RECALL,
                "data": goal.description[7:].strip(),
            })
            return tasks

        # Files: list
        if any(phrase in text for phrase in ["list files", "show files", "directory", "folders", "ls"]):
            tasks.append({
                "id": str(uuid.uuid4()),
                "plan_version": goal.plan_version,
                "intent": constants.INTENT_FILES,
                "action": constants.ACTION_LIST_FILES,
                "data": ".",
            })
            return tasks

        # Internet: search
        if any(phrase in text for phrase in ["search ", "search web", "google", "find online"]):
            query = goal.description
            for phrase in ["search web", "search", "google", "find online"]:
                query = query.replace(phrase, "").strip()
            tasks.append({
                "id": str(uuid.uuid4()),
                "plan_version": goal.plan_version,
                "intent": constants.INTENT_INTERNET,
                "action": constants.ACTION_SEARCH_WEB,
                "data": query,
            })
            return tasks

        # Python: run
        if any(phrase in text for phrase in ["run python", "execute python", "python:"]):
            code = goal.description
            for phrase in ["run python", "execute python", "python:"]:
                code = code.replace(phrase, "").strip()
            tasks.append({
                "id": str(uuid.uuid4()),
                "plan_version": goal.plan_version,
                "intent": constants.INTENT_PYTHON,
                "action": constants.ACTION_RUN_PYTHON,
                "data": code,
            })
            return tasks

        # Project: summary
        if any(phrase in text for phrase in [
            "explain my project", "summarize my project", "summarize this repository",
            "project overview", "project architecture", "show project architecture", "explain this repository",
        ]):
            tasks.append({
                "id": str(uuid.uuid4()),
                "plan_version": goal.plan_version,
                "intent": constants.INTENT_PROJECT,
                "action": constants.ACTION_PROJECT_SUMMARY,
                "data": goal.description,
            })
            return tasks

        # Coding: generate code
        if any(phrase in text for phrase in [
            "write code", "generate code", "write python", "python code",
            "create function", "create a function", "debug", "fix code",
            "implement", "program", "script", "algorithm",
        ]):
            tasks.append({
                "id": str(uuid.uuid4()),
                "plan_version": goal.plan_version,
                "intent": constants.INTENT_CODING,
                "action": constants.ACTION_GENERATE_CODE,
                "model": "qwen2.5-coder:7b",
                "data": goal.description,
            })
            return tasks

        # General: chat
        tasks.append({
            "id": str(uuid.uuid4()),
            "plan_version": goal.plan_version,
            "intent": constants.INTENT_GENERAL,
            "action": constants.ACTION_CHAT,
            "model": "qwen3:8b",
            "data": goal.description,
        })
        return tasks

    def _create_alternative_task(self, task: dict) -> Optional[dict]:
        """Create an alternative task when the primary strategy fails.

        Safe alternatives that do not interpolate user input into code
        strings are preferred. Returns ``None`` if no safe alternative
        exists.

        Args:
            task: The original failed task.

        Returns:
            An alternative task dictionary, or ``None`` if no safe
            alternative exists.
        """
        action = task.get("action")
        data = task.get("data")

        # Fallback: if internet fails, try LLM with what we know
        if action == constants.ACTION_SEARCH_WEB:
            return {
                "id": str(uuid.uuid4()),
                "plan_version": task.get("plan_version", 0),
                "intent": constants.INTENT_GENERAL,
                "action": constants.ACTION_CHAT,
                "model": "qwen3:8b",
                "data": f"I could not search the web for '{data}'. What do you know about this topic?",
            }

        # Fallback: if Python fails, try LLM
        if action == constants.ACTION_RUN_PYTHON:
            return {
                "id": str(uuid.uuid4()),
                "plan_version": task.get("plan_version", 0),
                "intent": constants.INTENT_GENERAL,
                "action": constants.ACTION_CHAT,
                "model": "qwen3:8b",
                "data": f"The following Python code failed: {data}. Can you explain why or provide a fix?",
            }

        # No safe alternative for calculator or file operations.
        # The retry manager will escalate to replan or user.
        return None

    def progress(self, goal_id: str) -> dict:
        """Return progress for a goal and its task queue.

        Args:
            goal_id: Goal identifier.

        Returns:
            Dictionary with queue progress and latest memory record.
        """
        queue_progress = self._queue.progress()
        latest = self._memory.recall_latest(goal_id)
        return {
            "queue": queue_progress,
            "latest_record": latest,
        }
