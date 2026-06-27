from config.models import MODELS


class ToolRouter:

    def route(self, plan: str):

        routes = {

            "use_coder": MODELS["coding"],

            "use_creative_model": MODELS["creative"],

            "use_general_model": MODELS["general"],

            "use_memory": "memory",

            "use_internet": "internet",

            "use_calculator": "calculator"

        }

        return routes.get(plan, MODELS["general"])
