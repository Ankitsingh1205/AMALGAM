class Task:

    def __init__(
        self,
        intent: str,
        action: str,
        model: str = None,
        tool: str = None,
        data=None
    ):
        self.intent = intent
        self.action = action
        self.model = model
        self.tool = tool
        self.data = data

    def __repr__(self):

        return (
            f"Task("
            f"intent={self.intent}, "
            f"action={self.action}, "
            f"model={self.model}, "
            f"tool={self.tool})"
        )