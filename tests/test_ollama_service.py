from services.ollama_service import OllamaService

service = OllamaService()

print("Ollama Running:", service.is_running())

print()

print("Installed Models:")

for model in service.list_models():
    print("-", model)

print()

print("Total Models:", service.count_models())