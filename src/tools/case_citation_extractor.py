import asyncio
import logging

import logfire
from agents import Agent, Runner, TResponseInputItem

from models.analysis_models import CaseCitationOutput

logger = logging.getLogger(__name__)


def extract_case_citation(
    text: str,
    legal_system: str,
    jurisdiction: str,
    model: str,
):
    """
    Extract case citation from court decision.

    Args:
        text: Full court decision text
        col_section: Choice of Law section text
        legal_system: Legal system type (e.g., "Civil-law jurisdiction")
        jurisdiction: Precise jurisdiction (e.g., "Switzerland")
        model: Model to use for extraction

    Returns:
        RelevantFactsOutput: Extracted facts with confidence and reasoning
    """
    with logfire.span("extract_case_citation"):
        instructions = "Extract the case citation from the provided court decision text. Provide the citation in an academic format, including all necessary details such as case name, reporter, court, and year. If the citation is not explicitly mentioned in the text, infer it based on context. Ensure accuracy and clarity in the citation format. Tailor the citation style to the legal system and jurisdiction specified."

        prompt: list[TResponseInputItem] = [
            {
                "role": "user",
                "content": f"Jusdiction: {jurisdiction}\nLegal System: {legal_system}",
            },
            {
                "role": "user",
                "content": text,
            },
        ]

        agent = Agent(
            name="CaseCitationExtractor",
            instructions=instructions,
            output_type=CaseCitationOutput,
            model=model,
        )
        result = asyncio.run(Runner.run(agent, prompt)).final_output_as(CaseCitationOutput)

        return result
