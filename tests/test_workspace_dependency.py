from workspace.dependency import DependencySummary


def test_dependency_summary_reads_requirements():
    summary = DependencySummary()

    dependencies = summary.from_requirements(
        """
        # comment
        requests
        ollama>=0.5
        """
    )

    assert dependencies == ["requests", "ollama>=0.5"]


def test_dependency_summary_reads_pyproject_dependencies():
    summary = DependencySummary()

    dependencies = summary.from_pyproject(
        """
        [project]
        dependencies = [
            "requests",
            "ollama",
        ]
        """
    )

    assert dependencies == ["requests", "ollama"]


def test_dependency_summary_deduplicates_sources():
    summary = DependencySummary()

    dependencies = summary.summarize("requests\nollama\n", 'dependencies = [\n"requests",\n]')

    assert dependencies == ["ollama", "requests"]

