"""Prompts for the Polyglot Multi-Language Custom Code Debugging and Autonomous Repair Pipeline."""

from __future__ import annotations

from pydantic import BaseModel, Field


class DiagnosisResult(BaseModel):
    """Structured output for the code diagnosis phase."""
    bug_category: str = Field(
        description="Concise category of the bug, e.g. 'Null / Undefined Property Dereference', 'ZeroDivisionError', 'Boundary Condition', 'Syntax Error', 'Type Error'"
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
        description="Key edge cases that must be handled (e.g. empty inputs, null/undefined, boundary values)."
    )


DIAGNOSIS_SYSTEM_PROMPT = """You are an expert polyglot software engineer and static analysis specialist.
Your task is to analyze user-submitted code in TypeScript, JavaScript, Python, or other languages, understand its intended behavior, review any provided error messages or test contracts, and identify the root cause of any bugs, runtime exceptions, logical errors, or unhandled null/undefined/edge cases.

CRITICAL ALIGNMENT RULE:
Compare the submitted code with the provided tests. If the tests refer to functions, symbols, or logic that are completely absent from the source code (e.g., source is about binary search but tests are about user profiles), the tests are MISMATCHED. In this case, prioritize the INTENT of the source code and treat the tests as noise. Your diagnosis should highlight this mismatch.

Be precise, specific, and actionable. Never provide placeholder or generic text.
Analyze how the code executes line-by-line and identify all conditions under which it fails.
Output valid JSON matching the DiagnosisResult schema.
"""


def format_diagnosis_prompt(
    code: str,
    language: str = "typescript",
    expected_behavior: str = "",
    error_message: str = "",
    user_tests: str = "",
) -> str:
    lang = language.lower().strip()
    parts = [
        f"### User Submitted Code ({lang}):\n```{lang}",
        code.strip(),
        "```\n",
    ]
    if expected_behavior.strip():
        parts.extend(["### Expected Behavior:\n", expected_behavior.strip(), "\n"])
    if error_message.strip():
        parts.extend(["### Error Message / Traceback:\n```", error_message.strip(), "```\n"])
    if user_tests.strip():
        parts.extend([f"### User-Supplied Tests / Expectations:\n```{lang}", user_tests.strip(), "```\n"])

    parts.append(
        f"Diagnose the bug in this {lang} code thoroughly. Identify the bug category, root cause, exact conditions where it fails, potential fixes, and edge cases to consider."
    )
    return "\n".join(parts)


TEST_GEN_SYSTEM_PROMPT = """You are an expert QA and test automation engineer.
Your goal is to write a comprehensive, rigorous unit test suite for the user's code based on the provided expected behavior, diagnosis, and code.

CRITICAL RULES:
1. For TypeScript / JavaScript:
   - Write tests using standard `it(...)` or `test(...)` with `expect(...)` assertions (e.g. `expect(fn(args)).toBe(expected)`).
   - If a function returns void or logs output, verify that calling it does not throw errors.
2. For Python:
   - Every test function must be named `test_*`.
   - Use `assert` statements.
   - For void/print functions that do not return a value, simply invoke the function to verify it executes without raising exceptions (e.g. `say_hello()`).
3. Write REAL, MEANINGFUL assertions. NEVER assert or expect the bug/crash described in the error message!
4. Return ONLY valid executable test code enclosed in ```typescript ... ``` or ```python ... ``` corresponding to the target language.
"""


def format_test_gen_prompt(
    code: str,
    diagnosis: DiagnosisResult | dict,
    language: str = "typescript",
    expected_behavior: str = "",
    error_message: str = "",
    user_tests: str = "",
) -> str:
    lang = language.lower().strip()
    diag_str = diagnosis.summary if isinstance(diagnosis, DiagnosisResult) else str(diagnosis)
    root_cause = diagnosis.root_cause if isinstance(diagnosis, DiagnosisResult) else str(diagnosis.get("root_cause", ""))
    edge_cases = ", ".join(diagnosis.edge_cases if isinstance(diagnosis, DiagnosisResult) else diagnosis.get("edge_cases", []))

    parts = [
        f"### Target Code Under Test ({lang}):\n```{lang}",
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
        parts.append(f"### User Supplied Tests:\n```{lang}\n{user_tests.strip()}\n```\n")

    parts.append(f"Generate a complete {lang} test suite with 2 to 4 targeted, rigorous unit tests verifying the EXPECTED behavior.")
    return "\n".join(parts)


REPAIR_SYSTEM_PROMPT = """You are an expert polyglot software engineer specializing in autonomous bug repair.
Your goal is to produce a fully corrected, robust, and clean implementation of the user's code.

CRITICAL RULES:
1. PRESERVE THE COMPLETE CODE STRUCTURE, INPUTS, AND OUTPUT FORMAT:
   - If the user submitted a complete script with variable declarations, sample inputs, top-level calls, and print() / console.log() output statements, YOU MUST RETAIN THE ENTIRE SCRIPT with all input declarations, helper functions, invocations, and output statements in the same format.
   - If the user submitted a standalone function or class, return the standalone function or class.
   - If the user submitted imports, exports, comments, or type annotations, preserve them all.
   - NEVER discard or reduce a full script down to only a function. If the input has print statements or execution calls showing sample inputs and outputs, keep them intact and functioning.
2. Fix all logic errors, runtime crashes, nullability hazards, and unhandled edge cases identified in the diagnosis.
3. The corrected code must fulfill the intended behavior of the source code. If provided tests are completely unrelated to the source code's logic, ignore them and prioritize the original intent and format of the source.
4. For TypeScript / JavaScript: Use proper optional chaining `?.` and nullish coalescing `??` or defensive guards where null/undefined can occur.
5. For Python: Wrap standalone script executions in `if __name__ == '__main__':` guards or maintain top-level execution so tests can import safely while sample calls still run.
6. Return ONLY a single, complete, and valid executable code file in the target language enclosed in code fences. Do not return fragments, multiple unrelated functions, or conversational prose.
"""


def format_repair_prompt(
    original_code: str,
    diagnosis: DiagnosisResult | dict,
    language: str = "typescript",
    expected_behavior: str = "",
    test_code: str = "",
    previous_attempt_code: str = "",
    failure_details: list[str] | None = None,
    attempt: int = 1,
) -> str:
    lang = language.lower().strip()
    root_cause = diagnosis.root_cause if isinstance(diagnosis, DiagnosisResult) else str(diagnosis.get("root_cause", ""))
    parts = [
        f"### Original Code ({lang}):\n```{lang}",
        original_code.strip(),
        "```\n",
        f"### Root Cause Diagnosis:\n{root_cause}\n",
    ]
    if expected_behavior.strip():
        parts.append(f"### Expected Behavior:\n{expected_behavior.strip()}\n")
    if test_code.strip():
        parts.append(f"### Test Suite It Must Pass:\n```{lang}\n{test_code.strip()}\n```\n")

    if attempt > 1 and previous_attempt_code:
        parts.append(f"### Previous Attempt (Attempt {attempt - 1}):\n```{lang}\n{previous_attempt_code.strip()}\n```\n")
        if failure_details:
            parts.append("### Failed Test Feedback / Traceback:\n" + "\n".join(failure_details) + "\n")
        parts.append("Analyze the failed test feedback and correct the code so all tests pass. Remember to preserve the original code structure, input declarations, and output/print statements.")
    else:
        parts.append(f"Generate the complete corrected {lang} code. Preserve the exact structure, input data, helper functions, and print/output statements of the original code.")

    return "\n".join(parts)

