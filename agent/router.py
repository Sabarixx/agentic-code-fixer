"""Routing functions for conditional graph edges."""

from __future__ import annotations

from typing import Literal

from agent.state import MAX_ITERATIONS, AgentState


def route_after_tester(state: AgentState) -> Literal["coder_node", "__end__"]:
    """
    Conditional routing function after tester_node:
    - If status is 'passed' or 'error' -> END
    - If iteration_count >= MAX_ITERATIONS -> END (stops on 'failed')
    - Otherwise (tests failed and iteration_count < MAX_ITERATIONS) -> retry 'coder_node'
    """
    status = state.get("status")
    iteration_count = state.get("iteration_count", 0)

    if status == "passed" or status == "error":
        return "__end__"

    if iteration_count >= MAX_ITERATIONS:
        return "__end__"

    return "coder_node"
