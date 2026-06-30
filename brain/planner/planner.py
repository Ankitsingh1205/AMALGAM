from kernel.task import Task
from models.registry import ModelRegistry
from config import constants


class Planner:

    def __init__(self):
        self.registry = ModelRegistry()

    def create_task(self, intent: str, user_input: str):

        if intent == constants.INTENT_MATH:
            return Task(
                intent=intent,
                action=constants.ACTION_CALCULATE,
                data=user_input,
            )

        if intent == constants.INTENT_MEMORY:

            if user_input.lower().startswith("remember "):
                payload = user_input[9:]

                if "=" in payload:
                    key, value = payload.split("=", 1)

                    return Task(
                        intent=intent,
                        action=constants.ACTION_REMEMBER,
                        data=(key.strip(), value.strip()),
                    )

            if user_input.lower().startswith("recall "):
                return Task(
                    intent=intent,
                    action=constants.ACTION_RECALL,
                    data=user_input[7:].strip(),
                )

        if intent == constants.INTENT_FILES:
            return Task(
                intent=intent,
                action=constants.ACTION_LIST_FILES,
                data=".",
            )

        if intent == constants.INTENT_INTERNET:

            query = (
                user_input
                .replace("search web", "")
                .replace("search", "")
                .replace("google", "")
                .replace("find online", "")
                .strip()
            )

            return Task(
                intent=intent,
                action=constants.ACTION_SEARCH_WEB,
                data=query,
            )

        if intent == constants.INTENT_PYTHON:

            code = (
                user_input
                .replace("run python", "")
                .replace("execute python", "")
                .replace("python:", "")
                .strip()
            )

            return Task(
                intent=intent,
                action=constants.ACTION_RUN_PYTHON,
                data=code,
            )

        if intent == constants.INTENT_PROJECT:
            return Task(
                intent=intent,
                action=constants.ACTION_PROJECT_SUMMARY,
                data=user_input,
            )

        if intent == constants.INTENT_CODING:
            return Task(
                intent=intent,
                action=constants.ACTION_GENERATE_CODE,
                model=self.registry.get("coding"),
                data=user_input,
            )

        return Task(
            intent=constants.INTENT_GENERAL,
            action=constants.ACTION_CHAT,
            model=self.registry.get("general"),
            data=user_input,
        )
