from brain.tools.tool_router import ToolRouter
from config import settings


def test_tool_router_maps_known_plans():
    router = ToolRouter()

    assert router.route("use_coder") == settings.MODELS["coding"]
    assert router.route("use_calculator") == "calculator"
    assert router.route("use_memory") == "memory"


def test_tool_router_defaults_to_general_model():
    router = ToolRouter()

    assert router.route("missing") == settings.MODELS["general"]
