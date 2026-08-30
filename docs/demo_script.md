# Demo Script — Agentic Code Fixer (Live Presentation)

**Target Duration:** 6–8 minutes  
**Spec Showcased:** `spec_01` — Two Sum  
**Evidence Files:** `traces/final_run/spec_01.json` · `traces/final_run/generated_archive/spec_01_attempt_*.py`  
**Self-Eval Reference:** `docs/self_eval.md`  
**Fallback:** If LangSmith is slow, use local JSON files — all talking points below are pre-loaded from them.

---

## Before You Start — Setup Checklist (5 min before demo)

- [ ] Open `README.md` on GitHub — banner and Mermaid diagram visible
- [ ] Open `traces/final_run/spec_01.json` in VS Code (formatted JSON)
- [ ] Open `traces/final_run/generated_archive/spec_01_attempt_1.py` and `spec_01_attempt_2.py` side by side
- [ ] Open `docs/self_eval.md` — scrolled to Section 5 (Metrics)
- [ ] Terminal ready at `d:\Agentic-AI\agentic-code-fixer` with venv activated
- [ ] Run `.\venv\Scripts\python.exe scratch/verify_fresh_clone.py` — confirm all PASS

---

## Segment 1 — Introduction (60 seconds)

**[Show: GitHub README — banner + Mermaid diagram]**

> "This is the Agentic Code Fixer — an 8-week project implementing a closed-loop, multi-agent code synthesis system built with LangGraph.
>
> The core idea is: instead of a single-shot LLM prompt that generates code and hopes for the best, I modelled code synthesis as a **state machine graph** with four distinct agents.
>
> As you can see in this diagram — [point to Mermaid] — the pipeline is:
> **Planner** reads the spec and produces an algorithmic strategy.
> **Coder** turns that strategy into Python code.
> **Tester** runs it in a sandboxed pytest subprocess — fully isolated, with a hard 10-second timeout.
> If tests pass, the **Refactor node** improves code quality — but only if it doesn't regress the tests.
> If tests fail, a conditional edge loops back to Coder with the failure traceback injected into the retry prompt.
>
> The evaluation domain is 8 curated DSA function specs — 40 unit tests total. Every stage of every run is archived in `traces/final_run/`."

---

## Segment 2 — The Planner Node (60 seconds)

**[Show: `traces/final_run/spec_01.json` → `plan` field]**

> "Let me walk through one complete trace — spec_01, Two Sum.
>
> The planner receives the raw spec JSON — function name, signature, docstring, constraints — and its job is to produce a structured, step-by-step algorithmic strategy *before* any code is written.
>
> [Scroll to `plan.approach`]
>
> You can see it identified the correct algorithm: a hash map for O(n) lookups. It also enumerated six concrete edge cases — [point to `plan.edge_cases`] — duplicates forming the target pair, negative numbers, the case where target equals twice a single number.
>
> The planner's output is locked into `state['plan']` and passed to the coder. The coder never sees the raw spec directly — it only reads the plan. That's the key separation of concerns."

---

## Segment 3 — The Coder Node (60 seconds)

**[Show: `traces/final_run/generated_archive/spec_01_attempt_1.py`]**

> "The coder node reads the plan and generates a Python implementation. Every output is:
> — AST-validated before being accepted (I use `ast.parse()` to reject syntactically broken code immediately)
> — written to `generated/` for the full history
>
> Here's what the coder produced on its **first attempt**:
>
> [Read key lines]
> — It used a `seen` dict, exactly as the plan specified.
> — It handles the complement lookup in O(n) time.
> — It's functional, clean — but notice the variable names: `seen`, `num`, `complement`. Minimal but a bit terse.
>
> This code was handed to the tester node."

---

## Segment 4 — The Tester Node (60 seconds)

**[Show: `traces/final_run/spec_01.json` → `test_results` field]**

> "The tester node does something important — it does **not** run pytest in-process. It spins up a clean subprocess in a temporary directory, writes the generated code to a fresh file, runs the 5-spec test cases against it, and captures the full stdout, stderr, pass/fail counts, and any tracebacks.
>
> [Point to `test_results`]
>
> Result: 5 passed, 0 failed, `timed_out: false`. The pipeline routes to the refactor node.
>
> Notice `timed_out: false` — that field exists because the sandbox enforces a **hard 10-second kill**. Infinite loops cannot hang the pipeline.
>
> This is also where the self-correction mechanism would have activated: if `failed > 0` and `iteration_count < 3`, the router would have sent this back to the coder with the failure traceback injected. I'll show that in a moment."

---

## Segment 5 — The Refactor Node (60 seconds)

**[Show: `spec_01_attempt_1.py` and `spec_01_attempt_2.py` side by side]**

> "Because the tests passed, the pipeline moved to the refactor node.
>
> Its job is to improve code quality — readability, naming, type annotations — without changing behaviour. And critically: **it re-tests the refactored candidate before accepting it**. If the refactored version fails any test, it's silently discarded and the original is preserved.
>
> Here's the diff for spec_01:
>
> **Attempt 1 (coder output):**
> ```python
> seen = {}
> for i, num in enumerate(nums):
>     complement = target - num
>     if complement in seen:
>         return [seen[complement], i]
> ```
>
> **Attempt 2 (refactored):**
> ```python
> index_by_value: Dict[int, int] = {}
> for current_index, current_value in enumerate(nums):
>     needed = target - current_value
>     if needed in index_by_value:
>         return [index_by_value[needed], current_index]
> ```
>
> Same algorithm, same complexity — but the variable names are now self-documenting: `index_by_value` instead of `seen`, `current_index`/`current_value` instead of `i`/`num`, explicit `Dict[int, int]` type annotation. The refactor was kept — `refactor_discarded: false`."

---

## Segment 6 — Self-Correction: The Safety Nets (60 seconds)

**[Run in terminal: `.\venv\Scripts\python.exe -m pytest tests/test_refactor_node.py tests/test_retry_loop.py -v`]**

> "Now let me show the two self-correction mechanisms live.
>
> [Run the command — show output]
>
> `test_refactor_node_reverts_on_regression` — this test injects a deliberately broken refactor (one that always returns `[0, 0]`) and proves the system **detects the regression and reverts to the original passing code**. `refactor_discarded` becomes `True`.
>
> `test_route_passed_routes_to_refactor_first` and `test_route_failed_under_max_returns_coder_node` — these prove the **retry router** branches correctly:
> - If tests pass and no refactor yet → route to `refactor_node`
> - If tests fail and `iteration_count < 3` → route back to `coder_node` with failure details
> - If tests fail and at the cap → route to `__end__` as `failed`
>
> All five router tests pass. The retry path is proven correct even though the live 8-spec run didn't need it — because the LLM passed all specs on the first coder attempt."

---

## Segment 7 — Self-Evaluation Results & Honest Assessment (60 seconds)

**[Show: `docs/self_eval.md` — Section 5 Quantitative Metrics]**

> "The full results:
> — 8/8 specs reached `refactored` status
> — 40/40 reference tests passing
> — 0 unhandled failures, 0 timeouts, 0 refactor passes discarded
>
> The honest part — [scroll to Section 6, Limitations]:
>
> The retry loop was **not triggered organically** — the LLM passed all 8 specs on the first coder attempt. The retry mechanism is verified correct via unit tests, but its real-world effectiveness on genuinely hard specs is unproven.
>
> The refactor quality is only evaluated behaviourally — the tests pass — but there's no formal metric for *how much* the readability improved. A future extension would add a pylint score diff or cyclomatic complexity comparison.
>
> These limitations are documented — Section 6 of self_eval.md — because a known, well-understood constraint is better than an untested claim."

---

## Segment 8 — Wrap-Up (30 seconds)

**[Show: GitHub repo → Releases tab showing `v1.0-submission` tag]**

> "The repo is tagged `v1.0-submission` — a clean snapshot that passes the fresh-clone verification checklist: 52/52 checks, including all 40 reference tests and all 37 agent unit tests.
>
> Week by week — environment → planner → coder → tester → retry loop → refactor pass → self-evaluation → final submission. Eight weeks, one clean pipeline, 8 specs solved.
>
> Thank you."

---

## Timing Log (fill in during rehearsal)

| Rehearsal | Date | Total Duration | Over/Under | Notes |
| :---: | :---: | :---: | :---: | :--- |
| Run 1 | | | | |
| Run 2 | | | | |

**Target: 6:00–8:00. Cut Segment 5 diff reading if running long.**

---

## Fallback Plan (if LangSmith is unavailable)

All talking points above are grounded in **local files only**:
- Architecture: `README.md` Mermaid diagram
- Plan: `traces/final_run/spec_01.json → plan` field
- Code diff: `traces/final_run/generated_archive/spec_01_attempt_1.py` vs `spec_01_attempt_2.py`
- Test results: `traces/final_run/spec_01.json → test_results`
- Safety nets: `pytest tests/test_refactor_node.py tests/test_retry_loop.py -v` (live terminal)
- Results: `docs/self_eval.md`

**No LangSmith dependency. The demo runs entirely offline from the archived traces.**
