import asyncio
import logging

import logfire
from agents import Agent, Runner

from models.analysis_models import (
    AbstractOutput,
    ColIssueOutput,
    CourtsPositionOutput,
    DissentingOpinionsOutput,
    ObiterDictaOutput,
    PILProvisionsOutput,
    RelevantFactsOutput,
)
from models.classification_models import ThemeClassificationOutput
from prompts.prompt_selector import get_prompt_module
from utils.system_prompt_generator import generate_system_prompt

logger = logging.getLogger(__name__)


def extract_abstract(
    text: str,
    legal_system: str,
    jurisdiction: str | None,
    model: str,
    themes_output: ThemeClassificationOutput,
    facts_output: RelevantFactsOutput,
    pil_provisions_output: PILProvisionsOutput,
    col_issue_output: ColIssueOutput,
    court_position_output: CourtsPositionOutput,
    obiter_dicta_output: ObiterDictaOutput | None = None,
    dissenting_opinions_output: DissentingOpinionsOutput | None = None,
):
    """
    Generate abstract from court decision analysis.

    Args:
        text: Full court decision text
        legal_system: Legal system type (e.g., "Civil-law jurisdiction")
        jurisdiction: Precise jurisdiction (e.g., "Switzerland")
        model: Model to use for generation
        themes_output: Classified themes output
        facts_output: Relevant facts output
        pil_provisions_output: PIL provisions output
        col_issue_output: Choice of Law issue output
        court_position_output: Court's position output
        obiter_dicta_output: Obiter dicta output (for Common Law jurisdictions)
        dissenting_opinions_output: Dissenting opinions output (for Common Law jurisdictions)

    Returns:
        AbstractOutput: Generated abstract with confidence and reasoning
    """
    with logfire.span("generate_abstract"):
        ABSTRACT_PROMPT = get_prompt_module(legal_system, "analysis", jurisdiction).ABSTRACT_PROMPT

        themes = ", ".join(themes_output.themes)
        facts = facts_output.relevant_facts
        pil_provisions = "\n".join(pil_provisions_output.pil_provisions)
        col_issue = col_issue_output.col_issue
        court_position = court_position_output.courts_position

        prompt_vars = {
            "text": text,
            "classification": themes,
            "facts": facts,
            "pil_provisions": pil_provisions,
            "col_issue": col_issue,
            "court_position": court_position,
        }

        if legal_system == "Common-law jurisdiction" or (jurisdiction and jurisdiction.lower() == "india"):
            obiter_dicta = obiter_dicta_output.obiter_dicta if obiter_dicta_output else ""
            dissenting_opinions = dissenting_opinions_output.dissenting_opinions if dissenting_opinions_output else ""
            prompt_vars.update({"obiter_dicta": obiter_dicta, "dissenting_opinions": dissenting_opinions})

        prompt = ABSTRACT_PROMPT.format(**prompt_vars)
        system_prompt = generate_system_prompt(legal_system, jurisdiction, "analysis")

        agent = Agent(
            name="AbstractGenerator",
            instructions=system_prompt,
            output_type=AbstractOutput,
            model=model,
        )
        result = asyncio.run(Runner.run(agent, prompt)).final_output_as(AbstractOutput)

        return result
