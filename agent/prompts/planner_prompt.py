"""Planner prompt and Pydantic output model definition."""

from __future__ import annotations

from typing import Any
from pydantic import BaseModel, Field


class PlanOutput(BaseModel):
    """Structured plan output schema for Planner agent."""

    approach: str = Field(
        ...,
        description="High-level step-by-step algorithmic strategy to implement the function.",
    )
    edge_cases: list[str] = Field(
        ...,
        description="List of specific edge cases and boundary conditions to handle.",
    )
    complexity_target: str = Field(
        ...,
        description="Expected Big-O time and space complexity (e.g. 'O(N) Time, O(1) Space').",
    )


PLANNER_SYSTEM_PROMPT = """You are an expert algorithms and data structures software architect.
Given a function specification (title, function signature, docstring, constraints, and examples), analyze the problem and generate a structured algorithmic plan.

Your response MUST follow the strict JSON schema provided.

Guidelines:
1. 'approach': Provide a clear, detailed, step-by-step explanation of the optimal algorithm.
2. 'edge_cases': List all potential edge cases, boundary conditions, and invalid inputs.
3. 'complexity_target': Specify optimal Time and Space Big-O targets.
"""


def format_planner_user_prompt(spec: dict[str, Any]) -> str:
    """Format the spec data into the user prompt string."""
    title = spec.get("title", spec.get("id", "Unknown Problem"))
    signature = spec.get("signature", spec.get("function_name", "solution"))
    docstring = spec.get("docstring", "")
    constraints = spec.get("constraints", [])
    examples = spec.get("examples", [])

    prompt_parts = [
        f"Problem Title: {title}",
        f"Function Signature: {signature}",
        f"Docstring / Description:\n{docstring}",
    ]

    if constraints:
        prompt_parts.append(f"Constraints:\n" + "\n".join(f"- {c}" for c in constraints))

    if examples:
        prompt_parts.append(f"Examples:\n{examples}")

    return "\n\n".join(prompt_parts)
