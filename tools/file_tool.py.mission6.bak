from pathlib import Path


class FileTool:

    def read(self, path: str):

        try:
            return Path(path).read_text(encoding="utf-8")

        except Exception as e:
            return f"Read Error: {e}"

    def write(self, path: str, content: str):

        try:
            Path(path).write_text(content, encoding="utf-8")
            return "File saved."

        except Exception as e:
            return f"Write Error: {e}"

    def list_dir(self, path="."):

        try:
            return [p.name for p in Path(path).iterdir()]

        except Exception as e:
            return f"Directory Error: {e}"