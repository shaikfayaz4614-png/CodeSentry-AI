from app.analyzers.multi_language_analyzer import (
    SUPPORTED_LANGUAGES,
    analyze_code,
    normalize_language,
)


def test_all_advertised_languages_have_an_analyzer():
    samples = {
        "python": "value = 1",
        "javascript": "const value = 1;",
        "typescript": "const value: number = 1;",
        "java": "class Example { int value = 1; }",
        "c": "int main(void) { return 0; }",
        "cpp": "int main() { return 0; }",
        "csharp": "class Example { int value = 1; }",
        "go": "package main\nfunc main() {}",
        "rust": "fn main() {}",
        "php": "<?php $value = 1;",
        "ruby": "value = 1",
        "swift": "let value = 1",
        "kotlin": "fun main() {}",
        "dart": "void main() {}",
        "r": "value <- 1",
        "sql": "SELECT 1;",
        "bash": "value=1",
        "powershell": "$value = 1",
        "html": "<main><p>Ready</p></main>",
        "css": "main { color: red; }",
        "json": '{"value": 1}',
        "lua": "local value = 1",
    }

    assert set(samples) == set(SUPPORTED_LANGUAGES)
    for language, source in samples.items():
        findings, mode = analyze_code(source, language)
        assert isinstance(findings, list)
        assert mode in {"python_ast", "json_parser", "static_heuristics"}


def test_language_aliases_normalize_to_supported_ids():
    assert normalize_language("JS") == "javascript"
    assert normalize_language("c++") == "cpp"
    assert normalize_language("ps1") == "powershell"


def test_javascript_eval_is_reported_as_security_finding():
    findings, mode = analyze_code("const result = eval(input);", "javascript")
    assert mode == "static_heuristics"
    assert any(item["type"] == "security" for item in findings)


def test_invalid_json_is_reported_as_error():
    findings, mode = analyze_code('{"value": }', "json")
    assert mode == "json_parser"
    assert findings[0]["type"] == "error"


def test_unmatched_delimiter_is_reported_for_static_language():
    findings, _ = analyze_code("function run() {", "javascript")
    assert any(item["type"] == "error" for item in findings)
