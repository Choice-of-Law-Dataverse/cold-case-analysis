# utils/state_manager.py
"""
State management utilities for the CoLD Case Analyzer.
"""
import streamlit as st


def initialize_col_state():
    """Initialize the COL state in session state if not present."""
    if "col_state" not in st.session_state:
        st.session_state.col_state = {}
    if "is_processing" not in st.session_state:
        st.session_state.is_processing = False


def create_initial_analysis_state(case_citation, username, model, full_text, final_jurisdiction_data, user_email=None):
    """
    Create the initial analysis state dictionary.

    Args:
        case_citation: The case citation
        username: The current user
        model: The selected LLM model
        full_text: The full court decision text
        final_jurisdiction_data: The jurisdiction detection results

    Returns:
        dict: Initial state dictionary
    """
    return {
        "case_citation": case_citation,
        "username": username,
        "model": model,
        "full_text": full_text,
        "col_section": [],
        "col_section_feedback": [],
        "col_section_eval_iter": 0,
    "jurisdiction": final_jurisdiction_data.get("legal_system_type", "Unknown legal system"),
        "precise_jurisdiction": final_jurisdiction_data.get("jurisdiction_name"),
    "jurisdiction_eval_score": final_jurisdiction_data.get("evaluation_score"),
    "user_email": user_email,
    }


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
    # Also set a representative demo case citation
    st.session_state.case_citation = "Federal Court, 20.12.2005 - BGE 132 III 285"


def set_processing(is_processing: bool):
    """
    Set the processing state to disable/enable UI elements.
    
    Args:
        is_processing: True to disable UI elements, False to enable them
    """
    st.session_state.is_processing = is_processing


def is_processing() -> bool:
    """
    Check if the application is currently processing.
    
    Returns:
        bool: True if processing, False otherwise
    """
    return st.session_state.get("is_processing", False)
