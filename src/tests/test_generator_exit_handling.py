#!/usr/bin/env python3
"""
Test that GeneratorExit exception is properly handled in analyze_case_workflow.
"""

import logging
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))


def test_generator_exit_is_handled():
    """Test that GeneratorExit exception is caught and logged properly."""
    from tools.case_analyzer import analyze_case_workflow

    # Mock all the extraction functions to return simple outputs
    with patch("tools.case_analyzer.extract_col_section") as mock_col, \
         patch("tools.case_analyzer.extract_case_citation") as mock_citation, \
         patch("tools.case_analyzer.theme_classification_node") as mock_theme:

        # Create simple mock outputs
        from models.analysis_models import ColSectionOutput
        from models.classification_models import ThemeClassificationOutput

        mock_col_output = ColSectionOutput(
            col_sections=["Test section"],
            confidence="high",
            reasoning="Test reasoning"
        )
        mock_col.return_value = mock_col_output

        mock_citation_output = MagicMock()
        mock_citation.return_value = mock_citation_output

        mock_theme_output = ThemeClassificationOutput(
            themes=["Party autonomy"],
            confidence="high",
            reasoning="Test reasoning"
        )
        mock_theme.return_value = mock_theme_output

        # Create generator
        gen = analyze_case_workflow(
            text="Test text",
            legal_system="Civil-law jurisdiction",
            jurisdiction="Switzerland",
            model="gpt-4"
        )

        # Consume first result
        result = next(gen)
        assert result is not None, "Should get first result"
        print(f"✓ Got first result: {type(result).__name__}")

        # Close the generator early (simulating Streamlit rerun or navigation)
        gen.close()
        print("✓ Generator closed successfully without error")

        # Try to get next result - should raise StopIteration
        try:
            next(gen)
            raise AssertionError("Generator should have stopped after close()")
        except StopIteration:
            print("✓ Generator properly stopped after close()")


def test_generator_completes_normally():
    """Test that the generator can complete normally without errors."""
    from tools.case_analyzer import analyze_case_workflow

    # Mock all the extraction functions
    with patch("tools.case_analyzer.extract_col_section") as mock_col, \
         patch("tools.case_analyzer.extract_case_citation") as mock_citation, \
         patch("tools.case_analyzer.theme_classification_node") as mock_theme, \
         patch("tools.case_analyzer.extract_relevant_facts") as mock_facts, \
         patch("tools.case_analyzer.extract_pil_provisions") as mock_pil, \
         patch("tools.case_analyzer.extract_col_issue") as mock_issue, \
         patch("tools.case_analyzer.extract_courts_position") as mock_position, \
         patch("tools.case_analyzer.extract_abstract") as mock_abstract:

        # Create mock outputs
        from models.analysis_models import (
            AbstractOutput,
            ColIssueOutput,
            ColSectionOutput,
            CourtsPositionOutput,
            PILProvisionsOutput,
            RelevantFactsOutput,
        )
        from models.classification_models import ThemeClassificationOutput

        mock_col.return_value = ColSectionOutput(
            col_sections=["Test section"],
            confidence="high",
            reasoning="Test"
        )
        mock_citation.return_value = MagicMock()
        mock_theme.return_value = ThemeClassificationOutput(
            themes=["Party autonomy"],
            confidence="high",
            reasoning="Test"
        )
        mock_facts.return_value = RelevantFactsOutput(
            relevant_facts="Test facts",
            confidence="high",
            reasoning="Test"
        )
        mock_pil.return_value = PILProvisionsOutput(
            pil_provisions=["Test provision"],
            confidence="high",
            reasoning="Test"
        )
        mock_issue.return_value = ColIssueOutput(
            col_issue="Test issue",
            confidence="high",
            reasoning="Test"
        )
        mock_position.return_value = CourtsPositionOutput(
            courts_position="Test position",
            confidence="high",
            reasoning="Test"
        )
        mock_abstract.return_value = AbstractOutput(
            abstract="Test abstract",
            confidence="high",
            reasoning="Test"
        )

        # Create generator and consume all results
        gen = analyze_case_workflow(
            text="Test text",
            legal_system="Civil-law jurisdiction",
            jurisdiction="Switzerland",
            model="gpt-4"
        )

        results = []
        for result in gen:
            results.append(result)

        assert len(results) > 0, "Should have at least one result"
        print(f"✓ Generator completed normally with {len(results)} results")


if __name__ == "__main__":
    print("Testing GeneratorExit handling in analyze_case_workflow...\n")

    # Suppress logfire warnings for testing
    logging.getLogger("logfire").setLevel(logging.CRITICAL)

    try:
        test_generator_exit_is_handled()
        test_generator_completes_normally()
        print("\n✅ All tests passed!")
        sys.exit(0)
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
