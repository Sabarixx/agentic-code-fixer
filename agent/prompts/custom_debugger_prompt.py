"""Prompts for the Custom Code Debugging and Autonomous Repair Pipeline."""

from __future__ import annotations

from pydantic import BaseModel, Field


class DiagnosisResult(BaseModel):
    """Structured output for the code diagnosis phase."""
    bug_category: str = Field(
        description="Concise category of the bug, e.g. 'ZeroDivisionError / Empty List', 'Logic Error / Boundary Condition', 'Syntax Error', 'Type Error'"
    )
    root_cause: str = Field(
        description="Detailed explanation of why the code fails, referencing specific lines or logic flows."
    )
    summary: str = Field(
        description="One or two sentence summary of the issue."
    )
    potential_fixes: list[str] = Field(
        default_factory=list,
        description="List of concrete steps required to fix the code."
    )
    edge_cases: list[str] = Field(
        default_factory=list,
        description="Key edge cases that must be handled (e.g. empty inputs, negative numbers, None)."
    )


DIAGNOSIS_SYSTEM_PROMPT = """You are an expert Python debugger and static analysis specialist.
Your task is to analyze user-submitted Python code, understand its intended behavior, review any provided error messages or tracebacks, and identify the root cause of any bugs, runtime crashes, logical errors, or unhandled edge cases.

Be precise, specific, and actionable. Never provide placeholder or generic text.
Analyze how the code executes line-by-line and identify all conditions under which it fails.
"""


def format_diagnosis_prompt(
    code: str,
    expected_behavior: str = "",
    error_message: str = "",
    user_tests: str = "",
) -> str:
    parts = [
        "### User Submitted Code:\n```python",
        code.strip(),
        "```\n",
    ]
    if expected_behavior.strip():
        parts.extend(["### Expected Behavior:\n", expected_behavior.strip(), "\n"])
    if error_message.strip():
        parts.extend(["### Error Message / Traceback:\n```", error_message.strip(), "```\n"])
    if user_tests.strip():
        parts.extend(["### User-Supplied Tests / Expectations:\n```python", user_tests.strip(), "```\n"])

    parts.append(
        "Diagnose the bug thoroughly. Identify the bug category, root cause, exact conditions where it fails, potential fixes, and edge cases to consider."
    )
    return "\n".join(parts)


TEST_GEN_SYSTEM_PROMPT = """You are an expert QA and test automation engineer specializing in pytest.
Your goal is to write a comprehensive, rigorous pytest unit test suite for the user's Python code based on the provided expected behavior, diagnosis, and code.

CRITICAL RULES:
1. Every test function must be named `test_*`.
2. Tests must import the function(s) or class(es) directly from `candidate_code`, e.g.:
   `from candidate_code import <function_name>`
3. Write REAL, MEANINGFUL assertions. NEVER write trivial assertions like `assert True` or `assert 1 == 1`.
4. The test suite MUST test the EXPECTED BEHAVIOR.
   - If the user states that empty input or edge cases should be handled gracefully instead of crashing, assert that calling the function does NOT crash (e.g. returns a tuple/default or handles it without ZeroDivisionError).
   - NEVER write tests that assert or expect the bug/crash described in the error message!
5. Cover:
   - Normal / happy path inputs
   - The specific bug and edge cases (e.g. empty lists `[]`, negative numbers, single element, boundary values)
   - Handling of invalid or edge inputs without unhandled exceptions
6. If user tests were provided, incorporate and validate them.
7. Return ONLY valid Python test code enclosed in ```python ... ```.
"""


def format_test_gen_prompt(
    code: str,
    diagnosis: DiagnosisResult | dict,
    expected_behavior: str = "",
    error_message: str = "",
    user_tests: str = "",
) -> str:
    diag_str = diagnosis.summary if isinstance(diagnosis, DiagnosisResult) else str(diagnosis)
    root_cause = diagnosis.root_cause if isinstance(diagnosis, DiagnosisResult) else str(diagnosis.get("root_cause", ""))
    edge_cases = ", ".join(diagnosis.edge_cases if isinstance(diagnosis, DiagnosisResult) else diagnosis.get("edge_cases", []))

    parts = [
        "### Target Code Under Test:\n```python",
        code.strip(),
        "```\n",
        f"### Diagnosis Summary:\n{diag_str}\n",
        f"### Root Cause of Bug:\n{root_cause}\n",
    ]
    if expected_behavior.strip():
        parts.append(f"### Intended / Expected Behavior (TEST THIS):\n{expected_behavior.strip()}\n")
    if edge_cases:
        parts.append(f"### Edge Cases to Test:\n{edge_cases}\n")
    if user_tests.strip():
        parts.append(f"### User Supplied Tests:\n```python\n{user_tests.strip()}\n```\n")

    parts.append("Generate a complete pytest test file with 3 to 6 targeted, rigorous unit tests verifying the EXPECTED behavior.")
    return "\n".join(parts)


REPAIR_SYSTEM_PROMPT = """You are an expert Python software engineer specializing in autonomous bug repair.
Your goal is to produce a fully corrected, robust, and clean implementation of the user's Python code.

CRITICAL RULES:
1. Fix all logic errors, runtime crashes, and unhandled edge cases identified in the diagnosis.
2. The corrected code must fulfill the expected behavior and pass all test cases.
   - For example, if handling empty collections: add a check `if not marks:` and return an appropriate default (e.g. `(0.0, "N/A")` or `(0.0, "F")` or `0` as fits the return signature) instead of dividing by zero.
3. Preserve the original function names, signatures, and general intent unless explicitly requested otherwise.
4. If the original code contained top-level execution code or print statements (e.g., `print(calculate_average([]))`), wrap them in `if __name__ == '__main__':` so the module can be cleanly imported by pytest without executing side effects.
5. Return ONLY complete, valid, executable Python code in ```python ... ```. Do not omit code or use placeholders.
"""


def format_repair_prompt(
    original_code: str,
    diagnosis: DiagnosisResult | dict,
    expected_behavior: str = "",
    test_code: str = "",
    previous_attempt_code: str = "",
    failure_details: list[str] | None = None,
    attempt: int = 1,
) -> str:
    root_cause = diagnosis.root_cause if isinstance(diagnosis, DiagnosisResult) else str(diagnosis.get("root_cause", ""))
    parts = [
        "### Original Code:\n```python",
        original_code.strip(),
        "```\n",
        f"### Root Cause Diagnosis:\n{root_cause}\n",
    ]
    if expected_behavior.strip():
        parts.append(f"### Expected Behavior:\n{expected_behavior.strip()}\n")
    if test_code.strip():
        parts.append(f"### Pytest Suite It Must Pass:\n```python\n{test_code.strip()}\n```\n")

    if attempt > 1 and previous_attempt_code:
        parts.append(f"### Previous Attempt (Attempt {attempt - 1}):\n```python\n{previous_attempt_code.strip()}\n```\n")
        if failure_details:
            parts.append("### Failed Test Feedback / Traceback:\n" + "\n".join(failure_details) + "\n")
        parts.append("Analyze the failed test feedback and correct the code so all tests pass.")
    else:
        parts.append("Generate the complete corrected Python code.")

    return "\n".join(parts)
