# utils/browser_storage.py
"""
Client-side browser localStorage integration using streamlit-local-storage.
Provides persistent state storage in the user's browser.
"""
import json
import logging

from streamlit_local_storage import LocalStorage

logger = logging.getLogger(__name__)

# Storage keys
AUTH_STATE_KEY = "cold_auth_state"
ANALYSIS_STATE_KEY = "cold_analysis_state"

# Lazy initialization of localStorage
_local_storage = None


def _get_local_storage():
    """Get or create LocalStorage instance."""
    global _local_storage
    if _local_storage is None:
        _local_storage = LocalStorage()
    return _local_storage


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


def save_analysis_state(analysis_state: dict) -> None:
    """
    Save analysis state to browser localStorage.

    Args:
        analysis_state: Dictionary containing col_state, case_citation, full_text, etc.
    """
    try:
        localS = _get_local_storage()
        json_str = json.dumps(analysis_state)
        localS.setItem(ANALYSIS_STATE_KEY, json_str)
        logger.debug("Saved analysis state to browser localStorage")
    except Exception as e:
        logger.error(f"Error saving analysis state to localStorage: {e}")


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


def load_analysis_state() -> dict | None:
    """
    Load analysis state from browser localStorage.

    Returns:
        dict: Analysis state or None if not found
    """
    try:
        localS = _get_local_storage()
        json_str = localS.getItem(ANALYSIS_STATE_KEY)
        if json_str:
            analysis_state = json.loads(json_str)
            logger.debug("Loaded analysis state from browser localStorage")
            return analysis_state
        return None
    except Exception as e:
        logger.error(f"Error loading analysis state from localStorage: {e}")
        return None


def clear_auth_state() -> None:
    """Clear authentication state from browser localStorage."""
    try:
        localS = _get_local_storage()
        localS.deleteItem(AUTH_STATE_KEY)
        logger.debug("Cleared auth state from browser localStorage")
    except Exception as e:
        logger.error(f"Error clearing auth state: {e}")


def clear_analysis_state() -> None:
    """Clear analysis state from browser localStorage."""
    try:
        localS = _get_local_storage()
        localS.deleteItem(ANALYSIS_STATE_KEY)
        logger.debug("Cleared analysis state from browser localStorage")
    except Exception as e:
        logger.error(f"Error clearing analysis state: {e}")


def clear_all_storage() -> None:
    """Clear all CoLD app data from browser localStorage."""
    clear_auth_state()
    clear_analysis_state()
