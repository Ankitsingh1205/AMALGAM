from brain.tools.tool_router import ToolRouter

router = ToolRouter()

plans = [
    "use_coder",
    "use_calculator",
    "use_memory",
    "use_creative_model",
    "use_general_model"
]

for p in plans:
    print(f"{p} ---> {router.route(p)}")
