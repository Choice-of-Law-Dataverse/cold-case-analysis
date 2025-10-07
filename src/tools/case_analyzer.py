import logging
from collections.abc import Generator
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any, cast

import logfire

from models.analysis_models import (
    CourtsPositionOutput,
    DissentingOpinionsOutput,
    ObiterDictaOutput,
    PILProvisionsOutput,
    RelevantFactsOutput,
)
from models.classification_models import ThemeClassificationOutput, ThemeWithNA
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
        col_section_output = None
        if not col_sections:
            col_section_output = extract_col_section(
                text=text,
                legal_system=legal_system,
                jurisdiction=jurisdiction,
                model=model,
            )
            col_sections = col_section_output.col_sections
            yield col_section_output
        else:
            # Create output object from provided sections
            from models.analysis_models import ColSectionOutput

            col_section_output = ColSectionOutput(
                col_sections=col_sections, confidence="high", reasoning="Pre-extracted sections provided"
            )

        # Step 2: Classify themes if not provided
        themes_output = None
        if not themes:
            col_section_text = "\n\n".join(col_section_output.col_sections)
            themes_output = theme_classification_node(
                text=text,
                col_section=col_section_text,
                legal_system=legal_system,
                jurisdiction=jurisdiction,
                model=model,
            )
            yield themes_output
        else:
            themes_output = ThemeClassificationOutput(
                themes=cast(list[ThemeWithNA], themes), confidence="high", reasoning="Pre-classified themes provided"
            )

        # Step 3: Run parallel analysis (relevant facts + PIL provisions)
        facts_output = None
        pil_provisions_output = None
        futures = []
        with ThreadPoolExecutor(max_workers=2) as executor:
            col_section_text = "\n\n".join(col_section_output.col_sections)
            futures = {
                executor.submit(
                    extract_relevant_facts,
                    text,
                    col_section_text,
                    legal_system,
                    jurisdiction,
                    model,
                ),
                executor.submit(
                    extract_pil_provisions,
                    text,
                    col_section_text,
                    legal_system,
                    jurisdiction,
                    model,
                ),
            }

            for future in as_completed(futures):
                result = future.result()
                if isinstance(result, RelevantFactsOutput):
                    facts_output = result
                elif isinstance(result, PILProvisionsOutput):
                    pil_provisions_output = result
                yield result

        # Step 4: Extract CoL issue (depends on themes)
        col_issue_output = extract_col_issue(
            text=text,
            col_section_output=col_section_output,
            legal_system=legal_system,
            jurisdiction=jurisdiction,
            model=model,
            themes_output=themes_output,
        )
        yield col_issue_output

        # Step 5: Run parallel analysis (court's position + common law specific steps)
        courts_position_output = None
        obiter_dicta_output = None
        dissenting_opinions_output = None
        futures = []
        with ThreadPoolExecutor(max_workers=3) as executor:
            # Always extract court's position
            courts_future = executor.submit(
                extract_courts_position,
                text,
                col_section_output,
                legal_system,
                jurisdiction,
                model,
                themes_output,
                col_issue_output,
            )
            futures.append(courts_future)

            # Add Common Law specific extractions if applicable
            if legal_system == "Common-law jurisdiction":
                obiter_future = executor.submit(
                    extract_obiter_dicta,
                    text,
                    col_section_output,
                    legal_system,
                    jurisdiction,
                    model,
                    themes_output,
                    col_issue_output,
                )
                futures.append(obiter_future)

                dissent_future = executor.submit(
                    extract_dissenting_opinions,
                    text,
                    col_section_output,
                    legal_system,
                    jurisdiction,
                    model,
                    themes_output,
                    col_issue_output,
                )
                futures.append(dissent_future)

            # Collect results as they complete
            for future in as_completed(futures):
                result = future.result()
                if isinstance(result, CourtsPositionOutput):
                    courts_position_output = result
                elif isinstance(result, ObiterDictaOutput):
                    obiter_dicta_output = result
                elif isinstance(result, DissentingOpinionsOutput):
                    dissenting_opinions_output = result
                yield result

        # Step 6: Generate abstract (final step, depends on all previous steps)

        if facts_output is None:
            raise RuntimeError("Relevant facts extraction failed - cannot generate abstract")

        if pil_provisions_output is None:
            raise RuntimeError("PIL provisions extraction failed - cannot generate abstract")

        if courts_position_output is None:
            raise RuntimeError("Court's position extraction failed - cannot generate abstract")

        result = extract_abstract(
            text=text,
            legal_system=legal_system,
            jurisdiction=jurisdiction,
            model=model,
            themes_output=themes_output,
            facts_output=facts_output,
            pil_provisions_output=pil_provisions_output,
            col_issue_output=col_issue_output,
            court_position_output=courts_position_output,
            obiter_dicta_output=obiter_dicta_output,
            dissenting_opinions_output=dissenting_opinions_output,
        )
        yield result
