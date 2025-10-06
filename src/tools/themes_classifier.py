import asyncio
import csv
import logging
import time
from pathlib import Path

import logfire
from agents import Agent, Runner

from models.classification_models import ThemeClassificationOutput
from prompts.prompt_selector import get_prompt_module
from utils.themes_extractor import THEMES_TABLE_STR

logger = logging.getLogger(__name__)


def theme_classification_node(
    text: str,
    col_section: str,
    jurisdiction: str,
    specific_jurisdiction: str | None,
    model: str,
    previous_classification: str | None = None,
    iteration: int = 1,
):
    """
    Classify themes for a court decision.

    Args:
        text: Full court decision text
        col_section: Choice of Law section text
        jurisdiction: Legal system type (e.g., "Civil-law jurisdiction")
        specific_jurisdiction: Precise jurisdiction (e.g., "Switzerland")
        model: Model to use for classification
        previous_classification: Previously classified themes
        iteration: Iteration count for this classification

    Returns:
        ThemeClassificationOutput: Classified themes with confidence and reasoning
    """
    with logfire.span("classify_themes"):
        PIL_THEME_PROMPT = get_prompt_module(jurisdiction, "theme", specific_jurisdiction).PIL_THEME_PROMPT

        prompt = PIL_THEME_PROMPT.format(text=text, col_section=col_section, themes_table=THEMES_TABLE_STR)

        if previous_classification:
            prompt += f"\n\nPrevious classification: {previous_classification}\n"

        themes_path = Path(__file__).parents[1] / "data" / "themes.csv"
        valid_themes = set()
        with open(themes_path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                valid_themes.add(row["Theme"])

        max_attempts = 5
        cls_list: list[str] = []
        confidence = "low"
        reasoning = ""
        theme_time = 0.0
        attempt = 0
        result = None

        for attempt in range(1, max_attempts + 1):
            logger.debug("Prompting agent (attempt %d/%d) with: %s", attempt, max_attempts, prompt)
            start_time = time.time()

            # Create system prompt from parameters
            from utils.system_prompt_generator import generate_system_prompt
            system_prompt = generate_system_prompt(jurisdiction, specific_jurisdiction, "theme")

            agent = Agent(
                name="ThemeClassifier",
                instructions=system_prompt,
                output_type=ThemeClassificationOutput,
                model=model,
            )
            result = asyncio.run(Runner.run(agent, prompt)).final_output
            theme_time = time.time() - start_time

            cls_list = result.themes
            confidence = result.confidence
            reasoning = result.reasoning

            invalid = [item for item in cls_list if item not in valid_themes]
            if not invalid:
                break
            logger.debug("Invalid themes returned: %s. Retrying...", invalid)
            prompt += f"\n\nNote: These themes are invalid and should not be used: {invalid}. Please select only from the provided themes table."
        else:
            logger.debug("Max attempts reached. Proceeding with last classification: %s", cls_list)

        cls_str = ", ".join(str(item) for item in cls_list)
        logger.debug("Classified theme(s): %s (confidence: %s)", cls_list, confidence)

        logfire.info(
            "Classified themes",
            themes=cls_list,
            count=len(cls_list),
            time_seconds=theme_time,
            attempts=attempt,
            confidence=confidence,
        )

        if result is None:
            result = ThemeClassificationOutput(themes=cls_list, confidence=confidence, reasoning=reasoning)

        return result
