from kernel.state import KernelState
from kernel.task import Task
from kernel.dispatcher import Dispatcher
from models.registry import ModelRegistry
from config import constants, settings
from config.version import get_version_info
from services.logger import get_logger


class Executor:

    def __init__(self):

        self.state = KernelState()
        self.dispatcher = Dispatcher()
        self.logger = get_logger("kernel")

    def boot(self):

        separator = constants.BUILD_SEPARATOR * 60
        version = get_version_info()

        print(separator)
        print(settings.APP_NAME)
        print(settings.APP_DESCRIPTION)
        print(separator)

        self.state.memory_loaded = self.dispatcher.services.get("memory") is not None
        self.state.models_loaded = len(ModelRegistry().list_models())
        self.state.tools_loaded = len(self.dispatcher.tools.list_tools())
        self.state.services_loaded = len(self.dispatcher.services.list_services())

        self.state.ready()

        print(f"Kernel Version : {self.state.version}")
        print(f"Build Type     : {version['build_type']}")
        print(f"Environment    : {version['environment']}")
        print(f"Python Version : {version['python_version']}")
        print(f"OS             : {version['operating_system']}")
        print(f"Kernel Status  : {self.state.status}")
        print(f"Models Loaded  : {self.state.models_loaded}")
        print(f"Services       : {self.state.services_loaded}")
        print(f"Memory         : {'Connected' if self.state.memory_loaded else 'Offline'}")
        print(separator)

        self.logger.info(
            "kernel booted",
            version=self.state.version,
            status=self.state.status,
            models=self.state.models_loaded,
            tools=self.state.tools_loaded,
            services=self.state.services_loaded,
        )

    def execute(self, task: Task):

        self.logger.info("executing task", task=task)

        try:
            return self.dispatcher.dispatch(task)

        except Exception as e:
            message = f"Kernel Error: {e}"
            self.logger.error(message)
            return message
