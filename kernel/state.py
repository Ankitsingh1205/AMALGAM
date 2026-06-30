from config import constants, settings


class KernelState:

    def __init__(self):

        self.version = settings.APP_VERSION

        self.status = constants.KERNEL_STATUS_BOOTING

        self.models_loaded = 0

        self.memory_loaded = False

        self.tools_loaded = 0

        self.services_loaded = 0

    def ready(self):

        self.status = constants.KERNEL_STATUS_ONLINE
