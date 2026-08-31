"""Sandbox runner: executes generated code against spec test suites in an isolated subprocess."""

from __future__ import annotations

import json
import os
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
    """Structured result returned by the sandboxed pytest execution."""

    passed: int = 0
    failed: int = 0
    total: int = 0
    all_passed: bool = False
    failure_details: list[str] = []
    stdout: str = ""
    stderr: str = ""
    timed_out: bool = False
    error: str = ""


def _build_sandbox_test_file(spec_id: str, sandbox_dir: Path) -> Path:
    """
    Write a self-contained test file into the sandbox directory.
    The test imports from 'generated_code', which may be augmented with
    helper functions from the reference implementation when the spec needs them.
    """
    import re

    original_test = ROOT / "specs" / "tests" / f"test_{spec_id}.py"
    if not original_test.exists():
        raise FileNotFoundError(f"Reference test file not found: {original_test}")

    test_source = original_test.read_text(encoding="utf-8")

    # Find what symbols the test wants to import from the reference module
    import_match = re.search(
        r"^from specs\.reference\.\w+ import (.+)$", test_source, re.MULTILINE
    )
    imported_symbols: list[str] = []
    if import_match:
        imported_symbols = [s.strip() for s in import_match.group(1).split(",")]

    # Load generated code to check which symbols it already defines
    generated_code_path = sandbox_dir / "generated_code.py"
    generated_source = generated_code_path.read_text(encoding="utf-8")
    defined_in_generated = set(re.findall(r"^def (\w+)\s*[\\'(\\]|^class (\w+)\s*[\\'(:]", generated_source, re.MULTILINE))
    defined_names: set[str] = set()
    for match in re.finditer(r"^(?:def|class)\s+(\w+)", generated_source, re.MULTILINE):
        defined_names.add(match.group(1))

    # Determine which symbols are missing from generated code → need to inject from reference
    missing = [s for s in imported_symbols if s not in defined_names]

    if missing:
        # Append reference helpers to generated_code.py (strip __future__ to avoid syntax error)
        reference_path = ROOT / "specs" / "reference" / f"{spec_id}.py"
        if reference_path.exists():
            ref_source = reference_path.read_text(encoding="utf-8")
            # Remove __future__ imports – they MUST appear at the top of a file
            ref_clean = re.sub(r"^from __future__ import .+\n?", "", ref_source, flags=re.MULTILINE)
            injected = "\n\n# --- injected reference helpers ---\n" + ref_clean
            with open(generated_code_path, "a", encoding="utf-8") as fh:
                fh.write(injected)

    # Rewrite import to use the sandbox generated_code module
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
    """Parse pytest --tb=short output into (passed, failed, total, failure_details)."""
    import re

    passed = 0
    failed = 0
    failure_details: list[str] = []

    # Attempt to parse the summary line: e.g. "3 passed, 2 failed in 0.12s"
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

    # Collect FAILED lines as failure details
    for line in (stdout + stderr).splitlines():
        if line.strip().startswith("FAILED") or "AssertionError" in line or "Error" in line:
            failure_details.append(line.strip())

    return passed, failed, total, failure_details


def run_sandboxed_pytest(spec_id: str, attempt_n: int, timeout: int = 10) -> TestResult:
    """
    Run the pytest suite for `spec_id` against the generated attempt `attempt_n`.
    Execution happens in a fresh temp directory with minimal env vars and a hard timeout.
    """
    generated_file = GENERATED_DIR / f"{spec_id}_attempt_{attempt_n}.py"
    if not generated_file.exists():
        return TestResult(
            error=f"Generated file not found: {generated_file}",
        )

    tmp_dir = Path(tempfile.mkdtemp(prefix=f"sandbox_{spec_id}_"))
    try:
        # 1. Copy generated code as 'generated_code.py' into sandbox
        shutil.copy(generated_file, tmp_dir / "generated_code.py")

        # 2. Write adapted test file into sandbox
        try:
            _build_sandbox_test_file(spec_id, tmp_dir)
        except FileNotFoundError as exc:
            return TestResult(error=str(exc))

        # 3. Build minimal environment (Python path only)
        minimal_env = {
            "PATH": os.environ.get("PATH", ""),
            "SYSTEMROOT": os.environ.get("SYSTEMROOT", ""),  # needed on Windows
            "TEMP": os.environ.get("TEMP", ""),
            "TMP": os.environ.get("TMP", ""),
            "PYTHONPATH": str(tmp_dir),
        }

        python_exe = sys.executable

        # 4. Run pytest inside sandbox
        try:
            proc = subprocess.run(
                [
                    python_exe, "-m", "pytest",
                    "test_generated.py",
                    "--tb=short",
                    "-q",
                    "--no-header",
                ],
                cwd=str(tmp_dir),
                env=minimal_env,
                capture_output=True,
                text=True,
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

        # 5. Parse results
        passed, failed, total, failure_details = _parse_pytest_output(stdout, stderr)

        # If pytest returned non-zero but no failures parsed, capture raw error
        if proc.returncode not in (0, 1) and total == 0:
            combined = (stdout + "\n" + stderr).strip()
            return TestResult(
                error=f"pytest exited with code {proc.returncode}",
                failure_details=[combined[:2000]],  # cap to 2000 chars
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


def run_bandit_security_scan(code: str) -> list[str]:
    """Run bandit static security analysis on code string. Returns list of warning messages."""
    warnings: list[str] = []

    # 1. AST-based check for dangerous primitives
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

    # 2. Bandit CLI analysis (skipping B101 assert checks as assert is normal in test/debugging code)
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


def run_custom_sandboxed_pytest(code: str, test_code: str, timeout: int = 10) -> TestResult:
    """
    Execute user candidate code against a pytest test suite in a secure temp directory.
    """
    tmp_dir = Path(tempfile.mkdtemp(prefix="custom_sandbox_"))
    try:
        # Write candidate code
        candidate_file = tmp_dir / "candidate_code.py"
        candidate_file.write_text(code, encoding="utf-8")

        # Adapt test code: ensure candidate_code is imported if not already
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
        }

        python_exe = sys.executable

        try:
            proc = subprocess.run(
                [
                    python_exe, "-m", "pytest",
                    "test_candidate.py",
                    "--tb=short",
                    "-q",
                    "--no-header",
                ],
                cwd=str(tmp_dir),
                env=minimal_env,
                capture_output=True,
                text=True,
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

