from config import constants, settings


def test_settings_expose_required_runtime_values():
    assert settings.APP_NAME == "AMALGAM OS"
    assert settings.APP_VERSION
    assert settings.OLLAMA_HOST.startswith("http")
    assert settings.MEMORY_FILE.name == "memory.json"
    assert settings.INTERNET_TIMEOUT > 0


def test_constants_expose_runtime_names():
    assert constants.ACTION_CALCULATE == "calculate"
    assert constants.SERVICE_LLM == "llm"
    assert constants.TOOL_CALCULATOR == "calculator"

