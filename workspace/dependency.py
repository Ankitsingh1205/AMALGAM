from pathlib import Path


class DependencySummary:

    def from_requirements(self, text):
        dependencies = []

        for line in text.splitlines():
            cleaned = line.strip()

            if not cleaned or cleaned.startswith("#"):
                continue

            dependencies.append(cleaned)

        return dependencies

    def from_pyproject(self, text):
        dependencies = []
        in_dependencies = False

        for line in text.splitlines():
            stripped = line.strip()

            if stripped == "dependencies = [":
                in_dependencies = True
                continue

            if in_dependencies and stripped == "]":
                break

            if in_dependencies:
                value = stripped.rstrip(",").strip("\"'")

                if value:
                    dependencies.append(value)

        return dependencies

    def summarize(self, requirements_text="", pyproject_text=""):
        dependencies = []
        dependencies.extend(self.from_requirements(requirements_text))
        dependencies.extend(self.from_pyproject(pyproject_text))

        return sorted(set(dependencies))

    def read_file(self, path):
        path = Path(path)

        if not path.exists():
            return ""

        try:
            return path.read_text(encoding="utf-8")

        except OSError:
            return ""

