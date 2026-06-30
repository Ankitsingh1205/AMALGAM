from kernel.executor import Executor
from config import settings


def test_kernel_boot_uses_dynamic_registry_counts():
    kernel = Executor()

    kernel.boot()

    assert kernel.state.status == "Online"
    assert kernel.state.version == settings.APP_VERSION
    assert kernel.state.models_loaded == len(settings.MODELS)
    assert kernel.state.tools_loaded == len(kernel.dispatcher.tools.list_tools())
    assert kernel.state.services_loaded == len(kernel.dispatcher.services.list_services())
    assert kernel.state.memory_loaded is True
