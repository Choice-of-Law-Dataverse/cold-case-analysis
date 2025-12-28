# utils/state_manager.py
"""
State management utilities for the CoLD Case Analyzer.
"""

import streamlit as st


def initialize_col_state():
    """Initialize the COL state in session state if not present."""
    if "col_state" not in st.session_state:
        st.session_state.col_state = {}


def create_initial_analysis_state(case_citation, username, full_text, final_jurisdiction_data, user_email=None):
    """
    Create the initial analysis state dictionary.

    Args:
        case_citation: The case citation
        username: The current user
        full_text: The full court decision text
        final_jurisdiction_data: The jurisdiction detection results
        user_email: Optional user email for contact

    Returns:
        dict: Initial state dictionary
    """
    import streamlit as st

    state = {
        "case_citation": case_citation,
        "username": username,
        "full_text": full_text,
        "col_section": [],
        "col_section_feedback": [],
        "jurisdiction": final_jurisdiction_data.get("legal_system_type", "Unknown legal system"),
        "precise_jurisdiction": final_jurisdiction_data.get("jurisdiction_name"),
        "jurisdiction_eval_score": final_jurisdiction_data.get("evaluation_score"),
        "user_email": user_email,
    }

    # Include PDF metadata if available in session state
    if "pdf_url" in st.session_state:
        state["pdf_url"] = st.session_state.pdf_url
    if "pdf_uuid" in st.session_state:
        state["pdf_uuid"] = st.session_state.pdf_uuid
    if "pdf_filename" in st.session_state:
        state["pdf_filename"] = st.session_state.pdf_filename

    return state


def update_col_state(state_updates):
    """
    Update the COL state with new data.

    Args:
        state_updates: Dictionary of updates to apply to col_state
    """
    st.session_state.col_state.update(state_updates)


def get_col_state():
    """
    Get the current COL state.

    Returns:
        dict: Current col_state dictionary
    """
    return st.session_state.col_state


def load_demo_case():
    """Demo loader callback to populate the text widget state."""
    from utils.data_loaders import get_demo_case_text

    st.session_state.full_text_input = get_demo_case_text()


def reset_workflow_state():
    """
    Reset the workflow state for a new submission while preserving authentication.
    Keeps: user, llm_model_select, user_email
    Resets: everything else
    """
    # Preserve auth and model selection
    preserved_keys = {
        "user": st.session_state.get("user"),
        "llm_model_select": st.session_state.get("llm_model_select"),
        "user_email": st.session_state.get("user_email"),
    }

    # Clear all session state
    for key in list(st.session_state.keys()):
        if key not in preserved_keys:
            del st.session_state[key]

    # Restore preserved values
    for key, value in preserved_keys.items():
        if value is not None:
            st.session_state[key] = value

    # Reinitialize col_state
    initialize_col_state()
