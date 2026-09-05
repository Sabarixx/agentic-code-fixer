"""Week 6 LangGraph pipeline: planner -> coder -> tester (with retry) -> refactor -> tester."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from langgraph.graph import END, START, StateGraph

from agent.nodes.coder import coder_node
from agent.nodes.planner import planner_node
from agent.nodes.refactor import refactor_node
from agent.nodes.tester import tester_node
from agent.nodes.custom_debugger import debugger_node
from agent.router import route_after_tester
from agent.state import AgentState, initial_state



def build_graph():
    graph = StateGraph(AgentState)
    graph.add_node("planner_node", planner_node)
    graph.add_node("coder_node", coder_node)
    graph.add_node("tester_node", tester_node)
    graph.add_node("refactor_node", refactor_node)
    graph.add_node("debugger_node", debugger_node)


    graph.add_edge(START, "planner_node")
    graph.add_edge("planner_node", "coder_node")
    graph.add_edge("coder_node", "tester_node")
    graph.add_edge("debugger_node", "coder_node")


    # Refactor node returns to tester_node for post-refactor validation
    graph.add_edge("refactor_node", END)

    # Conditional routing after tester node
    graph.add_conditional_edges(
        "tester_node",
        route_after_tester,
        {
            "coder_node": "coder_node",
            "debugger_node": "debugger_node",
            "refactor_node": "refactor_node",
            "__end__": END,
        },

    )

    return graph.compile()


def main() -> None:
    spec_path = ROOT / "specs" / "spec_01.json"
    spec = json.loads(spec_path.read_text(encoding="utf-8")) if spec_path.exists() else {
        "id": "smoke",
        "title": "Smoke spec",
        "function_name": "smoke",
    }
    app = build_graph()
    result = app.invoke(initial_state(spec))
    print("status:", result["status"])
    print("iterations:", result.get("iteration_count", 0))
    print("has_refactored:", result.get("has_refactored", False))
    print("plan:", json.dumps(result["plan"], ensure_ascii=True, indent=2))
    print("code:\n", result["code"], sep="")
    print("test_results:", result["test_results"])
    print("workflow: planner_node -> coder_node -> tester_node -> refactor_node")


if __name__ == "__main__":
    main()
