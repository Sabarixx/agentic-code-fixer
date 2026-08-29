"""Manual test script to run planner_node -> coder_node on spec_01.json."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from agent.nodes.coder import coder_node
from agent.nodes.planner import planner_node
from agent.state import initial_state


def main():
    spec_path = ROOT / "specs" / "spec_01.json"
    spec = json.loads(spec_path.read_text(encoding="utf-8"))

    state = initial_state(spec)
    print("1. Running planner_node...")
    planner_result = planner_node(state)
    state.update(planner_result)

    print("2. Running coder_node...")
    coder_result = coder_node(state)

    print("\nResult status:", coder_result.get("status"))
    print("\nGenerated Code:")
    print(coder_result.get("code"))


if __name__ == "__main__":
    main()
