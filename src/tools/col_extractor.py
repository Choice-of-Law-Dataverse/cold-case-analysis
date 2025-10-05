import logging
import time
from typing import Any

import logfire

import config
from models.analysis_models import ColSectionOutput
from prompts.prompt_selector import get_prompt_module
from utils.system_prompt_generator import get_system_prompt_for_analysis

logger = logging.getLogger(__name__)


def _call_openai_structured(prompt: str, system_prompt: str, response_format: type, model: str | None = None) -> Any:
    """Call OpenAI API with structured outputs using Pydantic models."""
    client, selected_model = config.get_openai_client(model)
    completion = client.beta.chat.completions.parse(
        model=selected_model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt},
        ],
        response_format=response_format,
    )
    return completion.choices[0].message.parsed


def _coerce_to_text(content: Any) -> str:
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return "\n".join(str(item) for item in content if item is not None)
    return str(content) if content is not None else ""


def extract_col_section(state):
    with logfire.span("extract_col_section"):
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

        result = _call_openai_structured(prompt, system_prompt, ColSectionOutput, state.get("model"))
        col_time = time.time() - start_time
        col_section = result.col_section.strip()
        confidence = result.confidence
        reasoning = result.reasoning

        state.setdefault("col_section", []).append(col_section)
        state.setdefault("col_section_confidence", []).append(confidence)
        state.setdefault("col_section_reasoning", []).append(reasoning)
        logger.debug("Extracted Choice of Law section: %s (confidence: %.2f)", col_section, confidence)

        logfire.info("Extracted CoL section", chars=len(col_section), iteration=iter_count, time_seconds=col_time, confidence=confidence)
        return {
            "col_section": state["col_section"],
            "col_section_confidence": state["col_section_confidence"],
            "col_section_reasoning": state["col_section_reasoning"],
            "col_section_feedback": state.get("col_section_feedback", []),
            "col_section_time": col_time,
        }
