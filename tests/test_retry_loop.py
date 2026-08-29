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


def test_route_passed_returns_end():
    state = initial_state()
    state["status"] = "passed"
    state["iteration_count"] = 1
    assert route_after_tester(state) == "__end__"


def test_route_error_returns_end():
    state = initial_state()
    state["status"] = "error"
    state["iteration_count"] = 1
    assert route_after_tester(state) == "__end__"


def test_route_failed_under_max_returns_coder_node():
    state = initial_state()
    state["status"] = "failed"
    state["iteration_count"] = 1
    assert route_after_tester(state) == "coder_node"

    state["iteration_count"] = 2
    assert route_after_tester(state) == "coder_node"


def test_route_failed_at_max_returns_end():
    state = initial_state()
    state["status"] = "failed"
    state["iteration_count"] = MAX_ITERATIONS
    assert route_after_tester(state) == "__end__"

    state["iteration_count"] = MAX_ITERATIONS + 1
    assert route_after_tester(state) == "__end__"
