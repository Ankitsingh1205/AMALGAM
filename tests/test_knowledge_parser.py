from knowledge.parser import PythonParser


def test_python_parser_extracts_symbols_and_imports(tmp_path):
    root = tmp_path / "project"
    package = root / "pkg"
    package.mkdir(parents=True)
    module = package / "module.py"
    module.write_text(
        """
import os
from pathlib import Path

class Service:
    def run(self):
        pass

def helper():
    pass
""",
        encoding="utf-8",
    )

    parsed = PythonParser().parse_file(root, module)

    assert parsed["module"] == "pkg.module"
    assert {symbol["qualified_name"] for symbol in parsed["symbols"]} == {
        "pkg.module.Service",
        "pkg.module.Service.run",
        "pkg.module.helper",
    }
    assert {item["target"] for item in parsed["imports"]} == {"os", "pathlib"}

