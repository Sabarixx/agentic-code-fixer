"""Batch script to run full compiled retry graph on all 8 specs and log convergence traces."""

from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from agent.graph import build_graph
from agent.state import initial_state


def main():
    traces_dir = ROOT / "traces" / "week5_retry"
    traces_dir.mkdir(parents=True, exist_ok=True)

    summary_file = ROOT / "traces" / "week5_summary.csv"

    specs_dir = ROOT / "specs"
    spec_files = sorted(specs_dir.glob("spec_*.json"))

    print(f"Building compiled LangGraph workflow with conditional retry loop...")
    app = build_graph()

    summary_rows = []
    print(f"Running full retry pipeline on {len(spec_files)} specs...")

    for spec_path in spec_files:
        spec = json.loads(spec_path.read_text(encoding="utf-8"))
        spec_id = spec.get("id", spec_path.stem)
        title = spec.get("title", "Unknown")

        print(f"\n[Spec] {spec_id}: {title}", flush=True)
        state = initial_state(spec)

        result = app.invoke(state)

        final_status = result.get("status")
        iterations = result.get("iteration_count", 0)
        test_results = result.get("test_results") or {}
        passed_tests = test_results.get("passed", 0)
        total_tests = test_results.get("total", 0)

        print(f"  Final Status: {final_status}", flush=True)
        print(f"  Iterations Taken: {iterations}", flush=True)
        print(f"  Tests Passed: {passed_tests}/{total_tests}", flush=True)

        # Save trace JSON
        trace_data = {
            "spec_id": spec_id,
            "title": title,
            "final_status": final_status,
            "iterations_taken": iterations,
            "test_results": test_results,
            "plan": result.get("plan"),
            "final_code": result.get("code"),
        }
        (traces_dir / f"{spec_id}.json").write_text(
            json.dumps(trace_data, indent=2), encoding="utf-8"
        )

        summary_rows.append({
            "spec_id": spec_id,
            "title": title,
            "iterations_taken": iterations,
            "final_status": final_status,
            "passed_tests": passed_tests,
            "total_tests": total_tests,
        })

    # Write summary CSV
    with open(summary_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["spec_id", "title", "iterations_taken", "final_status", "passed_tests", "total_tests"],
        )
        writer.writeheader()
        writer.writerows(summary_rows)

    print(f"\nSaved summary CSV to {summary_file.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
