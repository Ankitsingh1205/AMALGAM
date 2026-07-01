from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from brain.fleet_manager import FleetManager

# Module-level frozensets for O(1) membership testing — avoids rebuilding
# list literals on every call to ``route()``.
_MEMORY_ACTIONS = frozenset(["remember", "recall"])
_DIAG_KW = frozenset(["doctor", "diagnostic", "diagnostics", "health", "status"])
_WORKSPACE_KW = frozenset(["workspace", "project", "tree", "folder", "directory", "structure"])
_KNOWLEDGE_KW = frozenset([
    "architecture", "import", "imports", "class", "classes",
    "function", "functions", "service", "services", "relationship",
])


class CapabilityRouter:
    """Decides which capability (or specific agent) should handle a task.

    Optimizations (Mission 6.5.2):
    - All keyword lists promoted to module-level frozensets (O(1) ``in``).
    - Memory action check uses frozenset instead of a list literal.
    
    Optimizations (Mission 6.6.2):
    - Dynamic load-aware routing (Least-Connections).
    - Fast dictionary iteration for O(N) dynamic routing where N is fleet size.
    """

    __slots__ = ()

    def route(self, task: dict, fleet_manager: FleetManager | None = None) -> str:
        """Route a task to a capability or specific agent.
        
        If a ``FleetManager`` is provided, this performs dynamic load-aware 
        routing and returns the name of the most appropriate agent.
        Otherwise, it returns the generic capability string.
        """
        capability = self._determine_capability(task)

        if fleet_manager:
            return self._dynamic_route(capability, fleet_manager)

        return capability

    def _determine_capability(self, task: dict) -> str:
        """Static capability matching based on task attributes."""
        # Handle dicts or objects depending on caller
        action = task.get("action", "") if isinstance(task, dict) else getattr(task, "action", "")
        data = str(task.get("data", "") if isinstance(task, dict) else getattr(task, "data", ""))

        action = (action or "").lower()
        data = data.lower()

        if action in _MEMORY_ACTIONS:
            return "memory"

        if any(word in data for word in _DIAG_KW):
            return "diagnostics"

        if any(word in data for word in _WORKSPACE_KW):
            return "workspace"

        if any(word in data for word in _KNOWLEDGE_KW):
            return "knowledge"

        if action == "calculate":
            return "calculator"

        if action == "run_python":
            return "python"

        if action == "list_files":
            return "files"

        return "llm"

    def _dynamic_route(self, capability: str, fleet_manager: FleetManager) -> str:
        """Find the least loaded agent matching the capability."""
        fleet_state = fleet_manager.get_fleet_state()
        
        best_agent = None
        lowest_load = float("inf")
        lowest_failures = float("inf")
        
        for agent_name, state in fleet_state.items():
            if capability in state.get("capabilities", set()):
                # Rank by load, tie-break by consecutive failures
                load = state.get("load", 0)
                failures = state.get("consecutive_failures", 0)
                
                if load < lowest_load or (load == lowest_load and failures < lowest_failures):
                    best_agent = agent_name
                    lowest_load = load
                    lowest_failures = failures
                    
        return best_agent or capability
