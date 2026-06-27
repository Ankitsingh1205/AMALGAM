class BaseTool:

    name = "base"

    def execute(self, *args, **kwargs):
        raise NotImplementedError