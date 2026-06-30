from config import settings
from models.registry import ModelRegistry
from services.memory import MemoryService
from services.ollama_service import OllamaService
from services.service_registry import ServiceRegistry
from tools.tool_registry import ToolRegistry


class DiagnosticsService:

    def run_checks(self):
        checks = {
            "configuration": self.check_configuration(),
            "memory": self.check_memory(),
            "tool_registry": self.check_tool_registry(),
            "service_registry": self.check_service_registry(),
            "ollama": self.check_ollama(),
            "storage": self.check_storage(),
        }

        return {
            "status": self.overall_status(checks),
            "checks": checks,
        }

    def overall_status(self, checks):
        if any(check["status"] == "error" for check in checks.values()):
            return "error"

        if any(check["status"] == "warning" for check in checks.values()):
            return "warning"

        return "ok"

    def check_configuration(self):
        models = ModelRegistry().list_models()
        required = [
            settings.APP_NAME,
            settings.APP_VERSION,
            settings.OLLAMA_HOST,
            settings.MEMORY_FILE,
            settings.INTERNET_SEARCH_URL,
            settings.INTERNET_TIMEOUT,
        ]

        if not all(required):
            return {
                "status": "error",
                "message": "Required configuration values are missing.",
            }

        if "general" not in models:
            return {
                "status": "error",
                "message": "General model is not configured.",
            }

        return {
            "status": "ok",
            "message": "Configuration loaded.",
            "details": {
                "app_name": settings.APP_NAME,
                "version": settings.APP_VERSION,
                "environment": settings.ENVIRONMENT,
                "model_roles": list(models.keys()),
            },
        }

    def check_memory(self):
        service = MemoryService()

        if not isinstance(service.show_all(), dict):
            return {
                "status": "error",
                "message": "Memory service did not load a dictionary.",
            }

        return {
            "status": "ok",
            "message": "Memory service loaded.",
            "details": {
                "entries": len(service.show_all()),
            },
        }

    def check_tool_registry(self):
        registry = ToolRegistry()
        tools = registry.list_tools()

        if not tools:
            return {
                "status": "error",
                "message": "No tools are registered.",
            }

        return {
            "status": "ok",
            "message": "Tool registry loaded.",
            "details": {
                "tools": tools,
            },
        }

    def check_service_registry(self):
        registry = ServiceRegistry()
        services = registry.list_services()

        if not services:
            return {
                "status": "error",
                "message": "No services are registered.",
            }

        return {
            "status": "ok",
            "message": "Service registry loaded.",
            "details": {
                "services": services,
            },
        }

    def check_ollama(self):
        service = OllamaService()
        running = service.is_running()

        return {
            "status": "ok" if running else "warning",
            "message": "Ollama is available." if running else "Ollama is not available.",
            "details": {
                "host": settings.OLLAMA_HOST,
                "models": service.list_models() if running else [],
            },
        }

    def check_storage(self):
        memory_file = settings.MEMORY_FILE
        storage_dir = memory_file.parent

        if memory_file.exists() and not memory_file.is_file():
            return {
                "status": "error",
                "message": "Memory path exists but is not a file.",
            }

        if not storage_dir.exists():
            return {
                "status": "warning",
                "message": "Storage directory has not been created yet.",
                "details": {
                    "path": str(storage_dir),
                },
            }

        return {
            "status": "ok",
            "message": "Storage path is available.",
            "details": {
                "path": str(storage_dir),
                "memory_file": str(memory_file),
            },
        }

