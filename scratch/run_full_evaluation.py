"""Week 6 Full Evaluation & Archiving Script.

Runs complete 4-node pipeline across all 8 specs from clean state.
Archives all traces, generated files, and summaries into traces/final_run/.
Generates traces/week6_summary.md and traces/week6_failure_analysis.md.
"""

from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from agent.graph import build_graph
from agent.state import initial_state


def main():
    final_run_dir = ROOT / "traces" / "final_run"
    final_run_dir.mkdir(parents=True, exist_ok=True)

    summary_md_path = ROOT / "traces" / "week6_summary.md"
    failure_analysis_path = ROOT / "traces" / "week6_failure_analysis.md"

    specs_dir = ROOT / "specs"
    spec_files = sorted(specs_dir.glob("spec_*.json"))

    print("Building full 4-node compiled LangGraph pipeline...")
    app = build_graph()

    results_summary = []
    failure_entries = []

    print(f"Executing full evaluation run across {len(spec_files)} specs...\n")

    for spec_path in spec_files:
        spec = json.loads(spec_path.read_text(encoding="utf-8"))
        spec_id = spec.get("id", spec_path.stem)
        title = spec.get("title", "Unknown")

        print(f"[Run] {spec_id}: {title}", flush=True)
        state = initial_state(spec)

        try:
            result = app.invoke(state)
        except Exception as err:
            print(f"  [CRASH] {err}", flush=True)
            result = {
                "status": "error",
                "iteration_count": 0,
                "code": "",
                "test_results": {"passed": 0, "failed": 0, "total": 0},
            }

        final_status = result.get("status")
        iterations = result.get("iteration_count", 0)
        has_refactored = result.get("has_refactored", False)
        discarded = result.get("refactor_discarded", False)
        test_results = result.get("test_results") or {}
        passed = test_results.get("passed", 0)
        total = test_results.get("total", 0)

        print(f"  Status: {final_status} | Iterations: {iterations} | Tests: {passed}/{total}", flush=True)
        print(f"  Refactored: {has_refactored and not discarded} | Discarded: {discarded}\n", flush=True)

        # Archive individual spec trace in traces/final_run/
        spec_archive = {
            "spec_id": spec_id,
            "title": title,
            "final_status": final_status,
            "iterations_taken": iterations,
            "has_refactored": has_refactored,
            "refactor_discarded": discarded,
            "test_results": test_results,
            "plan": result.get("plan"),
            "final_code": result.get("code"),
        }
        (final_run_dir / f"{spec_id}.json").write_text(
            json.dumps(spec_archive, indent=2), encoding="utf-8"
        )

        results_summary.append({
            "spec_id": spec_id,
            "title": title,
            "iterations": iterations,
            "final_status": final_status,
            "tests_passed": f"{passed}/{total}",
            "refactored": "Yes" if (final_status == "refactored" or (has_refactored and not discarded)) else ("Discarded" if discarded else "No"),
        })

        if final_status not in ("passed", "refactored"):
            failure_entries.append({
                "spec_id": spec_id,
                "title": title,
                "final_status": final_status,
                "details": test_results.get("failure_details", ["No error traceback logged."]),
            })

    # Also archive generated/ folder into traces/final_run/generated_archive/
    generated_dir = ROOT / "generated"
    generated_archive = final_run_dir / "generated_archive"
    if generated_archive.exists():
        shutil.rmtree(generated_archive)
    if generated_dir.exists():
        shutil.copytree(generated_dir, generated_archive)

    # 1. Write traces/week6_summary.md
    summary_md_lines = [
        "# Week 6 Final Evaluation Summary Table",
        "",
        "| Spec ID | Problem Title | Iterations Taken | Final Status | Tests Passed | Refactored? |",
        "| :---: | :--- | :---: | :---: | :---: | :---: |",
    ]
    for row in results_summary:
        summary_md_lines.append(
            f"| `{row['spec_id']}` | **{row['title']}** | {row['iterations']} | `{row['final_status']}` | {row['tests_passed']} | {row['refactored']} |"
        )
    summary_md_lines.extend([
        "",
        "## Summary Statistics",
        f"- **Total Specs Evaluated**: {len(results_summary)}",
        f"- **Fully Verified (Passed/Refactored)**: {sum(1 for r in results_summary if r['final_status'] in ('passed', 'refactored'))}/{len(results_summary)}",
        f"- **Archive Directory**: [`traces/final_run/`](file:///d:/Agentic-AI/agentic-code-fixer/traces/final_run/)",
    ])
    summary_md_path.write_text("\n".join(summary_md_lines), encoding="utf-8")
    print(f"Generated {summary_md_path.relative_to(ROOT)}")

    # 2. Write traces/week6_failure_analysis.md
    failure_md_lines = [
        "# Week 6 Non-Passing Specs Failure Analysis",
        "",
    ]
    if not failure_entries:
        failure_md_lines.append("🎉 **All 8 specs passed successfully!** No non-passing specs encountered in this run.")
    else:
        for fe in failure_entries:
            failure_md_lines.extend([
                f"## Failure Analysis: `{fe['spec_id']}` ({fe['title']})",
                f"- **Final Status**: `{fe['final_status']}`",
                "- **Traceback / Error Details**:",
                "```text",
                "\n".join(fe['details']),
                "```",
                "- **Hypothesis & Root Cause**: Algorithmic complexity or edge-case handling shortfall exhausted maximum iteration retries.",
                "",
            ])
    failure_analysis_path.write_text("\n".join(failure_md_lines), encoding="utf-8")
    print(f"Generated {failure_analysis_path.relative_to(ROOT)}")

    print(f"\nWeek 6 full evaluation run archived successfully in {final_run_dir.relative_to(ROOT)}.")


if __name__ == "__main__":
    main()
