import asyncio
import logging

import logfire
from agents import Agent, Runner

from models.analysis_models import AbstractOutput
from prompts.prompt_selector import get_prompt_module
from utils.system_prompt_generator import generate_system_prompt

logger = logging.getLogger(__name__)


def extract_abstract(
    text: str,
    jurisdiction: str,
    specific_jurisdiction: str | None,
    model: str,
    classification: str,
    facts: str,
    pil_provisions: str,
    col_issue: str,
    court_position: str,
    obiter_dicta: str = "",
    dissenting_opinions: str = "",
):
    """
    Generate abstract from court decision analysis.

    Args:
        text: Full court decision text
        jurisdiction: Legal system type (e.g., "Civil-law jurisdiction")
        specific_jurisdiction: Precise jurisdiction (e.g., "Switzerland")
        model: Model to use for generation
        classification: Classified themes
        facts: Relevant facts
        pil_provisions: PIL provisions
        col_issue: Choice of Law issue
        court_position: Court's position
        obiter_dicta: Obiter dicta (for Common Law jurisdictions)
        dissenting_opinions: Dissenting opinions (for Common Law jurisdictions)

    Returns:
        AbstractOutput: Generated abstract with confidence and reasoning
    """
    with logfire.span("generate_abstract"):
        ABSTRACT_PROMPT = get_prompt_module(jurisdiction, "analysis", specific_jurisdiction).ABSTRACT_PROMPT

        prompt_vars = {
            "text": text,
            "classification": classification,
            "facts": facts,
            "pil_provisions": pil_provisions,
            "col_issue": col_issue,
            "court_position": court_position,
        }

        if jurisdiction == "Common-law jurisdiction" or (specific_jurisdiction and specific_jurisdiction.lower() == "india"):
            prompt_vars.update({"obiter_dicta": obiter_dicta, "dissenting_opinions": dissenting_opinions})

        prompt = ABSTRACT_PROMPT.format(**prompt_vars)
        system_prompt = generate_system_prompt(jurisdiction, specific_jurisdiction, "analysis")

        agent = Agent(
            name="AbstractGenerator",
            instructions=system_prompt,
            output_type=AbstractOutput,
            model=model,
        )
        result = asyncio.run(Runner.run(agent, prompt)).final_output_as(AbstractOutput)

        logfire.info(
            "Generated abstract",
            text_length=len(text),
            result_length=len(result.abstract),
            confidence=result.confidence,
        )
        return result
