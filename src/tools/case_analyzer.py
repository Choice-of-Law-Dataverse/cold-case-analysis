import logging
from collections.abc import Generator
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any

import logfire

from models.analysis_models import (
    CourtsPositionOutput,
    DissentingOpinionsOutput,
    ObiterDictaOutput,
    PILProvisionsOutput,
    RelevantFactsOutput,
)
from tools.abstract_generator import extract_abstract
from tools.col_extractor import extract_col_section
from tools.col_issue_extractor import extract_col_issue
from tools.courts_position_extractor import extract_courts_position
from tools.dissenting_opinions_extractor import extract_dissenting_opinions
from tools.obiter_dicta_extractor import extract_obiter_dicta
from tools.pil_provisions_extractor import extract_pil_provisions
from tools.relevant_facts_extractor import extract_relevant_facts
from tools.theme_classifier import theme_classification_node

logger = logging.getLogger(__name__)


def analyze_case_workflow(
    text: str,
    legal_system: str,
    jurisdiction: str | None,
    model: str,
    col_sections: list[str] | None = None,
    themes: list[str] | None = None,
) -> Generator[Any, None, None]:
    """
    Execute complete case analysis workflow with parallel execution where possible.

    This generator orchestrates all analysis steps and yields intermediate results.
    The component should consume these yields and update the UI/state accordingly.

    Parallel execution phases:
    1. Relevant facts + PIL provisions (Step 3)
    2. Court's position + obiter dicta + dissenting opinions (Step 5)

    Args:
        text: Full court decision text
        legal_system: Legal system type (e.g., "Civil-law jurisdiction")
        jurisdiction: Precise jurisdiction (e.g., "Switzerland")
        model: Model to use for analysis
        col_sections: Pre-extracted Choice of Law sections (optional)
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
        # Step 1: Extract CoL sections if not provided
        col_section_text = ""
        if not col_sections:
            result = extract_col_section(
                text=text,
                legal_system=legal_system,
                jurisdiction=jurisdiction,
                model=model,
            )
            col_sections = result.col_sections
            col_section_text = "\n\n".join(col_sections)
            yield result
        else:
            col_section_text = "\n\n".join(col_sections) if isinstance(col_sections, list) else str(col_sections)

        # Step 2: Classify themes if not provided
        if not themes:
            result = theme_classification_node(
                text=text,
                col_section=col_section_text,
                legal_system=legal_system,
                jurisdiction=jurisdiction,
                model=model,
            )
            themes = [str(theme) for theme in result.themes]
            yield result

        # Step 3: Run parallel analysis (relevant facts + PIL provisions)
        parallel_results = {}
        with ThreadPoolExecutor(max_workers=2) as executor:
            futures = {
                executor.submit(
                    extract_relevant_facts,
                    text,
                    col_section_text,
                    legal_system,
                    jurisdiction,
                    model,
                ): "relevant_facts",
                executor.submit(
                    extract_pil_provisions,
                    text,
                    col_section_text,
                    legal_system,
                    jurisdiction,
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
            col_section=col_section_text,
            legal_system=legal_system,
            jurisdiction=jurisdiction,
            model=model,
            themes=themes_list,
        )
        col_issue_text = result.col_issue
        yield result

        # Step 5: Run parallel analysis (court's position + common law specific steps)
        themes_str = ", ".join(themes_list) if isinstance(themes_list, list) else str(themes_list)
        courts_position_text = ""
        obiter_dicta_text = ""
        dissenting_opinions_text = ""

        # Determine which extractions to run in parallel
        futures = []
        with ThreadPoolExecutor(max_workers=3) as executor:
            # Always extract court's position
            courts_future = executor.submit(
                extract_courts_position,
                text,
                col_section_text,
                legal_system,
                jurisdiction,
                model,
                themes_str,
                col_issue_text,
            )
            futures.append(courts_future)

            # Add Common Law specific extractions if applicable
            if legal_system == "Common-law jurisdiction":
                obiter_future = executor.submit(
                    extract_obiter_dicta,
                    text,
                    col_section_text,
                    legal_system,
                    jurisdiction,
                    model,
                    themes_str,
                    col_issue_text,
                )
                futures.append(obiter_future)

                dissent_future = executor.submit(
                    extract_dissenting_opinions,
                    text,
                    col_section_text,
                    legal_system,
                    jurisdiction,
                    model,
                    themes_str,
                    col_issue_text,
                )
                futures.append(dissent_future)

            # Collect results as they complete
            for future in as_completed(futures):
                result = future.result()
                if isinstance(result, CourtsPositionOutput):
                    courts_position_text = result.courts_position
                elif isinstance(result, ObiterDictaOutput):
                    obiter_dicta_text = result.obiter_dicta
                elif isinstance(result, DissentingOpinionsOutput):
                    dissenting_opinions_text = result.dissenting_opinions
                yield result

        # Step 6: Generate abstract (final step, depends on all previous steps)
        facts = parallel_results.get("relevant_facts", "")
        if isinstance(facts, RelevantFactsOutput):
            facts = facts.relevant_facts

        pil_provisions_data = parallel_results.get("pil_provisions", "")
        if isinstance(pil_provisions_data, PILProvisionsOutput):
            pil_provisions_data = pil_provisions_data.pil_provisions

        result = extract_abstract(
            text=text,
            legal_system=legal_system,
            jurisdiction=jurisdiction,
            model=model,
            themes=themes_str,
            facts=str(facts),
            pil_provisions=str(pil_provisions_data),
            col_issue=col_issue_text,
            court_position=courts_position_text,
            obiter_dicta=obiter_dicta_text,
            dissenting_opinions=dissenting_opinions_text,
        )
        yield result
