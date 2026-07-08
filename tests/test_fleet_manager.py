import time
from brain.fleet_manager import FleetManager
from brain.messaging import Messaging, Message

def test_fleet_manager_registration():
    msg = Messaging()
    fm = FleetManager(msg)
    
    # Simulate register message
    msg.send(Message(sender="agent1", recipient="fleet_manager", msg_type="register", payload={"capabilities": ["coding"]}))
    
    state = fm.get_agent_state("agent1")
    assert state
    assert "coding" in state["capabilities"]

def test_fleet_manager_heartbeat():
    msg = Messaging()
    fm = FleetManager(msg)
    
    fm.register("agent1", ["coding"])
    
    msg.send(Message(
        sender="agent1",
        recipient="fleet_manager",
        msg_type="heartbeat",
        payload={"status": "running", "load": 5}
    ))
    
    state = fm.get_agent_state("agent1")
    assert state["status"] == "running"
    assert state["load"] == 5

def test_fleet_manager_reap_dead_agents():
    msg = Messaging()
    fm = FleetManager(msg)
    
    fm.register("agent1", ["coding"])
    
    # Mock last seen to be old
    with fm._lock:
        fm._agents["agent1"]["last_seen"] = time.time() - 100
        
    dead = fm.reap_dead_agents(timeout_seconds=30.0)
    assert "agent1" in dead
    assert not fm.get_agent_state("agent1")


# ---------------------------------------------------------------------------
# Mission 7.3 — FleetManager lifecycle: unregister, failure tracking
# ---------------------------------------------------------------------------


def test_fleet_manager_unregister():
    msg = Messaging()
    fm = FleetManager(msg)

    fm.register("agent1", ["coding"])
    assert fm.get_agent_state("agent1")

    fm.unregister("agent1")
    assert fm.get_agent_state("agent1") == {}


def test_fleet_manager_unregister_unknown():
    msg = Messaging()
    fm = FleetManager(msg)

    # No-op for unknown agent — must not raise
    fm.unregister("nonexistent")


def test_fleet_manager_increment_failures():
    msg = Messaging()
    fm = FleetManager(msg)

    fm.register("agent1", ["coding"])
    assert fm.increment_failures("agent1") == 1
    assert fm.increment_failures("agent1") == 2
    assert fm.increment_failures("agent1") == 3

    state = fm.get_agent_state("agent1")
    assert state["consecutive_failures"] == 3


def test_fleet_manager_increment_failures_unknown():
    msg = Messaging()
    fm = FleetManager(msg)

    # Returns 0 for unknown agent — must not raise
    assert fm.increment_failures("nonexistent") == 0


def test_fleet_manager_clear_failures():
    msg = Messaging()
    fm = FleetManager(msg)

    fm.register("agent1", ["coding"])
    fm.increment_failures("agent1")
    fm.increment_failures("agent1")
    assert fm.get_agent_state("agent1")["consecutive_failures"] == 2

    fm.clear_failures("agent1")
    assert fm.get_agent_state("agent1")["consecutive_failures"] == 0


def test_fleet_manager_clear_failures_unknown():
    msg = Messaging()
    fm = FleetManager(msg)

    # No-op for unknown agent — must not raise
    fm.clear_failures("nonexistent")
