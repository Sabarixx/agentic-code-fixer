"""Shared LangGraph state — keep in lockstep with docs/architecture.md."""

from typing import Any, Literal, TypedDict

Status = Literal[
    "idle",
    "planning",
    "coding",
    "testing",
    "refactoring",
    "passed",
    "failed",
    "error",
]

MAX_ITERATIONS = 3


class AgentState(TypedDict):
    spec: dict[str, Any]
    plan: str
    code: str
    test_results: dict[str, Any]
    diagnosis: dict[str, Any] | None
    iteration_count: int
    status: Status



def initial_state(spec: dict[str, Any] | None = None) -> AgentState:
    return {
        "spec": spec or {},
        "plan": "",
        "code": "",
        "test_results": {},
        "diagnosis": None,
        "iteration_count": 0,
        "status": "idle",
    }
