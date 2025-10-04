"""
Tests for state persistence functionality.
"""
import uuid
from unittest.mock import MagicMock, patch

import pytest


def test_get_or_create_session_id_new():
    """Test creating a new session ID when none exists."""
    from utils.state_manager import get_or_create_session_id

    with patch("streamlit.query_params", {}), patch("streamlit.session_state", {}):
        session_id = get_or_create_session_id()
        assert session_id is not None
        assert isinstance(session_id, str)
        # Should be a valid UUID
        uuid.UUID(session_id)


def test_get_or_create_session_id_from_query_params():
    """Test retrieving session ID from query params."""
    from utils.state_manager import get_or_create_session_id

    test_session_id = str(uuid.uuid4())
    mock_query_params = {"session_id": test_session_id}
    mock_session_state = {}

    with patch("streamlit.query_params", mock_query_params), patch(
        "streamlit.session_state", mock_session_state
    ):
        session_id = get_or_create_session_id()
        assert session_id == test_session_id


def test_get_or_create_session_id_from_session_state():
    """Test retrieving session ID from session state."""
    from utils.state_manager import get_or_create_session_id

    test_session_id = str(uuid.uuid4())
    mock_query_params = {}
    mock_session_state = {"session_id": test_session_id}

    with patch("streamlit.query_params", mock_query_params), patch(
        "streamlit.session_state", mock_session_state
    ):
        session_id = get_or_create_session_id()
        assert session_id == test_session_id


def test_save_state_to_storage_no_database():
    """Test save_state_to_storage when database not configured."""
    from utils.state_manager import save_state_to_storage

    test_state = {"case_citation": "Test Case"}

    with patch("os.getenv", return_value=None):
        result = save_state_to_storage(test_state)
        assert result is False


def test_save_state_to_storage_success():
    """Test successful state save to database."""
    from utils.state_manager import save_state_to_storage

    test_state = {"case_citation": "Test Case", "full_text": "Test content"}
    test_session_id = str(uuid.uuid4())

    # Mock database connection and cursor
    mock_cursor = MagicMock()
    mock_conn = MagicMock()
    mock_conn.__enter__ = MagicMock(return_value=mock_conn)
    mock_conn.__exit__ = MagicMock(return_value=False)
    mock_conn.cursor.return_value.__enter__ = MagicMock(return_value=mock_cursor)
    mock_conn.cursor.return_value.__exit__ = MagicMock(return_value=False)

    with patch("os.getenv") as mock_getenv, patch(
        "psycopg2.connect", return_value=mock_conn
    ), patch("streamlit.query_params", {"session_id": test_session_id}), patch(
        "streamlit.session_state", {"session_id": test_session_id}
    ):
        # Configure getenv to return database config
        mock_getenv.side_effect = lambda key, default=None: {
            "POSTGRESQL_HOST": "localhost",
            "POSTGRESQL_PORT": "5432",
            "POSTGRESQL_DATABASE": "test_db",
            "POSTGRESQL_USERNAME": "test_user",
            "POSTGRESQL_PASSWORD": "test_pass",
        }.get(key, default)

        result = save_state_to_storage(test_state)
        assert result is True

        # Verify table creation was called
        assert mock_cursor.execute.call_count >= 2


def test_restore_state_from_storage_no_database():
    """Test restore_state_from_storage when database not configured."""
    from utils.state_manager import restore_state_from_storage

    with patch("os.getenv", return_value=None):
        result = restore_state_from_storage()
        assert result == {}


def test_restore_state_from_storage_no_session_id():
    """Test restore_state_from_storage when no session ID available."""
    from utils.state_manager import restore_state_from_storage

    with patch("os.getenv") as mock_getenv, patch("streamlit.query_params", {}), patch(
        "streamlit.session_state", {}
    ):
        mock_getenv.side_effect = lambda key, default=None: {
            "POSTGRESQL_HOST": "localhost",
        }.get(key, default)

        result = restore_state_from_storage()
        assert result == {}


def test_restore_state_from_storage_success():
    """Test successful state restoration from database."""
    from utils.state_manager import restore_state_from_storage

    test_session_id = str(uuid.uuid4())
    test_state = {
        "col_state": {"case_citation": "Test Case"},
        "precise_jurisdiction": "Switzerland",
    }

    # Mock database connection and cursor
    mock_cursor = MagicMock()
    mock_cursor.fetchone.return_value = (test_state,)
    mock_conn = MagicMock()
    mock_conn.__enter__ = MagicMock(return_value=mock_conn)
    mock_conn.__exit__ = MagicMock(return_value=False)
    mock_conn.cursor.return_value.__enter__ = MagicMock(return_value=mock_cursor)
    mock_conn.cursor.return_value.__exit__ = MagicMock(return_value=False)

    with patch("os.getenv") as mock_getenv, patch(
        "psycopg2.connect", return_value=mock_conn
    ), patch("streamlit.query_params", {"session_id": test_session_id}), patch(
        "streamlit.session_state", {}
    ):
        # Configure getenv to return database config
        mock_getenv.side_effect = lambda key, default=None: {
            "POSTGRESQL_HOST": "localhost",
            "POSTGRESQL_PORT": "5432",
            "POSTGRESQL_DATABASE": "test_db",
            "POSTGRESQL_USERNAME": "test_user",
            "POSTGRESQL_PASSWORD": "test_pass",
        }.get(key, default)

        result = restore_state_from_storage()
        assert result == test_state
        assert result["col_state"]["case_citation"] == "Test Case"
        assert result["precise_jurisdiction"] == "Switzerland"


def test_initialize_col_state_new():
    """Test initializing col_state when it doesn't exist."""
    from utils.state_manager import initialize_col_state

    mock_session_state = {}
    test_session_id = str(uuid.uuid4())

    with patch("streamlit.session_state", mock_session_state), patch(
        "streamlit.query_params", {}
    ) as mock_query_params, patch(
        "utils.state_manager.restore_state_from_storage", return_value={}
    ):
        initialize_col_state()
        assert "col_state" in mock_session_state
        assert mock_session_state["col_state"] == {}
        # Session ID should be generated
        assert "session_id" in mock_session_state


def test_initialize_col_state_restore():
    """Test initializing col_state with restored state."""
    from utils.state_manager import initialize_col_state

    restored_state = {
        "col_state": {"case_citation": "Test Case"},
        "precise_jurisdiction": "Switzerland",
        "precise_jurisdiction_detected": True,
    }
    mock_session_state = {}
    test_session_id = str(uuid.uuid4())

    with patch("streamlit.session_state", mock_session_state), patch(
        "streamlit.query_params", {"session_id": test_session_id}
    ), patch(
        "utils.state_manager.restore_state_from_storage", return_value=restored_state
    ):
        initialize_col_state()
        assert "col_state" in mock_session_state
        assert mock_session_state["col_state"]["case_citation"] == "Test Case"
        assert mock_session_state["precise_jurisdiction"] == "Switzerland"
        assert mock_session_state["precise_jurisdiction_detected"] is True


def test_update_col_state():
    """Test updating col_state with auto-save."""
    from utils.state_manager import update_col_state

    mock_session_state = {"col_state": {"case_citation": "Original"}}

    with patch("streamlit.session_state", mock_session_state), patch(
        "utils.state_manager.save_state_to_storage"
    ) as mock_save:
        update_col_state({"full_text": "New content"})
        assert mock_session_state["col_state"]["case_citation"] == "Original"
        assert mock_session_state["col_state"]["full_text"] == "New content"
        # Verify save was called
        mock_save.assert_called_once()
