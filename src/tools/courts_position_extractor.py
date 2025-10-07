import asyncio
import logging

import logfire
from agents import Agent, Runner

from models.analysis_models import ColIssueOutput, ColSectionOutput, CourtsPositionOutput
from models.classification_models import ThemeClassificationOutput
from prompts.prompt_selector import get_prompt_module
from utils.system_prompt_generator import generate_system_prompt

logger = logging.getLogger(__name__)


def extract_courts_position(
    text: str,
    col_section_output: ColSectionOutput,
    legal_system: str,
    jurisdiction: str | None,
    model: str,
    themes_output: ThemeClassificationOutput,
    col_issue_output: ColIssueOutput,
):
    """
    Extract court's position from court decision.

    Args:
        text: Full court decision text
        col_section_output: Extracted Choice of Law sections
        legal_system: Legal system type (e.g., "Civil-law jurisdiction")
        jurisdiction: Precise jurisdiction (e.g., "Switzerland")
        model: Model to use for extraction
        themes_output: Classified themes output
        col_issue_output: Extracted Choice of Law issue

    Returns:
        CourtsPositionOutput: Extracted position with confidence and reasoning
    """
    with logfire.span("extract_courts_position"):
        COURTS_POSITION_PROMPT = get_prompt_module(legal_system, "analysis", jurisdiction).COURTS_POSITION_PROMPT

        # Extract data from typed outputs
        col_section = "\n\n".join(col_section_output.col_sections)
        themes = ", ".join(themes_output.themes)
        col_issue = col_issue_output.col_issue

        prompt = COURTS_POSITION_PROMPT.format(
            col_issue=col_issue, text=text, col_section=col_section, classification=themes
        )
        system_prompt = generate_system_prompt(legal_system, jurisdiction, "analysis")

        agent = Agent(
            name="CourtsPositionAnalyzer",
            instructions=system_prompt,
            output_type=CourtsPositionOutput,
            model=model,
        )
        result = asyncio.run(Runner.run(agent, prompt)).final_output_as(CourtsPositionOutput)

        logfire.info(
            "Extracted court's position",
            text_length=len(text),
            col_section_length=len(col_section),
            result_length=len(result.courts_position),
            confidence=result.confidence,
        )
        return result
