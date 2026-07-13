from pathlib import Path

from config.models import MODELS


PROJECT_ROOT = Path(__file__).resolve().parent.parent

APP_NAME = "AMALGAM OS"
APP_DESCRIPTION = "Artificial Intelligence Operating System"
APP_VERSION = "0.8.0rc1"
BUILD_TYPE = "release-candidate"
ENVIRONMENT = "local"

OLLAMA_HOST = "http://127.0.0.1:11434"

MEMORY_FILE = PROJECT_ROOT / "storage" / "memory" / "memory.json"

INTERNET_SEARCH_URL = "https://duckduckgo.com/"
INTERNET_TIMEOUT = 10

LOG_LEVEL = "INFO"
LOG_TO_CONSOLE = True

