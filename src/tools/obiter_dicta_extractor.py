import asyncio
import logging

import logfire
from agents import Agent, Runner
from agents.models.openai_chatcompletions import OpenAIChatCompletionsModel

from config import get_model, get_openai_client
from models.analysis_models import ColIssueOutput, ColSectionOutput, ObiterDictaOutput
from models.classification_models import ThemeClassificationOutput
from prompts.prompt_selector import get_prompt_module
from utils.system_prompt_generator import generate_system_prompt

logger = logging.getLogger(__name__)


def extract_obiter_dicta(
    text: str,
    col_section_output: ColSectionOutput,
    legal_system: str,
    jurisdiction: str | None,
    themes_output: ThemeClassificationOutput,
    col_issue_output: ColIssueOutput,
):
    """
    Extract obiter dicta from court decision.

    Args:
        text: Full court decision text
        col_section_output: Extracted Choice of Law sections
        legal_system: Legal system type (e.g., "Civil-law jurisdiction")
        jurisdiction: Precise jurisdiction (e.g., "Switzerland")
        themes_output: Classified themes output
        col_issue_output: Extracted Choice of Law issue

    Returns:
        ObiterDictaOutput: Extracted obiter dicta with confidence and reasoning
    """
    with logfire.span("obiter_dicta"):
        prompt_module = get_prompt_module(legal_system, "analysis", jurisdiction)
        OBITER_PROMPT = prompt_module.COURTS_POSITION_OBITER_DICTA_PROMPT

        themes = ", ".join(themes_output.themes)
        col_issue = col_issue_output.col_issue

        prompt = OBITER_PROMPT.format(
            text=text, col_section=str(col_section_output), classification=themes, col_issue=col_issue
        )
        system_prompt = generate_system_prompt(legal_system, jurisdiction, "analysis")

        agent = Agent(
            name="ObiterDictaExtractor",
            instructions=system_prompt,
            output_type=ObiterDictaOutput,
            model=OpenAIChatCompletionsModel(
                model=get_model("obiter_dicta"),
                openai_client=get_openai_client(),
            ),
        )
        result = asyncio.run(Runner.run(agent, prompt)).final_output_as(ObiterDictaOutput)

        return result
