from config import constants, settings


class ToolRouter:
    """Routes a plan keyword to the appropriate tool or model.

    Optimization (Mission 6.5.2):
    - ``routes`` dict is built once in ``__init__`` instead of being
      reconstructed on every ``route()`` call.
    """

    def __init__(self):
        # Build the routing table once at construction time.
        self._routes = {
            "use_coder":          settings.MODELS["coding"],
            "use_creative_model": settings.MODELS["creative"],
            "use_general_model":  settings.MODELS["general"],
            "use_memory":         constants.TOOL_MEMORY,
            "use_internet":       constants.TOOL_INTERNET,
            "use_calculator":     constants.TOOL_CALCULATOR,
        }
        self._default = settings.MODELS["general"]

    def route(self, plan: str):
        return self._routes.get(plan, self._default)
