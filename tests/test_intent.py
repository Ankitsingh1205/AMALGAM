from brain.intent.intent import IntentAnalyzer


def test_detects_math_expression():
    intent = IntentAnalyzer()

    assert intent.detect("144 * 82") == "math"


def test_detects_coding_request():
    intent = IntentAnalyzer()

    assert intent.detect("Write Python code") == "coding"


def test_defaults_to_general_intent():
    intent = IntentAnalyzer()

    assert intent.detect("Who are you?") == "general"

def test_detects_project_request():
    intent = IntentAnalyzer()

    assert intent.detect("Explain my project") == "project"

