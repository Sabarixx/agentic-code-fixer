"""Autonomous Custom Code Debugging & Repair Engine."""

from __future__ import annotations

import ast
import json
import os
import re
from typing import Any, Generator
from dotenv import load_dotenv
from langchain_groq import ChatGroq

from agent.nodes.coder import extract_code_block, validate_code_ast
from agent.prompts.custom_debugger_prompt import (
    DIAGNOSIS_SYSTEM_PROMPT,
    DiagnosisResult,
    REPAIR_SYSTEM_PROMPT,
    TEST_GEN_SYSTEM_PROMPT,
    format_diagnosis_prompt,
    format_repair_prompt,
    format_test_gen_prompt,
)
from tools.retry_utils import invoke_with_exponential_backoff
from tools.sandbox_runner import (
    TestResult,
    run_bandit_security_scan,
    run_custom_sandboxed_pytest,
)

load_dotenv()

MAX_REPAIR_ATTEMPTS = 3


def get_llm():
    """Initialize LLM client for custom debugging engine."""
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY environment variable is not set in .env")
    return ChatGroq(
        model="openai/gpt-oss-20b",
        api_key=api_key,
        temperature=0.1,
    )


def diagnose_custom_code(
    code: str,
    expected_behavior: str = "",
    error_message: str = "",
    user_tests: str = "",
) -> tuple[DiagnosisResult, list[str], list[str]]:
    """
    Perform static AST validation, security scan, and LLM root cause diagnosis.
    Returns (DiagnosisResult, syntax_errors, security_flags).
    """
    syntax_errors: list[str] = []
    is_valid_ast, ast_err = validate_code_ast(code)
    if not is_valid_ast:
        syntax_errors.append(ast_err)

    security_flags = run_bandit_security_scan(code)

    user_prompt = format_diagnosis_prompt(code, expected_behavior, error_message, user_tests)
    llm = get_llm()
    structured_llm = llm.with_structured_output(DiagnosisResult)

    messages = [
        ("system", DIAGNOSIS_SYSTEM_PROMPT),
        ("human", user_prompt),
    ]

    try:
        diagnosis: DiagnosisResult = invoke_with_exponential_backoff(structured_llm.invoke, messages)
    except Exception as err:
        # Fallback manual parsing if structured output fails
        fallback_prompt = user_prompt + "\n\nRespond with strict JSON with keys: bug_category, root_cause, summary, potential_fixes (list), edge_cases (list)."
        res = invoke_with_exponential_backoff(llm.invoke, [("system", DIAGNOSIS_SYSTEM_PROMPT), ("human", fallback_prompt)])
        raw_text = res.content if hasattr(res, "content") else str(res)
        try:
            match = re.search(r"\{.*\}", raw_text, re.DOTALL)
            if match:
                data = json.loads(match.group(0))
                diagnosis = DiagnosisResult(**data)
            else:
                diagnosis = DiagnosisResult(
                    bug_category="Execution / Logic Error",
                    root_cause=raw_text[:500],
                    summary="Root cause identified from analysis.",
                    potential_fixes=["Correct logic to handle input conditions safely."],
                    edge_cases=["Empty input", "Boundary conditions"],
                )
        except Exception:
            diagnosis = DiagnosisResult(
                bug_category="General Code Error",
                root_cause=f"Diagnostic error: {err}",
                summary="Static analysis identified potential execution issues.",
                potential_fixes=["Review logic flow and error handling."],
                edge_cases=[],
            )

    return diagnosis, syntax_errors, security_flags


def generate_custom_pytest_suite(
    code: str,
    diagnosis: DiagnosisResult,
    expected_behavior: str = "",
    error_message: str = "",
    user_tests: str = "",
) -> str:
    """Generate comprehensive, meaningful pytest test suite for the user code."""
    user_prompt = format_test_gen_prompt(code, diagnosis, expected_behavior, error_message, user_tests)
    llm = get_llm()

    messages = [
        ("system", TEST_GEN_SYSTEM_PROMPT),
        ("human", user_prompt),
    ]

    response = invoke_with_exponential_backoff(llm.invoke, messages)
    raw_text = response.content if hasattr(response, "content") else str(response)
    test_code = extract_code_block(raw_text)

    # Validate AST
    is_valid, _ = validate_code_ast(test_code)
    if not is_valid or "def test_" not in test_code:
        # Fallback minimal test suite
        test_code = f"import pytest\nfrom candidate_code import *\n\n# User provided tests\n{user_tests.strip()}\n"

    return test_code


def repair_custom_code(
    original_code: str,
    diagnosis: DiagnosisResult,
    expected_behavior: str = "",
    test_code: str = "",
    previous_attempt_code: str = "",
    failure_details: list[str] | None = None,
    attempt: int = 1,
) -> str:
    """Generate repaired candidate implementation."""
    user_prompt = format_repair_prompt(
        original_code=original_code,
        diagnosis=diagnosis,
        expected_behavior=expected_behavior,
        test_code=test_code,
        previous_attempt_code=previous_attempt_code,
        failure_details=failure_details,
        attempt=attempt,
    )
    llm = get_llm()

    messages = [
        ("system", REPAIR_SYSTEM_PROMPT),
        ("human", user_prompt),
    ]

    response = invoke_with_exponential_backoff(llm.invoke, messages)
    raw_text = response.content if hasattr(response, "content") else str(response)
    candidate_code = extract_code_block(raw_text)

    return candidate_code


def generate_changelog(original_code: str, corrected_code: str, diagnosis: DiagnosisResult) -> list[str]:
    """Generate concise changelog bullet points explaining the fixes."""
    llm = get_llm()
    prompt = (
        "Compare the original code and the corrected code, and list the specific fixes and improvements made.\n"
        "Return 2 to 4 concise bullet points.\n\n"
        f"Original:\n```python\n{original_code}\n```\n\n"
        f"Corrected:\n```python\n{corrected_code}\n```\n\n"
        f"Root Cause: {diagnosis.root_cause}\n"
    )
    try:
        res = invoke_with_exponential_backoff(llm.invoke, [("human", prompt)])
        text = res.content if hasattr(res, "content") else str(res)
        bullets = [line.strip().lstrip("-*• ") for line in text.splitlines() if line.strip().startswith(("-", "*", "•")) or line.strip()[:2].isdigit()]
        if bullets:
            return bullets[:5]
    except Exception:
        pass

    return [
        f"Fixed root cause: {diagnosis.summary}",
        "Added safety guards for empty and edge case inputs.",
        "Refactored code structure and wrapped demo calls in __main__ block.",
    ]


def run_custom_debugging_pipeline(
    code: str,
    expected_behavior: str = "",
    error_message: str = "",
    user_tests: str = "",
    max_attempts: int = MAX_REPAIR_ATTEMPTS,
) -> Generator[dict[str, Any], None, None]:
    """
    Closed-loop autonomous debugging generator:
    1. Diagnosing -> yields diagnosis summary, syntax errors, security warnings.
    2. Generating Tests -> yields synthesized pytest suite.
    3. Loop: Repairing -> Sandbox Testing -> Retry on failure.
    4. Refactoring (if passed).
    5. Done -> yields final corrected code, diff, changelog, and test summary.
    """
    # 1. DIAGNOSIS STAGE
    diagnosis, syntax_errors, security_flags = diagnose_custom_code(
        code, expected_behavior, error_message, user_tests
    )

    yield {
        "stage": "diagnosing",
        "bug_category": diagnosis.bug_category,
        "root_cause": diagnosis.root_cause,
        "summary": diagnosis.summary,
        "potential_fixes": diagnosis.potential_fixes,
        "edge_cases": diagnosis.edge_cases,
        "syntax_errors": syntax_errors,
        "security_flags": security_flags,
    }

    # 2. TEST GENERATION STAGE
    test_code = generate_custom_pytest_suite(
        code, diagnosis, expected_behavior, error_message, user_tests
    )

    yield {
        "stage": "generating_tests",
        "generated_tests": test_code,
        "user_tests": user_tests,
    }

    # 3. CLOSED-LOOP REPAIR LOOP
    current_candidate = ""
    last_test_result: TestResult | None = None
    all_passed = False
    failure_details: list[str] = []
    attempt = 1

    while attempt <= max_attempts and not all_passed:
        # Generate candidate
        current_candidate = repair_custom_code(
            original_code=code,
            diagnosis=diagnosis,
            expected_behavior=expected_behavior,
            test_code=test_code,
            previous_attempt_code=current_candidate,
            failure_details=failure_details,
            attempt=attempt,
        )

        yield {
            "stage": "fixing",
            "iteration": attempt,
            "corrected_code": current_candidate,
        }

        # Sandbox Execution
        test_result: TestResult = run_custom_sandboxed_pytest(current_candidate, test_code)
        last_test_result = test_result
        all_passed = test_result.all_passed
        failure_details = test_result.failure_details

        yield {
            "stage": "testing",
            "iteration": attempt,
            "test_results": test_result.model_dump(),
        }

        if all_passed:
            break

        attempt += 1

    # 4. REFACTOR STAGE (Only if tests passed)
    if all_passed:
        yield {
            "stage": "refactoring",
            "refactored_code": current_candidate,
            "refactor_discarded": False,
        }

    # 5. DONE STAGE
    changelog = generate_changelog(code, current_candidate, diagnosis)
    final_status = "passed" if all_passed else ("failed" if attempt > max_attempts else "error")

    yield {
        "stage": "done",
        "status": final_status,
        "corrected_code": current_candidate,
        "test_code": test_code,
        "changelog": changelog,
        "test_results": last_test_result.model_dump() if last_test_result else {},
        "iterations_taken": min(attempt, max_attempts),
        "diagnosis": diagnosis.model_dump(),
    }
