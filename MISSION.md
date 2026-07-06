# MISSION

## Mission Number

Mission 7

## Mission Name

Mission Engine

## Objective

Build a complete Mission Engine subsystem: Mission Core dataclasses (Mission, MissionID, MissionStatus, MissionPriority), Epic grouping, Mission Graph with DAG operations, Planner integration, persistence layer, Event Bus with publish/subscribe and lifecycle notifications, and full regression suite. Extend with ChiefAgent orchestration, FleetManager agent lifecycle, WorkPool capability-based distribution, DependencyResolver task DAG scheduling, CapabilityRouter load-aware routing, KnowledgeRouter topic-based filtering, and end-to-end integration testing.

## Current Status

In Progress (~75%)

## Acceptance Criteria

- Mission Core (Mission, MissionID, MissionStatus, MissionPriority): implemented and tested
- Epic: implemented and tested
- Mission Graph: DAG with topological sort (Kahn's), cycle detection, add/remove nodes and edges, validation
- Planner Integration: Planner reads Mission context and generates tasks aligned with mission objectives
- Persistence: serialization/deserialization (to_dict/from_dict) for Mission, Epic, MissionGraph
- Event Bus: event publication, subscription, mission lifecycle notifications (MISSION_STATUS_CHANGED, MISSION_COMPLETED, MISSION_FAILED, MISSION_CANCELLED)
- ChiefAgent: adaptive mission orchestration
- FleetManager: agent lifecycle management
- WorkPool: capability-based task distribution
- DependencyResolver: task DAG scheduler
- CapabilityRouter: load-aware routing
- KnowledgeRouter: topic-based context filtering
- Integration: end-to-end tests across all Mission 7 components
- All tests pass with no regressions
- No breaking changes to existing public APIs
- Layer boundaries and import DAG preserved

## Files Modified

- `brain/mission/mission.py` — Mission dataclass with lifecycle transitions and Event Bus integration
- `brain/mission/mission_status.py` — MissionStatus enum with state machine transitions
- `brain/mission/mission_priority.py` — MissionPriority enum (LOW/NORMAL/HIGH/CRITICAL)
- `brain/mission/mission_id.py` — MissionID immutable UUID4 identifier
- `brain/mission/epic.py` — Epic grouping and metadata container
- `brain/mission/graph.py` — Mission Graph DAG with Kahn's topological sort, cycle detection
- `brain/mission/event.py` — MissionEvent dataclass
- `brain/mission/event_types.py` — MissionEventType enum
- `brain/mission/event_bus.py` — EventBus publish/subscribe with lifecycle hooks
- `brain/planner/` — Mission-aware plan generation integration
- `tests/test_{mission,mission_status,mission_priority,mission_id,epic,graph,event,event_bus}.py` — Mission Engine test files

## Tests Added

- `tests/test_mission.py` — Mission lifecycle transitions, state machine validation, serialization
- `tests/test_mission_status.py` — Status enum, terminal state detection, valid transitions
- `tests/test_mission_priority.py` — Priority enum ordering
- `tests/test_mission_id.py` — UUID4 generation, validation, equality, hashing
- `tests/test_epic.py` — Epic creation, metadata, serialization
- `tests/test_graph.py` — DAG operations: topological sort, cycle detection, add/remove nodes/edges
- `tests/test_event.py` — MissionEvent creation, payload validation
- `tests/test_event_bus.py` — EventBus publish, subscribe, unsubscribe, lifecycle event dispatch

## Completion Progress

| Milestone | Description | Status |
|-----------|-------------|--------|
| M7.1.0 | Mission Core dataclasses | Completed |
| M7.1.1 | Epic grouping | Completed |
| M7.1.2 | Mission Graph DAG | Completed |
| M7.1.3 | Planner Integration | Completed |
| M7.1.4 | Persistence layer | Completed |
| M7.1.5 | Event Bus Integration | Completed |
| M7.1.6 | Scheduler Integration | Completed |
| M7.1.7 | Mission Execution + AutonomousExecutor Integration | Completed |
| M7.1.8 | Tool Integration | Completed |
| M7.2 | ChiefAgent orchestration | Pending |
| M7.3 | FleetManager agent lifecycle | Pending |
| M7.4 | WorkPool task distribution | Pending |
| M7.5 | DependencyResolver task DAG | Pending |
| M7.6 | CapabilityRouter routing | Pending |
| M7.7 | KnowledgeRouter filtering | Pending |
| M7.8 | Integration and E2E tests | Pending |

## Dependencies

| From | Depends On |
|------|------------|
| M7.1.0 | None |
| M7.1.1 | M7.1.0 |
| M7.1.2 | M7.1.0, M7.1.1 |
| M7.1.3 | M7.1.0, M7.1.1, M7.1.2 |
| M7.1.4 | M7.1.0, M7.1.1, M7.1.2 |
| M7.1.5 | M7.1.0–M7.1.4 |
| M7.2 | M7.1.5 |
| M7.3 | M7.2 |
| M7.4 | M7.3 |
| M7.5 | M7.4 |
| M7.6 | M7.5 |
| M7.7 | M7.6 |
| M7.8 | All M7.x sub-missions |

## Next Mission

Mission 7.1.5 — Event Bus Integration

MISSION COMPLETE