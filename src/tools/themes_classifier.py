import csv
import json
import time
from pathlib import Path

from langchain_core.messages import HumanMessage, SystemMessage

import config
from prompts.prompt_selector import get_prompt_module
from utils.system_prompt_generator import get_system_prompt_for_analysis
from utils.themes_extractor import THEMES_TABLE_STR


def theme_classification_node(state):
    print("\n--- THEME CLASSIFICATION ---")
    text = state["full_text"]
    jurisdiction = state.get("jurisdiction", "Civil-law jurisdiction")
    specific_jurisdiction = state.get("precise_jurisdiction")
    # Dynamically select the correct prompt
    PIL_THEME_PROMPT = get_prompt_module(jurisdiction, "theme", specific_jurisdiction).PIL_THEME_PROMPT
    # get last col_section (string)
    col_section = ""
    sections = state.get("col_section", [])
    if sections:
        col_section = sections[-1]
    # bump iteration counter
    iter_count = state.get("theme_eval_iter", 0) + 1
    state["theme_eval_iter"] = iter_count
    # build prompt
    prompt = PIL_THEME_PROMPT.format(text=text, col_section=col_section, themes_table=THEMES_TABLE_STR)
    # add previous classification if exists
    existing = state.get("classification", [])
    if existing:
        prev = existing[-1]
        if prev:
            prompt += f"\n\nPrevious classification: {prev}\n"
    # load valid themes from CSV
    themes_path = Path(__file__).parents[1] / "data" / "themes.csv"
    valid_themes = set()
    with open(themes_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            valid_themes.add(row["Theme"])
    # attempt classification up to 5 times ensuring valid themes
    max_attempts = 5
    for attempt in range(1, max_attempts + 1):
        print(f"\nPrompting LLM (attempt {attempt}/{max_attempts}) with:\n{prompt}\n")
        start_time = time.time()

        # Get dynamic system prompt based on jurisdiction
        system_prompt = get_system_prompt_for_analysis(state)

        response = config.llm.invoke([
            SystemMessage(content=system_prompt),
            HumanMessage(content=prompt)
        ])
        theme_time = time.time() - start_time
        # parse classification list
        try:
            cls_list = json.loads(response.content)
        except Exception:
            cls_list = [response.content.strip()]
        # validate returned themes
        invalid = [item for item in cls_list if item not in valid_themes]
        if not invalid:
            break
        print(f"Invalid themes returned: {invalid}. Retrying...\n")
    else:
        print(f"Max attempts reached. Proceeding with last classification: {cls_list}\n")
    # convert to string for display
    cls_str = ", ".join(str(item) for item in cls_list)
    print(f"\nClassified theme(s): {cls_list}\n")
    # append classification
    state.setdefault("classification", []).append(cls_str)
    # return updated lists
    return {
        "classification": state["classification"],
        "theme_feedback": state.get("theme_feedback", []),
        "theme_classification_time": theme_time
    }
