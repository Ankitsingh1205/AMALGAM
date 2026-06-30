from kernel.executor import Executor
from kernel.task import Task
from tools.internet_tool import InternetTool
from config import settings


class FakeResponse:
    status_code = 200


def test_internet_tool_search_reports_status(monkeypatch):
    def fake_get(url, timeout):
        assert "q=OpenAI+news" in url
        assert timeout == settings.INTERNET_TIMEOUT
        return FakeResponse()

    monkeypatch.setattr("tools.internet_tool.requests.get", fake_get)

    tool = InternetTool()

    assert tool.search("OpenAI news") == "Connected (HTTP 200)"


def test_executor_dispatches_internet_task(monkeypatch):
    def fake_get(url, timeout):
        return FakeResponse()

    monkeypatch.setattr("tools.internet_tool.requests.get", fake_get)
    kernel = Executor()

    result = kernel.execute(
        Task(
            intent="internet",
            action="search_web",
            data="OpenAI",
        )
    )

    assert result == "Connected (HTTP 200)"
