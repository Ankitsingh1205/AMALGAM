from pathlib import Path

from knowledge.parser import PythonParser


class RelationshipBuilder:

    def __init__(self):
        self.parser = PythonParser()

    def build(self, root, paths, packages):
        relationships = []

        for path in paths:
            if not path.is_file() or path.suffix != ".py":
                continue

            parsed = self.parser.parse_file(root, path)
            relationships.extend(parsed["imports"])

        relationships.extend(self.package_relationships(packages))

        return sorted(
            relationships,
            key=lambda item: (item["source"], item["target"], item["type"]),
        )

    def package_relationships(self, packages):
        relationships = []
        package_set = set(packages)

        for package in packages:
            parent = ".".join(package.split(".")[:-1])

            if parent and parent in package_set:
                relationships.append(
                    {
                        "source": parent,
                        "target": package,
                        "type": "package",
                        "line": None,
                    }
                )

        return relationships

