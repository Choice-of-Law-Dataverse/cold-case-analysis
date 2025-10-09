import logging
from collections.abc import Generator
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any

import logfire

from models.analysis_models import (
    ColIssueOutput,
    ColSectionOutput,
    CourtsPositionOutput,
    DissentingOpinionsOutput,
    ObiterDictaOutput,
    PILProvisionsOutput,
    RelevantFactsOutput,
)
from tools.abstract_generator import extract_abstract
from tools.case_citation_extractor import extract_case_citation
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
    jurisdiction: str,
    model: str,
) -> Generator[Any, None, None]:
    """
    Execute complete case analysis workflow with parallel execution where possible.

    This generator orchestrates all analysis steps and yields intermediate results.
    The component should consume these yields and update the UI/state accordingly.


    Args:
        text: Full court decision text
        legal_system: Legal system type (e.g., "Civil-law jurisdiction")
        jurisdiction: Precise jurisdiction (e.g., "Switzerland")
        model: Model to use for analysis
        themes: Pre-classified themes (optional)

    Yields:
        Output objects for each completed step:
            - ColSectionOutput
            - ThemeClassificationOutput
            - CaseCitationOutput
            - RelevantFactsOutput
            - PILProvisionsOutput
            - ColIssueOutput
            - CourtsPositionOutput
            - ObiterDictaOutput (Common Law only)
            - DissentingOpinionsOutput (Common Law only)
            - AbstractOutput
    """
    with logfire.span("analyze_case_workflow"):
        # Step: Extract CoL sections and case citation in parallel
        col_section_output = None
        future = []
        with ThreadPoolExecutor(max_workers=2) as executor:
            future.append(
                executor.submit(
                    extract_col_section,
                    text=text,
                    legal_system=legal_system,
                    jurisdiction=jurisdiction,
                    model=model,
                )
            )
            future.append(
                executor.submit(
                    extract_case_citation,
                    text=text,
                    legal_system=legal_system,
                    jurisdiction=jurisdiction,
                    model=model,
                )
            )

            for f in as_completed(future):
                result = f.result()
                if isinstance(result, ColSectionOutput):
                    col_section_output = result
                yield result

        if col_section_output is None:
            raise RuntimeError("Choice of Law issue extraction failed - cannot proceed")

        # Step: Classify themes
        themes_output = theme_classification_node(
            text=text,
            col_section=str(col_section_output),
            legal_system=legal_system,
            jurisdiction=jurisdiction,
            model=model,
        )
        yield themes_output

        # Step: Run parallel analysis (relevant facts + PIL provisions + CoL issue)
        facts_output = None
        pil_provisions_output = None
        col_issue_output = None
        futures = []
        with ThreadPoolExecutor(max_workers=2) as executor:
            futures.extend(
                [
                    executor.submit(
                        extract_relevant_facts,
                        text,
                        col_section_output,
                        legal_system,
                        jurisdiction,
                        model,
                    ),
                    executor.submit(
                        extract_pil_provisions,
                        text,
                        col_section_output,
                        legal_system,
                        jurisdiction,
                        model,
                    ),
                    executor.submit(
                        extract_col_issue,
                        text,
                        col_section_output,
                        legal_system,
                        jurisdiction,
                        model,
                        themes_output,
                    ),
                ]
            )

            for future in as_completed(futures):
                result = future.result()
                if isinstance(result, RelevantFactsOutput):
                    facts_output = result
                elif isinstance(result, PILProvisionsOutput):
                    pil_provisions_output = result
                elif isinstance(result, ColIssueOutput):
                    col_issue_output = result
                yield result

        if col_issue_output is None:
            raise RuntimeError("Choice of Law issue extraction failed - cannot proceed")

        # Step: Run parallel analysis (court's position + common law specific steps)
        courts_position_output = None
        obiter_dicta_output = None
        dissenting_opinions_output = None
        futures = []
        with ThreadPoolExecutor(max_workers=3) as executor:
            futures.append(
                executor.submit(
                    extract_courts_position,
                    text,
                    col_section_output,
                    legal_system,
                    jurisdiction,
                    model,
                    themes_output,
                    col_issue_output,
                )
            )

            if legal_system == "Common-law jurisdiction":
                futures.extend(
                    [
                        executor.submit(
                            extract_obiter_dicta,
                            text,
                            col_section_output,
                            legal_system,
                            jurisdiction,
                            model,
                            themes_output,
                            col_issue_output,
                        ),
                        executor.submit(
                            extract_dissenting_opinions,
                            text,
                            col_section_output,
                            legal_system,
                            jurisdiction,
                            model,
                            themes_output,
                            col_issue_output,
                        ),
                    ]
                )

            for future in as_completed(futures):
                result = future.result()
                if isinstance(result, CourtsPositionOutput):
                    courts_position_output = result
                elif isinstance(result, ObiterDictaOutput):
                    obiter_dicta_output = result
                elif isinstance(result, DissentingOpinionsOutput):
                    dissenting_opinions_output = result
                yield result

        if facts_output is None:
            raise RuntimeError("Relevant facts extraction failed - cannot generate abstract")

        if pil_provisions_output is None:
            raise RuntimeError("PIL provisions extraction failed - cannot generate abstract")

        if courts_position_output is None:
            raise RuntimeError("Court's position extraction failed - cannot generate abstract")

        # Step: Generate abstract (final step, depends on all previous steps)
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
