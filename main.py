from brain.brain import Brain
from kernel.executor import Executor
from config import constants
from services.logger import get_logger


def main():

    logger = get_logger("cli")

    brain = Brain()

    kernel = Executor()

    kernel.boot()

    while True:

        try:
            user_input = input("\nYou: ")

            if user_input.lower() in constants.APP_EXIT_COMMANDS:

                print("AMALGAM shutting down...")
                logger.info("shutdown requested")

                break

            task = brain.think(user_input)

            kernel.execute(task)

        except KeyboardInterrupt:
            print("\nAMALGAM shutting down...")
            logger.info("shutdown interrupted")
            break

        except Exception as e:
            logger.error(f"Runtime Error: {e}")


if __name__ == "__main__":
    main()
