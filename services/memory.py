import json
import os


class MemoryService:

    def __init__(self):

        self.file = "data/memory.json"

        self.memories = {}

        self.load()

    def load(self):

        if os.path.exists(self.file):

            with open(self.file, "r") as f:

                self.memories = json.load(f)

    def save(self):

        with open(self.file, "w") as f:

            json.dump(self.memories, f, indent=4)

    def remember(self, key, value):

        self.memories[key] = value

        self.save()

    def recall(self, key):

        return self.memories.get(key)

    def show_all(self):

        return self.memories