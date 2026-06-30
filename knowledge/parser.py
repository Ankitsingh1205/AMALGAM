import ast
from pathlib import Path


class PythonParser:

    def parse_file(self, root, path):
        root = Path(root)
        path = Path(path)

        try:
            source = path.read_text(encoding="utf-8")
            tree = ast.parse(source)

        except (OSError, SyntaxError):
            return {
                "module": self.module_name(root, path),
                "symbols": [],
                "imports": [],
            }

        module = self.module_name(root, path)

        return {
            "module": module,
            "symbols": self.symbols(module, tree),
            "imports": self.imports(module, tree),
        }

    def module_name(self, root, path):
        relative = Path(path).relative_to(root).with_suffix("")
        parts = list(relative.parts)

        if parts[-1] == "__init__":
            parts = parts[:-1]

        return ".".join(parts)

    def symbols(self, module, tree):
        found = []

        for node in ast.iter_child_nodes(tree):
            if isinstance(node, ast.ClassDef):
                found.append(
                    {
                        "name": node.name,
                        "qualified_name": f"{module}.{node.name}",
                        "kind": "class",
                        "module": module,
                        "line": node.lineno,
                    }
                )

                for child in node.body:
                    if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        found.append(
                            {
                                "name": child.name,
                                "qualified_name": f"{module}.{node.name}.{child.name}",
                                "kind": "function",
                                "module": module,
                                "parent": node.name,
                                "line": child.lineno,
                            }
                        )

            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                found.append(
                    {
                        "name": node.name,
                        "qualified_name": f"{module}.{node.name}",
                        "kind": "function",
                        "module": module,
                        "line": node.lineno,
                    }
                )

        return found

    def imports(self, module, tree):
        found = []

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    found.append(
                        {
                            "source": module,
                            "target": alias.name,
                            "type": "import",
                            "line": node.lineno,
                        }
                    )

            if isinstance(node, ast.ImportFrom):
                if node.module:
                    target = "." * node.level + node.module
                else:
                    target = "." * node.level

                found.append(
                    {
                        "source": module,
                        "target": target,
                        "type": "import",
                        "line": node.lineno,
                    }
                )

        return found

