from config import constants


class ActionRegistry:

    def __init__(self):

        self.routes = {
            constants.ACTION_CALCULATE: (constants.TOOL_CALCULATOR, "calculate"),
            constants.ACTION_RUN_PYTHON: (constants.TOOL_PYTHON, "execute"),
            constants.ACTION_LIST_FILES: (constants.TOOL_FILES, "list_dir"),
            constants.ACTION_REMEMBER: (constants.TOOL_MEMORY, "remember"),
            constants.ACTION_RECALL: (constants.TOOL_MEMORY, "recall"),
            constants.ACTION_SEARCH_WEB: (constants.TOOL_INTERNET, "search"),
            constants.ACTION_PROJECT_SUMMARY: (constants.SERVICE_PROJECT, "summarize"),
        }

    def get(self, action):

        return self.routes.get(action)

