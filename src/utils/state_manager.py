# utils/state_manager.py
"""
State management utilities for the CoLD Case Analyzer.
"""
import logging

import streamlit as st

logger = logging.getLogger(__name__)


def initialize_col_state():
    """Initialize the COL state in session state if not present."""
    if "col_state" not in st.session_state:
        st.session_state.col_state = {}


def restore_state_from_browser():
    """
    Restore state from browser localStorage if available.
    This should be called early in app initialization.
    """
    if "state_restored" in st.session_state:
        return

    try:
        from utils.browser_storage import (
            get_current_analysis_id,
            load_analysis_state,
            load_auth_state,
        )

        # Restore auth state
        auth_state = load_auth_state()
        if auth_state:
            for key, value in auth_state.items():
                if value is not None and key not in st.session_state:
                    st.session_state[key] = value
            logger.info("Restored auth state from browser localStorage")

        # Get current analysis ID
        analysis_id = get_current_analysis_id()
        if analysis_id:
            st.session_state["current_analysis_id"] = analysis_id

        # Restore current analysis state
        analysis_state = load_analysis_state()
        if analysis_state:
            for key, value in analysis_state.items():
                if value is not None and key not in st.session_state:
                    st.session_state[key] = value
            logger.info(f"Restored analysis state from browser localStorage: {analysis_id}")

        st.session_state.state_restored = True
    except Exception as e:
        logger.error(f"Error restoring state from browser: {e}")
        st.session_state.state_restored = True


def save_state_to_browser():
    """
    Save current session state to browser localStorage.
    This should be called after state changes.
    """
    try:
        from utils.browser_storage import save_analysis_state, save_auth_state

        # Save auth state
        auth_state = {
            "logged_in": st.session_state.get("logged_in", False),
            "user": st.session_state.get("user", ""),
            "llm_model_select": st.session_state.get("llm_model_select"),
        }
        save_auth_state(auth_state)

        # Save analysis state (to current analysis)
        analysis_state = {
            "col_state": st.session_state.get("col_state", {}),
            "case_citation": st.session_state.get("case_citation"),
            "full_text_input": st.session_state.get("full_text_input"),
            "user_email": st.session_state.get("user_email"),
            "col_extraction_started": st.session_state.get("col_extraction_started", False),
            "jurisdiction_detected": st.session_state.get("jurisdiction_detected", False),
            "jurisdiction_confirmed": st.session_state.get("jurisdiction_confirmed", False),
            "precise_jurisdiction": st.session_state.get("precise_jurisdiction"),
            "precise_jurisdiction_confirmed": st.session_state.get("precise_jurisdiction_confirmed", False),
            "legal_system_type": st.session_state.get("legal_system_type"),
        }

        # Get current analysis ID
        analysis_id = st.session_state.get("current_analysis_id")
        save_analysis_state(analysis_state, analysis_id)

        # Update current_analysis_id if it was just created
        from utils.browser_storage import get_current_analysis_id

        new_id = get_current_analysis_id()
        if new_id and new_id != analysis_id:
            st.session_state["current_analysis_id"] = new_id

    except Exception as e:
        logger.error(f"Error saving state to browser: {e}")


def clear_analysis_state_only():
    """Clear only the analysis state, keeping authentication intact."""
    try:
        from utils.browser_storage import clear_analysis_state

        # Clear browser storage
        clear_analysis_state()

        # Clear session state
        analysis_keys = [
            "col_state",
            "case_citation",
            "full_text_input",
            "user_email",
            "col_extraction_started",
            "jurisdiction_detected",
            "jurisdiction_confirmed",
            "precise_jurisdiction",
            "precise_jurisdiction_confirmed",
            "legal_system_type",
        ]

        for key in analysis_keys:
            if key in st.session_state:
                del st.session_state[key]

        st.session_state.col_state = {}
        logger.info("Cleared analysis state")
    except Exception as e:
        logger.error(f"Error clearing analysis state: {e}")


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
