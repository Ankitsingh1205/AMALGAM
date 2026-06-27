from brain.brain import Brain
from kernel.executor import Executor


def main():

    brain = Brain()

    kernel = Executor()

    kernel.boot()

    while True:

        user_input = input("\nYou: ")

        if user_input.lower() in ["exit", "quit"]:

            print("AMALGAM shutting down...")

            break

        task = brain.think(user_input)

        kernel.execute(task)


if __name__ == "__main__":
    main()