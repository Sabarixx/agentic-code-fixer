"""Batch evaluation script: runs Tester Node on all 8 generated Week 3 files."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.sandbox_runner import run_sandboxed_pytest


def main():
    traces_dir = ROOT / "traces" / "week4_test_results"
    traces_dir.mkdir(parents=True, exist_ok=True)

    specs = [
        ("spec_01", "Two Sum"),
        ("spec_02", "Reverse Linked List"),
        ("spec_03", "Valid Parentheses"),
        ("spec_04", "Merge Intervals"),
        ("spec_05", "Group Anagrams"),
        ("spec_06", "Search in Rotated Sorted Array"),
        ("spec_07", "LRU Cache"),
        ("spec_08", "Topological Sort"),
    ]

    pass_count = 0
    for spec_id, title in specs:
        print(f"Testing {spec_id} ({title})...")
        result = run_sandboxed_pytest(spec_id, 1)

        trace = result.model_dump()
        (traces_dir / f"{spec_id}.json").write_text(
            json.dumps(trace, indent=2), encoding="utf-8"
        )

        if result.all_passed:
            print(f"  [PASS] {result.passed}/{result.total} tests passed")
            pass_count += 1
        elif result.timed_out:
            print(f"  [TIMEOUT] Execution exceeded 10s")
        elif result.error:
            print(f"  [ERROR] {result.error[:120]}")
        else:
            print(f"  [FAIL] {result.passed}/{result.total} passed, {result.failed} failed")
            for detail in result.failure_details[:3]:
                print(f"    >> {detail[:100]}")

    print(f"\nResult: {pass_count}/{len(specs)} specs fully passing.")


if __name__ == "__main__":
    main()
