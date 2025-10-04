"""Tests for the OpenAI Agents PoC implementation."""

import pytest

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
from openai_agents_poc.orchestrator import CaseAnalysisOrchestrator
from openai_agents_poc.sub_agents import (
    create_abstract_agent,
    create_col_extraction_agent,
    create_col_issue_agent,
    create_courts_position_agent,
    create_dissenting_opinions_agent,
    create_jurisdiction_agent,
    create_obiter_dicta_agent,
    create_pil_provisions_agent,
    create_relevant_facts_agent,
    create_theme_classification_agent,
)


class TestPydanticModels:
    """Test Pydantic model definitions."""

    def test_jurisdiction_detection_model(self):
        """Test JurisdictionDetection model."""
        data = {
            "legal_system_type": "Civil-law jurisdiction",
            "precise_jurisdiction": "Switzerland",
            "confidence": "high",
            "reasoning": "Based on Swiss court structure and PILA references",
        }
        model = JurisdictionDetection(**data)
        assert model.legal_system_type == "Civil-law jurisdiction"
        assert model.precise_jurisdiction == "Switzerland"
        assert model.confidence == "high"

    def test_col_extraction_model(self):
        """Test ChoiceOfLawExtraction model."""
        data = {
            "col_sections": ["Section 1", "Section 2"],
            "confidence": "high",
            "reasoning": "Clear CoL discussion in paragraphs 5-7",
        }
        model = ChoiceOfLawExtraction(**data)
        assert len(model.col_sections) == 2
        assert model.confidence == "high"

    def test_theme_classification_model(self):
        """Test ThemeClassification model."""
        data = {
            "themes": ["Choice of Law", "International Contracts"],
            "confidence": "high",
            "reasoning": "Case involves contract and CoL analysis",
        }
        model = ThemeClassification(**data)
        assert len(model.themes) == 2
        assert "Choice of Law" in model.themes

    def test_complete_case_analysis_model(self):
        """Test CompleteCaseAnalysis model."""
        data = {
            "case_citation": "Test Case 123",
            "jurisdiction_detection": {
                "legal_system_type": "Civil-law jurisdiction",
                "precise_jurisdiction": "Switzerland",
                "confidence": "high",
                "reasoning": "Test",
            },
            "col_extraction": {"col_sections": ["Section 1"], "confidence": "high", "reasoning": "Test"},
            "theme_classification": {"themes": ["Choice of Law"], "confidence": "high", "reasoning": "Test"},
            "relevant_facts": {"facts": "Test facts"},
            "pil_provisions": {"provisions": ["PILA Art. 116"]},
            "col_issue": {"issue": "Which law applies?"},
            "courts_position": {"position": "Swiss law applies"},
            "abstract": {"abstract": "Test abstract"},
        }
        model = CompleteCaseAnalysis(**data)
        assert model.case_citation == "Test Case 123"
        assert model.jurisdiction_detection.legal_system_type == "Civil-law jurisdiction"
        assert len(model.theme_classification.themes) == 1

    def test_complete_case_analysis_with_common_law_fields(self):
        """Test CompleteCaseAnalysis with Common Law specific fields."""
        data = {
            "case_citation": "Test Case 456",
            "jurisdiction_detection": {
                "legal_system_type": "Common-law jurisdiction",
                "precise_jurisdiction": "USA",
                "confidence": "high",
                "reasoning": "Test",
            },
            "col_extraction": {"col_sections": ["Section 1"], "confidence": "high", "reasoning": "Test"},
            "theme_classification": {"themes": ["Choice of Law"], "confidence": "high", "reasoning": "Test"},
            "relevant_facts": {"facts": "Test facts"},
            "pil_provisions": {"provisions": ["Restatement (Second) Conflict of Laws"]},
            "col_issue": {"issue": "Which law applies?"},
            "courts_position": {"position": "State law applies"},
            "abstract": {"abstract": "Test abstract"},
            "obiter_dicta": {"obiter_dicta": "Some dicta"},
            "dissenting_opinions": {"dissenting_opinions": "Judge X dissented"},
        }
        model = CompleteCaseAnalysis(**data)
        assert model.obiter_dicta is not None
        assert model.dissenting_opinions is not None
        assert model.obiter_dicta.obiter_dicta == "Some dicta"


class TestSubAgents:
    """Test sub-agent creation."""

    def test_create_jurisdiction_agent(self):
        """Test jurisdiction agent creation."""
        agent = create_jurisdiction_agent()
        assert agent.name == "JurisdictionDetector"
        assert agent.output_type is not None
        assert "legal systems" in agent.instructions.lower()

    def test_create_col_extraction_agent(self):
        """Test CoL extraction agent creation."""
        agent = create_col_extraction_agent()
        assert agent.name == "ChoiceOfLawExtractor"
        assert "choice of law" in agent.instructions.lower()

    def test_create_theme_classification_agent(self):
        """Test theme classification agent creation."""
        themes = ["Theme 1", "Theme 2", "Theme 3"]
        agent = create_theme_classification_agent(themes)
        assert agent.name == "ThemeClassifier"
        assert "Theme 1" in agent.instructions
        assert "Theme 2" in agent.instructions

    def test_create_relevant_facts_agent(self):
        """Test relevant facts agent creation."""
        agent = create_relevant_facts_agent()
        assert agent.name == "RelevantFactsExtractor"
        assert "facts" in agent.instructions.lower()

    def test_create_pil_provisions_agent(self):
        """Test PIL provisions agent creation."""
        agent = create_pil_provisions_agent()
        assert agent.name == "PILProvisionsExtractor"
        assert "provisions" in agent.instructions.lower()

    def test_create_col_issue_agent(self):
        """Test CoL issue agent creation."""
        agent = create_col_issue_agent()
        assert agent.name == "ChoiceOfLawIssueIdentifier"
        assert "issue" in agent.instructions.lower()

    def test_create_courts_position_agent(self):
        """Test court's position agent creation."""
        agent = create_courts_position_agent()
        assert agent.name == "CourtsPositionAnalyzer"
        assert "court" in agent.instructions.lower()

    def test_create_obiter_dicta_agent(self):
        """Test obiter dicta agent creation."""
        agent = create_obiter_dicta_agent()
        assert agent.name == "ObiterDictaExtractor"
        assert "obiter dicta" in agent.instructions.lower()

    def test_create_dissenting_opinions_agent(self):
        """Test dissenting opinions agent creation."""
        agent = create_dissenting_opinions_agent()
        assert agent.name == "DissentingOpinionsExtractor"
        assert "dissent" in agent.instructions.lower()

    def test_create_abstract_agent(self):
        """Test abstract agent creation."""
        agent = create_abstract_agent()
        assert agent.name == "AbstractGenerator"
        assert "abstract" in agent.instructions.lower()


class TestOrchestrator:
    """Test orchestrator."""

    def test_orchestrator_initialization(self):
        """Test orchestrator initialization."""
        orchestrator = CaseAnalysisOrchestrator(model="gpt-4o-mini")
        assert orchestrator.model == "gpt-4o-mini"
        assert len(orchestrator.available_themes) > 0

    def test_orchestrator_with_custom_themes(self):
        """Test orchestrator with custom themes."""
        custom_themes = ["Custom Theme 1", "Custom Theme 2"]
        orchestrator = CaseAnalysisOrchestrator(available_themes=custom_themes)
        assert orchestrator.available_themes == custom_themes

    @pytest.mark.asyncio
    async def test_orchestrator_requires_api_key(self):
        """Test that orchestrator requires API key for actual analysis."""

        orchestrator = CaseAnalysisOrchestrator(model="gpt-4o-mini")

        # This test only checks that the method exists and has the right signature
        # Actual API calls would require a valid API key and are tested separately
        assert hasattr(orchestrator, "analyze_case")
        assert callable(orchestrator.analyze_case)


class TestModelValidation:
    """Test Pydantic model validation."""

    def test_jurisdiction_detection_requires_all_fields(self):
        """Test that JurisdictionDetection requires all fields."""
        with pytest.raises(Exception):  # Pydantic ValidationError  # noqa: B017
            JurisdictionDetection(legal_system_type="Civil-law jurisdiction")

    def test_col_extraction_validates_list(self):
        """Test that ChoiceOfLawExtraction validates col_sections as list."""
        data = {
            "col_sections": ["Section 1"],
            "confidence": "high",
            "reasoning": "Test",
        }
        model = ChoiceOfLawExtraction(**data)
        assert isinstance(model.col_sections, list)

    def test_theme_classification_validates_list(self):
        """Test that ThemeClassification validates themes as list."""
        data = {
            "themes": ["Theme 1", "Theme 2"],
            "confidence": "high",
            "reasoning": "Test",
        }
        model = ThemeClassification(**data)
        assert isinstance(model.themes, list)
        assert len(model.themes) == 2

    def test_pil_provisions_validates_list(self):
        """Test that PILProvisions validates provisions as list."""
        model = PILProvisions(provisions=["PILA Art. 116", "Rome I"])
        assert isinstance(model.provisions, list)
        assert len(model.provisions) == 2

    def test_complete_case_analysis_serialization(self):
        """Test that CompleteCaseAnalysis can be serialized."""
        data = {
            "case_citation": "Test Case",
            "jurisdiction_detection": {
                "legal_system_type": "Civil-law jurisdiction",
                "precise_jurisdiction": "Switzerland",
                "confidence": "high",
                "reasoning": "Test",
            },
            "col_extraction": {"col_sections": ["Section 1"], "confidence": "high", "reasoning": "Test"},
            "theme_classification": {"themes": ["Choice of Law"], "confidence": "high", "reasoning": "Test"},
            "relevant_facts": {"facts": "Test facts"},
            "pil_provisions": {"provisions": ["PILA Art. 116"]},
            "col_issue": {"issue": "Which law applies?"},
            "courts_position": {"position": "Swiss law applies"},
            "abstract": {"abstract": "Test abstract"},
            "metadata": {"model": "gpt-4o-mini", "timestamp": "2024-01-01T00:00:00"},
        }
        model = CompleteCaseAnalysis(**data)

        # Test that model can be dumped to dict
        dumped = model.model_dump()
        assert isinstance(dumped, dict)
        assert dumped["case_citation"] == "Test Case"
        assert "jurisdiction_detection" in dumped

        # Test that model can be serialized to JSON
        json_str = model.model_dump_json()
        assert isinstance(json_str, str)
        assert "Test Case" in json_str


class TestIntegration:
    """Integration tests for the PoC."""

    def test_poc_structure_complete(self):
        """Test that all components are available."""
        # Test models
        assert JurisdictionDetection is not None
        assert ChoiceOfLawExtraction is not None
        assert ThemeClassification is not None
        assert CompleteCaseAnalysis is not None

        # Test agent creators
        assert create_jurisdiction_agent is not None
        assert create_col_extraction_agent is not None
        assert create_theme_classification_agent is not None
        assert create_abstract_agent is not None

        # Test orchestrator
        assert CaseAnalysisOrchestrator is not None

    def test_agent_output_types_match_models(self):
        """Test that agent output types match the expected Pydantic models."""
        # Check that each agent has the correct output type
        jurisdiction_agent = create_jurisdiction_agent()
        assert jurisdiction_agent.output_type == JurisdictionDetection

        col_agent = create_col_extraction_agent()
        assert col_agent.output_type == ChoiceOfLawExtraction

        theme_agent = create_theme_classification_agent(["Theme 1"])
        assert theme_agent.output_type == ThemeClassification

        facts_agent = create_relevant_facts_agent()
        assert facts_agent.output_type == RelevantFacts

        provisions_agent = create_pil_provisions_agent()
        assert provisions_agent.output_type == PILProvisions

        issue_agent = create_col_issue_agent()
        assert issue_agent.output_type == ChoiceOfLawIssue

        position_agent = create_courts_position_agent()
        assert position_agent.output_type == CourtsPosition

        obiter_agent = create_obiter_dicta_agent()
        assert obiter_agent.output_type == ObiterDicta

        dissent_agent = create_dissenting_opinions_agent()
        assert dissent_agent.output_type == DissentingOpinions

        abstract_agent = create_abstract_agent()
        assert abstract_agent.output_type == CaseAbstract
