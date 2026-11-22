
import { useState } from "react";
import Editor from "@monaco-editor/react";
import {
  ShieldCheck,
  Code2,
  LayoutDashboard,
  History,
  Settings,
  Search,
  Bell,
  Play,
  Bug,
  ShieldAlert,
  Zap,
  CheckCircle2,
  AlertTriangle,
  FileCode2,
  ChevronDown,
  Sparkles,
  Clock3,
  Activity,
  Menu,
  X,
  Copy,
  WandSparkles
} from "lucide-react";
import "./App.css";

const initialCode = `def calculate_average(numbers):
    total = 0

    for number in numbers:
        total += number

    average = total / len(numbers)
    return average


numbers = [10, 20, 30, 40]
result = calculate_average(numbers)

print("Average:", result)
`;

function App() {
  const [code, setCode] = useState(initialCode);
  const [language, setLanguage] = useState("python");
  const [analyzed, setAnalyzed] = useState(false);
  const [loading, setLoading] = useState(false);
  const [mobileMenu, setMobileMenu] = useState(false);
  const [results, setResults] = useState(null);
  const [apiError, setApiError] = useState("");

  // AI Review states
  const [aiReview, setAiReview] = useState("");
  const [aiLoading, setAiLoading] = useState(false);
  const [aiError, setAiError] = useState("");

  // AI Fix states
  const [correctedCode, setCorrectedCode] = useState("");
  const [fixLoading, setFixLoading] = useState(false);
  const [fixError, setFixError] = useState("");
  const [showPreview, setShowPreview] = useState(false);
  const [copyMessage, setCopyMessage] = useState("");

  // Static code analysis
  const handleAnalyze = async () => {
    setLoading(true);
    setAnalyzed(false);
    setResults(null);
    setApiError("");

    try {
      const response = await fetch(
        "http://127.0.0.1:8000/api/analyze",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json"
          },
          body: JSON.stringify({
            code: code,
            language: language
          })
        }
      );

      if (!response.ok) {
        throw new Error(`Server error: ${response.status}`);
      }

      const data = await response.json();

      if (!data.success) {
        throw new Error(
          data.message || "Analysis could not be completed."
        );
      }

      setResults(data);
      setAnalyzed(true);

    } catch (error) {
      setApiError(
        error.message === "Failed to fetch"
          ? "Cannot connect to backend. Make sure FastAPI is running on port 8000."
          : error.message
      );

    } finally {
      setLoading(false);
    }
  };

  // AI-powered code review
  const handleAIReview = async () => {
    if (!code.trim()) return;

    setAiLoading(true);
    setAiReview("");
    setAiError("");

    try {
      const response = await fetch(
        "http://127.0.0.1:8000/api/ai-review",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json"
          },
          body: JSON.stringify({
            code: code,
            language: language
          })
        }
      );

      if (!response.ok) {
        throw new Error(`Server error: ${response.status}`);
      }

      const data = await response.json();

      if (!data.success) {
        throw new Error(data.message || "AI review failed.");
      }

      setAiReview(
        data.review || "The AI returned an empty review."
      );

    } catch (error) {
      setAiError(
        error.message === "Failed to fetch"
          ? "Cannot connect to backend. Make sure FastAPI and Ollama are running."
          : error.message
      );

    } finally {
      setAiLoading(false);
    }
  };

  // AI code fixer
  const handleAIFix = async () => {
    if (!code.trim()) return;

    setFixLoading(true);
    setCorrectedCode("");
    setFixError("");
    setCopyMessage("");
    setShowPreview(false);

    try {
      const response = await fetch(
        "http://127.0.0.1:8000/api/ai-fix",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json"
          },
          body: JSON.stringify({
            code: code,
            language: language
          })
        }
      );

      if (!response.ok) {
        throw new Error(`Server error: ${response.status}`);
      }

      const data = await response.json();

      if (!data.success) {
        throw new Error(
          data.message || "AI code fixing failed."
        );
      }

      if (!data.corrected_code) {
        throw new Error("No corrected code was returned.");
      }

      setCorrectedCode(data.corrected_code);
      setShowPreview(true);

    } catch (error) {
      setFixError(
        error.message === "Failed to fetch"
          ? "Cannot connect to backend. Check FastAPI and Ollama."
          : error.message
      );

    } finally {
      setFixLoading(false);
    }
  };

  // Copy corrected code
  const handleCopyFix = async () => {
    try {
      await navigator.clipboard.writeText(correctedCode);
      setCopyMessage("Code copied successfully!");
    } catch (error) {
      setFixError(
        "Unable to copy code. Please select and copy it manually."
      );
    }
  };

  // Apply corrected code to Monaco editor
  const handleApplyFix = () => {
    if (!correctedCode) return;

    setCode(correctedCode);
    setShowPreview(false);

    setAnalyzed(false);
    setResults(null);
    setApiError("");

    setAiReview("");
    setAiError("");

    setFixError("");
    setCopyMessage("");
  };

  // Calculate issue counts
  const findings = results?.findings || [];

  const securityCount = findings.filter(
    (item) => item.type === "security"
  ).length;

  const warningCount = findings.filter(
    (item) => item.type === "warning"
  ).length;

  const bugCount = findings.filter(
    (item) =>
      item.type === "bug" || item.type === "error"
  ).length;

  const qualityScore = Math.max(
    0,
    100 -
      findings.reduce((score, finding) => {
        if (finding.severity === "high") return score + 20;
        if (finding.severity === "medium") return score + 10;
        if (finding.severity === "low") return score + 5;
        return score;
      }, 0)
  );

  return (
    <div className="app-container">

      {/* Sidebar */}
      <aside
        className={`sidebar ${mobileMenu ? "mobile-open" : ""}`}
      >
        <div className="brand">
          <div className="brand-icon">
            <ShieldCheck size={25} />
          </div>

          <div>
            <h2>
              CodeSentry<span> AI</span>
            </h2>
            <p>INTELLIGENT CODE REVIEW</p>
          </div>

          <button
            className="close-menu"
            onClick={() => setMobileMenu(false)}
          >
            <X size={20} />
          </button>
        </div>

        <div className="workspace-label">WORKSPACE</div>

        <nav className="navigation">
          <button className="nav-item active">
            <LayoutDashboard size={19} />
            Dashboard
          </button>

          <button className="nav-item">
            <Code2 size={19} />
            Code Review
          </button>

          <button className="nav-item">
            <History size={19} />
            Review History
          </button>

          <button className="nav-item">
            <ShieldAlert size={19} />
            Security Scanner
          </button>
        </nav>

        <div className="sidebar-bottom">
          <div className="upgrade-card">
            <Sparkles size={20} />
            <h3>Developer workspace</h3>
            <p>Your intelligent code review environment.</p>
          </div>

          <button className="nav-item">
            <Settings size={19} />
            Settings
          </button>

          <div className="profile">
            <div className="avatar">S</div>
            <div>
              <h4>Developer</h4>
              <p>Free workspace</p>
            </div>
          </div>
        </div>
      </aside>

      {/* Main Content */}
      <main className="main-content">

        {/* Topbar */}
        <header className="topbar">
          <button
            className="mobile-toggle"
            onClick={() => setMobileMenu(!mobileMenu)}
          >
            <Menu size={22} />
          </button>

          <div className="breadcrumb">
            Workspace <span>/</span> Code Review
          </div>

          <div className="topbar-actions">
            <button className="icon-button">
              <Search size={19} />
            </button>

            <button className="icon-button">
              <Bell size={19} />
              <span className="notification-dot"></span>
            </button>

            <div className="top-avatar">S</div>
          </div>
        </header>

        <section className="dashboard">

          {/* Welcome Section */}
          <div className="welcome-section">
            <div>
              <div className="eyebrow">
                <Sparkles size={15} />
                AI-POWERED DEVELOPMENT
              </div>

              <h1>
                Code Review <span>Workspace</span>
              </h1>

              <p>
                Analyze your code, discover issues and improve code quality.
              </p>
            </div>

            <div className="system-status">
              <span className="status-dot"></span>
              Workspace ready
            </div>
          </div>

          {/* Statistics */}
          <div className="stats-grid">

            <div className="stat-card">
              <div className="stat-top">
                <span>Total Reviews</span>
                <div className="stat-icon purple">
                  <FileCode2 size={19} />
                </div>
              </div>

              <h2>{analyzed ? "1" : "0"}</h2>
              <p>Reviews in this session</p>
            </div>

            <div className="stat-card">
              <div className="stat-top">
                <span>Issues Found</span>
                <div className="stat-icon orange">
                  <Bug size={19} />
                </div>
              </div>

              <h2>
                {analyzed ? results.total_issues : "0"}
              </h2>

              <p>Issues detected by backend</p>
            </div>

            <div className="stat-card">
              <div className="stat-top">
                <span>Security Alerts</span>
                <div className="stat-icon red">
                  <ShieldAlert size={19} />
                </div>
              </div>

              <h2>
                {analyzed ? securityCount : "0"}
              </h2>

              <p>Security issues detected</p>
            </div>

            <div className="stat-card">
              <div className="stat-top">
                <span>Code Quality</span>
                <div className="stat-icon green">
                  <Activity size={19} />
                </div>
              </div>

              <h2>
                {analyzed ? qualityScore : "--"}
                <small>/100</small>
              </h2>

              <p>
                {analyzed
                  ? "Estimated quality score"
                  : "Run analysis to calculate"}
              </p>
            </div>

          </div>

          {/* Editor Heading and Action Buttons */}
          <div className="editor-heading">
            <div>
              <h2>
                <Code2 size={20} />
                Code Analyzer
              </h2>

              <p>
                Write or paste your source code to begin reviewing.
              </p>
            </div>

            <button
              className="analyze-button"
              onClick={handleAnalyze}
              disabled={loading || !code.trim()}
            >
              {loading ? (
                <>Analyzing...</>
              ) : (
                <>
                  <Play size={16} fill="currentColor" />
                  Analyze Code
                </>
              )}
            </button>

            <button
              className="ai-review-button"
              onClick={handleAIReview}
              disabled={aiLoading || !code.trim()}
            >
              <Sparkles size={16} />
              {aiLoading ? "AI Reviewing..." : "AI Review"}
            </button>

            <button
              className="ai-fix-button"
              onClick={handleAIFix}
              disabled={fixLoading || !code.trim()}
            >
              <WandSparkles size={16} />
              {fixLoading ? "Fixing Code..." : "AI Fix"}
            </button>
          </div>

          {/* Workspace */}
          <div className="workspace-grid">

            {/* Code Editor */}
            <div className="editor-card">
              <div className="editor-toolbar">

                <div className="file-name">
                  <FileCode2 size={17} />

                  main.
                  {language === "python"
                    ? "py"
                    : language === "java"
                    ? "java"
                    : "c"}

                  <span className="unsaved-dot"></span>
                </div>

                <div className="language-select">
                  <select
                    value={language}
                    onChange={(e) => {
                      setLanguage(e.target.value);
                      setAnalyzed(false);
                      setResults(null);
                      setApiError("");
                      setAiReview("");
                      setAiError("");
                      setCorrectedCode("");
                      setShowPreview(false);
                      setFixError("");
                    }}
                  >
                    <option value="python">Python</option>
                    <option value="java">Java</option>
                    <option value="c">C</option>
                  </select>

                  <ChevronDown size={14} />
                </div>

              </div>

              <div className="monaco-container">
                <Editor
                  height="420px"
                  language={language}
                  theme="vs-dark"
                  value={code}
                  onChange={(value) => {
                    setCode(value || "");
                    setAnalyzed(false);
                    setResults(null);
                    setApiError("");
                    setAiReview("");
                    setAiError("");
                    setCorrectedCode("");
                    setShowPreview(false);
                    setFixError("");
                    setCopyMessage("");
                  }}
                  options={{
                    minimap: { enabled: false },
                    fontSize: 14,
                    lineNumbers: "on",
                    scrollBeyondLastLine: false,
                    automaticLayout: true,
                    padding: { top: 18 },
                    fontFamily: "Consolas, monospace",
                    wordWrap: "on"
                  }}
                />
              </div>

              <div className="editor-footer">
                <span>
                  <Code2 size={14} />
                  {language.toUpperCase()}
                </span>

                <span>
                  UTF-8 &nbsp; | &nbsp; {code.split("\n").length} lines
                </span>
              </div>
            </div>

            {/* Review Results */}
            <div className="review-card">

              <div className="review-header">
                <div>
                  <h3>
                    <Sparkles size={18} />
                    Review Results
                  </h3>

                  <p>Code analysis overview</p>
                </div>

                <span className="ai-badge">LIVE API</span>
              </div>

              {apiError ? (

                <div className="empty-state">
                  <div className="empty-icon">
                    <AlertTriangle size={30} />
                  </div>

                  <h3>Analysis failed</h3>
                  <p>{apiError}</p>
                </div>

              ) : !analyzed ? (

                <div className="empty-state">
                  <div className="empty-icon">
                    <Zap size={30} />
                  </div>

                  <h3>Ready to analyze</h3>

                  <p>
                    Your code review results will appear here after
                    you start an analysis.
                  </p>

                  <div className="review-tip">
                    <Sparkles size={16} />
                    Tip: Write clean, readable code for better analysis.
                  </div>
                </div>

              ) : (

                <div className="results-content">

                  <div className="result-score">
                    <div className="score-circle">
                      {results.total_issues}
                    </div>

                    <div>
                      <h3>Analysis completed</h3>
                      <p>
                        {results.total_issues} issue(s) detected
                      </p>
                    </div>
                  </div>

                  <div className="issue-summary">

                    <div>
                      <Bug size={17} />
                      Bugs / Errors
                      <strong>{bugCount}</strong>
                    </div>

                    <div>
                      <ShieldAlert size={17} />
                      Security alerts
                      <strong>{securityCount}</strong>
                    </div>

                    <div>
                      <AlertTriangle size={17} />
                      Warnings
                      <strong>{warningCount}</strong>
                    </div>

                  </div>

                  {findings.length === 0 ? (

                    <div className="finding-success">
                      <CheckCircle2 size={17} />
                      No issues detected by the current analyzer.
                    </div>

                  ) : (

                    findings.map((finding, index) => (

                      <div className="finding" key={index}>

                        <span className="finding-label">
                          {finding.severity.toUpperCase()}
                          {" · "}
                          {finding.type.toUpperCase()}
                        </span>

                        <h4>{finding.message}</h4>

                        <p>
                          <strong>Recommended fix:</strong>
                          {" "}
                          {finding.suggestion ||
                            "Review this issue and update your code."}
                        </p>

                        <span className="line-reference">
                          Line {finding.line ?? "Unknown"}
                        </span>

                      </div>

                    ))

                  )}

                  <div className="finding-success">
                    <CheckCircle2 size={17} />
                    Live backend analysis completed successfully.
                  </div>

                </div>

              )}

            </div>
          </div>

          {/* AI Review Results */}
          <div className="ai-review-card">
            <div className="ai-review-header">
              <h2>
                <Sparkles size={20} />
                AI Code Review
              </h2>
              <span>POWERED BY QWEN AI</span>
            </div>

            {aiError && (
              <div className="ai-error">
                {aiError}
              </div>
            )}

            {aiLoading && (
              <div className="ai-loading">
                <Sparkles size={20} />
                AI is reviewing your code. Please wait...
              </div>
            )}

            {!aiLoading && !aiReview && !aiError && (
              <div className="ai-empty">
                Click AI Review to get a code explanation, bug analysis,
                security review and improvement suggestions.
              </div>
            )}

            {aiReview && (
              <div className="ai-review-content">
                <pre>{aiReview}</pre>
              </div>
            )}
          </div>

          {/* AI Fix Preview */}
          {showPreview && correctedCode && (
            <div className="ai-fix-card">

              <div className="ai-fix-header">
                <div>
                  <h2>
                    <WandSparkles size={20} />
                    AI Corrected Code
                  </h2>

                  <p>
                    Review the generated code before applying it.
                  </p>
                </div>

                <span className="ai-fix-badge">
                  AI GENERATED
                </span>
              </div>

              {fixError && (
                <div className="ai-error">
                  {fixError}
                </div>
              )}

              <pre className="ai-fix-code">
                <code>{correctedCode}</code>
              </pre>

              {copyMessage && (
                <p className="copy-success">
                  <CheckCircle2 size={16} />
                  {copyMessage}
                </p>
              )}

              <div className="ai-fix-actions">

                <button
                  className="copy-fix-button"
                  onClick={handleCopyFix}
                >
                  <Copy size={16} />
                  Copy Code
                </button>

                <button
                  className="apply-fix-button"
                  onClick={handleApplyFix}
                >
                  <CheckCircle2 size={16} />
                  Apply Fix to Editor
                </button>

                <button
                  className="close-preview-button"
                  onClick={() => setShowPreview(false)}
                >
                  Close Preview
                </button>

              </div>
            </div>
          )}

          {fixError && !showPreview && (
            <div className="ai-error">
              {fixError}
            </div>
          )}

          {/* Bottom Information */}
          <div className="bottom-info">
            <div>
              <Clock3 size={15} />
              CodeSentry AI · Development Preview
            </div>

            <div>
              <ShieldCheck size={15} />
              Secure code analysis workspace
            </div>
          </div>

        </section>
      </main>
    </div>
  );
}

export default App;
