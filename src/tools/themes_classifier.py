import csv
import json
import logging
import time
from pathlib import Path
from typing import Any

import logfire
from langchain_core.messages import HumanMessage, SystemMessage

import config
from prompts.prompt_selector import get_prompt_module
from utils.system_prompt_generator import get_system_prompt_for_analysis
from utils.themes_extractor import THEMES_TABLE_STR

logger = logging.getLogger(__name__)


def _coerce_to_text(content: Any) -> str:
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return "\n".join(str(item) for item in content if item is not None)
    return str(content) if content is not None else ""


def theme_classification_node(state):
    with logfire.span("classify_themes"):
        text = state["full_text"]
        jurisdiction = state.get("jurisdiction", "Civil-law jurisdiction")
        specific_jurisdiction = state.get("precise_jurisdiction")
        PIL_THEME_PROMPT = get_prompt_module(jurisdiction, "theme", specific_jurisdiction).PIL_THEME_PROMPT

        col_section = ""
        sections = state.get("col_section", [])
        if sections:
            col_section = sections[-1]

        iter_count = state.get("theme_eval_iter", 0) + 1
        state["theme_eval_iter"] = iter_count

        prompt = PIL_THEME_PROMPT.format(text=text, col_section=col_section, themes_table=THEMES_TABLE_STR)

        existing = state.get("classification", [])
        if existing:
            prev = existing[-1]
            if prev:
                prompt += f"\n\nPrevious classification: {prev}\n"

        themes_path = Path(__file__).parents[1] / "data" / "themes.csv"
        valid_themes = set()
        with open(themes_path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                valid_themes.add(row["Theme"])

        max_attempts = 5
        cls_list: list[Any] = []
        theme_time = 0.0
        for attempt in range(1, max_attempts + 1):
            logger.debug("Prompting LLM (attempt %d/%d) with: %s", attempt, max_attempts, prompt)
            start_time = time.time()

            system_prompt = get_system_prompt_for_analysis(state)

            response = config.llm.invoke([
                SystemMessage(content=system_prompt),
                HumanMessage(content=prompt)
            ])
            theme_time = time.time() - start_time

            raw_content = getattr(response, "content", "")
            content_str = _coerce_to_text(raw_content)
            try:
                parsed = json.loads(content_str)
                cls_list = parsed if isinstance(parsed, list) else [parsed]
            except Exception:
                cls_list = [content_str.strip()]
            cls_list = [str(item) for item in cls_list if str(item).strip()]

            invalid = [item for item in cls_list if item not in valid_themes]
            if not invalid:
                break
            logger.debug("Invalid themes returned: %s. Retrying...", invalid)
        else:
            logger.debug("Max attempts reached. Proceeding with last classification: %s", cls_list)

        cls_str = ", ".join(str(item) for item in cls_list)
        logger.debug("Classified theme(s): %s", cls_list)
        state.setdefault("classification", []).append(cls_str)

        logfire.info("Classified themes", themes=cls_list, count=len(cls_list), time_seconds=theme_time, attempts=attempt)
        return {
            "classification": state["classification"],
            "theme_feedback": state.get("theme_feedback", []),
            "theme_classification_time": theme_time
        }
