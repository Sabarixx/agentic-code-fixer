"""
Fresh-clone verification checklist.

Simulates what a reviewer gets after:
    git clone https://github.com/Sabarixx/agentic-code-fixer
    pip install -r requirements.txt
    cp .env.example .env  # then fill in GROQ_API_KEY

Run this before Week 8 submission or any demo to confirm the environment is clean.

Usage:
    python scratch/verify_fresh_clone.py
"""

from __future__ import annotations

import importlib
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BOLD = "\033[1m"
DIM = "\033[2m"
RESET = "\033[0m"

PASS = f"{GREEN}[PASS]{RESET}"
FAIL = f"{RED}[FAIL]{RESET}"
WARN = f"{YELLOW}[WARN]{RESET}"

results: list[tuple[str, bool, str]] = []


def check(label: str, ok: bool, detail: str = "") -> bool:
    tag = PASS if ok else FAIL
    detail_str = f"  {DIM}{detail}{RESET}" if detail else ""
    print(f"  {tag}  {label}{detail_str}")
    results.append((label, ok, detail))
    return ok


def section(title: str):
    print(f"\n{BOLD}-- {title} {'-' * (60 - len(title))}{RESET}")


# -- 1. Environment Variables ---------------------------------------------------

section("Environment Variables")

from dotenv import load_dotenv
load_dotenv(ROOT / ".env")

groq_key = os.getenv("GROQ_API_KEY", "")
check(".env file exists", (ROOT / ".env").exists())
check("GROQ_API_KEY is set and non-empty", bool(groq_key), f"Value length: {len(groq_key)} chars")
langchain_trace = os.getenv("LANGCHAIN_TRACING_V2", "")
if not langchain_trace:
    print(f"  {WARN}  LANGCHAIN_TRACING_V2 not set (optional -- set for LangSmith observability)")
else:
    check("LANGCHAIN_TRACING_V2 is set (optional for LangSmith)", True)

# -- 2. Required Directories ----------------------------------------------------

section("Required Directories")

required_dirs = [
    "agent", "agent/nodes", "agent/prompts",
    "specs", "specs/tests", "specs/reference",
    "tools", "tests", "traces/final_run",
    "generated", "docs",
]
for d in required_dirs:
    path = ROOT / d
    check(f"Directory exists: {d}/", path.is_dir())

# -- 3. Required Files ----------------------------------------------------------

section("Required Files")

required_files = [
    "requirements.txt",
    "pytest.ini",
    "agent/__init__.py",
    "agent/state.py",
    "agent/graph.py",
    "agent/router.py",
    "agent/nodes/planner.py",
    "agent/nodes/coder.py",
    "agent/nodes/tester.py",
    "agent/nodes/refactor.py",
    "tools/sandbox_runner.py",
    "tools/file_writer.py",
    "tools/retry_utils.py",
    "docs/architecture.md",
    "docs/self_eval.md",
    "traces/week6_summary.md",
]
for f in required_files:
    path = ROOT / f
    check(f"File exists: {f}", path.is_file())

# -- 4. Python Imports ----------------------------------------------------------

section("Python Package Imports")

packages = [
    ("langgraph", "langgraph"),
    ("langchain_groq", "langchain-groq"),
    ("pydantic", "pydantic"),
    ("dotenv", "python-dotenv"),
]
for module_name, pip_name in packages:
    try:
        importlib.import_module(module_name)
        check(f"import {module_name}", True)
    except ImportError as e:
        check(f"import {module_name}", False, f"pip install {pip_name}")

# -- 5. Spec Files (8 specs) ----------------------------------------------------

section("Spec Files (8 required)")

for i in range(1, 9):
    spec_file = ROOT / "specs" / f"spec_{i:02d}.json"
    test_file = ROOT / "specs" / "tests" / f"test_spec_{i:02d}.py"
    ref_file  = ROOT / "specs" / "reference" / f"spec_{i:02d}.py"
    check(f"spec_{i:02d}.json + test + reference", all(f.exists() for f in [spec_file, test_file, ref_file]))

# -- 6. Reference Pytest Suite (40 tests) ---------------------------------------

section("Reference Pytest Suite (40 ground-truth tests)")

proc = subprocess.run(
    [sys.executable, "-m", "pytest", "specs/tests/", "-q", "--no-header", "--tb=no"],
    cwd=str(ROOT),
    capture_output=True,
    text=True,
    timeout=30,
)
stdout = proc.stdout.strip()
ok = proc.returncode == 0
check("pytest specs/tests/ -- all 40 reference tests pass", ok, stdout.splitlines()[-1] if stdout else "")

# -- 7. Agent State & Graph Import ----------------------------------------------

section("Agent Graph -- Import and Build")

try:
    sys.path.insert(0, str(ROOT))
    from agent.state import initial_state, AgentState, MAX_ITERATIONS
    check("agent.state imports OK (initial_state, AgentState, MAX_ITERATIONS)", True)
except Exception as e:
    check("agent.state imports OK", False, str(e))

try:
    from agent.graph import build_graph
    app = build_graph()
    check("build_graph() compiles without error", True)
except Exception as e:
    check("build_graph() compiles without error", False, str(e))

# -- 8. Final Run Archive Integrity ---------------------------------------------

section("Final Run Archive Integrity (traces/final_run/)")

for i in range(1, 9):
    trace_file = ROOT / "traces" / "final_run" / f"spec_{i:02d}.json"
    if trace_file.exists():
        import json
        data = json.loads(trace_file.read_text(encoding="utf-8"))
        ok = data.get("final_status") in ("passed", "refactored")
        check(f"spec_{i:02d}.json -- final_status is passed/refactored", ok, data.get("final_status", "missing"))
    else:
        check(f"spec_{i:02d}.json -- exists in traces/final_run/", False)

# -- Summary --------------------------------------------------------------------

total = len(results)
passed = sum(1 for _, ok, _ in results if ok)
failed = total - passed

print(f"\n{BOLD}{'=' * 68}{RESET}")
if failed == 0:
    print(f"{GREEN}{BOLD}  ALL {total} CHECKS PASSED -- Environment is demo-ready!{RESET}")
else:
    print(f"{RED}{BOLD}  {failed}/{total} CHECKS FAILED -- Fix before demo/submission.{RESET}")
    print(f"\n{RED}Failing checks:{RESET}")
    for label, ok, detail in results:
        if not ok:
            print(f"  x  {label}  {DIM}{detail}{RESET}")

print(f"{BOLD}{'=' * 68}{RESET}\n")
sys.exit(0 if failed == 0 else 1)
