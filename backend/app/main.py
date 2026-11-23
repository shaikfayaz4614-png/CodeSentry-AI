from app.analyzers.multi_language_analyzer import (
    SUPPORTED_LANGUAGES,
    analyze_code as analyze_source_code,
    normalize_language,
)
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import json
from urllib.request import Request, urlopen
# Create FastAPI application
app = FastAPI(
    title="CodeSentry AI",
    description="AI-Powered Code Review and Bug Detection API",
    version="1.0.0"
)

# Allow communication with React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5175",
        "http://127.0.0.1:5175"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request model
class CodeRequest(BaseModel):
    code: str
    language: str = "python"
class AIReviewRequest(BaseModel):
    code: str
    language: str = "python"

# Home route
@app.get("/")
def home():
    return {
        "message": "Welcome to CodeSentry AI API",
        "status": "running"
    }


# Health check
@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "service": "CodeSentry AI Backend"
    }


@app.get("/api/languages")
def supported_languages():
    return {
        "languages": [
            {"id": key, **details}
            for key, details in SUPPORTED_LANGUAGES.items()
        ],
        "analysis_modes": {
            "python": "Python AST analysis",
            "json": "JSON parser validation",
            "other": "Static heuristic checks; source code is not executed",
        },
    }


# Analyze code

@app.post("/api/analyze")
def analyze_code(request: CodeRequest):
    code = request.code
    language = normalize_language(request.language)

    # Check empty code
    if not code.strip():
        return {
            "success": False,
            "message": "Please provide source code.",
            "findings": []
        }

    if language not in SUPPORTED_LANGUAGES:
        return {
            "success": False,
            "message": "This language is not supported yet.",
            "findings": [],
            "supported_languages": list(SUPPORTED_LANGUAGES),
        }

    findings, analysis_mode = analyze_source_code(code, language)

    return {
        "success": True,
        "language": language,
        "language_label": SUPPORTED_LANGUAGES[language]["label"],
        "analysis_mode": analysis_mode,
        "total_issues": len(findings),
        "findings": findings
    }
@app.post("/api/ai-review")
def ai_review(request: AIReviewRequest):

    if not request.code.strip():
        return {
            "success": False,
            "message": "Please provide code to review."
        }

    prompt = f"""
You are CodeSentry AI, an expert software engineer and code reviewer.

Review the following {request.language} code.

Provide your response using these sections:

1. CODE EXPLANATION
Explain what the code does in simple language.

2. BUGS AND ERRORS
Identify possible bugs and explain why they are problems.

3. SECURITY ANALYSIS
Identify security vulnerabilities, if any.

4. CODE QUALITY
Evaluate readability, performance and maintainability.

5. RECOMMENDED IMPROVEMENTS
Suggest specific improvements.

6. CORRECTED CODE
Provide an improved version of the code.

If no issue is found in a section, clearly say so.
Do not claim that code has been executed or tested.

CODE:
{request.code}
"""

    payload = {
        "model": "qwen2.5-coder:3b",
        "prompt": prompt,
        "stream": False
    }

    try:
        data = json.dumps(payload).encode("utf-8")

        ollama_request = Request(
            "http://127.0.0.1:11434/api/generate",
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST"
        )

        with urlopen(ollama_request, timeout=180) as response:
            result = json.loads(response.read().decode("utf-8"))

        return {
            "success": True,
            "review": result.get("response", "")
        }

    except Exception as error:
        return {
            "success": False,
            "message": f"AI review failed: {str(error)}"
        }
    
@app.post("/api/ai-fix")
def ai_fix(request: AIReviewRequest):

    if not request.code.strip():
        return {
            "success": False,
            "message": "Please provide code to fix."
        }

    prompt = f"""
You are an expert software engineer.

Fix the bugs and improve the following {request.language} code.

Requirements:
- Preserve the original functionality.
- Fix errors and potential bugs.
- Improve readability where appropriate.
- Do not include explanations or Markdown.
- Return only the complete corrected source code.
- Do not invent missing requirements.

Original code:

{request.code}
"""

    payload = {
        "model": "qwen2.5-coder:3b",
        "prompt": prompt,
        "stream": False
    }

    try:
        data = json.dumps(payload).encode("utf-8")

        ollama_request = Request(
            "http://127.0.0.1:11434/api/generate",
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST"
        )

        with urlopen(ollama_request, timeout=180) as response:
            result = json.loads(
                response.read().decode("utf-8")
            )

        corrected_code = result.get("response", "").strip()

        if not corrected_code:
            return {
                "success": False,
                "message": "The AI did not generate corrected code."
            }

        # Remove Markdown code fences if the model includes them.
        if corrected_code.startswith("```"):
            lines = corrected_code.splitlines()

            if lines and lines[0].startswith("```"):
                lines = lines[1:]

            if lines and lines[-1].strip() == "```":
                lines = lines[:-1]

            corrected_code = "\n".join(lines).strip()

        return {
            "success": True,
            "corrected_code": corrected_code
        }

    except Exception as error:
        return {
            "success": False,
            "message": f"AI code fixing failed: {str(error)}"
        }
