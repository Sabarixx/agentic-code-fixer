"""Pytest suite for Planner Agent node."""

from __future__ import annotations

import json
from pathlib import Path
import pytest

from agent.nodes.planner import planner_node
from agent.state import initial_state

ROOT = Path(__file__).resolve().parent.parent
SPEC_FILES = sorted((ROOT / "specs").glob("spec_*.json"))


@pytest.mark.parametrize("spec_path", SPEC_FILES, ids=lambda p: p.stem)
def test_planner_node_returns_valid_plan_schema(spec_path: Path):
    """Test that planner_node produces a valid PlanOutput-shaped dict for every curated spec."""
    assert spec_path.exists(), f"Spec file missing: {spec_path}"
    spec = json.loads(spec_path.read_text(encoding="utf-8"))

    state = initial_state(spec)
    result = planner_node(state)

    assert result["status"] == "planning"
    assert "plan" in result
    plan = result["plan"]

    assert isinstance(plan, dict), f"Expected dict for plan, got {type(plan)}"
    assert "approach" in plan and isinstance(plan["approach"], str) and len(plan["approach"]) > 0
    assert "edge_cases" in plan and isinstance(plan["edge_cases"], list)
    assert "complexity_target" in plan and isinstance(plan["complexity_target"], str) and len(plan["complexity_target"]) > 0


def test_planner_node_empty_spec():
    """Test that planner_node handles empty spec gracefully without crashing."""
    state = initial_state({})
    result = planner_node(state)
    assert result["status"] in ("planning", "error")
    assert "plan" in result
