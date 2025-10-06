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
    jurisdiction: str,
    specific_jurisdiction: str | None,
    model: str,
    feedback: list[str] | None = None,
    previous_section: str | None = None,
    iteration: int = 1,
):
    """
    Extract Choice of Law section from court decision text.

    Args:
        text: Full court decision text
        jurisdiction: Legal system type (e.g., "Civil-law jurisdiction")
        specific_jurisdiction: Precise jurisdiction (e.g., "Switzerland")
        model: Model to use for extraction
        feedback: List of feedback to improve extraction
        previous_section: Previously extracted section
        iteration: Iteration count for this extraction

    Returns:
        ColSectionOutput: Extracted section with confidence and reasoning
    """
    with logfire.span("extract_col_section"):
        COL_SECTION_PROMPT = get_prompt_module(jurisdiction, "col_section", specific_jurisdiction).COL_SECTION_PROMPT

        prompt = COL_SECTION_PROMPT.format(text=text)

        if previous_section:
            prompt += f"\n\nPrevious extraction: {previous_section}\n"

        if feedback:
            last_fb = feedback[-1]
            prompt += f"\n\nFeedback: {last_fb}\n"

        system_prompt = generate_system_prompt(jurisdiction, specific_jurisdiction, "col_section")

        agent = Agent(
            name="ColSectionExtractor",
            instructions=system_prompt,
            output_type=ColSectionOutput,
            model=model,
        )
        result = asyncio.run(Runner.run(agent, prompt)).final_output

        logfire.info(
            "Extracted CoL section",
            text_length=len(text),
            result_length=len(result.col_section),
            iteration=iteration,
            has_feedback=bool(feedback),
            confidence=result.confidence,
        )
        return result
