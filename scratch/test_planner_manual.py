"""Manual test script to run planner_node on spec_01.json."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from agent.nodes.planner import planner_node
from agent.state import initial_state


def main():
    spec_path = ROOT / "specs" / "spec_01.json"
    if not spec_path.exists():
        print(f"Error: {spec_path} does not exist.")
        return

    spec = json.loads(spec_path.read_text(encoding="utf-8"))
    state = initial_state(spec)

    print(f"Running planner_node on {spec.get('id')} ({spec.get('title')})...")
    result = planner_node(state)

    print("\nResult status:", result.get("status"))
    print("\nGenerated Plan:")
    print(json.dumps(result.get("plan"), indent=2))


if __name__ == "__main__":
    main()
