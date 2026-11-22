# CodeSentry AI – AI-Powered Code Review & Bug Detection System

CodeSentry AI is an AI-powered code review and bug detection platform designed to identify potential programming errors, security vulnerabilities, and code-quality issues.

It combines static code analysis with a local Large Language Model (LLM) to provide code explanations, recommendations, and AI-generated fixes.

## Features

- **Static Code Analysis:** Detects common Python programming issues using Python AST.
- **AI Code Review:** Uses Ollama and Qwen2.5-Coder to explain bugs, security risks, and code improvements.
- **AI Code Fixer:** Generates corrected source code.
- **Code Preview:** Preview, copy, and apply AI-generated fixes.
- **Quality Score:** Displays an estimated code-quality score based on detected findings.
- **Automated Testing:** Includes pytest tests for analyzer functionality.

## Technology Stack

| Component | Technology |
|---|---|
| Frontend | React, Vite |
| Code Editor | Monaco Editor |
| Backend | Python, FastAPI |
| Static Analysis | Python AST |
| AI Model Runtime | Ollama |
| AI Model | Qwen2.5-Coder |
| Testing | Pytest |

## Project Structure

```text
CodeSentry-AI/
├── backend/
│   ├── app/
│   │   ├── analyzers/
│   │   └── main.py
│   ├── tests/
│   └── requirements.txt
├── frontend/
│   ├── src/
│   └── package.json
├── .gitignore
└── README.md
```

## Installation and Setup

### 1. Clone the repository

```bash
git clone YOUR_GITHUB_REPOSITORY_URL
cd CodeSentry-AI
```

### 2. Set up the backend

```bash
cd backend
python -m venv .venv
```

Activate the environment on Windows:

```powershell
.\.venv\Scripts\Activate.ps1
```

Install dependencies:

```bash
pip install -r requirements.txt
pip install pytest
```

Start FastAPI:

```bash
uvicorn app.main:app --reload --port 8000
```

Backend documentation:

http://127.0.0.1:8000/docs

### 3. Set up Ollama

Install Ollama and download the model:

```bash
ollama pull qwen2.5-coder:3b
```

Keep Ollama running while using the AI features.

### 4. Set up the frontend

Open another terminal:

```bash
cd frontend
npm install
npm run dev
```

Open the local URL displayed by Vite in your browser.

## Run Automated Tests

From the backend directory:

```bash
python -m pytest tests/test_analyzer.py -v
```

## Current Limitations

- Static AST-based analysis currently targets Python code.
- AI-generated fixes should be reviewed and tested before use.
- The quality score is an estimate based on detected findings.
- AI features require a locally running Ollama model.

## Future Enhancements

- Java and C static analysis.
- Automated execution and validation of corrected code in a sandbox.
- GitHub integration for pull-request reviews.
- More advanced security vulnerability detection.
- Improved control-flow analysis to reduce false positives.

## Author

**Shaik Fayaz**

B.Tech – Computer Science and Engineering

## Project Status

Core development and initial automated testing completed.