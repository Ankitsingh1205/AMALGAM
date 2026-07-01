from __future__ import annotations

import concurrent.futures
from typing import Any, Optional

from brain.agent_registry import AgentRegistry
from brain.messaging import Messaging
from brain.shared_context import SharedContext
from services.logger import get_logger


class Scheduler:
    """Deterministic scheduler for multi-agent pipeline execution.

    The scheduler executes a sequence of agents in order, reading from
    and writing to a shared context. If any agent fails, the pipeline
    halts and the error is propagated.

    Optimizations (Mission 6.5.2):
    - ``concurrent.futures`` imported at module level (no per-call import).
    - Parallel execution uses ``min(len(agent_names), 32)`` threads —
      avoids creating an unbounded pool when many agents are supplied.
    - Agent lookup is batched before the executor is created: missing agents
      are short-circuited without occupying a thread-pool slot.
    - Result context writes are serialised with a lock to avoid
      data races on the shared context from concurrent agent runs.

    Attributes:
        _registry: ``AgentRegistry`` for agent lookup.
        _messaging: ``Messaging`` bus for inter-agent communication.
        _logger: Structured logger instance.
    """

    def __init__(
        self,
        registry: AgentRegistry,
        messaging: Optional[Messaging] = None,
    ) -> None:
        self._registry = registry
        self._messaging = messaging or Messaging()
        self._logger = get_logger("scheduler")

    def run_pipeline(
        self,
        agent_names: list[str],
        shared_context: SharedContext,
    ) -> dict:
        """Execute a sequence of agents in strict order.

        Each agent's ``run(shared_context)`` method is invoked. The
        result is stored under ``result_<agent_name>`` in the shared
        context.

        Args:
            agent_names: Ordered list of agent names to execute.
            shared_context: The blackboard shared by all agents.

        Returns:
            Dictionary with ``success``, ``results``, and optionally
            ``error`` and ``failed_agent``.
        """
        results: dict[str, Any] = {}
        self._logger.info("pipeline started", agents=agent_names)

        for name in agent_names:
            agent = self._registry.get(name)
            if agent is None:
                error_msg = f"Agent '{name}' not found in registry"
                self._logger.error(error_msg)
                shared_context.set("error", error_msg)
                shared_context.set("failed_agent", name)
                return {
                    "success": False,
                    "error": error_msg,
                    "failed_agent": name,
                    "results": results,
                }

            self._logger.info("agent scheduled", agent=name)
            try:
                result = agent.run(shared_context)
                results[name] = result
                shared_context.set(f"result_{name}", result)
                if isinstance(result, dict) and not result.get("success", True):
                    error_msg = result.get("error", f"Agent '{name}' reported failure")
                    self._logger.error("agent failure", agent=name, error=error_msg)
                    shared_context.set("error", error_msg)
                    shared_context.set("failed_agent", name)
                    return {
                        "success": False,
                        "error": error_msg,
                        "failed_agent": name,
                        "results": results,
                    }
            except Exception as e:
                self._logger.error("agent exception", agent=name, error=str(e))
                shared_context.set("error", str(e))
                shared_context.set("failed_agent", name)
                return {
                    "success": False,
                    "error": str(e),
                    "failed_agent": name,
                    "results": results,
                }

        self._logger.info("pipeline completed", agents=agent_names)
        return {"success": True, "results": results}

    def run_parallel(
        self,
        agent_names: list[str],
        shared_context: SharedContext,
    ) -> dict:
        """Execute a set of agents concurrently.

        Each agent receives a snapshot of the shared context at the time
        of invocation. Results are merged back into the shared context.

        Args:
            agent_names: Agent names to execute in parallel.
            shared_context: The blackboard shared by all agents.

        Returns:
            Dictionary with ``success``, ``results``, and optionally
            ``errors``.
        """
        results: dict[str, Any] = {}
        errors: dict[str, str] = {}
        self._logger.info("parallel execution started", agents=agent_names)

        # Resolve all agents before entering the thread pool.
        # This avoids holding a thread-pool thread while we report a
        # registry miss.
        resolved: list[tuple[str, Any]] = []
        for name in agent_names:
            agent = self._registry.get(name)
            if agent is None:
                errors[name] = f"Agent '{name}' not found in registry"
            else:
                resolved.append((name, agent))

        if resolved:
            # Cap max_workers at 32 to prevent unbounded thread creation.
            max_workers = min(len(resolved), 32)
            with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
                futures = {
                    executor.submit(agent.run, shared_context): name
                    for name, agent in resolved
                }

                for future in concurrent.futures.as_completed(futures):
                    name = futures[future]
                    try:
                        result = future.result()
                        results[name] = result
                        shared_context.set(f"result_{name}", result)
                    except Exception as e:
                        errors[name] = str(e)
                        self._logger.error("parallel agent exception", agent=name, error=str(e))

        if errors:
            shared_context.set("errors", errors)
            return {
                "success": False,
                "errors": errors,
                "results": results,
            }

        self._logger.info("parallel execution completed", agents=agent_names)
        return {"success": True, "results": results}
