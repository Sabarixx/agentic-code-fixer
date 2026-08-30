"""Pytest test suite for Refactor Node and Discard-on-Regression logic."""

from __future__ import annotations

import json
import sys
import textwrap
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from agent.nodes.refactor import refactor_node
from agent.state import initial_state

SPEC_01_PATH = ROOT / "specs" / "spec_01.json"


@pytest.fixture
def spec_01():
    return json.loads(SPEC_01_PATH.read_text(encoding="utf-8"))


def test_refactor_node_keeps_valid_refactor(spec_01, monkeypatch):
    """Test that refactor_node updates status to 'refactored' when candidate passes tests."""
    passing_code = textwrap.dedent("""\
        def two_sum(nums: list[int], target: int) -> list[int]:
            seen = {}
            for i, n in enumerate(nums):
                diff = target - n
                if diff in seen:
                    return [seen[diff], i]
                seen[n] = i
            return []
    """)

    state = initial_state(spec_01)
    state["code"] = passing_code
    state["status"] = "passed"
    state["iteration_count"] = 1

    # Mock get_llm to return clean refactored code
    clean_refactored = textwrap.dedent("""\
        def two_sum(nums: list[int], target: int) -> list[int]:
            lookup: dict[int, int] = {}
            for idx, num in enumerate(nums):
                needed = target - num
                if needed in lookup:
                    return [lookup[needed], idx]
                lookup[num] = idx
            return []
    """)

    class DummyResponse:
        content = f"```python\n{clean_refactored}\n```"

    class DummyLLM:
        def invoke(self, messages):
            return DummyResponse()

    monkeypatch.setattr("agent.nodes.refactor.get_llm", lambda: DummyLLM())

    result = refactor_node(state)
    assert result["status"] == "refactored"
    assert result["has_refactored"] is True
    assert result["refactor_discarded"] is False
    assert "lookup" in result["code"]


def test_refactor_node_reverts_on_regression(spec_01, monkeypatch):
    """Test discard-on-regression: if refactoring breaks code, node reverts to original."""
    passing_code = textwrap.dedent("""\
        def two_sum(nums: list[int], target: int) -> list[int]:
            seen = {}
            for i, n in enumerate(nums):
                diff = target - n
                if diff in seen:
                    return [seen[diff], i]
                seen[n] = i
            return []
    """)

    state = initial_state(spec_01)
    state["code"] = passing_code
    state["status"] = "passed"
    state["iteration_count"] = 1

    # Mock LLM returning broken code (returns wrong indices)
    broken_refactor = textwrap.dedent("""\
        def two_sum(nums: list[int], target: int) -> list[int]:
            return [0, 0]
    """)

    class DummyResponse:
        content = f"```python\n{broken_refactor}\n```"

    class DummyLLM:
        def invoke(self, messages):
            return DummyResponse()

    monkeypatch.setattr("agent.nodes.refactor.get_llm", lambda: DummyLLM())

    result = refactor_node(state)
    assert result["status"] == "passed"
    assert result["has_refactored"] is True
    assert result["refactor_discarded"] is True
    assert result["code"] == passing_code
