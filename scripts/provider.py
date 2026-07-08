#!/usr/bin/env python3
"""
AMALGAM Provider Engine

Automatically manage AI providers for the AMALGAM operating system.

Responsibilities:
    - Provider registration (configurable, no hardcoding).
    - Provider health monitoring.
    - Priority-based provider selection.
    - Automatic failover on provider failure.
    - Rate-limit detection.
    - Timeout detection.
    - Retry delegation to the Recovery Engine (never duplicates recovery).
    - Session continuity via STATE.json persistence.

Design contract:
    ProviderManager decides WHERE execution continues (which provider).
    Recovery Engine decides HOW execution resumes (backoff, state restore).

Dependencies: Python standard library only.
Never imports agents/, brain/, kernel/, or services/.
"""

from __future__ import annotations

import sys
import time
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Callable

_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from scripts.context import (  # noqa: E402
    load_json,
    now_iso,
    save_json,
    new_uuid,
)
from scripts.recovery import (  # noqa: E402
    FailureClass,
    classify as recovery_classify,
    recover as recovery_recover,
    RecoveryRecord,
    report as recovery_report,
    log_recovery,
)


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

PROVIDER_VERSION = "1.0"

# Default provider configuration.  Callers may override via register() or
# by supplying a full provider list.  This list is intentionally empty to
# enforce the "no hardcoded providers" rule.
DEFAULT_PROVIDERS: list[dict[str, Any]] = []

# Health-check thresholds.
DEFAULT_HEALTH_WINDOW = 60.0  # seconds to consider for rolling health
DEFAULT_ERROR_THRESHOLD = 5   # errors within window to mark degraded
DEFAULT_TIMEOUT_MS = 30_000   # default call timeout in milliseconds


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------


class ProviderStatus(Enum):
    """Lifecycle status of a registered provider."""

    HEALTHY = "HEALTHY"
    DEGRADED = "DEGRADED"
    UNAVAILABLE = "UNAVAILABLE"
    DISABLED = "DISABLED"

    def is_selectable(self) -> bool:
        """Return True if the provider can accept requests."""
        return self in (ProviderStatus.HEALTHY, ProviderStatus.DEGRADED)


# ---------------------------------------------------------------------------
# Errors
# ---------------------------------------------------------------------------


class ProviderError(Exception):
    """Raised when a provider operation fails."""

    pass


# ---------------------------------------------------------------------------
# Provider record
# ---------------------------------------------------------------------------


@dataclass
class ProviderRecord:
    """Runtime state for a single registered provider.

    Attributes:
        provider_id: Unique identifier (UUID4 or user-supplied slug).
        name: Human-readable provider name.
        priority: Lower number = higher priority (0 is highest).
        status: Current operational status.
        endpoint: Optional API endpoint URL.
        model: Optional default model identifier.
        config: Arbitrary provider-specific configuration.
        total_requests: Lifetime request count.
        total_errors: Lifetime error count.
        total_timeouts: Lifetime timeout count.
        total_rate_limits: Lifetime rate-limit hit count.
        last_error: Description of most recent error.
        last_error_at: ISO timestamp of most recent error.
        last_success_at: ISO timestamp of most recent success.
        registered_at: ISO timestamp when the provider was registered.
        cooldown_until: ISO timestamp until which the provider is in cooldown.
    """

    provider_id: str
    name: str
    priority: int = 0
    status: ProviderStatus = ProviderStatus.HEALTHY
    endpoint: str = ""
    model: str = ""
    config: dict[str, Any] = field(default_factory=dict)
    total_requests: int = 0
    total_errors: int = 0
    total_timeouts: int = 0
    total_rate_limits: int = 0
    last_error: str = ""
    last_error_at: str = ""
    last_success_at: str = ""
    registered_at: str = ""
    cooldown_until: str = ""


# ---------------------------------------------------------------------------
# Serialisation helpers
# ---------------------------------------------------------------------------


def _record_to_dict(rec: ProviderRecord) -> dict[str, Any]:
    """Serialise a ProviderRecord to a JSON-safe dict."""
    return {
        "provider_id": rec.provider_id,
        "name": rec.name,
        "priority": rec.priority,
        "status": rec.status.value,
        "endpoint": rec.endpoint,
        "model": rec.model,
        "config": rec.config,
        "total_requests": rec.total_requests,
        "total_errors": rec.total_errors,
        "total_timeouts": rec.total_timeouts,
        "total_rate_limits": rec.total_rate_limits,
        "last_error": rec.last_error,
        "last_error_at": rec.last_error_at,
        "last_success_at": rec.last_success_at,
        "registered_at": rec.registered_at,
        "cooldown_until": rec.cooldown_until,
    }


def _dict_to_record(data: dict[str, Any]) -> ProviderRecord:
    """Deserialise a dict into a ProviderRecord."""
    status_str = data.get("status", "HEALTHY")
    try:
        status = ProviderStatus(status_str)
    except ValueError:
        status = ProviderStatus.HEALTHY

    return ProviderRecord(
        provider_id=data.get("provider_id", new_uuid()),
        name=data.get("name", "unknown"),
        priority=data.get("priority", 0),
        status=status,
        endpoint=data.get("endpoint", ""),
        model=data.get("model", ""),
        config=data.get("config", {}),
        total_requests=data.get("total_requests", 0),
        total_errors=data.get("total_errors", 0),
        total_timeouts=data.get("total_timeouts", 0),
        total_rate_limits=data.get("total_rate_limits", 0),
        last_error=data.get("last_error", ""),
        last_error_at=data.get("last_error_at", ""),
        last_success_at=data.get("last_success_at", ""),
        registered_at=data.get("registered_at", ""),
        cooldown_until=data.get("cooldown_until", ""),
    )


# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------


def log(message: str) -> None:
    """Print a structured log line with a PROVIDER prefix."""
    print(f"[PROVIDER] {message}")


# ---------------------------------------------------------------------------
# ProviderManager
# ---------------------------------------------------------------------------


class ProviderManager:
    """Manages AI provider lifecycle, selection, and failover.

    The manager maintains an ordered roster of providers, tracks health
    metrics, selects the best available provider, and coordinates failover
    when a provider becomes unavailable.

    Recovery logic (backoff, state restoration, retry) is delegated to the
    Recovery Engine.  ProviderManager only decides WHERE execution continues.

    Args:
        providers: Optional list of provider dicts to pre-register.
    """

    def __init__(self, providers: list[dict[str, Any]] | None = None) -> None:
        self._providers: dict[str, ProviderRecord] = {}
        self._selection_order: list[str] = []  # provider_ids sorted by priority

        if providers:
            for pdata in providers:
                self.register(pdata)

    # -- Registration -------------------------------------------------------

    def register(self, provider_data: dict[str, Any]) -> ProviderRecord:
        """Register a new provider or update an existing one.

        Args:
            provider_data: Dict with at least ``name``.  Optional keys:
                ``provider_id``, ``priority``, ``endpoint``, ``model``,
                ``config``, ``status``.

        Returns:
            The registered ProviderRecord.

        Raises:
            ProviderError: If ``name`` is missing.
        """
        name = provider_data.get("name")
        if not name:
            raise ProviderError("Provider registration requires a 'name'.")

        pid = provider_data.get("provider_id", new_uuid())
        provider_data["provider_id"] = pid
        if "registered_at" not in provider_data or not provider_data["registered_at"]:
            provider_data["registered_at"] = now_iso()

        record = _dict_to_record(provider_data)
        self._providers[pid] = record
        self._rebuild_selection_order()

        log(f"Registered provider '{record.name}' (id={pid}, "
            f"priority={record.priority}).")
        return record

    def unregister(self, provider_id: str) -> bool:
        """Remove a provider from the roster.

        Args:
            provider_id: The unique provider identifier.

        Returns:
            True if removed, False if not found.
        """
        if provider_id in self._providers:
            name = self._providers[provider_id].name
            del self._providers[provider_id]
            self._rebuild_selection_order()
            log(f"Unregistered provider '{name}' (id={provider_id}).")
            return True
        return False

    # -- Lookup -------------------------------------------------------------

    def get(self, provider_id: str) -> ProviderRecord | None:
        """Return a provider by ID, or None."""
        return self._providers.get(provider_id)

    def get_by_name(self, name: str) -> ProviderRecord | None:
        """Return the first provider matching the given name."""
        for rec in self._providers.values():
            if rec.name == name:
                return rec
        return None

    def all_providers(self) -> list[ProviderRecord]:
        """Return all registered providers sorted by priority."""
        return [self._providers[pid] for pid in self._selection_order]

    # -- Selection ----------------------------------------------------------

    def select(self) -> ProviderRecord | None:
        """Select the highest-priority healthy provider.

        Skips providers that are UNAVAILABLE, DISABLED, or in cooldown.

        Returns:
            The best available ProviderRecord, or None if none available.
        """
        now = now_iso()
        for pid in self._selection_order:
            rec = self._providers[pid]
            if not rec.status.is_selectable():
                continue
            if rec.cooldown_until and rec.cooldown_until > now:
                continue
            return rec
        return None

    def select_excluding(self, exclude_ids: set[str]) -> ProviderRecord | None:
        """Select the best provider, excluding the given IDs.

        Used for failover: the caller excludes the provider that just failed.

        Args:
            exclude_ids: Set of provider_ids to skip.

        Returns:
            The best available ProviderRecord not in exclude_ids, or None.
        """
        now = now_iso()
        for pid in self._selection_order:
            if pid in exclude_ids:
                continue
            rec = self._providers[pid]
            if not rec.status.is_selectable():
                continue
            if rec.cooldown_until and rec.cooldown_until > now:
                continue
            return rec
        return None

    # -- Health tracking ----------------------------------------------------

    def record_success(self, provider_id: str) -> None:
        """Record a successful request for the given provider.

        Args:
            provider_id: The provider that succeeded.
        """
        rec = self._providers.get(provider_id)
        if rec is None:
            return
        rec.total_requests += 1
        rec.last_success_at = now_iso()
        # Recover from DEGRADED if a request succeeds.
        if rec.status == ProviderStatus.DEGRADED:
            rec.status = ProviderStatus.HEALTHY
            log(f"Provider '{rec.name}' recovered to HEALTHY.")

    def record_error(
        self,
        provider_id: str,
        error: Any,
        context: dict[str, Any] | None = None,
    ) -> FailureClass:
        """Record a failed request and classify the error.

        Delegates classification to the Recovery Engine's ``classify()``
        to avoid duplicating classification logic.

        Args:
            provider_id: The provider that failed.
            error: The error object or string.
            context: Optional context dict for classification.

        Returns:
            The classified FailureClass.
        """
        rec = self._providers.get(provider_id)
        if rec is None:
            return recovery_classify(error, context)

        fc = recovery_classify(error, context)
        rec.total_requests += 1
        rec.total_errors += 1
        rec.last_error = str(error)
        rec.last_error_at = now_iso()

        if fc == FailureClass.RATE_LIMIT:
            rec.total_rate_limits += 1
            log(f"Provider '{rec.name}' hit rate limit "
                f"(total={rec.total_rate_limits}).")
        elif fc == FailureClass.TIMEOUT:
            rec.total_timeouts += 1
            log(f"Provider '{rec.name}' timed out "
                f"(total={rec.total_timeouts}).")

        # Determine if the provider should be degraded or marked unavailable.
        if rec.total_errors >= DEFAULT_ERROR_THRESHOLD:
            if rec.status == ProviderStatus.HEALTHY:
                rec.status = ProviderStatus.DEGRADED
                log(f"Provider '{rec.name}' degraded "
                    f"(errors={rec.total_errors}).")
            elif rec.status == ProviderStatus.DEGRADED:
                rec.status = ProviderStatus.UNAVAILABLE
                log(f"Provider '{rec.name}' marked UNAVAILABLE "
                    f"(errors={rec.total_errors}).")

        return fc

    # -- Failover -----------------------------------------------------------

    def failover(
        self,
        failed_provider_id: str,
        error: Any,
        context: dict[str, Any] | None = None,
        stage_number: int = 0,
    ) -> tuple[ProviderRecord | None, RecoveryRecord | None]:
        """Execute provider failover after a failure.

        1. Records the error on the failed provider.
        2. Delegates recovery to the Recovery Engine.
        3. If recovery fails, selects the next available provider.

        ProviderManager decides WHERE execution continues.
        Recovery Engine decides HOW execution resumes.

        Args:
            failed_provider_id: The provider that experienced the failure.
            error: The error object or string.
            context: Optional context dict for classification/recovery.
            stage_number: Loop stage number for recovery context.

        Returns:
            Tuple of (next_provider, recovery_record).
            next_provider is None if no providers remain.
            recovery_record is None if no recovery was attempted.
        """
        ctx = context or {}
        fc = self.record_error(failed_provider_id, error, ctx)

        recovery_record: RecoveryRecord | None = None
        if fc.is_retryable() and stage_number > 0:
            recovery_record = recovery_recover(stage_number, error, ctx)
            if recovery_record.resolved:
                # Recovery succeeded on the same provider.
                rec = self._providers.get(failed_provider_id)
                if rec and rec.status.is_selectable():
                    log(f"Recovery succeeded on '{rec.name}'. "
                        f"Continuing with same provider.")
                    return rec, recovery_record

        # Select next available provider, excluding the failed one.
        next_provider = self.select_excluding({failed_provider_id})
        if next_provider:
            log(f"Failover: '{self._providers[failed_provider_id].name}' -> "
                f"'{next_provider.name}'.")
        else:
            log("Failover: No alternative providers available.")

        return next_provider, recovery_record

    # -- Priority management ------------------------------------------------

    def set_priority(self, provider_id: str, priority: int) -> bool:
        """Update a provider's priority.

        Args:
            provider_id: The provider to update.
            priority: New priority value (lower = higher priority).

        Returns:
            True if updated, False if provider not found.
        """
        rec = self._providers.get(provider_id)
        if rec is None:
            return False
        rec.priority = priority
        self._rebuild_selection_order()
        log(f"Provider '{rec.name}' priority set to {priority}.")
        return True

    def set_status(self, provider_id: str, status: ProviderStatus) -> bool:
        """Manually set a provider's status.

        Args:
            provider_id: The provider to update.
            status: The new ProviderStatus.

        Returns:
            True if updated, False if provider not found.
        """
        rec = self._providers.get(provider_id)
        if rec is None:
            return False
        old = rec.status
        rec.status = status
        log(f"Provider '{rec.name}' status: {old.value} -> {status.value}.")
        return True

    # -- Cooldown -----------------------------------------------------------

    def set_cooldown(self, provider_id: str, until: str) -> bool:
        """Place a provider in cooldown until the given ISO timestamp.

        During cooldown, the provider is skipped by ``select()``.

        Args:
            provider_id: The provider to cool down.
            until: ISO 8601 timestamp when the cooldown expires.

        Returns:
            True if set, False if provider not found.
        """
        rec = self._providers.get(provider_id)
        if rec is None:
            return False
        rec.cooldown_until = until
        log(f"Provider '{rec.name}' cooldown until {until}.")
        return True

    def clear_cooldown(self, provider_id: str) -> bool:
        """Remove cooldown from a provider.

        Args:
            provider_id: The provider to clear.

        Returns:
            True if cleared, False if provider not found.
        """
        rec = self._providers.get(provider_id)
        if rec is None:
            return False
        rec.cooldown_until = ""
        log(f"Provider '{rec.name}' cooldown cleared.")
        return True

    # -- Reset --------------------------------------------------------------

    def reset_errors(self, provider_id: str) -> bool:
        """Reset error counters and restore a provider to HEALTHY.

        Args:
            provider_id: The provider to reset.

        Returns:
            True if reset, False if provider not found.
        """
        rec = self._providers.get(provider_id)
        if rec is None:
            return False
        rec.total_errors = 0
        rec.total_timeouts = 0
        rec.total_rate_limits = 0
        rec.last_error = ""
        rec.last_error_at = ""
        rec.cooldown_until = ""
        rec.status = ProviderStatus.HEALTHY
        log(f"Provider '{rec.name}' errors reset. Status: HEALTHY.")
        return True

    # -- Persistence --------------------------------------------------------

    def save_state(self) -> None:
        """Persist provider roster to STATE.json under the 'providers' key."""
        state = load_json("STATE.json")
        if not isinstance(state, dict):
            state = {}

        providers_data: list[dict[str, Any]] = []
        for pid in self._selection_order:
            rec = self._providers[pid]
            providers_data.append(_record_to_dict(rec))

        state["providers"] = {
            "version": PROVIDER_VERSION,
            "updated_at": now_iso(),
            "roster": providers_data,
            "active_provider": None,
        }

        # Set active provider to the currently selected best.
        selected = self.select()
        if selected:
            state["providers"]["active_provider"] = selected.provider_id
            # Also update the top-level provider key for context.py compat.
            state["provider"] = {
                "name": selected.name,
                "model": selected.model,
            }

        state["last_updated"] = now_iso()
        save_json("STATE.json", state)
        log(f"Provider state saved ({len(providers_data)} providers).")

    def load_state(self) -> int:
        """Load provider roster from STATE.json.

        Returns:
            Number of providers loaded.
        """
        state = load_json("STATE.json")
        if not isinstance(state, dict):
            return 0

        providers_block = state.get("providers")
        if not isinstance(providers_block, dict):
            return 0

        roster = providers_block.get("roster", [])
        if not isinstance(roster, list):
            return 0

        self._providers.clear()
        self._selection_order.clear()

        for pdata in roster:
            if isinstance(pdata, dict) and pdata.get("name"):
                record = _dict_to_record(pdata)
                self._providers[record.provider_id] = record

        self._rebuild_selection_order()
        log(f"Provider state loaded ({len(self._providers)} providers).")
        return len(self._providers)

    # -- Report -------------------------------------------------------------

    def report(self) -> dict[str, Any]:
        """Produce a structured provider status report.

        Returns:
            Dict with provider roster, health summary, and active provider.
        """
        providers = []
        for pid in self._selection_order:
            rec = self._providers[pid]
            providers.append(_record_to_dict(rec))

        selected = self.select()
        healthy = sum(
            1 for r in self._providers.values()
            if r.status == ProviderStatus.HEALTHY
        )
        degraded = sum(
            1 for r in self._providers.values()
            if r.status == ProviderStatus.DEGRADED
        )
        unavailable = sum(
            1 for r in self._providers.values()
            if r.status == ProviderStatus.UNAVAILABLE
        )

        return {
            "version": PROVIDER_VERSION,
            "total_providers": len(self._providers),
            "healthy": healthy,
            "degraded": degraded,
            "unavailable": unavailable,
            "active_provider": selected.name if selected else None,
            "active_provider_id": selected.provider_id if selected else None,
            "roster": providers,
        }

    # -- Internal -----------------------------------------------------------

    def _rebuild_selection_order(self) -> None:
        """Rebuild the priority-sorted selection order."""
        self._selection_order = sorted(
            self._providers.keys(),
            key=lambda pid: self._providers[pid].priority,
        )


# ---------------------------------------------------------------------------
# Module-level convenience functions
# ---------------------------------------------------------------------------


def create_manager(
    providers: list[dict[str, Any]] | None = None,
) -> ProviderManager:
    """Create a ProviderManager, optionally with initial providers.

    Args:
        providers: Optional list of provider config dicts.

    Returns:
        A configured ProviderManager instance.
    """
    return ProviderManager(providers)


def resume_manager() -> ProviderManager:
    """Create a ProviderManager and load state from STATE.json.

    Supports session continuity: interrupted sessions are restored
    automatically from persisted provider state.

    Returns:
        A ProviderManager with providers loaded from STATE.json.
    """
    mgr = ProviderManager()
    loaded = mgr.load_state()
    if loaded == 0:
        log("No persisted provider state found. Starting fresh.")
    else:
        log(f"Resumed {loaded} providers from STATE.json.")
    return mgr


# ---------------------------------------------------------------------------
# CLI dispatch
# ---------------------------------------------------------------------------


COMMAND_MAP: dict[str, str] = {
    "status": "cmd_status",
    "register": "cmd_register",
    "select": "cmd_select",
    "failover": "cmd_failover",
    "reset": "cmd_reset",
}


def cmd_status() -> None:
    """Print current provider status from STATE.json."""
    mgr = resume_manager()
    rpt = mgr.report()

    print()
    print("AMALGAM PROVIDER STATUS")
    print("-" * 50)
    print(f"Version          : {rpt['version']}")
    print(f"Total Providers  : {rpt['total_providers']}")
    print(f"Healthy          : {rpt['healthy']}")
    print(f"Degraded         : {rpt['degraded']}")
    print(f"Unavailable      : {rpt['unavailable']}")
    print(f"Active Provider  : {rpt['active_provider'] or '—'}")
    print("-" * 50)

    for p in rpt["roster"]:
        print(f"  [{p['priority']}] {p['name']} ({p['status']})")
        print(f"      ID        : {p['provider_id']}")
        print(f"      Model     : {p['model'] or '—'}")
        print(f"      Requests  : {p['total_requests']}")
        print(f"      Errors    : {p['total_errors']}")
        print(f"      Timeouts  : {p['total_timeouts']}")
        print(f"      Rate Limits: {p['total_rate_limits']}")
        if p["last_error"]:
            print(f"      Last Error: {p['last_error'][:60]}")
        print()

    print()


def cmd_register() -> None:
    """Register a provider from CLI arguments."""
    if len(sys.argv) < 3:
        print("ERROR: Usage: py scripts/provider.py register <name> [priority] [model]")
        sys.exit(1)

    name = sys.argv[2]
    priority = int(sys.argv[3]) if len(sys.argv) > 3 else 0
    model = sys.argv[4] if len(sys.argv) > 4 else ""

    mgr = resume_manager()
    mgr.register({"name": name, "priority": priority, "model": model})
    mgr.save_state()
    print(f"Provider '{name}' registered (priority={priority}, model={model}).")


def cmd_select() -> None:
    """Select and display the best available provider."""
    mgr = resume_manager()
    selected = mgr.select()
    if selected:
        print(f"Selected provider: {selected.name} "
              f"(id={selected.provider_id}, priority={selected.priority})")
    else:
        print("No providers available.")


def cmd_failover() -> None:
    """Simulate a failover from the currently active provider."""
    if len(sys.argv) < 3:
        print("ERROR: Usage: py scripts/provider.py failover <error_message>")
        sys.exit(1)

    error_msg = " ".join(sys.argv[2:])
    mgr = resume_manager()

    current = mgr.select()
    if not current:
        print("No active provider to fail over from.")
        sys.exit(1)

    next_prov, rec = mgr.failover(current.provider_id, error_msg)
    mgr.save_state()

    if next_prov:
        print(f"Failover: {current.name} -> {next_prov.name}")
    else:
        print(f"Failover: {current.name} -> No alternative available.")
    if rec:
        print(f"Recovery: resolved={rec.resolved}, "
              f"resolution={rec.resolution}")


def cmd_reset() -> None:
    """Reset error counters for a provider."""
    if len(sys.argv) < 3:
        print("ERROR: Usage: py scripts/provider.py reset <provider_name>")
        sys.exit(1)

    name = sys.argv[2]
    mgr = resume_manager()
    rec = mgr.get_by_name(name)
    if not rec:
        print(f"Provider '{name}' not found.")
        sys.exit(1)

    mgr.reset_errors(rec.provider_id)
    mgr.save_state()
    print(f"Provider '{name}' errors reset.")


def print_help() -> None:
    """Print the available commands."""
    print("AMALGAM Provider Engine")
    print()
    print("Commands:")
    for cmd in COMMAND_MAP:
        print(f"  py scripts/provider.py {cmd} [args]")
    print()
    print("  status                       : Print provider roster and health.")
    print("  register <name> [pri] [model]: Register a new provider.")
    print("  select                       : Show best available provider.")
    print("  failover <error>             : Simulate failover from active.")
    print("  reset <name>                 : Reset error counters.")
    print()


def main() -> None:
    """Parse CLI arguments and dispatch to the requested command."""
    if len(sys.argv) < 2:
        print("Usage: py scripts/provider.py <command> [args]")
        print()
        print_help()
        sys.exit(0)

    cmd = sys.argv[1].lower()
    if cmd in ("help", "--help", "-h"):
        print_help()
        sys.exit(0)

    func_name = COMMAND_MAP.get(cmd)
    if func_name is None:
        print(f"ERROR: Unknown command '{cmd}'.")
        print_help()
        sys.exit(1)

    func = globals().get(func_name)
    if func is None:
        print(f"ERROR: Internal dispatch failure for '{cmd}' -> '{func_name}'.")
        sys.exit(1)

    try:
        func()
    except ProviderError as exc:
        print(f"ERROR: {exc}")
        sys.exit(1)
    except Exception as exc:
        print(f"ERROR: Command '{cmd}' failed: {exc}")
        sys.exit(1)


if __name__ == "__main__":
    main()
