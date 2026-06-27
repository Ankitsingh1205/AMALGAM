from core.orchestrator import Orchestrator

def main():
    amalgam = Orchestrator()
    amalgam.start()

    while True:
        user_input = input("\nYou: ")

        if user_input.lower() in ["exit", "quit"]:
            print("AMALGAM shutting down...")
            break

        amalgam.process(user_input)

if __name__ == "__main__":
    main()