"""Proof of Concept script for the OpenAI Agents-based CoLD Case Analyzer.

This script demonstrates:
1. Pydantic models for structured outputs
2. Multiple specialized agents for different analysis tasks
3. Parallel execution of independent analysis steps
4. Structured, type-safe results
"""

import asyncio
import json
import logging
import os
from pathlib import Path

from dotenv import load_dotenv

from openai_agents_poc.orchestrator import CaseAnalysisOrchestrator

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Demo case text (shortened for PoC)
DEMO_CASE = """
BUNDESGERICHT (SWITZERLAND)
BGer 4A_709/2021
Date: May 31, 2022

Facts:
A Swiss company (Seller) and a German company (Buyer) entered into a contract for the sale of machinery.
The contract contained a choice of law clause selecting Swiss law. A dispute arose regarding defects in the machinery.
The Buyer initiated proceedings in Germany, while the Seller sought a declaration in Switzerland.

The question before the court was which jurisdiction's law applies to the assessment of the defects and
whether the choice of law clause is valid under Swiss Private International Law.

Legal Analysis:
The court examined the Swiss Federal Act on Private International Law (PILA), particularly Article 116,
which governs the law applicable to contracts. The court noted that parties are generally free to choose
the applicable law for their contractual relationship.

The court held that the choice of Swiss law was valid and binding. The court applied Swiss substantive law
to assess the defects and the Buyer's claims. The court analyzed the connecting factors and determined that
the choice of law clause was not contrary to Swiss public policy or mandatory provisions.

Reasoning:
The court reasoned that party autonomy is a fundamental principle in Swiss PIL. The choice of law clause
was clear, unambiguous, and agreed upon by both parties. The court distinguished this case from situations
where one party has a weaker bargaining position, noting that both parties were commercial entities with
equal negotiating power.

The court further held that the German proceedings should be stayed in favor of the Swiss proceedings,
as the choice of law clause implicitly included a choice of jurisdiction.

Decision:
The court declared that Swiss law applies to the contract and that the Swiss courts have jurisdiction
to hear the dispute. The German proceedings were found to be contrary to the parties' agreement.
"""


async def run_poc():
    """Run the Proof of Concept demonstration."""
    logger.info("=" * 80)
    logger.info("CoLD Case Analyzer - OpenAI Agents PoC")
    logger.info("=" * 80)
    logger.info("")

    # Check for API key
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key or api_key == "test_key":
        logger.warning("⚠️  No valid OPENAI_API_KEY found in environment.")
        logger.warning("⚠️  This PoC requires a real OpenAI API key to function.")
        logger.warning("⚠️  Set OPENAI_API_KEY in your .env file to run the full demo.")
        logger.info("")
        logger.info("However, we can demonstrate the structure of the implementation:")
        logger.info("")
        demonstrate_structure()
        return

    # Initialize orchestrator
    logger.info("Initializing Case Analysis Orchestrator...")
    orchestrator = CaseAnalysisOrchestrator(
        model="gpt-4o-mini",  # Use a cost-effective model for PoC
        available_themes=[
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
        ],
    )
    logger.info("Orchestrator initialized ✓")
    logger.info("")

    # Run analysis
    logger.info("Analyzing demo case...")
    logger.info("This will use multiple specialized agents working in parallel...")
    logger.info("")

    try:
        result = await orchestrator.analyze_case(
            case_text=DEMO_CASE,
            case_citation="BGer 4A_709/2021 (Switzerland)",
            case_metadata={"source": "PoC Demo", "language": "English (translated)"},
        )

        # Display results
        logger.info("=" * 80)
        logger.info("ANALYSIS RESULTS")
        logger.info("=" * 80)
        logger.info("")

        logger.info("📍 JURISDICTION DETECTION")
        logger.info(f"  Legal System: {result.jurisdiction_detection.legal_system_type}")
        logger.info(f"  Precise Jurisdiction: {result.jurisdiction_detection.precise_jurisdiction}")
        logger.info(f"  Confidence: {result.jurisdiction_detection.confidence}")
        logger.info(f"  Reasoning: {result.jurisdiction_detection.reasoning}")
        logger.info("")

        logger.info("📜 CHOICE OF LAW SECTIONS")
        logger.info(f"  Sections Extracted: {len(result.col_extraction.col_sections)}")
        logger.info(f"  Confidence: {result.col_extraction.confidence}")
        for i, section in enumerate(result.col_extraction.col_sections, 1):
            logger.info(f"  Section {i}: {section[:100]}...")
        logger.info("")

        logger.info("🏷️  THEME CLASSIFICATION")
        logger.info(f"  Themes: {', '.join(result.theme_classification.themes)}")
        logger.info(f"  Confidence: {result.theme_classification.confidence}")
        logger.info("")

        logger.info("📋 RELEVANT FACTS")
        logger.info(f"  {result.relevant_facts.facts[:200]}...")
        logger.info("")

        logger.info("⚖️  PIL PROVISIONS")
        logger.info(f"  Provisions Cited: {len(result.pil_provisions.provisions)}")
        for provision in result.pil_provisions.provisions:
            logger.info(f"  - {provision}")
        logger.info("")

        logger.info("❓ CHOICE OF LAW ISSUE")
        logger.info(f"  {result.col_issue.issue}")
        logger.info("")

        logger.info("🔍 COURT'S POSITION")
        logger.info(f"  {result.courts_position.position[:300]}...")
        logger.info("")

        logger.info("📝 ABSTRACT")
        logger.info(f"  {result.abstract.abstract}")
        logger.info("")

        logger.info("⏱️  METADATA")
        logger.info(f"  Model Used: {result.metadata.get('model')}")
        logger.info(f"  Analysis Duration: {result.metadata.get('duration_seconds'):.2f} seconds")
        logger.info(f"  Timestamp: {result.metadata.get('analysis_timestamp')}")
        logger.info("")

        # Save results to file
        output_dir = Path("output")
        output_dir.mkdir(exist_ok=True)
        output_file = output_dir / "poc_analysis_result.json"

        with open(output_file, "w") as f:
            json.dump(result.model_dump(), f, indent=2)

        logger.info(f"💾 Full results saved to: {output_file}")
        logger.info("")

        logger.info("=" * 80)
        logger.info("✅ PoC Complete!")
        logger.info("=" * 80)

    except Exception as e:
        logger.error("❌ Error during analysis: %s", str(e))
        logger.exception("Full traceback:")


def demonstrate_structure():
    """Demonstrate the structure of the implementation without API calls."""
    logger.info("📋 Implementation Structure:")
    logger.info("")
    logger.info("1️⃣  Pydantic Models (src/agents_poc/models.py)")
    logger.info("   - JurisdictionDetection")
    logger.info("   - ChoiceOfLawExtraction")
    logger.info("   - ThemeClassification")
    logger.info("   - RelevantFacts")
    logger.info("   - PILProvisions")
    logger.info("   - ChoiceOfLawIssue")
    logger.info("   - CourtsPosition")
    logger.info("   - ObiterDicta")
    logger.info("   - DissentingOpinions")
    logger.info("   - CaseAbstract")
    logger.info("   - CompleteCaseAnalysis")
    logger.info("")
    logger.info("2️⃣  Specialized Agents (src/agents_poc/agents.py)")
    logger.info("   - JurisdictionDetector")
    logger.info("   - ChoiceOfLawExtractor")
    logger.info("   - ThemeClassifier")
    logger.info("   - RelevantFactsExtractor")
    logger.info("   - PILProvisionsExtractor")
    logger.info("   - ChoiceOfLawIssueIdentifier")
    logger.info("   - CourtsPositionAnalyzer")
    logger.info("   - ObiterDictaExtractor")
    logger.info("   - DissentingOpinionsExtractor")
    logger.info("   - AbstractGenerator")
    logger.info("")
    logger.info("3️⃣  Orchestrator (src/agents_poc/orchestrator.py)")
    logger.info("   - Coordinates workflow")
    logger.info("   - Runs agents in parallel where possible")
    logger.info("   - Manages dependencies between steps")
    logger.info("   - Returns structured, type-safe results")
    logger.info("")
    logger.info("🔀 Parallel Execution Strategy:")
    logger.info("   Step 1: Detect jurisdiction (sequential)")
    logger.info("   Step 2: Extract CoL sections, classify themes, extract facts (parallel)")
    logger.info("   Step 3: Extract PIL provisions, identify CoL issue (parallel)")
    logger.info("   Step 4: Analyze court's position (sequential)")
    logger.info("   Step 5: Extract obiter dicta, dissenting opinions (parallel, Common Law only)")
    logger.info("   Step 6: Generate abstract (sequential)")
    logger.info("")
    logger.info("✨ Key Benefits:")
    logger.info("   ✓ Structured outputs with Pydantic models")
    logger.info("   ✓ No text parsing errors")
    logger.info("   ✓ Parallel execution for faster analysis")
    logger.info("   ✓ Type safety and validation")
    logger.info("   ✓ Clear separation of concerns")
    logger.info("   ✓ Easy to test and maintain")
    logger.info("   ✓ Scalable architecture")


if __name__ == "__main__":
    asyncio.run(run_poc())
