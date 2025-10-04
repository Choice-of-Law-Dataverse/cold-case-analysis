import logging
import time
from typing import Any

from langchain_core.messages import HumanMessage, SystemMessage

import config
from prompts.prompt_selector import get_prompt_module
from utils.system_prompt_generator import get_system_prompt_for_analysis

logger = logging.getLogger(__name__)


def _coerce_to_text(content: Any) -> str:
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return "\n".join(str(item) for item in content if item is not None)
    return str(content) if content is not None else ""


def extract_col_section(state):
    logger.debug("--- COL SECTION EXTRACTION ---")
    feedback = state.get("col_section_feedback", [])
    text = state["full_text"]
    jurisdiction = state.get("jurisdiction", "Civil-law jurisdiction")
    specific_jurisdiction = state.get("precise_jurisdiction")
    COL_SECTION_PROMPT = get_prompt_module(jurisdiction, "col_section", specific_jurisdiction).COL_SECTION_PROMPT
    
    if feedback:
        logger.debug("Feedback for col section: %s", feedback)
    prompt = COL_SECTION_PROMPT.format(text=text)

    iter_count = state.get("col_section_eval_iter", 0) + 1
    state["col_section_eval_iter"] = iter_count
    
    existing_sections = state.get("col_section", [])
    if existing_sections:
        prev = existing_sections[-1]
        if prev:
            prompt += f"\n\nPrevious extraction: {prev}\n"

    if feedback:
        last_fb = feedback[-1]
        prompt += f"\n\nFeedback: {last_fb}\n"
    logger.debug("Prompting LLM with: %s", prompt)
    start_time = time.time()

    system_prompt = get_system_prompt_for_analysis(state)

    response = config.llm.invoke([
        SystemMessage(content=system_prompt),
        HumanMessage(content=prompt)
    ])
    col_time = time.time() - start_time
    col_section = _coerce_to_text(getattr(response, "content", "")).strip()
    state.setdefault("col_section", []).append(col_section)
    logger.debug("Extracted Choice of Law section: %s", col_section)

    return {
        "col_section": state["col_section"],
        "col_section_feedback": state.get("col_section_feedback", []),
        "col_section_time": col_time
    }
