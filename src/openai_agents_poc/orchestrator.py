"""Orchestrator for the CoLD Case Analyzer agents workflow."""

import asyncio
import logging
from datetime import datetime
from typing import Any

from agents import Runner

from .models import (
    CaseAbstract,
    ChoiceOfLawExtraction,
    ChoiceOfLawIssue,
    CompleteCaseAnalysis,
    CourtsPosition,
    DissentingOpinions,
    JurisdictionDetection,
    ObiterDicta,
    PILProvisions,
    RelevantFacts,
    ThemeClassification,
)
from .sub_agents import (
    create_abstract_agent,
    create_col_extraction_agent,
    create_col_issue_agent,
    create_courts_position_agent,
    create_dissenting_opinions_agent,
    create_jurisdiction_agent,
    create_obiter_dicta_agent,
    create_pil_provisions_agent,
    create_relevant_facts_agent,
    create_theme_classification_agent,
)

logger = logging.getLogger(__name__)


class CaseAnalysisOrchestrator:
    """Orchestrates the case analysis workflow using multiple specialized agents."""

    def __init__(self, model: str = "gpt-4o-mini", available_themes: list[str] | None = None):
        """Initialize the orchestrator with agents.

        Args:
            model: The OpenAI model to use for all agents
            available_themes: List of available PIL themes for classification
        """
        self.model = model
        self.available_themes = available_themes or [
            "Jurisdiction",
            "Choice of Law",
            "Recognition and Enforcement",
            "International Contracts",
            "International Torts",
            "Family Law",
            "Succession",
            "Property",
            "Commercial Law",
            "Insolvency",
        ]

    async def analyze_case(
        self, case_text: str, case_citation: str = "Unknown", case_metadata: dict[str, Any] | None = None
    ) -> CompleteCaseAnalysis:
        """Analyze a case using multiple specialized agents in parallel where possible.

        Args:
            case_text: The full text of the court decision
            case_citation: Citation or identifier for the case
            case_metadata: Optional metadata about the case (should include jurisdiction and precise_jurisdiction)

        Returns:
            CompleteCaseAnalysis: Complete structured analysis of the case
        """
        logger.info("Starting case analysis for: %s", case_citation)
        start_time = datetime.now()
        
        case_metadata = case_metadata or {}

        # Use jurisdiction from metadata (already confirmed by user via HITL)
        jurisdiction_legal_system = case_metadata.get("jurisdiction", "Unknown")
        jurisdiction_precise = case_metadata.get("precise_jurisdiction")
        
        logger.info("Using jurisdiction from HITL: %s (%s)", jurisdiction_legal_system, jurisdiction_precise)
        
        # Create jurisdiction result from HITL data
        jurisdiction_result = JurisdictionDetection(
            legal_system_type=jurisdiction_legal_system,
            precise_jurisdiction=jurisdiction_precise,
            confidence="high",
            reasoning="Jurisdiction confirmed by user via human-in-the-loop"
        )

        # Step 1: Run initial parallel analysis (CoL extraction, themes, relevant facts)
        logger.info("Step 1: Running initial parallel analysis (CoL extraction, themes, facts)...")
        col_extraction, themes, relevant_facts = await asyncio.gather(
            self._extract_col_sections(
                case_text, jurisdiction_result.legal_system_type, jurisdiction_result.precise_jurisdiction
            ),
            self._classify_themes(case_text, jurisdiction_result.legal_system_type, jurisdiction_result.precise_jurisdiction),
            self._extract_relevant_facts(
                case_text, jurisdiction_result.legal_system_type, jurisdiction_result.precise_jurisdiction
            ),
        )
        logger.info("Initial parallel analysis complete")

        # Step 2: Run PIL provisions and CoL issue in parallel
        logger.info("Step 2: Extracting PIL provisions and identifying CoL issue...")
        pil_provisions, col_issue = await asyncio.gather(
            self._extract_pil_provisions(
                case_text,
                col_extraction.col_sections,
                jurisdiction_result.legal_system_type,
                jurisdiction_result.precise_jurisdiction,
            ),
            self._identify_col_issue(
                case_text,
                col_extraction.col_sections,
                jurisdiction_result.legal_system_type,
                jurisdiction_result.precise_jurisdiction,
            ),
        )
        logger.info("PIL provisions and CoL issue identified")

        # Step 3: Analyze court's position
        logger.info("Step 3: Analyzing court's position...")
        courts_position = await self._analyze_courts_position(
            case_text,
            col_extraction.col_sections,
            col_issue.issue,
            jurisdiction_result.legal_system_type,
            jurisdiction_result.precise_jurisdiction,
        )
        logger.info("Court's position analyzed")

        # Step 4: Extract jurisdiction-specific elements (if Common Law)
        obiter_dicta = None
        dissenting_opinions = None
        if "Common-law" in jurisdiction_result.legal_system_type or "Indian" in jurisdiction_result.legal_system_type:
            logger.info("Step 4: Extracting Common Law specific elements (obiter dicta, dissenting opinions)...")
            obiter_dicta, dissenting_opinions = await asyncio.gather(
                self._extract_obiter_dicta(
                    case_text, jurisdiction_result.legal_system_type, jurisdiction_result.precise_jurisdiction
                ),
                self._extract_dissenting_opinions(
                    case_text, jurisdiction_result.legal_system_type, jurisdiction_result.precise_jurisdiction
                ),
            )
            logger.info("Common Law specific elements extracted")

        # Step 5: Generate abstract (uses all previous results)
        logger.info("Step 5: Generating case abstract...")
        abstract = await self._generate_abstract(case_text, jurisdiction_result, col_issue, courts_position, themes)
        logger.info("Abstract generated")

        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        logger.info("Case analysis complete in %.2f seconds", duration)

        # Compile metadata
        metadata = case_metadata or {}
        metadata.update(
            {
                "model": self.model,
                "analysis_timestamp": end_time.isoformat(),
                "duration_seconds": duration,
            }
        )

        return CompleteCaseAnalysis(
            case_citation=case_citation,
            jurisdiction_detection=jurisdiction_result,
            col_extraction=col_extraction,
            theme_classification=themes,
            relevant_facts=relevant_facts,
            pil_provisions=pil_provisions,
            col_issue=col_issue,
            courts_position=courts_position,
            abstract=abstract,
            obiter_dicta=obiter_dicta,
            dissenting_opinions=dissenting_opinions,
            metadata=metadata,
        )

    async def _detect_jurisdiction(self, case_text: str) -> JurisdictionDetection:
        """Detect the jurisdiction of the case."""
        agent = create_jurisdiction_agent()
        agent.model = self.model

        result = await Runner.run(agent, f"Analyze this court decision and determine its jurisdiction:\n\n{case_text}")
        return result.final_output_as(JurisdictionDetection)

    async def _extract_col_sections(
        self, case_text: str, jurisdiction: str, precise_jurisdiction: str | None
    ) -> ChoiceOfLawExtraction:
        """Extract Choice of Law sections from the case."""
        agent = create_col_extraction_agent(jurisdiction, precise_jurisdiction)
        agent.model = self.model

        result = await Runner.run(agent, f"Extract all Choice of Law sections from this court decision:\n\n{case_text}")
        return result.final_output_as(ChoiceOfLawExtraction)

    async def _classify_themes(
        self, case_text: str, jurisdiction: str, precise_jurisdiction: str | None
    ) -> ThemeClassification:
        """Classify PIL themes in the case."""
        agent = create_theme_classification_agent(self.available_themes, jurisdiction, precise_jurisdiction)
        agent.model = self.model

        result = await Runner.run(
            agent, f"Classify the Private International Law themes in this court decision:\n\n{case_text}"
        )
        return result.final_output_as(ThemeClassification)

    async def _extract_relevant_facts(
        self, case_text: str, jurisdiction: str, precise_jurisdiction: str | None
    ) -> RelevantFacts:
        """Extract relevant facts from the case."""
        agent = create_relevant_facts_agent(jurisdiction, precise_jurisdiction)
        agent.model = self.model

        result = await Runner.run(agent, f"Extract the relevant facts from this court decision:\n\n{case_text}")
        return result.final_output_as(RelevantFacts)

    async def _extract_pil_provisions(
        self, case_text: str, col_sections: list[str], jurisdiction: str, precise_jurisdiction: str | None
    ) -> PILProvisions:
        """Extract PIL provisions cited in the case."""
        agent = create_pil_provisions_agent(jurisdiction, precise_jurisdiction)
        agent.model = self.model

        col_context = "\n\n".join(col_sections) if col_sections else "Not extracted separately"
        result = await Runner.run(
            agent,
            f"Extract PIL provisions from this court decision.\n\nChoice of Law sections:\n{col_context}\n\nFull text:\n{case_text}",
        )
        return result.final_output_as(PILProvisions)

    async def _identify_col_issue(
        self, case_text: str, col_sections: list[str], jurisdiction: str, precise_jurisdiction: str | None
    ) -> ChoiceOfLawIssue:
        """Identify the Choice of Law issue."""
        agent = create_col_issue_agent(jurisdiction, precise_jurisdiction)
        agent.model = self.model

        col_context = "\n\n".join(col_sections) if col_sections else "Not extracted separately"
        result = await Runner.run(
            agent,
            f"Identify the Choice of Law issue in this court decision.\n\nChoice of Law sections:\n{col_context}\n\nFull text:\n{case_text}",
        )
        return result.final_output_as(ChoiceOfLawIssue)

    async def _analyze_courts_position(
        self, case_text: str, col_sections: list[str], col_issue: str, jurisdiction: str, precise_jurisdiction: str | None
    ) -> CourtsPosition:
        """Analyze the court's position."""
        agent = create_courts_position_agent(jurisdiction, precise_jurisdiction)
        agent.model = self.model

        col_context = "\n\n".join(col_sections) if col_sections else "Not extracted separately"
        result = await Runner.run(
            agent,
            f"Analyze the court's position on this Choice of Law issue.\n\nIssue: {col_issue}\n\nChoice of Law sections:\n{col_context}\n\nFull text:\n{case_text}",
        )
        return result.final_output_as(CourtsPosition)

    async def _extract_obiter_dicta(self, case_text: str, jurisdiction: str, precise_jurisdiction: str | None) -> ObiterDicta:
        """Extract obiter dicta (Common Law)."""
        agent = create_obiter_dicta_agent()
        agent.model = self.model

        result = await Runner.run(agent, f"Extract obiter dicta from this court decision:\n\n{case_text}")
        return result.final_output_as(ObiterDicta)

    async def _extract_dissenting_opinions(
        self, case_text: str, jurisdiction: str, precise_jurisdiction: str | None
    ) -> DissentingOpinions:
        """Extract dissenting opinions (Common Law)."""
        agent = create_dissenting_opinions_agent()
        agent.model = self.model

        result = await Runner.run(agent, f"Extract dissenting opinions from this court decision:\n\n{case_text}")
        return result.final_output_as(DissentingOpinions)

    async def _generate_abstract(
        self,
        case_text: str,
        jurisdiction: JurisdictionDetection,
        col_issue: ChoiceOfLawIssue,
        courts_position: CourtsPosition,
        themes: ThemeClassification,
    ) -> CaseAbstract:
        """Generate case abstract."""
        agent = create_abstract_agent(jurisdiction.legal_system_type, jurisdiction.precise_jurisdiction)
        agent.model = self.model

        context = f"""Jurisdiction: {jurisdiction.legal_system_type} ({jurisdiction.precise_jurisdiction})
Choice of Law Issue: {col_issue.issue}
Themes: {", ".join(themes.themes)}
Court's Position Summary: {courts_position.position[:500]}...

Full text:
{case_text}"""

        result = await Runner.run(agent, f"Generate a concise abstract for this case:\n\n{context}")
        return result.final_output_as(CaseAbstract)
