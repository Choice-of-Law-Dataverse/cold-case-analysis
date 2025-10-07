import asyncio
import logging

import logfire
from agents import Agent, Runner

from models.analysis_models import ColIssueOutput, ColSectionOutput
from models.classification_models import ThemeClassificationOutput
from prompts.prompt_selector import get_prompt_module
from utils.system_prompt_generator import generate_system_prompt
from utils.themes_extractor import filter_themes_by_list

logger = logging.getLogger(__name__)


def extract_col_issue(
    text: str,
    col_section_output: ColSectionOutput,
    legal_system: str,
    jurisdiction: str | None,
    model: str,
    themes_output: ThemeClassificationOutput,
):
    """
    Extract Choice of Law issue from court decision.

    Args:
        text: Full court decision text
        col_section_output: Extracted Choice of Law sections
        legal_system: Legal system type (e.g., "Civil-law jurisdiction")
        jurisdiction: Precise jurisdiction (e.g., "Switzerland")
        model: Model to use for extraction
        themes_output: Classified themes output

    Returns:
        ColIssueOutput: Extracted issue with confidence and reasoning
    """
    with logfire.span("extract_col_issue"):
        COL_ISSUE_PROMPT = get_prompt_module(legal_system, "analysis", jurisdiction).COL_ISSUE_PROMPT

        # Extract data from typed outputs
        col_section = "\n\n".join(col_section_output.col_sections)
        themes = themes_output.themes
        themes_definitions = filter_themes_by_list(themes)

        prompt = COL_ISSUE_PROMPT.format(
            text=text, col_section=col_section, classification_definitions=themes_definitions
        )
        system_prompt = generate_system_prompt(legal_system, jurisdiction, "analysis")

        agent = Agent(
            name="ColIssueExtractor",
            instructions=system_prompt,
            output_type=ColIssueOutput,
            model=model,
        )
        result = asyncio.run(Runner.run(agent, prompt)).final_output_as(ColIssueOutput)

        logfire.info(
            "Extracted CoL issue",
            text_length=len(text),
            col_section_length=len(col_section),
            themes_count=len(themes),
            result_length=len(result.col_issue),
            confidence=result.confidence,
        )
        return result
