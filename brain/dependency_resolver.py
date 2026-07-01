from __future__ import annotations

from collections import deque


class CycleError(Exception):
    """Raised when a circular dependency is detected in the DAG."""
    pass


class DependencyResolver:
    """Resolves task dependencies into an ordered execution plan.

    Uses Kahn's algorithm for topological sorting in O(V + E) time.
    Optimized for low allocation and fast dictionary lookups.
    """

    __slots__ = ()

    def resolve(self, tasks: list[dict]) -> list[dict]:
        """Resolve a list of tasks into a linear execution order.

        Each task must be a dict containing an ``id`` key and optionally
        a ``depends_on`` list of IDs.

        Args:
            tasks: List of task dictionaries.

        Returns:
            List of tasks ordered such that all dependencies appear before
            the tasks that depend on them.

        Raises:
            CycleError: If a dependency cycle is detected.
            ValueError: If a task depends on an unknown task ID.
        """
        if not tasks:
            return []

        # Maps task_id -> list of task_ids that depend on it
        graph: dict[str, list[str]] = {t["id"]: [] for t in tasks}
        # Maps task_id -> count of unsatisfied dependencies
        in_degree: dict[str, int] = {t["id"]: 0 for t in tasks}
        # Maps task_id -> original task dict
        task_map: dict[str, dict] = {t["id"]: t for t in tasks}

        for task in tasks:
            task_id = task["id"]
            deps = task.get("depends_on", [])
            for dep_id in deps:
                if dep_id not in graph:
                    raise ValueError(f"Task '{task_id}' depends on unknown task '{dep_id}'")
                graph[dep_id].append(task_id)
                in_degree[task_id] += 1

        # Queue of tasks with no pending dependencies
        queue: deque[str] = deque(tid for tid, deg in in_degree.items() if deg == 0)
        ordered: list[dict] = []

        while queue:
            current_id = queue.popleft()
            ordered.append(task_map[current_id])

            # Satisfy the dependency for all downstream tasks
            for dependent_id in graph[current_id]:
                in_degree[dependent_id] -= 1
                if in_degree[dependent_id] == 0:
                    queue.append(dependent_id)

        if len(ordered) != len(tasks):
            # Graph has a cycle if we couldn't process all nodes
            raise CycleError("Dependency cycle detected in tasks")

        return ordered
