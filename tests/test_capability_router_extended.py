from brain.capability_router import CapabilityRouter
from brain.fleet_manager import FleetManager
from brain.messaging import Messaging

def test_static_routing():
    router = CapabilityRouter()
    
    assert router.route({"action": "list_files"}) == "files"
    assert router.route({"action": "remember"}) == "memory"
    assert router.route({"data": "please explain this class relationships"}) == "knowledge"
    assert router.route({"action": "unknown"}) == "llm"

def test_dynamic_routing():
    router = CapabilityRouter()
    msg = Messaging()
    fm = FleetManager(msg)
    
    fm.register("agent1", ["files", "llm"])
    fm.register("agent2", ["files", "llm"])
    
    fm.report_health("agent1", {"load": 10})
    fm.report_health("agent2", {"load": 2})
    
    # agent2 has lower load, should be chosen for "files" capability
    route = router.route({"action": "list_files"}, fleet_manager=fm)
    assert route == "agent2"
    
    # Tie break by consecutive failures
    fm.report_health("agent2", {"load": 10, "consecutive_failures": 5})
    fm.report_health("agent1", {"load": 10, "consecutive_failures": 0})
    
    route = router.route({"action": "list_files"}, fleet_manager=fm)
    assert route == "agent1"
