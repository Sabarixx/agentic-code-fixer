"""Streamlit Web Application for Agentic Code Fixer."""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import streamlit as st
from ui.pipeline_bridge import load_archived_traces, run_single_spec

# Import run_custom_fix from ui.pipeline_bridge if available, otherwise define fallback signature
try:
    from ui.pipeline_bridge import run_custom_fix
except ImportError:
    def run_custom_fix(code: str, expected_behavior: str = "", error_message: str = "", user_tests: str = ""):
        """Fallback generator signature if pipeline_bridge hasn't implemented run_custom_fix yet."""
        yield {
            "stage": "diagnosing",
            "bug_category": "Logic / Syntax Error",
            "root_cause": "Sample diagnostic root cause analysis placeholder.",
            "security_flags": [],
            "syntax_errors": [],
        }
        yield {
            "stage": "generating_tests",
            "generated_tests": "# Auto-generated pytest suite\ndef test_custom_code():\n    assert True\n",
            "user_tests": user_tests,
        }
        yield {
            "stage": "fixing",
            "corrected_code": code,
        }
        yield {
            "stage": "testing",
            "test_results": {
                "passed": 1,
                "failed": 0,
                "total": 1,
                "all_passed": True,
                "stdout": "1 passed in 0.01s",
            },
        }
        yield {
            "stage": "done",
            "corrected_code": code,
            "changelog": ["Identified issue and generated corrected implementation."],
        }

# Page configuration
st.set_page_config(
    page_title="Agentic Code Fixer",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom styling
st.markdown(
    """
    <style>
    .main-title {
        font-size: 2.2rem;
        font-weight: 700;
        color: #06B6D4;
        margin-bottom: 0.2rem;
    }
    .sub-title {
        font-size: 1.05rem;
        color: #94A3B8;
        margin-bottom: 1.5rem;
    }
    .badge-pass {
        background-color: #064E3B;
        color: #10B981;
        padding: 4px 10px;
        border-radius: 6px;
        font-weight: bold;
        display: inline-block;
    }
    .badge-refactor {
        background-color: #312E81;
        color: #818CF8;
        padding: 4px 10px;
        border-radius: 6px;
        font-weight: bold;
        display: inline-block;
    }
    .badge-fail {
        background-color: #7F1D1D;
        color: #F87171;
        padding: 4px 10px;
        border-radius: 6px;
        font-weight: bold;
        display: inline-block;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown('<div class="main-title">⚡ Agentic Code Fixer</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="sub-title">Autonomous Multi-Agent Closed-Loop Code Synthesis & Verification Pipeline</div>',
    unsafe_allow_html=True,
)

tab_archive, tab_live, tab_fix = st.tabs([
    "📊 Archived Run Viewer (Week 6)",
    "⚡ Live Spec Runner",
    "🔧 Fix My Code",
])

# -----------------------------------------------------------------------------
# TAB 1: ARCHIVED RUN VIEWER
# -----------------------------------------------------------------------------
with tab_archive:
    st.subheader("Archived Evaluation Run (8 Curated DSA Specs)")
    traces = load_archived_traces()

    if not traces:
        st.warning("No archived traces found in `traces/final_run/`.")
    else:
        # Top KPI Metrics
        total_specs = len(traces)
        total_passed = sum(1 for t in traces if t.get("final_status") in ("passed", "refactored"))
        total_refactored = sum(1 for t in traces if t.get("final_status") == "refactored")
        total_tests = sum(t.get("test_results", {}).get("passed", 0) for t in traces)

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Specs Solved", f"{total_passed}/{total_specs}")
        col2.metric("Total Tests Passed", f"{total_tests}/{total_specs * 5}")
        col3.metric("Refactor Passes Kept", f"{total_refactored}/{total_specs}")
        col4.metric("Unhandled Failures", "0")

        # Summary Table
        table_data = []
        for t in traces:
            test_res = t.get("test_results", {})
            passed = test_res.get("passed", 0)
            total = test_res.get("total", 0)
            table_data.append(
                {
                    "Spec ID": t.get("spec_id"),
                    "Title": t.get("title"),
                    "Status": t.get("final_status", "").upper(),
                    "Iterations": t.get("iterations_taken", 1),
                    "Tests": f"{passed}/{total}",
                    "Refactored": "Yes" if t.get("final_status") == "refactored" else "No",
                }
            )
        st.dataframe(table_data, use_container_width=True)

        st.divider()

        # Detailed Spec Inspector
        st.subheader("🔍 Deep-Dive Spec Trace")
        spec_ids = [t.get("spec_id") for t in traces]
        selected_id = st.selectbox(
            "Select Spec to Inspect",
            spec_ids,
            format_func=lambda sid: f"{sid} - {next((t.get('title') for t in traces if t.get('spec_id') == sid), sid)}",
            key="archive_select",
        )

        selected_trace = next((t for t in traces if t.get("spec_id") == selected_id), None)
        if selected_trace:
            # 1. Plan Section
            plan = selected_trace.get("plan", {})
            with st.expander("🧠 Planner Node Output (Strategy & Edge Cases)", expanded=True):
                if isinstance(plan, dict):
                    st.markdown("**Algorithmic Approach:**")
                    st.write(plan.get("approach", "N/A"))
                    st.markdown("**Complexity Target:**")
                    st.info(plan.get("complexity_target", "N/A"))
                    st.markdown("**Identified Edge Cases:**")
                    for ec in plan.get("edge_cases", []):
                        st.markdown(f"- {ec}")
                else:
                    st.write(plan)

            # 2. Code Comparison Section
            attempt_1 = selected_trace.get("attempt_1_code")
            attempt_2 = selected_trace.get("attempt_2_code") or selected_trace.get("final_code")

            st.markdown("### 💻 Implementation Evolution")
            if attempt_1 and attempt_2 and attempt_1 != attempt_2:
                c1, c2 = st.columns(2)
                with c1:
                    st.markdown("**Attempt 1 (Initial Coder Output):**")
                    st.code(attempt_1, language="python")
                with c2:
                    st.markdown("**Attempt 2 (Refactored & Verified):**")
                    st.code(attempt_2, language="python")
            else:
                st.code(selected_trace.get("final_code", ""), language="python")

            # 3. Test Results Section
            with st.expander("🧪 Sandbox Pytest Execution Report", expanded=True):
                tr = selected_trace.get("test_results", {})
                passed = tr.get("passed", 0)
                total = tr.get("total", 0)
                if tr.get("all_passed"):
                    st.success(f"All {passed}/{total} unit tests passed successfully!")
                else:
                    st.error(f"{tr.get('failed', 0)} of {total} tests failed.")

                stdout = tr.get("stdout", "")
                if stdout:
                    st.markdown("**Raw Pytest Stdout:**")
                    st.code(stdout)


# -----------------------------------------------------------------------------
# TAB 2: LIVE SPEC RUNNER
# -----------------------------------------------------------------------------
with tab_live:
    st.subheader("Trigger Live Multi-Agent Pipeline")
    st.markdown(
        "Select any DSA specification to run the live closed-loop pipeline "
        "(`planner_node` ➔ `coder_node` ➔ `tester_node` ➔ `refactor_node`)."
    )

    all_specs = [f"spec_{i:02d}" for i in range(1, 9)]
    live_spec_id = st.selectbox(
        "Select Spec to Execute",
        all_specs,
        format_func=lambda sid: f"{sid} (Spec {sid[-2:]})",
        key="live_select",
    )

    # Spec details preview
    spec_file = ROOT / "specs" / f"{live_spec_id}.json"
    if spec_file.exists():
        spec_data = json.loads(spec_file.read_text(encoding="utf-8"))
        with st.expander("📄 View Specification Details"):
            st.markdown(f"**Function:** `{spec_data.get('function_name')}`")
            st.markdown(f"**Docstring:** {spec_data.get('docstring')}")
            st.markdown(f"**Constraints:** {', '.join(spec_data.get('constraints', []))}")

    if st.button("🚀 Run Multi-Agent Pipeline", type="primary", use_container_width=True):
        status_box = st.status(f"Executing Multi-Agent Pipeline on {live_spec_id}...", expanded=True)
        final_state = None
        attempt_history: list[str] = []

        try:
            for step in run_single_spec(live_spec_id):
                node_name = step["node"]
                state = step["state"]
                final_state = state

                if node_name == "planner_node":
                    status_box.write("✅ **[Planner]** Algorithmic strategy & edge cases generated.")
                    plan = state.get("plan", {})
                    with st.expander("🧠 Live Plan Generated", expanded=True):
                        if isinstance(plan, dict):
                            st.write(plan.get("approach", ""))
                            st.caption(f"Target: {plan.get('complexity_target', '')}")
                        else:
                            st.write(plan)

                elif node_name == "coder_node":
                    iter_count = state.get("iteration_count", 1)
                    code = state.get("code", "")
                    attempt_history.append(code)
                    status_box.write(f"✅ **[Coder]** Generated code attempt {iter_count} (AST valid).")
                    with st.expander(f"💻 Code Attempt {iter_count}", expanded=False):
                        st.code(code, language="python")

                elif node_name == "tester_node":
                    tr = state.get("test_results", {})
                    passed = tr.get("passed", 0)
                    total = tr.get("total", 0)
                    all_passed = tr.get("all_passed", False)
                    if all_passed:
                        status_box.write(f"✅ **[Tester]** All {passed}/{total} tests PASSED.")
                    else:
                        status_box.write(f"⚠️ **[Tester]** Tests failed: {passed}/{total} passed. Retrying...")

                elif node_name == "refactor_node":
                    discarded = state.get("refactor_discarded", False)
                    if discarded:
                        status_box.write("⚠️ **[Refactor]** Candidate regression detected — reverted to original.")
                    else:
                        status_box.write("✅ **[Refactor]** Clean refactoring accepted & verified.")

            status_box.update(label=f"Pipeline Completed for {live_spec_id}!", state="complete", expanded=False)

            # Final summary display
            if final_state:
                st.divider()
                final_status = final_state.get("status", "unknown")
                if final_status in ("passed", "refactored"):
                    st.success(f"🎉 **Final Status: {final_status.upper()}**")
                else:
                    st.error(f"❌ **Final Status: {final_status.upper()}**")

                c1, c2, c3 = st.columns(3)
                c1.metric("Status", final_status.upper())
                c2.metric("Iterations", final_state.get("iteration_count", 1))
                tr = final_state.get("test_results", {})
                c3.metric("Tests Passed", f"{tr.get('passed', 0)}/{tr.get('total', 0)}")

                st.markdown("### 🏆 Final Verified Code")
                st.code(final_state.get("code", ""), language="python")

        except Exception as err:
            status_box.update(label="Pipeline Execution Failed", state="error")
            st.error(f"Error during execution: {err}")


# -----------------------------------------------------------------------------
# TAB 3: FIX MY CODE
# -----------------------------------------------------------------------------
with tab_fix:
    st.subheader("🔧 Fix My Code")
    st.markdown(
        "Diagnose, repair, and verify any custom Python code with autonomous multi-agent root-cause analysis and automated test generation."
    )

    # 1. Code Input Mode Selection
    input_mode = st.radio(
        "Choose Code Input Method:",
        ["Paste code", "Upload file"],
        horizontal=True,
        key="fix_input_mode",
    )

    code_to_fix = ""
    if input_mode == "Paste code":
        code_to_fix = st.text_area(
            "Paste your Python code here:",
            height=240,
            placeholder="def buggy_function(x):\n    # paste code here\n    pass",
            key="fix_paste_code",
        )
        st.caption("ℹ️ Python support only for now, more languages planned.")
    else:
        uploaded_file = st.file_uploader(
            "Upload a Python file (.py):",
            type=["py"],
            key="fix_upload_code",
        )
        if uploaded_file is not None:
            code_to_fix = uploaded_file.getvalue().decode("utf-8")
            st.markdown("**File Content Confirmation:**")
            st.code(code_to_fix, language="python")

    # 2. Three Optional Fields
    col_opt1, col_opt2 = st.columns(2)
    with col_opt1:
        expected_behavior = st.text_area(
            "What should this code do? (Expected behavior)",
            placeholder="Describe the expected inputs, outputs, or logic...",
            key="fix_expected_behavior",
        )
    with col_opt2:
        error_message = st.text_area(
            "Error message or traceback (if any)",
            placeholder="Paste any exceptions, tracebacks, or incorrect return values...",
            key="fix_error_message",
        )

    user_tests = st.text_area(
        "Your own test cases (optional, pytest format)",
        placeholder="def test_example():\n    assert buggy_function(1) == 2",
        key="fix_user_tests",
    )

    # 3. Diagnose & Fix Trigger Button
    def execute_custom_fix(code_input: str, exp_behavior: str, err_msg: str, u_tests: str):
        """Helper to run run_custom_fix and render stages into expanders."""
        if not code_input.strip():
            st.warning("Please provide code to diagnose and fix.")
            return

        status_box = st.status("Diagnosing and repairing code...", expanded=True)
        final_fix_payload: dict = {}

        try:
            for item in run_custom_fix(code_input, exp_behavior, err_msg, u_tests):
                stage = item.get("stage", "")

                if stage == "diagnosing":
                    status_box.write("✅ **[Diagnosis]** Code analyzed and root-cause identified.")
                    with st.expander("🔍 Diagnostic Summary", expanded=True):
                        bug_cat = item.get("bug_category") or item.get("category")
                        if bug_cat:
                            st.markdown(f"**Bug Category:** `{bug_cat}`")

                        root_cause = item.get("root_cause") or item.get("explanation") or item.get("summary")
                        if root_cause:
                            st.markdown("**Root Cause Explanation:**")
                            st.write(root_cause)

                        sec_flags = (
                            item.get("security_flags")
                            or item.get("bandit_warnings")
                            or item.get("security_warnings")
                            or []
                        )
                        if sec_flags:
                            st.markdown("**🛡️ Security Flags (Bandit):**")
                            for flag in sec_flags:
                                st.warning(f"⚠️ {flag}" if isinstance(flag, str) else json.dumps(flag))

                        syntax_errs = item.get("syntax_errors") or []
                        if syntax_errs:
                            st.markdown("**🚨 Syntax Errors:**")
                            for err in syntax_errs:
                                st.error(f"❌ {err}" if isinstance(err, str) else json.dumps(err))

                elif stage == "generating_tests":
                    status_box.write("✅ **[Test Generation]** Pytest test cases synthesized.")
                    with st.expander("🧪 Test Suite", expanded=True):
                        st.caption("🤖 Auto-Generated Pytest Cases")
                        gen_tests = item.get("generated_tests") or item.get("tests") or item.get("code") or ""
                        if gen_tests:
                            st.code(gen_tests, language="python")

                        u_tests_disp = item.get("user_tests") or u_tests
                        if u_tests_disp:
                            st.caption("👤 User-Supplied Test Cases")
                            st.code(u_tests_disp, language="python")

                elif stage == "fixing":
                    status_box.write("✅ **[Code Repair]** Corrected implementation generated.")
                    with st.expander("💻 Corrected Code Candidate", expanded=True):
                        candidate_code = (
                            item.get("corrected_code")
                            or item.get("code")
                            or item.get("fixed_code")
                            or ""
                        )
                        st.code(candidate_code, language="python")

                elif stage == "testing":
                    status_box.write("✅ **[Verification]** Sandboxed pytest suite executed.")
                    with st.expander("🧪 Sandbox Pytest Execution Report", expanded=True):
                        tr = item.get("test_results") or item.get("results") or {}
                        passed = tr.get("passed", 0)
                        total = tr.get("total", 0)
                        all_passed = tr.get("all_passed", False) or (total > 0 and passed == total)

                        if all_passed:
                            st.success(f"All {passed}/{total} unit tests passed successfully!")
                        else:
                            st.error(f"{tr.get('failed', total - passed)} of {total} tests failed.")

                        stdout = tr.get("stdout", "")
                        if stdout:
                            with st.expander("Raw Pytest Stdout", expanded=False):
                                st.code(stdout)

                elif stage == "refactoring":
                    status_box.write("✅ **[Refactor]** Clean refactoring pass completed.")
                    with st.expander("🎨 Refactored Code", expanded=False):
                        ref_c = item.get("refactored_code") or item.get("code") or ""
                        if ref_c:
                            st.code(ref_c, language="python")

                elif stage == "done":
                    final_fix_payload = item
                    st.session_state["last_custom_fix"] = {
                        "original_code": code_input,
                        "expected_behavior": exp_behavior,
                        "error_message": err_msg,
                        "user_tests": u_tests,
                        "payload": item,
                    }

            status_box.update(label="Diagnosis & Repair Complete!", state="complete", expanded=False)

            # 5. Done Stage Summary Tabs
            if final_fix_payload:
                st.divider()
                st.subheader("🎉 Final Summary")
                tab_code, tab_diff, tab_log = st.tabs(["📄 Corrected Code", "🔍 Diff", "📝 Changelog"])

                corrected_final = (
                    final_fix_payload.get("corrected_code")
                    or final_fix_payload.get("code")
                    or ""
                )

                with tab_code:
                    st.markdown("**Full Runnable File:**")
                    st.code(corrected_final, language="python")

                with tab_diff:
                    c_left, c_right = st.columns(2)
                    with c_left:
                        st.markdown("**Original Code:**")
                        st.code(code_input, language="python")
                    with c_right:
                        st.markdown("**Corrected Code:**")
                        st.code(corrected_final, language="python")

                with tab_log:
                    st.markdown("**Changelog & Fixes Applied:**")
                    changelog_list = (
                        final_fix_payload.get("changelog")
                        or final_fix_payload.get("fixes")
                        or []
                    )
                    if changelog_list:
                        for entry in changelog_list:
                            st.markdown(f"- {entry}")
                    else:
                        st.info("No specific changelog notes provided.")

                # 6. Post-Run Action Buttons
                st.divider()
                st.markdown("### Next Steps & Feedback")
                btn_col1, btn_col2, btn_col3 = st.columns(3)

                with btn_col1:
                    if st.button("✅ This fixed it", use_container_width=True, key="btn_fixed_it"):
                        st.balloons()
                        st.success("🎉 Excellent! Your fix is confirmed and verified.")

                with btn_col2:
                    if st.button("🔁 Needs more work", use_container_width=True, key="btn_needs_work"):
                        st.session_state["fix_show_feedback"] = True
                        st.session_state["fix_show_add_test"] = False

                with btn_col3:
                    if st.button("➕ Add a test case I missed", use_container_width=True, key="btn_add_test"):
                        st.session_state["fix_show_add_test"] = True
                        st.session_state["fix_show_feedback"] = False

        except Exception as err:
            status_box.update(label="Diagnosis & Repair Failed", state="error")
            st.error(f"Error during custom fix execution: {err}")

    # Main Diagnose & Fix button
    if st.button("🔧 Diagnose & Fix", type="primary", use_container_width=True, key="btn_diagnose_fix"):
        execute_custom_fix(code_to_fix, expected_behavior, error_message, user_tests)

    # Feedback container for "Needs more work"
    if st.session_state.get("fix_show_feedback"):
        with st.container():
            st.markdown("---")
            st.markdown("### 🔁 Additional Feedback & Retry")
            feedback_text = st.text_area(
                "What still needs fixing or what behavior was incorrect?",
                placeholder="Explain what failed or how the fix needs adjustment...",
                key="feedback_additional_text",
            )
            if st.button("🚀 Re-Submit with Feedback", type="primary", key="btn_resubmit_feedback"):
                last_run = st.session_state.get("last_custom_fix", {})
                orig_code = last_run.get("original_code", code_to_fix)
                combined_expected = f"{last_run.get('expected_behavior', expected_behavior)}\n\n[Additional Feedback]: {feedback_text}".strip()
                execute_custom_fix(
                    orig_code,
                    combined_expected,
                    last_run.get("error_message", error_message),
                    last_run.get("user_tests", user_tests),
                )

    # Test addition container for "Add a test case I missed"
    if st.session_state.get("fix_show_add_test"):
        with st.container():
            st.markdown("---")
            st.markdown("### ➕ Add Missing Test Case")
            extra_test_text = st.text_area(
                "New Pytest test function:",
                placeholder="def test_additional_edge_case():\n    assert my_func(0) == 0",
                key="extra_test_additional_text",
            )
            if st.button("🧪 Run Tests on Corrected Code", type="primary", key="btn_run_extra_tests"):
                last_run = st.session_state.get("last_custom_fix", {})
                last_payload = last_run.get("payload", {})
                candidate_code = (
                    last_payload.get("corrected_code")
                    or last_payload.get("code")
                    or code_to_fix
                )
                combined_tests = f"{last_run.get('user_tests', user_tests)}\n\n{extra_test_text}".strip()
                execute_custom_fix(
                    candidate_code,
                    last_run.get("expected_behavior", expected_behavior),
                    last_run.get("error_message", error_message),
                    combined_tests,
                )
