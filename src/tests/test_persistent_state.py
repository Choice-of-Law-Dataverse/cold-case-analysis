# tests/test_persistent_state.py
"""
Tests for persistent state management.
"""
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

# Add src directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.persistent_state import (
    clear_analysis_state,
    delete_persistent_state,
    generate_session_id,
    get_session_file_path,
    load_persistent_state,
    save_persistent_state,
)


@pytest.fixture
def temp_session_dir(tmp_path):
    """Create a temporary session directory for testing."""
    with patch("utils.persistent_state.SESSION_DIR", tmp_path):
        yield tmp_path


def test_generate_session_id():
    """Test session ID generation."""
    session_id1 = generate_session_id()
    session_id2 = generate_session_id()

    assert session_id1 != session_id2
    assert len(session_id1) == 36  # UUID4 format
    assert "-" in session_id1


def test_save_and_load_persistent_state(temp_session_dir):
    """Test saving and loading persistent state."""
    session_id = "test-session-123"
    auth_state = {"logged_in": True, "user": "testuser"}
    analysis_state = {"col_state": {"case_citation": "Test Case"}}

    success = save_persistent_state(session_id, auth_state, analysis_state)
    assert success

    session_file = temp_session_dir / f"{session_id}.json"
    assert session_file.exists()

    loaded_data = load_persistent_state(session_id)
    assert loaded_data is not None
    assert loaded_data["session_id"] == session_id
    assert loaded_data["auth_state"] == auth_state
    assert loaded_data["analysis_state"] == analysis_state
    assert "timestamp" in loaded_data


def test_load_nonexistent_state(temp_session_dir):
    """Test loading state that doesn't exist."""
    result = load_persistent_state("nonexistent-session")
    assert result is None


def test_delete_persistent_state(temp_session_dir):
    """Test deleting persistent state."""
    session_id = "test-session-delete"
    auth_state = {"logged_in": True}
    analysis_state = {"col_state": {}}

    save_persistent_state(session_id, auth_state, analysis_state)

    session_file = temp_session_dir / f"{session_id}.json"
    assert session_file.exists()

    success = delete_persistent_state(session_id)
    assert success
    assert not session_file.exists()

    success = delete_persistent_state(session_id)
    assert not success


def test_clear_analysis_state(temp_session_dir):
    """Test clearing only analysis state while keeping auth."""
    session_id = "test-session-clear"
    auth_state = {"logged_in": True, "user": "testuser"}
    analysis_state = {"col_state": {"case_citation": "Test"}, "full_text": "Some text"}

    save_persistent_state(session_id, auth_state, analysis_state)

    success = clear_analysis_state(session_id)
    assert success

    loaded_data = load_persistent_state(session_id)
    assert loaded_data is not None
    assert loaded_data["auth_state"] == auth_state
    assert loaded_data["analysis_state"] == {}


def test_state_persistence_with_complex_data(temp_session_dir):
    """Test persistence with complex nested data structures."""
    session_id = "test-session-complex"
    auth_state = {
        "logged_in": True,
        "user": "admin",
        "llm_model_select": "gpt-5-nano"
    }
    analysis_state = {
        "col_state": {
            "case_citation": "BGE 132 III 285",
            "jurisdiction": "Civil-law jurisdiction",
            "col_section": ["First extraction", "Second extraction"],
            "themes_data": [
                {"theme": "Contract Law", "score": 0.95},
                {"theme": "Property Law", "score": 0.82}
            ]
        },
        "full_text_input": "This is a long court decision text...",
        "jurisdiction_confirmed": True
    }

    success = save_persistent_state(session_id, auth_state, analysis_state)
    assert success

    loaded_data = load_persistent_state(session_id)
    assert loaded_data is not None
    assert loaded_data["auth_state"] == auth_state
    assert loaded_data["analysis_state"]["col_state"]["col_section"] == ["First extraction", "Second extraction"]
    assert len(loaded_data["analysis_state"]["col_state"]["themes_data"]) == 2


def test_session_file_path(temp_session_dir):
    """Test session file path generation."""
    session_id = "test-session-path"
    expected_path = temp_session_dir / f"{session_id}.json"

    with patch("utils.persistent_state.SESSION_DIR", temp_session_dir):
        actual_path = get_session_file_path(session_id)
        assert actual_path == expected_path


def test_save_state_creates_directory(tmp_path):
    """Test that save_persistent_state creates the directory if it doesn't exist."""
    new_dir = tmp_path / "new_session_dir"
    assert not new_dir.exists()

    with patch("utils.persistent_state.SESSION_DIR", new_dir):
        session_id = "test-session-mkdir"
        auth_state = {"logged_in": False}
        analysis_state = {}

        success = save_persistent_state(session_id, auth_state, analysis_state)
        assert success
        assert new_dir.exists()
        assert (new_dir / f"{session_id}.json").exists()
