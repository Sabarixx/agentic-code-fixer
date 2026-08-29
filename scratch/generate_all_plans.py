"""Script to run planner_node on all 8 specs and save traces to traces/week2_plans/."""

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
    traces_dir = ROOT / "traces" / "week2_plans"
    traces_dir.mkdir(parents=True, exist_ok=True)

    specs_dir = ROOT / "specs"
    spec_files = sorted(specs_dir.glob("spec_*.json"))

    print(f"Found {len(spec_files)} spec files. Generating plans...")

    success_count = 0
    for spec_path in spec_files:
        spec = json.loads(spec_path.read_text(encoding="utf-8"))
        spec_id = spec.get("id", spec_path.stem)
        print(f"Processing {spec_id} ({spec.get('title')})...")

        state = initial_state(spec)
        result = planner_node(state)

        if result.get("status") == "planning" and isinstance(result.get("plan"), dict):
            output_file = traces_dir / f"{spec_id}.json"
            output_file.write_text(json.dumps(result["plan"], indent=2), encoding="utf-8")
            print(f"  [OK] Saved to {output_file.relative_to(ROOT)}")
            success_count += 1
        else:
            print(f"  [FAIL] Failed for {spec_id}: {result.get('plan')}")

    print(f"\nCompleted: {success_count}/{len(spec_files)} plans successfully generated and saved.")


if __name__ == "__main__":
    main()
