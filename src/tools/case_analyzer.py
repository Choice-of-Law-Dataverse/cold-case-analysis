import asyncio
import json
import logging
import os
import time
from collections.abc import Sequence
from typing import Any

import logfire
from agents import Agent, Runner

from models.analysis_models import (
    AbstractOutput,
    ColIssueOutput,
    CourtsPositionOutput,
    DissentingOpinionsOutput,
    ObiterDictaOutput,
    PILProvisionsOutput,
    RelevantFactsOutput,
)
from prompts.prompt_selector import get_prompt_module
from utils.system_prompt_generator import get_system_prompt_for_analysis
from utils.themes_extractor import filter_themes_by_list

logger = logging.getLogger(__name__)


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


def relevant_facts(state):
    with logfire.span("extract_relevant_facts"):
        text = state["full_text"]
        jurisdiction = state.get("jurisdiction", "Civil-law jurisdiction")
        specific_jurisdiction = state.get("precise_jurisdiction")
        FACTS_PROMPT = get_prompt_module(jurisdiction, "analysis", specific_jurisdiction).FACTS_PROMPT

        col_section = ""
        sections = state.get("col_section", [])
        if sections:
            col_section = sections[-1]
        prompt = FACTS_PROMPT.format(text=text, col_section=col_section)
        logger.debug("Prompting agent with: %s", prompt)
        start_time = time.time()

        system_prompt = get_system_prompt_for_analysis(state)

        selected_model = state.get("model") or os.getenv("OPENAI_MODEL") or "gpt-5-nano"
        agent = Agent(
            name="RelevantFactsExtractor",
            instructions=system_prompt,
            output_type=RelevantFactsOutput,
            model=selected_model,
        )
        result = asyncio.run(Runner.run(agent, prompt)).final_output
        facts_time = time.time() - start_time
        facts = result.relevant_facts
        confidence = result.confidence
        reasoning = result.reasoning

        logger.debug("Relevant Facts: %s (confidence: %s)", facts, confidence)
        state.setdefault("relevant_facts", []).append(facts)
        state.setdefault("relevant_facts_confidence", []).append(confidence)
        state.setdefault("relevant_facts_reasoning", []).append(reasoning)

        logfire.info("Extracted relevant facts", chars=len(facts), time_seconds=facts_time, confidence=confidence)
        return {
            "relevant_facts": state["relevant_facts"],
            "relevant_facts_confidence": state["relevant_facts_confidence"],
            "relevant_facts_reasoning": state["relevant_facts_reasoning"],
        }


def pil_provisions(state):
    with logfire.span("extract_pil_provisions"):
        text = state["full_text"]
        jurisdiction = state.get("jurisdiction", "Civil-law jurisdiction")
        specific_jurisdiction = state.get("precise_jurisdiction")
        PIL_PROVISIONS_PROMPT = get_prompt_module(jurisdiction, "analysis", specific_jurisdiction).PIL_PROVISIONS_PROMPT

        col_section = ""
        sections = state.get("col_section", [])
        if sections:
            col_section = sections[-1]
        prompt = PIL_PROVISIONS_PROMPT.format(text=text, col_section=col_section)
        logger.debug("Prompting agent with: %s", prompt)
        start_time = time.time()

        system_prompt = get_system_prompt_for_analysis(state)

        selected_model = state.get("model") or os.getenv("OPENAI_MODEL") or "gpt-5-nano"
        agent = Agent(
            name="PILProvisionsExtractor",
            instructions=system_prompt,
            output_type=PILProvisionsOutput,
            model=selected_model,
        )
        result = asyncio.run(Runner.run(agent, prompt)).final_output
        provisions_time = time.time() - start_time
        pil_provisions = result.pil_provisions
        confidence = result.confidence
        reasoning = result.reasoning

        logger.debug("PIL Provisions: %s (confidence: %s)", pil_provisions, confidence)
        state.setdefault("pil_provisions", []).append(pil_provisions)
        state.setdefault("pil_provisions_confidence", []).append(confidence)
        state.setdefault("pil_provisions_reasoning", []).append(reasoning)

        logfire.info("Extracted PIL provisions", count=len(pil_provisions), time_seconds=provisions_time, confidence=confidence)
        return {
            "pil_provisions": state["pil_provisions"],
            "pil_provisions_confidence": state["pil_provisions_confidence"],
            "pil_provisions_reasoning": state["pil_provisions_reasoning"],
        }


def col_issue(state):
    with logfire.span("extract_col_issue"):
        text = state["full_text"]
        jurisdiction = state.get("jurisdiction", "Civil-law jurisdiction")
        specific_jurisdiction = state.get("precise_jurisdiction")
        COL_ISSUE_PROMPT = get_prompt_module(jurisdiction, "analysis", specific_jurisdiction).COL_ISSUE_PROMPT

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
        logger.debug("Themes list for classification: %s", themes_list)
        classification_definitions = filter_themes_by_list(themes_list)

        prompt = COL_ISSUE_PROMPT.format(
            text=text, col_section=col_section, classification_definitions=classification_definitions
        )
        logger.debug("Prompting agent with: %s", prompt)
        start_time = time.time()

        system_prompt = get_system_prompt_for_analysis(state)

        selected_model = state.get("model") or os.getenv("OPENAI_MODEL") or "gpt-5-nano"
        agent = Agent(
            name="ColIssueExtractor",
            instructions=system_prompt,
            output_type=ColIssueOutput,
            model=selected_model,
        )
        result = asyncio.run(Runner.run(agent, prompt)).final_output
        issue_time = time.time() - start_time
        col_issue_text = result.col_issue
        confidence = result.confidence
        reasoning = result.reasoning

        logger.debug("Choice of Law Issue: %s (confidence: %s)", col_issue_text, confidence)
        state.setdefault("col_issue", []).append(col_issue_text)
        state.setdefault("col_issue_confidence", []).append(confidence)
        state.setdefault("col_issue_reasoning", []).append(reasoning)

        logfire.info("Extracted CoL issue", chars=len(col_issue_text), time_seconds=issue_time, confidence=confidence)
        return {
            "col_issue": state["col_issue"],
            "col_issue_confidence": state["col_issue_confidence"],
            "col_issue_reasoning": state["col_issue_reasoning"],
        }


def courts_position(state):
    text = state["full_text"]
    jurisdiction = state.get("jurisdiction", "Civil-law jurisdiction")
    specific_jurisdiction = state.get("precise_jurisdiction")
    COURTS_POSITION_PROMPT = get_prompt_module(jurisdiction, "analysis", specific_jurisdiction).COURTS_POSITION_PROMPT

    col_section = ""
    sections = state.get("col_section", [])
    if sections:
        col_section = sections[-1]

    classification = ""
    all_classifications = state.get("classification", [])
    if all_classifications:
        classification = all_classifications[-1]

    col_issue = ""
    all_col_issues = state.get("col_issue", [])
    if all_col_issues:
        col_issue = all_col_issues[-1]

    prompt = COURTS_POSITION_PROMPT.format(
        col_issue=col_issue, text=text, col_section=col_section, classification=classification
    )
    logger.debug("Prompting agent with: %s", prompt)
    start_time = time.time()

    system_prompt = get_system_prompt_for_analysis(state)

    selected_model = state.get("model") or os.getenv("OPENAI_MODEL") or "gpt-5-nano"
    agent = Agent(
        name="CourtsPositionAnalyzer",
        instructions=system_prompt,
        output_type=CourtsPositionOutput,
        model=selected_model,
    )
    result = asyncio.run(Runner.run(agent, prompt)).final_output
    position_time = time.time() - start_time
    courts_position_text = result.courts_position
    confidence = result.confidence
    reasoning = result.reasoning

    logger.debug("Court's Position: %s (confidence: %s)", courts_position_text, confidence)
    state.setdefault("courts_position", []).append(courts_position_text)
    state.setdefault("courts_position_confidence", []).append(confidence)
    state.setdefault("courts_position_reasoning", []).append(reasoning)

    return {
        "courts_position": state["courts_position"],
        "courts_position_confidence": state["courts_position_confidence"],
        "courts_position_reasoning": state["courts_position_reasoning"],
    }


def obiter_dicta(state):
    text = state.get("full_text", "")
    jurisdiction = state.get("jurisdiction", "Civil-law jurisdiction")
    specific_jurisdiction = state.get("precise_jurisdiction")
    prompt_module = get_prompt_module(jurisdiction, "analysis", specific_jurisdiction)
    OBITER_PROMPT = prompt_module.COURTS_POSITION_OBITER_DICTA_PROMPT
    col_section = state.get("col_section", [""])[-1]
    classification = state.get("classification", [""])[-1]
    col_issue = state.get("col_issue", [""])[-1]
    prompt = OBITER_PROMPT.format(text=text, col_section=col_section, classification=classification, col_issue=col_issue)
    logger.debug("Prompting agent for obiter dicta with: %s", prompt)

    system_prompt = get_system_prompt_for_analysis(state)

    selected_model = state.get("model") or os.getenv("OPENAI_MODEL") or "gpt-5-nano"
    agent = Agent(
        name="ObiterDictaExtractor",
        instructions=system_prompt,
        output_type=ObiterDictaOutput,
        model=selected_model,
    )
    result = asyncio.run(Runner.run(agent, prompt)).final_output
    obiter = result.obiter_dicta
    confidence = result.confidence
    reasoning = result.reasoning

    logger.debug("Obiter Dicta: %s (confidence: %s)", obiter, confidence)
    state.setdefault("obiter_dicta", []).append(obiter)
    state.setdefault("obiter_dicta_confidence", []).append(confidence)
    state.setdefault("obiter_dicta_reasoning", []).append(reasoning)

    return {
        "obiter_dicta": state["obiter_dicta"],
        "obiter_dicta_confidence": state["obiter_dicta_confidence"],
        "obiter_dicta_reasoning": state["obiter_dicta_reasoning"],
    }


def dissenting_opinions(state):
    text = state.get("full_text", "")
    jurisdiction = state.get("jurisdiction", "Civil-law jurisdiction")
    specific_jurisdiction = state.get("precise_jurisdiction")
    prompt_module = get_prompt_module(jurisdiction, "analysis", specific_jurisdiction)
    DISSENT_PROMPT = prompt_module.COURTS_POSITION_DISSENTING_OPINIONS_PROMPT
    col_section = state.get("col_section", [""])[-1]
    classification = state.get("classification", [""])[-1]
    col_issue = state.get("col_issue", [""])[-1]
    prompt = DISSENT_PROMPT.format(text=text, col_section=col_section, classification=classification, col_issue=col_issue)
    logger.debug("Prompting agent for dissenting opinions with: %s", prompt)

    system_prompt = get_system_prompt_for_analysis(state)

    selected_model = state.get("model") or os.getenv("OPENAI_MODEL") or "gpt-5-nano"
    agent = Agent(
        name="DissentingOpinionsExtractor",
        instructions=system_prompt,
        output_type=DissentingOpinionsOutput,
        model=selected_model,
    )
    result = asyncio.run(Runner.run(agent, prompt)).final_output
    dissent = result.dissenting_opinions
    confidence = result.confidence
    reasoning = result.reasoning

    logger.debug("Dissenting Opinions: %s (confidence: %s)", dissent, confidence)
    state.setdefault("dissenting_opinions", []).append(dissent)
    state.setdefault("dissenting_opinions_confidence", []).append(confidence)
    state.setdefault("dissenting_opinions_reasoning", []).append(reasoning)

    return {
        "dissenting_opinions": state["dissenting_opinions"],
        "dissenting_opinions_confidence": state["dissenting_opinions_confidence"],
        "dissenting_opinions_reasoning": state["dissenting_opinions_reasoning"],
    }


def abstract(state):
    with logfire.span("generate_abstract"):
        text = state["full_text"]
        jurisdiction = state.get("jurisdiction", "Civil-law jurisdiction")
        specific_jurisdiction = state.get("precise_jurisdiction")
        ABSTRACT_PROMPT = get_prompt_module(jurisdiction, "analysis", specific_jurisdiction).ABSTRACT_PROMPT

        classification = state.get("classification", [""])[-1] if state.get("classification") else ""
        facts = state.get("relevant_facts", [""])[-1] if state.get("relevant_facts") else ""
        pil_provisions = state.get("pil_provisions", [""])[-1] if state.get("pil_provisions") else ""
        col_issue = state.get("col_issue", [""])[-1] if state.get("col_issue") else ""
        court_position = state.get("courts_position", [""])[-1] if state.get("courts_position") else ""

        prompt_vars = {
            "text": text,
            "classification": classification,
            "facts": facts,
            "pil_provisions": pil_provisions,
            "col_issue": col_issue,
            "court_position": court_position,
        }

        if jurisdiction == "Common-law jurisdiction" or (specific_jurisdiction and specific_jurisdiction.lower() == "india"):
            obiter_dicta = state.get("obiter_dicta", [""])[-1] if state.get("obiter_dicta") else ""
            dissenting_opinions = state.get("dissenting_opinions", [""])[-1] if state.get("dissenting_opinions") else ""
            prompt_vars.update({"obiter_dicta": obiter_dicta, "dissenting_opinions": dissenting_opinions})

        prompt = ABSTRACT_PROMPT.format(**prompt_vars)
        logger.debug("Prompting agent with: %s", prompt)
        start_time = time.time()

        system_prompt = get_system_prompt_for_analysis(state)

        selected_model = state.get("model") or os.getenv("OPENAI_MODEL") or "gpt-5-nano"
        agent = Agent(
            name="AbstractGenerator",
            instructions=system_prompt,
            output_type=AbstractOutput,
            model=selected_model,
        )
        result = asyncio.run(Runner.run(agent, prompt)).final_output
        abstract_time = time.time() - start_time
        abstract_text = result.abstract
        confidence = result.confidence
        reasoning = result.reasoning

        logger.debug("Abstract: %s (confidence: %s)", abstract_text, confidence)
        state.setdefault("abstract", []).append(abstract_text)
        state.setdefault("abstract_confidence", []).append(confidence)
        state.setdefault("abstract_reasoning", []).append(reasoning)

        logfire.info("Generated abstract", chars=len(abstract_text), time_seconds=abstract_time, confidence=confidence)
        return {
            "abstract": state["abstract"],
            "abstract_confidence": state["abstract_confidence"],
            "abstract_reasoning": state["abstract_reasoning"],
        }
