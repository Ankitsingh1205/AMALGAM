# AMALGAM OS Development Notes

## Mission 2 Guardrails

Mission 2 is infrastructure-only.

Do not change the canonical runtime flow:

User -> Brain -> Planner -> Task -> Executor -> Dispatcher -> Tool / Service

Do not introduce plugins, dependency injection, routing redesigns, state
machines, or multi-agent execution in this phase.

## Configuration

Use `config/settings.py` for runtime configuration values.

Use `config/constants.py` for immutable names such as actions, intents, tools,
services, and kernel statuses.

Avoid adding hardcoded infrastructure values directly to runtime modules.

## Logging

Use `services.logger.get_logger()` for reusable infrastructure logs.

Keep direct `print()` calls only where output is intentionally user-facing, such
as CLI prompts, assistant responses, and boot display text.

## Diagnostics

Use `DiagnosticsService.run_checks()` to collect structured health data for
future GUI or diagnostics views.

## Workspace Engine

Use `Workspace(path).report()` when another component needs read-only project
context.

Workspace code must not execute project actions, modify files, change Git
history, or alter routing. It should inspect files and return structured data
only.
