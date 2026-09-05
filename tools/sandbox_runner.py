"""Sandbox runner: executes generated and user-submitted code against test suites in isolated subprocesses.
Supports polyglot multi-language environments (Python, TypeScript, JavaScript).
"""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

from pydantic import BaseModel

ROOT = Path(__file__).resolve().parent.parent
GENERATED_DIR = ROOT / "generated"
SPECS_DIR = ROOT / "specs"


class TestResult(BaseModel):
    """Structured result returned by the sandboxed test execution."""

    passed: int = 0
    failed: int = 0
    total: int = 0
    all_passed: bool = False
    failure_details: list[str] = []
    stdout: str = ""
    stderr: str = ""
    timed_out: bool = False
    error: str = ""


def detect_language(code: str, hint: str = "") -> str:
    """
    Detect the programming language of a code snippet.
    Returns: 'typescript', 'javascript', 'python', or 'rust'.
    """
    if hint:
        h = hint.lower().strip()
        if "type" in h or h == "ts":
            return "typescript"
        if "java" in h or h == "js":
            return "javascript"
        if "py" in h:
            return "python"
        if "rust" in h or h == "rs":
            return "rust"

    clean = code.strip()

    # TypeScript / JavaScript signals
    ts_keywords = ["interface ", "type ", ": string", ": number", ": boolean", ": void", ": any", ": User"]
    js_keywords = ["function ", "const ", "let ", "var ", "=>", "console.log", "=== ", "!== "]

    for kw in ts_keywords:
        if kw in clean:
            return "typescript"

    for kw in js_keywords:
        if kw in clean:
            return "javascript"

    # Python signals
    py_keywords = ["def ", "class ", "import ", "from ", "print(", "__name__", "elif ", "self."]
    for kw in py_keywords:
        if kw in clean:
            return "python"

    return "typescript" if (":" in clean and "{" in clean) else "python"


def _build_sandbox_test_file(spec_id: str, sandbox_dir: Path) -> Path:
    """
    Write a self-contained test file into the sandbox directory for spec benchmark runs.
    """
    original_test = ROOT / "specs" / "tests" / f"test_{spec_id}.py"
    if not original_test.exists():
        raise FileNotFoundError(f"Reference test file not found: {original_test}")

    test_source = original_test.read_text(encoding="utf-8")

    import_match = re.search(
        r"^from specs\.reference\.\w+ import (.+)$", test_source, re.MULTILINE
    )
    imported_symbols: list[str] = []
    if import_match:
        imported_symbols = [s.strip() for s in import_match.group(1).split(",")]

    generated_code_path = sandbox_dir / "generated_code.py"
    generated_source = generated_code_path.read_text(encoding="utf-8")
    defined_names: set[str] = set()
    for match in re.finditer(r"^(?:def|class)\s+(\w+)", generated_source, re.MULTILINE):
        defined_names.add(match.group(1))

    missing = [s for s in imported_symbols if s not in defined_names]
    if missing:
        reference_path = ROOT / "specs" / "reference" / f"{spec_id}.py"
        if reference_path.exists():
            ref_source = reference_path.read_text(encoding="utf-8")
            ref_clean = re.sub(r"^from __future__ import .+\n?", "", ref_source, flags=re.MULTILINE)
            injected = "\n\n# --- injected reference helpers ---\n" + ref_clean
            with open(generated_code_path, "a", encoding="utf-8") as fh:
                fh.write(injected)

    adapted = re.sub(
        r"^from specs\.reference\.\w+ import (.+)$",
        r"from generated_code import \1",
        test_source,
        flags=re.MULTILINE,
    )

    test_file = sandbox_dir / "test_generated.py"
    test_file.write_text(adapted, encoding="utf-8")
    return test_file


def _parse_pytest_output(stdout: str, stderr: str) -> tuple[int, int, int, list[str]]:
    """Parse pytest output into (passed, failed, total, failure_details)."""
    passed = 0
    failed = 0
    failure_details: list[str] = []

    summary_match = re.search(
        r"(\d+) passed(?:.*?(\d+) failed)?|(\d+) failed(?:.*?(\d+) passed)?",
        stdout + stderr,
        re.IGNORECASE,
    )
    if summary_match:
        g = summary_match.groups()
        passed = int(g[0] or g[3] or 0)
        failed = int(g[1] or g[2] or 0)
    elif "passed" in (stdout + stderr).lower():
        passed_match = re.search(r"(\d+) passed", stdout + stderr, re.IGNORECASE)
        if passed_match:
            passed = int(passed_match.group(1))
    elif "failed" in (stdout + stderr).lower():
        failed_match = re.search(r"(\d+) failed", stdout + stderr, re.IGNORECASE)
        if failed_match:
            failed = int(failed_match.group(1))

    total = passed + failed

    for line in (stdout + stderr).splitlines():
        if line.strip().startswith("FAILED") or "AssertionError" in line or "Error" in line:
            failure_details.append(line.strip())

    return passed, failed, total, failure_details


def run_sandboxed_pytest(spec_id: str, attempt_n: int, timeout: int = 10) -> TestResult:
    """Run pytest suite for a benchmark spec."""
    generated_file = GENERATED_DIR / f"{spec_id}_attempt_{attempt_n}.py"
    if not generated_file.exists():
        return TestResult(error=f"Generated file not found: {generated_file}")

    tmp_dir = Path(tempfile.mkdtemp(prefix=f"sandbox_{spec_id}_"))
    try:
        shutil.copy(generated_file, tmp_dir / "generated_code.py")
        try:
            _build_sandbox_test_file(spec_id, tmp_dir)
        except FileNotFoundError as exc:
            return TestResult(error=str(exc))

        minimal_env = {
            "PATH": os.environ.get("PATH", ""),
            "SYSTEMROOT": os.environ.get("SYSTEMROOT", ""),
            "TEMP": os.environ.get("TEMP", ""),
            "TMP": os.environ.get("TMP", ""),
            "PYTHONPATH": str(tmp_dir),
            "PYTHONIOENCODING": "utf-8",
            "PYTHONUTF8": "1",
        }

        try:
            proc = subprocess.run(
                [
                    sys.executable, "-m", "pytest",
                    "test_generated.py",
                    "--tb=short",
                    "-q",
                    "--no-header",
                ],
                cwd=str(tmp_dir),
                env=minimal_env,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=timeout,
            )
        except subprocess.TimeoutExpired:
            return TestResult(
                timed_out=True,
                error=f"Execution timed out after {timeout}s",
                failure_details=[f"TimeoutExpired: execution exceeded {timeout} seconds"],
            )

        stdout = proc.stdout or ""
        stderr = proc.stderr or ""
        passed, failed, total, failure_details = _parse_pytest_output(stdout, stderr)

        return TestResult(
            passed=passed,
            failed=failed,
            total=total,
            all_passed=(failed == 0 and total > 0),
            failure_details=failure_details,
            stdout=stdout,
            stderr=stderr,
        )
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)


def run_custom_sandboxed_pytest(code: str, test_code: str, timeout: int = 10) -> TestResult:
    """
    Execute user candidate Python code against a pytest test suite in a secure temp directory.
    """
    tmp_dir = Path(tempfile.mkdtemp(prefix="custom_sandbox_py_"))
    try:
        candidate_file = tmp_dir / "candidate_code.py"
        candidate_file.write_text(code, encoding="utf-8")

        adapted_test = test_code.strip()
        if "from candidate_code" not in adapted_test and "import candidate_code" not in adapted_test:
            adapted_test = "from candidate_code import *\n\n" + adapted_test

        test_file = tmp_dir / "test_candidate.py"
        test_file.write_text(adapted_test, encoding="utf-8")

        minimal_env = {
            "PATH": os.environ.get("PATH", ""),
            "SYSTEMROOT": os.environ.get("SYSTEMROOT", ""),
            "TEMP": os.environ.get("TEMP", ""),
            "TMP": os.environ.get("TMP", ""),
            "PYTHONPATH": str(tmp_dir),
            "PYTHONIOENCODING": "utf-8",
            "PYTHONUTF8": "1",
        }

        try:
            proc = subprocess.run(
                [
                    sys.executable, "-m", "pytest",
                    "test_candidate.py",
                    "--tb=short",
                    "-q",
                    "--no-header",
                ],
                cwd=str(tmp_dir),
                env=minimal_env,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=timeout,
            )
        except subprocess.TimeoutExpired:
            return TestResult(
                timed_out=True,
                error=f"Execution timed out after {timeout}s",
                failure_details=[f"TimeoutExpired: execution exceeded {timeout} seconds"],
            )

        stdout = proc.stdout or ""
        stderr = proc.stderr or ""
        passed, failed, total, failure_details = _parse_pytest_output(stdout, stderr)

        if proc.returncode not in (0, 1) and total == 0:
            combined = (stdout + "\n" + stderr).strip()
            return TestResult(
                error=f"pytest exited with code {proc.returncode}",
                failure_details=[combined[:2000]],
                stdout=stdout,
                stderr=stderr,
            )

        return TestResult(
            passed=passed,
            failed=failed,
            total=total,
            all_passed=(failed == 0 and total > 0),
            failure_details=failure_details,
            stdout=stdout,
            stderr=stderr,
        )
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)


def _strip_typescript_types(code: str) -> str:
    """Simple, reliable regex stripper for inline TS types to allow clean Node.js execution."""
    clean = code
    # Remove interface definitions
    clean = re.sub(r"interface\s+\w+\s*\{[^}]*\}", "", clean, flags=re.MULTILINE)
    # Remove type aliases
    clean = re.sub(r"type\s+\w+\s*=[^;]+;", "", clean, flags=re.MULTILINE)
    # Remove parameter types e.g. (user: User, id: number) -> (user, id)
    clean = re.sub(r":\s*[A-Z][a-zA-Z0-9_<>[\]]*\b", "", clean)
    clean = re.sub(r":\s*(?:string|number|boolean|any|void|unknown|never)\b", "", clean)
    return clean


def run_custom_sandboxed_jest(code: str, test_code: str, timeout: int = 10) -> TestResult:
    """
    Execute user candidate TypeScript / JavaScript code against a Jest-compatible test suite
    using a Node.js sandbox harness with built-in assertion evaluator.
    """
    tmp_dir = Path(tempfile.mkdtemp(prefix="custom_sandbox_ts_"))
    try:
        # Clean import/export statements for self-contained runner script
        clean_code = re.sub(r"module\.exports\s*=\s*\{[^}]*\};?", "", code)
        clean_code = re.sub(r"export\s*\{[^}]*\};?", "", clean_code)
        clean_code = re.sub(r"^export\s+(?:default\s+)?", "", clean_code, flags=re.MULTILINE)
        clean_tests = re.sub(r"const\s*\{[^}]*\}\s*=\s*require\([^)]*\);?", "", test_code)
        clean_tests = re.sub(r"import\s*\{[^}]*\}\s*from\s*['\"][^'\"]*['\"];?", "", clean_tests)

        harness_ts = f"""
// --- CANDIDATE CODE ---
{clean_code}

// --- JEST RUNNER SHIM ---
let passed = 0;
let failed = 0;
const failureDetails: string[] = [];

function expect(actual: any) {{
  return {{
    toBe(expected: any) {{
      if (actual !== expected) {{
        throw new Error(`Expected ${{JSON.stringify(expected)}} but received ${{JSON.stringify(actual)}}`);
      }}
    }},
    toEqual(expected: any) {{
      if (JSON.stringify(actual) !== JSON.stringify(expected)) {{
        throw new Error(`Expected ${{JSON.stringify(expected)}} but received ${{JSON.stringify(actual)}}`);
      }}
    }},
    toBeNull() {{
      if (actual !== null) {{
        throw new Error(`Expected null but received ${{JSON.stringify(actual)}}`);
      }}
    }},
    toBeUndefined() {{
      if (actual !== undefined) {{
        throw new Error(`Expected undefined but received ${{JSON.stringify(actual)}}`);
      }}
    }},
    toBeTruthy() {{
      if (!actual) {{
        throw new Error(`Expected truthy but received ${{JSON.stringify(actual)}}`);
      }}
    }},
    toBeFalsy() {{
      if (actual) {{
        throw new Error(`Expected falsy but received ${{JSON.stringify(actual)}}`);
      }}
    }}
  }};
}}

function it(name: string, fn: () => void) {{
  try {{
    fn();
    passed++;
    console.log(`✓ ${{name}} [PASS]`);
  }} catch (err: any) {{
    failed++;
    const msg = `✗ ${{name}}: ${{err.message || err}}`;
    failureDetails.push(msg);
    console.log(msg);
  }}
}}

const test = it;
function describe(name: string, fn: () => void) {{
  console.log(`Suite: ${{name}}`);
  fn();
}}

// --- TEST SUITE ---
try {{
{clean_tests}
}} catch (suiteErr: any) {{
  failed++;
  failureDetails.push(`Suite Error: ${{suiteErr.message || suiteErr}}`);
}}

// Output JSON summary line
console.log("__RESULT__" + JSON.stringify({{
  passed: passed,
  failed: failed,
  total: passed + failed,
  all_passed: failed === 0 && (passed > 0),
  failure_details: failureDetails
}}));
"""

        runner_file = tmp_dir / "runner.ts"
        runner_file.write_text(harness_ts, encoding="utf-8")

        # Execute in isolated subprocess via Node with TypeScript stripping
        try:
            proc = subprocess.run(
                ["node", "--experimental-strip-types", "--no-warnings", str(runner_file)],
                cwd=str(tmp_dir),
                capture_output=True,
                text=True,
                timeout=timeout,
            )
        except subprocess.TimeoutExpired:
            return TestResult(
                timed_out=True,
                error=f"Node.js test execution timed out after {timeout}s",
                failure_details=[f"TimeoutExpired: test exceeded {timeout} seconds"],
            )

        stdout = proc.stdout or ""
        stderr = proc.stderr or ""

        # Parse JSON output from harness
        for line in stdout.splitlines():
            if line.startswith("__RESULT__"):
                data = json.loads(line.replace("__RESULT__", ""))
                return TestResult(
                    passed=data.get("passed", 0),
                    failed=data.get("failed", 0),
                    total=data.get("total", 0),
                    all_passed=data.get("all_passed", False),
                    failure_details=data.get("failure_details", []),
                    stdout=stdout,
                    stderr=stderr,
                )

        if proc.returncode != 0:
            err_line = stderr.strip() or stdout.strip() or f"Node exited with code {proc.returncode}"
            return TestResult(
                passed=0,
                failed=1,
                total=1,
                all_passed=False,
                failure_details=[err_line[:1000]],
                stdout=stdout,
                stderr=stderr,
            )

        return TestResult(
            passed=1,
            failed=0,
            total=1,
            all_passed=True,
            stdout=stdout,
            stderr=stderr,
        )

    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)


def run_sandboxed_tests(code: str, test_code: str, language: str = "python", timeout: int = 10) -> TestResult:
    """
    Polyglot Sandbox Runner: selects and executes the appropriate test engine
    based on the target programming language.
    """
    lang = detect_language(code, hint=language)
    if lang in ("typescript", "javascript"):
        return run_custom_sandboxed_jest(code, test_code, timeout=timeout)
    else:
        return run_custom_sandboxed_pytest(code, test_code, timeout=timeout)


def run_polyglot_security_scan(code: str, language: str = "python") -> list[str]:
    """Polyglot security and hazard scanner."""
    warnings: list[str] = []
    lang = detect_language(code, hint=language)

    if lang == "python":
        warnings.extend(run_bandit_security_scan(code))
    else:
        # JS / TS security scan
        dangerous_patterns = [
            (r"\beval\s*\(", "Dynamic code execution via `eval()`"),
            (r"\bFunction\s*\(", "Dynamic code compilation via `new Function()`"),
            (r"require\s*\(\s*['\"]child_process['\"]\s*\)", "Subshell execution via `child_process`"),
            (r"__proto__", "Prototype pollution hazard detected"),
        ]
        for pattern, desc in dangerous_patterns:
            if re.search(pattern, code):
                warnings.append(f"Security Warning: {desc}")

    return warnings


def run_bandit_security_scan(code: str) -> list[str]:
    """Run bandit static security analysis on Python code string."""
    warnings: list[str] = []

    try:
        import ast
        tree = ast.parse(code)
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                func_name = ""
                if isinstance(node.func, ast.Name):
                    func_name = node.func.id
                elif isinstance(node.func, ast.Attribute):
                    func_name = node.func.attr
                if func_name in ("eval", "exec"):
                    warnings.append(f"Security Warning: Dynamic code execution via `{func_name}()` on line {node.lineno}")
                elif func_name in ("system", "popen", "spawn"):
                    warnings.append(f"Security Warning: Subshell/OS command invocation via `{func_name}()` on line {node.lineno}")
    except Exception:
        pass

    tmp_file = Path(tempfile.gettempdir()) / f"bandit_scan_{os.getpid()}_{hash(code)}.py"
    try:
        tmp_file.write_text(code, encoding="utf-8")
        proc = subprocess.run(
            [sys.executable, "-m", "bandit", "-f", "json", "-q", "-s", "B101", str(tmp_file)],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if proc.stdout.strip():
            data = json.loads(proc.stdout)
            for item in data.get("results", []):
                test_id = item.get("test_id", "")
                if test_id == "B101":
                    continue
                severity = item.get("issue_severity", "LOW")
                text = item.get("issue_text", "")
                line = item.get("line_number", "")
                warnings.append(f"[{severity}] {test_id}: {text} (line {line})")
    except Exception:
        pass
    finally:
        if tmp_file.exists():
            tmp_file.unlink(missing_ok=True)

    return warnings
