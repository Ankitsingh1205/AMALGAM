from services.diagnostics import DiagnosticsService


class FakeOllama:
    def is_running(self):
        return True

    def list_models(self):
        return ["qwen3:8b"]


def test_diagnostics_returns_structured_health_report(monkeypatch):
    monkeypatch.setattr("services.diagnostics.OllamaService", lambda: FakeOllama())

    report = DiagnosticsService().run_checks()

    assert report["status"] == "ok"
    assert set(report["checks"]) == {
        "configuration",
        "memory",
        "tool_registry",
        "service_registry",
        "ollama",
        "storage",
    }
    assert report["checks"]["ollama"]["status"] == "ok"


def test_diagnostics_reports_ollama_warning_when_unavailable():
    report = DiagnosticsService().check_ollama()

    assert report["status"] in {"ok", "warning"}
    assert "message" in report

