<!--
  AGENTIC CODE FIXER - README
  Theme Palette:
    - Primary Cyan:   #06B6D4
    - Deep Purple:    #8B5CF6
    - Emerald Green:  #10B981
    - Dark Slate:     #0F172A
-->

<!-- PROJECT BANNER -->
<p align="center">
  <img src="assets/banner.jpg" alt="Agentic Code Fixer Banner" width="100%" style="border-radius: 12px; box-shadow: 0 8px 24px rgba(0,0,0,0.3);">
</p>

<h1 align="center">⚡ Agentic Code Fixer</h1>

<p align="center">
  <b>An Autonomous Multi-Agent Code Generation, Execution & Self-Correction Pipeline built with LangGraph</b>
</p>

<p align="center">
  <a href="#-badges--status"><img src="https://img.shields.io/badge/Version-v1.0--submission-06B6D4?style=for-the-badge&logo=git&logoColor=white" alt="Version"></a>
  <a href="https://python.org"><img src="https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python"></a>
  <a href="https://langchain-ai.github.io/langgraph/"><img src="https://img.shields.io/badge/LangGraph-StateGraph-8B5CF6?style=for-the-badge&logo=langchain&logoColor=white" alt="LangGraph"></a>
  <a href="https://groq.com"><img src="https://img.shields.io/badge/LLM-Groq%20%2F%20Gemini-10B981?style=for-the-badge&logo=openai&logoColor=white" alt="LLM Provider"></a>
  <a href="#-verification--tests"><img src="https://img.shields.io/badge/Tests-40%2F40%20Passing-brightgreen?style=for-the-badge&logo=pytest&logoColor=white" alt="Tests"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-6366F1?style=for-the-badge" alt="License"></a>
</p>

---

<!-- RESULTS SUMMARY -->
<p align="center">
  <img src="https://img.shields.io/badge/Specs%20Solved-8%20%2F%208-10B981?style=for-the-badge" alt="8/8 Specs">
  <img src="https://img.shields.io/badge/Tests%20Passing-40%20%2F%2040-10B981?style=for-the-badge&logo=pytest&logoColor=white" alt="40/40 Tests">
  <img src="https://img.shields.io/badge/Refactor%20Passes%20Kept-8%20%2F%208-8B5CF6?style=for-the-badge" alt="Refactored">
  <img src="https://img.shields.io/badge/Unhandled%20Failures-0-06B6D4?style=for-the-badge" alt="0 Failures">
</p>

<blockquote>
<p align="center">
  <b>🏆 Final Result:</b> All 8 specs autonomously solved · 40/40 unit tests passing · Every refactor pass kept · Zero sandbox timeouts or crashes<br>
  Self-correction mechanisms verified via <code>tests/test_refactor_node.py</code> (discard-on-regression) and <code>tests/test_retry_loop.py</code> (retry router).<br>
  Full evidence: <a href="traces/final_run/"><code>traces/final_run/</code></a> · Self-evaluation: <a href="docs/self_eval.md"><code>docs/self_eval.md</code></a> · Demo walkthrough: <a href="docs/demo_script.md"><code>docs/demo_script.md</code></a>
</p>
</blockquote>

---

## 📌 Table of Contents

<p align="center">
  <a href="#-results-summary">Results</a> •
  <a href="#-overview">Overview</a> •
  <a href="#-key-architecture">Key Architecture</a> •
  <a href="#-curated-problem-specs">Curated Specs</a> •
  <a href="#-quick-start">Quick Start</a> •
  <a href="#-web-ui-extension">Web UI</a> •
  <a href="#-demo">Demo</a> •
  <a href="#-observability--tracing">Observability</a> •
  <a href="#-repository-structure">Repo Structure</a> •
  <a href="#-state-schema-technical-reference-click-to-expand">State Schema</a> •
  <a href="#-author--license">Author & License</a>
</p>

---

## 🎯 Overview

**Agentic Code Fixer** is an 8-week structured project implementing a closed-loop multi-agent system designed to plan, generate, evaluate, and refactor Python function implementations autonomously.

Rather than relying on single-shot LLM prompts, the architecture models code synthesis as a state-machine graph (using **LangGraph**). When generated code fails unit tests, error tracebacks are fed back into the agentic loop to perform target-driven self-correction.

```text
[ Function Spec ] ➔ ( Planner Node ) ➔ ( Coder Node ) ➔ ( Tester Node ) ➔ [ Passed / Refactored Code ]
                                               ▲                  │
                                               └─ (Retry Loop) ───┘ (if tests fail & count < 3)
```

---

## 🛠️ Key Architecture

The core graph connects distinct functional roles via shared typed state (`AgentState`). Below is the system flow and conditional control topology:

```mermaid
flowchart TD
    classDef startNode fill:#0F172A,stroke:#06B6D4,stroke-width:2px,color:#fff;
    classDef agentNode fill:#1E293B,stroke:#8B5CF6,stroke-width:2px,color:#fff;
    classDef passNode fill:#064E3B,stroke:#10B981,stroke-width:2px,color:#fff;
    classDef failNode fill:#7F1D1D,stroke:#EF4444,stroke-width:2px,color:#fff;

    START(["START: Load Spec"]) --> Planner["planner_node: Generate Strategy"]
    Planner --> Coder["coder_node: Generate or Fix Code"]
    Coder --> Tester["tester_node: Execute Pytest Sandbox"]

    Tester -->|"All Tests Passed"| Refactor["refactor_node: Optimize Code"]
    Refactor --> ReTest["Re-Test Refactored Code"]
    ReTest -->|"Passed"| END(["DONE: Solution Verified"])
    ReTest -->|"Regression"| Revert["Revert to Pre-Refactor"] --> END

    Tester -->|"Tests Failed & Count < 3"| Coder
    Tester -->|"Tests Failed & Count >= 3"| FAILED(["FAILED: Max Iterations Exceeded"])

    class START startNode;
    class Planner,Coder,Tester,ReTest agentNode;
    class Refactor,Revert,END passNode;
    class FAILED failNode;
```

### 👥 Agent Node Responsibilities

| Icon | Node | Responsibilities | Output State Field |
| :---: | :--- | :--- | :--- |
| 🧠 | `planner_node` | Analyzes spec constraints, identifies edge cases, selects algorithmic strategy. | `state["plan"]` |
| 💻 | `coder_node` | Writes function implementation matching spec signature & plan guidelines. | `state["code"]` |
| 🧪 | `tester_node` | Runs sandboxed `pytest` execution, extracts pass/fail metrics & tracebacks. | `state["test_results"]` |
| 🎨 | `refactor_node` | Enhances readability & complexity of verified code without regressing logic. | `state["code"]` |

---

## 📚 Curated Problem Specs

The evaluation benchmark contains **8 curated function specifications** spanning classic Data Structures & Algorithms (DSA), each backed by a 5-test reference suite (**40 total ground-truth tests**).

| ID | Problem Title | Algorithmic Category | Reference Tests | Status |
| :---: | :--- | :--- | :---: | :---: |
| `spec_01` | **Two Sum** | Hash Map / Two Pointers | 5 / 5 Passed | `refactored` |
| `spec_02` | **Reverse Linked List** | Pointer Manipulation | 5 / 5 Passed | `refactored` |
| `spec_03` | **Valid Parentheses** | Stack | 5 / 5 Passed | `refactored` |
| `spec_04` | **Merge Intervals** | Sorting / Interval Array | 5 / 5 Passed | `refactored` |
| `spec_05` | **Group Anagrams** | Hash Table / String Categorization | 5 / 5 Passed | `refactored` |
| `spec_06` | **Search in Rotated Sorted Array** | Modified Binary Search | 5 / 5 Passed | `refactored` |
| `spec_07` | **LRU Cache** | Doubly Linked List + Hash Map | 5 / 5 Passed | `refactored` |
| `spec_08` | **Topological Sort** | Graph DAG / Kahn's Algorithm | 5 / 5 Passed | `refactored` |

---

## 📈 Final Results

> Full evaluation run completed across all 8 specs in Week 6. Archive: [`traces/final_run/`](traces/final_run/) · Summary: [`traces/week6_summary.md`](traces/week6_summary.md)

| Metric | Value |
| :--- | :--- |
| Specs Evaluated | **8 / 8** |
| Tests Passing | **40 / 40** |
| Refactor Passes Kept | **8 / 8** |
| Retry Loop Organically Triggered | 0 (all passed first attempt) |
| Average Iterations per Spec | 2 |

---

## ⚡ Demo

Run the full 4-node pipeline on any spec in one command:

```powershell
# Run demo on Two Sum (default)
.\venv\Scripts\python.exe scratch/run_demo.py spec_01

# Run demo on LRU Cache
.\venv\Scripts\python.exe scratch/run_demo.py spec_07
```

The demo prints each stage (`[PLAN]`, `[CODE]`, `[TEST]`, `[REFACTOR]`) as it executes, and exits with code `0` on success, `1` on failure.

### Pre-Demo Environment Check

```powershell
# Verify all 52 environment checks before a live demo
.\venv\Scripts\python.exe scratch/verify_fresh_clone.py
```

---

## 🖥️ Web UI Extension

A Streamlit web interface is available to inspect archived traces and run live specs:

```powershell
# Launch the Streamlit application
.\venv\Scripts\streamlit.exe run ui/app.py
```

### Features:
- **📊 Archived Run Viewer**: Browse all 8 archived DSA specs, review generated plans, inspect side-by-side code diffs (initial vs refactored), and examine unit test logs.
- **⚡ Live Spec Runner**: Trigger live execution on any specification with real-time status updates per pipeline stage (`planner` ➔ `coder` ➔ `tester` ➔ `refactor`).

---

## 🗓️ Week-by-Week Progress

| Week | Focus | Status |
| :---: | :--- | :---: |
| **Week 1** | Environment setup, LangGraph skeleton (`planner→coder→tester`), architecture contract locked | ✅ Done |
| **Week 2** | `planner_node` — structured `PlanOutput` Pydantic model, 8 plans generated & audited | ✅ Done |
| **Week 3** | `coder_node` — regex extraction, AST validation, `tools/file_writer.py`, 8 implementations generated | ✅ Done |
| **Week 4** | `tester_node` — sandboxed `pytest` subprocess, `TestResult` schema, 8/8 specs passing | ✅ Done |
| **Week 5** | Conditional retry loop — `route_after_tester`, failure injection into retry prompt, 8/8 refactored | ✅ Done |
| **Week 6** | `refactor_node` — discard-on-regression safety net, exponential backoff, full 8-spec evaluation run | ✅ Done |
| **Week 7** | Self-evaluation doc (`docs/self_eval.md`), demo script, fresh-clone verifier, README polish | ✅ Done |
---

## 🗓️ Week 8: Project Completion & Final Delivery

<p align="center">
  <img src="https://img.shields.io/badge/Status-Project_Complete-10B981?style=for-the-badge" alt="Complete">
  <img src="https://img.shields.io/badge/Version-v1.0--Final-06B6D4?style=for-the-badge" alt="v1.0">
</p>

<blockquote style="border-left: 4px solid var(--teal-primary); padding-left: 1.5rem; background: rgba(13, 110, 110, 0.05); border-radius: 0 12px 12px 0;">
  <b>🏆 Final Milestone:</b> The Agentic Code Fixer has transitioned from a theoretical skeleton to a fully autonomous, polyglot repair engine. The system now supports end-to-end deployment, real-time API streaming, and verifiable self-correction across multiple programming languages.
</blockquote>

### 🛠️ Final Feature Set
- **Polyglot Repair Engine**: Autonomous diagnosis and fixing for Python and TypeScript/JavaScript.
- **Closed-Loop Verification**: Integration of a sandboxed `pytest` execution environment with automated retry logic.
- **Live API Bridge**: A FastAPI-powered backend allowing the professional Web UI to trigger real agent runs in real-time.
- **Zero-Regression Refactoring**: A specialized `refactor_node` that optimizes code while automatically reverting on any logic regression.
- **Professional Observability**: Full LangSmith integration for node-level tracing and latency analysis.

### 📐 Final Architecture Overview
The system operates as a **StateGraph** directed acyclic graph (DAG) with conditional edges:
`START` $\rightarrow$ `Planner` $\rightarrow$ `Coder` $\rightarrow$ `Tester` $\rightarrow$ `(If Fail $\rightarrow$ Debugger $\rightarrow$ Coder)` $\rightarrow$ `Refactor` $\rightarrow$ `END`.

### 🚀 Deployment & Execution
**Quick-start for production:**
1. **Backend**: Deploy `ui/api_server.py` to Render/Railway.
2. **Frontend**: Host the `web/` folder on Vercel/GitHub Pages.
3. **Configuration**: Set `GROQ_API_KEY` in the server environment variables.

### 🗺️ Future Roadmap
- [ ] **Multi-Language Sandboxes**: Adding Node.js/Jest support for native TypeScript verification.
- [ ] **LLM-as-a-Judge**: Implementing a secondary LLM to grade the quality of the refactor.
- [ ] **IDE Extension**: Porting the bridge to a VS Code extension for "one-click" repairs.

---
<p align="right">
  <i>Developed by <b>Sabari</b> as part of the Agentic AI Engineering Track.</i><br>
  <a href="#hero"><b>⬆️ Back to Top</b></a>
</p>

---

## 🚀 Quick Start

### 1. Prerequisites & Virtual Environment

Clone the repository and initialize the Python 3.10+ virtual environment:

```powershell
# Clone repository
git clone https://github.com/Sabarixx/agentic-code-fixer.git
cd agentic-code-fixer

# Create and activate virtual environment (PowerShell)
python -m venv venv
.\venv\Scripts\Activate.ps1

# Install requirements
pip install -r requirements.txt
```

### 2. Environment Variables Configuration

Copy the example environment file and configure your API credentials:

```powershell
copy .env.example .env
```

Edit `.env` to supply your Groq / Gemini API key:

```env
GROQ_API_KEY="your_groq_api_key_here"
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY="your_langsmith_api_key_here"
LANGCHAIN_PROJECT="agentic-code-fixer"
```

### 3. Execution & Verification

Run the components using the virtual environment:

```powershell
# 1. Verify LLM API Access (Day 1)
.\venv\Scripts\python.exe scratch/test_llm.py

# 2. Run LangGraph Skeleton Pipeline (Day 3)
.\venv\Scripts\python.exe agent/graph.py

# 3. Execute 40 Reference Ground-Truth Tests (Day 7)
.\venv\Scripts\python.exe -m pytest specs/tests/
```

---

## 📊 Observability & Tracing

Full execution observability is powered by **LangSmith**. Every graph run logs node-level inputs, outputs, tokens, and execution latency.

```powershell
# Ensure tracing is enabled in .env
LANGCHAIN_TRACING_V2=true
LANGCHAIN_PROJECT=agentic-code-fixer
```

When running `python agent/graph.py`, inspect traces in your [LangSmith Dashboard](https://smith.langchain.com/) to analyze node timing and state transitions.

---

## 📁 Repository Structure

```text
agentic-code-fixer/
├── 📂 agent/                       # Core LangGraph implementation
│   ├── 📄 state.py                 # TypedDict AgentState schema & Status enum
│   ├── 📄 graph.py                 # Compiled StateGraph & node wiring
│   ├── 📄 router.py                # Conditional edge routing (retry + refactor)
│   └── 📂 nodes/                   # One file per agent node
│       ├── 📄 planner.py           # PlanOutput Pydantic model, structured plan
│       ├── 📄 coder.py             # AST-validated code generation & retry prompt
│       ├── 📄 tester.py            # Sandboxed pytest execution, TestResult schema
│       └── 📄 refactor.py          # Code improvement + discard-on-regression safety
├── 📂 docs/                        # Project documentation (all committed)
│   ├── 📄 architecture.md          # Locked architecture contract (Week 1, never changed)
│   ├── 📄 self_eval.md             # Week 7 self-evaluation (8 sections, evidence-grounded)
│   └── 📄 demo_script.md           # Week 8 live demo talking script (6–8 min)
├── 📂 specs/                       # Evaluation benchmark
│   ├── 📄 spec_01.json … spec_08.json  # 8 problem definitions
│   ├── 📂 reference/               # Ground-truth reference implementations
│   └── 📂 tests/                   # 5 pytest unit tests per spec (40 total)
├── 📂 tools/                       # Shared utilities
│   ├── 📄 sandbox_runner.py        # Subprocess pytest isolation + timeout
│   ├── 📄 file_writer.py           # Generated code file manager
│   └── 📄 retry_utils.py           # Exponential backoff for LLM API calls
├── 📂 tests/                       # Agent unit test suites (37 tests)
│   ├── 📄 test_planner.py          # 9 tests — planner schema & edge cases
│   ├── 📄 test_coder.py            # 14 tests — extraction, AST, file writer
│   ├── 📄 test_tester_node.py      # 7 tests — sandbox, timeout, result model
│   ├── 📄 test_retry_loop.py       # 5 tests — router branching logic
│   └── 📄 test_refactor_node.py    # 2 tests — keep valid / revert on regression
├── 📂 traces/                      # Evaluation evidence archive (read-only after Week 6)
│   ├── 📂 final_run/               # 8 complete JSON traces + generated code archive
│   ├── 📄 week6_summary.md         # Final evaluation results table (8/8 refactored)
│   └── 📄 week6_failure_analysis.md # 0 failures
├── 📂 generated/                   # All LLM code attempts (never manually pruned)
├── 📂 scratch/                     # Utility scripts
│   ├── 📄 run_demo.py              # Single-command live demo (all 4 nodes, colored output)
│   └── 📄 verify_fresh_clone.py    # 52-check pre-demo environment verifier
├── 📂 assets/                      # README visual assets
│   └── 🖼️ banner.jpg               # Cyber duotone header banner
├── 📄 requirements.txt             # Project dependencies
├── 📄 README.md                    # Project documentation
└── 📄 pytest.ini                   # Pytest configuration
```

---

<details>
<summary><b>🔍 State Schema Technical Reference (Click to Expand)</b></summary>

<br/>

### `AgentState` TypedDict Fields

The system state is locked per [`docs/architecture.md`](file:///d:/Agentic-AI/agentic-code-fixer/docs/architecture.md):

| Field | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `spec` | `dict[str, Any]` | `{}` | Loaded problem specification (name, signature, docstring, constraints). |
| `plan` | `str` | `""` | Algorithmic strategy & edge case handling produced by Planner node. |
| `code` | `str` | `""` | Generated Python code candidate. |
| `test_results` | `dict[str, Any]` | `{}` | Sandbox execution report (passed count, failed count, tracebacks). |
| `iteration_count` | `int` | `0` | Count of Coder ↔ Tester retry iterations (max limit = 3). |
| `status` | `Status` | `"idle"` | Current pipeline status (`idle`, `planning`, `coding`, `testing`, `refactoring`, `passed`, `failed`, `error`). |

</details>

---

## 🤝 Contributing & Asset Maintenance

- **Adding Function Specs**: Create `specs/spec_XX.json`, add reference solution in `specs/reference/spec_XX.py`, and write 5 test cases in `specs/tests/test_spec_XX.py`.
- **Maintaining Visual Theme**: When updating banners or graphics, maintain the core duotone color palette:
  - **Cyan (`#06B6D4`)** - Primary accents & nodes
  - **Deep Purple (`#8B5CF6`)** - Secondary flow lines & connections
  - **Dark Slate (`#0F172A`)** - Dark mode background containers
- **Asset Hosting**: Store all project images inside `assets/` relative to repo root for GitHub relative path resolution.

---

## 👤 Author & License

Developed as part of the **8-Week Agentic AI Engineering Track**.

- **Author**: [Sabari](https://github.com/Sabarixx)
- **Repository**: [Sabarixx/agentic-code-fixer](https://github.com/Sabarixx/agentic-code-fixer)
- **License**: [MIT License](LICENSE)

<p align="right">
  <a href="#-agentic-code-fixer"><b>⬆️ Back to Top</b></a>
</p>
