import threading
from agents.chief_agent import ChiefAgent
from brain.dependency_resolver import DependencyResolver
from brain.messaging import Messaging, Message
from brain.shared_context import SharedContext
from brain.work_pool import WorkPool

def test_chief_agent_mission_decomposition():
    msg = Messaging()
    pool = WorkPool(msg)
    resolver = DependencyResolver()
    ctx = SharedContext()
    ctx.set("task", "build website")
    
    chief = ChiefAgent(pool, resolver, ctx, msg)
    
    # We will run chief.run() in a separate thread since it blocks,
    # then we simulate the planner and workers completing tasks.
    
    def simulate_workers():
        import time
        time.sleep(0.1) # Wait for chief to submit planning task
        
        # 1. Planner steals the planning task
        plan_task = pool.steal_task("planner_1", ["planner"])
        assert plan_task is not None
        assert plan_task["action"] == "plan"
        
        # 2. Planner returns the decomposed tasks
        sub_tasks = [
            {"id": "write_html", "depends_on": []},
            {"id": "write_css", "depends_on": ["write_html"]},
        ]
        pool.complete_task(plan_task["id"], result=sub_tasks)
        
        time.sleep(0.1)
        
        # 3. Chief should have submitted "write_html"
        t1 = pool.steal_task("engineer_1", ["llm"])
        assert t1 is not None
        assert t1["id"] == "write_html"
        
        # "write_css" shouldn't be submitted yet
        assert pool.steal_task("engineer_2", ["llm"]) is None
        
        # Complete t1
        pool.complete_task(t1["id"], result="html done")
        
        time.sleep(0.1)
        
        # 4. Chief should have submitted "write_css"
        t2 = pool.steal_task("engineer_1", ["llm"])
        assert t2 is not None
        assert t2["id"] == "write_css"
        
        # Complete t2
        pool.complete_task(t2["id"], result="css done")
        
    worker_thread = threading.Thread(target=simulate_workers)
    worker_thread.start()
    
    # Blocks until all tasks are completed
    result = chief.run(ctx)
    
    worker_thread.join(timeout=2.0)
    
    assert result["success"] is True
