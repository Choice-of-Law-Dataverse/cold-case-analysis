# components/main_workflow.py
"""
Main workflow orchestrator for the CoLD Case Analyzer.
"""

import streamlit as st

from components.agents_integration import execute_agents_workflow, render_agents_workflow_button
from components.analysis_workflow import render_analysis_workflow
from components.col_processor import render_col_processing
from components.input_handler import render_input_phase
from components.jurisdiction_detection import get_final_jurisdiction_data, render_jurisdiction_detection
from components.theme_classifier import render_theme_classification
from tools.col_extractor import extract_col_section
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

    # Automatically start COL extraction after jurisdiction confirmed
    if jurisdiction_confirmed:
        # Get final jurisdiction data
        final_jurisdiction_data = get_final_jurisdiction_data()

        # Create initial analysis state
        state = create_initial_analysis_state(
            case_citation=st.session_state.get("case_citation"),
            username=st.session_state.get("user"),
            model=st.session_state.get("llm_model_select"),
            full_text=full_text,
            final_jurisdiction_data=final_jurisdiction_data,
            user_email=st.session_state.get("user_email"),
        )

        # Update session state with initial state
        if not st.session_state.get("col_state"):
            st.session_state.col_state = state

        # Check if user wants to use agents workflow
        workflow_choice = render_agents_workflow_button(state)

        if workflow_choice == "agents":
            # User selected automated analysis
            execute_agents_workflow(state)
            return False
        elif workflow_choice == "traditional":
            # User selected traditional workflow - mark and start extraction
            st.session_state["col_extraction_started"] = True
            st.rerun()
        elif workflow_choice == "waiting":
            # Still showing the choice UI, don't proceed yet
            return False

        # Traditional workflow: Check if we haven't already started extraction
        if not st.session_state.get("col_extraction_started", False):
            st.markdown("## Choice of Law Analysis")
            st.markdown(
                "The Case Analyzer tends to over-extract. Please make sure only the relevant passages are left after your final review."
            )

            # Show progress banner while extracting
            from utils.progress_banner import hide_progress_banner, show_progress_banner

            show_progress_banner("Extracting Choice of Law section...")

            # Extract COL section
            result = extract_col_section(state)
            state.update(result)

            # Update session state
            st.session_state.col_state = state
            st.session_state["col_extraction_started"] = True

            # Clear the progress banner
            hide_progress_banner()
            st.rerun()

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
