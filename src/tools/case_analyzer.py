import asyncio
import logging
from collections.abc import Generator
from concurrent.futures import ThreadPoolExecutor, as_completed
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
from utils.system_prompt_generator import generate_system_prompt
from utils.themes_extractor import filter_themes_by_list

logger = logging.getLogger(__name__)


def extract_relevant_facts(
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
        system_prompt = generate_system_prompt(jurisdiction, specific_jurisdiction, "analysis")

        agent = Agent(
            name="RelevantFactsExtractor",
            instructions=system_prompt,
            output_type=RelevantFactsOutput,
            model=model,
        )
        result = asyncio.run(Runner.run(agent, prompt)).final_output_as(RelevantFactsOutput)

        logfire.info(
            "Extracted relevant facts",
            text_length=len(text),
            col_section_length=len(col_section),
            result_length=len(result.relevant_facts),
            confidence=result.confidence,
        )
        return result


def extract_pil_provisions(
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
        system_prompt = generate_system_prompt(jurisdiction, specific_jurisdiction, "analysis")

        agent = Agent(
            name="PILProvisionsExtractor",
            instructions=system_prompt,
            output_type=PILProvisionsOutput,
            model=model,
        )
        result = asyncio.run(Runner.run(agent, prompt)).final_output_as(PILProvisionsOutput)

        logfire.info(
            "Extracted PIL provisions",
            text_length=len(text),
            col_section_length=len(col_section),
            provisions_count=len(result.pil_provisions),
            confidence=result.confidence,
        )
        return result


def extract_col_issue(
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
        system_prompt = generate_system_prompt(jurisdiction, specific_jurisdiction, "analysis")

        agent = Agent(
            name="ColIssueExtractor",
            instructions=system_prompt,
            output_type=ColIssueOutput,
            model=model,
        )
        result = asyncio.run(Runner.run(agent, prompt)).final_output_as(ColIssueOutput)

        logfire.info(
            "Extracted CoL issue",
            text_length=len(text),
            col_section_length=len(col_section),
            themes_count=len(classification_themes),
            result_length=len(result.col_issue),
            confidence=result.confidence,
        )
        return result


def extract_courts_position(
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
    system_prompt = generate_system_prompt(jurisdiction, specific_jurisdiction, "analysis")

    agent = Agent(
        name="CourtsPositionAnalyzer",
        instructions=system_prompt,
        output_type=CourtsPositionOutput,
        model=model,
    )
    result = asyncio.run(Runner.run(agent, prompt)).final_output_as(CourtsPositionOutput)

    return result


def extract_obiter_dicta(
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
    system_prompt = generate_system_prompt(jurisdiction, specific_jurisdiction, "analysis")

    agent = Agent(
        name="ObiterDictaExtractor",
        instructions=system_prompt,
        output_type=ObiterDictaOutput,
        model=model,
    )
    result = asyncio.run(Runner.run(agent, prompt)).final_output_as(ObiterDictaOutput)

    return result


def extract_dissenting_opinions(
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
    system_prompt = generate_system_prompt(jurisdiction, specific_jurisdiction, "analysis")

    agent = Agent(
        name="DissentingOpinionsExtractor",
        instructions=system_prompt,
        output_type=DissentingOpinionsOutput,
        model=model,
    )
    result = asyncio.run(Runner.run(agent, prompt)).final_output_as(DissentingOpinionsOutput)

    return result


def extract_abstract(
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
        system_prompt = generate_system_prompt(jurisdiction, specific_jurisdiction, "analysis")

        agent = Agent(
            name="AbstractGenerator",
            instructions=system_prompt,
            output_type=AbstractOutput,
            model=model,
        )
        result = asyncio.run(Runner.run(agent, prompt)).final_output_as(AbstractOutput)

        logfire.info(
            "Generated abstract",
            text_length=len(text),
            result_length=len(result.abstract),
            confidence=result.confidence,
        )
        return result


def analyze_case_workflow(
    text: str,
    jurisdiction: str,
    specific_jurisdiction: str | None,
    model: str,
    col_section: str | None = None,
    themes: list[str] | None = None,
) -> Generator[Any, None, None]:
    """
    Execute complete case analysis workflow with parallel execution where possible.

    This generator orchestrates all analysis steps and yields intermediate results.
    The component should consume these yields and update the UI/state accordingly.

    Args:
        text: Full court decision text
        jurisdiction: Legal system type (e.g., "Civil-law jurisdiction")
        specific_jurisdiction: Precise jurisdiction (e.g., "Switzerland")
        model: Model to use for analysis
        col_section: Pre-extracted Choice of Law section (optional)
        themes: Pre-classified themes (optional)

    Yields:
        Output objects for each completed step:
            - ColSectionOutput
            - ThemeClassificationOutput
            - RelevantFactsOutput
            - PILProvisionsOutput
            - ColIssueOutput
            - CourtsPositionOutput
            - ObiterDictaOutput (Common Law only)
            - DissentingOpinionsOutput (Common Law only)
            - AbstractOutput
    """
    with logfire.span("analyze_case_workflow"):
        # Step 1: Extract CoL section if not provided
        if not col_section:
            from tools.col_extractor import extract_col_section

            result = extract_col_section(
                text=text,
                jurisdiction=jurisdiction,
                specific_jurisdiction=specific_jurisdiction,
                model=model,
                feedback=None,
                previous_section=None,
                iteration=1,
            )
            col_section = result.col_section
            yield result

        # Step 2: Classify themes if not provided
        if not themes:
            from tools.themes_classifier import theme_classification_node

            result = theme_classification_node(
                text=text,
                col_section=col_section,
                jurisdiction=jurisdiction,
                specific_jurisdiction=specific_jurisdiction,
                model=model,
                previous_classification=None,
                iteration=1,
            )
            themes = result.themes
            yield result

        # Step 3: Run parallel analysis (relevant facts + PIL provisions)
        parallel_results = {}
        with ThreadPoolExecutor(max_workers=2) as executor:
            futures = {
                executor.submit(
                    extract_relevant_facts,
                    text,
                    col_section,
                    jurisdiction,
                    specific_jurisdiction,
                    model,
                ): "relevant_facts",
                executor.submit(
                    extract_pil_provisions,
                    text,
                    col_section,
                    jurisdiction,
                    specific_jurisdiction,
                    model,
                ): "pil_provisions",
            }

            for future in as_completed(futures):
                step_name = futures[future]
                try:
                    result = future.result()
                    parallel_results[step_name] = result
                    yield result
                except Exception as e:
                    logger.error(f"Error in parallel step {step_name}: {e}")
                    raise

        # Step 4: Extract CoL issue (depends on themes)
        themes_list = themes if isinstance(themes, list) else [t.strip() for t in str(themes).split(",")]
        result = extract_col_issue(
            text=text,
            col_section=col_section,
            jurisdiction=jurisdiction,
            specific_jurisdiction=specific_jurisdiction,
            model=model,
            classification_themes=themes_list,
        )
        col_issue_text = result.col_issue
        yield result

        # Step 5: Extract court's position (sequential, depends on col_issue)
        classification_str = ", ".join(themes_list) if isinstance(themes_list, list) else str(themes_list)
        result = extract_courts_position(
            text=text,
            col_section=col_section,
            jurisdiction=jurisdiction,
            specific_jurisdiction=specific_jurisdiction,
            model=model,
            classification=classification_str,
            col_issue=col_issue_text,
        )
        courts_position_text = result.courts_position
        yield result

        # Step 6: Common Law specific steps (obiter dicta + dissenting opinions)
        obiter_dicta_text = ""
        dissenting_opinions_text = ""
        if jurisdiction == "Common-law jurisdiction":
            result = extract_obiter_dicta(
                text=text,
                col_section=col_section,
                jurisdiction=jurisdiction,
                specific_jurisdiction=specific_jurisdiction,
                model=model,
                classification=classification_str,
                col_issue=col_issue_text,
            )
            obiter_dicta_text = result.obiter_dicta
            yield result

            result = extract_dissenting_opinions(
                text=text,
                col_section=col_section,
                jurisdiction=jurisdiction,
                specific_jurisdiction=specific_jurisdiction,
                model=model,
                classification=classification_str,
                col_issue=col_issue_text,
            )
            dissenting_opinions_text = result.dissenting_opinions
            yield result

        # Step 7: Generate abstract (final step, depends on all previous steps)
        facts = parallel_results.get("relevant_facts", "")
        if hasattr(facts, "relevant_facts"):
            facts = facts.relevant_facts

        pil_provisions_data = parallel_results.get("pil_provisions", "")
        if hasattr(pil_provisions_data, "pil_provisions"):
            pil_provisions_data = pil_provisions_data.pil_provisions

        result = extract_abstract(
            text=text,
            jurisdiction=jurisdiction,
            specific_jurisdiction=specific_jurisdiction,
            model=model,
            classification=classification_str,
            facts=str(facts),
            pil_provisions=str(pil_provisions_data),
            col_issue=col_issue_text,
            court_position=courts_position_text,
            obiter_dicta=obiter_dicta_text,
            dissenting_opinions=dissenting_opinions_text,
        )
        yield result
