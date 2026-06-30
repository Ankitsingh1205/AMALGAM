from pathlib import Path


class ProjectTree:

    def build(self, root, paths):
        root = Path(root).resolve()
        tree = {
            "name": root.name,
            "path": ".",
            "type": "directory",
            "children": [],
        }

        directories = {Path("."): tree}

        for path in sorted(paths, key=lambda item: item.relative_to(root).as_posix()):
            relative = path.relative_to(root)
            parent_relative = relative.parent

            parent = directories.get(parent_relative)
            if parent is None:
                parent = self.ensure_directory(root, directories, parent_relative)

            node = {
                "name": path.name,
                "path": relative.as_posix(),
                "type": "directory" if path.is_dir() else "file",
            }

            if path.is_dir():
                node["children"] = []
                directories[relative] = node

            parent["children"].append(node)

        return tree

    def ensure_directory(self, root, directories, relative):
        parts = relative.parts
        current_relative = Path(".")
        current = directories[current_relative]

        for part in parts:
            current_relative = current_relative / part

            if current_relative not in directories:
                node = {
                    "name": part,
                    "path": current_relative.as_posix(),
                    "type": "directory",
                    "children": [],
                }
                current["children"].append(node)
                directories[current_relative] = node

            current = directories[current_relative]

        return current

