"""Refactor Node implementation with discard-on-regression safety net."""

from __future__ import annotations

import os
from typing import Any
from dotenv import load_dotenv
from langchain_groq import ChatGroq

from agent.nodes.coder import extract_code_block, validate_code_ast
from agent.prompts.refactor_prompt import (
    REFACTOR_SYSTEM_PROMPT,
    format_refactor_user_prompt,
)
from agent.state import AgentState
from tools.file_writer import write_code_to_file
from tools.retry_utils import invoke_with_exponential_backoff
from tools.sandbox_runner import run_sandboxed_pytest, TestResult

load_dotenv()


def get_llm():
    """Initialize LLM client for Refactor node."""
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY environment variable is not set in .env")
    return ChatGroq(
        model="openai/gpt-oss-20b",
        api_key=api_key,
        temperature=0.1,
    )


def refactor_node(state: AgentState) -> dict[str, Any]:
    """
    LangGraph Refactor Node:
    1. Asks LLM to optimize passing code for readability/naming.
    2. Tests candidate code in sandbox.
    3. If candidate passes all tests -> keep refactored code and set status="refactored".
    4. If candidate fails tests (regression) -> discard refactored code, keep original passing code, log discard.
    """
    spec = state.get("spec") or {}
    original_code = state.get("code") or ""
    spec_id = spec.get("id", "spec_unknown")
    iteration_count = state.get("iteration_count", 1) + 1

    if not original_code:
        return {"status": "passed", "has_refactored": True, "refactor_discarded": True}

    user_prompt = format_refactor_user_prompt(spec, original_code)
    llm = get_llm()

    messages = [
        ("system", REFACTOR_SYSTEM_PROMPT),
        ("human", user_prompt),
    ]

    try:
        response = invoke_with_exponential_backoff(llm.invoke, messages)
        raw_text = response.content if hasattr(response, "content") else str(response)
        candidate_code = extract_code_block(raw_text)
    except Exception as err:
        print(f"[RefactorNode] LLM invocation failed: {err}. Keeping original code.")
        return {"status": "passed", "has_refactored": True, "refactor_discarded": True}

    # Validate AST syntax of refactored candidate
    is_valid, ast_err = validate_code_ast(candidate_code)
    if not is_valid:
        print(f"[RefactorNode] Candidate AST invalid ({ast_err}). Discarding refactor attempt.")
        return {"status": "passed", "has_refactored": True, "refactor_discarded": True}

    # Temporarily write candidate file to run sandbox pytest verification
    candidate_filepath = write_code_to_file(spec_id, iteration_count, candidate_code)
    candidate_result: TestResult = run_sandboxed_pytest(spec_id, iteration_count)

    if candidate_result.all_passed:
        print(f"[RefactorNode] Refactored candidate passed all tests! Updating code for {spec_id}.")
        return {
            "status": "refactored",
            "code": candidate_code,
            "has_refactored": True,
            "refactor_discarded": False,
            "iteration_count": iteration_count,
        }
    else:
        print(f"[RefactorNode] Discard-on-regression: refactor attempt failed {candidate_result.failed} tests. Reverting to original code.")
        # Re-write original passing code to attempt file so latest file is passing
        write_code_to_file(spec_id, iteration_count, original_code)
        return {
            "status": "passed",
            "code": original_code,
            "has_refactored": True,
            "refactor_discarded": True,
            "iteration_count": iteration_count,
        }
