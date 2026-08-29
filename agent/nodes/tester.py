"""Tester Node: executes sandboxed pytest against generated code and updates AgentState."""

from __future__ import annotations

from typing import Any

from agent.state import AgentState
from tools.sandbox_runner import TestResult, run_sandboxed_pytest


def tester_node(state: AgentState) -> dict[str, Any]:
    """LangGraph Tester Node: runs generated code against spec test suite in sandbox."""
    spec = state.get("spec") or {}
    spec_id = spec.get("id", "spec_unknown")
    iteration_count = state.get("iteration_count", 1)

    result: TestResult = run_sandboxed_pytest(spec_id, iteration_count)
    result_dict = result.model_dump()

    if result.timed_out or result.error:
        status = "error"
    elif result.all_passed:
        status = "passed"
    else:
        status = "failed"

    return {
        "status": status,
        "test_results": result_dict,
    }
