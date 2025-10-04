"""Pydantic models for structured outputs in the CoLD Case Analyzer agents PoC."""

from typing import Any

from pydantic import BaseModel, Field


class JurisdictionDetection(BaseModel):
    """Result of jurisdiction detection analysis."""

    legal_system_type: str = Field(
        description="The legal system type: 'Civil-law jurisdiction', 'Common-law jurisdiction', or 'Indian jurisdiction'"
    )
    precise_jurisdiction: str | None = Field(
        default=None, description="The specific jurisdiction (e.g., 'Switzerland', 'USA', 'India')"
    )
    confidence: str = Field(description="Confidence level: 'high', 'medium', or 'low'")
    reasoning: str = Field(description="Explanation of how the jurisdiction was determined")


class ChoiceOfLawExtraction(BaseModel):
    """Result of Choice of Law section extraction."""

    col_sections: list[str] = Field(description="List of extracted Choice of Law sections from the court decision")
    confidence: str = Field(description="Confidence level: 'high', 'medium', or 'low'")
    reasoning: str = Field(description="Explanation of why these sections were selected")


class ThemeClassification(BaseModel):
    """Result of PIL theme classification."""

    themes: list[str] = Field(description="List of classified Private International Law themes")
    confidence: str = Field(description="Confidence level: 'high', 'medium', or 'low'")
    reasoning: str = Field(description="Explanation of how the themes were classified")


class RelevantFacts(BaseModel):
    """Relevant facts from the case."""

    facts: str = Field(description="Relevant factual background of the case")


class PILProvisions(BaseModel):
    """Private International Law provisions cited in the case."""

    provisions: list[str] = Field(description="List of PIL provisions cited")


class ChoiceOfLawIssue(BaseModel):
    """Choice of Law issue identified in the case."""

    issue: str = Field(description="The Choice of Law issue identified by the court")


class CourtsPosition(BaseModel):
    """Court's position and reasoning."""

    position: str = Field(description="The court's reasoning and position on the Choice of Law issue")


class ObiterDicta(BaseModel):
    """Obiter dicta from the case (Common Law jurisdictions)."""

    obiter_dicta: str = Field(description="Obiter dicta statements from the court")


class DissentingOpinions(BaseModel):
    """Dissenting opinions from the case (Common Law jurisdictions)."""

    dissenting_opinions: str = Field(description="Dissenting opinions in the case")


class CaseAbstract(BaseModel):
    """Abstract/summary of the case."""

    abstract: str = Field(description="Brief summary of the case and its Choice of Law aspects")


class CompleteCaseAnalysis(BaseModel):
    """Complete case analysis result with all components."""

    case_citation: str = Field(description="Case citation or identifier")
    jurisdiction_detection: JurisdictionDetection
    col_extraction: ChoiceOfLawExtraction
    theme_classification: ThemeClassification
    relevant_facts: RelevantFacts
    pil_provisions: PILProvisions
    col_issue: ChoiceOfLawIssue
    courts_position: CourtsPosition
    abstract: CaseAbstract
    obiter_dicta: ObiterDicta | None = Field(default=None, description="Only for Common Law jurisdictions")
    dissenting_opinions: DissentingOpinions | None = Field(default=None, description="Only for Common Law jurisdictions")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Additional metadata (model used, timestamps, etc.)")
