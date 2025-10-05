"""Pydantic models for classification tasks."""

from pydantic import BaseModel, Field


class JurisdictionOutput(BaseModel):
    """Output model for jurisdiction detection."""

    legal_system_type: str = Field(
        description="The type of legal system (e.g., 'Civil-law jurisdiction', 'Common-law jurisdiction', 'Indian jurisdiction')"
    )
    precise_jurisdiction: str = Field(description="The specific jurisdiction (e.g., 'Switzerland', 'United States', 'India')")
    jurisdiction_code: str = Field(description="ISO country code for the jurisdiction (e.g., 'CH', 'US', 'IN')")
    confidence: float = Field(
        ge=0.0, le=1.0, description="Confidence level in the detection (0.0 to 1.0)"
    )
    reasoning: str = Field(description="Explanation of how the jurisdiction was determined")


class ThemeClassificationOutput(BaseModel):
    """Output model for theme classification."""

    themes: list[str] = Field(description="List of classified PIL themes")
    confidence: float = Field(
        ge=0.0, le=1.0, description="Overall confidence level in the classification (0.0 to 1.0)"
    )
    reasoning: str = Field(description="Explanation of why these themes were selected")
