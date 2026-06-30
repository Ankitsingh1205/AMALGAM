from dataclasses import dataclass
from datetime import datetime, timezone

from config import settings


LEVELS = {
    "DEBUG": 10,
    "INFO": 20,
    "WARNING": 30,
    "ERROR": 40,
}


@dataclass
class LogRecord:
    timestamp: str
    level: str
    source: str
    message: str
    context: dict

    def as_dict(self):
        return {
            "timestamp": self.timestamp,
            "level": self.level,
            "source": self.source,
            "message": self.message,
            "context": self.context,
        }


class Logger:

    def __init__(self, source: str, level: str = None, console: bool = None):
        self.source = source
        self.level = level or settings.LOG_LEVEL
        self.console = settings.LOG_TO_CONSOLE if console is None else console
        self.records = []

    def debug(self, message: str, **context):
        return self.log("DEBUG", message, **context)

    def info(self, message: str, **context):
        return self.log("INFO", message, **context)

    def warning(self, message: str, **context):
        return self.log("WARNING", message, **context)

    def error(self, message: str, **context):
        return self.log("ERROR", message, **context)

    def log(self, level: str, message: str, **context):
        level = level.upper()

        if LEVELS[level] < LEVELS.get(self.level, LEVELS["INFO"]):
            return None

        record = LogRecord(
            timestamp=datetime.now(timezone.utc).isoformat(),
            level=level,
            source=self.source,
            message=message,
            context=context,
        )
        self.records.append(record)

        if self.console:
            print(self.format(record))

        return record

    def format(self, record: LogRecord):
        context = ""

        if record.context:
            pairs = [f"{key}={value}" for key, value in record.context.items()]
            context = " " + " ".join(pairs)

        return f"[{record.level}] {record.source}: {record.message}{context}"


def get_logger(source: str):
    return Logger(source)

