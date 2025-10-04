import json
import time
from collections.abc import Sequence
from typing import Any

from langchain_core.messages import HumanMessage, SystemMessage

import config
from prompts.prompt_selector import get_prompt_module
from utils.system_prompt_generator import get_system_prompt_for_analysis
from utils.themes_extractor import filter_themes_by_list


# Helper function to extract content from the last message in a list of messages
def _ensure_text(content: Any) -> str:
    if isinstance(content, str):
        return content
    if content is None:
        return ""
    if isinstance(content, list):
        return "\n".join(_ensure_text(item) for item in content if item is not None)
    if isinstance(content, dict):
        try:
            return json.dumps(content)
        except TypeError:
            return str(content)
    return str(content)


def _get_last_message_content(messages: Sequence[Any] | None) -> str:
    if messages:
        last_message = messages[-1]
        if hasattr(last_message, "content"):
            return _ensure_text(last_message.content)
    return ""


# Helper function to extract and format classification content
def _get_classification_content_str(messages: Sequence[Any] | None) -> str:
    if messages:
        last_message = messages[-1]
        if hasattr(last_message, "content"):
            raw_content = last_message.content
            if isinstance(raw_content, list):
                values = [str(item) for item in raw_content if isinstance(item, str) and item]
                if values:
                    return ", ".join(values)
            return _ensure_text(raw_content)
    return ""


# ===== RELEVANT FACTS =====
def relevant_facts(state):
    print("\n--- RELEVANT FACTS ---")
    text = state["full_text"]
    jurisdiction = state.get("jurisdiction", "Civil-law jurisdiction")
    specific_jurisdiction = state.get("precise_jurisdiction")
    FACTS_PROMPT = get_prompt_module(jurisdiction, "analysis", specific_jurisdiction).FACTS_PROMPT
    # get last col_section (string)
    col_section = ""
    sections = state.get("col_section", [])
    if sections:
        col_section = sections[-1]
    prompt = FACTS_PROMPT.format(text=text, col_section=col_section)
    print(f"\nPrompting LLM with:\n{prompt}\n")
    start_time = time.time()

    # Get dynamic system prompt based on jurisdiction
    system_prompt = get_system_prompt_for_analysis(state)

    response = config.llm.invoke([SystemMessage(content=system_prompt), HumanMessage(content=prompt)])
    facts_time = time.time() - start_time
    facts = _ensure_text(getattr(response, "content", ""))
    print(f"\nRelevant Facts:\n{facts}\n")
    # append relevant facts
    state.setdefault("relevant_facts", []).append(facts)
    # return full updated lists
    return {"relevant_facts": state["relevant_facts"], "relevant_facts_time": facts_time}


# ===== PIL PROVISIONS =====
def pil_provisions(state):
    print("\n--- PIL PROVISIONS ---")
    text = state["full_text"]
    jurisdiction = state.get("jurisdiction", "Civil-law jurisdiction")
    specific_jurisdiction = state.get("precise_jurisdiction")
    PIL_PROVISIONS_PROMPT = get_prompt_module(jurisdiction, "analysis", specific_jurisdiction).PIL_PROVISIONS_PROMPT
    # get last col_section (string)
    col_section = ""
    sections = state.get("col_section", [])
    if sections:
        col_section = sections[-1]
    prompt = PIL_PROVISIONS_PROMPT.format(text=text, col_section=col_section)
    print(f"\nPrompting LLM with:\n{prompt}\n")
    start_time = time.time()

    # Get dynamic system prompt based on jurisdiction
    system_prompt = get_system_prompt_for_analysis(state)

    response = config.llm.invoke([SystemMessage(content=system_prompt), HumanMessage(content=prompt)])
    provisions_time = time.time() - start_time
    raw_content = getattr(response, "content", "")
    content_str = _ensure_text(raw_content)
    try:
        pil_provisions = json.loads(content_str)
    except json.JSONDecodeError:
        print(f"Warning: Could not parse PIL provisions as JSON. Content: {content_str}")
        pil_provisions = [content_str.strip()]
    print(f"\nPIL Provisions:\n{pil_provisions}\n")
    # append pil_provisions
    state.setdefault("pil_provisions", []).append(pil_provisions)
    # return full updated lists
    return {"pil_provisions": state["pil_provisions"], "pil_provisions_time": provisions_time}


# ===== CHOICE OF LAW ISSUE =====
def col_issue(state):
    print("\n--- CHOICE OF LAW ISSUE ---")
    text = state["full_text"]
    jurisdiction = state.get("jurisdiction", "Civil-law jurisdiction")
    specific_jurisdiction = state.get("precise_jurisdiction")
    COL_ISSUE_PROMPT = get_prompt_module(jurisdiction, "analysis", specific_jurisdiction).COL_ISSUE_PROMPT
    # get last col_section (string)
    col_section = ""
    sections = state.get("col_section", [])
    if sections:
        col_section = sections[-1]
    classification_messages = state.get("classification", [])
    themes_list: list[str] = []
    if classification_messages:
        last_msg = classification_messages[-1]
        if hasattr(last_msg, "content"):
            content_value = last_msg.content
            if isinstance(content_value, list):
                themes_list = content_value
            elif isinstance(content_value, str) and content_value:
                themes_list = [content_value]
    print(f"\nThemes list for classification: {themes_list}\n")
    classification_definitions = filter_themes_by_list(themes_list)

    prompt = COL_ISSUE_PROMPT.format(text=text, col_section=col_section, classification_definitions=classification_definitions)
    print(f"\nPrompting LLM with:\n{prompt}\n")
    start_time = time.time()

    # Get dynamic system prompt based on jurisdiction
    system_prompt = get_system_prompt_for_analysis(state)

    response = config.llm.invoke([SystemMessage(content=system_prompt), HumanMessage(content=prompt)])
    issue_time = time.time() - start_time
    col_issue = _ensure_text(getattr(response, "content", ""))
    print(f"\nChoice of Law Issue:\n{col_issue}\n")
    # append col_issue
    state.setdefault("col_issue", []).append(col_issue)
    # return full updated lists
    return {"col_issue": state["col_issue"], "col_issue_time": issue_time}


# ===== COURT'S POSITION =====
def courts_position(state):
    print("\n--- COURT'S POSITION ---")
    text = state["full_text"]
    jurisdiction = state.get("jurisdiction", "Civil-law jurisdiction")
    specific_jurisdiction = state.get("precise_jurisdiction")
    COURTS_POSITION_PROMPT = get_prompt_module(jurisdiction, "analysis", specific_jurisdiction).COURTS_POSITION_PROMPT
    # get last col_section (string)
    col_section = ""
    sections = state.get("col_section", [])
    if sections:
        col_section = sections[-1]
    # get classification (string)
    classification = ""
    all_classifications = state.get("classification", [])
    if all_classifications:
        classification = all_classifications[-1]
    # get last col_issue (string)
    col_issue = ""
    all_col_issues = state.get("col_issue", [])
    if all_col_issues:
        col_issue = all_col_issues[-1]

    prompt = COURTS_POSITION_PROMPT.format(
        col_issue=col_issue, text=text, col_section=col_section, classification=classification
    )
    print(f"\nPrompting LLM with:\n{prompt}\n")
    start_time = time.time()

    # Get dynamic system prompt based on jurisdiction
    system_prompt = get_system_prompt_for_analysis(state)

    response = config.llm.invoke([SystemMessage(content=system_prompt), HumanMessage(content=prompt)])
    position_time = time.time() - start_time
    courts_position = _ensure_text(getattr(response, "content", ""))
    print(f"\nCourt's Position:\n{courts_position}\n")
    # append courts_position
    state.setdefault("courts_position", []).append(courts_position)
    # return full updated lists
    return {"courts_position": state["courts_position"], "courts_position_time": position_time}


def obiter_dicta(state):
    print("\n--- OBITER DICTA ---")
    text = state.get("full_text", "")
    jurisdiction = state.get("jurisdiction", "Civil-law jurisdiction")
    specific_jurisdiction = state.get("precise_jurisdiction")
    prompt_module = get_prompt_module(jurisdiction, "analysis", specific_jurisdiction)
    OBITER_PROMPT = prompt_module.COURTS_POSITION_OBITER_DICTA_PROMPT
    col_section = state.get("col_section", [""])[-1]
    classification = state.get("classification", [""])[-1]
    col_issue = state.get("col_issue", [""])[-1]
    prompt = OBITER_PROMPT.format(text=text, col_section=col_section, classification=classification, col_issue=col_issue)
    print(f"\nPrompting LLM for obiter dicta with:\n{prompt}\n")

    # Get dynamic system prompt based on jurisdiction
    system_prompt = get_system_prompt_for_analysis(state)

    response = config.llm.invoke([SystemMessage(content=system_prompt), HumanMessage(content=prompt)])
    obiter = _ensure_text(getattr(response, "content", ""))
    print(f"\nObiter Dicta:\n{obiter}\n")
    state.setdefault("obiter_dicta", []).append(obiter)
    return {"obiter_dicta": state["obiter_dicta"]}


def dissenting_opinions(state):
    print("\n--- DISSENTING OPINIONS ---")
    text = state.get("full_text", "")
    jurisdiction = state.get("jurisdiction", "Civil-law jurisdiction")
    specific_jurisdiction = state.get("precise_jurisdiction")
    prompt_module = get_prompt_module(jurisdiction, "analysis", specific_jurisdiction)
    DISSENT_PROMPT = prompt_module.COURTS_POSITION_DISSENTING_OPINIONS_PROMPT
    col_section = state.get("col_section", [""])[-1]
    classification = state.get("classification", [""])[-1]
    col_issue = state.get("col_issue", [""])[-1]
    prompt = DISSENT_PROMPT.format(text=text, col_section=col_section, classification=classification, col_issue=col_issue)
    print(f"\nPrompting LLM for dissenting opinions with:\n{prompt}\n")

    # Get dynamic system prompt based on jurisdiction
    system_prompt = get_system_prompt_for_analysis(state)

    response = config.llm.invoke([SystemMessage(content=system_prompt), HumanMessage(content=prompt)])
    dissent = _ensure_text(getattr(response, "content", ""))
    print(f"\nDissenting Opinions:\n{dissent}\n")
    state.setdefault("dissenting_opinions", []).append(dissent)
    return {"dissenting_opinions": state["dissenting_opinions"]}


# ===== ABSTRACT =====
def abstract(state):
    print("\n--- ABSTRACT ---")
    text = state["full_text"]
    jurisdiction = state.get("jurisdiction", "Civil-law jurisdiction")
    specific_jurisdiction = state.get("precise_jurisdiction")
    ABSTRACT_PROMPT = get_prompt_module(jurisdiction, "analysis", specific_jurisdiction).ABSTRACT_PROMPT

    # Get required variables for all jurisdictions
    classification = state.get("classification", [""])[-1] if state.get("classification") else ""
    facts = state.get("relevant_facts", [""])[-1] if state.get("relevant_facts") else ""
    pil_provisions = state.get("pil_provisions", [""])[-1] if state.get("pil_provisions") else ""
    col_issue = state.get("col_issue", [""])[-1] if state.get("col_issue") else ""
    court_position = state.get("courts_position", [""])[-1] if state.get("courts_position") else ""

    # Prepare base prompt variables
    prompt_vars = {
        "text": text,
        "classification": classification,
        "facts": facts,
        "pil_provisions": pil_provisions,
        "col_issue": col_issue,
        "court_position": court_position,
    }

    # Add common law / India specific variables if available
    if jurisdiction == "Common-law jurisdiction" or (specific_jurisdiction and specific_jurisdiction.lower() == "india"):
        obiter_dicta = state.get("obiter_dicta", [""])[-1] if state.get("obiter_dicta") else ""
        dissenting_opinions = state.get("dissenting_opinions", [""])[-1] if state.get("dissenting_opinions") else ""
        prompt_vars.update({"obiter_dicta": obiter_dicta, "dissenting_opinions": dissenting_opinions})

    prompt = ABSTRACT_PROMPT.format(**prompt_vars)
    print(f"\nPrompting LLM with:\n{prompt}\n")
    start_time = time.time()

    # Get dynamic system prompt based on jurisdiction
    system_prompt = get_system_prompt_for_analysis(state)

    response = config.llm.invoke([SystemMessage(content=system_prompt), HumanMessage(content=prompt)])
    abstract_time = time.time() - start_time
    abstract = _ensure_text(getattr(response, "content", ""))
    print(f"\nAbstract:\n{abstract}\n")
    # append abstract
    state.setdefault("abstract", []).append(abstract)
    # return full updated lists
    return {"abstract": state["abstract"], "abstract_time": abstract_time}
