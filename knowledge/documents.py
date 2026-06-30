from pathlib import Path


DOCUMENT_EXTENSIONS = {".md", ".rst", ".txt"}


class DocumentReader:

    def read(self, root):
        root = Path(root)
        documents = []

        for path in self.document_paths(root):
            try:
                content = path.read_text(encoding="utf-8")

            except OSError:
                content = ""

            documents.append(
                {
                    "path": path.relative_to(root).as_posix(),
                    "title": self.title(path, content),
                    "content": content,
                    "line_count": len(content.splitlines()),
                }
            )

        return documents

    def document_paths(self, root):
        paths = []

        for name in ("README.md", "README.rst", "README.txt"):
            path = root / name

            if path.exists() and path.is_file():
                paths.append(path)

        for directory_name in ("docs", "spec"):
            directory = root / directory_name

            if not directory.exists() or not directory.is_dir():
                continue

            for path in directory.rglob("*"):
                if path.is_file() and path.suffix.lower() in DOCUMENT_EXTENSIONS:
                    paths.append(path)

        return sorted(set(paths), key=lambda item: item.relative_to(root).as_posix())

    def title(self, path, content):
        for line in content.splitlines():
            stripped = line.strip()

            if stripped.startswith("#"):
                return stripped.lstrip("#").strip()

        return path.stem

