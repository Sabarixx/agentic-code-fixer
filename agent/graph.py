"""Weeks 1-4 LangGraph pipeline: planner -> coder -> tester (live nodes)."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from langgraph.graph import END, START, StateGraph
from agent.state import AgentState, initial_state
from agent.nodes.planner import planner_node
from agent.nodes.coder import coder_node
from agent.nodes.tester import tester_node


def build_graph():
    graph = StateGraph(AgentState)
    graph.add_node("planner_node", planner_node)
    graph.add_node("coder_node", coder_node)
    graph.add_node("tester_node", tester_node)
    graph.add_edge(START, "planner_node")
    graph.add_edge("planner_node", "coder_node")
    graph.add_edge("coder_node", "tester_node")
    graph.add_edge("tester_node", END)
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
    print("plan:", json.dumps(result["plan"], ensure_ascii=True, indent=2))
    print("code:\n", result["code"], sep="")
    print("test_results:", result["test_results"])
    print("nodes: planner_node -> coder_node -> tester_node")


if __name__ == "__main__":
    main()
