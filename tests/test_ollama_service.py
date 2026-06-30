from services.ollama_service import OllamaService


class FakeModel:
    model = "qwen3:8b"


class FakeResponse:
    models = [FakeModel()]


class FakeClient:
    def list(self):
        return FakeResponse()


class FailingClient:
    def list(self):
        raise RuntimeError("offline")


def test_ollama_service_reports_running_with_client():
    service = OllamaService()
    service.client = FakeClient()

    assert service.is_running() is True


def test_ollama_service_lists_models():
    service = OllamaService()
    service.client = FakeClient()

    assert service.list_models() == ["qwen3:8b"]
    assert service.count_models() == 1


def test_ollama_service_handles_failures():
    service = OllamaService()
    service.client = FailingClient()

    assert service.is_running() is False
    assert service.list_models() == []
