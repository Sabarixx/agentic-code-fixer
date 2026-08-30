"""Routing functions for conditional graph edges including refactor pass."""

from __future__ import annotations

from typing import Literal

from agent.state import MAX_ITERATIONS, AgentState


def route_after_tester(state: AgentState) -> Literal["coder_node", "refactor_node", "__end__"]:
    """
    Conditional routing function after tester_node:
    - If status is 'passed' and refactor hasn't run yet -> 'refactor_node'
    - If status is 'refactored', 'passed' (post-refactor), or 'error' -> '__end__'
    - If iteration_count >= MAX_ITERATIONS -> '__end__'
    - Otherwise (tests failed and under MAX_ITERATIONS) -> 'coder_node'
    """
    status = state.get("status")
    iteration_count = state.get("iteration_count", 0)
    has_refactored = state.get("has_refactored", False)

    if status == "refactored":
        return "__end__"

    if status == "passed":
        if not has_refactored:
            return "refactor_node"
        return "__end__"

    if status == "error":
        return "__end__"

    if iteration_count >= MAX_ITERATIONS:
        return "__end__"

    return "coder_node"
