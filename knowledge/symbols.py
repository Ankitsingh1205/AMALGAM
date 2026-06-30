from pathlib import Path

from knowledge.parser import PythonParser


class SymbolIndex:

    def __init__(self):
        self.parser = PythonParser()

    def build(self, root, paths):
        root = Path(root)
        symbols = []

        for path in paths:
            if not path.is_file() or path.suffix != ".py":
                continue

            parsed = self.parser.parse_file(root, path)
            module = parsed["module"]

            if module:
                symbols.append(
                    {
                        "name": module.split(".")[-1],
                        "qualified_name": module,
                        "kind": "module",
                        "module": module,
                        "line": 1,
                    }
                )

            symbols.extend(parsed["symbols"])

        return sorted(symbols, key=lambda item: (item["qualified_name"], item["kind"]))

