import asyncio
import logging

import logfire
from agents import Agent, Runner

from models.analysis_models import ObiterDictaOutput
from prompts.prompt_selector import get_prompt_module
from utils.system_prompt_generator import generate_system_prompt

logger = logging.getLogger(__name__)


def extract_obiter_dicta(
    text: str,
    col_section: str,
    jurisdiction: str,
    specific_jurisdiction: str | None,
    model: str,
    classification: str,
    col_issue: str,
):
    """
    Extract obiter dicta from court decision.

    Args:
        text: Full court decision text
        col_section: Choice of Law section text
        jurisdiction: Legal system type (e.g., "Civil-law jurisdiction")
        specific_jurisdiction: Precise jurisdiction (e.g., "Switzerland")
        model: Model to use for extraction
        classification: Classified themes
        col_issue: Choice of Law issue

    Returns:
        ObiterDictaOutput: Extracted obiter dicta with confidence and reasoning
    """
    with logfire.span("extract_obiter_dicta"):
        prompt_module = get_prompt_module(jurisdiction, "analysis", specific_jurisdiction)
        OBITER_PROMPT = prompt_module.COURTS_POSITION_OBITER_DICTA_PROMPT
        prompt = OBITER_PROMPT.format(text=text, col_section=col_section, classification=classification, col_issue=col_issue)
        system_prompt = generate_system_prompt(jurisdiction, specific_jurisdiction, "analysis")

        agent = Agent(
            name="ObiterDictaExtractor",
            instructions=system_prompt,
            output_type=ObiterDictaOutput,
            model=model,
        )
        result = asyncio.run(Runner.run(agent, prompt)).final_output_as(ObiterDictaOutput)

        logfire.info(
            "Extracted obiter dicta",
            text_length=len(text),
            col_section_length=len(col_section),
            result_length=len(result.obiter_dicta),
            confidence=result.confidence,
        )
        return result
