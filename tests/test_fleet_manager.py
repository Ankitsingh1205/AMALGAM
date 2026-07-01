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
