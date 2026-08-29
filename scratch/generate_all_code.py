"""Batch script to run Planner -> Coder pipeline on all 8 specs and write generated files."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from agent.nodes.coder import coder_node, validate_code_ast
from agent.nodes.planner import planner_node
from agent.state import initial_state


def main():
    specs_dir = ROOT / "specs"
    spec_files = sorted(specs_dir.glob("spec_*.json"))

    print(f"Found {len(spec_files)} spec files. Running Planner -> Coder pipeline...")

    success_count = 0
    for spec_path in spec_files:
        spec = json.loads(spec_path.read_text(encoding="utf-8"))
        spec_id = spec.get("id", spec_path.stem)
        print(f"Processing {spec_id} ({spec.get('title')})...")

        state = initial_state(spec)

        # 1. Planner node
        p_res = planner_node(state)
        state.update(p_res)

        # 2. Coder node
        c_res = coder_node(state)
        state.update(c_res)

        code = state.get("code", "")
        status = state.get("status")

        is_valid, ast_err = validate_code_ast(code)

        if is_valid and status == "coding":
            print(f"  [OK] Valid AST. Generated file: generated/{spec_id}_attempt_1.py")
            success_count += 1
        else:
            print(f"  [FAIL] Syntax/AST error for {spec_id}: {ast_err}")

    print(f"\nCompleted: {success_count}/{len(spec_files)} code implementations generated and validated.")


if __name__ == "__main__":
    main()
