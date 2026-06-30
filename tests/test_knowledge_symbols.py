from knowledge.symbols import SymbolIndex


def test_symbol_index_includes_modules_classes_and_functions(tmp_path):
    root = tmp_path / "project"
    package = root / "pkg"
    package.mkdir(parents=True)
    module = package / "module.py"
    module.write_text(
        """
class Service:
    pass

def helper():
    pass
""",
        encoding="utf-8",
    )

    symbols = SymbolIndex().build(root, [module])
    qualified = {symbol["qualified_name"] for symbol in symbols}

    assert "pkg.module" in qualified
    assert "pkg.module.Service" in qualified
    assert "pkg.module.helper" in qualified

