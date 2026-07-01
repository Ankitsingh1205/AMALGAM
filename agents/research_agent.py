from __future__ import annotations

from typing import Any, Optional

from agents.base_agent import BaseAgent
from brain.shared_context import SharedContext
from services.memory import MemoryService
from services.logger import get_logger


class ResearchAgent(BaseAgent):
    """Agent that gathers contextual information before execution.

    The research agent inspects the task and plan, then uses available
    tools and services (memory, project, files) to collect supporting
    data. Findings are written back to the shared context.
    """

    def __init__(
        self,
        shared_context: Optional[SharedContext] = None,
        messaging: Optional[Any] = None,
        memory_service: Optional[MemoryService] = None,
    ) -> None:
        super().__init__("researcher", shared_context, messaging)
        self._memory = memory_service or MemoryService()

    def run(self, shared_context: SharedContext) -> dict:
        """Gather research for the current task and plan.

        Returns:
            Dictionary with ``success``, ``findings``, and ``summary``.
        """
        self._status = "running"
        self._record("research_start")

        task = shared_context.get("task", "")
        plan = shared_context.get("plan", "")
        findings: dict[str, Any] = {}

        text = task.lower()

        # Memory research
        if any(word in text for word in ["remember", "recall", "store", "retrieve", "memory"]):
            findings["memory"] = self._research_memory(task)

        # File research
        if any(word in text for word in ["read", "file", "open", "content", "list", "directory", "ls"]):
            findings["files"] = self._research_files(task)

        # Project research
        if any(word in text for word in ["project", "repository", "summarize", "overview", "architecture"]):
            findings["project"] = self._research_project()

        # Web research
        if any(word in text for word in ["search", "web", "find online", "google"]):
            findings["web"] = self._research_web(task)

        summary = {
            "task": task,
            "plan": plan,
            "findings_count": len(findings),
            "findings": findings,
        }

        shared_context.set("research", findings)
        shared_context.set("research_summary", summary)

        self._record("research_complete", summary)
        self._status = "completed"

        return {"success": True, "findings": findings, "summary": summary}

    def _research_memory(self, task: str) -> dict:
        """Recall relevant memory entries."""
        try:
            all_memories = self._memory.show_all()
            # Simple heuristic: find keys mentioned in the task
            relevant = {
                k: v for k, v in all_memories.items()
                if k.lower() in task.lower()
            }
            return {
                "relevant_entries": relevant,
                "total_entries": len(all_memories),
            }
        except Exception as e:
            return {"error": str(e)}

    def _research_files(self, task: str) -> dict:
        """Gather file system context."""
        from tools.file_tool import FileTool
        try:
            ft = FileTool()
            files = ft.list_files(".")
            return {
                "current_directory": ".",
                "file_count": len(files) if isinstance(files, list) else 0,
            }
        except Exception as e:
            return {"error": str(e)}

    def _research_project(self) -> dict:
        """Gather project-level context."""
        try:
            from services.project_service import ProjectService
            ps = ProjectService()
            if hasattr(ps, "summarize"):
                return ps.summarize()
            return {"status": "ProjectService unavailable"}
        except Exception as e:
            return {"error": str(e)}

    def _research_web(self, task: str) -> dict:
        """Gather web search context."""
        return {"status": "web research requires internet tool", "query": task}
