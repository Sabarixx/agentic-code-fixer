"""Pytest test suite for Router and Conditional Retry Loop."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from agent.router import route_after_tester
from agent.state import MAX_ITERATIONS, initial_state


def test_route_passed_routes_to_refactor_first():
    """Week 6: status=passed with no prior refactor routes to refactor_node."""
    state = initial_state()
    state["status"] = "passed"
    state["iteration_count"] = 1
    state["has_refactored"] = False
    assert route_after_tester(state) == "refactor_node"


def test_route_passed_after_refactor_returns_end():
    """Week 6: status=passed with has_refactored=True routes to __end__."""
    state = initial_state()
    state["status"] = "passed"
    state["iteration_count"] = 1
    state["has_refactored"] = True
    assert route_after_tester(state) == "__end__"


def test_route_error_returns_end():
    state = initial_state()
    state["status"] = "error"
    state["iteration_count"] = 1
    assert route_after_tester(state) == "__end__"


def test_route_failed_under_max_returns_debugger_node():
    state = initial_state()
    state["status"] = "failed"
    state["iteration_count"] = 1
    assert route_after_tester(state) == "debugger_node"

    state["iteration_count"] = 2
    assert route_after_tester(state) == "debugger_node"



def test_route_failed_at_max_returns_end():
    state = initial_state()
    state["status"] = "failed"
    state["iteration_count"] = MAX_ITERATIONS
    assert route_after_tester(state) == "__end__"

    state["iteration_count"] = MAX_ITERATIONS + 1
    assert route_after_tester(state) == "__end__"
