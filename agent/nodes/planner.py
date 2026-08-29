"""Planner node implementation using LLM with structured output."""

from __future__ import annotations

import os
from typing import Any
from dotenv import load_dotenv
from langchain_groq import ChatGroq

from agent.prompts.planner_prompt import (
    PLANNER_SYSTEM_PROMPT,
    PlanOutput,
    format_planner_user_prompt,
)
from agent.state import AgentState

load_dotenv()


def get_llm():
    """Initialize LLM client with Groq or fallback provider."""
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY environment variable is not set in .env")
    return ChatGroq(
        model="openai/gpt-oss-20b",
        api_key=api_key,
        temperature=0.1,
    )


def planner_node(state: AgentState) -> dict[str, Any]:
    """LangGraph node: generates a structured PlanOutput for the given specification."""
    spec = state.get("spec") or {}
    user_prompt = format_planner_user_prompt(spec)
    llm = get_llm()
    structured_llm = llm.with_structured_output(PlanOutput)

    messages = [
        ("system", PLANNER_SYSTEM_PROMPT),
        ("human", user_prompt),
    ]

    # Attempt 1: Invocation with structured schema parsing
    try:
        plan_output: PlanOutput = structured_llm.invoke(messages)
    except Exception as err:
        # Fallback / Retry attempt with explicit instruction
        retry_messages = [
            ("system", PLANNER_SYSTEM_PROMPT + "\n\nIMPORTANT: Return valid JSON matching the schema strictly."),
            ("human", user_prompt + f"\n\nNote: Previous attempt failed with error: {err}. Please format response strictly."),
        ]
        try:
            plan_output = structured_llm.invoke(retry_messages)
        except Exception as retry_err:
            return {
                "status": "error",
                "plan": f"Planner failed after retry: {retry_err}",
            }

    plan_dict = plan_output.model_dump()
    return {
        "status": "planning",
        "plan": plan_dict,
    }
