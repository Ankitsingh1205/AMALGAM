from config import constants, settings


class ToolRouter:

    def route(self, plan: str):

        routes = {

            "use_coder": settings.MODELS["coding"],

            "use_creative_model": settings.MODELS["creative"],

            "use_general_model": settings.MODELS["general"],

            "use_memory": constants.TOOL_MEMORY,

            "use_internet": constants.TOOL_INTERNET,

            "use_calculator": constants.TOOL_CALCULATOR

        }

        return routes.get(plan, settings.MODELS["general"])
