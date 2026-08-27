# Agentic Code Fixer

8-week **multi-agent code-fix** system (Option C). A LangGraph workflow plans, writes, tests, and later refactors solutions to curated DSA function specs.

**Week 1 scope:** environment, architecture contract, linear graph skeleton (three placeholder nodes), and eight function specs with 40 reference pytest cases.

Later weeks replace placeholders with real Planner, Coder, Tester, and Refactor nodes. Do not change `docs/architecture.md` or `agent/state.py` fields without treating that as a schema lock revision.

## Setup

From PowerShell, in this folder:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
```

Put your Groq key in `.env` as `GROQ_API_KEY`. This repo already uses Groq in `scratch/test_llm.py`.

## What to open in Cursor (where the code lives)

| Goal | File |
|------|------|
| Architecture lock (schema + diagrams) | `docs/architecture.md` |
| Typed state | `agent/state.py` |
| Week 1 graph | `agent/graph.py` |
| LLM smoke test | `scratch/test_llm.py` |
| Spec *N* | `specs/spec_0N.json` |
| Tests for spec *N* | `specs/tests/test_spec_0N.py` |
| Ground-truth solutions | `specs/reference/` |

Create new agent logic **inside `agent/`**. Do not paste graph code into the specs JSON files.

## Execution

Activate the venv, then:

```powershell
# Day 1 — LLM
python scratch/test_llm.py

# Day 3 — graph skeleton
python agent/graph.py

# Day 7 — 40 reference tests
pytest specs/tests/
```

## LangSmith (Day 6)

1. Create a project at [LangSmith](https://smith.langchain.com/).
2. Copy API key into `.env`:

```text
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=...
LANGCHAIN_PROJECT=agentic-code-fixer
```

3. Run `python agent/graph.py` and confirm three node spans on the dashboard.

## Curated specs

| ID | Problem |
|----|---------|
| spec_01 | Two Sum |
| spec_02 | Reverse Linked List |
| spec_03 | Valid Parentheses |
| spec_04 | Merge Intervals |
| spec_05 | Group Anagrams |
| spec_06 | Search in Rotated Sorted Array |
| spec_07 | LRU Cache |
| spec_08 | Topological Sort |

## Out of scope (Week 1)

- Real LLM planner/coder prompts
- Running generated code under pytest inside `tester_node`
- Conditional retry and `refactor_node` in the compiled graph
