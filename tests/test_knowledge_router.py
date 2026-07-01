from brain.shared_context import SharedContext
from brain.knowledge_router import KnowledgeRouter

def test_knowledge_router_subscribe_and_publish():
    ctx = SharedContext()
    kr = KnowledgeRouter(ctx)
    
    kr.subscribe("agent1", "architecture")
    kr.publish("architecture", {"nodes": 5})
    kr.publish("other_topic", {"data": 123})
    
    agent_ctx = kr.get_context("agent1")
    
    assert "architecture" in agent_ctx
    assert agent_ctx["architecture"] == {"nodes": 5}
    assert "other_topic" not in agent_ctx

def test_knowledge_router_unsubscribed_agent():
    ctx = SharedContext()
    kr = KnowledgeRouter(ctx)
    
    kr.publish("architecture", {"nodes": 5})
    
    agent_ctx = kr.get_context("unsubscribed_agent")
    assert agent_ctx == {}
