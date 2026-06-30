from config import settings
from models.registry import ModelRegistry
from models.selector import ModelSelector


def test_model_registry_returns_configured_model():
    registry = ModelRegistry()

    assert registry.get("coding") == settings.MODELS["coding"]


def test_model_registry_falls_back_to_general():
    registry = ModelRegistry()

    assert registry.get("missing") == settings.MODELS["general"]


def test_model_selector_maps_plan_to_model():
    selector = ModelSelector()

    assert selector.select("use_coder") == settings.MODELS["coding"]
    assert selector.select("use_fast") == settings.MODELS["fast"]
