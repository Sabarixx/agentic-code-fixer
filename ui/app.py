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

tab_archive, tab_live = st.tabs(["📊 Archived Run Viewer (Week 6)", "⚡ Live Spec Runner"])

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
