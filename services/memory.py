import json
from pathlib import Path

from config import settings


class MemoryService:

    def __init__(self):

        self.file = settings.MEMORY_FILE

        self.memories = {}

        self.load()

    def load(self):

        try:
            self.file = Path(self.file)

            if not self.file.exists():
                self.memories = {}
                return

            with self.file.open("r", encoding="utf-8") as f:

                self.memories = json.load(f)

        except (OSError, json.JSONDecodeError):
            self.memories = {}

    def save(self):

        try:
            self.file = Path(self.file)

            self.file.parent.mkdir(parents=True, exist_ok=True)

            with self.file.open("w", encoding="utf-8") as f:

                json.dump(self.memories, f, indent=4)

            return True

        except OSError:
            return False

    def remember(self, key, value):

        self.memories[key] = value

        return self.save()

    def forget(self, key):

        if key in self.memories:

            del self.memories[key]

            return self.save()

        return True

    def recall(self, key):

        return self.memories.get(key)

    def show_all(self):

        return self.memories
