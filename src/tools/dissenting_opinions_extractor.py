import asyncio
import logging

import logfire
from agents import Agent, Runner

from models.analysis_models import DissentingOpinionsOutput
from prompts.prompt_selector import get_prompt_module
from utils.system_prompt_generator import generate_system_prompt

logger = logging.getLogger(__name__)


def extract_dissenting_opinions(
    text: str,
    col_section: str,
    jurisdiction: str,
    specific_jurisdiction: str | None,
    model: str,
    classification: str,
    col_issue: str,
):
    """
    Extract dissenting opinions from court decision.

    Args:
        text: Full court decision text
        col_section: Choice of Law section text
        jurisdiction: Legal system type (e.g., "Civil-law jurisdiction")
        specific_jurisdiction: Precise jurisdiction (e.g., "Switzerland")
        model: Model to use for extraction
        classification: Classified themes
        col_issue: Choice of Law issue

    Returns:
        DissentingOpinionsOutput: Extracted opinions with confidence and reasoning
    """
    with logfire.span("extract_dissenting_opinions"):
        prompt_module = get_prompt_module(jurisdiction, "analysis", specific_jurisdiction)
        DISSENT_PROMPT = prompt_module.COURTS_POSITION_DISSENTING_OPINIONS_PROMPT
        prompt = DISSENT_PROMPT.format(text=text, col_section=col_section, classification=classification, col_issue=col_issue)
        system_prompt = generate_system_prompt(jurisdiction, specific_jurisdiction, "analysis")

        agent = Agent(
            name="DissentingOpinionsExtractor",
            instructions=system_prompt,
            output_type=DissentingOpinionsOutput,
            model=model,
        )
        result = asyncio.run(Runner.run(agent, prompt)).final_output_as(DissentingOpinionsOutput)

        logfire.info(
            "Extracted dissenting opinions",
            text_length=len(text),
            col_section_length=len(col_section),
            result_length=len(result.dissenting_opinions),
            confidence=result.confidence,
        )
        return result
