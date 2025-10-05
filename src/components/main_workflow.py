# components/main_workflow.py
"""
Main workflow orchestrator for the CoLD Case Analyzer.
"""

import streamlit as st

from components.agents_integration import execute_agents_workflow
from components.analysis_workflow import render_analysis_workflow
from components.col_processor import render_col_processing
from components.input_handler import render_input_phase
from components.jurisdiction_detection import get_final_jurisdiction_data, render_jurisdiction_detection
from components.theme_classifier import render_theme_classification
from utils.state_manager import create_initial_analysis_state, get_col_state


def render_initial_input_phase():
    """
    Render the initial input phase before any processing has begun.

    Returns:
        bool: True if ready to proceed to COL extraction, False otherwise
    """
    # Render input components
    case_citation, full_text = render_input_phase()

    # Enforce mandatory case citation
    if not case_citation or not case_citation.strip():
        st.warning("Please enter a Case Citation before proceeding.")
        return False

    if not full_text.strip():
        return False

    # Enhanced Jurisdiction Detection
    st.markdown("## Jurisdiction Identification")
    st.markdown(
        "The first step consists of identifying the precise jurisdiction and legal system type from the court decision."
    )

    jurisdiction_confirmed = render_jurisdiction_detection(full_text)

    # Automatically start agents workflow after jurisdiction confirmed
    if jurisdiction_confirmed:
        # Get final jurisdiction data
        final_jurisdiction_data = get_final_jurisdiction_data()

        # Create initial analysis state
        # Use existing state if available, otherwise create new
        if st.session_state.get("col_state"):
            state = st.session_state.col_state
        else:
            state = create_initial_analysis_state(
                case_citation=st.session_state.get("case_citation"),
                username=st.session_state.get("user"),
                model=st.session_state.get("llm_model_select"),
                full_text=full_text,
                final_jurisdiction_data=final_jurisdiction_data,
                user_email=st.session_state.get("user_email"),
            )
            st.session_state.col_state = state

        # Automatically run agents workflow if not already completed
        if not state.get("agents_workflow_completed", False):
            execute_agents_workflow(state)
            return False

    return False


def render_processing_phases():
    """Render the COL processing, theme classification, and analysis phases."""
    col_state = get_col_state()

    # COL processing phase
    render_col_processing(col_state)

    # Theme classification phase
    render_theme_classification(col_state)

    # Analysis workflow phase
    render_analysis_workflow(col_state)


def render_main_workflow():
    """Render the complete main workflow."""
    if not get_col_state().get("full_text"):
        render_initial_input_phase()
    else:
        render_processing_phases()
