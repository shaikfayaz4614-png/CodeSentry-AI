
from app.analyzers.python_analyzer import analyze_python_code


def test_detect_unsafe_eval():
    code = """
result = eval("10 + 20")
"""
    findings = analyze_python_code(code)

    assert any(
        finding["type"] == "security"
        for finding in findings
    )


def test_detect_bare_except():
    code = """
try:
    print("Hello")
except:
    pass
"""
    findings = analyze_python_code(code)

    assert any(
        "Bare except" in finding["message"]
        for finding in findings
    )


def test_detect_mutable_default():
    code = """
def add_item(items=[]):
    items.append(10)
    return items
"""
    findings = analyze_python_code(code)

    assert any(
        "Mutable default argument" in finding["message"]
        for finding in findings
    )


def test_detect_division_by_zero_risk():
    code = """
def calculate(numbers):
    return sum(numbers) / len(numbers)
"""
    findings = analyze_python_code(code)

    assert any(
        "division by zero" in finding["message"].lower()
        for finding in findings
    )


def test_empty_collection_guard():
    code = """
def calculate(numbers):
    if not numbers:
        return None

    return sum(numbers) / len(numbers)
"""
    findings = analyze_python_code(code)

    assert not any(
        "division by zero" in finding["message"].lower()
        for finding in findings
    )


def test_detect_syntax_error():
    code = """
def calculate(
    print("Hello")
"""
    findings = analyze_python_code(code)

    assert findings[0]["type"] == "error"
