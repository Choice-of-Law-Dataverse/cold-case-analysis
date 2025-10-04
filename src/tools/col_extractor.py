import time
from typing import Any

from langchain_core.messages import HumanMessage, SystemMessage

import config
from prompts.prompt_selector import get_prompt_module
from utils.system_prompt_generator import get_system_prompt_for_analysis


def _coerce_to_text(content: Any) -> str:
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return "\n".join(str(item) for item in content if item is not None)
    return str(content) if content is not None else ""


def extract_col_section(state):
    print("\n--- COL SECTION EXTRACTION ---")
    feedback = state.get("col_section_feedback", [])
    text = state["full_text"]
    jurisdiction = state.get("jurisdiction", "Civil-law jurisdiction")
    specific_jurisdiction = state.get("precise_jurisdiction")
    # Dynamically select the correct prompt
    COL_SECTION_PROMPT = get_prompt_module(jurisdiction, "col_section", specific_jurisdiction).COL_SECTION_PROMPT
    # add feedback info to logs if exists
    if feedback:
        print("\nFeedback for col section:", feedback, "\n")
    prompt = COL_SECTION_PROMPT.format(text=text)

    # ===== BUMP AND READ COUNTER =====
    iter_count = state.get("col_section_eval_iter", 0) + 1
    state["col_section_eval_iter"] = iter_count
    # ===== ADD EXISTING COL SECTION TO PROMPT =====
    existing_sections = state.get("col_section", [])
    if existing_sections:
        prev = existing_sections[-1]
        if prev:
            prompt += f"\n\nPrevious extraction: {prev}\n"

    # ===== ADD FEEDBACK TO PROMPT =====
    if feedback:
        last_fb = feedback[-1]
        prompt += f"\n\nFeedback: {last_fb}\n"
    print(f"\nPrompting LLM with:\n{prompt}\n")
    start_time = time.time()

    # Get dynamic system prompt based on jurisdiction
    system_prompt = get_system_prompt_for_analysis(state)

    response = config.llm.invoke([
        SystemMessage(content=system_prompt),
        HumanMessage(content=prompt)
    ])
    col_time = time.time() - start_time
    col_section = _coerce_to_text(getattr(response, "content", "")).strip()
    # append new extraction
    state.setdefault("col_section", []).append(col_section)
    print(f"\nExtracted Choice of Law section:\n{col_section}\n")

    # return full updated lists
    return {
        "col_section": state["col_section"],
        "col_section_feedback": state.get("col_section_feedback", []),
        "col_section_time": col_time
    }
