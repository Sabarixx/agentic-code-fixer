"""Coder Agent prompt templates."""

from __future__ import annotations

from typing import Any

CODER_SYSTEM_PROMPT = """You are an expert Python software engineer.
Your task is to write a clean, efficient, and complete Python function matching the given specification and algorithmic plan.

CRITICAL INSTRUCTIONS:
1. Return ONLY executable Python code inside a markdown code block (```python ... ```).
2. Do NOT include any introductory or concluding conversational prose.
3. Your code MUST define the function with the exact signature specified.
4. Include necessary imports (e.g. typing, collections, heapq) at the top of the code block.
"""


def format_coder_user_prompt(spec: dict[str, Any], plan: dict[str, Any] | str) -> str:
    """Format spec and plan into the coder user prompt."""
    title = spec.get("title", spec.get("id", "Unknown Problem"))
    signature = spec.get("signature", spec.get("function_name", "solution"))
    docstring = spec.get("docstring", "")
    constraints = spec.get("constraints", [])

    if isinstance(plan, dict):
        approach = plan.get("approach", "")
        edge_cases = plan.get("edge_cases", [])
        complexity = plan.get("complexity_target", "")
        plan_str = (
            f"Approach:\n{approach}\n\n"
            f"Edge Cases to Handle:\n" + "\n".join(f"- {ec}" for ec in edge_cases) + "\n\n"
            f"Target Complexity: {complexity}"
        )
    else:
        plan_str = str(plan)

    prompt_parts = [
        f"Problem Title: {title}",
        f"Required Function Signature:\n```python\n{signature}\n```",
        f"Docstring / Specification:\n{docstring}",
    ]

    if constraints:
        prompt_parts.append("Constraints:\n" + "\n".join(f"- {c}" for c in constraints))

    prompt_parts.append(f"Algorithmic Strategy Plan:\n{plan_str}")
    prompt_parts.append("Please write the complete Python function implementation now:")

    return "\n\n".join(prompt_parts)


def format_coder_retry_prompt(
    spec: dict[str, Any],
    plan: dict[str, Any] | str,
    previous_code: str,
    test_results: dict[str, Any],
    diagnosis: dict[str, Any] | None = None,
) -> str:
    """Format retry prompt including previous code, failure tracebacks, and deep diagnosis."""
    base_prompt = format_coder_user_prompt(spec, plan)

    failures = test_results.get("failure_details", [])
    failure_msg = "\n".join(failures[:5]) if failures else "Unit tests failed."

    retry_parts = [
        base_prompt,
    ]

    if diagnosis:
        diag_section = (
            "--- DEEP DIAGNOSIS ---\n"
            f"Bug Category: {diagnosis.get('bug_category', 'Unknown')}\n"
            f"Root Cause: {diagnosis.get('root_cause', 'Not identified')}\n"
            f"Summary: {diagnosis.get('summary', 'N/A')}\n"
            "Suggested Fixes:\n" + "\n".join(f"- {f}" for f in diagnosis.get("potential_fixes", [])) + "\n"
            "Edge Cases to Consider:\n" + "\n".join(f"- {e}" for e in diagnosis.get("edge_cases", []))
        )
        retry_parts.append(diag_section)

    retry_parts.extend([
        "--- PREVIOUS ATTEMPT (FAILED UNIT TESTS) ---",
        f"```python\n{previous_code}\n```",
        "--- TEST FAILURE DETAILS / TRACEBACK ---",
        failure_msg,
        "--- REPAIR INSTRUCTIONS ---",
        "Analyze the test failure details and the deep diagnosis provided above and fix the bug in your previous code.",
        "Ensure your fix addresses the specific failure case while maintaining the required signature.",
        "Return ONLY the updated executable Python code inside a ```python ... ``` code block.",
    ])

    return "\n\n".join(retry_parts)

