# tests/test_browser_storage.py
"""
Tests for browser localStorage integration.
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
    """Mock the LocalStorage class."""
    with patch("utils.browser_storage._get_local_storage") as mock_getter:
        instance = MagicMock()
        mock_getter.return_value = instance
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


def test_save_analysis_state(mock_local_storage):
    """Test saving analysis state."""
    from utils.browser_storage import save_analysis_state

    analysis_state = {
        "col_state": {"case_citation": "Test Case"},
        "full_text_input": "Some text",
        "jurisdiction_detected": True,
    }

    save_analysis_state(analysis_state)

    mock_local_storage.setItem.assert_called_once()
    args = mock_local_storage.setItem.call_args[0]
    assert args[0] == "cold_analysis_state"
    assert json.loads(args[1]) == analysis_state


def test_load_auth_state(mock_local_storage):
    """Test loading authentication state."""
    from utils.browser_storage import load_auth_state

    auth_state = {"logged_in": True, "user": "testuser"}
    mock_local_storage.getItem.return_value = json.dumps(auth_state)

    result = load_auth_state()

    mock_local_storage.getItem.assert_called_once_with("cold_auth_state")
    assert result == auth_state


def test_load_analysis_state(mock_local_storage):
    """Test loading analysis state."""
    from utils.browser_storage import load_analysis_state

    analysis_state = {"col_state": {}, "case_citation": "Test"}
    mock_local_storage.getItem.return_value = json.dumps(analysis_state)

    result = load_analysis_state()

    mock_local_storage.getItem.assert_called_once_with("cold_analysis_state")
    assert result == analysis_state


def test_load_nonexistent_state(mock_local_storage):
    """Test loading state that doesn't exist."""
    from utils.browser_storage import load_auth_state

    mock_local_storage.getItem.return_value = None

    result = load_auth_state()

    assert result is None


def test_clear_auth_state(mock_local_storage):
    """Test clearing authentication state."""
    from utils.browser_storage import clear_auth_state

    clear_auth_state()

    mock_local_storage.deleteItem.assert_called_once_with("cold_auth_state")


def test_clear_analysis_state(mock_local_storage):
    """Test clearing analysis state."""
    from utils.browser_storage import clear_analysis_state

    clear_analysis_state()

    mock_local_storage.deleteItem.assert_called_once_with("cold_analysis_state")


def test_clear_all_storage(mock_local_storage):
    """Test clearing all storage."""
    from utils.browser_storage import clear_all_storage

    clear_all_storage()

    assert mock_local_storage.deleteItem.call_count == 2
    calls = [call[0][0] for call in mock_local_storage.deleteItem.call_args_list]
    assert "cold_auth_state" in calls
    assert "cold_analysis_state" in calls


def test_save_with_complex_data(mock_local_storage):
    """Test saving complex nested data structures."""
    from utils.browser_storage import save_analysis_state

    analysis_state = {
        "col_state": {
            "case_citation": "BGE 132 III 285",
            "col_section": ["First extraction", "Second extraction"],
            "themes_data": [{"theme": "Contract Law", "score": 0.95}],
        },
        "full_text_input": "Long text...",
        "jurisdiction_confirmed": True,
    }

    save_analysis_state(analysis_state)

    mock_local_storage.setItem.assert_called_once()
    args = mock_local_storage.setItem.call_args[0]
    assert json.loads(args[1])["col_state"]["col_section"] == ["First extraction", "Second extraction"]
