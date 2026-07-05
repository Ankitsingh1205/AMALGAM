from __future__ import annotations

from typing import Any

import pytest

from brain.mission import (
    Mission,
    MissionEvent,
    MissionEventBus,
    MissionEventType,
    MissionID,
    MissionStatus,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_mission(
    status: MissionStatus = MissionStatus.CREATED,
    title: str = "Test Mission",
) -> Mission:
    mission = Mission(
        id=MissionID.generate(),
        title=title,
        status=status,
    )
    mission.event_bus = MissionEventBus()
    return mission


# ---------------------------------------------------------------------------
# MissionEventType
# ---------------------------------------------------------------------------


class TestMissionEventType:
    def test_all_expected_values(self):
        assert MissionEventType.MISSION_CREATED.value == "mission_created"
        assert MissionEventType.MISSION_UPDATED.value == "mission_updated"
        assert (
            MissionEventType.MISSION_STATUS_CHANGED.value
            == "mission_status_changed"
        )
        assert MissionEventType.MISSION_STARTED.value == "mission_started"
        assert (
            MissionEventType.MISSION_COMPLETED.value
            == "mission_completed"
        )
        assert MissionEventType.MISSION_FAILED.value == "mission_failed"
        assert (
            MissionEventType.MISSION_CANCELLED.value
            == "mission_cancelled"
        )
        assert MissionEventType.MISSION_RECOVERING.value == "mission_recovering"
        assert MissionEventType.MISSION_REMOVED.value == "mission_removed"
        assert MissionEventType.MISSION_DELETED.value == "mission_deleted"

    def test_is_str_enum(self):
        assert isinstance(MissionEventType.MISSION_CREATED, str)


# ---------------------------------------------------------------------------
# MissionEvent — creation and validation
# ---------------------------------------------------------------------------


class TestMissionEventCreation:
    def test_default_construction_produces_valid_event(self):
        event = MissionEvent()
        assert isinstance(event.event_id, str)
        assert len(event.event_id) == 36
        assert event.event_type == MissionEventType.MISSION_STATUS_CHANGED
        assert event.mission_id == ""
        assert isinstance(event.timestamp, str)
        assert event.payload == {}

    def test_explicit_construction_stores_all_fields(self):
        event = MissionEvent(
            event_id="evt-001",
            event_type=MissionEventType.MISSION_CREATED,
            mission_id="m-42",
            timestamp="2026-07-03T00:00:00Z",
            payload={"source": "test"},
        )
        assert event.event_id == "evt-001"
        assert event.event_type == MissionEventType.MISSION_CREATED
        assert event.mission_id == "m-42"
        assert event.timestamp == "2026-07-03T00:00:00Z"
        assert event.payload == {"source": "test"}

    def test_unique_event_ids_by_default(self):
        e1 = MissionEvent()
        e2 = MissionEvent()
        assert e1.event_id != e2.event_id

    def test_is_frozen_immutable(self):
        event = MissionEvent(mission_id="m-1")
        with pytest.raises(Exception):
            event.mission_id = "m-2"  # type: ignore[misc]

    def test_equality_based_on_fields(self):
        e1 = MissionEvent(
            event_id="a",
            event_type=MissionEventType.MISSION_CREATED,
            mission_id="m",
            timestamp="t",
            payload={"k": "v"},
        )
        e2 = MissionEvent(
            event_id="a",
            event_type=MissionEventType.MISSION_CREATED,
            mission_id="m",
            timestamp="t",
            payload={"k": "v"},
        )
        e3 = MissionEvent(event_id="b")
        assert e1 == e2
        assert e1 != e3

    def test_hash_consistent_with_equality(self):
        e1 = MissionEvent(
            event_id="a",
            event_type=MissionEventType.MISSION_CREATED,
            mission_id="m",
            timestamp="t",
        )
        e2 = MissionEvent(
            event_id="a",
            event_type=MissionEventType.MISSION_CREATED,
            mission_id="m",
            timestamp="t",
        )
        assert hash(e1) == hash(e2)


# ---------------------------------------------------------------------------
# MissionEventBus — subscribe / unsubscribe
# ---------------------------------------------------------------------------


class TestEventBusSubscribe:
    def test_subscribe_adds_callback(self):
        bus = MissionEventBus()
        calls: list[MissionEvent] = []

        def handler(e: MissionEvent) -> None:
            calls.append(e)

        bus.subscribe(handler)
        assert bus.subscriber_count() == 1

    def test_duplicate_subscription_ignored(self):
        bus = MissionEventBus()
        events: list[MissionEvent] = []

        def handler(e: MissionEvent) -> None:
            events.append(e)

        bus.subscribe(handler)
        bus.subscribe(handler)
        assert bus.subscriber_count() == 1

        bus.publish(MissionEvent())
        assert len(events) == 1

    def test_subscribe_preserves_fifo_order(self):
        bus = MissionEventBus()
        order: list[int] = []

        def h1(e: MissionEvent) -> None:
            order.append(1)

        def h2(e: MissionEvent) -> None:
            order.append(2)

        def h3(e: MissionEvent) -> None:
            order.append(3)

        bus.subscribe(h1)
        bus.subscribe(h2)
        bus.subscribe(h3)
        bus.publish(MissionEvent())
        assert order == [1, 2, 3]

    def test_unsubscribe_removes_callback(self):
        bus = MissionEventBus()
        events: list[MissionEvent] = []

        def handler(e: MissionEvent) -> None:
            events.append(e)

        bus.subscribe(handler)
        bus.unsubscribe(handler)
        assert bus.subscriber_count() == 0

        bus.publish(MissionEvent())
        assert len(events) == 0

    def test_unsubscribe_non_subscriber_is_noop(self):
        bus = MissionEventBus()

        def handler(e: MissionEvent) -> None:
            pass

        bus.unsubscribe(handler)
        assert bus.subscriber_count() == 0

    def test_multiple_subscribers_deterministic_dispatch(self):
        bus = MissionEventBus()
        order: list[int] = []

        for i in range(5):

            def make_handler(n: int = i) -> Any:
                def h(e: MissionEvent) -> None:
                    order.append(n)

                return h

            bus.subscribe(make_handler())

        bus.publish(MissionEvent())
        assert order == [0, 1, 2, 3, 4]

    def test_subscriber_exception_isolation(self):
        bus = MissionEventBus()
        received: list[int] = []

        def good(e: MissionEvent) -> None:
            received.append(1)

        def bad(e: MissionEvent) -> None:
            raise RuntimeError("subscriber error")

        def also_good(e: MissionEvent) -> None:
            received.append(2)

        bus.subscribe(good)
        bus.subscribe(bad)
        bus.subscribe(also_good)

        result = bus.publish(MissionEvent())
        assert received == [1, 2]
        assert result == 2

    def test_publish_returns_delivered_count(self):
        bus = MissionEventBus()
        received: list[MissionEvent] = []

        def h(e: MissionEvent) -> None:
            received.append(e)

        bus.subscribe(h)
        count = bus.publish(MissionEvent(mission_id="X"))
        assert count == 1
        assert len(received) == 1

    def test_publish_rejects_non_mission_event(self):
        bus = MissionEventBus()

        def h(e: MissionEvent) -> None:
            pass

        bus.subscribe(h)

        with pytest.raises(TypeError, match="Expected MissionEvent"):
            bus.publish({"not": "an event"})  # type: ignore[arg-type]

    def test_publish_zero_subscribers_returns_zero(self):
        bus = MissionEventBus()
        count = bus.publish(MissionEvent())
        assert count == 0

    def test_clear_removes_all_subscribers(self):
        bus = MissionEventBus()
        events: list[MissionEvent] = []

        def h(e: MissionEvent) -> None:
            events.append(e)

        bus.subscribe(h)
        bus.clear()
        assert bus.subscriber_count() == 0
        bus.publish(MissionEvent())
        assert len(events) == 0

    def test_subscriber_count_empty(self):
        bus = MissionEventBus()
        assert bus.subscriber_count() == 0

    def test_subscriber_count_after_operations(self):
        bus = MissionEventBus()

        def h1(e: MissionEvent) -> None:
            pass

        def h2(e: MissionEvent) -> None:
            pass

        bus.subscribe(h1)
        assert bus.subscriber_count() == 1
        bus.subscribe(h2)
        assert bus.subscriber_count() == 2
        bus.unsubscribe(h1)
        assert bus.subscriber_count() == 1
        bus.clear()
        assert bus.subscriber_count() == 0

    def test_propagates_to_all_even_after_failure(self):
        bus = MissionEventBus()
        received: list[str] = []

        def h1(e: MissionEvent) -> None:
            received.append("a")

        def h2(e: MissionEvent) -> None:
            raise RuntimeError("fail")

        def h3(e: MissionEvent) -> None:
            received.append("c")

        bus.subscribe(h1)
        bus.subscribe(h2)
        bus.subscribe(h3)
        bus.publish(MissionEvent())
        assert received == ["a", "c"]

    def test_synchronous_dispatch_is_deterministic(self):
        bus = MissionEventBus()
        events: list[MissionEvent] = []

        def collector(e: MissionEvent) -> None:
            events.append(e)

        bus.subscribe(collector)

        e1 = MissionEvent(event_id="1")
        e2 = MissionEvent(event_id="2")
        bus.publish(e1)
        bus.publish(e2)

        assert events[0] is e1
        assert events[1] is e2


# ---------------------------------------------------------------------------
# Event ordering through the bus
# ---------------------------------------------------------------------------


class TestEventOrdering:
    def test_events_published_in_order_arrive_in_order(self):
        bus = MissionEventBus()
        received: list[str] = []

        def collector(e: MissionEvent) -> None:
            received.append(e.event_id)

        bus.subscribe(collector)
        bus.publish(MissionEvent(event_id="A"))
        bus.publish(MissionEvent(event_id="B"))
        bus.publish(MissionEvent(event_id="C"))
        assert received == ["A", "B", "C"]


# ---------------------------------------------------------------------------
# Payload correctness
# ---------------------------------------------------------------------------


class TestEventPayload:
    def test_status_changed_payload_includes_old_and_new(self):
        bus = MissionEventBus()
        events: list[MissionEvent] = []

        def collector(e: MissionEvent) -> None:
            events.append(e)

        bus.subscribe(collector)

        event = MissionEvent(
            event_type=MissionEventType.MISSION_STATUS_CHANGED,
            mission_id="m",
            payload={"old_status": "created", "new_status": "analyzing"},
        )
        bus.publish(event)

        assert events[0].payload["old_status"] == "created"
        assert events[0].payload["new_status"] == "analyzing"

    def test_payload_is_preserved_exactly(self):
        bus = MissionEventBus()
        captured: dict[str, Any] = {}

        def collector(e: MissionEvent) -> None:
            captured["payload"] = dict(e.payload)

        bus.subscribe(collector)
        payload = {"custom": "data", "nested": {"x": 1}}
        bus.publish(MissionEvent(payload=payload))
        assert captured["payload"] == payload


# ---------------------------------------------------------------------------
# Mission integration — lifecycle events
# ---------------------------------------------------------------------------


class TestMissionLifecycleEvents:
    @staticmethod
    def _collect(bus: MissionEventBus) -> list[tuple[str, dict[str, Any]]]:
        events: list[tuple[str, dict[str, Any]]] = []

        def collector(e: MissionEvent) -> None:
            events.append((e.event_type.value, dict(e.payload)))

        bus.subscribe(collector)
        return events

    def test_created_to_analyzing_emits_status_changed(self):
        mission = _make_mission(MissionStatus.CREATED)
        collected = self._collect(mission.event_bus)

        mission.transition(MissionStatus.ANALYZING)

        assert collected == [
            (
                "mission_status_changed",
                {"old_status": "created", "new_status": "analyzing"},
            ),
        ]

    def test_analyzing_to_planning_emits_status_changed(self):
        mission = _make_mission(MissionStatus.ANALYZING)
        collected = self._collect(mission.event_bus)

        mission.transition(MissionStatus.PLANNING)

        assert len(collected) == 1
        assert collected[0][0] == "mission_status_changed"

    def test_planning_to_ready_emits_status_changed(self):
        mission = _make_mission(MissionStatus.PLANNING)
        collected = self._collect(mission.event_bus)

        mission.transition(MissionStatus.READY)

        assert len(collected) == 1
        assert collected[0][0] == "mission_status_changed"

    def test_ready_to_running_emits_status_changed(self):
        mission = _make_mission(MissionStatus.READY)
        collected = self._collect(mission.event_bus)

        mission.transition(MissionStatus.RUNNING)

        assert len(collected) == 1
        assert collected[0][0] == "mission_status_changed"
        assert collected[0][1]["old_status"] == "ready"
        assert collected[0][1]["new_status"] == "running"

    def test_running_to_verifying_emits_status_changed(self):
        mission = _make_mission(MissionStatus.RUNNING)
        collected = self._collect(mission.event_bus)

        mission.transition(MissionStatus.VERIFYING)

        assert len(collected) == 1
        assert collected[0][0] == "mission_status_changed"

    def test_verifying_to_completed_emits_status_changed_and_completed(self):
        mission = _make_mission(MissionStatus.VERIFYING)
        collected = self._collect(mission.event_bus)

        mission.transition(MissionStatus.COMPLETED)

        assert collected == [
            (
                "mission_status_changed",
                {"old_status": "verifying", "new_status": "completed"},
            ),
            (
                "mission_completed",
                {"status": "completed"},
            ),
        ]

    def test_running_to_failed_emits_status_changed_and_failed(self):
        mission = _make_mission(MissionStatus.RUNNING)
        collected = self._collect(mission.event_bus)

        mission.transition(MissionStatus.FAILED)

        assert collected == [
            (
                "mission_status_changed",
                {"old_status": "running", "new_status": "failed"},
            ),
            (
                "mission_failed",
                {"status": "failed"},
            ),
        ]

    def test_ready_to_failed_emits_status_changed_and_failed(self):
        mission = _make_mission(MissionStatus.READY)
        collected = self._collect(mission.event_bus)

        mission.transition(MissionStatus.FAILED)

        types = [t for t, _ in collected]
        assert "mission_status_changed" in types
        assert "mission_failed" in types
        assert len(collected) == 2

    def test_created_to_cancelled_emits_status_changed_and_cancelled(self):
        mission = _make_mission(MissionStatus.CREATED)
        collected = self._collect(mission.event_bus)

        mission.transition(MissionStatus.CANCELLED)

        types = [t for t, _ in collected]
        assert "mission_status_changed" in types
        assert "mission_cancelled" in types
        assert len(collected) == 2

    def test_any_nonterminal_to_cancelled_emits_cancelled(self):
        mission = _make_mission(MissionStatus.RUNNING)
        collected = self._collect(mission.event_bus)

        mission.transition(MissionStatus.CANCELLED)

        types = [t for t, _ in collected]
        assert "mission_cancelled" in types

    def test_any_nonterminal_to_failed_emits_failed(self):
        mission = _make_mission(MissionStatus.ANALYZING)
        collected = self._collect(mission.event_bus)

        mission.transition(MissionStatus.FAILED)

        types = [t for t, _ in collected]
        assert "mission_failed" in types

    def test_recovering_to_running_emits_status_changed_only(self):
        mission = _make_mission(MissionStatus.RECOVERING)
        collected = self._collect(mission.event_bus)

        mission.transition(MissionStatus.RUNNING)

        assert len(collected) == 1
        assert collected[0][0] == "mission_status_changed"

    def test_idempotent_transition_emits_no_events(self):
        mission = _make_mission(MissionStatus.RUNNING)
        collected = self._collect(mission.event_bus)

        mission.transition(MissionStatus.RUNNING)

        assert collected == []

    def test_invalid_transition_emits_no_events(self):
        mission = _make_mission(MissionStatus.CREATED)
        collected = self._collect(mission.event_bus)

        with pytest.raises(ValueError, match="Invalid transition"):
            mission.transition(MissionStatus.COMPLETED)

        assert collected == []

    def test_terminal_to_anything_emits_no_events(self):
        mission = _make_mission(MissionStatus.COMPLETED)
        collected = self._collect(mission.event_bus)

        with pytest.raises(ValueError, match="Cannot transition from terminal"):
            mission.transition(MissionStatus.FAILED)

        assert collected == []

    def test_mission_id_in_event_matches(self):
        mission = _make_mission(MissionStatus.ANALYZING)
        events: list[MissionEvent] = []

        def collector(e: MissionEvent) -> None:
            events.append(e)

        mission.event_bus.subscribe(collector)
        mission.transition(MissionStatus.PLANNING)

        assert events[0].mission_id == str(mission.id)


# ---------------------------------------------------------------------------
# Mission integration — multiple subscribers
# ---------------------------------------------------------------------------


class TestMissionIntegrationMultipleSubscribers:
    def test_multiple_subscribers_all_receive(self):
        mission = _make_mission(MissionStatus.PLANNING)
        r1: list[str] = []
        r2: list[str] = []

        def s1(e: MissionEvent) -> None:
            r1.append(e.event_type.value)

        def s2(e: MissionEvent) -> None:
            r2.append(e.event_type.value)

        mission.event_bus.subscribe(s1)
        mission.event_bus.subscribe(s2)
        mission.transition(MissionStatus.READY)

        assert r1 == ["mission_status_changed"]
        assert r2 == ["mission_status_changed"]

    def test_subscriber_exception_does_not_break_mission(self):
        mission = _make_mission(MissionStatus.PLANNING)
        received: list[str] = []

        def bad(e: MissionEvent) -> None:
            raise RuntimeError("fail")

        def good(e: MissionEvent) -> None:
            received.append(e.event_type.value)

        mission.event_bus.subscribe(bad)
        mission.event_bus.subscribe(good)

        mission.transition(MissionStatus.READY)
        assert mission.status == MissionStatus.READY
        assert received == ["mission_status_changed"]


# ---------------------------------------------------------------------------
# Backward compatibility
# ---------------------------------------------------------------------------


class TestBackwardCompatibility:
    def test_mission_without_event_bus_transitions_unchanged(self):
        mission = Mission(id=MissionID.generate(), title="No Bus")
        assert mission.event_bus is None

        mission.transition(MissionStatus.ANALYZING)
        assert mission.status == MissionStatus.ANALYZING

        mission.transition(MissionStatus.FAILED)
        assert mission.status == MissionStatus.FAILED

    def test_serialization_excludes_event_bus(self):
        mission = _make_mission(MissionStatus.CREATED)
        bus = mission.event_bus

        data = mission.to_dict()
        assert "event_bus" not in data

        restored = Mission.from_dict(data)
        assert restored.event_bus is None

    def test_existing_public_api_unchanged(self):
        mission = Mission(id=MissionID.generate(), title="Compat")
        assert mission.title == "Compat"
        assert mission.description == ""
        assert mission.priority.value == 5
        assert mission.status == MissionStatus.CREATED
        assert mission.children == []
        assert mission.dependencies == []
        mission.transition(MissionStatus.ANALYZING)
        assert mission.status == MissionStatus.ANALYZING
        mission.add_child(Mission(id=MissionID.generate(), title="Child"))
        assert len(mission.children) == 1
        assert mission.to_dict()["title"] == "Compat"

    def test_persistence_load_mission_no_event_bus(self):
        mission = Mission(id=MissionID.generate(), title="PTest")
        serialized = mission.to_dict()
        restored = Mission.from_dict(serialized)
        assert restored.event_bus is None
        restored.transition(MissionStatus.ANALYZING)
        assert restored.status == MissionStatus.ANALYZING

    def test_event_bus_not_serialized_in_children(self):
        parent = _make_mission(MissionStatus.CREATED, title="Parent")
        child = _make_mission(MissionStatus.CREATED, title="Child")
        child.event_bus = MissionEventBus()  # child has its own bus
        parent.add_child(child)

        data = parent.to_dict()
        assert "event_bus" not in data
        child_data = data["children"][0]
        assert "event_bus" not in child_data

    def test_from_dict_does_not_crash_on_unknown_keys(self):
        raw = {
            "id": str(MissionID.generate()),
            "title": "ForwardCompat",
            "event_bus": {"should": "be ignored"},
            "unknown_field": 42,
        }
        mission = Mission.from_dict(raw)
        assert mission.title == "ForwardCompat"
        assert mission.event_bus is None

    def test_subscriber_count_after_clear(self):
        bus = MissionEventBus()

        def h(e: MissionEvent) -> None:
            pass

        bus.subscribe(h)
        bus.subscribe(h)
        assert bus.subscriber_count() == 1
        bus.clear()
        assert bus.subscriber_count() == 0

    def test_unsubscribe_one_does_not_affect_others(self):
        bus = MissionEventBus()
        received: list[str] = []

        def h1(e: MissionEvent) -> None:
            received.append("a")

        def h2(e: MissionEvent) -> None:
            received.append("b")

        bus.subscribe(h1)
        bus.subscribe(h2)
        bus.unsubscribe(h1)
        bus.publish(MissionEvent())
        assert received == ["b"]

    def test_clear_before_publish_safe(self):
        bus = MissionEventBus()
        bus.clear()
        result = bus.publish(MissionEvent())
        assert result == 0

    def test_event_bus_attrs(self):
        bus = MissionEventBus()
        assert bus.subscriber_count() == 0

        bus.subscribe(lambda e: None)
        assert bus.subscriber_count() == 1

        bus.clear()
        assert bus.subscriber_count() == 0

    def test_event_created_typed_correctly(self):
        bus = MissionEventBus()
        events: list[MissionEvent] = []

        def handler(e: MissionEvent) -> None:
            events.append(e)

        bus.subscribe(handler)
        bus.publish(MissionEvent(
            event_type=MissionEventType.MISSION_CREATED,
            mission_id="m",
        ))
        assert len(events) == 1
        assert events[0].event_type == MissionEventType.MISSION_CREATED

    def test_event_updated_typed_correctly(self):
        bus = MissionEventBus()
        events: list[MissionEvent] = []

        def handler(e: MissionEvent) -> None:
            events.append(e)

        bus.subscribe(handler)
        bus.publish(MissionEvent(
            event_type=MissionEventType.MISSION_UPDATED,
            mission_id="m",
        ))
        assert events[0].event_type == MissionEventType.MISSION_UPDATED

    def test_event_deleted_typed_correctly(self):
        bus = MissionEventBus()
        events: list[MissionEvent] = []

        def handler(e: MissionEvent) -> None:
            events.append(e)

        bus.subscribe(handler)
        bus.publish(MissionEvent(
            event_type=MissionEventType.MISSION_DELETED,
            mission_id="m",
        ))
        assert events[0].event_type == MissionEventType.MISSION_DELETED


# ---------------------------------------------------------------------------
# New event types — MISSION_STARTED, MISSION_RECOVERING, MISSION_REMOVED
# ---------------------------------------------------------------------------


class TestNewEventTypes:
    def test_event_started_typed_correctly(self):
        bus = MissionEventBus()
        events: list[MissionEvent] = []

        def handler(e: MissionEvent) -> None:
            events.append(e)

        bus.subscribe(handler)
        bus.publish(MissionEvent(
            event_type=MissionEventType.MISSION_STARTED,
            mission_id="m",
        ))
        assert len(events) == 1
        assert events[0].event_type == MissionEventType.MISSION_STARTED

    def test_event_recovering_typed_correctly(self):
        bus = MissionEventBus()
        events: list[MissionEvent] = []

        def handler(e: MissionEvent) -> None:
            events.append(e)

        bus.subscribe(handler)
        bus.publish(MissionEvent(
            event_type=MissionEventType.MISSION_RECOVERING,
            mission_id="m",
        ))
        assert events[0].event_type == MissionEventType.MISSION_RECOVERING

    def test_event_removed_typed_correctly(self):
        bus = MissionEventBus()
        events: list[MissionEvent] = []

        def handler(e: MissionEvent) -> None:
            events.append(e)

        bus.subscribe(handler)
        bus.publish(MissionEvent(
            event_type=MissionEventType.MISSION_REMOVED,
            mission_id="m",
        ))
        assert events[0].event_type == MissionEventType.MISSION_REMOVED

    def test_started_enum_is_str(self):
        assert isinstance(MissionEventType.MISSION_STARTED, str)
        assert MissionEventType.MISSION_STARTED == "mission_started"

    def test_recovering_enum_is_str(self):
        assert isinstance(MissionEventType.MISSION_RECOVERING, str)
        assert MissionEventType.MISSION_RECOVERING == "mission_recovering"

    def test_removed_enum_is_str(self):
        assert isinstance(MissionEventType.MISSION_REMOVED, str)
        assert MissionEventType.MISSION_REMOVED == "mission_removed"


# ---------------------------------------------------------------------------
# Event history — insertion order, bounded capacity, clear
# ---------------------------------------------------------------------------


class TestEventHistory:
    def test_history_empty_by_default(self):
        bus = MissionEventBus()
        assert bus.event_history() == []

    def test_history_preserves_insertion_order(self):
        bus = MissionEventBus()
        e1 = MissionEvent(event_id="A")
        e2 = MissionEvent(event_id="B")
        e3 = MissionEvent(event_id="C")

        bus.publish(e1)
        bus.publish(e2)
        bus.publish(e3)

        history = bus.event_history()
        assert history == [e1, e2, e3]

    def test_history_by_event_id_order(self):
        bus = MissionEventBus()
        ids = ["X", "Y", "Z"]
        for eid in ids:
            bus.publish(MissionEvent(event_id=eid))

        history = bus.event_history()
        assert [e.event_id for e in history] == ["X", "Y", "Z"]

    def test_history_with_no_subscribers(self):
        bus = MissionEventBus()
        bus.publish(MissionEvent(event_id="A"))
        assert len(bus.event_history()) == 1

    def test_history_limit_bounded(self):
        bus = MissionEventBus(history_limit=3)
        for i in range(5):
            bus.publish(MissionEvent(event_id=str(i)))

        history = bus.event_history()
        assert len(history) == 3
        assert [e.event_id for e in history] == ["2", "3", "4"]

    def test_history_limit_exactly_at_capacity(self):
        bus = MissionEventBus(history_limit=3)
        bus.publish(MissionEvent(event_id="1"))
        bus.publish(MissionEvent(event_id="2"))
        bus.publish(MissionEvent(event_id="3"))

        history = bus.event_history()
        assert len(history) == 3
        assert [e.event_id for e in history] == ["1", "2", "3"]

    def test_history_limit_zero_is_effectively_unbounded(self):
        bus = MissionEventBus(history_limit=0)
        for i in range(10):
            bus.publish(MissionEvent(event_id=str(i)))

        history = bus.event_history()
        assert len(history) == 10

    def test_history_limit_negative_is_unbounded(self):
        bus = MissionEventBus(history_limit=-5)
        bus.publish(MissionEvent(event_id="A"))
        bus.publish(MissionEvent(event_id="B"))
        assert len(bus.event_history()) == 2

    def test_history_unbounded_by_default(self):
        bus = MissionEventBus()
        for i in range(50):
            bus.publish(MissionEvent(event_id=str(i)))
        assert len(bus.event_history()) == 50

    def test_history_clear_resets(self):
        bus = MissionEventBus()
        bus.publish(MissionEvent(event_id="A"))
        bus.publish(MissionEvent(event_id="B"))
        assert len(bus.event_history()) == 2

        bus.clear()
        assert bus.event_history() == []
        assert bus.subscriber_count() == 0

    def test_history_copy_is_shallow(self):
        bus = MissionEventBus()
        e1 = MissionEvent(event_id="1")
        bus.publish(e1)

        history = bus.event_history()
        assert history == [e1]
        assert history[0] is e1

    def test_history_independent_from_internal_buffer(self):
        bus = MissionEventBus()
        bus.publish(MissionEvent(event_id="A"))
        history = bus.event_history()
        history.clear()

        still_there = bus.event_history()
        assert len(still_there) == 1
        assert still_there[0].event_id == "A"

    def test_history_limit_one(self):
        bus = MissionEventBus(history_limit=1)
        bus.publish(MissionEvent(event_id="first"))
        bus.publish(MissionEvent(event_id="second"))
        bus.publish(MissionEvent(event_id="third"))

        history = bus.event_history()
        assert len(history) == 1
        assert history[0].event_id == "third"

    def test_publish_history_order(self):
        bus = MissionEventBus()
        events = [MissionEvent(event_id=str(i)) for i in range(5)]
        for e in events:
            bus.publish(e)

        history = bus.event_history()
        assert history == events

    def test_type_invalid_event_not_recorded_in_history(self):
        bus = MissionEventBus()
        with pytest.raises(TypeError, match="Expected MissionEvent"):
            bus.publish({"not": "event"})

        assert bus.event_history() == []