# components/main_workflow.py
"""
Main workflow orchestrator for the CoLD Case Analyzer.
"""

import streamlit as st

from components.analysis_workflow import render_analysis_workflow
from components.input_handler import render_input_phase
from components.jurisdiction import get_final_jurisdiction_data, render_jurisdiction_detection
from utils.state_manager import create_initial_analysis_state, get_col_state


def render_initial_input_phase():
    """
    Render the initial input phase before any processing has begun.

    Returns:
        bool: True if ready to proceed to COL extraction, False otherwise
    """

    full_text = render_input_phase()

    if not full_text.strip():
        return False

    jurisdiction_confirmed = render_jurisdiction_detection(full_text)

    if jurisdiction_confirmed:
        if not st.session_state.get("workflow_started", False):
            st.markdown("## Case Analysis")

            with st.spinner("Initializing analysis..."):
                final_jurisdiction_data = get_final_jurisdiction_data()

                state = create_initial_analysis_state(
                    case_citation=st.session_state.get("case_citation"),
                    username=st.session_state.get("user"),
                    full_text=full_text,
                    final_jurisdiction_data=final_jurisdiction_data,
                    user_email=st.session_state.get("user_email"),
                )

                # Mark workflow as started and analysis as ready
                # The generator will handle CoL extraction and theme classification automatically
                state["workflow_started"] = True
                state["analysis_ready"] = True

                st.session_state.col_state = state
                st.session_state["workflow_started"] = True
                st.rerun()

    return False


def render_main_workflow():
    """Render the complete main workflow."""
    if not get_col_state().get("full_text"):
        render_initial_input_phase()
    else:
        render_analysis_workflow()
