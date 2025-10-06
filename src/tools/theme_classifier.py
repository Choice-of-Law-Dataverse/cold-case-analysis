import asyncio
import logging

import logfire
from agents import Agent, Runner

from models.classification_models import ThemeClassificationOutput
from prompts.prompt_selector import get_prompt_module
from utils.system_prompt_generator import generate_system_prompt
from utils.themes_extractor import THEMES_TABLE_STR

logger = logging.getLogger(__name__)


def theme_classification_node(
    text: str,
    col_section: str,
    jurisdiction: str,
    specific_jurisdiction: str | None,
    model: str,
):
    """
    Classify themes for a court decision.

    Args:
        text: Full court decision text
        col_section: Choice of Law section text
        jurisdiction: Legal system type (e.g., "Civil-law jurisdiction")
        specific_jurisdiction: Precise jurisdiction (e.g., "Switzerland")
        model: Model to use for classification

    Returns:
        ThemeClassificationOutput: Classified themes with confidence and reasoning
    """
    with logfire.span("classify_themes"):
        PIL_THEME_PROMPT = get_prompt_module(jurisdiction, "theme", specific_jurisdiction).PIL_THEME_PROMPT

        base_prompt = PIL_THEME_PROMPT.format(text=text, col_section=col_section, themes_table=THEMES_TABLE_STR)

        max_attempts = 5
        attempt = 0
        result = None
        current_prompt = base_prompt

        for attempt in range(1, max_attempts + 1):
            try:
                system_prompt = generate_system_prompt(jurisdiction, specific_jurisdiction, "theme")

                agent = Agent(
                    name="ThemeClassifier",
                    instructions=system_prompt,
                    output_type=ThemeClassificationOutput,
                    model=model,
                )
                result = asyncio.run(Runner.run(agent, current_prompt)).final_output_as(ThemeClassificationOutput)
                break
            except Exception as e:
                logger.error("Error during theme classification attempt %d: %s", attempt, e)
                if attempt == max_attempts:
                    logger.error("Max attempts reached. Returning fallback result.")
                    result = None
                continue

        logfire.info(
            "Classified themes",
            text_length=len(text),
            col_section_length=len(col_section),
            themes_table_length=len(THEMES_TABLE_STR),
            themes_count=len(result.themes) if result else 0,
            attempts=attempt,
            confidence=result.confidence if result else "none",
        )

        if result is None:
            fallback_reason = f"Classification failed after {max_attempts} attempts."
            result = ThemeClassificationOutput(themes=["NA"], confidence="low", reasoning=fallback_reason)

        return result
