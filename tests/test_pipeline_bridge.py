"""Tests for UI pipeline bridge."""

from __future__ import annotations

import pytest
from ui.pipeline_bridge import load_archived_traces, run_single_spec


def test_load_archived_traces_returns_8_specs():
    """Confirms all 8 archived specs are loaded with required fields."""
    traces = load_archived_traces()
    assert len(traces) == 8, f"Expected 8 archived specs, got {len(traces)}"

    for t in traces:
        assert "spec_id" in t
        assert "title" in t
        assert "final_status" in t
        assert t["final_status"] in ("passed", "refactored")
        assert "test_results" in t
        assert t["test_results"]["all_passed"] is True


def test_invalid_spec_id_raises():
    """Confirms requesting a nonexistent spec raises FileNotFoundError."""
    with pytest.raises(FileNotFoundError):
        list(run_single_spec("spec_999"))


def test_archived_traces_contain_code():
    """Confirms attempts or final code are extracted properly."""
    traces = load_archived_traces()
    spec_01 = next((t for t in traces if t["spec_id"] == "spec_01"), None)
    assert spec_01 is not None
    assert "two_sum" in (spec_01.get("final_code") or "")
