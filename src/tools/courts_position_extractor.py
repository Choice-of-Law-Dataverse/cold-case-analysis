import asyncio
import logging

import logfire
from agents import Agent, Runner

from models.analysis_models import CourtsPositionOutput
from prompts.prompt_selector import get_prompt_module
from utils.system_prompt_generator import generate_system_prompt

logger = logging.getLogger(__name__)


def extract_courts_position(
    text: str,
    col_section: str,
    jurisdiction: str,
    specific_jurisdiction: str | None,
    model: str,
    classification: str,
    col_issue: str,
):
    """
    Extract court's position from court decision.

    Args:
        text: Full court decision text
        col_section: Choice of Law section text
        jurisdiction: Legal system type (e.g., "Civil-law jurisdiction")
        specific_jurisdiction: Precise jurisdiction (e.g., "Switzerland")
        model: Model to use for extraction
        classification: Classified themes
        col_issue: Choice of Law issue

    Returns:
        CourtsPositionOutput: Extracted position with confidence and reasoning
    """
    with logfire.span("extract_courts_position"):
        COURTS_POSITION_PROMPT = get_prompt_module(jurisdiction, "analysis", specific_jurisdiction).COURTS_POSITION_PROMPT

        prompt = COURTS_POSITION_PROMPT.format(
            col_issue=col_issue, text=text, col_section=col_section, classification=classification
        )
        system_prompt = generate_system_prompt(jurisdiction, specific_jurisdiction, "analysis")

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
