"""Pydantic models for classification tasks."""

from typing import Literal

from pydantic import BaseModel, Field


class JurisdictionOutput(BaseModel):
    """Output model for jurisdiction detection."""

    legal_system_type: str = Field(
        description="The type of legal system (e.g., 'Civil-law jurisdiction', 'Common-law jurisdiction', 'Indian jurisdiction')"
    )
    precise_jurisdiction: str = Field(description="The specific jurisdiction (e.g., 'Switzerland', 'United States', 'India')")
    jurisdiction_code: str = Field(description="ISO country code for the jurisdiction (e.g., 'CH', 'US', 'IN')")
    confidence: Literal["low", "medium", "high"] = Field(
        description="Confidence level in the detection: 'low', 'medium', or 'high'"
    )
    reasoning: str = Field(description="Explanation of how the jurisdiction was determined")


class ThemeClassificationOutput(BaseModel):
    """Output model for theme classification."""

    themes: list[str] = Field(description="List of classified PIL themes")
    confidence: Literal["low", "medium", "high"] = Field(
        description="Overall confidence level in the classification: 'low', 'medium', or 'high'"
    )
    reasoning: str = Field(description="Explanation of why these themes were selected")
