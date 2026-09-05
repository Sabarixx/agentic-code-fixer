"""Coder Node implementation with LLM code generation and AST syntax validation."""

from __future__ import annotations

import ast
import os
import re
from typing import Any
from dotenv import load_dotenv
from langchain_groq import ChatGroq

from agent.prompts.coder_prompt import (
    CODER_SYSTEM_PROMPT,
    format_coder_retry_prompt,
    format_coder_user_prompt,
)
from agent.state import AgentState
from tools.file_writer import write_code_to_file

load_dotenv()


def get_llm():
    """Initialize LLM client for Coder node."""
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY environment variable is not set in .env")
    return ChatGroq(
        model="openai/gpt-oss-20b",
        api_key=api_key,
        temperature=0.1,
    )


def extract_code_block(response_text: str) -> str:
    """Extract code from LLM response text, stripping markdown fences and language specifiers."""
    pattern_lang = re.compile(r"```(?:python|typescript|javascript|ts|js|rust)?\s*\n?(.*?)\s*```", re.DOTALL | re.IGNORECASE)
    match = pattern_lang.search(response_text)
    if match:
        code = match.group(1).strip()
        code = re.sub(r"^(?:typescript|javascript|python|ts|js|rust)\s*\n", "", code, flags=re.IGNORECASE)
        return code.strip()

    pattern_generic = re.compile(r"```\s*(.*?)\s*```", re.DOTALL)
    match = pattern_generic.search(response_text)
    if match:
        code = match.group(1).strip()
        code = re.sub(r"^(?:typescript|javascript|python|ts|js|rust)\s*\n", "", code, flags=re.IGNORECASE)
        return code.strip()

    clean = response_text.strip()
    clean = re.sub(r"^(?:typescript|javascript|python|ts|js|rust)\s*\n", "", clean, flags=re.IGNORECASE)
    return clean


def validate_code_ast(code: str) -> tuple[bool, str]:
    """Validate python code using AST parsing. Returns (is_valid, error_msg)."""
    try:
        ast.parse(code)
        return True, ""
    except SyntaxError as err:
        return False, f"SyntaxError at line {err.lineno}: {err.msg}"
    except Exception as err:
        return False, str(err)


def coder_node(state: AgentState) -> dict[str, Any]:
    """LangGraph Coder Node: generates Python solution code, validates AST, writes file."""
    spec = state.get("spec") or {}
    plan = state.get("plan") or {}
    previous_code = state.get("code") or ""
    test_results = state.get("test_results") or {}
    iteration_count = state.get("iteration_count", 0) + 1
    spec_id = spec.get("id", "spec_unknown")

    # Use retry prompt if previous attempt failed test execution
    if test_results and not test_results.get("all_passed", False) and previous_code:
        user_prompt = format_coder_retry_prompt(spec, plan, previous_code, test_results, state.get("diagnosis"))
    else:
        user_prompt = format_coder_user_prompt(spec, plan)


    llm = get_llm()

    messages = [
        ("system", CODER_SYSTEM_PROMPT),
        ("human", user_prompt),
    ]

    try:
        response = llm.invoke(messages)
        raw_text = response.content if hasattr(response, "content") else str(response)
        code = extract_code_block(raw_text)
    except Exception as err:

        return {
            "status": "error",
            "code": f"# Coder failed: {err}",
            "iteration_count": iteration_count,
        }

    # Validate AST syntax
    is_valid, ast_error = validate_code_ast(code)
    status = "coding" if is_valid else "coder_syntax_error"

    # Write generated file to generated/
    filepath = write_code_to_file(spec_id, iteration_count, code)

    return {
        "status": status,
        "code": code,
        "iteration_count": iteration_count,
    }
