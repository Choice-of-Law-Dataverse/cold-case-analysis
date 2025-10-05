# tests/test_browser_storage.py
"""
Tests for browser localStorage integration with multi-analysis support.
Note: These tests mock the streamlit-local-storage component since we can't
actually access browser localStorage in a test environment.
"""
import json
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# Add src directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))


@pytest.fixture
def mock_local_storage():
    """Mock the LocalStorage class and session state."""
    instance = MagicMock()

    # Create a mock session state class that behaves like a dict with attribute access
    class MockSessionState(dict):
        def __getattr__(self, key):
            try:
                return self[key]
            except KeyError as e:
                raise AttributeError(key) from e

        def __setattr__(self, key, value):
            self[key] = value

        def __contains__(self, key):
            return dict.__contains__(self, key)

    mock_session_state = MockSessionState()
    mock_session_state["_local_storage_instance"] = instance

    with patch("streamlit_local_storage.LocalStorage", return_value=instance):
        with patch("streamlit.session_state", mock_session_state, create=True):
            with patch("utils.browser_storage.st.session_state", mock_session_state):
                yield instance


def test_save_auth_state(mock_local_storage):
    """Test saving authentication state."""
    from utils.browser_storage import save_auth_state

    auth_state = {"logged_in": True, "user": "testuser", "llm_model_select": "gpt-5-nano"}

    save_auth_state(auth_state)

    mock_local_storage.setItem.assert_called_once()
    args = mock_local_storage.setItem.call_args[0]
    assert args[0] == "cold_auth_state"
    assert json.loads(args[1]) == auth_state


def test_load_auth_state(mock_local_storage):
    """Test loading authentication state."""
    from utils.browser_storage import load_auth_state

    auth_state = {"logged_in": True, "user": "testuser"}
    mock_local_storage.getItem.return_value = json.dumps(auth_state)

    result = load_auth_state()

    mock_local_storage.getItem.assert_called_once_with("cold_auth_state")
    assert result == auth_state


def test_create_new_analysis(mock_local_storage):
    """Test creating a new analysis."""
    from utils.browser_storage import create_new_analysis

    mock_local_storage.getItem.return_value = None  # No existing analyses

    analysis_id = create_new_analysis("Test Case")

    # Should have 8 character ID
    assert len(analysis_id) == 8

    # Should save analyses list and analysis data
    assert mock_local_storage.setItem.call_count >= 3


def test_list_analyses(mock_local_storage):
    """Test listing analyses."""
    from utils.browser_storage import list_analyses

    analyses = [
        {"id": "abc12345", "created_at": 1234567890, "case_citation": "Test 1"},
        {"id": "def67890", "created_at": 1234567900, "case_citation": "Test 2"},
    ]
    mock_local_storage.getItem.return_value = json.dumps(analyses)

    result = list_analyses()

    # Should be sorted by created_at descending
    assert len(result) == 2
    assert result[0]["created_at"] >= result[1]["created_at"]


def test_save_analysis_state(mock_local_storage):
    """Test saving analysis state."""
    from utils.browser_storage import save_analysis_state

    analysis_state = {
        "col_state": {"case_citation": "Test Case"},
        "full_text_input": "Some text",
        "jurisdiction_detected": True,
    }

    mock_local_storage.getItem.return_value = None  # No current analysis
    save_analysis_state(analysis_state)

    # Should create new analysis if none exists
    assert mock_local_storage.setItem.call_count >= 1


def test_load_analysis_state(mock_local_storage):
    """Test loading analysis state."""
    from utils.browser_storage import load_analysis_state

    analysis_state = {"col_state": {}, "case_citation": "Test"}
    mock_local_storage.getItem.return_value = json.dumps(analysis_state)

    result = load_analysis_state("abc12345")

    # Should include defaults for missing keys
    assert result is not None
    assert result["col_state"] == {}
    assert result["case_citation"] == "Test"
    assert result["full_text_input"] == ""
    assert result["col_extraction_started"] is False
    assert result["jurisdiction_detected"] is False


def test_mark_analysis_submitted(mock_local_storage):
    """Test marking analysis as submitted."""
    from utils.browser_storage import mark_analysis_submitted

    analyses = [
        {"id": "abc12345", "created_at": 1234567890, "submitted_at": None},
    ]
    mock_local_storage.getItem.return_value = json.dumps(analyses)

    mark_analysis_submitted("abc12345")

    # Should update analyses list
    assert mock_local_storage.setItem.call_count >= 1
    call_args = mock_local_storage.setItem.call_args[0]
    updated_analyses = json.loads(call_args[1])
    assert updated_analyses[0]["submitted_at"] is not None


def test_delete_analysis(mock_local_storage):
    """Test deleting an analysis."""
    from utils.browser_storage import delete_analysis

    analyses = [
        {"id": "abc12345", "created_at": 1234567890},
        {"id": "def67890", "created_at": 1234567900},
    ]
    mock_local_storage.getItem.return_value = json.dumps(analyses)

    delete_analysis("abc12345")

    # Should update analyses list and delete analysis data
    assert mock_local_storage.setItem.call_count >= 1
    assert mock_local_storage.deleteItem.call_count >= 1


def test_get_current_analysis_id(mock_local_storage):
    """Test getting current analysis ID."""
    from utils.browser_storage import get_current_analysis_id

    mock_local_storage.getItem.return_value = "abc12345"

    result = get_current_analysis_id()

    assert result == "abc12345"
    mock_local_storage.getItem.assert_called_once_with("cold_current_analysis_id")


def test_clear_all_storage(mock_local_storage):
    """Test clearing all storage."""
    from utils.browser_storage import clear_all_storage

    analyses = [
        {"id": "abc12345", "created_at": 1234567890},
        {"id": "def67890", "created_at": 1234567900},
    ]
    mock_local_storage.getItem.return_value = json.dumps(analyses)

    clear_all_storage()

    # Should delete auth, analyses list, current ID, and all analysis data
    assert mock_local_storage.deleteItem.call_count >= 4
