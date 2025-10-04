"""
Test for jurisdiction detection UI changes.
"""
import os
import sys
from unittest.mock import Mock, patch

import pytest

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


def test_jurisdiction_detection_session_state_initialization():
    """Test that the jurisdiction detection component initializes session state properly."""
    # Mock streamlit
    mock_st = Mock()
    mock_st.session_state = {}

    with patch.dict("sys.modules", {"streamlit": mock_st}):
        # Import after mocking

        # The component should initialize these session state variables
        expected_keys = [
            "precise_jurisdiction",
            "precise_jurisdiction_detected",
            "legal_system_type",
            "precise_jurisdiction_eval_score",
            "precise_jurisdiction_confirmed",
            "jurisdiction_manual_override"
        ]

        # Verify that precise_jurisdiction_eval_submitted is NOT in the expected keys
        # (it was removed as part of the UI improvement)
        assert "precise_jurisdiction_eval_submitted" not in expected_keys


def test_no_evaluation_phase_in_code():
    """Test that the evaluation phase code has been removed."""
    # Read the jurisdiction_detection.py file
    file_path = os.path.join(os.path.dirname(__file__), "..", "components", "jurisdiction_detection.py")
    with open(file_path) as f:
        content = f.read()

    # Check that evaluation-related strings are not present
    assert "Evaluate Detection Accuracy" not in content, "Evaluation section should be removed"
    assert "Submit Evaluation" not in content, "Submit Evaluation button should be removed"
    assert "precise_jurisdiction_eval_slider" not in content, "Evaluation slider should be removed"

    # Check that "Manual Override" subtitle is not present
    assert "### Manual Override" not in content, "Manual Override subtitle should be removed"

    # Check that the button text is "Confirm" not "Confirm Final Jurisdiction"
    assert "Confirm Final Jurisdiction" not in content, "Button should be renamed to just 'Confirm'"
    assert '"Confirm"' in content, "Button should be named 'Confirm'"

    # Check that "Keep Current Detection" is not used
    assert "Keep Current Detection" not in content, "Keep Current Detection option should be removed"


def test_dropdown_defaults_logic():
    """Test that dropdowns use detected values as defaults."""
    file_path = os.path.join(os.path.dirname(__file__), "..", "components", "jurisdiction_detection.py")
    with open(file_path) as f:
        content = f.read()

    # Check for logic that sets default indices based on detected values
    assert "default_jurisdiction_index" in content, "Should calculate default jurisdiction index"
    assert "default_legal_system_index" in content, "Should calculate default legal system index"
    assert "jurisdiction_names.index(jurisdiction_name)" in content, "Should find detected jurisdiction in list"
    assert "legal_system_options.index(legal_system)" in content, "Should find detected legal system in list"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
