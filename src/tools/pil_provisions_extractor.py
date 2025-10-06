import asyncio
import logging

import logfire
from agents import Agent, Runner

from models.analysis_models import PILProvisionsOutput
from prompts.prompt_selector import get_prompt_module
from utils.system_prompt_generator import generate_system_prompt

logger = logging.getLogger(__name__)


def extract_pil_provisions(
    text: str,
    col_section: str,
    legal_system: str,
    jurisdiction: str | None,
    model: str,
):
    """
    Extract PIL provisions from court decision.

    Args:
        text: Full court decision text
        col_section: Choice of Law section text
        legal_system: Legal system type (e.g., "Civil-law jurisdiction")
        jurisdiction: Precise jurisdiction (e.g., "Switzerland")
        model: Model to use for extraction

    Returns:
        PILProvisionsOutput: Extracted provisions with confidence and reasoning
    """
    with logfire.span("extract_pil_provisions"):
        PIL_PROVISIONS_PROMPT = get_prompt_module(legal_system, "analysis", jurisdiction).PIL_PROVISIONS_PROMPT

        prompt = PIL_PROVISIONS_PROMPT.format(text=text, col_section=col_section)
        system_prompt = generate_system_prompt(legal_system, jurisdiction, "analysis")

        agent = Agent(
            name="PILProvisionsExtractor",
            instructions=system_prompt,
            output_type=PILProvisionsOutput,
            model=model,
        )
        result = asyncio.run(Runner.run(agent, prompt)).final_output_as(PILProvisionsOutput)

        logfire.info(
            "Extracted PIL provisions",
            text_length=len(text),
            col_section_length=len(col_section),
            provisions_count=len(result.pil_provisions),
            confidence=result.confidence,
        )
        return result
