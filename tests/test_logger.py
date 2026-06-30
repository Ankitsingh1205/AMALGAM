from services.logger import Logger


def test_logger_returns_structured_record_without_console(capsys):
    logger = Logger("test", console=False)

    record = logger.info("hello", action="run")

    assert record.as_dict()["level"] == "INFO"
    assert record.as_dict()["source"] == "test"
    assert record.as_dict()["context"] == {"action": "run"}
    assert capsys.readouterr().out == ""


def test_logger_filters_below_configured_level():
    logger = Logger("test", level="ERROR", console=False)

    assert logger.info("ignored") is None
    assert logger.error("kept") is not None

