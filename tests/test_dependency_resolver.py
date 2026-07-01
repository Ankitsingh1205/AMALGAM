from brain.dependency_resolver import DependencyResolver, CycleError
import pytest

def test_resolve_linear_dependencies():
    resolver = DependencyResolver()
    tasks = [
        {"id": "c", "depends_on": ["b"]},
        {"id": "a", "depends_on": []},
        {"id": "b", "depends_on": ["a"]}
    ]
    
    ordered = resolver.resolve(tasks)
    ids = [t["id"] for t in ordered]
    
    assert ids == ["a", "b", "c"]

def test_resolve_independent_tasks():
    resolver = DependencyResolver()
    tasks = [
        {"id": "a", "depends_on": []},
        {"id": "b", "depends_on": []}
    ]
    
    ordered = resolver.resolve(tasks)
    ids = [t["id"] for t in ordered]
    
    assert set(ids) == {"a", "b"}

def test_resolve_cycle_raises_error():
    resolver = DependencyResolver()
    tasks = [
        {"id": "a", "depends_on": ["b"]},
        {"id": "b", "depends_on": ["c"]},
        {"id": "c", "depends_on": ["a"]}
    ]
    
    with pytest.raises(CycleError):
        resolver.resolve(tasks)

def test_resolve_missing_dependency():
    resolver = DependencyResolver()
    tasks = [
        {"id": "a", "depends_on": ["unknown"]}
    ]
    
    with pytest.raises(ValueError, match="depends on unknown task"):
        resolver.resolve(tasks)
