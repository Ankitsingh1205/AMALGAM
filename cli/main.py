import sys
from cli.commands import COMMANDS

def main():

    if len(sys.argv) < 2:
        print("Usage: amalgam <command>")
        return

    command = sys.argv[1]

    if command not in COMMANDS:
        print("Unknown command.")
        return

    COMMANDS[command]()

if __name__ == "__main__":
    main()
