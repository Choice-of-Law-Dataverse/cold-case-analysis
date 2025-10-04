"""Tests for the agents integration with Streamlit."""

import pytest

from components.agents_integration import convert_agents_result_to_state
from openai_agents_poc.models import (
    CaseAbstract,
    ChoiceOfLawExtraction,
    ChoiceOfLawIssue,
    CompleteCaseAnalysis,
    CourtsPosition,
    DissentingOpinions,
    JurisdictionDetection,
    ObiterDicta,
    PILProvisions,
    RelevantFacts,
    ThemeClassification,
)


class TestAgentsIntegration:
    """Test the integration of OpenAI Agents with Streamlit."""

    def test_convert_agents_result_to_state_basic(self):
        """Test basic conversion of agents result to state format."""
        # Create a complete analysis result
        result = CompleteCaseAnalysis(
            case_citation="Test Case [2024]",
            jurisdiction_detection=JurisdictionDetection(
                legal_system_type="Civil-law jurisdiction",
                precise_jurisdiction="Switzerland",
                confidence="high",
                reasoning="Based on PILA references",
            ),
            col_extraction=ChoiceOfLawExtraction(
                col_sections=["Section 1", "Section 2"], confidence="high", reasoning="Clear CoL sections"
            ),
            theme_classification=ThemeClassification(
                themes=["Choice of Law", "International Contracts"], confidence="high", reasoning="Contract case"
            ),
            relevant_facts=RelevantFacts(facts="Test facts about the case"),
            pil_provisions=PILProvisions(provisions=["PILA Art. 116", "Rome I"]),
            col_issue=ChoiceOfLawIssue(issue="Which law applies to the contract?"),
            courts_position=CourtsPosition(position="Swiss law applies based on choice of law clause"),
            abstract=CaseAbstract(abstract="Test case summary"),
            metadata={"model": "gpt-4o-mini", "duration_seconds": 75.5},
        )

        # Convert to state
        state = convert_agents_result_to_state(result)

        # Verify basic fields
        assert state["case_citation"] == "Test Case [2024]"
        assert state["jurisdiction"] == "Civil-law jurisdiction"
        assert state["precise_jurisdiction"] == "Switzerland"

        # Verify CoL sections
        assert len(state["col_section"]) == 1
        assert "Section 1" in state["col_section"][0]
        assert "Section 2" in state["col_section"][0]
        assert state["col_done"] is True
        assert state["col_first_score_submitted"] is True

        # Verify themes
        assert len(state["classification"]) == 1
        assert "Choice of Law" in state["classification"][0]
        assert "International Contracts" in state["classification"][0]
        assert state["theme_done"] is True

        # Verify analysis results
        assert len(state["relevant_facts"]) == 1
        assert "Test facts" in state["relevant_facts"][0]
        assert len(state["pil_provisions"]) == 1
        assert "PILA Art. 116" in state["pil_provisions"][0]
        assert len(state["col_issue"]) == 1
        assert "Which law applies" in state["col_issue"][0]

        # Verify flags
        assert state["analysis_ready"] is True
        assert state["analysis_done"] is True
        assert state["relevant_facts_printed"] is True
        assert state["relevant_facts_score_submitted"] is True

    def test_convert_agents_result_with_common_law_fields(self):
        """Test conversion with Common Law specific fields."""
        result = CompleteCaseAnalysis(
            case_citation="Test Case [2024]",
            jurisdiction_detection=JurisdictionDetection(
                legal_system_type="Common-law jurisdiction",
                precise_jurisdiction="USA",
                confidence="high",
                reasoning="Based on case law references",
            ),
            col_extraction=ChoiceOfLawExtraction(
                col_sections=["Section 1"], confidence="high", reasoning="Clear"
            ),
            theme_classification=ThemeClassification(themes=["Choice of Law"], confidence="high", reasoning="CoL"),
            relevant_facts=RelevantFacts(facts="Facts"),
            pil_provisions=PILProvisions(provisions=["Restatement"]),
            col_issue=ChoiceOfLawIssue(issue="Issue"),
            courts_position=CourtsPosition(position="Position"),
            abstract=CaseAbstract(abstract="Abstract"),
            obiter_dicta=ObiterDicta(obiter_dicta="Some dicta"),
            dissenting_opinions=DissentingOpinions(dissenting_opinions="Judge X dissented"),
            metadata={},
        )

        state = convert_agents_result_to_state(result)

        # Verify Common Law fields
        assert len(state["obiter_dicta"]) == 1
        assert state["obiter_dicta"][0] == "Some dicta"
        assert state["obiter_dicta_printed"] is True
        assert state["obiter_dicta_score_submitted"] is True

        assert len(state["dissenting_opinions"]) == 1
        assert state["dissenting_opinions"][0] == "Judge X dissented"
        assert state["dissenting_opinions_printed"] is True
        assert state["dissenting_opinions_score_submitted"] is True

    def test_convert_agents_result_without_common_law_fields(self):
        """Test conversion without Common Law fields."""
        result = CompleteCaseAnalysis(
            case_citation="Test Case [2024]",
            jurisdiction_detection=JurisdictionDetection(
                legal_system_type="Civil-law jurisdiction",
                precise_jurisdiction="Switzerland",
                confidence="high",
                reasoning="PILA",
            ),
            col_extraction=ChoiceOfLawExtraction(col_sections=["Section 1"], confidence="high", reasoning="Clear"),
            theme_classification=ThemeClassification(themes=["Choice of Law"], confidence="high", reasoning="CoL"),
            relevant_facts=RelevantFacts(facts="Facts"),
            pil_provisions=PILProvisions(provisions=["PILA"]),
            col_issue=ChoiceOfLawIssue(issue="Issue"),
            courts_position=CourtsPosition(position="Position"),
            abstract=CaseAbstract(abstract="Abstract"),
            metadata={},
        )

        state = convert_agents_result_to_state(result)

        # Verify Common Law fields are empty lists
        assert state["obiter_dicta"] == []
        assert state["dissenting_opinions"] == []
        assert "obiter_dicta_printed" not in state
        assert "dissenting_opinions_printed" not in state

    def test_convert_preserves_metadata(self):
        """Test that metadata is properly preserved."""
        result = CompleteCaseAnalysis(
            case_citation="Test Case [2024]",
            jurisdiction_detection=JurisdictionDetection(
                legal_system_type="Civil-law jurisdiction",
                precise_jurisdiction="Switzerland",
                confidence="high",
                reasoning="PILA",
            ),
            col_extraction=ChoiceOfLawExtraction(col_sections=["Section 1"], confidence="high", reasoning="Clear"),
            theme_classification=ThemeClassification(themes=["Choice of Law"], confidence="high", reasoning="CoL"),
            relevant_facts=RelevantFacts(facts="Facts"),
            pil_provisions=PILProvisions(provisions=["PILA"]),
            col_issue=ChoiceOfLawIssue(issue="Issue"),
            courts_position=CourtsPosition(position="Position"),
            abstract=CaseAbstract(abstract="Abstract"),
            metadata={
                "model": "gpt-4o",
                "username": "test_user",
                "user_email": "test@example.com",
                "analysis_timestamp": "2024-10-04T12:00:00",
                "duration_seconds": 85.3,
            },
        )

        state = convert_agents_result_to_state(result)

        # Verify metadata
        assert state["model"] == "gpt-4o"
        assert state["username"] == "test_user"
        assert state["user_email"] == "test@example.com"
        assert state["analysis_timestamp"] == "2024-10-04T12:00:00"
        assert state["duration_seconds"] == 85.3
