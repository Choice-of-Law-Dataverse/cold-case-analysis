# utils/browser_storage.py
"""
Client-side browser localStorage integration using streamlit-local-storage.
Provides persistent state storage in the user's browser with support for multiple analyses.
"""
import json
import logging
import time
import uuid

import streamlit as st
from streamlit_local_storage import LocalStorage

logger = logging.getLogger(__name__)

# Storage keys
AUTH_STATE_KEY = "cold_auth_state"
ANALYSES_LIST_KEY = "cold_analyses_list"
CURRENT_ANALYSIS_ID_KEY = "cold_current_analysis_id"


def _get_local_storage():
    """Get or create LocalStorage instance from session state."""
    if "_local_storage_instance" not in st.session_state:
        st.session_state._local_storage_instance = LocalStorage()
    return st.session_state._local_storage_instance


def _generate_analysis_id() -> str:
    """
    Generate a short analysis ID from UUID v7 (time-ordered).
    Returns last 8 characters for display purposes.
    """
    # Python's uuid doesn't have v7 yet, so we'll use v4 with timestamp
    # and extract last 8 chars for a short ID
    full_id = str(uuid.uuid4())
    short_id = full_id.split("-")[-1][:8]  # Last 8 chars of last segment
    return short_id


def _get_analysis_key(analysis_id: str) -> str:
    """Get localStorage key for specific analysis."""
    return f"cold_analysis_{analysis_id}"


def save_auth_state(auth_state: dict) -> None:
    """
    Save authentication state to browser localStorage.

    Args:
        auth_state: Dictionary containing logged_in, user, llm_model_select
    """
    try:
        localS = _get_local_storage()
        json_str = json.dumps(auth_state)
        localS.setItem(AUTH_STATE_KEY, json_str)
        logger.debug("Saved auth state to browser localStorage")
    except Exception as e:
        logger.error(f"Error saving auth state to localStorage: {e}")


def load_auth_state() -> dict | None:
    """
    Load authentication state from browser localStorage.

    Returns:
        dict: Auth state or None if not found
    """
    try:
        localS = _get_local_storage()
        json_str = localS.getItem(AUTH_STATE_KEY)
        if json_str:
            auth_state = json.loads(json_str)
            logger.debug("Loaded auth state from browser localStorage")
            return auth_state
        return None
    except Exception as e:
        logger.error(f"Error loading auth state from localStorage: {e}")
        return None


def clear_auth_state() -> None:
    """Clear authentication state from browser localStorage."""
    try:
        localS = _get_local_storage()
        localS.deleteItem(AUTH_STATE_KEY)
        logger.debug("Cleared auth state from browser localStorage")
    except Exception as e:
        logger.error(f"Error clearing auth state: {e}")


def create_new_analysis(case_citation: str = "") -> str:
    """
    Create a new analysis and return its ID.

    Args:
        case_citation: Optional case citation for the analysis

    Returns:
        str: The new analysis ID
    """
    try:
        localS = _get_local_storage()
        analysis_id = _generate_analysis_id()

        # Create analysis metadata
        metadata = {
            "id": analysis_id,
            "created_at": time.time(),
            "updated_at": time.time(),
            "submitted_at": None,
            "case_citation": case_citation or "Untitled Analysis",
        }

        # Add to analyses list
        analyses = list_analyses()
        analyses.append(metadata)
        localS.setItem(ANALYSES_LIST_KEY, json.dumps(analyses))

        # Initialize empty analysis state with proper defaults
        analysis_state = {
            "col_state": {},
            "case_citation": case_citation or "",
            "full_text_input": "",
            "user_email": "",
            "col_extraction_started": False,
            "jurisdiction_detected": False,
            "jurisdiction_confirmed": False,
            "precise_jurisdiction": None,
            "precise_jurisdiction_confirmed": False,
            "legal_system_type": None,
        }

        analysis_key = _get_analysis_key(analysis_id)
        localS.setItem(analysis_key, json.dumps(analysis_state))

        # Set as current analysis
        localS.setItem(CURRENT_ANALYSIS_ID_KEY, analysis_id)

        logger.info(f"Created new analysis: {analysis_id}")
        return analysis_id

    except Exception as e:
        logger.error(f"Error creating new analysis: {e}")
        # Return empty string on error - caller should check for this
        return ""


def list_analyses() -> list:
    """
    Get list of all analyses with metadata.

    Returns:
        list: List of analysis metadata dictionaries
    """
    try:
        localS = _get_local_storage()
        json_str = localS.getItem(ANALYSES_LIST_KEY)
        if json_str:
            analyses = json.loads(json_str)
            # Sort by created_at descending (newest first)
            analyses.sort(key=lambda x: x.get("created_at", 0), reverse=True)
            return analyses
        return []
    except Exception as e:
        logger.error(f"Error listing analyses: {e}")
        return []


def get_current_analysis_id() -> str | None:
    """Get the ID of the current analysis."""
    try:
        localS = _get_local_storage()
        return localS.getItem(CURRENT_ANALYSIS_ID_KEY)
    except Exception as e:
        logger.error(f"Error getting current analysis ID: {e}")
        return None


def set_current_analysis_id(analysis_id: str) -> None:
    """Set the current analysis ID."""
    try:
        localS = _get_local_storage()
        localS.setItem(CURRENT_ANALYSIS_ID_KEY, analysis_id)
        logger.info(f"Set current analysis to: {analysis_id}")
    except Exception as e:
        logger.error(f"Error setting current analysis ID: {e}")


def save_analysis_state(analysis_state: dict, analysis_id: str | None = None) -> None:
    """
    Save analysis state to browser localStorage.

    Args:
        analysis_state: Dictionary containing col_state, case_citation, full_text, etc.
        analysis_id: Optional specific analysis ID, uses current if not provided
    """
    try:
        localS = _get_local_storage()

        if analysis_id is None:
            analysis_id = get_current_analysis_id()

        if not analysis_id:
            # No current analysis, create one
            case_citation = analysis_state.get("case_citation", "")
            analysis_id = create_new_analysis(case_citation)

        # Save analysis state
        analysis_key = _get_analysis_key(analysis_id)
        json_str = json.dumps(analysis_state)
        localS.setItem(analysis_key, json_str)

        # Update metadata
        _update_analysis_metadata(analysis_id, analysis_state)

        logger.debug(f"Saved analysis state for: {analysis_id}")
    except Exception as e:
        logger.error(f"Error saving analysis state to localStorage: {e}")


def _update_analysis_metadata(analysis_id: str, analysis_state: dict) -> None:
    """Update analysis metadata in the list."""
    try:
        localS = _get_local_storage()
        analyses = list_analyses()

        for analysis in analyses:
            if analysis["id"] == analysis_id:
                analysis["updated_at"] = time.time()
                analysis["case_citation"] = analysis_state.get("case_citation") or analysis.get("case_citation", "Untitled")
                break

        localS.setItem(ANALYSES_LIST_KEY, json.dumps(analyses))
    except Exception as e:
        logger.error(f"Error updating analysis metadata: {e}")


def load_analysis_state(analysis_id: str | None = None) -> dict | None:
    """
    Load analysis state from browser localStorage.

    Args:
        analysis_id: Optional specific analysis ID, uses current if not provided

    Returns:
        dict: Analysis state with default values, or None if not found
    """
    try:
        localS = _get_local_storage()

        if analysis_id is None:
            analysis_id = get_current_analysis_id()

        if not analysis_id:
            return None

        analysis_key = _get_analysis_key(analysis_id)
        json_str = localS.getItem(analysis_key)

        if json_str:
            analysis_state = json.loads(json_str)

            # Ensure all expected keys have default values
            defaults = {
                "col_state": {},
                "case_citation": "",
                "full_text_input": "",
                "user_email": "",
                "col_extraction_started": False,
                "jurisdiction_detected": False,
                "jurisdiction_confirmed": False,
                "precise_jurisdiction": None,
                "precise_jurisdiction_confirmed": False,
                "legal_system_type": None,
            }

            # Merge with defaults
            for key, default_value in defaults.items():
                if key not in analysis_state or analysis_state[key] is None:
                    analysis_state[key] = default_value

            logger.debug(f"Loaded analysis state for: {analysis_id}")
            return analysis_state
        return None
    except Exception as e:
        logger.error(f"Error loading analysis state from localStorage: {e}")
        return None


def mark_analysis_submitted(analysis_id: str | None = None) -> None:
    """
    Mark an analysis as submitted with timestamp.

    Args:
        analysis_id: Optional specific analysis ID, uses current if not provided
    """
    try:
        localS = _get_local_storage()

        if analysis_id is None:
            analysis_id = get_current_analysis_id()

        if not analysis_id:
            return

        analyses = list_analyses()
        for analysis in analyses:
            if analysis["id"] == analysis_id:
                analysis["submitted_at"] = time.time()
                break

        localS.setItem(ANALYSES_LIST_KEY, json.dumps(analyses))
        logger.info(f"Marked analysis as submitted: {analysis_id}")
    except Exception as e:
        logger.error(f"Error marking analysis as submitted: {e}")


def delete_analysis(analysis_id: str) -> None:
    """
    Delete an analysis from browser localStorage.

    Args:
        analysis_id: The analysis ID to delete
    """
    try:
        localS = _get_local_storage()

        # Remove from analyses list
        analyses = list_analyses()
        analyses = [a for a in analyses if a["id"] != analysis_id]
        localS.setItem(ANALYSES_LIST_KEY, json.dumps(analyses))

        # Delete analysis data
        analysis_key = _get_analysis_key(analysis_id)
        localS.deleteItem(analysis_key)

        # If this was the current analysis, clear it
        if get_current_analysis_id() == analysis_id:
            localS.deleteItem(CURRENT_ANALYSIS_ID_KEY)

        logger.info(f"Deleted analysis: {analysis_id}")
    except Exception as e:
        logger.error(f"Error deleting analysis: {e}")


def clear_analysis_state() -> None:
    """Clear current analysis state from browser localStorage."""
    try:
        analysis_id = get_current_analysis_id()
        if analysis_id:
            delete_analysis(analysis_id)
        logger.debug("Cleared current analysis state")
    except Exception as e:
        logger.error(f"Error clearing analysis state: {e}")


def clear_all_storage() -> None:
    """Clear all CoLD app data from browser localStorage."""
    try:
        localS = _get_local_storage()

        # Clear auth
        clear_auth_state()

        # Delete all analyses
        analyses = list_analyses()
        for analysis in analyses:
            analysis_key = _get_analysis_key(analysis["id"])
            localS.deleteItem(analysis_key)

        # Clear metadata
        localS.deleteItem(ANALYSES_LIST_KEY)
        localS.deleteItem(CURRENT_ANALYSIS_ID_KEY)

        logger.info("Cleared all storage")
    except Exception as e:
        logger.error(f"Error clearing all storage: {e}")
