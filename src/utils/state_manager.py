# utils/state_manager.py
"""
State management utilities for the CoLD Case Analyzer.
"""
import json
import uuid
from datetime import datetime

import streamlit as st


def initialize_col_state():
    """Initialize the COL state in session state if not present."""
    if "col_state" not in st.session_state:
        # Try to restore from storage first
        restored_state = restore_state_from_storage()
        st.session_state.col_state = restored_state.get("col_state", {}) if restored_state else {}

        # Also restore jurisdiction-related session state keys
        if restored_state:
            jurisdiction_keys = [
                "precise_jurisdiction", "precise_jurisdiction_detected", "legal_system_type",
                "precise_jurisdiction_eval_score", "precise_jurisdiction_eval_submitted",
                "precise_jurisdiction_confirmed", "jurisdiction_manual_override"
            ]
            for key in jurisdiction_keys:
                if key in restored_state:
                    st.session_state[key] = restored_state[key]

    # Ensure session ID exists
    get_or_create_session_id()


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

    # Auto-save to storage for persistence
    save_state_to_storage(st.session_state.col_state)


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


def get_or_create_session_id():
    """
    Get or create a unique session ID for state persistence.

    Returns:
        str: Session ID
    """
    # Try to get session ID from query params first
    if "session_id" in st.query_params:
        session_id = st.query_params["session_id"]
        if "session_id" not in st.session_state:
            st.session_state["session_id"] = session_id
        return session_id

    # Check if already in session state
    if "session_id" in st.session_state:
        return st.session_state["session_id"]

    # Create new session ID
    session_id = str(uuid.uuid4())
    st.session_state["session_id"] = session_id
    st.query_params["session_id"] = session_id

    return session_id


def save_state_to_storage(state=None):
    """
    Save current state to database for persistence across browser refreshes.

    Args:
        state: Optional state dictionary to save. If None, uses col_state from session.

    Returns:
        bool: True if saved successfully, False otherwise
    """
    try:
        import os

        # Check if database is configured
        if not os.getenv("POSTGRESQL_HOST"):
            return False

        import psycopg2

        # Get state to save
        if state is None:
            state = st.session_state.get("col_state", {})

        # Build comprehensive state including jurisdiction info
        full_state = {
            "col_state": state,
            # Include jurisdiction-related session state for full recovery
            "precise_jurisdiction": st.session_state.get("precise_jurisdiction"),
            "precise_jurisdiction_detected": st.session_state.get("precise_jurisdiction_detected", False),
            "legal_system_type": st.session_state.get("legal_system_type"),
            "precise_jurisdiction_eval_score": st.session_state.get("precise_jurisdiction_eval_score"),
            "precise_jurisdiction_eval_submitted": st.session_state.get("precise_jurisdiction_eval_submitted", False),
            "precise_jurisdiction_confirmed": st.session_state.get("precise_jurisdiction_confirmed", False),
            "jurisdiction_manual_override": st.session_state.get("jurisdiction_manual_override"),
        }

        # Don't save if state is empty
        if not state and not any(full_state.values()):
            return False

        session_id = get_or_create_session_id()

        # Save to database with session ID
        with psycopg2.connect(
            host=os.getenv("POSTGRESQL_HOST"),
            port=int(os.getenv("POSTGRESQL_PORT", "5432")),
            dbname=os.getenv("POSTGRESQL_DATABASE"),
            user=os.getenv("POSTGRESQL_USERNAME"),
            password=os.getenv("POSTGRESQL_PASSWORD"),
        ) as conn:
            with conn.cursor() as cur:
                # Create table if not exists
                cur.execute(
                    """
                    CREATE TABLE IF NOT EXISTS session_state_storage (
                        session_id TEXT PRIMARY KEY,
                        state_data JSONB,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    );
                    """
                )

                # Upsert state data
                cur.execute(
                    """
                    INSERT INTO session_state_storage (session_id, state_data, updated_at)
                    VALUES (%s, %s, %s)
                    ON CONFLICT (session_id)
                    DO UPDATE SET state_data = EXCLUDED.state_data, updated_at = EXCLUDED.updated_at;
                    """,
                    (session_id, json.dumps(full_state), datetime.now())
                )
            conn.commit()

        return True
    except Exception:
        # Silently fail if database not available - persistence is optional
        return False


def restore_state_from_storage():
    """
    Restore state from database if available.

    Returns:
        dict: Restored state dictionary, or empty dict if not found
    """
    try:
        import os

        # Check if database is configured
        if not os.getenv("POSTGRESQL_HOST"):
            return {}

        import psycopg2

        # Get session ID from query params or session state
        session_id = None
        if "session_id" in st.query_params:
            session_id = st.query_params["session_id"]
        elif "session_id" in st.session_state:
            session_id = st.session_state["session_id"]

        if not session_id:
            return {}

        # Restore from database
        with psycopg2.connect(
            host=os.getenv("POSTGRESQL_HOST"),
            port=int(os.getenv("POSTGRESQL_PORT", "5432")),
            dbname=os.getenv("POSTGRESQL_DATABASE"),
            user=os.getenv("POSTGRESQL_USERNAME"),
            password=os.getenv("POSTGRESQL_PASSWORD"),
        ) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT state_data FROM session_state_storage
                    WHERE session_id = %s;
                    """,
                    (session_id,)
                )
                result = cur.fetchone()

                if result:
                    return result[0]  # PostgreSQL JSONB is automatically parsed to dict

        return {}
    except Exception:
        # Silently fail if database not available - persistence is optional
        return {}
