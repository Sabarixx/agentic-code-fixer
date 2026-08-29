"""Pytest test suite for Tester Node and Sandbox Runner."""

from __future__ import annotations

import sys
import textwrap
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.sandbox_runner import TestResult, run_sandboxed_pytest


# ─── Sample implementations ─────────────────────────────────────────────────

CORRECT_TWO_SUM = textwrap.dedent("""\
    from typing import List

    def two_sum(nums: List[int], target: int) -> List[int]:
        seen = {}
        for i, n in enumerate(nums):
            comp = target - n
            if comp in seen:
                return [seen[comp], i]
            seen[n] = i
        raise ValueError("No solution")
""")

BUGGY_TWO_SUM = textwrap.dedent("""\
    from typing import List

    def two_sum(nums: List[int], target: int) -> List[int]:
        # intentionally wrong
        return [0, 1]
""")

INFINITE_LOOP_CODE = textwrap.dedent("""\
    from typing import List

    def two_sum(nums: List[int], target: int) -> List[int]:
        while True:
            pass
""")


@pytest.fixture(autouse=True)
def patch_generated_dir(tmp_path, monkeypatch):
    """Redirect GENERATED_DIR so test files are written to a tmp directory."""
    import tools.sandbox_runner as sr
    monkeypatch.setattr(sr, "GENERATED_DIR", tmp_path)
    return tmp_path


def _write_generated(tmp_path: Path, spec_id: str, attempt: int, code: str):
    f = tmp_path / f"{spec_id}_attempt_{attempt}.py"
    f.write_text(code, encoding="utf-8")


# ─── Unit tests ─────────────────────────────────────────────────────────────

def test_correct_code_passes_all_tests(tmp_path):
    _write_generated(tmp_path, "spec_01", 1, CORRECT_TWO_SUM)
    result = run_sandboxed_pytest("spec_01", 1)
    assert result.all_passed is True
    assert result.passed == 5
    assert result.failed == 0
    assert result.total == 5
    assert not result.timed_out
    assert result.error == ""


def test_buggy_code_fails_tests(tmp_path):
    _write_generated(tmp_path, "spec_01", 1, BUGGY_TWO_SUM)
    result = run_sandboxed_pytest("spec_01", 1)
    assert result.all_passed is False
    assert result.failed > 0


def test_timeout_is_enforced(tmp_path):
    _write_generated(tmp_path, "spec_01", 1, INFINITE_LOOP_CODE)
    result = run_sandboxed_pytest("spec_01", 1, timeout=3)
    assert result.timed_out is True
    assert result.all_passed is False


def test_missing_generated_file_returns_error():
    result = run_sandboxed_pytest("spec_01", 999)
    assert result.error != ""
    assert result.all_passed is False


def test_result_model_fields():
    r = TestResult(passed=4, failed=1, total=5, all_passed=False, failure_details=["AssertionError"])
    assert r.total == 5
    assert r.all_passed is False
    assert "AssertionError" in r.failure_details


# ─── Integration: tester_node ───────────────────────────────────────────────

def test_tester_node_passes_on_correct_code(tmp_path):
    _write_generated(tmp_path, "spec_01", 1, CORRECT_TWO_SUM)
    from agent.nodes.tester import tester_node
    from agent.state import initial_state
    import json

    spec = json.loads((ROOT / "specs" / "spec_01.json").read_text(encoding="utf-8"))
    state = initial_state(spec)
    state["iteration_count"] = 1

    result = tester_node(state)
    assert result["status"] == "passed"
    assert result["test_results"]["all_passed"] is True


def test_tester_node_fails_on_buggy_code(tmp_path):
    _write_generated(tmp_path, "spec_01", 1, BUGGY_TWO_SUM)
    from agent.nodes.tester import tester_node
    from agent.state import initial_state
    import json

    spec = json.loads((ROOT / "specs" / "spec_01.json").read_text(encoding="utf-8"))
    state = initial_state(spec)
    state["iteration_count"] = 1

    result = tester_node(state)
    assert result["status"] == "failed"
    assert result["test_results"]["all_passed"] is False
