"""Tests for the autonomous custom code debugging pipeline."""

from __future__ import annotations

import pytest
from agent.nodes.custom_debugger import (
    diagnose_custom_code,
    generate_custom_pytest_suite,
    repair_custom_code,
    run_custom_debugging_pipeline,
)
from tools.sandbox_runner import (
    run_bandit_security_scan,
    run_custom_sandboxed_pytest,
)
from ui.pipeline_bridge import run_custom_fix


def test_sandbox_runner_custom_pytest_pass():
    """Verify custom sandbox runs and passes clean code."""
    code = "def add(a, b):\n    return a + b\n"
    test_code = "from candidate_code import add\n\ndef test_add():\n    assert add(2, 3) == 5\n"
    res = run_custom_sandboxed_pytest(code, test_code)
    assert res.all_passed is True
    assert res.passed == 1
    assert res.failed == 0


def test_sandbox_runner_custom_pytest_fail():
    """Verify custom sandbox detects failing assertions."""
    code = "def add(a, b):\n    return a - b\n"
    test_code = "from candidate_code import add\n\ndef test_add():\n    assert add(2, 3) == 5\n"
    res = run_custom_sandboxed_pytest(code, test_code)
    assert res.all_passed is False
    assert res.failed == 1


def test_bandit_security_scan():
    """Verify bandit scan flags dangerous eval calls and ignores normal assert statements."""
    unsafe_code = "def dangerous(cmd):\n    eval(cmd)\n"
    warnings = run_bandit_security_scan(unsafe_code)
    assert any("eval" in w.lower() for w in warnings)

    code_with_assert = "def check(x):\n    assert x > 0\n"
    assert_warnings = run_bandit_security_scan(code_with_assert)
    assert not any("B101" in w for w in assert_warnings)


def test_custom_fix_calculate_average():
    """
    Test Bug 1 from prompt: calculate_average division by zero on empty list.
    Verifies real diagnosis, test generation, and verified fix.
    """
    buggy_code = """def calculate_average(marks):
    total = 0

    for i in range(len(marks)):
        total += marks[i]

    average = total / len(marks)

    if average >= 90:
        grade = "A"
    elif average >= 75:
        grade = "B"
    elif average >= 60:
        grade = "C"
    elif average >= 50:
        grade = "D"
    else:
        grade = "F"

    return average, grade


print(calculate_average([90, 80, 70]))
print(calculate_average([100, 90, 80]))
print(calculate_average([]))
"""
    expected = "Calculate the average and grade for a list of marks. When marks is empty, return 0, 'F' gracefully instead of crashing."
    error_msg = "ZeroDivisionError: division by zero"
    user_tests = """def test_calculate_average():
    assert calculate_average([90, 80, 70]) == (80.0, 'B')
    assert calculate_average([]) == (0, 'F')
"""

    stages = list(run_custom_fix(buggy_code, language="python", expected_behavior=expected, error_message=error_msg, user_tests=user_tests))

    stage_names = [s.get("stage") for s in stages]

    assert "diagnosing" in stage_names
    assert "generating_tests" in stage_names
    assert "fixing" in stage_names
    assert "testing" in stage_names
    assert "done" in stage_names

    # Check diagnosis is meaningful
    diag_stage = next(s for s in stages if s.get("stage") == "diagnosing")
    assert "division" in diag_stage.get("root_cause", "").lower() or "empty" in diag_stage.get("root_cause", "").lower() or "zero" in diag_stage.get("root_cause", "").lower()

    # Check final stage status
    done_stage = next(s for s in stages if s.get("stage") == "done")
    assert done_stage.get("status") == "passed"
    corrected_code = done_stage.get("corrected_code", "")
    assert "calculate_average" in corrected_code
    assert corrected_code != buggy_code


def test_custom_fix_find_largest_negative_numbers():
    """
    Test Bug 2 from prompt: find_largest failing on negative numbers.
    Verifies real repair against negative numbers logic.
    """
    buggy_code = """def find_largest(numbers):
    largest = 0

    for i in range(len(numbers)):
        if numbers[i] < largest:
            largest = numbers[i]

    return largest
"""
    expected = "Return the largest number in the list, including when all numbers are negative."
    user_tests = """def test_find_largest():
    assert find_largest([3, 7, 2, 9, 4]) == 9
    assert find_largest([-5, -2, -10, -1]) == -1
    assert find_largest([100, 50, 25]) == 100
"""

    stages = list(run_custom_fix(buggy_code, language="python", expected_behavior=expected, user_tests=user_tests))

    done_stage = next(s for s in stages if s.get("stage") == "done")

    assert done_stage.get("status") == "passed"
    corrected_code = done_stage.get("corrected_code", "")
    assert "find_largest" in corrected_code
    assert corrected_code != buggy_code


def test_are_tests_compatible_detection():
    """Verify incompatible leftover tests are detected and ignored."""
    from agent.nodes.custom_debugger import are_tests_compatible

    code = "function findMax(numbers: number[]) {\n    return Math.max(...numbers);\n}"
    leftover_fixture_tests = "it('returns a user display name', () => { expect(getUserName({profile: null})).toBe(''); });"
    matching_tests = "it('finds max number', () => { expect(findMax([1, 5, 2])).toBe(5); });"

    assert are_tests_compatible(code, leftover_fixture_tests) is False
    assert are_tests_compatible(code, matching_tests) is True
    assert are_tests_compatible(code, "") is False

