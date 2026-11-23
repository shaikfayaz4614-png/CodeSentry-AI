"""Lightweight static checks for common languages without running user code."""

import json
import re

from app.analyzers.python_analyzer import analyze_python_code


SUPPORTED_LANGUAGES = {
    "python": {"label": "Python", "extension": "py", "monaco": "python"},
    "javascript": {"label": "JavaScript", "extension": "js", "monaco": "javascript"},
    "typescript": {"label": "TypeScript", "extension": "ts", "monaco": "typescript"},
    "java": {"label": "Java", "extension": "java", "monaco": "java"},
    "c": {"label": "C", "extension": "c", "monaco": "c"},
    "cpp": {"label": "C++", "extension": "cpp", "monaco": "cpp"},
    "csharp": {"label": "C#", "extension": "cs", "monaco": "csharp"},
    "go": {"label": "Go", "extension": "go", "monaco": "go"},
    "rust": {"label": "Rust", "extension": "rs", "monaco": "rust"},
    "php": {"label": "PHP", "extension": "php", "monaco": "php"},
    "ruby": {"label": "Ruby", "extension": "rb", "monaco": "ruby"},
    "swift": {"label": "Swift", "extension": "swift", "monaco": "swift"},
    "kotlin": {"label": "Kotlin", "extension": "kt", "monaco": "kotlin"},
    "dart": {"label": "Dart", "extension": "dart", "monaco": "dart"},
    "r": {"label": "R", "extension": "r", "monaco": "r"},
    "sql": {"label": "SQL", "extension": "sql", "monaco": "sql"},
    "bash": {"label": "Bash", "extension": "sh", "monaco": "shell"},
    "powershell": {"label": "PowerShell", "extension": "ps1", "monaco": "powershell"},
    "html": {"label": "HTML", "extension": "html", "monaco": "html"},
    "css": {"label": "CSS", "extension": "css", "monaco": "css"},
    "json": {"label": "JSON", "extension": "json", "monaco": "json"},
    "lua": {"label": "Lua", "extension": "lua", "monaco": "lua"},
}

LANGUAGE_ALIASES = {
    "py": "python",
    "js": "javascript",
    "jsx": "javascript",
    "ts": "typescript",
    "tsx": "typescript",
    "c++": "cpp",
    "cc": "cpp",
    "cxx": "cpp",
    "c#": "csharp",
    "cs": "csharp",
    "golang": "go",
    "rs": "rust",
    "rb": "ruby",
    "kt": "kotlin",
    "kts": "kotlin",
    "sh": "bash",
    "shell": "bash",
    "ps1": "powershell",
}

_DELIMITERS = {"(": ")", "[": "]", "{": "}"}
_UNSAFE_PATTERNS = (
    re.compile(r"\beval\s*\(", re.IGNORECASE),
    re.compile(r"\b(?:exec|execSync|spawnSync)\s*\(", re.IGNORECASE),
    re.compile(r"\b(?:os\s*\.\s*system|shell_exec|passthru|popen)\s*\(", re.IGNORECASE),
    re.compile(r"\bRuntime\s*\.\s*getRuntime\s*\(\s*\)\s*\.\s*exec\s*\(", re.IGNORECASE),
)
_SECRET_PATTERN = re.compile(
    r"\b(password|passwd|api[_-]?key|secret|access[_-]?token)\b\s*[:=]\s*['\"]([^'\"]{6,})['\"]",
    re.IGNORECASE,
)
_WEAK_CRYPTO_PATTERN = re.compile(r"\b(?:md5|sha1)\s*\(", re.IGNORECASE)
_DIVIDE_BY_ZERO_PATTERN = re.compile(r"/\s*0(?![\w.])")


def normalize_language(language: str) -> str:
    normalized = (language or "").strip().lower()
    return LANGUAGE_ALIASES.get(normalized, normalized)


def _finding(issue_type: str, severity: str, message: str, line: int, suggestion: str) -> dict:
    return {
        "type": issue_type,
        "severity": severity,
        "message": message,
        "line": line,
        "suggestion": suggestion,
    }


def _check_balanced_delimiters(code: str, language: str) -> list[dict]:
    """Catch obvious bracket mismatches while ignoring strings and comments."""
    findings = []
    stack = []
    quote = None
    escaped = False
    block_comment = False
    line = 1
    index = 0
    hash_comments = {"bash", "powershell", "ruby", "r", "lua"}
    supports_line_comments = language not in {"html", "json"}

    while index < len(code):
        char = code[index]
        next_two = code[index:index + 2]
        next_four = code[index:index + 4]

        if char == "\n":
            line += 1
            escaped = False
            index += 1
            continue

        if language == "html" and next_four == "<!--":
            end = code.find("-->", index + 4)
            if end < 0:
                break
            line += code[index:end + 3].count("\n")
            index = end + 3
            continue

        if language == "powershell" and next_two == "<#":
            block_comment = True
            index += 2
            continue
        if block_comment:
            if (language == "powershell" and next_two == "#>") or (language != "powershell" and next_two == "*/"):
                block_comment = False
                index += 2
            else:
                index += 1
            continue

        if quote:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == quote:
                quote = None
            index += 1
            continue

        if char in {"'", '"', "`"}:
            quote = char
            index += 1
            continue

        if next_two == "/*":
            block_comment = True
            index += 2
            continue
        if supports_line_comments and next_two == "//":
            end = code.find("\n", index + 2)
            index = len(code) if end < 0 else end
            continue
        if char == "#" and language in hash_comments:
            end = code.find("\n", index + 1)
            index = len(code) if end < 0 else end
            continue
        if language == "sql" and next_two == "--":
            end = code.find("\n", index + 2)
            index = len(code) if end < 0 else end
            continue

        if char in _DELIMITERS:
            stack.append((char, line))
        elif char in _DELIMITERS.values():
            if not stack or _DELIMITERS[stack[-1][0]] != char:
                findings.append(_finding(
                    "error", "high", f"Unexpected closing delimiter '{char}'.", line,
                    "Check that opening and closing brackets match.",
                ))
                return findings
            stack.pop()
        index += 1

    if stack:
        opening, opening_line = stack[-1]
        findings.append(_finding(
            "error", "high", f"Unclosed delimiter '{opening}'.", opening_line,
            "Add the matching closing bracket and check the surrounding block.",
        ))
    return findings


def _analyze_json(code: str) -> list[dict]:
    try:
        json.loads(code)
        return []
    except json.JSONDecodeError as error:
        return [_finding(
            "error", "high", f"Invalid JSON: {error.msg}.", error.lineno,
            "Check commas, quotes, and brackets around this line.",
        )]


def _analyze_heuristics(code: str, language: str) -> list[dict]:
    findings = _check_balanced_delimiters(code, language)
    lines = code.splitlines()

    for line_number, line in enumerate(lines, 1):
        for pattern in _UNSAFE_PATTERNS:
            match = pattern.search(line)
            if match:
                findings.append(_finding(
                    "security", "high",
                    "Potentially unsafe dynamic code or command execution.", line_number,
                    "Avoid evaluating untrusted input or passing it to shell execution. Use safe APIs and validated arguments.",
                ))
                break

        if _SECRET_PATTERN.search(line):
            findings.append(_finding(
                "security", "high", "Possible hard-coded credential or secret.", line_number,
                "Load credentials from environment variables or a dedicated secret store.",
            ))

        if _WEAK_CRYPTO_PATTERN.search(line):
            findings.append(_finding(
                "security", "medium", "MD5 or SHA-1 may be unsuitable for security-sensitive hashing.", line_number,
                "Use a modern hash such as SHA-256 for integrity, or a password hashing function such as Argon2 or bcrypt.",
            ))

        if _DIVIDE_BY_ZERO_PATTERN.search(line):
            findings.append(_finding(
                "bug", "medium", "Possible division by zero.", line_number,
                "Validate that the divisor is non-zero before performing this division.",
            ))

        if language in {"javascript", "typescript", "java", "csharp", "go", "rust", "php", "swift", "kotlin", "dart"}:
            if re.search(r"\bcatch\s*\([^)]*\)\s*\{\s*\}", line):
                findings.append(_finding(
                    "warning", "medium", "Empty catch block silently discards an error.", line_number,
                    "Handle the error, add useful logging, or remove the catch block.",
                ))

        if language == "sql" and re.search(r"\b(?:SELECT|UPDATE|DELETE)\b.*\+\s*\w+", line, re.IGNORECASE):
            findings.append(_finding(
                "security", "high", "SQL statement may be built by concatenating input.", line_number,
                "Use parameterized queries instead of concatenating values into SQL.",
            ))

    return findings


def analyze_code(code: str, language: str) -> tuple[list[dict], str]:
    normalized = normalize_language(language)
    if normalized == "python":
        return analyze_python_code(code), "python_ast"
    if normalized == "json":
        return _analyze_json(code), "json_parser"
    return _analyze_heuristics(code, normalized), "static_heuristics"
