class KernelState:

    def __init__(self):

        self.version = "0.2"

        self.status = "Booting"

        self.models_loaded = 0

        self.memory_loaded = False

        self.tools_loaded = 0

        self.services_loaded = 0

    def ready(self):

        self.status = "Online"