"""Pipeline bridge: connects Streamlit UI to the LangGraph agent without modifying core logic."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Generator

ROOT = Path(__file__).resolve().parent.parent

from agent.graph import build_graph
from agent.state import AgentState, initial_state


def load_archived_traces() -> list[dict[str, Any]]:
    """Load all 8 archived spec runs from traces/final_run/."""
    traces_dir = ROOT / "traces" / "final_run"
    archive_dir = traces_dir / "generated_archive"
    records: list[dict[str, Any]] = []

    for i in range(1, 9):
        spec_id = f"spec_{i:02d}"
        trace_file = traces_dir / f"{spec_id}.json"
        if not trace_file.exists():
            continue

        data = json.loads(trace_file.read_text(encoding="utf-8"))

        # Look up attempt 1 and attempt 2 files if present
        attempt_1_file = archive_dir / f"{spec_id}_attempt_1.py"
        attempt_2_file = archive_dir / f"{spec_id}_attempt_2.py"

        data["attempt_1_code"] = attempt_1_file.read_text(encoding="utf-8") if attempt_1_file.exists() else ""
        data["attempt_2_code"] = attempt_2_file.read_text(encoding="utf-8") if attempt_2_file.exists() else ""

        records.append(data)

    return records


def run_single_spec(spec_id: str) -> Generator[dict[str, Any], None, None]:
    """
    Run the LangGraph pipeline on a spec and yield intermediate node states.

    Yields dicts with:
        {"node": str, "state": AgentState}
    """
    spec_path = ROOT / "specs" / f"{spec_id}.json"
    if not spec_path.exists():
        raise FileNotFoundError(f"Spec file not found: {spec_path}")

    spec = json.loads(spec_path.read_text(encoding="utf-8"))

    # Reset state cleanly to prevent any session leaks
    state = initial_state(spec)

    app = build_graph()

    for chunk in app.stream(state, stream_mode="updates"):
        for node_name, node_update in chunk.items():
            # Update state with node output
            state = {**state, **node_update}
            yield {
                "node": node_name,
                "update": node_update,
                "state": state,
            }
