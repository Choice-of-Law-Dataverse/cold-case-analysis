import asyncio
import logging

import logfire
from agents import Agent, Runner

from models.analysis_models import ColSectionOutput, RelevantFactsOutput
from prompts.prompt_selector import get_prompt_module
from utils.system_prompt_generator import generate_system_prompt

logger = logging.getLogger(__name__)


def extract_relevant_facts(
    text: str,
    col_section_output: ColSectionOutput,
    legal_system: str,
    jurisdiction: str | None,
    model: str,
):
    """
    Extract relevant facts from court decision.

    Args:
        text: Full court decision text
        col_section: Choice of Law section text
        legal_system: Legal system type (e.g., "Civil-law jurisdiction")
        jurisdiction: Precise jurisdiction (e.g., "Switzerland")
        model: Model to use for extraction

    Returns:
        RelevantFactsOutput: Extracted facts with confidence and reasoning
    """
    with logfire.span("extract_relevant_facts"):
        FACTS_PROMPT = get_prompt_module(legal_system, "analysis", jurisdiction).FACTS_PROMPT

        prompt = FACTS_PROMPT.format(text=text, col_section=str(col_section_output))
        system_prompt = generate_system_prompt(legal_system, jurisdiction, "analysis")

        agent = Agent(
            name="RelevantFactsExtractor",
            instructions=system_prompt,
            output_type=RelevantFactsOutput,
            model=model,
        )
        result = asyncio.run(Runner.run(agent, prompt)).final_output_as(RelevantFactsOutput)

        return result
