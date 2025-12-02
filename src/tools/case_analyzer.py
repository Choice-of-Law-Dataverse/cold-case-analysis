import logging
from collections.abc import Generator
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any

import logfire
import openai

from models.analysis_models import (
    CaseCitationOutput,
    ColIssueOutput,
    ColSectionOutput,
    CourtsPositionOutput,
    DissentingOpinionsOutput,
    ObiterDictaOutput,
    PILProvisionsOutput,
    RelevantFactsOutput,
)
from models.classification_models import ThemeClassificationOutput
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
    # Optional existing outputs to resume analysis
    existing_col_section: ColSectionOutput | None = None,
    existing_case_citation: CaseCitationOutput | None = None,
    existing_themes: ThemeClassificationOutput | None = None,
    existing_facts: RelevantFactsOutput | None = None,
    existing_pil_provisions: PILProvisionsOutput | None = None,
    existing_col_issue: ColIssueOutput | None = None,
    existing_courts_position: CourtsPositionOutput | None = None,
    existing_obiter_dicta: ObiterDictaOutput | None = None,
    existing_dissenting_opinions: DissentingOpinionsOutput | None = None,
) -> Generator[Any, None, None]:
    """
    Execute complete case analysis workflow with parallel execution where possible.

    This generator orchestrates all analysis steps and yields intermediate results.
    The component should consume these yields and update the UI/state accordingly.


    Args:
        text: Full court decision text
        legal_system: Legal system type (e.g., "Civil-law jurisdiction")
        jurisdiction: Precise jurisdiction (e.g., "Switzerland")
        existing_*: Optional existing outputs to skip steps (for retry/resume)

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
    with logfire.span("case_analysis"):
        try:
            # Step: Extract CoL sections and case citation in parallel
            col_section_output = existing_col_section

            # If we have existing outputs, yield them immediately
            if existing_col_section:
                yield existing_col_section
            if existing_case_citation:
                yield existing_case_citation

            future = []
            with ThreadPoolExecutor(max_workers=2) as executor:
                if not existing_col_section:
                    future.append(
                        executor.submit(
                            extract_col_section,
                            text=text,
                            legal_system=legal_system,
                            jurisdiction=jurisdiction,
                        )
                    )

                if not existing_case_citation:
                    future.append(
                        executor.submit(
                            extract_case_citation,
                            text=text,
                            legal_system=legal_system,
                            jurisdiction=jurisdiction,
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
            themes_output = existing_themes
            if themes_output:
                yield themes_output
            else:
                themes_output = theme_classification_node(
                    text=text,
                    col_section=str(col_section_output),
                    legal_system=legal_system,
                    jurisdiction=jurisdiction,
                )
                yield themes_output

            # Step: Run parallel analysis (relevant facts + PIL provisions + CoL issue)
            facts_output = existing_facts
            pil_provisions_output = existing_pil_provisions
            col_issue_output = existing_col_issue

            # Yield existing outputs
            if existing_facts:
                yield existing_facts
            if existing_pil_provisions:
                yield existing_pil_provisions
            if existing_col_issue:
                yield existing_col_issue

            futures = []
            with ThreadPoolExecutor(max_workers=3) as executor:
                if not existing_facts:
                    futures.append(
                        executor.submit(
                            extract_relevant_facts,
                            text,
                            col_section_output,
                            legal_system,
                            jurisdiction,
                        )
                    )

                if not existing_pil_provisions:
                    futures.append(
                        executor.submit(
                            extract_pil_provisions,
                            text,
                            col_section_output,
                            legal_system,
                            jurisdiction,
                        )
                    )

                if not existing_col_issue:
                    futures.append(
                        executor.submit(
                            extract_col_issue,
                            text,
                            col_section_output,
                            legal_system,
                            jurisdiction,
                            themes_output,
                        )
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
            courts_position_output = existing_courts_position
            obiter_dicta_output = existing_obiter_dicta
            dissenting_opinions_output = existing_dissenting_opinions

            # Yield existing outputs
            if existing_courts_position:
                yield existing_courts_position
            if existing_obiter_dicta:
                yield existing_obiter_dicta
            if existing_dissenting_opinions:
                yield existing_dissenting_opinions

            futures = []
            with ThreadPoolExecutor(max_workers=3) as executor:
                if not existing_courts_position:
                    futures.append(
                        executor.submit(
                            extract_courts_position,
                            text,
                            col_section_output,
                            legal_system,
                            jurisdiction,
                            themes_output,
                            col_issue_output,
                        )
                    )

                if legal_system == "Common-law jurisdiction":
                    if not existing_obiter_dicta:
                        futures.append(
                            executor.submit(
                                extract_obiter_dicta,
                                text,
                                col_section_output,
                                legal_system,
                                jurisdiction,
                                themes_output,
                                col_issue_output,
                            )
                        )

                    if not existing_dissenting_opinions:
                        futures.append(
                            executor.submit(
                                extract_dissenting_opinions,
                                text,
                                col_section_output,
                                legal_system,
                                jurisdiction,
                                themes_output,
                                col_issue_output,
                            )
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
                themes_output=themes_output,
                facts_output=facts_output,
                pil_provisions_output=pil_provisions_output,
                col_issue_output=col_issue_output,
                court_position_output=courts_position_output,
                obiter_dicta_output=obiter_dicta_output,
                dissenting_opinions_output=dissenting_opinions_output,
            )
            yield result
        except GeneratorExit:
            logger.info("Analysis workflow generator closed early (user navigation or timeout)")
            return
        except openai.APITimeoutError as e:
            logger.error(f"OpenAI API timeout: {e}")
            raise RuntimeError("The AI service request timed out. Please try again in a moment.") from e
        except openai.RateLimitError as e:
            logger.error(f"OpenAI rate limit exceeded: {e}")
            raise RuntimeError("Too many requests to the AI service. Please wait a moment and try again.") from e
        except openai.AuthenticationError as e:
            logger.error(f"OpenAI authentication error: {e}")
            raise RuntimeError("Authentication failed with the AI service. Please check your API key configuration.") from e
        except openai.APIConnectionError as e:
            logger.error(f"OpenAI API connection error: {e}")
            raise RuntimeError(
                "Unable to connect to the AI service. Please check your internet connection and try again."
            ) from e
        except openai.APIError as e:
            logger.error(f"OpenAI API error: {e}")
            raise RuntimeError(
                f"AI service error: {str(e)}. Please try again or contact support if the problem persists."
            ) from e
