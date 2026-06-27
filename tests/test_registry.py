from tools.tool_registry import ToolRegistry

registry = ToolRegistry()

print("Installed Tools:")

for tool in registry.list_tools():
    print("-", tool)