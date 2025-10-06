import asyncio
import json
import logging
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


def relevant_facts(
    text: str,
    col_section: str,
    jurisdiction: str,
    specific_jurisdiction: str | None,
    model: str,
):
    """
    Extract relevant facts from court decision.

    Args:
        text: Full court decision text
        col_section: Choice of Law section text
        jurisdiction: Legal system type (e.g., "Civil-law jurisdiction")
        specific_jurisdiction: Precise jurisdiction (e.g., "Switzerland")
        model: Model to use for extraction

    Returns:
        RelevantFactsOutput: Extracted facts with confidence and reasoning
    """
    with logfire.span("extract_relevant_facts"):
        FACTS_PROMPT = get_prompt_module(jurisdiction, "analysis", specific_jurisdiction).FACTS_PROMPT

        prompt = FACTS_PROMPT.format(text=text, col_section=col_section)
        logger.debug("Prompting agent with: %s", prompt)
        start_time = time.time()

        # Create system prompt from parameters
        from utils.system_prompt_generator import generate_system_prompt
        system_prompt = generate_system_prompt(jurisdiction, specific_jurisdiction, "analysis")

        agent = Agent(
            name="RelevantFactsExtractor",
            instructions=system_prompt,
            output_type=RelevantFactsOutput,
            model=model,
        )
        result = asyncio.run(Runner.run(agent, prompt)).final_output
        facts_time = time.time() - start_time
        facts = result.relevant_facts
        confidence = result.confidence
        reasoning = result.reasoning

        logger.debug("Relevant Facts: %s (confidence: %s)", facts, confidence)

        logfire.info("Extracted relevant facts", chars=len(facts), time_seconds=facts_time, confidence=confidence)
        return result


def pil_provisions(
    text: str,
    col_section: str,
    jurisdiction: str,
    specific_jurisdiction: str | None,
    model: str,
):
    """
    Extract PIL provisions from court decision.

    Args:
        text: Full court decision text
        col_section: Choice of Law section text
        jurisdiction: Legal system type (e.g., "Civil-law jurisdiction")
        specific_jurisdiction: Precise jurisdiction (e.g., "Switzerland")
        model: Model to use for extraction

    Returns:
        PILProvisionsOutput: Extracted provisions with confidence and reasoning
    """
    with logfire.span("extract_pil_provisions"):
        PIL_PROVISIONS_PROMPT = get_prompt_module(jurisdiction, "analysis", specific_jurisdiction).PIL_PROVISIONS_PROMPT

        prompt = PIL_PROVISIONS_PROMPT.format(text=text, col_section=col_section)
        logger.debug("Prompting agent with: %s", prompt)
        start_time = time.time()

        # Create system prompt from parameters
        from utils.system_prompt_generator import generate_system_prompt
        system_prompt = generate_system_prompt(jurisdiction, specific_jurisdiction, "analysis")

        agent = Agent(
            name="PILProvisionsExtractor",
            instructions=system_prompt,
            output_type=PILProvisionsOutput,
            model=model,
        )
        result = asyncio.run(Runner.run(agent, prompt)).final_output
        provisions_time = time.time() - start_time
        pil_provisions = result.pil_provisions
        confidence = result.confidence
        reasoning = result.reasoning

        logger.debug("PIL Provisions: %s (confidence: %s)", pil_provisions, confidence)

        logfire.info("Extracted PIL provisions", count=len(pil_provisions), time_seconds=provisions_time, confidence=confidence)
        return result


def col_issue(
    text: str,
    col_section: str,
    jurisdiction: str,
    specific_jurisdiction: str | None,
    model: str,
    classification_themes: list[str],
):
    """
    Extract Choice of Law issue from court decision.

    Args:
        text: Full court decision text
        col_section: Choice of Law section text
        jurisdiction: Legal system type (e.g., "Civil-law jurisdiction")
        specific_jurisdiction: Precise jurisdiction (e.g., "Switzerland")
        model: Model to use for extraction
        classification_themes: List of classified themes

    Returns:
        ColIssueOutput: Extracted issue with confidence and reasoning
    """
    with logfire.span("extract_col_issue"):
        COL_ISSUE_PROMPT = get_prompt_module(jurisdiction, "analysis", specific_jurisdiction).COL_ISSUE_PROMPT

        classification_definitions = filter_themes_by_list(classification_themes)

        prompt = COL_ISSUE_PROMPT.format(
            text=text, col_section=col_section, classification_definitions=classification_definitions
        )
        logger.debug("Prompting agent with: %s", prompt)
        start_time = time.time()

        # Create system prompt from parameters
        from utils.system_prompt_generator import generate_system_prompt
        system_prompt = generate_system_prompt(jurisdiction, specific_jurisdiction, "analysis")

        agent = Agent(
            name="ColIssueExtractor",
            instructions=system_prompt,
            output_type=ColIssueOutput,
            model=model,
        )
        result = asyncio.run(Runner.run(agent, prompt)).final_output
        issue_time = time.time() - start_time
        col_issue_text = result.col_issue
        confidence = result.confidence
        reasoning = result.reasoning

        logger.debug("Choice of Law Issue: %s (confidence: %s)", col_issue_text, confidence)

        logfire.info("Extracted CoL issue", chars=len(col_issue_text), time_seconds=issue_time, confidence=confidence)
        return result


def courts_position(
    text: str,
    col_section: str,
    jurisdiction: str,
    specific_jurisdiction: str | None,
    model: str,
    classification: str,
    col_issue: str,
):
    """
    Extract court's position from court decision.

    Args:
        text: Full court decision text
        col_section: Choice of Law section text
        jurisdiction: Legal system type (e.g., "Civil-law jurisdiction")
        specific_jurisdiction: Precise jurisdiction (e.g., "Switzerland")
        model: Model to use for extraction
        classification: Classified themes
        col_issue: Choice of Law issue

    Returns:
        CourtsPositionOutput: Extracted position with confidence and reasoning
    """
    COURTS_POSITION_PROMPT = get_prompt_module(jurisdiction, "analysis", specific_jurisdiction).COURTS_POSITION_PROMPT

    prompt = COURTS_POSITION_PROMPT.format(
        col_issue=col_issue, text=text, col_section=col_section, classification=classification
    )
    logger.debug("Prompting agent with: %s", prompt)

    # Create system prompt from parameters
    from utils.system_prompt_generator import generate_system_prompt
    system_prompt = generate_system_prompt(jurisdiction, specific_jurisdiction, "analysis")

    agent = Agent(
        name="CourtsPositionAnalyzer",
        instructions=system_prompt,
        output_type=CourtsPositionOutput,
        model=model,
    )
    result = asyncio.run(Runner.run(agent, prompt)).final_output
    courts_position_text = result.courts_position
    confidence = result.confidence
    reasoning = result.reasoning

    logger.debug("Court's Position: %s (confidence: %s)", courts_position_text, confidence)

    return result


def obiter_dicta(
    text: str,
    col_section: str,
    jurisdiction: str,
    specific_jurisdiction: str | None,
    model: str,
    classification: str,
    col_issue: str,
):
    """
    Extract obiter dicta from court decision.

    Args:
        text: Full court decision text
        col_section: Choice of Law section text
        jurisdiction: Legal system type (e.g., "Civil-law jurisdiction")
        specific_jurisdiction: Precise jurisdiction (e.g., "Switzerland")
        model: Model to use for extraction
        classification: Classified themes
        col_issue: Choice of Law issue

    Returns:
        ObiterDictaOutput: Extracted obiter dicta with confidence and reasoning
    """
    prompt_module = get_prompt_module(jurisdiction, "analysis", specific_jurisdiction)
    OBITER_PROMPT = prompt_module.COURTS_POSITION_OBITER_DICTA_PROMPT
    prompt = OBITER_PROMPT.format(text=text, col_section=col_section, classification=classification, col_issue=col_issue)
    logger.debug("Prompting agent for obiter dicta with: %s", prompt)

    # Create system prompt from parameters
    from utils.system_prompt_generator import generate_system_prompt
    system_prompt = generate_system_prompt(jurisdiction, specific_jurisdiction, "analysis")

    agent = Agent(
        name="ObiterDictaExtractor",
        instructions=system_prompt,
        output_type=ObiterDictaOutput,
        model=model,
    )
    result = asyncio.run(Runner.run(agent, prompt)).final_output
    obiter = result.obiter_dicta
    confidence = result.confidence
    reasoning = result.reasoning

    logger.debug("Obiter Dicta: %s (confidence: %s)", obiter, confidence)

    return result


def dissenting_opinions(
    text: str,
    col_section: str,
    jurisdiction: str,
    specific_jurisdiction: str | None,
    model: str,
    classification: str,
    col_issue: str,
):
    """
    Extract dissenting opinions from court decision.

    Args:
        text: Full court decision text
        col_section: Choice of Law section text
        jurisdiction: Legal system type (e.g., "Civil-law jurisdiction")
        specific_jurisdiction: Precise jurisdiction (e.g., "Switzerland")
        model: Model to use for extraction
        classification: Classified themes
        col_issue: Choice of Law issue

    Returns:
        DissentingOpinionsOutput: Extracted opinions with confidence and reasoning
    """
    prompt_module = get_prompt_module(jurisdiction, "analysis", specific_jurisdiction)
    DISSENT_PROMPT = prompt_module.COURTS_POSITION_DISSENTING_OPINIONS_PROMPT
    prompt = DISSENT_PROMPT.format(text=text, col_section=col_section, classification=classification, col_issue=col_issue)
    logger.debug("Prompting agent for dissenting opinions with: %s", prompt)

    # Create system prompt from parameters
    from utils.system_prompt_generator import generate_system_prompt
    system_prompt = generate_system_prompt(jurisdiction, specific_jurisdiction, "analysis")

    agent = Agent(
        name="DissentingOpinionsExtractor",
        instructions=system_prompt,
        output_type=DissentingOpinionsOutput,
        model=model,
    )
    result = asyncio.run(Runner.run(agent, prompt)).final_output
    dissent = result.dissenting_opinions
    confidence = result.confidence
    reasoning = result.reasoning

    logger.debug("Dissenting Opinions: %s (confidence: %s)", dissent, confidence)

    return result


def abstract(
    text: str,
    jurisdiction: str,
    specific_jurisdiction: str | None,
    model: str,
    classification: str,
    facts: str,
    pil_provisions: str,
    col_issue: str,
    court_position: str,
    obiter_dicta: str = "",
    dissenting_opinions: str = "",
):
    """
    Generate abstract from court decision analysis.

    Args:
        text: Full court decision text
        jurisdiction: Legal system type (e.g., "Civil-law jurisdiction")
        specific_jurisdiction: Precise jurisdiction (e.g., "Switzerland")
        model: Model to use for generation
        classification: Classified themes
        facts: Relevant facts
        pil_provisions: PIL provisions
        col_issue: Choice of Law issue
        court_position: Court's position
        obiter_dicta: Obiter dicta (for Common Law jurisdictions)
        dissenting_opinions: Dissenting opinions (for Common Law jurisdictions)

    Returns:
        AbstractOutput: Generated abstract with confidence and reasoning
    """
    with logfire.span("generate_abstract"):
        ABSTRACT_PROMPT = get_prompt_module(jurisdiction, "analysis", specific_jurisdiction).ABSTRACT_PROMPT

        prompt_vars = {
            "text": text,
            "classification": classification,
            "facts": facts,
            "pil_provisions": pil_provisions,
            "col_issue": col_issue,
            "court_position": court_position,
        }

        if jurisdiction == "Common-law jurisdiction" or (specific_jurisdiction and specific_jurisdiction.lower() == "india"):
            prompt_vars.update({"obiter_dicta": obiter_dicta, "dissenting_opinions": dissenting_opinions})

        prompt = ABSTRACT_PROMPT.format(**prompt_vars)
        logger.debug("Prompting agent with: %s", prompt)
        start_time = time.time()

        # Create system prompt from parameters
        from utils.system_prompt_generator import generate_system_prompt
        system_prompt = generate_system_prompt(jurisdiction, specific_jurisdiction, "analysis")

        agent = Agent(
            name="AbstractGenerator",
            instructions=system_prompt,
            output_type=AbstractOutput,
            model=model,
        )
        result = asyncio.run(Runner.run(agent, prompt)).final_output
        abstract_time = time.time() - start_time
        abstract_text = result.abstract
        confidence = result.confidence
        reasoning = result.reasoning

        logger.debug("Abstract: %s (confidence: %s)", abstract_text, confidence)

        logfire.info("Generated abstract", chars=len(abstract_text), time_seconds=abstract_time, confidence=confidence)
        return result
