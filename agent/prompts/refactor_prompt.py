"""Refactor Agent prompt templates."""

from __future__ import annotations

from typing import Any

REFACTOR_SYSTEM_PROMPT = """You are an expert Python software refactoring engineer.
Your task is to improve the readability, variable naming, and structure of a Python function that is ALREADY PASSING all unit tests.

CRITICAL INSTRUCTIONS:
1. Do NOT change the function's algorithmic behavior, logic, or signature.
2. Return ONLY the improved Python code inside a markdown code block (```python ... ```).
3. Do NOT include any conversational prose before or after the code block.
4. Add clear type hints, concise inline docstrings, and clean variable names.
"""


def format_refactor_user_prompt(spec: dict[str, Any], code: str) -> str:
    """Format spec and current passing code into the refactor user prompt."""
    title = spec.get("title", spec.get("id", "Unknown Problem"))
    signature = spec.get("signature", spec.get("function_name", "solution"))

    prompt_parts = [
        f"Problem Title: {title}",
        f"Function Signature: {signature}",
        f"Current Verified Code:\n```python\n{code}\n```",
        "Please provide an improved, refactored version of this code now:",
    ]

    return "\n\n".join(prompt_parts)
