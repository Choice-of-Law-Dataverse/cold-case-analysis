import asyncio
import logging

import logfire
from agents import Agent, Runner

from models.analysis_models import ColSectionOutput
from prompts.prompt_selector import get_prompt_module
from utils.system_prompt_generator import generate_system_prompt

logger = logging.getLogger(__name__)


def extract_col_section(
    text: str,
    legal_system: str,
    jurisdiction: str | None,
    model: str,
):
    """
    Extract Choice of Law section from court decision text.

    Args:
        text: Full court decision text
        legal_system: Legal system type (e.g., "Civil-law jurisdiction")
        jurisdiction: Precise jurisdiction (e.g., "Switzerland")
        model: Model to use for extraction


    Returns:
        ColSectionOutput: Extracted sections with confidence and reasoning
    """
    with logfire.span("extract_col_section"):
        COL_SECTION_PROMPT = get_prompt_module(legal_system, "col_section", jurisdiction).COL_SECTION_PROMPT

        prompt = COL_SECTION_PROMPT.format(text=text)

        system_prompt = generate_system_prompt(legal_system, jurisdiction, "col_section")

        agent = Agent(
            name="ColSectionExtractor",
            instructions=system_prompt,
            output_type=ColSectionOutput,
            model=model,
        )
        result = asyncio.run(Runner.run(agent, prompt)).final_output_as(ColSectionOutput)

        logfire.info(
            "Extracted CoL sections",
            text_length=len(text),
            sections_count=len(result.col_sections),
            confidence=result.confidence,
        )
        return result
