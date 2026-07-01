from brain.messaging import Messaging, Message
from brain.work_pool import WorkPool

def test_work_pool_submit_and_steal():
    msg = Messaging()
    pool = WorkPool(msg)
    
    # Track broadcast messages
    received = []
    msg.subscribe("*", lambda m: received.append(m))
    
    task_id = pool.submit_task({"action": "read"}, "files")
    
    # Broadcast should have been sent
    assert any(m.msg_type == "work_available" and m.payload["capability"] == "files" for m in received)
    
    # Steal the task
    task = pool.steal_task("agent1", ["files", "llm"])
    assert task is not None
    assert task["id"] == task_id
    assert task["owner"] == "agent1"
    assert task["status"] == "running"
    
    # Steal again should be empty
    assert pool.steal_task("agent2", ["files"]) is None

def test_work_pool_requeue():
    msg = Messaging()
    pool = WorkPool(msg)
    
    task_id = pool.submit_task({"action": "read"}, "files")
    pool.steal_task("agent1", ["files"])
    
    assert pool.requeue_task(task_id) is True
    
    # Can be stolen again
    task = pool.steal_task("agent2", ["files"])
    assert task is not None
    assert task["owner"] == "agent2"

def test_work_pool_complete():
    msg = Messaging()
    pool = WorkPool(msg)
    
    received = []
    msg.subscribe("*", lambda m: received.append(m))
    
    task_id = pool.submit_task({"action": "read"}, "files")
    pool.steal_task("agent1", ["files"])
    
    assert pool.complete_task(task_id, result="done") is True
    assert any(m.msg_type == "task_completed" and m.payload["task_id"] == task_id for m in received)
    
    progress = pool.get_progress()
    assert progress["total_active"] == 0
