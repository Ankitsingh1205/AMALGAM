from services.service_registry import ServiceRegistry

registry = ServiceRegistry()

print("Installed Services:")

for service in registry.list_services():
    print("-", service)