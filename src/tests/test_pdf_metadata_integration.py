"""
Integration test to verify PDF metadata flows through to state and database save.
"""

import json
import sys
from pathlib import Path

# Add src directory to path for imports
src_path = Path(__file__).parent.parent
sys.path.insert(0, str(src_path))


def test_pdf_metadata_in_state():
    """Test that PDF metadata is included in the analysis state."""
    from utils.state_manager import create_initial_analysis_state

    # Mock streamlit session state
    class MockSessionState(dict):
        """Mock session state for testing."""

        pass

    class MockStreamlit:
        session_state: MockSessionState

        def __init__(self):
            self.session_state = MockSessionState()

    mock_st = MockStreamlit()

    # Set PDF metadata in mock session state
    mock_st.session_state["pdf_url"] = "https://test.blob.core.windows.net/container/test-uuid.pdf"
    mock_st.session_state["pdf_uuid"] = "test-uuid-12345"
    mock_st.session_state["pdf_filename"] = "test_case.pdf"

    # Mock streamlit module
    sys.modules["streamlit"] = mock_st  # type: ignore

    try:
        # Create initial state
        state = create_initial_analysis_state(
            case_citation="Test v. Case",
            username="testuser",
            full_text="Test court decision text",
            final_jurisdiction_data={
                "legal_system_type": "Civil-law jurisdiction",
                "jurisdiction_name": "Switzerland",
                "evaluation_score": 0.9,
            },
            user_email="test@example.com",
        )

        # Verify PDF metadata is in state
        assert "pdf_url" in state, "pdf_url should be in state"
        assert state["pdf_url"] == "https://test.blob.core.windows.net/container/test-uuid.pdf"

        assert "pdf_uuid" in state, "pdf_uuid should be in state"
        assert state["pdf_uuid"] == "test-uuid-12345"

        assert "pdf_filename" in state, "pdf_filename should be in state"
        assert state["pdf_filename"] == "test_case.pdf"

        # Verify the state can be serialized to JSON (as it would be for database save)
        serialized = json.dumps(state)
        deserialized = json.loads(serialized)

        assert deserialized["pdf_url"] == "https://test.blob.core.windows.net/container/test-uuid.pdf"
        assert deserialized["pdf_uuid"] == "test-uuid-12345"
        assert deserialized["pdf_filename"] == "test_case.pdf"

        print("✓ PDF metadata correctly flows through to state and can be serialized")

    finally:
        # Clean up mock
        if "streamlit" in sys.modules:
            del sys.modules["streamlit"]


def test_state_without_pdf_metadata():
    """Test that state creation works even without PDF metadata."""
    from utils.state_manager import create_initial_analysis_state

    # Mock streamlit session state without PDF metadata
    class MockSessionState(dict):
        """Mock session state for testing."""

        pass

    class MockStreamlit:
        session_state: MockSessionState

        def __init__(self):
            self.session_state = MockSessionState()

    mock_st = MockStreamlit()

    # Mock streamlit module
    sys.modules["streamlit"] = mock_st  # type: ignore

    try:
        # Create initial state without PDF metadata
        state = create_initial_analysis_state(
            case_citation="Test v. Case",
            username="testuser",
            full_text="Test court decision text",
            final_jurisdiction_data={
                "legal_system_type": "Civil-law jurisdiction",
                "jurisdiction_name": "Switzerland",
                "evaluation_score": 0.9,
            },
        )

        # Verify state is created without PDF metadata
        assert "pdf_url" not in state, "pdf_url should not be in state when not uploaded"
        assert "pdf_uuid" not in state, "pdf_uuid should not be in state when not uploaded"
        assert "pdf_filename" not in state, "pdf_filename should not be in state when not uploaded"

        # Verify the state can still be serialized
        serialized = json.dumps(state)
        deserialized = json.loads(serialized)

        assert deserialized["case_citation"] == "Test v. Case"
        assert deserialized["username"] == "testuser"

        print("✓ State creation works correctly without PDF metadata")

    finally:
        # Clean up mock
        if "streamlit" in sys.modules:
            del sys.modules["streamlit"]


if __name__ == "__main__":
    test_pdf_metadata_in_state()
    test_state_without_pdf_metadata()
    print("\n✓ All integration tests passed!")
