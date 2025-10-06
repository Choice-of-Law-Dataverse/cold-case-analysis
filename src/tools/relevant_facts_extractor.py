import asyncio
import logging

import logfire
from agents import Agent, Runner

from models.analysis_models import RelevantFactsOutput
from prompts.prompt_selector import get_prompt_module
from utils.system_prompt_generator import generate_system_prompt

logger = logging.getLogger(__name__)


def extract_relevant_facts(
    text: str,
    col_section: str,
    jurisdiction: str,
    specific_jurisdiction: str | None,
    model: str,
):
    """
    Extract relevant facts from court decision.

    Args:
        text: Full court decision text
        col_section: Choice of Law section text
        jurisdiction: Legal system type (e.g., "Civil-law jurisdiction")
        specific_jurisdiction: Precise jurisdiction (e.g., "Switzerland")
        model: Model to use for extraction

    Returns:
        RelevantFactsOutput: Extracted facts with confidence and reasoning
    """
    with logfire.span("extract_relevant_facts"):
        FACTS_PROMPT = get_prompt_module(jurisdiction, "analysis", specific_jurisdiction).FACTS_PROMPT

        prompt = FACTS_PROMPT.format(text=text, col_section=col_section)
        system_prompt = generate_system_prompt(jurisdiction, specific_jurisdiction, "analysis")

        agent = Agent(
            name="RelevantFactsExtractor",
            instructions=system_prompt,
            output_type=RelevantFactsOutput,
            model=model,
        )
        result = asyncio.run(Runner.run(agent, prompt)).final_output_as(RelevantFactsOutput)

        logfire.info(
            "Extracted relevant facts",
            text_length=len(text),
            col_section_length=len(col_section),
            result_length=len(result.relevant_facts),
            confidence=result.confidence,
        )
        return result
