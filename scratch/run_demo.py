"""
Demo script: runs the full 4-node pipeline on a single spec and pretty-prints each stage.

Usage:
    python scratch/run_demo.py [spec_id]

Examples:
    python scratch/run_demo.py spec_01     # Two Sum (default)
    python scratch/run_demo.py spec_07     # LRU Cache
"""

from __future__ import annotations

import json
import sys
import textwrap
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


# ── helpers ──────────────────────────────────────────────────────────────────

CYAN = "\033[96m"
PURPLE = "\033[35m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
DIM = "\033[2m"
BOLD = "\033[1m"
RESET = "\033[0m"


def hr(char="─", width=72):
    return char * width


def header(tag: str, title: str, color: str = CYAN) -> None:
    print(f"\n{color}{BOLD}{hr()}{RESET}")
    print(f"{color}{BOLD} {tag}  {title}{RESET}")
    print(f"{color}{hr()}{RESET}")


def indent(text: str, prefix: str = "    ") -> str:
    return textwrap.indent(text.strip(), prefix)


def _diff_summary(original: str, refactored: str) -> str:
    """Return a short textual diff summary (first changed lines only)."""
    orig_lines = original.strip().splitlines()
    new_lines = refactored.strip().splitlines()
    added = [l for l in new_lines if l not in orig_lines]
    removed = [l for l in orig_lines if l not in new_lines]
    summary_lines = []
    for l in removed[:5]:
        summary_lines.append(f"{RED}- {l}{RESET}")
    for l in added[:5]:
        summary_lines.append(f"{GREEN}+ {l}{RESET}")
    if not summary_lines:
        summary_lines.append(f"{DIM}(no line-level diff detected — likely whitespace/docstring changes){RESET}")
    return "\n".join(summary_lines)


# ── LangGraph callback: observe each node as it executes ─────────────────────

class NodeObserver:
    """Tracks state transitions through each graph node for live display."""

    def __init__(self, original_code_holder: dict):
        self._original_code = original_code_holder

    def on_node_end(self, node_name: str, result: dict) -> None:
        if node_name == "planner_node":
            plan = result.get("plan") or {}
            if isinstance(plan, dict):
                approach = plan.get("approach", "")
                complexity = plan.get("complexity_target", "")
                edge_cases = plan.get("edge_cases", [])
                header("[PLAN]", "Planner Node — Algorithmic Strategy", CYAN)
                print(f"{DIM}Approach (first 300 chars):{RESET}")
                print(indent(approach[:300] + ("…" if len(approach) > 300 else "")))
                if edge_cases:
                    print(f"\n{DIM}Edge Cases:{RESET}")
                    for ec in edge_cases:
                        print(f"    • {ec}")
                print(f"\n{DIM}Complexity Target:{RESET} {complexity}")
            else:
                header("[PLAN]", "Planner Node — Plan (raw)", CYAN)
                print(indent(str(plan)[:400]))

        elif node_name == "coder_node":
            code = result.get("code") or ""
            iteration = result.get("iteration_count", "?")
            self._original_code["value"] = code
            header("[CODE]", f"Coder Node — Generated Code (Iteration {iteration})", PURPLE)
            print(indent(code[:600] + ("…" if len(code) > 600 else ""), "    "))

        elif node_name == "tester_node":
            tr = result.get("test_results") or {}
            status = result.get("status")
            passed = tr.get("passed", 0)
            total = tr.get("total", 0)
            all_ok = tr.get("all_passed", False)
            color = GREEN if all_ok else RED
            label = "PASS" if all_ok else "FAIL"
            header("[TEST]", f"Tester Node — Sandbox Pytest Results [{label}]", color)
            print(f"  Tests Passed: {color}{BOLD}{passed}/{total}{RESET}")
            stdout = tr.get("stdout", "").strip()
            if stdout:
                print(f"\n{DIM}Pytest Output:{RESET}")
                print(indent(stdout))
            failures = tr.get("failure_details", [])
            if failures:
                print(f"\n{DIM}Failure Details:{RESET}")
                for f in failures[:3]:
                    print(f"    {RED}{f[:120]}{RESET}")

        elif node_name == "refactor_node":
            status = result.get("status")
            discarded = result.get("refactor_discarded", False)
            new_code = result.get("code") or ""
            if discarded:
                header("[REFACTOR]", "Refactor Node — DISCARDED (regression detected, reverted)", RED)
                print(f"  {YELLOW}Original code preserved. Refactored candidate failed tests.{RESET}")
            else:
                header("[REFACTOR]", "Refactor Node — Candidate Accepted", GREEN)
                print(f"\n{DIM}Code Diff (original → refactored):{RESET}")
                print(_diff_summary(self._original_code.get("value", ""), new_code))


# ── main ─────────────────────────────────────────────────────────────────────

def main():
    spec_id = sys.argv[1] if len(sys.argv) > 1 else "spec_01"
    spec_path = ROOT / "specs" / f"{spec_id}.json"

    if not spec_path.exists():
        print(f"{RED}Error: spec file not found: {spec_path}{RESET}")
        sys.exit(1)

    spec = json.loads(spec_path.read_text(encoding="utf-8"))
    title = spec.get("title", spec_id)

    print(f"\n{BOLD}{CYAN}{'═' * 72}{RESET}")
    print(f"{BOLD}{CYAN}  ⚡ Agentic Code Fixer — Live Demo{RESET}")
    print(f"{BOLD}{CYAN}  Spec: {spec_id} — {title}{RESET}")
    print(f"{BOLD}{CYAN}{'═' * 72}{RESET}\n")

    from agent.graph import build_graph
    from agent.state import initial_state

    # Build graph
    print(f"{DIM}Building compiled LangGraph pipeline (planner → coder → tester → refactor)…{RESET}")
    app = build_graph()

    # Wrap with node observer
    original_code_holder: dict = {"value": ""}
    observer = NodeObserver(original_code_holder)

    # LangGraph stream to observe each node output
    state = initial_state(spec)
    final_state = None

    for chunk in app.stream(state, stream_mode="updates"):
        for node_name, node_result in chunk.items():
            observer.on_node_end(node_name, node_result)
        final_state = chunk

    # ── Final Summary ─────────────────────────────────────────────────────────
    # Re-invoke to get the final accumulated state
    app2 = build_graph()
    result = app2.invoke(initial_state(spec))

    final_status = result.get("status")
    iterations = result.get("iteration_count", 0)
    test_results = result.get("test_results") or {}
    passed = test_results.get("passed", 0)
    total = test_results.get("total", 0)
    discarded = result.get("refactor_discarded", False)

    color = GREEN if final_status in ("passed", "refactored") else RED
    print(f"\n{BOLD}{color}{'═' * 72}{RESET}")
    print(f"{BOLD}{color}  FINAL RESULT: {final_status.upper()}{RESET}")
    print(f"{BOLD}{color}{'═' * 72}{RESET}")
    print(f"  • Spec:            {spec_id} ({title})")
    print(f"  • Final Status:    {color}{BOLD}{final_status}{RESET}")
    print(f"  • Iterations:      {iterations}")
    print(f"  • Tests Passed:    {passed}/{total}")
    print(f"  • Refactor:        {'Kept' if not discarded else 'Discarded (safety revert)'}")
    print()

    exit_code = 0 if final_status in ("passed", "refactored") else 1
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
