# Self-Evaluation Report — Multi-Agent Code-Fix System

**Author:** Sabari | **Project:** Agentic Code Fixer | **Track:** 8-Week Agentic AI Engineering  
**Evaluation Date:** Week 7 (Post-Week-6 Full Run)  
**Evidence Base:** [`traces/final_run/`](../traces/final_run/) — 8 complete JSON traces, preserved read-only from the Week 6 unattended execution.

---

## 1. System Overview

The **Agentic Code Fixer** is a closed-loop, multi-agent pipeline built with **LangGraph** that autonomously plans, generates, tests, retries, and refactors Python function implementations given a structured spec.

### 1.1 Four-Node Pipeline Architecture

| Node | Role | Key Output |
| :--- | :--- | :--- |
| `planner_node` | Reads spec constraints, selects algorithmic strategy, identifies edge cases | `state["plan"]` (structured dict: approach, edge_cases, complexity_target) |
| `coder_node` | Generates Python implementation from plan; uses failure tracebacks on retry | `state["code"]` (AST-validated Python source) |
| `tester_node` | Runs `pytest` in isolated subprocess (10s timeout, fresh `tempfile` dir) | `state["test_results"]` (passed, failed, total, failure_details, timed_out) |
| `refactor_node` | Asks LLM to improve readability/naming of verified passing code; re-tests candidate | `state["code"]` (refactored or reverted to original) |

### 1.2 Compiled Graph Topology (Final — Week 6)

```text
START → planner_node → coder_node → tester_node
                             ▲              │
              ┌──────────────┴───────────── │ ──────────────────┐
              │ status="failed"             │ status="passed"   │
              │ iteration_count < 3         │                   │
              │                             ▼                   │
              └──────────────── (retry)  refactor_node          │
                                             │                  │
                                          END ◄─────────────────┘
                                        (refactored / passed / failed)
```

### 1.3 Safety Mechanisms

Two self-correction mechanisms are implemented and verified:

1. **Retry Loop Cap (`MAX_ITERATIONS = 3`)** — If `tester_node` reports `status="failed"` and `iteration_count >= 3`, the router directs to `END` with `status="failed"` rather than looping indefinitely. *(Evidence: `agent/router.py`, `tests/test_retry_loop.py` — 4/4 router unit tests passing.)*

2. **Discard-on-Regression Safety Net** — `refactor_node` runs the full `pytest` sandbox on its candidate code before accepting it. If the refactored candidate fails any test, the node reverts to the original passing code and sets `refactor_discarded=True`. *(Evidence: `tests/test_refactor_node.py` — 2/2 tests: `test_refactor_node_keeps_valid_refactor` and `test_refactor_node_reverts_on_regression`.)*

---

## 2. Final Evaluation Results Table

**Source:** [`traces/week6_summary.md`](../traces/week6_summary.md) (auto-generated from `traces/final_run/`)

| Spec ID | Problem Title | Algorithm Category | Iterations | Final Status | Tests (5 total) | Refactored? |
| :---: | :--- | :--- | :---: | :---: | :---: | :---: |
| `spec_01` | Two Sum | Hash Map | 2 | `refactored` | 5/5 ✅ | Yes |
| `spec_02` | Reverse Linked List | Pointer Manipulation | 2 | `refactored` | 5/5 ✅ | Yes |
| `spec_03` | Valid Parentheses | Stack | 2 | `refactored` | 5/5 ✅ | Yes |
| `spec_04` | Merge Intervals | Sorting / Interval | 2 | `refactored` | 5/5 ✅ | Yes |
| `spec_05` | Group Anagrams | Hash Table / String | 2 | `refactored` | 5/5 ✅ | Yes |
| `spec_06` | Search in Rotated Sorted Array | Modified Binary Search | 2 | `refactored` | 5/5 ✅ | Yes |
| `spec_07` | LRU Cache | Doubly Linked List + Hash Map | 2 | `refactored` | 5/5 ✅ | Yes |
| `spec_08` | Topological Sort | Graph DAG / Kahn's Algorithm | 2 | `refactored` | 5/5 ✅ | Yes |

**Summary: 8/8 specs reached `status="refactored"` · 40/40 unit tests passing · All refactor passes kept (0 discarded)**

---

## 3. Objective Analysis

### Objective 1: Full Pipeline Correctness (Planner → Coder → Tester → Refactor)

**Claim:** The 4-node pipeline produces syntactically valid, test-passing, refactored code for all 8 specs in a single unattended run.

**Evidence:**
- Each trace in `traces/final_run/spec_XX.json` records `final_status: "refactored"` and `test_results.all_passed: true`.
- Example from `traces/final_run/spec_01.json` (Two Sum):
  - `iterations_taken: 2` (1 coder pass + 1 refactor iteration counted)
  - `test_results.passed: 5`, `test_results.failed: 0`
  - `final_code` shows a fully documented, type-annotated implementation with a `Dict[int, int]` `index_by_value` map — clearly distinct from the coder's initial draft.
- The `planner_node` produced structured plans (`approach`, `edge_cases`, `complexity_target`) for all 8 specs, stored in `traces/week2_plans/`.
- The `coder_node` used AST validation (via `ast.parse()`) before writing each attempt, preventing malformed code from reaching the sandbox.
- The `tester_node` ran isolated `pytest` subprocess execution with a 10-second hard timeout for all 8 specs.

**Verdict:** ✅ **Objective fully met.** The pipeline completed correctly for all 8 specs in a single unattended run, producing verified, refactored solutions.

---

### Objective 2: Self-Correcting Retry Loop

**Claim:** When generated code fails unit tests, the system automatically injects failure tracebacks back into the coder prompt and retries, up to `MAX_ITERATIONS = 3` times.

**Evidence (Direct):**
- `agent/router.py`: `route_after_tester()` returns `"coder_node"` when `status="failed"` and `iteration_count < MAX_ITERATIONS`, routes to `"__end__"` when at the cap.
- `agent/nodes/coder.py`: When `state["test_results"]` is non-empty and `all_passed=False`, `format_coder_retry_prompt()` is used instead of the initial prompt — injecting `failure_details` and the previous code into the next attempt.
- `tests/test_retry_loop.py`: 4/4 unit tests verify all router branches:
  - `test_route_passed_returns_end`
  - `test_route_error_returns_end`
  - `test_route_failed_under_max_returns_coder_node`
  - `test_route_failed_at_max_returns_end`

**Evidence (Indirect — Week 5 batch run):**
- `traces/week5_retry/` contains 8 traces from the Week 5 experiment, all showing `final_status: "passed"` at `iteration_count: 1`. The LLM generated correct code on the first attempt across all specs.

**Honest Assessment:** The retry loop was exercised in testing (unit tests, forced-buggy-code integration tests) but was not observed triggering organically during the live 8-spec run since all specs passed on the first coder attempt. This is a positive outcome but means the retry path's effectiveness in the wild (against genuinely difficult specs) remains theoretical.

**Verdict:** ✅ **Objective implemented and unit-tested.** The mechanism is confirmed working via controlled tests, though the real-world evaluation did not trigger retries.

---

### Objective 3: Refactor Pass with Discard-on-Regression Safety

**Claim:** After a spec passes, the system runs a refactor pass. If the refactored candidate introduces regressions, it is discarded and the original code is preserved.

**Evidence:**
- All 8 `traces/final_run/spec_XX.json` files show `final_status: "refactored"`, meaning all 8 refactor candidates passed post-refactor testing.
- `spec_01.json` final code shows a meaningfully refactored version: variable renamed from `index_map` (coder output) to `index_by_value` with a `Dict[int, int]` type annotation and an explicit docstring — demonstrating the refactor improved clarity.
- `tests/test_refactor_node.py`:
  - `test_refactor_node_keeps_valid_refactor`: Confirms `status="refactored"` and `refactor_discarded=False` when candidate passes.
  - `test_refactor_node_reverts_on_regression`: Injects a broken refactor (`return [0, 0]`) and confirms `status="passed"`, `refactor_discarded=True`, and `code` reverts to the original.

**Honest Assessment:** The discard-on-regression path was only triggered synthetically (forced broken candidate in unit tests), not by a real LLM refactor failure during the 8-spec run. This is because the LLM consistently produced safe refactors. The safety net is verified correct, but its real-world value is demonstrated through the test suite rather than a live failure.

**Verdict:** ✅ **Objective fully implemented and verified.** Refactor pass active for all 8 specs; safety net confirmed via unit tests.

---

## 4. Self-Correction Mechanisms Summary

| Mechanism | Implementation File | Trigger Condition | Verified By |
| :--- | :--- | :--- | :--- |
| **Retry Loop** | `agent/router.py` + `agent/nodes/coder.py` | `status="failed"` and `iteration_count < 3` | `tests/test_retry_loop.py` (4/4 pass) |
| **Retry Cap** | `agent/router.py` | `iteration_count >= MAX_ITERATIONS` | `tests/test_retry_loop.py` (4/4 pass) |
| **Discard-on-Regression** | `agent/nodes/refactor.py` | Refactored candidate fails sandbox pytest | `tests/test_refactor_node.py` (2/2 pass) |
| **Sandbox Isolation** | `tools/sandbox_runner.py` | Every test execution | `tests/test_tester_node.py` (7/7 pass) |
| **Timeout Enforcement** | `tools/sandbox_runner.py` | Subprocess exceeds 10 seconds | `tests/test_tester_node.py::test_timeout_is_enforced` |
| **API Backoff** | `tools/retry_utils.py` | Transient LLM API errors | 3-attempt exponential backoff (2s/4s/8s) |

---

## 5. Quantitative Metrics

| Metric | Value |
| :--- | :--- |
| Specs evaluated | 8 / 8 |
| Specs reaching `passed` or `refactored` | **8 / 8 (100%)** |
| Reference unit tests passing | **40 / 40 (100%)** |
| Average iterations per spec | **2** (1 coder + 1 refactor counted) |
| Retry loop triggered organically | 0 (all passed on first attempt) |
| Refactor passes kept | **8 / 8 (100%)** |
| Refactor passes discarded | 0 |
| Execution timeouts | 0 |
| Sandbox isolation: unhandled crashes | 0 |
| Total pytest tests across all suites | **≥ 17** (test_planner, test_coder, test_tester_node, test_retry_loop, test_refactor_node) |

---

## 6. Limitations & Honest Assessment

### 6.1 Test Suite Coverage

The 5-test-per-spec reference suite was sufficient to validate correctness on standard cases, but is narrow:
- Tests do not cover adversarial inputs (max constraints, random large arrays) that might reveal O(n²) vs O(n) performance differences.
- No property-based tests (e.g., Hypothesis) — a more rigorous evaluation would include parametrized random inputs.

### 6.2 LLM Non-Determinism

All 8 specs passed on the first coder attempt in the live run. This is partly due to LLM capability (the model was given a high-quality plan), but it means the retry loop's effectiveness for genuinely hard specs remains unproven at scale. Future evaluation should include deliberately difficult specs (e.g., dynamic programming, segment trees) to stress-test the retry loop organically.

### 6.3 Reference Helpers in Sandbox

The sandbox runner (`tools/sandbox_runner.py`) had to inject reference helper functions (`from_list`, `to_list`, `is_valid_topo`) into the generated code file when tests imported them alongside the main function. This is a structural limitation: the system assumes generated code is self-contained, but some specs have test utilities that must be shared. A more robust design would generate the helper functions as part of the coder's output.

### 6.4 No Cross-Spec Learning

Each spec is evaluated independently. The system has no memory of past successes or failures across different problem types. A future version could maintain a spec-type → successful-approach index to guide the planner.

### 6.5 Refactor Quality Not Formally Measured

The refactor pass is evaluated only by re-running the same unit tests (behavioral correctness). It is not measured for readability improvement, complexity reduction, or code style (e.g., via `flake8`, `pylint` scores, or cyclomatic complexity). A formal "before/after" quality metric would strengthen the refactor objective.

---

## 7. Lessons Learned

### Technical

1. **Subprocess isolation is essential.** Running `pytest` inside the same Python process would have caused import conflicts between specs. Using `tempfile.mkdtemp()` + `subprocess.run()` with a custom minimal environment eliminated cross-contamination entirely.

2. **`__future__` imports must be at the top of a file.** When injecting reference helpers by appending them to generated code, the `from __future__ import annotations` statement caused `SyntaxError`. Stripping it during injection was the fix — a non-obvious Python gotcha.

3. **LangGraph conditional edges require explicit key-to-node mapping.** `add_conditional_edges("tester_node", fn, {"key": "node_name"})` requires the routing function to return string keys that exactly match the dict — returning `"__end__"` vs `END` are different values. Getting this right required careful reading of the LangGraph docs.

4. **Windows encoding (`cp1252`) breaks non-ASCII console output.** Using `json.dumps(obj, ensure_ascii=True)` for all console output avoided `UnicodeEncodeError` when printing Unicode characters (e.g., checkmarks) from subprocess stdout.

5. **LLM temperature matters for code generation.** Temperature `0.1` (near-deterministic) produced consistently correct implementations across all specs. Higher temperatures may be appropriate for creative retry prompts where the previous attempt was definitively wrong.

### Process

6. **Week-by-week incremental architecture locks work.** Defining `AgentState` and the graph contract in Week 1 (and treating it as locked) prevented Weeks 2–6 from introducing incompatible state fields. Every node could be built and tested in isolation because the shared contract was stable.

7. **Batch evaluation scripts are more valuable than expected.** The ability to run `python scratch/evaluate_all_tests.py` or `python scratch/run_full_evaluation.py` at any point and get an immediate 8-spec status report was critical for catching regressions quickly between weeks.

---

## 8. Go / No-Go Assessment (Week 7 Gate)

| Criterion | Status | Evidence |
| :--- | :---: | :--- |
| Full 8-spec run completed and archived | ✅ GO | `traces/final_run/` — 8 JSON traces |
| Refactor pass implemented and tested | ✅ GO | `tests/test_refactor_node.py` 2/2 pass |
| Discard-on-regression confirmed | ✅ GO | `test_refactor_node_reverts_on_regression` |
| Failure analysis written (Week 6) | ✅ GO | `traces/week6_failure_analysis.md` — 0 failures |
| All pytest suites green | ✅ GO | See Section 5 metrics |
| No unhandled crashes in live run | ✅ GO | `traces/final_run/` — all statuses recorded |

**Overall Go/No-Go: ✅ GO — Week 8 (Final Demo & Submission) may proceed.**
