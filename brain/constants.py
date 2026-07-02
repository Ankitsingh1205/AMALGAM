"""Centralized constants for keyword sets used across the brain module.

This module contains frozensets of keywords used for intent detection,
capability routing, and plan generation. Centralizing these constants
avoids duplication and ensures consistency.

Note: These constants are intentionally duplicated from their original
locations to avoid changing behavior during the hotfix. In a future
refactor, consider replacing them with enums or configuration.
"""

from __future__ import annotations

# IntentAnalyzer keyword sets
INTENT_FILES_KW = frozenset([
    "list files", "show files", "directory", "folders", "ls",
])

INTENT_INTERNET_KW = frozenset([
    "search ", "search web", "google", "find online",
])

INTENT_PYTHON_KW = frozenset([
    "run python", "execute python", "python:",
])

INTENT_CODING_KW = frozenset([
    "write code", "generate code", "write python", "python code",
    "create function", "create a function", "debug", "fix code",
    "implement", "program", "script", "algorithm",
])

INTENT_PROJECT_KW = frozenset([
    "explain my project", "summarize my project", "summarize this repository",
    "project overview", "project architecture", "show project architecture",
    "explain this repository",
])

# CapabilityRouter keyword sets (note: some overlap with above)
_MEMORY_ACTIONS = frozenset(["remember", "recall"])
_DIAG_KW = frozenset(["doctor", "diagnostic", "diagnostics", "health", "status"])
_WORKSPACE_KW = frozenset(["workspace", "project", "tree", "folder", "directory", "structure"])
_KNOWLEDGE_KW = frozenset([
    "architecture", "import", "imports", "class", "classes",
    "function", "functions", "service", "services", "relationship",
])

# AutonomousExecutor heuristic planning keywords
_PLAN_KW_MATH = frozenset(["calculate", "math", "compute", "sum"])
_PLAN_KW_FILE_R = frozenset(["read", "file", "open", "content"])
_PLAN_KW_FILE_W = frozenset(["write", "save", "create file"])
_PLAN_KW_LIST = frozenset(["list", "show files", "directory", "ls"])
_PLAN_KW_PYTHON = frozenset(["python", "run code", "execute script"])
_PLAN_KW_SEARCH = frozenset(["search", "web", "find online"])
_PLAN_KW_REMEMBER = frozenset(["remember", "store", "save data"])
_PLAN_KW_RECALL = frozenset(["recall", "retrieve", "fetch memory"])
_PLAN_KW_PROJECT = frozenset(["project", "repository", "summarize", "overview"])

_TASK_KW_FILES = frozenset(["list files", "show files", "directory", "folders", "ls"])
_TASK_KW_SEARCH = frozenset(["search ", "search web", "google", "find online"])
_TASK_KW_PYTHON = frozenset(["run python", "execute python", "python:"])
_TASK_KW_PROJECT = frozenset([
    "explain my project", "summarize my project", "summarize this repository",
    "project overview", "project architecture", "show project architecture",
    "explain this repository",
])
_TASK_KW_CODE = frozenset([
    "write code", "generate code", "write python", "python code",
    "create function", "create a function", "debug", "fix code",
    "implement", "program", "script", "algorithm",
])