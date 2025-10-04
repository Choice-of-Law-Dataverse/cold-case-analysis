# utils/persistent_state.py
"""
Local file-based state persistence for browser refresh resilience.
Uses JSON files in a temporary directory for local, performant state storage.
"""
import json
import logging
import time
import uuid
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

# Session storage directory
SESSION_DIR = Path("/tmp/cold_sessions")
SESSION_MAX_AGE_DAYS = 7


def _ensure_session_dir():
    """Create session directory if it doesn't exist."""
    SESSION_DIR.mkdir(parents=True, exist_ok=True)


def _cleanup_old_sessions():
    """Remove session files older than SESSION_MAX_AGE_DAYS."""
    try:
        _ensure_session_dir()
        current_time = time.time()
        max_age_seconds = SESSION_MAX_AGE_DAYS * 24 * 60 * 60

        for session_file in SESSION_DIR.glob("*.json"):
            file_age = current_time - session_file.stat().st_mtime
            if file_age > max_age_seconds:
                session_file.unlink()
                logger.debug(f"Cleaned up old session file: {session_file.name}")
    except Exception as e:
        logger.warning(f"Error cleaning up old sessions: {e}")


def generate_session_id() -> str:
    """Generate a new unique session ID."""
    return str(uuid.uuid4())


def get_session_file_path(session_id: str) -> Path:
    """Get the file path for a session ID."""
    _ensure_session_dir()
    return SESSION_DIR / f"{session_id}.json"


def save_persistent_state(session_id: str, auth_state: dict[str, Any], analysis_state: dict[str, Any]) -> bool:
    """
    Save state to local file storage.

    Args:
        session_id: The session identifier
        auth_state: Authentication state (logged_in, user, etc.)
        analysis_state: Analysis state (col_state)

    Returns:
        bool: True if save was successful, False otherwise
    """
    try:
        _ensure_session_dir()
        _cleanup_old_sessions()

        session_file = get_session_file_path(session_id)

        state_data = {
            "session_id": session_id,
            "timestamp": time.time(),
            "auth_state": auth_state,
            "analysis_state": analysis_state,
        }

        with open(session_file, "w") as f:
            json.dump(state_data, f, indent=2)

        logger.debug(f"Saved persistent state for session {session_id}")
        return True

    except Exception as e:
        logger.error(f"Error saving persistent state: {e}")
        return False


def load_persistent_state(session_id: str) -> dict[str, Any] | None:
    """
    Load state from local file storage.

    Args:
        session_id: The session identifier

    Returns:
        dict: State data with 'auth_state' and 'analysis_state' keys, or None if not found
    """
    try:
        session_file = get_session_file_path(session_id)

        if not session_file.exists():
            logger.debug(f"No persistent state found for session {session_id}")
            return None

        with open(session_file) as f:
            state_data = json.load(f)

        logger.debug(f"Loaded persistent state for session {session_id}")
        return state_data

    except Exception as e:
        logger.error(f"Error loading persistent state: {e}")
        return None


def delete_persistent_state(session_id: str) -> bool:
    """
    Delete persistent state for a session.

    Args:
        session_id: The session identifier

    Returns:
        bool: True if deletion was successful, False otherwise
    """
    try:
        session_file = get_session_file_path(session_id)

        if session_file.exists():
            session_file.unlink()
            logger.debug(f"Deleted persistent state for session {session_id}")
            return True
        return False

    except Exception as e:
        logger.error(f"Error deleting persistent state: {e}")
        return False


def clear_analysis_state(session_id: str) -> bool:
    """
    Clear only the analysis state, keeping auth state intact.

    Args:
        session_id: The session identifier

    Returns:
        bool: True if successful, False otherwise
    """
    try:
        state_data = load_persistent_state(session_id)
        if state_data:
            # Keep auth state, clear analysis state
            state_data["analysis_state"] = {}
            state_data["timestamp"] = time.time()

            session_file = get_session_file_path(session_id)
            with open(session_file, "w") as f:
                json.dump(state_data, f, indent=2)

            logger.debug(f"Cleared analysis state for session {session_id}")
            return True
        return False

    except Exception as e:
        logger.error(f"Error clearing analysis state: {e}")
        return False
